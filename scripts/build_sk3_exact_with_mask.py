"""
Builder to create an exact replica of sk3-bigdat-data2017-3kelas-ak85.ipynb
with only two requested changes:
1. Data loaded from /kaggle/input/datasets/nadiraanindita/ham10k-and-isic-2019
   (reads pre-split CSVs, both irisan 3-class and binary supported, with automatic Colab kagglehub support).
2. Preprocessing Active Contour Snake replaced with real mask segmentation
   (HAM10000 Tschandl mask + ISIC 2019 U-Net pseudo-mask).
All Spark configuration, multi-GPU strategy, Triplet Attention architecture,
oversampling, training 2-phase, and evaluation remain 100% identical to sk3.
"""

import json
from pathlib import Path

REF_PATH = Path("kode/7_referensi tugas sebelumnya/sk3-bigdat-data2017-3kelas-ak85.ipynb")
TARGET_PATH = Path("kode/5_segmentasi_unet/sk3-bigdat-ham2019-unetmask-ak85.ipynb")

ref_nb = json.load(open(REF_PATH, encoding="utf-8"))
cells = ref_nb["cells"]

def get_src(idx):
    return "".join(cells[idx]["source"])

new_cells = []

# Cell 0: Header & Imports (Identical to sk3 + auto-install kagglehub if needed)
cell_0_code = '''import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os

try:
    import kagglehub
except ImportError:
    os.system("pip install -q kagglehub")

for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))
'''
new_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": cell_0_code.splitlines(keepends=True)
})

# Cell 1: Markdown "# Inisialisasi spark" (Identical)
new_cells.append(cells[1])

# Cell 2: Spark Init (Identical to sk3: instances=2, cores=1, memory=1536m, overhead=384m, driver=2g)
new_cells.append(cells[2])

# Cell 3: Markdown "# Load dataset" (Identical)
new_cells.append(cells[3])

