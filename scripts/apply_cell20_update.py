import json
from pathlib import Path

new_code = '''# =============================================================================
# GANTI CELL 20 dengan kode ini.
#
# Tambahan dari versi sebelumnya: parameter HAIR_REMOVAL_BEFORE_CONTOUR
# untuk switch antara 2 urutan pipeline tanpa perlu tulis ulang kode:
#
#   HAIR_REMOVAL_BEFORE_CONTOUR = True   (urutan "dibalik", saran saya)
#       Resize -> Hair Removal -> Contrast Stretch -> Active Contour -> Blend
#
#   HAIR_REMOVAL_BEFORE_CONTOUR = False  (urutan ASLI PAPER, Behara et al. 2024)
#       Resize -> Contrast Stretch -> Active Contour -> Hair Removal -> Blend
#
# Cara pakai untuk ablasi A/B:
#   1. Set HAIR_REMOVAL_BEFORE_CONTOUR = True  -> jalankan Fase 5 -> catat akurasi
#   2. Set HAIR_REMOVAL_BEFORE_CONTOUR = False -> jalankan ulang Fase 5 -> catat akurasi
#   3. Bandingkan. Kalau hasilnya tidak beda signifikan, pakai urutan ASLI PAPER
#      (lebih aman untuk laporan/skripsi -- tidak perlu disclaimer modifikasi metodologi).
# =============================================================================

import subprocess
import os

# --- SWITCH UNTUK ABLASI: ganti nilai ini lalu jalankan ulang Fase 5 ---
HAIR_REMOVAL_BEFORE_CONTOUR = True
# ------------------------------------------------------------------------


def run_distributed_preprocessing(spark, hdfs_dir, num_partitions, img_size, label_to_index,
                                   monitor=None, hair_before_contour=HAIR_REMOVAL_BEFORE_CONTOUR):
    # 1. Ambil metadata path dari HDFS via CLI
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
    print(f"Mode urutan pipeline: "
          f"{'Hair Removal SEBELUM Active Contour (dibalik)' if hair_before_contour else 'Hair Removal SETELAH Active Contour (sesuai paper asli)'}")

    # 2. Distribusikan path ke RDD worker
    paths_rdd = spark.sparkContext.parallelize(image_paths).repartition(num_partitions)

    java_home = os.environ["JAVA_HOME"]
    hadoop_home = str(HADOOP_HOME)
    hadoop_classpath = subprocess.run(
        [f"{hadoop_home}/bin/hadoop", "classpath", "--glob"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    error_acc = spark.sparkContext.accumulator(0)
    fallback_contour_acc = spark.sparkContext.accumulator(0)

    _hair_before = hair_before_contour  # closure lokal untuk dikirim ke worker

    # 3. Eksekusi fungsi preprocessing per partisi di worker
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
        from skimage.filters import gaussian
        from skimage.segmentation import active_contour

        hdfs = pafs.HadoopFileSystem("localhost", port=9000)

        MIN_LESION_RATIO = 0.05
        MAX_LESION_RATIO = 0.80

        # Helper 1: Pad & Resize menjaga aspect ratio
        def _pad_and_resize(img_rgb, target_size=img_size):
            h, w = img_rgb.shape[:2]
            max_dim = max(h, w)
            top, bottom = (max_dim - h) // 2, (max_dim - h) - ((max_dim - h) // 2)
            left, right = (max_dim - w) // 2, (max_dim - w) - ((max_dim - w) // 2)
            padded = cv2.copyMakeBorder(img_rgb, top, bottom, left, right, cv2.BORDER_REFLECT)
            return cv2.resize(padded, (target_size, target_size), interpolation=cv2.INTER_AREA)

        # Helper 2: Hair Removal (Dull Razor via Black-hat + Inpaint)
        def _remove_hair_dull_razor(img_rgb, threshold=10):
            gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 17))
            blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
            _, hair_mask = cv2.threshold(blackhat, threshold, 255, cv2.THRESH_BINARY)
            return cv2.inpaint(img_rgb, hair_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

        # Helper 3: Contrast Stretching Normalization per-channel independen (vectorized)
        def _contrast_stretching_norm(img_rgb, n0=128.0, var0=4000.0):
            img_f = img_rgb.astype(np.float32)
            m = np.mean(img_f, axis=(0, 1), keepdims=True)
            v = np.var(img_f, axis=(0, 1), keepdims=True)
            scaled = n0 + np.sqrt(np.maximum(var0 / (v + 1e-7), 0.0)) * (img_f - m)
            return np.clip(scaled, 0, 255).astype(np.uint8)

        # Helper 4: Inisialisasi snake adaptif multi-polaritas Otsu
        def _get_adaptive_initialization(smooth_gray_u8, h, w):
            total_area = h * w
            center_img = np.array([w / 2.0, h / 2.0])
            thresh_val, _ = cv2.threshold(smooth_gray_u8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            mask_dark = (smooth_gray_u8 < thresh_val).astype(np.uint8) * 255
            mask_bright = (smooth_gray_u8 >= thresh_val).astype(np.uint8) * 255

            best_contour = None
            best_dist = float("inf")

            for mask in [mask_dark, mask_bright]:
                cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if not cnts:
                    continue
                c = max(cnts, key=cv2.contourArea)
                area = cv2.contourArea(c)
                if MIN_LESION_RATIO * total_area <= area <= MAX_LESION_RATIO * total_area:
                    M = cv2.moments(c)
                    if M["m00"] > 0:
                        centroid = np.array([M["m10"] / M["m00"], M["m01"] / M["m00"]])
                        dist = np.linalg.norm(centroid - center_img)
                        if dist < best_dist:
                            best_dist = dist
                            best_contour = c

            if best_contour is None:
                return h / 2.0, w / 2.0, h * 0.35, w * 0.35

            M = cv2.moments(best_contour)
            cx, cy = M["m10"] / M["m00"], M["m01"] / M["m00"]
            if len(best_contour) >= 5:
                _, (ma, mi), _ = cv2.fitEllipse(best_contour)
                rx = np.clip(ma / 2.0, w * 0.15, w * 0.45)
                ry = np.clip(mi / 2.0, h * 0.15, h * 0.45)
            else:
                rx, ry = w * 0.35, h * 0.35

            return cy, cx, ry, rx

        # Helper 5: Active Contour -> menghasilkan MASK saja (tanpa blending)
        # Dipisah dari blending supaya bisa dipakai untuk 2 urutan pipeline berbeda.
        def _run_active_contour(gray_source_img, h, w):
            gray = cv2.cvtColor(gray_source_img, cv2.COLOR_RGB2GRAY)
            smooth_gray = gaussian(gray, sigma=2.0, preserve_range=False)
            smooth_u8 = (smooth_gray * 255).astype(np.uint8)

            cy, cx, ry, rx = _get_adaptive_initialization(smooth_u8, h, w)
            s = np.linspace(0, 2 * np.pi, 75)
            init_snake = np.array([cy + ry * np.sin(s), cx + rx * np.cos(s)]).T

            total_area = h * w
            try:
                snake = active_contour(
                    smooth_gray, init_snake,
                    alpha=0.015, beta=10.0, gamma=0.001,
                    max_num_iter=20
                )
                mask = np.zeros((h, w), dtype=np.uint8)
                pts = np.int32([np.flip(snake, axis=1)])
                cv2.fillPoly(mask, pts, 255)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))

                seg_area = np.sum(mask > 0)
                is_success = (MIN_LESION_RATIO * total_area <= seg_area <= MAX_LESION_RATIO * total_area)
                return mask, is_success
            except Exception:
                return np.zeros((h, w), dtype=np.uint8), False

        # Helper 6: Soft-blend citra dengan mask yang sudah jadi
        def _soft_blend(img_rgb, mask):
            alpha = cv2.GaussianBlur(mask.astype(np.float32) / 255.0, (15, 15), 0)[:, :, np.newaxis]
            blurred_bg = cv2.GaussianBlur(img_rgb, (21, 21), 0)
            return (alpha * img_rgb + (1.0 - alpha) * blurred_bg).astype(np.uint8)

        # Loop pemrosesan data di worker
        for path in paths:
            try:
                with hdfs.open_input_stream(path, buffer_size=65536) as f:
                    raw_bytes = f.read()

                nparr = np.frombuffer(raw_bytes, np.uint8)
                img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img_bgr is None:
                    continue
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

                # Tahap 1: Pad & Resize (selalu sama di kedua varian)
                resized = _pad_and_resize(img_rgb, target_size=img_size)
                h, w = resized.shape[:2]

                if _hair_before:
                    # ================================================
                    # VARIAN X: Hair Removal SEBELUM Active Contour
                    # Resize -> Hair Removal -> Contrast Stretch -> Snake -> Blend
                    # (urutan "dibalik", saran saya -- perlu disclaimer di laporan)
                    # ================================================
                    hairless = _remove_hair_dull_razor(resized, threshold=10)
                    stretched = _contrast_stretching_norm(hairless)
                    mask, is_success = _run_active_contour(stretched, h, w)
                    final_img = _soft_blend(stretched, mask) if is_success else stretched
                else:
                    # ================================================
                    # VARIAN Y: Hair Removal SETELAH Active Contour
                    # Resize -> Contrast Stretch -> Snake -> Hair Removal -> Blend
                    # (urutan ASLI paper Behara et al. 2024, Section 4.3 & Fig. 10)
                    # ================================================
                    stretched = _contrast_stretching_norm(resized)
                    mask, is_success = _run_active_contour(stretched, h, w)
                    hairless = _remove_hair_dull_razor(stretched, threshold=10)
                    final_img = _soft_blend(hairless, mask) if is_success else hairless

                if not is_success:
                    fallback_contour_acc.add(1)

                label_name = path.rstrip("/").split("/")[-2]
                label = label_to_index[label_name]
                image_id = _Path(path).stem

                yield (final_img, label, image_id)
            except Exception as exc:
                error_acc.add(1)
                print(f"Error memproses citra {path}: {exc}")

    processed_rdd = (
        paths_rdd
        .mapPartitions(preprocess_partition)
        .persist(StorageLevel.DISK_ONLY)
    )

    # 4. Pengukuran materialisasi RDD
    if monitor is not None:
        monitor.start()
    start_time = time.time()
    image_count = processed_rdd.count()
    elapsed_sec = time.time() - start_time
    if monitor is not None:
        monitor.stop()

    partition_sizes = processed_rdd.mapPartitions(lambda it: [sum(1 for _ in it)]).collect()
    failed = error_acc.value
    total_fallback = fallback_contour_acc.value
    pct_fallback = (total_fallback / image_count) * 100 if image_count > 0 else 0

    print("Prapemrosesan jurnal terdistribusi selesai!")
    print(f"Distribusi partisi: {partition_sizes}")
    print(f"Segmentasi snake: {image_count - total_fallback} berhasil, {total_fallback} fallback ({pct_fallback:.2f}%)")
    if failed:
        print(f"PERINGATAN: {failed} citra gagal diproses ({image_count}/{expected_total} berhasil).")

    return processed_rdd, elapsed_sec, image_count
'''

lines = [l + '\n' for l in new_code.split('\n')[:-1]] + [new_code.split('\n')[-1]]

targets = [
    Path(r'kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk1-irisan-tipe1-ringkas-prepjurnal.ipynb'),
    Path(r'kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk2-biner-tipe1-ringkas-prepjurnal.ipynb')
]

for t in targets:
    if not t.exists():
        continue
    with open(t, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    for i, c in enumerate(nb['cells']):
        if c['cell_type'] == 'code' and 'def run_distributed_preprocessing' in ''.join(c['source']):
            c['source'] = lines
            print(f'Patched Cell {i} in {t.name}')
            break
    with open(t, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
