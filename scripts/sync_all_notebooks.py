import json

cell_20_code = """# =============================================================================
# TAHAP 5: PRAPEMROSESAN TERDISTRIBUSI SPARK ON YARN (224x224)
# PIPELINE: PAD & RESIZE 224 -> DULL RAZOR -> ADAPTIVE MULTI-COMPONENT CONTOUR -> ISOLASI BERSIH
# (Anti-Bintik Kecil, Mencegah Pemotongan Lesi Difus, Kebal Vignette, Lesi 100% Tajam Asli)
# =============================================================================

import subprocess
import os

def run_distributed_preprocessing(spark, hdfs_dir, num_partitions, img_size, label_to_index, monitor=None):
    listing = subprocess.run(
        ["hdfs", "dfs", "-ls", "-R", hdfs_dir],
        capture_output=True, text=True, check=True,
    ).stdout

    image_paths = []
    for line in listing.splitlines():
        parts = line.split()
        if len(parts) < 8 or parts[0].startswith("d"):
            continue
        path = parts[-1]
        if path.lower().endswith((".jpg", ".jpeg", ".png")):
            image_paths.append(path)

    if not image_paths:
        raise RuntimeError(f"Tidak ada citra ditemukan di direktori HDFS: {hdfs_dir}")

    expected_total = len(image_paths)
    print(f"Jumlah path citra terdaftar di HDFS: {expected_total}")
    print(f"Resolusi target: {img_size}x{img_size} px | Pipeline: Multi-Component Contour with Safety Fallback")

    paths_rdd = spark.sparkContext.parallelize(image_paths).repartition(num_partitions)

    java_home = os.environ["JAVA_HOME"]
    hadoop_home = str(HADOOP_HOME)
    hadoop_classpath = subprocess.run(
        [f"{hadoop_home}/bin/hadoop", "classpath", "--glob"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    error_acc = spark.sparkContext.accumulator(0)
    fallback_contour_acc = spark.sparkContext.accumulator(0)

    def preprocess_partition(paths):
        import os
        os.environ["JAVA_HOME"] = java_home
        os.environ["HADOOP_HOME"] = hadoop_home
        os.environ["LD_LIBRARY_PATH"] = f"{hadoop_home}/lib/native:{java_home}/lib/server"
        os.environ["CLASSPATH"] = hadoop_classpath

        import cv2
        import numpy as np
        from pathlib import Path as _Path
        import pyarrow.fs as pafs

        hdfs = pafs.HadoopFileSystem("localhost", port=9000)

        def _pad_and_resize(img_rgb, target_size=img_size):
            h, w = img_rgb.shape[:2]
            max_dim = max(h, w)
            top = (max_dim - h) // 2
            bottom = max_dim - h - top
            left = (max_dim - w) // 2
            right = max_dim - w - left
            padded = cv2.copyMakeBorder(img_rgb, top, bottom, left, right, cv2.BORDER_REFLECT)
            return cv2.resize(padded, (target_size, target_size), interpolation=cv2.INTER_AREA)

        def _remove_hair_safe(img_rgb):
            gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
            k_h = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 1))
            k_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 11))
            bh = cv2.max(cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, k_h),
                         cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, k_v))
            _, hair_mask = cv2.threshold(bh, 15, 255, cv2.THRESH_BINARY)
            return cv2.inpaint(img_rgb, hair_mask, inpaintRadius=2, flags=cv2.INPAINT_TELEA)

        def _segment_lesion_adaptive(img_rgb):
            h, w = img_rgb.shape[:2]
            gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

            # 1. Eliminasi sudut hitam vignette dermatoskop via floodFill 4 sudut
            ff_mask = np.zeros((h + 2, w + 2), np.uint8)
            for pt in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
                if gray[pt[1], pt[0]] < 40:
                    cv2.floodFill(gray.copy(), ff_mask, pt, 255, 15, 15, cv2.FLOODFILL_MASK_ONLY | (255 << 8))
            corner_vignette = (ff_mask[1:-1, 1:-1] == 255)
            skin_fov = ~corner_vignette

            # 2. Kanal L* ruang warna Lab untuk ekstraksi kontras lesi
            lab = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2LAB)
            l_chan = lab[:, :, 0]
            blurred = cv2.GaussianBlur(l_chan, (15, 15), 0)

            valid_l = blurred[skin_fov]
            if len(valid_l) < 500:
                return np.ones((h, w), dtype=np.uint8) * 255, False

            otsu_val, _ = cv2.threshold(valid_l.reshape(-1, 1), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Masker biner: piksel dalam skin_fov yang lebih gelap dari threshold
            raw_mask = np.zeros((h, w), dtype=np.uint8)
            raw_mask[(blurred < otsu_val) & skin_fov] = 255

            # 3. Morfologi closing untuk menggabungkan pulau-pulau lesi yang menyebar
            k_merge = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17))
            merged = cv2.morphologyEx(raw_mask, cv2.MORPH_CLOSE, k_merge)

            cnts, _ = cv2.findContours(merged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            lesion_mask = np.zeros((h, w), dtype=np.uint8)

            if cnts:
                cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
                max_a = cv2.contourArea(cnts[0])
                total_px = h * w

                # Ambil semua komponen lesi signifikan (minimal 15% dari luas kontur terbesar)
                sig_cnts = [c for c in cnts if cv2.contourArea(c) >= max_a * 0.15 and cv2.contourArea(c) > 80]
                for c in sig_cnts:
                    cv2.drawContours(lesion_mask, [c], -1, 255, -1)

                area_ratio = np.count_nonzero(lesion_mask) / total_px

                # JARING PENGAMAN (SAFETY FALLBACK):
                # Lesi terisolasi yang valid harus mencakup antara 4% s/d 75% luas gambar.
                # Jika < 4%: itu hanya bintik noise/pudar (JANGAN DIPOTONG!), gunakan citra kulit utuh.
                # Jika > 75%: itu seluruh kulit/lensa, gunakan citra kulit utuh.
                if 0.04 <= area_ratio <= 0.75:
                    return lesion_mask, True
                else:
                    return (skin_fov * 255).astype(np.uint8), False
            else:
                return (skin_fov * 255).astype(np.uint8), False

        for path in paths:
            try:
                with hdfs.open_input_stream(path, buffer_size=65536) as f:
                    raw_bytes = f.read()

                nparr = np.frombuffer(raw_bytes, np.uint8)
                img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img_bgr is None:
                    continue
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

                resized = _pad_and_resize(img_rgb, target_size=img_size)
                hairless = _remove_hair_safe(resized)
                mask, is_success = _segment_lesion_adaptive(hairless)

                # ISOLASI BERSIH: Lesi 100% Tajam Asli
                if is_success:
                    final_img = cv2.bitwise_and(hairless, hairless, mask=mask)
                else:
                    final_img = hairless
                    fallback_contour_acc.add(1)

                label_name = path.rstrip("/").split("/")[-2]
                label = label_to_index[label_name]
                image_id = _Path(path).stem

                yield (final_img, label, image_id)
            except Exception as exc:
                error_acc.add(1)
                print(f"Error memproses citra {path}: {exc}")

    from pyspark import StorageLevel
    processed_rdd = (
        paths_rdd
        .mapPartitions(preprocess_partition)
        .persist(StorageLevel.DISK_ONLY)
    )

    if monitor is not None:
        monitor.start()
    import time
    start_time = time.time()
    partition_sizes = processed_rdd.mapPartitions(lambda it: [sum(1 for _ in it)]).collect()
    elapsed_sec = time.time() - start_time
    if monitor is not None:
        monitor.stop()

    image_count = sum(partition_sizes)
    failed = error_acc.value
    total_fallback = fallback_contour_acc.value
    pct_fallback = (total_fallback / image_count * 100) if image_count > 0 else 0

    print("Prapemrosesan terdistribusi selesai!")
    print(f"Distribusi partisi: {partition_sizes}")
    print(f"Segmentasi bersih: {image_count - total_fallback} terisolasi kontur, {total_fallback} fallback aman ({pct_fallback:.2f}%)")
    if failed:
        print(f"PERINGATAN: {failed} citra gagal diproses ({image_count}/{expected_total} berhasil).")

    return processed_rdd, elapsed_sec, image_count
"""

