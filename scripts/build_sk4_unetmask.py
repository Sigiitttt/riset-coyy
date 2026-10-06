import json
from pathlib import Path

REF = Path("kode/7_referensi tugas sebelumnya/sk3-bigdat-data2017-3kelas-ak85.ipynb")
OUT = Path("kode/5_segmentasi_unet/sk4-ham2019-unetmask-ak85.ipynb")

ref = json.load(open(REF, encoding="utf-8"))["cells"]


def ref_src(i):
    return "".join(ref[i]["source"])


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": text.strip("\n").splitlines(keepends=True)}


def swap(src, old, new):
    assert old in src, old
    return src.replace(old, new)


cells = []

cells.append(md("""# Klasifikasi Lesi Kulit: ResNet-50 + Triplet Attention (Split HAM10k + ISIC 2019, Masker U-Net)

* Dataset: split `ham10k-and-isic-2019` (train/val/test bebas kebocoran, tidak di-split ulang).
* Preprocessing: pad-resize 224, normalisasi kontras, segmentasi soft-blend dengan masker.
* Masker: HAM10000 dari Tschandl, ISIC 2019 dari pseudo-mask U-Net (Val Dice 0,9368).
* Arsitektur, loss, dan fase pelatihan sama dengan `sk3-bigdat-data2017-3kelas-ak85`.
* Dioptimalkan untuk GPU A100: mixed precision, batch 64, data di RAM, augmentasi di GPU.
* Ubah `TASK` di sel konfigurasi: `irisan` (3 kelas) atau `binary` (2 kelas)."""))

cells.append(md("# Konfigurasi"))
cells.append(code('''
!pip install -q kagglehub
import os
from pathlib import Path

TASK = "irisan"   # "irisan" (3 kelas) atau "binary" (2 kelas)

IS_COLAB = os.path.exists("/content") and not os.path.exists("/kaggle/working")
WORK_DIR = Path("/content") if IS_COLAB else Path("/kaggle/working")


def get_dataset(slug):
    if IS_COLAB:
        import kagglehub
        return Path(kagglehub.dataset_download(f"nadiraanindita/{slug}"))
    return Path("/kaggle/input/datasets/nadiraanindita") / slug


DIR_SPLIT = get_dataset("ham10k-and-isic-2019")
DIR_HAM = get_dataset("dataset-riset-ham10k")
DIR_2019 = get_dataset("dataset-riset-isic-2019")
DIR_HAM_MASK = get_dataset("ham-segmentations-lesion-riset-saya")
DIR_PSEUDO = get_dataset("isic2019-pseudo-masks-zip")

NUM_WORKERS = 2      # jumlah worker Spark (local[N])
NUM_PARTITIONS = 2   # jumlah partisi data Spark
IMG_SIZE = 224
BATCH_SIZE = 64
BG_KEEP = 0.2        # sisa intensitas latar di luar lesi (0 = hitam penuh, 1 = tanpa segmentasi)
PROC_DIR = WORK_DIR / "processed_images"
PROC_DIR.mkdir(parents=True, exist_ok=True)
CKPT_PATH = str(WORK_DIR / "best_model_ak85.keras")

if TASK == "irisan":
    LABEL_COL, SUFFIX = "harmonized_label", "_3class.csv"
    LABEL_MAP = {"nv": "nevus", "mel": "melanoma", "bkl": "seborrheic_keratosis"}
else:
    LABEL_COL, SUFFIX = "binary_class", ".csv"
    LABEL_MAP = {"benign": "benign", "malignant": "malignant"}
NUM_CLASSES = len(LABEL_MAP)
print(f"Colab={IS_COLAB} | TASK={TASK} | kelas={list(LABEL_MAP.values())}")
'''))

