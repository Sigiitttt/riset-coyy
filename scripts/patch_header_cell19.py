import json
from pathlib import Path

files = [
    Path(r'kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk1-irisan-tipe1-ringkas-optimasi.ipynb'),
    Path(r'kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk2-biner-tipe1-ringkas-optimasi.ipynb'),
    Path(r'kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk1-irisan-tipe1-ringkas-prepjurnal.ipynb'),
    Path(r'kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk2-biner-tipe1-ringkas-prepjurnal.ipynb')
]

old_block = """RESULTS_LOG_PATH = PROJECT_DIR / "results.csv"
if RESULTS_LOG_PATH.exists():
    with open(RESULTS_LOG_PATH, "a", newline="") as _f:
        csv.writer(_f).writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            SCENARIO_NAME, NUM_WORKERS, NUM_PARTITIONS,
            "yarn_container_allocation", f"{yarn_alloc_time_sec:.2f}",
            "", "", "", "", "", "", ""
        ])
    print(f"Log alokasi kontainer YARN ({yarn_alloc_time_sec:.2f}s) dicatat ke results.csv.")"""

new_block = """RESULTS_LOG_PATH = PROJECT_DIR / "results.csv"
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
print(f"Log alokasi kontainer YARN ({yarn_alloc_time_sec:.2f}s) dicatat ke results.csv.")"""

for fpath in files:
    if not fpath.exists():
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            src = ''.join(cell['source'])
            if 'RESULTS_LOG_PATH = PROJECT_DIR / "results.csv"' in src and 'yarn_container_allocation' in src:
                src = src.replace(old_block, new_block)
                cell['source'] = [line + '\n' for line in src.split('\n')[:-1]] + ([src.split('\n')[-1]] if src.split('\n')[-1] else [])
    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print(f'Updated {fpath.name}')
    