# Cell 4: Load Dataset (Modified: read from nadiraanindita datasets with dual Kaggle & Colab support)
cell_4_code = '''import os
import re
import time
import glob
import zipfile
import warnings
import pandas as pd
from pathlib import Path
from pyspark.sql.functions import col, when
from pyspark import TaskContext

warnings.filterwarnings('ignore')
spark.sparkContext.setLogLevel("ERROR")

# ==============================================================================
# KONFIGURASI TUGAS: "irisan" (3 KELAS) ATAU "binary" (2 KELAS)
# ==============================================================================
TASK = "irisan"  # Ganti "binary" jika ingin klasifikasi 2-kelas (Benign vs Malignant)

print(f"[INFO] Memproses Dataset Riset {TASK.upper()} (HAM10000 + ISIC 2019) dengan Masker Segmentasi...")

# Deteksi otomatis lingkungan: Colab vs Kaggle
IS_COLAB = os.path.exists("/content") and not os.path.exists("/kaggle/working")
WORK_DIR = Path("/content") if IS_COLAB else Path("/kaggle/working")

def get_dataset(slug):
    if IS_COLAB:
        import kagglehub
        return Path(kagglehub.dataset_download(f"nadiraanindita/{slug}"))
    return Path("/kaggle/input/datasets/nadiraanindita") / slug

DIR_SPLIT = get_dataset("ham10k-and-isic-2019")
DIR_HAM_IMG = get_dataset("dataset-riset-ham10k")
DIR_2019_IMG = get_dataset("dataset-riset-isic-2019")
DIR_HAM_MASK = get_dataset("ham-segmentations-lesion-riset-saya")
DIR_PSEUDO_ZIP = get_dataset("isic2019-pseudo-masks-zip")

print(f"Lingkungan aktif: {'Google Colab' if IS_COLAB else 'Kaggle'}")
print(f"Direktori Kerja : {WORK_DIR}")

# Helper pembaca CSV multi-encoding aman
def safe_read_csv(p):
    for enc in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
        try:
            return pd.read_csv(p, encoding=enc)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(p, encoding_errors='replace')

# 1. Pemuatan Manifest Split Resmi (Bebas Kebocoran)
if TASK == "irisan":
    suffix = "_3class.csv"
    label_map = {
        "nv": "nevus", "mel": "melanoma", "bkl": "seborrheic_keratosis",
        "nevus": "nevus", "melanoma": "melanoma", "seborrheic_keratosis": "seborrheic_keratosis"
    }
    target_labels = ["nevus", "melanoma", "seborrheic_keratosis"]
else:
    suffix = ".csv"
    label_map = {
        "benign": "benign", "malignant": "malignant",
        "0": "benign", "1": "malignant",
        0: "benign", 1: "malignant"
    }
    target_labels = ["benign", "malignant"]

dfs = []
for split_name in ["train", "val", "test"]:
    csv_matches = list(DIR_SPLIT.glob(f"**/{split_name}{suffix}"))
    if not csv_matches:
        # Fallback jika nama file tanpa suffix
        csv_matches = list(DIR_SPLIT.glob(f"**/{split_name}.csv"))
    
    assert csv_matches, f"File split {split_name} tidak ditemukan di {DIR_SPLIT}!"
    df_part = safe_read_csv(csv_matches[0])
    
    # Standarisasi kolom image_id
    if 'image_id' not in df_part.columns:
        for c in ['image', 'isic_id', 'Image', 'IMAGE']:
            if c in df_part.columns:
                df_part = df_part.rename(columns={c: 'image_id'})
                break
    df_part['image_id'] = df_part['image_id'].astype(str).str.strip().str.replace(r'\.jpg$', '', regex=True)
                
    # Standarisasi kolom label
    col_lbl = None
    if TASK == "irisan":
        for cand in ['label_3class', 'label_class', 'harmonized_label', 'class_name', 'label', 'original_label', 'dx']:
            if cand in df_part.columns:
                col_lbl = cand
                break
    else:
        for cand in ['label', 'binary_class', 'target_binary', 'label_binary']:
            if cand in df_part.columns:
                col_lbl = cand
                break
        if col_lbl in ['target_binary', 'label_binary']:
            df_part['binary_class'] = df_part[col_lbl].map({0: 'benign', 1: 'malignant'})
            col_lbl = 'binary_class'
            
    assert col_lbl is not None, f"Kolom label tidak ditemukan di {csv_matches[0].name}! Kolom tersedia: {list(df_part.columns)}"
    df_part['label'] = df_part[col_lbl].astype(str).str.strip().str.lower().map(label_map)
    df_part['split'] = split_name
    if 'source' not in df_part.columns:
        df_part['source'] = df_part['dataset'] if 'dataset' in df_part.columns else 'dataset'
        
    df_clean = df_part[['image_id', 'label', 'source', 'split']].dropna(subset=['label']).drop_duplicates(subset=['image_id'])
    dfs.append(df_clean)

df_manifest = pd.concat(dfs, ignore_index=True)
print(f"[INFO] Total manifest split termuat: {len(df_manifest):,} baris.")
print(pd.crosstab(df_manifest['split'], df_manifest['label'], margins=True))

# 2. Pengindeksan Path Citra Fisik
image_index = {}
for d in [DIR_HAM_IMG, DIR_2019_IMG]:
    if d.exists():
        for ext in ['*.jpg', '*.jpeg', '*.JPG', '*.JPEG']:
            for p in d.glob(f'**/{ext}'):
                image_index[p.stem] = str(p)

# 3. Pengindeksan Path Masker Fisik (Ekstrak ZIP Pseudo-Mask jika masih ZIP)
mask_index = {}
# A. Masker HAM10000 Dokter
if DIR_HAM_MASK.exists():
    for ext in ['*.png', '*.jpg', '*.PNG', '*.JPG']:
        for p in DIR_HAM_MASK.glob(f'**/{ext}'):
            clean_stem = re.sub(r'(_segmentation|_mask)$', '', p.stem)
            mask_index[clean_stem] = str(p)

# B. Pseudo-Mask ISIC 2019 (Ekstrak otomatis jika berupa ZIP)
if DIR_PSEUDO_ZIP.exists():
    zip_files = list(DIR_PSEUDO_ZIP.glob('**/*.zip'))
    if zip_files:
        unzip_dir = WORK_DIR / "isic2019_masks_extracted"
        if not unzip_dir.exists():
            unzip_dir.mkdir(parents=True, exist_ok=True)
            print(f"[INFO] Mengekstrak {zip_files[0].name} ke {unzip_dir}...")
            with zipfile.ZipFile(zip_files[0], 'r') as zf:
                zf.extractall(unzip_dir)
        for ext in ['*.png', '*.jpg', '*.PNG', '*.JPG']:
            for p in unzip_dir.glob(f'**/{ext}'):
                clean_stem = re.sub(r'(_segmentation|_mask)$', '', p.stem)
                if clean_stem not in mask_index:
                    mask_index[clean_stem] = str(p)
    else:
        for ext in ['*.png', '*.jpg', '*.PNG', '*.JPG']:
            for p in DIR_PSEUDO_ZIP.glob(f'**/{ext}'):
                clean_stem = re.sub(r'(_segmentation|_mask)$', '', p.stem)
                if clean_stem not in mask_index:
                    mask_index[clean_stem] = str(p)

print(f"[INFO] Indeks Citra: {len(image_index):,} file | Indeks Masker: {len(mask_index):,} file.")

# Pasangkan path citra dan masker ke df_manifest
df_manifest['filepath'] = df_manifest['image_id'].map(image_index)
df_manifest['mask_path'] = df_manifest['image_id'].map(mask_index)

# Filter hanya yang memiliki citra dan masker lengkap
df_final = df_manifest.dropna(subset=['filepath', 'mask_path']).reset_index(drop=True)
print(f"[INFO] Citra berpasangan lengkap siap diproses: {len(df_final):,} baris.")

# 4. Verifikasi dan Pelacakan Waktu Executor Spark (Sesuai Standar sk3)
spark_df = spark.createDataFrame(df_final[['image_id', 'label', 'split']])

def track_executor_time(iterator):
    start_time = time.time()
    count = sum(1 for _ in iterator)
    elapsed = time.time() - start_time
    ctx = TaskContext.get()
    pid = ctx.partitionId() if ctx else "Unknown"
    yield (pid, count, elapsed)

metrik_executors = spark_df.rdd.mapPartitions(track_executor_time).collect()
print("\\n=== LAPORAN BEBAN KERJA EXECUTOR SPARK ===")
for pid, count, elapsed in metrik_executors:
    print(f"Executor Task [Partisi {pid}] -> Memproses {count} baris dalam {elapsed:.4f} detik")
print("==========================================\\n")

# Tutup Spark Session untuk Melepas Memori RAM ke Sistem
spark.stop()
import gc
gc.collect()
print("[INFO] Spark Session ditutup, seluruh memori RAM dibebaskan untuk tahap pelatihan TensorFlow.")
'''
new_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": cell_4_code.splitlines(keepends=True)
})