cells.append(md("# Inisialisasi spark"))
cells.append(code('''
!pip install pyspark -q

import os
import tensorflow as tf
from pyspark.sql import SparkSession

print("Daftar Perangkat Fisik GPU:")
print(tf.config.list_physical_devices('GPU'))
print("-" * 40)

tf.keras.mixed_precision.set_global_policy("mixed_float16")
print("Mixed precision aktif:", tf.keras.mixed_precision.global_policy().name)

spark = SparkSession.builder \\
    .appName("SkinCancer_BigData_UNetMask") \\
    .master(f"local[{NUM_WORKERS}]") \\
    .config("spark.default.parallelism", str(NUM_PARTITIONS)) \\
    .config("spark.driver.memory", "8g") \\
    .config("spark.driver.maxResultSize", "2g") \\
    .config("spark.sql.shuffle.partitions", "8") \\
    .getOrCreate()

print(f"Spark Session siap: {NUM_WORKERS} worker, {NUM_PARTITIONS} partisi.")
'''))

cells.append(md("# Load dataset"))
cells.append(code('''
import os, re, time, zipfile, warnings
import pandas as pd
from pyspark import TaskContext

warnings.filterwarnings("ignore")
spark.sparkContext.setLogLevel("ERROR")


def safe_read_csv(path):
    for enc in ["utf-8", "latin-1", "cp1252"]:
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(path, encoding_errors="replace")


def load_split(name):
    hits = [p for p in DIR_SPLIT.rglob(f"{name}{SUFFIX}")]
    assert hits, f"{name}{SUFFIX} tidak ditemukan di {DIR_SPLIT}"
    df = safe_read_csv(hits[0])
    if "image_id" not in df.columns:
        df = df.rename(columns={next(c for c in df.columns if c.lower() in ("image", "isic_id")): "image_id"})
    if LABEL_COL not in df.columns and TASK == "binary" and "target_binary" in df.columns:
        df[LABEL_COL] = df["target_binary"].map({0: "benign", 1: "malignant"})
    assert LABEL_COL in df.columns, f"Kolom {LABEL_COL} tidak ada. Kolom tersedia: {list(df.columns)}"
    df["label"] = df[LABEL_COL].astype(str).str.strip().str.lower().map(LABEL_MAP)
    df["split"] = name
    if "source" not in df.columns:
        df["source"] = "unknown"
    return df[["image_id", "label", "source", "split"]].dropna(subset=["label"]).drop_duplicates("image_id")


df_split = pd.concat([load_split(n) for n in ["train", "val", "test"]], ignore_index=True)
print(f"[INFO] Manifest split: {len(df_split)} baris")
print(df_split.groupby(["split", "label"]).size().unstack(fill_value=0))


def index_files(root, exts):
    found = {}
    for r, _, files in os.walk(root):
        for f in files:
            stem, ext = os.path.splitext(f)
            if ext.lower() in exts:
                found.setdefault(re.sub(r"_segmentation$", "", stem), os.path.join(r, f))
    return found


image_index = {**index_files(DIR_2019, {".jpg", ".jpeg"}), **index_files(DIR_HAM, {".jpg", ".jpeg"})}

pseudo_zips = list(DIR_PSEUDO.rglob("*.zip"))
if pseudo_zips:
    pseudo_dir = WORK_DIR / "pseudo_masks"
    pseudo_dir.mkdir(exist_ok=True)
    for z in pseudo_zips:
        with zipfile.ZipFile(z) as zf:
            zf.extractall(pseudo_dir)
    pseudo_root = pseudo_dir
else:
    pseudo_root = DIR_PSEUDO
mask_pseudo = index_files(pseudo_root, {".png"})
mask_ham = index_files(DIR_HAM_MASK, {".png"})
mask_index = {**mask_pseudo, **mask_ham}
print(f"[INFO] Citra: {len(image_index)} | Masker HAM: {len(mask_ham)} | Pseudo-mask 2019: {len(mask_pseudo)}")

df_split["filepath"] = df_split["image_id"].map(image_index)
df_split["mask_path"] = df_split["image_id"].map(mask_index)
ok = df_split["filepath"].notna() & df_split["mask_path"].notna()
print("\\n=== Baris dibuang (citra atau masker tidak ada) ===")
print(df_split[~ok].groupby(["source", "split"]).size().to_string() or "tidak ada")
df_final = df_split[ok].reset_index(drop=True)
print(f"[INFO] Siap diproses: {len(df_final)} dari {len(df_split)} baris")


def track_executor_time(iterator):
    start = time.time()
    n = sum(1 for _ in iterator)
    ctx = TaskContext.get()
    yield (ctx.partitionId() if ctx else -1, n, time.time() - start)


spark_df = spark.createDataFrame(df_final[["image_id", "label", "split"]])
print("\\n=== BEBAN KERJA EXECUTOR SPARK ===")
for pid, n, t in spark_df.rdd.mapPartitions(track_executor_time).collect():
    print(f"Partisi {pid}: {n} baris, {t:.4f} detik")

'''))

