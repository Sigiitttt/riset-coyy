from pathlib import Path

p = Path("scripts/build_sk4_unetmask.py")
s = p.read_text(encoding="utf-8")


def rep(old, new):
    global s
    assert s.count(old) == 1, old
    s = s.replace(old, new)


rep('IMG_SIZE = 224\nBATCH_SIZE = 64\n',
    'NUM_WORKERS = 2      # jumlah worker Spark (local[N])\nNUM_PARTITIONS = 2   # jumlah partisi data Spark\nIMG_SIZE = 224\nBATCH_SIZE = 64\n')

rep('    .master("local[*]") \\\\\n    .config("spark.driver.memory", "8g") \\\\',
    '    .master(f"local[{NUM_WORKERS}]") \\\\\n    .config("spark.default.parallelism", str(NUM_PARTITIONS)) \\\\\n    .config("spark.driver.memory", "8g") \\\\')
rep('print("Spark Session (local[*]) siap.")',
    'print(f"Spark Session siap: {NUM_WORKERS} worker, {NUM_PARTITIONS} partisi.")')

rep('\nspark.stop()\nimport gc\ngc.collect()\nprint("[INFO] Spark ditutup, RAM dibebaskan untuk TensorFlow.")\n', '\n')

old_start = s.index("def process_one(args):")
old_end = s.index("df_final[\"filepath\"] = [p for _, p in sorted(results)]")
new_block = '''def process_partition(rows):
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

print("\\\\n=== BEBAN KERJA PREPROCESSING SPARK ===")
for k, (n, t, _) in enumerate(parts):
    print(f"Partisi {k}: {n} citra, {t:.1f} detik")
print(f"Total waktu preprocessing: {elapsed_prep:.1f} detik")
results = [r for _, _, rows in parts for r in rows]

spark.stop()
import gc
gc.collect()
print("[INFO] Spark ditutup, RAM dibebaskan untuk TensorFlow.")

'''
s = s[:old_start] + new_block + s[old_end:]

rep('from tqdm import tqdm\nfrom concurrent.futures import ThreadPoolExecutor\n\n\ndef pad_and_resize',
    'import time\nfrom tqdm import tqdm\nfrom concurrent.futures import ThreadPoolExecutor\nfrom pyspark.sql import SparkSession\n\n\ndef pad_and_resize')

rep('def load_rgb(path):', 'workers = min(os.cpu_count() or 4, 16)\n\n\ndef load_rgb(path):')

p.write_text(s, encoding="utf-8")
print("patched")