# Cell 5: Visualisasi Distribusi (Identical logic to sk3)
cell_5_code = '''import matplotlib.pyplot as plt
import pandas as pd

# Menampilkan Ringkasan Distribusi Data
print(f"=== RINGKASAN DATASET ({TASK.upper()}) ===")
print(f"Total Citra Terdaftar: {len(df_final):,} citra\\n")

print("1. Distribusi Berdasarkan Kelas Medis:")
kelas_counts = df_final['label'].value_counts()
for k, v in kelas_counts.items():
    persen = (v / len(df_final)) * 100
    print(f"   - {k:<22}: {v:6d} citra ({persen:.2f}%)")

print("\\n2. Distribusi Berdasarkan Partisi Split:")
split_counts = df_final['split'].value_counts()
for s, v in split_counts.items():
    print(f"   - {s:<22}: {v:6d} citra")

# Visualisasi Distribusi Kelas
plt.figure(figsize=(8, 4))
colors = ['#2b5c8f', '#d95f02', '#7570b3', '#1b9e77'][:len(kelas_counts)]
bars = plt.bar(kelas_counts.index, kelas_counts.values, color=colors)
plt.title(f"Distribusi Citra Dataset {TASK.upper()} (Bebas Duplikat)", fontsize=12)
plt.ylabel("Jumlah Citra")
plt.grid(axis='y', linestyle='--', alpha=0.6)

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2.0, yval + 100, f"{yval:,}", ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.show()
'''
new_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": cell_5_code.splitlines(keepends=True)
})

# Cell 6: Markdown "# preprosesing citra" (Identical)
new_cells.append(cells[6])