cells.append(code('''
import matplotlib.pyplot as plt

print(f"=== RINGKASAN DATASET ({TASK.upper()}) ===")
print(f"Total citra: {len(df_final)}\\n")
print(pd.crosstab(df_final["split"], df_final["label"], margins=True))
print()
print(pd.crosstab(df_final["source"], df_final["split"], margins=True))

counts = df_final["label"].value_counts()
plt.figure(figsize=(8, 4))
bars = plt.bar(counts.index, counts.values, color=["#2b5c8f", "#d95f02", "#7570b3"][:len(counts)])
plt.title(f"Distribusi Kelas ({TASK})")
plt.ylabel("Jumlah Citra")
plt.grid(axis="y", linestyle="--", alpha=0.6)
for b in bars:
    plt.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{int(b.get_height()):,}", ha="center", va="bottom")
plt.tight_layout()
plt.show()
'''))

cells.append(md("# preprosesing citra (resize, normalisasi kontras, segmentasi masker U-Net)"))
cells.append(code('''
import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from pyspark.sql import SparkSession


def pad_and_resize(img, size, interp, border):
    h, w = img.shape[:2]
    m = max(h, w)
    top, left = (m - h) // 2, (m - w) // 2
    padded = cv2.copyMakeBorder(img, top, m - h - top, left, m - w - left, border)
    return cv2.resize(padded, (size, size), interpolation=interp)


def contrast_stretching_norm(img, n0=128.0, var0=4000.0):
    img_f = img.astype(np.float32)
    out = []
    for c in range(3):
        ch = img_f[..., c]
        m, var = ch.mean(), ch.var() + 1e-6
        coeff = np.sqrt(var0 * (ch - m) ** 2 / var)
        out.append(np.where(ch > m, n0 + coeff, n0 - coeff))
    return np.clip(np.stack(out, axis=-1), 0, 255).astype(np.uint8)


def soft_segment(img, mask_bin, bg_keep=BG_KEEP):
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    m = cv2.dilate(mask_bin.astype(np.float32), k)
    m = cv2.GaussianBlur(m, (0, 0), 5)
    weight = bg_keep + (1.0 - bg_keep) * m
    return np.clip(img.astype(np.float32) * weight[..., None], 0, 255).astype(np.uint8)


def run_pipeline(img_path, mask_path):
    bgr = cv2.imread(img_path)
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    if bgr is None or mask is None:
        return None
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    h, w = rgb.shape[:2]
    if mask.shape != (h, w):
        mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_LINEAR)
    resized = pad_and_resize(rgb, IMG_SIZE, cv2.INTER_AREA, cv2.BORDER_REFLECT)
    mask_r = pad_and_resize(mask, IMG_SIZE, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT)
    mask_bin = (mask_r > 127).astype(np.uint8)
    normed = contrast_stretching_norm(resized)
    return rgb, resized, normed, mask_bin, soft_segment(normed, mask_bin)


print("[INFO] Sampel per sumber:")
for src, grp in df_final.groupby("source"):
    row = grp.iloc[0]
    res = run_pipeline(row["filepath"], row["mask_path"])
    if res is None:
        continue
    rgb, resized, normed, mask_bin, seg = res
    fig, axes = plt.subplots(1, 5, figsize=(18, 4))
    for ax, im, t in zip(axes, [rgb, resized, normed, mask_bin, seg],
                         ["Asli", f"Resize {IMG_SIZE}", "Normalisasi Kontras", "Masker", "Hasil Segmentasi"]):
        ax.imshow(im, cmap="gray" if im.ndim == 2 else None)
        ax.set_title(f"{t}\\n{src}" if t == "Asli" else t)
        ax.axis("off")
    plt.tight_layout()
    plt.show()


def process_partition(rows):
    import time
    start = time.time()
    out = []
    for idx, image_id, img_path, mask_path in rows:
        out_path = PROC_DIR / f"{image_id}.jpg"
        if not out_path.exists():
            res = run_pipeline(img_path, mask_path)
            if res is None:
                out.append((idx, None))
                continue
            cv2.imwrite(str(out_path), cv2.cvtColor(res[4], cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 95])
        out.append((idx, str(out_path)))
    yield (len(out), time.time() - start, out)


spark = SparkSession.builder.getOrCreate()
tasks = [(i, r.image_id, r.filepath, r.mask_path) for i, r in df_final.iterrows()]
print(f"[INFO] Spark memproses {len(tasks)} citra: {NUM_WORKERS} worker, {NUM_PARTITIONS} partisi...")
t0 = time.time()
parts = spark.sparkContext.parallelize(tasks, NUM_PARTITIONS).mapPartitions(process_partition).collect()
elapsed_prep = time.time() - t0

print("\\n=== BEBAN KERJA PREPROCESSING SPARK ===")
for k, (n, t, _) in enumerate(parts):
    print(f"Partisi {k}: {n} citra, {t:.1f} detik")
print(f"Total waktu preprocessing: {elapsed_prep:.1f} detik")
results = [r for _, _, rows in parts for r in rows]

spark.stop()
import gc
gc.collect()
print("[INFO] Spark ditutup, RAM dibebaskan untuk TensorFlow.")

df_final["filepath"] = [p for _, p in sorted(results)]
failed = df_final["filepath"].isna().sum()
df_final = df_final.dropna(subset=["filepath"]).reset_index(drop=True)
df_final.to_csv(WORK_DIR / f"processed_metadata_{TASK}.csv", index=False)
print(f"[INFO] Selesai. Berhasil: {len(df_final)} | gagal: {failed}")
'''))

