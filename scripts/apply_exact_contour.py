import json
from pathlib import Path

def apply_exact_contour_segmentation():
    notebooks = [
        Path("kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk1-irisan-tipe1-ringkas-prepjurnal.ipynb"),
        Path("kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk2-biner-tipe1-ringkas-prepjurnal.ipynb"),
        Path("kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk1-irisan-tipe1-ringkas-optimasi.ipynb"),
        Path("kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk2-biner-tipe1-ringkas-optimasi.ipynb"),
        Path("kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk3-irisan-local-prepjurnal-ak85.ipynb"),
        Path("kode/7_referensi tugas sebelumnya/sk3-irisan-local-prepjurnal-ak85.ipynb"),
    ]

    for p in notebooks:
        with open(p, "r", encoding="utf-8") as f:
            nb = json.load(f)

        is_sk3 = "sk3" in p.name
        
        if not is_sk3:
            # Spark on YARN notebooks (33 cells): Cell 20 is preprocessing
            c20_src = """# =============================================================================
# TAHAP 5: PRAPEMROSESAN TERDISTRIBUSI SPARK ON YARN (224x224)
# PIPELINE: PAD & RESIZE 224 -> DULL RAZOR -> ADAPTIVE CONTOUR SEGMENTATION -> SOFT-BLEND
# (Masker 100% menjiplak lekukan asli penyakit, warna alami murni tanpa Contrast Stretching)
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
    print(f"Resolusi target: {img_size}x{img_size} px | Pipeline: Dull Razor -> Exact Contour -> Soft-Blend")

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

        MIN_LESION_RATIO = 0.03
        MAX_LESION_RATIO = 0.85

        def _pad_and_resize(img_rgb, target_size=img_size):
            h, w = img_rgb.shape[:2]
            max_dim = max(h, w)
            top, bottom = (max_dim - h) // 2, (max_dim - h) - ((max_dim - h) // 2)
            left, right = (max_dim - w) // 2, (max_dim - w) - ((max_dim - w) // 2)
            padded = cv2.copyMakeBorder(img_rgb, top, bottom, left, right, cv2.BORDER_REFLECT)
            return cv2.resize(padded, (target_size, target_size), interpolation=cv2.INTER_AREA)

        def _remove_hair_dull_razor(img_rgb, threshold=10):
            gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 17))
            blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
            _, hair_mask = cv2.threshold(blackhat, threshold, 255, cv2.THRESH_BINARY)
            return cv2.inpaint(img_rgb, hair_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

        def _segment_lesion_exact_contour(img_rgb):
            # Segmentasi adaptif yang menjiplak lekukan bentuk riil penyakit (bukan bulatan kaku)
            gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
            blurred = cv2.GaussianBlur(gray, (7, 7), 0)
            
            # Otsu thresholding memisahkan lesi gelap dari kulit terang
            _, thresh_mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Morfologi closing untuk menutup pori-pori dan lubang mikro
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            closed = cv2.morphologyEx(thresh_mask, cv2.MORPH_CLOSE, kernel)
            
            cnts, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not cnts:
                return np.ones(gray.shape, dtype=np.uint8) * 255, False
            
            # Ambil kontur terbesar (lesi utama)
            c = max(cnts, key=cv2.contourArea)
            total_area = gray.shape[0] * gray.shape[1]
            area = cv2.contourArea(c)
            
            mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.drawContours(mask, [c], -1, 255, -1)
            
            is_success = (MIN_LESION_RATIO * total_area <= area <= MAX_LESION_RATIO * total_area)
            return mask, is_success

        def _soft_blend(img_rgb, mask):
            alpha = cv2.GaussianBlur(mask.astype(np.float32) / 255.0, (15, 15), 0)[:, :, np.newaxis]
            blurred_bg = cv2.GaussianBlur(img_rgb, (21, 21), 0)
            return (alpha * img_rgb + (1.0 - alpha) * blurred_bg).astype(np.uint8)

        for path in paths:
            try:
                with hdfs.open_input_stream(path, buffer_size=65536) as f:
                    raw_bytes = f.read()

                nparr = np.frombuffer(raw_bytes, np.uint8)
                img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img_bgr is None:
                    continue
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

                # 1. Pad & Resize 224x224
                resized = _pad_and_resize(img_rgb, target_size=img_size)
                # 2. Dull Razor Hair Removal
                hairless = _remove_hair_dull_razor(resized, threshold=10)
                # 3. Exact Lesion Contour Segmentation (menjiplak lekukan asli lesi)
                mask, is_success = _segment_lesion_exact_contour(hairless)
                # 4. Soft-Blending
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

    print("Prapemrosesan terdistribusi (Exact Contour + Soft-Blend) selesai!")
    print(f"Distribusi partisi: {partition_sizes}")
    print(f"Segmentasi kontur riil: {image_count - total_fallback} berhasil, {total_fallback} fallback ({pct_fallback:.2f}%)")
    if failed:
        print(f"PERINGATAN: {failed} citra gagal diproses ({image_count}/{expected_total} berhasil).")

    return processed_rdd, elapsed_sec, image_count
"""
            nb["cells"][20]["source"] = [l + "\n" for l in c20_src.splitlines()]

            # Cell 22: Update visualization to display the true organic contour
            c22_src = """import matplotlib.pyplot as plt
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
        if path.lower().endswith(('.jpg', '.jpeg', '.png')):
            label_name = path.rstrip("/").split("/")[-2]
            if label_name in paths_by_class:
                paths_by_class[label_name].append(path)

samples_per_class = 2
total_samples = len(class_names) * samples_per_class
fig, axes = plt.subplots(total_samples, 5, figsize=(18, 3.5 * total_samples))

row_idx = 0
for i, class_name in enumerate(class_names):
    sample_paths = random.sample(paths_by_class[class_name], min(len(paths_by_class[class_name]), samples_per_class))
    for j, sample_path in enumerate(sample_paths):
        cat_result = subprocess.run(["hdfs", "dfs", "-cat", sample_path], capture_output=True, check=True)
        raw_bytes = cat_result.stdout
        nparr = np.frombuffer(raw_bytes, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        orig_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        # 1. Pad & Resize 224x224
        h, w = orig_rgb.shape[:2]
        max_dim = max(h, w)
        top, bottom = (max_dim - h) // 2, (max_dim - h) - ((max_dim - h) // 2)
        left, right = (max_dim - w) // 2, (max_dim - w) - ((max_dim - w) // 2)
        padded = cv2.copyMakeBorder(orig_rgb, top, bottom, left, right, cv2.BORDER_REFLECT)
        resized_img = cv2.resize(padded, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_AREA)

        # 2. Dull Razor Hair Removal
        gray = cv2.cvtColor(resized_img, cv2.COLOR_RGB2GRAY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 17))
        blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
        _, hair_mask = cv2.threshold(blackhat, 10, 255, cv2.THRESH_BINARY)
        hairless = cv2.inpaint(resized_img, hair_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

        # 3. Exact Lesion Contour Segmentation (menjiplak lekukan bentuk asli lesi)
        blurred = cv2.GaussianBlur(cv2.cvtColor(hairless, cv2.COLOR_RGB2GRAY), (7, 7), 0)
        _, thresh_mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel_m = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        closed = cv2.morphologyEx(thresh_mask, cv2.MORPH_CLOSE, kernel_m)
        cnts, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        mask = np.zeros((IMG_SIZE, IMG_SIZE), dtype=np.uint8)
        if cnts:
            c = max(cnts, key=cv2.contourArea)
            cv2.drawContours(mask, [c], -1, 255, -1)
        else:
            mask = np.ones((IMG_SIZE, IMG_SIZE), dtype=np.uint8) * 255

        # 4. Soft-Blending
        alpha = cv2.GaussianBlur(mask.astype(np.float32) / 255.0, (15, 15), 0)[:, :, np.newaxis]
        blurred_bg = cv2.GaussianBlur(hairless, (21, 21), 0)
        final_roi = (alpha * hairless + (1.0 - alpha) * blurred_bg).astype(np.uint8)

        axes[row_idx, 0].imshow(orig_rgb)
        axes[row_idx, 0].set_title(f"1. Asli ({class_name})\\n{orig_rgb.shape[1]}x{orig_rgb.shape[0]} px", fontsize=8)
        axes[row_idx, 0].axis("off")

        axes[row_idx, 1].imshow(resized_img)
        axes[row_idx, 1].set_title(f"2. Pad & Resize\\n{IMG_SIZE}x{IMG_SIZE} px", fontsize=8)
        axes[row_idx, 1].axis("off")

        axes[row_idx, 2].imshow(hairless)
        axes[row_idx, 2].set_title("3. Dull Razor\\n(Bebas Rambut)", fontsize=8)
        axes[row_idx, 2].axis("off")

        axes[row_idx, 3].imshow(mask, cmap='gray')
        axes[row_idx, 3].set_title("4. Mask Kontur Asli\\n(Menjiplak Bentuk Lesi)", fontsize=8)
        axes[row_idx, 3].axis("off")

        axes[row_idx, 4].imshow(final_roi)
        axes[row_idx, 4].set_title(f"5. Soft-Blended ROI\\nWarna Alami Murni", fontsize=8)
        axes[row_idx, 4].axis("off")

        row_idx += 1

plt.tight_layout()
vis_path = PROJECT_DIR / f"preprocessing_exact_contour_{SCENARIO_NAME}.png"
plt.savefig(vis_path)
plt.show()
print(f"Grafik bukti prapemrosesan tersimpan di: {vis_path}")
"""
            nb["cells"][22]["source"] = [l + "\n" for l in c22_src.splitlines()]

        else:
            # sk3 notebook (20 cells): Cell 7 is preprocessing
            c7_src = """# =============================================================================
# TAHAP 3: REKAYASA CITRA (224x224 RESNET-50)
# PIPELINE: PAD & RESIZE 224 -> DULL RAZOR -> EXACT CONTOUR SEGMENTATION -> SOFT-BLEND
# (Masker menjiplak 100% bentuk asli penyakit, warna alami murni tanpa Contrast Stretching)
# =============================================================================
import os
import cv2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

TARGET_SIZE = 224
MIN_LESION_RATIO = 0.03
MAX_LESION_RATIO = 0.85

def pad_and_resize(img_rgb, target_size=TARGET_SIZE):
    h, w = img_rgb.shape[:2]
    max_dim = max(h, w)
    top, bottom = (max_dim - h) // 2, (max_dim - h) - ((max_dim - h) // 2)
    left, right = (max_dim - w) // 2, (max_dim - w) - ((max_dim - w) // 2)
    padded = cv2.copyMakeBorder(img_rgb, top, bottom, left, right, cv2.BORDER_REFLECT)
    return cv2.resize(padded, (target_size, target_size), interpolation=cv2.INTER_AREA)

def remove_hair_dull_razor(img_rgb, threshold=10):
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 17))
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
    _, hair_mask = cv2.threshold(blackhat, threshold, 255, cv2.THRESH_BINARY)
    return cv2.inpaint(img_rgb, hair_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

def segment_lesion_exact_contour(img_rgb):
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    _, thresh_mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    closed = cv2.morphologyEx(thresh_mask, cv2.MORPH_CLOSE, kernel)
    cnts, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return np.ones(gray.shape, dtype=np.uint8) * 255, False
    c = max(cnts, key=cv2.contourArea)
    total_area = gray.shape[0] * gray.shape[1]
    area = cv2.contourArea(c)
    mask = np.zeros(gray.shape, dtype=np.uint8)
    cv2.drawContours(mask, [c], -1, 255, -1)
    is_success = (MIN_LESION_RATIO * total_area <= area <= MAX_LESION_RATIO * total_area)
    return mask, is_success

def soft_blend(img_rgb, mask):
    alpha = cv2.GaussianBlur(mask.astype(np.float32) / 255.0, (15, 15), 0)[:, :, np.newaxis]
    blurred_bg = cv2.GaussianBlur(img_rgb, (21, 21), 0)
    return (alpha * img_rgb + (1.0 - alpha) * blurred_bg).astype(np.uint8)

def preprocess_exact(img_rgb):
    resized = pad_and_resize(img_rgb, target_size=TARGET_SIZE)
    hairless = remove_hair_dull_razor(resized, threshold=10)
    mask, is_success = segment_lesion_exact_contour(hairless)
    final_img = soft_blend(hairless, mask) if is_success else hairless
    return resized, hairless, mask, final_img

def plot_perbandingan(asli, resized, hairless, mask, segmented, index):
    fig, axes = plt.subplots(1, 5, figsize=(18, 4))
    axes[0].imshow(asli); axes[0].set_title(f"1. Asli (Sampel {index})"); axes[0].axis('off')
    axes[1].imshow(resized); axes[1].set_title("2. Resize (224x224)"); axes[1].axis('off')
    axes[2].imshow(hairless); axes[2].set_title("3. Dull Razor (No Hair)"); axes[2].axis('off')
    axes[3].imshow(mask, cmap='gray'); axes[3].set_title("4. Mask Kontur Asli"); axes[3].axis('off')
    axes[4].imshow(segmented); axes[4].set_title("5. Soft-Blended ROI"); axes[4].axis('off')
    plt.tight_layout()
    plt.show()

output_dir = "/kaggle/working/processed_images/"
os.makedirs(output_dir, exist_ok=True)

print("[INFO] Menampilkan visualisasi 3 sampel pertama (Exact Contour 224x224):")
for index, row in df_final.head(3).iterrows():
    img_bgr = cv2.imread(row['filepath'])
    if img_bgr is not None:
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        resized, hairless, mask, final_img = preprocess_exact(img_rgb)
        plot_perbandingan(img_rgb, resized, hairless, mask, final_img, index)

def process_single_image(args):
    index, img_path = args
    filename = f"{index}_{os.path.basename(img_path)}"
    new_img_path = os.path.join(output_dir, filename)
    if os.path.exists(new_img_path):
        return index, new_img_path
    img_bgr = cv2.imread(img_path)
    if img_bgr is None:
        return index, img_path
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    _, _, _, final_img = preprocess_exact(img_rgb)
    cv2.imwrite(new_img_path, cv2.cvtColor(final_img, cv2.COLOR_RGB2BGR))
    return index, new_img_path

tasks = [(idx, row['filepath']) for idx, row in df_final.iterrows()]
num_workers = min(os.cpu_count() or 4, 8)
print(f"[INFO] Memproses {len(tasks)} citra secara paralel menggunakan {num_workers} worker CPU...")

with ThreadPoolExecutor(max_workers=num_workers) as executor:
    results = list(tqdm(executor.map(process_single_image, tasks), total=len(tasks)))

results.sort(key=lambda x: x[0])
df_final['filepath'] = [r[1] for r in results]
df_final.to_csv("/kaggle/working/processed_metadata_combined.csv", index=False)
print(f"\\n[INFO] Selesai! Sebanyak {len(results)} citra tersegmentasi kontur riil siap digunakan.")
"""
            nb["cells"][7]["source"] = [l + "\n" for l in c7_src.splitlines()]

        with open(p, "w", encoding="utf-8") as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
        print(f"Updated {p.name} with exact contour segmentation!")

if __name__ == "__main__":
    apply_exact_contour_segmentation()