# Cell 7: Preprocessing (Lesion ROI Crop + Hair Removal + CLAHE)
cell_7_code = '''# ==========================================
# TAHAP 3: REKAYASA CITRA (ROI CROP + HAIR REMOVAL + CLAHE)
# PIPELINE: HAIR REMOVAL -> LESION ROI CROP (15% PADDING) -> CLAHE -> PAD & RESIZE 224
# ==========================================
import os
import cv2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

cv2.setNumThreads(1)
TARGET_SIZE = 224
REF_SIZE = 600

def remove_hair(img_rgb):
    """Black-hat (ukuran kernel ikut resolusi) -> threshold -> dilasi -> inpainting."""
    h, w = img_rgb.shape[:2]
    k = max(9, int(round(9 * max(h, w) / REF_SIZE)) | 1)
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (k, k))
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
    _, hair_mask = cv2.threshold(blackhat, 10, 255, cv2.THRESH_BINARY)
    hair_mask = cv2.dilate(
        hair_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=1
    )
    return cv2.inpaint(img_rgb, hair_mask, 3, cv2.INPAINT_TELEA)

def crop_lesion_roi(img_rgb, mask_path, padding_ratio=0.15):
    """
    Menggunakan mask untuk mencari bounding box lesi,
    kemudian crop dengan padding 15% agar tetap ada konteks kulit sehat di sekitarnya.
    """
    h, w = img_rgb.shape[:2]
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        return img_rgb, np.full((h, w), 255, dtype=np.uint8)

    if mask.shape != (h, w):
        mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_LINEAR)

    mask_bin = (mask > 127).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_clean = cv2.morphologyEx(mask_bin, cv2.MORPH_CLOSE, kernel)

    ys, xs = np.where(mask_clean > 0)
    if len(xs) == 0 or len(ys) == 0:
        return img_rgb, mask_clean

    x1, x2 = xs.min(), xs.max()
    y1, y2 = ys.min(), ys.max()

    lesion_w = x2 - x1 + 1
    lesion_h = y2 - y1 + 1

    pad_x = int(lesion_w * padding_ratio)
    pad_y = int(lesion_h * padding_ratio)

    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(w, x2 + pad_x + 1)
    y2 = min(h, y2 + pad_y + 1)

    roi = img_rgb[y1:y2, x1:x2]
    return roi, mask_clean

def apply_enhancement(img_rgb):
    """ CLAHE untuk penajaman tekstur lesi (Tanpa Blur) """
    img = img_rgb.astype('uint8')
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    clahe_img = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
    return clahe_img

def pad_and_resize(img, target_size=224, is_mask=False):
    """ Letterbox padding reflect agar lesi tidak terdistorsi/gepeng """
    h, w = img.shape[:2]
    max_dim = max(h, w)
    top, bottom = (max_dim - h) // 2, (max_dim - h) - ((max_dim - h) // 2)
    left, right = (max_dim - w) // 2, (max_dim - w) - ((max_dim - w) // 2)
    border_mode = cv2.BORDER_CONSTANT if is_mask else cv2.BORDER_REFLECT
    padded = cv2.copyMakeBorder(img, top, bottom, left, right, border_mode)
    interp = cv2.INTER_LINEAR if is_mask else cv2.INTER_AREA
    return cv2.resize(padded, (target_size, target_size), interpolation=interp)

def plot_perbandingan(asli, bersih, mask, roi, final_img, index):
    """ Menampilkan plot 5 tahap preprocessing berdampingan """
    fig, axes = plt.subplots(1, 5, figsize=(18, 4))
    axes[0].imshow(asli)
    axes[0].set_title(f"1. Asli (Img {index})")
    axes[0].axis('off')

    axes[1].imshow(bersih)
    axes[1].set_title("2. Tanpa Rambut")
    axes[1].axis('off')

    axes[2].imshow(mask, cmap='gray')
    axes[2].set_title("3. Mask U-Net / Dokter")
    axes[2].axis('off')

    axes[3].imshow(roi)
    axes[3].set_title("4. ROI Crop (Pad 15%)")
    axes[3].axis('off')

    axes[4].imshow(final_img)
    axes[4].set_title("5. CLAHE + Resize (224x224)")
    axes[4].axis('off')

    plt.tight_layout()
    plt.show()

# ==========================================
# OFFLINE PREPROCESSING (MULTI-THREADED PARALEL)
# ==========================================

output_dir = str(WORK_DIR / "processed_images_roi") + "/"
os.makedirs(output_dir, exist_ok=True)

# 1. Visualisasi 3 Sampel Pertama sebagai Pengecekan Kualitas
print("[INFO] Menampilkan visualisasi 3 sampel citra pertama:")
for index, row in df_final.head(3).iterrows():
    img_bgr = cv2.imread(row['filepath'])
    if img_bgr is not None:
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        clean_img = remove_hair(img_rgb)
        roi_img, mask_full = crop_lesion_roi(clean_img, row['mask_path'], padding_ratio=0.15)
        enhanced_roi = apply_enhancement(roi_img)
        final_img = pad_and_resize(enhanced_roi, target_size=TARGET_SIZE, is_mask=False)
        plot_perbandingan(img_rgb, clean_img, mask_full, roi_img, final_img, index)

# 2. Fungsi Worker untuk Eksekusi Paralel Multi-Core
def process_single_image(args):
    index, img_path, mask_path = args
    filename = f"{index}_{os.path.basename(img_path)}"
    new_img_path = os.path.join(output_dir, filename)

    if os.path.exists(new_img_path):
        return index, new_img_path

    img = cv2.imread(img_path)
    if img is None:
        return index, img_path

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    clean_img = remove_hair(img)
    roi_img, _ = crop_lesion_roi(clean_img, mask_path, padding_ratio=0.15)
    enhanced_roi = apply_enhancement(roi_img)
    final_img = pad_and_resize(enhanced_roi, target_size=TARGET_SIZE, is_mask=False)

    final_bgr = cv2.cvtColor(final_img, cv2.COLOR_RGB2BGR)
    cv2.imwrite(new_img_path, final_bgr)
    return index, new_img_path

# 3. Jalankan Eksekusi Multi-Threaded dengan Seluruh CPU Cores
tasks = [(idx, row['filepath'], row['mask_path']) for idx, row in df_final.iterrows()]
num_workers = os.cpu_count() or 4
print(f"[INFO] Memproses {len(tasks):,} gambar secara paralel menggunakan {num_workers} worker CPU...")

with ThreadPoolExecutor(max_workers=num_workers) as executor:
    results = list(tqdm(executor.map(process_single_image, tasks), total=len(tasks)))

# 4. Susun Kembali Path Sesuai Indeks Asli
results.sort(key=lambda x: x[0])
df_final['filepath'] = [r[1] for r in results]
df_final.to_csv(str(WORK_DIR / "processed_metadata_combined.csv"), index=False)

print(f"\\n[INFO] Selesai! Sebanyak {len(results):,} citra tersegmentasi siap digunakan.")
'''
new_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": cell_7_code.splitlines(keepends=True)
})

