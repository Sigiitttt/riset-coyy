import json
from pathlib import Path

target_file = Path(r"C:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\4-4-irisan-ringkas-optimasi-8p8w-selesai.ipynb")

with open(target_file, "r", encoding="utf-8") as f:
    nb = json.load(f)

new_cell_19_source = """import gc
import ctypes

# Bersihkan variabel memori lama & paksa OS Linux bebaskan RAM
for _v in ['X_train', 'X_val', 'X_test', 'y_train', 'y_val', 'y_test', 'model', 'history']:
    if _v in globals():
        del globals()[_v]
gc.collect()
try:
    ctypes.CDLL('libc.so.6').malloc_trim(0)
except Exception:
    pass

import time
import csv

!pip install -q findspark pyarrow scikit-image opencv-python-headless
import findspark

findspark.init(str(SPARK_HOME))

import os
# Fix port gateway residual Kaggle
os.environ.pop('PYSPARK_GATEWAY_PORT', None)
os.environ.pop('PYSPARK_GATEWAY_SECRET', None)

from pyspark import SparkContext
if SparkContext._active_spark_context:
    SparkContext._active_spark_context.stop()

from pyspark.sql import SparkSession
# Hapus cache sesi lama agar konfigurasi worker baru terbaca
SparkSession._instantiatedSession = None
SparkSession._activeSession = None

from pyspark import StorageLevel

# Set jumlah executor dan paralelisme secara eksplisit sesuai NUM_WORKERS
spark = (
    SparkSession.builder
    .appName(f"skincancer-preprocessing-{SCENARIO_NAME}")
    .config("spark.executor.instances", str(NUM_WORKERS))
    .config("spark.default.parallelism", str(NUM_WORKERS))
    .getOrCreate()
)

print(f"Versi Spark: {spark.version}")
print(f"Master: {spark.sparkContext.master}")
print(f"Default Parallelism: {spark.sparkContext.defaultParallelism}")

# Executor mendaftar ke driver secara asinkron; tunggu sampai jumlahnya sesuai skenario.
# Tanpa verifikasi ini, kolom num_workers pada results.csv mencatat jumlah yang DIMINTA,
# bukan yang benar-benar dialokasikan YARN, sehingga grafik speedup bisa menyesatkan.
_t_alloc_start = time.time()
_deadline = time.time() + 120
active_executors = 0
while time.time() < _deadline:
    # PERBAIKAN: Menggunakan getExecutorMemoryStatus dari underlying Java SparkContext
    active_executors = spark.sparkContext._jsc.sc().getExecutorMemoryStatus().size() - 1
    if active_executors >= NUM_WORKERS:
        break
    time.sleep(3)

yarn_alloc_time_sec = time.time() - _t_alloc_start
print(f"Executor aktif: {active_executors} (target skenario: {NUM_WORKERS}) | Waktu Alokasi YARN: {yarn_alloc_time_sec:.2f} detik")

# Catat Waktu Alokasi Kontainer YARN ke results.csv (Sesuai Proposal Riset)
RESULTS_LOG_PATH = PROJECT_DIR / "results.csv"
LOG_COLUMNS = [
    "timestamp", "scenario", "num_workers", "num_partitions", "stage",
    "elapsed_sec", "image_count", "avg_cpu_percent", "avg_mem_mb",
    "accuracy", "f1_score", "loss", "roc_auc"
]
if not RESULTS_LOG_PATH.exists():
    with open(RESULTS_LOG_PATH, "w", newline="") as _f:
        csv.writer(_f).writerow(LOG_COLUMNS)

with open(RESULTS_LOG_PATH, "a", newline="") as _f:
    csv.writer(_f).writerow([
        time.strftime("%Y-%m-%d %H:%M:%S"),
        SCENARIO_NAME, NUM_WORKERS, NUM_PARTITIONS,
        "yarn_container_allocation", f"{yarn_alloc_time_sec:.2f}",
        "", "", "", "", "", "", ""
    ])
print(f"Log alokasi kontainer YARN ({yarn_alloc_time_sec:.2f}s) dicatat ke results.csv.")

assert active_executors == NUM_WORKERS, (
    f"YARN hanya mengalokasikan {active_executors} executor dari {NUM_WORKERS} yang diminta. "
    f"Hasil speedup tidak valid. Periksa kapasitas yarn-site.xml."
)

IMG_SIZE = 224

class_names = sorted(CLASS_NAMES)
label_to_index = {name: idx for idx, name in enumerate(class_names)}

print(f"Target Resolusi: {IMG_SIZE}x{IMG_SIZE} piksel (3 kanal RGB)")
print(f"Pemetaan Label ke Indeks: {label_to_index}")
"""

nb["cells"][19]["source"] = [l + "\n" for l in new_cell_19_source.splitlines()]
if nb["cells"][19]["source"]:
    nb["cells"][19]["source"][-1] = nb["cells"][19]["source"][-1].rstrip("\n")

with open(target_file, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("SUCCESS: Updated Cell 19 in 4-4-irisan-ringkas-optimasi-8p8w-selesai.ipynb")