cell_22_code = """import matplotlib.pyplot as plt
import numpy as np
import cv2
import random
import subprocess

listing = subprocess.run(
    ["hdfs", "dfs", "-ls", "-R", HDFS_WORKDIR],
    capture_output=True, text=True, check=True
).stdout

paths_by_class = {c: [] for c in class_names}
for line in listing.splitlines():
    parts = line.split()
    if len(parts) > 0:
        path = parts[-1]
        if path.lower().endswith((".jpg", ".jpeg", ".png")):
            label_name = path.rstrip("/").split("/")[-2]
            if label_name in paths_by_class:
                paths_by_class[label_name].append(path)

samples_per_class = 2
fig, axes = plt.subplots(len(class_names), samples_per_class * 4, figsize=(18, 3.8 * len(class_names)))
if len(class_names) == 1:
    axes = axes.reshape(1, -1)

for i, class_name in enumerate(class_names):
    sample_paths = random.sample(paths_by_class[class_name], min(len(paths_by_class[class_name]), samples_per_class))
    for j, sample_path in enumerate(sample_paths):
        cat_result = subprocess.run(
            ["hdfs", "dfs", "-cat", sample_path],
            capture_output=True, check=True
        )
        raw_bytes = cat_result.stdout
        nparr = np.frombuffer(raw_bytes, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        # 1. Pad & Resize
        h, w = img_rgb.shape[:2]
        max_dim = max(h, w)
        top = (max_dim - h) // 2
        bottom = max_dim - h - top
        left = (max_dim - w) // 2
        right = max_dim - w - left
        padded = cv2.copyMakeBorder(img_rgb, top, bottom, left, right, cv2.BORDER_REFLECT)
        resized = cv2.resize(padded, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_AREA)

        # 2. Dull Razor
        gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)
        k_h = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 1))
        k_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 11))
        bh = cv2.max(cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, k_h),
                     cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, k_v))
        _, hair_mask = cv2.threshold(bh, 15, 255, cv2.THRESH_BINARY)
        hairless = cv2.inpaint(resized, hair_mask, inpaintRadius=2, flags=cv2.INPAINT_TELEA)

        # 3. Segmentasi Adaptif Multi-Komponen
        ff_mask = np.zeros((IMG_SIZE + 2, IMG_SIZE + 2), np.uint8)
        for pt in [(0, 0), (IMG_SIZE - 1, 0), (0, IMG_SIZE - 1), (IMG_SIZE - 1, IMG_SIZE - 1)]:
            if gray[pt[1], pt[0]] < 40:
                cv2.floodFill(gray.copy(), ff_mask, pt, 255, 15, 15, cv2.FLOODFILL_MASK_ONLY | (255 << 8))
        skin_fov = ~(ff_mask[1:-1, 1:-1] == 255)

        lab = cv2.cvtColor(hairless, cv2.COLOR_BGR2LAB)
        blurred = cv2.GaussianBlur(lab[:, :, 0], (15, 15), 0)
        valid_l = blurred[skin_fov]
        
        lesion_mask = np.zeros((IMG_SIZE, IMG_SIZE), dtype=np.uint8)
        is_segmented = False
        
        if len(valid_l) >= 500:
            otsu_val, _ = cv2.threshold(valid_l.reshape(-1, 1), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            raw_mask = np.zeros((IMG_SIZE, IMG_SIZE), dtype=np.uint8)
            raw_mask[(blurred < otsu_val) & skin_fov] = 255
            merged = cv2.morphologyEx(raw_mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17)))
            cnts, _ = cv2.findContours(merged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if cnts:
                cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
                max_a = cv2.contourArea(cnts[0])
                sig_cnts = [c for c in cnts if cv2.contourArea(c) >= max_a * 0.15 and cv2.contourArea(c) > 80]
                for c in sig_cnts:
                    cv2.drawContours(lesion_mask, [c], -1, 255, -1)
                
                ratio = np.count_nonzero(lesion_mask) / (IMG_SIZE * IMG_SIZE)
                if 0.04 <= ratio <= 0.75:
                    is_segmented = True
                else:
                    lesion_mask = (skin_fov * 255).astype(np.uint8)
            else:
                lesion_mask = (skin_fov * 255).astype(np.uint8)
        else:
            lesion_mask = (skin_fov * 255).astype(np.uint8)

        # 4. Hasil Isolasi Akhir
        if is_segmented:
            final_img = cv2.bitwise_and(hairless, hairless, mask=lesion_mask)
            status_txt = "Kontur Terisolasi"
            c_color = (0, 0, 255)
        else:
            final_img = hairless
            status_txt = "Safe Fallback (Utuh)"
            c_color = (255, 165, 0)

        overlay = hairless.copy()
        cnts_disp, _ = cv2.findContours(lesion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(overlay, cnts_disp, -1, c_color, 2)

        col_base = j * 4
        axes[i, col_base].imshow(resized)
        axes[i, col_base].set_title(f"1. Asli ({class_name})\\n224x224 px", fontsize=8)
        axes[i, col_base].axis("off")

        axes[i, col_base + 1].imshow(hairless)
        axes[i, col_base + 1].set_title("2. Dull Razor\\n(Tekstur Tajam)", fontsize=8)
        axes[i, col_base + 1].axis("off")

        axes[i, col_base + 2].imshow(overlay)
        axes[i, col_base + 2].set_title(f"3. Batas Lesi\\n({status_txt})", fontsize=8)
        axes[i, col_base + 2].axis("off")

        axes[i, col_base + 3].imshow(final_img)
        axes[i, col_base + 3].set_title("4. Input CNN\\n(Lesi 100% Utuh)", fontsize=8)
        axes[i, col_base + 3].axis("off")

plt.tight_layout()
vis_path = PROJECT_DIR / f"preprocessing_safe_adaptive_{SCENARIO_NAME}.png"
plt.savefig(vis_path, dpi=150)
plt.show()
print(f"Grafik verifikasi segmentasi aman tersimpan di: {vis_path}")
"""

if __name__ == "__main__":
    target_files = [
        'kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk1-irisan-tipe1-ringkas-prepjurnal.ipynb',
        'kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk2-biner-tipe1-ringkas-prepjurnal.ipynb'
    ]
    for filepath in target_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            nb = json.load(f)
        nb['cells'][20]['source'] = [line + '\n' for line in cell_20_code.splitlines()]
        nb['cells'][22]['source'] = [line + '\n' for line in cell_22_code.splitlines()]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
        print(f"UPDATED WITH SAFE ADAPTIVE CONTOUR: {filepath}")