# Cell 8: Markdown "## cek hasil" (Identical)
new_cells.append(cells[8])

# Cell 9: Cek Dimensi Hasil (Identical)
new_cells.append(cells[9])

# Cell 10: Markdown "# split dataset" (Identical)
new_cells.append(cells[10])

# Cell 11: Split Dataset (Modified: Read official split from metadata without re-splitting, then exact same oversampling & generators)
cell_11_code = '''# ==========================================
# TAHAP 4: PIPELINE DISTRIBUSI & OVERSAMPLING
# (MEMAKAI SPLIT RESMI ANTI-KEBOCORAN: TRAIN / VAL / TEST)
# ==========================================

from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.utils import resample
import numpy as np
import pandas as pd

# ----------------------------------------------------
# 1. MEMUAT SPLIT RESMI (TRAIN / VAL / TEST)
# ----------------------------------------------------
train_df = df_final[df_final['split'] == 'train'].reset_index(drop=True)
val_df = df_final[df_final['split'] == 'val'].reset_index(drop=True)
test_df = df_final[df_final['split'] == 'test'].reset_index(drop=True)

# Verifikasi Keamanan Anti-Kebocoran
assert not (set(train_df['image_id']) & set(val_df['image_id'])), "Data Leakage terdeteksi antara Train dan Val!"
assert not (set(train_df['image_id']) & set(test_df['image_id'])), "Data Leakage terdeteksi antara Train dan Test!"
assert not (set(val_df['image_id']) & set(test_df['image_id'])), "Data Leakage terdeteksi antara Val dan Test!"

print("=== RINGKASAN PEMBAGIAN DATA (RESMI) ===")
print(f"Jumlah data Train      : {len(train_df):,}")
print(f"Jumlah data Validation : {len(val_df):,}")
print(f"Jumlah data Test       : {len(test_df):,}\\n")

# ----------------------------------------------------
# 2. OVERSAMPLING SEMUA KELAS MINORITAS
# ----------------------------------------------------
max_count = train_df['label'].value_counts().max()
dfs_balanced = []

for kelas in sorted(train_df['label'].unique()):
    df_kelas = train_df[train_df['label'] == kelas]
    if len(df_kelas) < max_count:
        df_kelas_upsampled = resample(
            df_kelas,
            replace=True,
            n_samples=max_count,
            random_state=42
        )
        dfs_balanced.append(df_kelas_upsampled)
    else:
        dfs_balanced.append(df_kelas)

# Menggabungkan data yang sudah seimbang
train_df_balanced = pd.concat(dfs_balanced)

# Mengacak urutan baris agar tidak menumpuk
train_df_balanced = train_df_balanced.sample(
    frac=1, random_state=42
).reset_index(drop=True)

print("=== DISTRIBUSI TRAIN SET (OVERSAMPLED) ===")
print(train_df_balanced['label'].value_counts().to_string())
print("\\n==========================================\\n")

# ----------------------------------------------------
# 3. KONFIGURASI AUGMENTASI TINGKAT LANJUT
# ----------------------------------------------------
train_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    rotation_range=15,             # Rotasi -15 s/d +15 derajat (Jurnal LA-CapsNet)
    brightness_range=[0.7, 1.3],   # Pengaturan kecerahan & kontras 0.7 - 1.3
    horizontal_flip=True,          # Flip horizontal acak
    vertical_flip=True,            # Flip vertikal acak
    zoom_range=0.15,               # Random crop / zoom
    width_shift_range=0.1,         # Shift horizontal
    height_shift_range=0.1,        # Shift vertikal
    fill_mode='reflect'         
)

# Validation dan Test HANYA di-preprocess, TIDAK di-augmentasi
val_test_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input
)

# ----------------------------------------------------
# 4. PEMBUATAN BATCH DATA (RESIZE & DISTRIBUSI)
# ----------------------------------------------------
target_dim = (224, 224) 
batch_sz = 32            

train_data = train_datagen.flow_from_dataframe(
    dataframe=train_df_balanced, 
    x_col="filepath", 
    y_col="label",
    target_size=target_dim, 
    batch_size=batch_sz,
    class_mode="categorical",
    shuffle=True
)

val_data = val_test_datagen.flow_from_dataframe(
    dataframe=val_df, 
    x_col="filepath", 
    y_col="label",
    target_size=target_dim, 
    batch_size=batch_sz,
    class_mode="categorical",
    shuffle=False
)

# Generator baru untuk evaluasi akhir (Blind Test)
test_data = val_test_datagen.flow_from_dataframe(
    dataframe=test_df, 
    x_col="filepath", 
    y_col="label",
    target_size=target_dim, 
    batch_size=batch_sz,
    class_mode="categorical",
    shuffle=False
)
'''
new_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": cell_11_code.splitlines(keepends=True)
})

