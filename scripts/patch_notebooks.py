import json
from pathlib import Path

files = [
    Path(r'c:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\kode\4_Spark_on_Yarn\4.4-ringkas-optimasi\sk1-irisan-tipe1-ringkas-optimasi.ipynb'),
    Path(r'c:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\kode\4_Spark_on_Yarn\4.4-ringkas-optimasi\sk2-biner-tipe1-ringkas-optimasi.ipynb'),
    Path(r'c:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\kode\4_Spark_on_Yarn\4.6-ringkas-optimasi-prepjurnal\sk1-irisan-tipe1-ringkas-prepjurnal.ipynb'),
    Path(r'c:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\kode\4_Spark_on_Yarn\4.6-ringkas-optimasi-prepjurnal\sk2-biner-tipe1-ringkas-prepjurnal.ipynb'),
    Path(r'c:\Users\ARII\Downloads\4-4-irisan-ringkas-optimasi-2p2w-selesai.ipynb')
]

for fpath in files:
    if not fpath.exists():
        print(f"Skipping non-existent: {fpath}")
        continue
    
    with open(fpath, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    modified = False
    
    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] != 'code':
            continue
        
        src = ''.join(cell['source'])
        
        # 1. Update YARN_NM_VCORES
        if 'YARN_NM_VCORES = max(cpu_count, MAX_WORKERS_PLANNED)' in src:
            src = src.replace(
                'YARN_NM_VCORES = max(cpu_count, MAX_WORKERS_PLANNED)',
                'YARN_NM_VCORES = max(cpu_count, MAX_WORKERS_PLANNED) + 2'
            )
            cell['source'] = [line + '\n' for line in src.splitlines()]
            if cell['source'] and not cell['source'][-1].endswith('\n'):
                cell['source'][-1] += '\n'
            modified = True
            print(f"[{fpath.name}] Updated YARN_NM_VCORES in cell {i}")
            
        # 2. Remove SparkPi from cell 14
        if '!$SPARK_HOME/bin/spark-submit' in src and 'SparkPi' in src:
            lines = src.splitlines()
            new_lines = []
            skip = False
            for l in lines:
                if '!$SPARK_HOME/bin/spark-submit' in l:
                    skip = True
                if not skip:
                    new_lines.append(l)
                if skip and '10' in l and 'spark-examples' in l:
                    skip = False
            cell['source'] = [line + '\n' for line in new_lines]
            modified = True
            print(f"[{fpath.name}] Removed SparkPi from cell {i}")
            
        # 3. Update SparkSession.builder in cell 19
        if 'SparkSession.builder' in src and '.config("spark.executor.instances"' not in src:
            # Replace SparkSession.builder block
            target_old = """spark = (
    SparkSession.builder
    .appName(f"skincancer-preprocessing-{SCENARIO_NAME}")
    .getOrCreate()
)"""
            replacement_new = """# Hapus cache sesi lama agar konfigurasi worker baru terbaca
SparkSession._instantiatedSession = None
SparkSession._activeSession = None

# Set jumlah executor dan paralelisme secara eksplisit sesuai NUM_WORKERS
spark = (
    SparkSession.builder
    .appName(f"skincancer-preprocessing-{SCENARIO_NAME}")
    .config("spark.executor.instances", str(NUM_WORKERS))
    .config("spark.default.parallelism", str(NUM_WORKERS))
    .getOrCreate()
)"""
            if target_old in src:
                src = src.replace(target_old, replacement_new)
                cell['source'] = [line + '\n' for line in src.splitlines()]
                modified = True
                print(f"[{fpath.name}] Updated SparkSession.builder in cell {i}")
            else:
                # If slight whitespace difference
                import re
                pattern = r'spark\s*=\s*\(\s*SparkSession\.builder\s*\.appName\(f"skincancer-preprocessing-\{SCENARIO_NAME\}"\)\s*\.getOrCreate\(\)\s*\)'
                if re.search(pattern, src):
                    src = re.sub(pattern, replacement_new, src)
                    cell['source'] = [line + '\n' for line in src.splitlines()]
                    modified = True
                    print(f"[{fpath.name}] Updated SparkSession.builder via regex in cell {i}")
                else:
                    print(f"[{fpath.name}] Warning: SparkSession.builder pattern not matched in cell {i}")

    if modified:
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
        print(f"Successfully saved {fpath.name}\n")
    else:
        print(f"No changes made to {fpath.name}\n")
