import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

# Mock data based on user results.csv
data = """timestamp,scenario,num_workers,num_partitions,stage,elapsed_sec,image_count,avg_cpu_percent,avg_mem_mb,accuracy,f1_score,loss,roc_auc
2026-09-27 01:01:09,irisan_2W2P,2,2,yarn_container_allocation,0.01,,,,,,,,
2026-09-27 01:02:51,irisan_2W2P,2,2,preprocessing,92.45,22051.0,64.94,6564.39,,,,
2026-09-27 01:16:08,irisan_2W2P,2,2,training_centralized_gpu,616.51,17656.0,,,0.7463,0.6864,1.4835,0.8977
2026-09-27 01:27:40,irisan_2W8P,2,8,yarn_container_allocation,0.01,,,,,,,,
2026-09-27 01:30:00,irisan_2W8P,2,8,preprocessing,99.22,22051.0,61.93,11869.73,,,,
2026-09-27 01:42:16,irisan_2W8P,2,8,training_centralized_gpu,619.84,17656.0,,,0.7363,0.6634,1.5352,0.8903
"""

import io
df = pd.read_csv(io.StringIO(data))

numeric_cols = [
    "elapsed_sec", "image_count", "avg_cpu_percent", "avg_mem_mb",
    "accuracy", "f1_score", "loss", "roc_auc",
]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df_prep = df[df["stage"] == "preprocessing"].drop_duplicates(subset=["scenario"], keep="last").copy()
df_prep["throughput"] = df_prep["image_count"] / df_prep["elapsed_sec"]
df_train = df[df["stage"] == "training_centralized_gpu"].drop_duplicates(subset=["scenario"], keep="last").copy()
df_alloc = df[df["stage"] == "yarn_container_allocation"].drop_duplicates(subset=["scenario"], keep="last").copy()

print("Preprocessing scenarios:", df_prep["scenario"].tolist())
print("CPU:", df_prep["avg_cpu_percent"].tolist())
print("RAM:", df_prep["avg_mem_mb"].tolist())