cells.append(md("## cek hasil"))
cells.append(code(ref_src(9)))

cells.append(md("# split dataset (pakai split resmi) dan pipeline data di RAM"))
cells.append(code('''
import math
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.applications.resnet50 import preprocess_input
from sklearn.utils import resample

train_df = df_final[df_final["split"] == "train"].reset_index(drop=True)
val_df = df_final[df_final["split"] == "val"].reset_index(drop=True)
test_df = df_final[df_final["split"] == "test"].reset_index(drop=True)

assert not (set(train_df.image_id) & set(val_df.image_id)), "Bocor train-val"
assert not (set(train_df.image_id) & set(test_df.image_id)), "Bocor train-test"
assert not (set(val_df.image_id) & set(test_df.image_id)), "Bocor val-test"

print("=== RINGKASAN PEMBAGIAN DATA ===")
print(f"Train: {len(train_df)} | Validation: {len(val_df)} | Test: {len(test_df)}\\n")

CLASS_NAMES = sorted(df_final["label"].unique())
class_idx = {c: i for i, c in enumerate(CLASS_NAMES)}
assert len(CLASS_NAMES) == NUM_CLASSES

train_df["pos"] = np.arange(len(train_df))
max_count = train_df["label"].value_counts().max()
dfs_balanced = []
for kelas in CLASS_NAMES:
    df_kelas = train_df[train_df["label"] == kelas]
    if len(df_kelas) < max_count:
        df_kelas = resample(df_kelas, replace=True, n_samples=max_count, random_state=42)
    dfs_balanced.append(df_kelas)
train_df_balanced = pd.concat(dfs_balanced).sample(frac=1, random_state=42).reset_index(drop=True)
print("=== DISTRIBUSI TRAIN SET (OVERSAMPLED) ===")
print(train_df_balanced["label"].value_counts().to_string())


workers = min(os.cpu_count() or 4, 16)


def load_rgb(path):
    return cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)


def load_array(df):
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return np.stack(list(tqdm(ex.map(load_rgb, df["filepath"]), total=len(df))))


print("\\n[INFO] Memuat citra ke RAM (uint8)...")
X_train_uni = load_array(train_df)
X_train = X_train_uni[train_df_balanced["pos"].to_numpy()]
del X_train_uni
X_val, X_test = load_array(val_df), load_array(test_df)
assert X_train.shape[1:] == (IMG_SIZE, IMG_SIZE, 3)

y_train_idx = train_df_balanced["label"].map(class_idx).to_numpy()
y_val_idx = val_df["label"].map(class_idx).to_numpy()
y_test_idx = test_df["label"].map(class_idx).to_numpy()
eye = np.eye(NUM_CLASSES, dtype=np.float32)
print(f"X_train {X_train.shape} | X_val {X_val.shape} | X_test {X_test.shape}")

augment = tf.keras.Sequential([
    layers.RandomFlip("horizontal_and_vertical"),
    layers.RandomRotation(15 / 360, fill_mode="reflect"),
    layers.RandomZoom(0.15, fill_mode="reflect"),
    layers.RandomTranslation(0.1, 0.1, fill_mode="reflect"),
    layers.RandomBrightness(0.3, value_range=(0, 255)),
])


class BatchSeq(tf.keras.utils.Sequence):
    def __init__(self, X, y_idx, batch_size, train=False):
        super().__init__()
        self.X, self.y, self.bs, self.train = X, eye[y_idx], batch_size, train
        self.order = np.arange(len(X))
        if train:
            np.random.shuffle(self.order)

    def __len__(self):
        return math.ceil(len(self.X) / self.bs)

    def __getitem__(self, i):
        if i >= len(self):
            raise IndexError(i)
        idx = self.order[i * self.bs:(i + 1) * self.bs]
        x = tf.constant(self.X[idx], dtype=tf.float32)
        if self.train:
            x = augment(x, training=True)
        return preprocess_input(x).numpy(), self.y[idx]

    def on_epoch_end(self):
        if self.train:
            np.random.shuffle(self.order)


train_data = BatchSeq(X_train, y_train_idx, BATCH_SIZE, train=True)
val_data = BatchSeq(X_val, y_val_idx, BATCH_SIZE)
test_data = BatchSeq(X_test, y_test_idx, BATCH_SIZE)
print(f"Batch: train {len(train_data)} | val {len(val_data)} | test {len(test_data)}")
'''))

