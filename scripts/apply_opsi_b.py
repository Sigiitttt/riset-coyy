import json
from pathlib import Path

def update_to_opsi_b():
    # =========================================================================
    # 1. Update sk1-irisan-tipe1-ringkas-prepjurnal.ipynb (Spark on YARN)
    # =========================================================================
    p1 = Path("kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk1-irisan-tipe1-ringkas-prepjurnal.ipynb")
    with open(p1, "r", encoding="utf-8") as f:
        nb1 = json.load(f)

    # Cell 19: set IMG_SIZE = 224
    c19 = nb1["cells"][19]
    c19_str = "".join(c19["source"])
    c19_str = c19_str.replace("IMG_SIZE = 299", "IMG_SIZE = 224")
    c19_str = c19_str.replace("Target Resolusi (Jurnal LA-CapsNet): 299x299", "Target Resolusi: 224x224")
    c19["source"] = [l + "\n" for l in c19_str.splitlines()]

    # Cell 20: Preprocessing with Hair Removal + Active Contour + Soft Blend (Tanpa Contrast Stretching, 224x224)
    c20_src = """# =============================================================================
# TAHAP 5: PRAPEMROSESAN TERDISTRIBUSI SPARK ON YARN (OPSI B: 224x224)
# PIPELINE: PAD & RESIZE 224 -> DULL RAZOR HAIR REMOVAL -> ACTIVE CONTOUR -> SOFT-BLEND
# (Warna asli lesi dipertahankan 100% tanpa distorsi Contrast Stretching)
# =============================================================================

import subprocess
import os

def run_distributed_preprocessing(spark, hdfs_dir, num_partitions, img_size, label_to_index, monitor=None):
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
    print(f"Resolusi target: {img_size}x{img_size} px | Pipeline: Dull Razor -> Active Contour -> Soft-Blend")

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

        # Helper 1: Pad & Resize menjaga proporsi lesi ke 224x224
        def _pad_and_resize(img_rgb, target_size=img_size):
            h, w = img_rgb.shape[:2]
            max_dim = max(h, w)
            top, bottom = (max_dim - h) // 2, (max_dim - h) - ((max_dim - h) // 2)
            left, right = (max_dim - w) // 2, (max_dim - w) - ((max_dim - w) // 2)
            padded = cv2.copyMakeBorder(img_rgb, top, bottom, left, right, cv2.BORDER_REFLECT)
            return cv2.resize(padded, (target_size, target_size), interpolation=cv2.INTER_AREA)

        # Helper 2: Hair Removal (Dull Razor via Black-hat Morphology + Inpainting)
        def _remove_hair_dull_razor(img_rgb, threshold=10):
            gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 17))
            blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
            _, hair_mask = cv2.threshold(blackhat, threshold, 255, cv2.THRESH_BINARY)
            return cv2.inpaint(img_rgb, hair_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

        # Helper 3: Inisialisasi snake adaptif multi-polaritas Otsu
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

        # Helper 4: Active Contour -> menghasilkan masker lesi ROI
        def _run_active_contour(gray_source_img, h, w):
            gray = cv2.cvtColor(gray_source_img, cv2.COLOR_RGB2GRAY)
            smooth_gray = gaussian(gray, sigma=2.0, preserve_range=False)
            smooth_u8 = (smooth_gray * 255).astype(np.uint8)

            cy, cx, ry, rx = _get_adaptive_initialization(smooth_u8, h, w)
            s = np.linspace(0, 2 * np.pi, 60)
            init_snake = np.array([cy + ry * np.sin(s), cx + rx * np.cos(s)]).T

            total_area = h * w
            try:
                snake = active_contour(
                    smooth_gray, init_snake,
                    alpha=0.015, beta=10.0, gamma=0.001,
                    max_num_iter=15
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

        # Helper 5: Soft-blend citra dengan mask (Alpha Feathering)
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

                # 1. Pad & Resize 224x224
                resized = _pad_and_resize(img_rgb, target_size=img_size)
                h, w = resized.shape[:2]

                # 2. Hair Removal (Dull Razor) - permukaan lesi bersih dari rambut
                hairless = _remove_hair_dull_razor(resized, threshold=10)

                # 3. Active Contour Snake Segmentation
                mask, is_success = _run_active_contour(hairless, h, w)

                # 4. Soft-Blending (Latar belakang diburamkan halus, warna lesi asli murni)
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

    # 4. Pengukuran materialisasi RDD
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

    print("Prapemrosesan terdistribusi (Opsi B: 224x224) selesai!")
    print(f"Distribusi partisi: {partition_sizes}")
    print(f"Segmentasi snake: {image_count - total_fallback} berhasil, {total_fallback} fallback ({pct_fallback:.2f}%)")
    if failed:
        print(f"PERINGATAN: {failed} citra gagal diproses ({image_count}/{expected_total} berhasil).")

    return processed_rdd, elapsed_sec, image_count
"""
    nb1["cells"][20]["source"] = [l + "\n" for l in c20_src.splitlines()]

    # Cell 22: Update Visualisasi Before-After 5 Panel (Asli, Resize 224, Dull Razor, Mask, Soft-Blend)
    c22_src = """import matplotlib.pyplot as plt
import numpy as np
import cv2
import random
import subprocess
from skimage.filters import gaussian
from skimage.segmentation import active_contour

# Kumpulkan path citra per kelas dari HDFS untuk perbandingan visual
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

        # 3. Active Contour Snake Segmentation
        try:
            smooth_gray = gaussian(cv2.cvtColor(hairless, cv2.COLOR_RGB2GRAY), sigma=2.0, preserve_range=False)
            cy, cx = IMG_SIZE / 2.0, IMG_SIZE / 2.0
            ry, rx = IMG_SIZE * 0.38, IMG_SIZE * 0.38
            s = np.linspace(0, 2 * np.pi, 60)
            init_c = np.array([cy + ry * np.sin(s), cx + rx * np.cos(s)]).T
            snake = active_contour(smooth_gray, init_c, alpha=0.015, beta=10.0, gamma=0.001, max_num_iter=15)
            mask = np.zeros((IMG_SIZE, IMG_SIZE), dtype=np.uint8)
            pts = np.int32([np.flip(snake, axis=1)])
            cv2.fillPoly(mask, pts, 255)
            kernel_m = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_m)

            # 4. Soft-Blending
            alpha = cv2.GaussianBlur(mask.astype(np.float32) / 255.0, (15, 15), 0)[:, :, np.newaxis]
            blurred_bg = cv2.GaussianBlur(hairless, (21, 21), 0)
            final_roi = (alpha * hairless + (1.0 - alpha) * blurred_bg).astype(np.uint8)
        except Exception:
            mask = np.ones((IMG_SIZE, IMG_SIZE), dtype=np.uint8) * 255
            final_roi = hairless

        # Plot 5 kolom per sampel
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
        axes[row_idx, 3].set_title("4. Mask Active Contour\\n(Snake Model)", fontsize=8)
        axes[row_idx, 3].axis("off")

        axes[row_idx, 4].imshow(final_roi)
        axes[row_idx, 4].set_title(f"5. Soft-Blended ROI\\nWarna Alami Murni", fontsize=8)
        axes[row_idx, 4].axis("off")

        row_idx += 1

plt.tight_layout()
vis_path = PROJECT_DIR / f"preprocessing_opsi_b_{SCENARIO_NAME}.png"
plt.savefig(vis_path)
plt.show()
print(f"Grafik bukti prapemrosesan Opsi B tersimpan di: {vis_path}")
"""
    nb1["cells"][22]["source"] = [l + "\n" for l in c22_src.splitlines()]

    with open(p1, "w", encoding="utf-8") as f:
        json.dump(nb1, f, indent=1, ensure_ascii=False)
    print("Berhasil memperbarui sk1-irisan-tipe1-ringkas-prepjurnal.ipynb ke Opsi B (224x224)")

    # =========================================================================
    # 2. Update sk3-irisan-local-prepjurnal-ak85.ipynb (di kedua folder)
    # =========================================================================
    for p3 in [
        Path("kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk3-irisan-local-prepjurnal-ak85.ipynb"),
        Path("kode/7_referensi tugas sebelumnya/sk3-irisan-local-prepjurnal-ak85.ipynb")
    ]:
        with open(p3, "r", encoding="utf-8") as f:
            nb3 = json.load(f)

        # Cell 7: Pipeline Opsi B 224x224
        c7_src = """# =============================================================================
# TAHAP 3: REKAYASA CITRA (OPSI B: 224x224 RESNET-50 DEFAULT)
# PIPELINE: PAD & RESIZE 224 -> DULL RAZOR HAIR REMOVAL -> ACTIVE CONTOUR -> SOFT-BLEND
# (Warna asli lesi dipertahankan 100% tanpa distorsi Contrast Stretching)
# =============================================================================
import os
import cv2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from skimage.filters import gaussian
from skimage.segmentation import active_contour

TARGET_SIZE = 224
MIN_LESION_RATIO = 0.05
MAX_LESION_RATIO = 0.80

# Helper 1: Pad & Resize menjaga proporsi asli lesi ke 224x224
def pad_and_resize(img_rgb, target_size=TARGET_SIZE):
    h, w = img_rgb.shape[:2]
    max_dim = max(h, w)
    top, bottom = (max_dim - h) // 2, (max_dim - h) - ((max_dim - h) // 2)
    left, right = (max_dim - w) // 2, (max_dim - w) - ((max_dim - w) // 2)
    padded = cv2.copyMakeBorder(img_rgb, top, bottom, left, right, cv2.BORDER_REFLECT)
    return cv2.resize(padded, (target_size, target_size), interpolation=cv2.INTER_AREA)

# Helper 2: Hair Removal (Dull Razor via Black-hat Morphology + Inpainting)
def remove_hair_dull_razor(img_rgb, threshold=10):
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 17))
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
    _, hair_mask = cv2.threshold(blackhat, threshold, 255, cv2.THRESH_BINARY)
    return cv2.inpaint(img_rgb, hair_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

# Helper 3: Inisialisasi snake adaptif multi-polaritas Otsu
def get_adaptive_initialization(smooth_gray_u8, h, w):
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

# Helper 4: Active Contour -> menghasilkan masker lesi ROI
def run_active_contour(gray_source_img, h, w):
    gray = cv2.cvtColor(gray_source_img, cv2.COLOR_RGB2GRAY)
    smooth_gray = gaussian(gray, sigma=2.0, preserve_range=False)
    smooth_u8 = (smooth_gray * 255).astype(np.uint8)

    cy, cx, ry, rx = get_adaptive_initialization(smooth_u8, h, w)
    s = np.linspace(0, 2 * np.pi, 60)
    init_snake = np.array([cy + ry * np.sin(s), cx + rx * np.cos(s)]).T

    total_area = h * w
    try:
        snake = active_contour(
            smooth_gray, init_snake,
            alpha=0.015, beta=10.0, gamma=0.001,
            max_num_iter=15
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

# Helper 5: Soft-blend citra dengan mask (Alpha Feathering)
def soft_blend(img_rgb, mask):
    alpha = cv2.GaussianBlur(mask.astype(np.float32) / 255.0, (15, 15), 0)[:, :, np.newaxis]
    blurred_bg = cv2.GaussianBlur(img_rgb, (21, 21), 0)
    return (alpha * img_rgb + (1.0 - alpha) * blurred_bg).astype(np.uint8)

def preprocess_opsi_b(img_rgb):
    # 1. Pad & Resize 224x224
    resized = pad_and_resize(img_rgb, target_size=TARGET_SIZE)
    h, w = resized.shape[:2]
    # 2. Dull Razor
    hairless = remove_hair_dull_razor(resized, threshold=10)
    # 3. Active Contour
    mask, is_success = run_active_contour(hairless, h, w)
    # 4. Soft-Blend
    final_img = soft_blend(hairless, mask) if is_success else hairless
    return resized, hairless, mask, final_img

def plot_perbandingan(asli, resized, hairless, mask, segmented, index):
    fig, axes = plt.subplots(1, 5, figsize=(18, 4))
    axes[0].imshow(asli); axes[0].set_title(f"1. Asli (Sampel {index})"); axes[0].axis('off')
    axes[1].imshow(resized); axes[1].set_title("2. Resize (224x224)"); axes[1].axis('off')
    axes[2].imshow(hairless); axes[2].set_title("3. Dull Razor (No Hair)"); axes[2].axis('off')
    axes[3].imshow(mask, cmap='gray'); axes[3].set_title("4. Mask Snake"); axes[3].axis('off')
    axes[4].imshow(segmented); axes[4].set_title("5. Soft-Blended ROI"); axes[4].axis('off')
    plt.tight_layout()
    plt.show()

# =============================================================================
# OFFLINE PREPROCESSING (MULTI-THREADED PARALEL)
# =============================================================================
output_dir = "/kaggle/working/processed_images/"
os.makedirs(output_dir, exist_ok=True)

# 1. Visualisasi 3 Sampel Pertama sebagai Pengecekan Kualitas
print("[INFO] Menampilkan visualisasi 3 sampel citra pertama (Opsi B: 224x224):")
for index, row in df_final.head(3).iterrows():
    img_bgr = cv2.imread(row['filepath'])
    if img_bgr is not None:
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        resized, hairless, mask, final_img = preprocess_opsi_b(img_rgb)
        plot_perbandingan(img_rgb, resized, hairless, mask, final_img, index)

# 2. Fungsi Worker untuk Eksekusi Paralel Multi-Core
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
    _, _, _, final_img = preprocess_opsi_b(img_rgb)

    final_bgr = cv2.cvtColor(final_img, cv2.COLOR_RGB2BGR)
    cv2.imwrite(new_img_path, final_bgr)
    return index, new_img_path

# 3. Eksekusi Multi-Threaded dengan Seluruh CPU Cores
tasks = [(idx, row['filepath']) for idx, row in df_final.iterrows()]
num_workers = min(os.cpu_count() or 4, 8)
print(f"[INFO] Memproses {len(tasks)} citra secara paralel menggunakan {num_workers} worker CPU...")

with ThreadPoolExecutor(max_workers=num_workers) as executor:
    results = list(tqdm(executor.map(process_single_image, tasks), total=len(tasks)))

# 4. Susun Kembali Path Sesuai Indeks Asli
results.sort(key=lambda x: x[0])
df_final['filepath'] = [r[1] for r in results]
df_final.to_csv("/kaggle/working/processed_metadata_combined.csv", index=False)

print(f"\\n[INFO] Selesai! Sebanyak {len(results)} citra prapemrosesan Opsi B (224x224) siap digunakan.")
"""
        nb3["cells"][7]["source"] = [l + "\n" for l in c7_src.splitlines()]

        with open(p3, "w", encoding="utf-8") as f:
            json.dump(nb3, f, indent=1, ensure_ascii=False)
        print(f"Berhasil memperbarui {p3} ke Opsi B (224x224)")

if __name__ == "__main__":
    update_to_opsi_b()