# Cell 12: Markdown "## cek hasil" (Identical)
new_cells.append(cells[12])

# Cell 13: Cek Generator (Identical)
new_cells.append(cells[13])

# Cell 14: Markdown "# Modeling" (Identical)
new_cells.append(cells[14])

# Cell 15: Modeling (ResNet50 + Triplet Attention, dynamic NUM_CLASSES)
cell_15_code = get_src(15)
cell_15_code = cell_15_code.replace("Dense(3, activation='softmax')", "Dense(len(train_data.class_indices), activation='softmax')")
new_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": cell_15_code.splitlines(keepends=True)
})

# Cell 16: Markdown "# Training" (Identical)
new_cells.append(cells[16])

# Cell 17: Training (Identical, dynamic num_labels, dynamic checkpoint path)
cell_17_code = get_src(17)
cell_17_code = cell_17_code.replace("num_labels=3", "num_labels=len(train_data.class_indices)")
cell_17_code = cell_17_code.replace("filepath='/kaggle/working/best_melanoma_model.keras'", "filepath=str(WORK_DIR / 'best_melanoma_model.keras')")
new_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": cell_17_code.splitlines(keepends=True)
})

# Cell 18: Markdown "# Evaluasi" (Identical)
new_cells.append(cells[18])

# Cell 19: Evaluasi (Identical, dynamic checkpoint path)
cell_19_code = get_src(19)
cell_19_code = cell_19_code.replace("'/kaggle/working/best_melanoma_model.keras'", "str(WORK_DIR / 'best_melanoma_model.keras')")
new_cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": cell_19_code.splitlines(keepends=True)
})

out_nb = {
    "cells": new_cells,
    "metadata": {
        "accelerator": "GPU",
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

with open(TARGET_PATH, "w", encoding="utf-8") as f:
    json.dump(out_nb, f, indent=1, ensure_ascii=False)

print(f"File berhasil dibuat: {TARGET_PATH} ({len(new_cells)} sel, persis sk3).")