cells.append(md("## cek hasil"))
cells.append(code(swap(swap(ref_src(13),
                            "images, labels = next(iter(train_data))",
                            "images, labels = train_data[0]"),
                       "class_labels = list(train_data.class_indices.keys())",
                       "class_labels = CLASS_NAMES")))

cells.append(md("# Modeling"))
model_src = swap(ref_src(15), "Dense(3, activation='softmax')", "Dense(NUM_CLASSES, activation='softmax', dtype='float32')")
model_src = swap(model_src, "# OUTPUT 3-KELAS: softmax untuk klasifikasi multi-kelas", "# OUTPUT: softmax float32 sesuai NUM_CLASSES")
cells.append(code(model_src))

cells.append(md("# Training"))
train_src = swap(ref_src(17), "num_labels=3", "num_labels=NUM_CLASSES")
train_src = swap(train_src, "'/kaggle/working/best_melanoma_model.keras'", "CKPT_PATH")
cells.append(code(train_src))

cells.append(md("# Evaluasi"))
eval_src = swap(ref_src(19), "'/kaggle/working/best_melanoma_model.keras'", "CKPT_PATH")
eval_src = swap(eval_src, "val_data, steps=len(val_data), verbose=0", "val_data, verbose=0")
eval_src = swap(eval_src, "test_data, steps=len(test_data), verbose=0", "test_data, verbose=0")
eval_src = swap(eval_src, "y_true_val = np.array(val_data.classes)", "y_true_val = y_val_idx")
eval_src = swap(eval_src, "y_true_test = np.array(test_data.classes)", "y_true_test = y_test_idx")
eval_src = swap(eval_src, "target_names = list(val_data.class_indices.keys())", "target_names = CLASS_NAMES")
eval_src = "\n".join(l for l in eval_src.split("\n") if not l.strip().startswith(("val_data.reset", "test_data.reset")))
cells.append(code(eval_src))

nb = {
    "cells": cells,
    "metadata": {"accelerator": "GPU",
                 "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                 "language_info": {"name": "python"}},
    "nbformat": 4,
    "nbformat_minor": 5,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
json.dump(nb, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(f"Notebook dibuat: {OUT} ({len(cells)} sel)")
