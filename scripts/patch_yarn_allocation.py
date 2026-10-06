import json
from pathlib import Path

files = [
    Path(r'c:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\kode\4_Spark_on_Yarn\4.4-ringkas-optimasi\sk1-irisan-tipe1-ringkas-optimasi.ipynb'),
    Path(r'c:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\kode\4_Spark_on_Yarn\4.4-ringkas-optimasi\sk2-biner-tipe1-ringkas-optimasi.ipynb'),
    Path(r'c:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\kode\4_Spark_on_Yarn\4.6-ringkas-optimasi-prepjurnal\sk1-irisan-tipe1-ringkas-prepjurnal.ipynb'),
    Path(r'c:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\kode\4_Spark_on_Yarn\4.6-ringkas-optimasi-prepjurnal\sk2-biner-tipe1-ringkas-prepjurnal.ipynb'),
    Path(r'c:\Users\ARII\Downloads\4-4-irisan-ringkas-optimasi-2p2w-selesai.ipynb'),
    Path(r'c:\Users\ARII\Downloads\irisan\4-4-irisan-ringkas-optimasi-8p8w-selesai.ipynb')
]

for fpath in files:
    if not fpath.exists():
        continue
    
    with open(fpath, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    modified = False
    
    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] != 'code':
            continue
        src = ''.join(cell['source'])
        
        # Patch Cell 19: Add malloc_trim, measure YARN allocation time, and log to results.csv
        if 'SparkSession.builder' in src and 'active_executors' in src:
            # 1. Add malloc_trim at top of cell if not present
            if 'malloc_trim' not in src:
                cleanup_code = """import gc
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

"""
                src = cleanup_code + src
                modified = True
                print(f"[{fpath.name}] Added malloc_trim cleanup to cell {i}")
            
            # 2. Add timer for YARN allocation time
            if 'yarn_alloc_time_sec' not in src:
                src = src.replace('_deadline = time.time() + 120', '_t_alloc_start = time.time()\n_deadline = time.time() + 120')
                src = src.replace('print(f"Executor aktif: {active_executors} (target skenario: {NUM_WORKERS})")',
"""yarn_alloc_time_sec = time.time() - _t_alloc_start
print(f"Executor aktif: {active_executors} (target skenario: {NUM_WORKERS}) | Waktu Alokasi YARN: {yarn_alloc_time_sec:.2f} detik")

# Catat Waktu Alokasi Kontainer YARN ke results.csv (Sesuai Proposal Riset)
RESULTS_LOG_PATH = PROJECT_DIR / "results.csv"
if RESULTS_LOG_PATH.exists():
    with open(RESULTS_LOG_PATH, "a", newline="") as _f:
        csv.writer(_f).writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            SCENARIO_NAME, NUM_WORKERS, NUM_PARTITIONS,
            "yarn_container_allocation", f"{yarn_alloc_time_sec:.2f}",
            "", "", "", "", "", "", ""
        ])
    print(f"Log alokasi kontainer YARN ({yarn_alloc_time_sec:.2f}s) dicatat ke results.csv.")""")
                modified = True
                print(f"[{fpath.name}] Added YARN allocation logging to cell {i}")
            
            cell['source'] = [line + '\n' for line in src.splitlines()]
            if cell['source']:
                cell['source'][-1] = cell['source'][-1].rstrip('\n')
                
    if modified:
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
        print(f"Successfully saved {fpath.name}\n")
