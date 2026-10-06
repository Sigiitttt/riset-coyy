import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(".")
RESULTS_LOG_PATH = PROJECT_DIR / "results.csv"

# 1. Baca data dari file log resmi
df = pd.read_csv(RESULTS_LOG_PATH)

# Konversi kolom numerik
numeric_cols = [
    "elapsed_sec",
    "image_count",
    "avg_cpu_percent",
    "avg_mem_mb",
    "accuracy",
    "f1_score",
    "loss",
    "roc_auc",
]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Filter stage dan ambil data unik per skenario
df_prep = df[df["stage"] == "preprocessing"].drop_duplicates(subset=["scenario"], keep="last").copy()
df_prep["throughput"] = df_prep["image_count"] / df_prep["elapsed_sec"]
df_train = df[df["stage"] == "training_centralized_gpu"].drop_duplicates(subset=["scenario"], keep="last").copy()
df_alloc = df[df["stage"] == "yarn_container_allocation"].drop_duplicates(subset=["scenario"], keep="last").copy()

# Setup Figure Grafik Batang (6 Panel: 2 Baris x 3 Kolom)
fig, axes = plt.subplots(2, 3, figsize=(20, 11))
fig.suptitle(
    "Komparasi Kinerja Lengkap PySpark on YARN: Waktu, Resource (CPU & RAM), dan Kualitas Model",
    fontsize=15,
    fontweight="bold",
    y=0.98,
)

# Palet warna profesional untuk skenario
palette = ["#2b5c8f", "#3b8b88", "#d95f02", "#7570b3"]
scenarios = df_prep["scenario"].tolist()
colors = [palette[i % len(palette)] for i in range(len(scenarios))]

# -------------------------------------------------------------
# Panel 1: Durasi Prapemrosesan Spark
# -------------------------------------------------------------
bars1 = axes[0, 0].bar(scenarios, df_prep["elapsed_sec"], color=colors, edgecolor="black", width=0.45)
axes[0, 0].set_title("1. Durasi Prapemrosesan Spark\n(Detik, Lebih Rendah = Cepat)", fontsize=11, fontweight="semibold")
axes[0, 0].set_ylabel("Detik")
axes[0, 0].set_ylim(0, max(df_prep["elapsed_sec"].max() * 1.25, 10))
axes[0, 0].grid(axis="y", linestyle="--", alpha=0.5)
for bar in bars1:
    h = bar.get_height()
    axes[0, 0].text(bar.get_x() + bar.get_width() / 2.0, h + 1.5, f"{h:.1f}s", ha="center", va="bottom", fontweight="bold", fontsize=10)

# -------------------------------------------------------------
# Panel 2: Rata-Rata Utilisasi CPU Worker (%)
# -------------------------------------------------------------
bars2 = axes[0, 1].bar(scenarios, df_prep["avg_cpu_percent"], color=colors, edgecolor="black", width=0.45)
axes[0, 1].set_title("2. Rata-Rata Utilisasi CPU Cluster\n(Persentase CPU %, Beban Worker)", fontsize=11, fontweight="semibold")
axes[0, 1].set_ylabel("CPU (%)")
axes[0, 1].set_ylim(0, max(df_prep["avg_cpu_percent"].fillna(0).max() * 1.25, 100))
axes[0, 1].grid(axis="y", linestyle="--", alpha=0.5)
for bar in bars2:
    h = bar.get_height()
    txt = f"{h:.1f}%" if not np.isnan(h) else "N/A"
    axes[0, 1].text(bar.get_x() + bar.get_width() / 2.0, (h if not np.isnan(h) else 0) + 1.5, txt, ha="center", va="bottom", fontweight="bold", fontsize=10)

# -------------------------------------------------------------
# Panel 3: Rata-Rata Konsumsi RAM Cluster (MB)
# -------------------------------------------------------------
bars3 = axes[0, 2].bar(scenarios, df_prep["avg_mem_mb"], color=colors, edgecolor="black", width=0.45)
axes[0, 2].set_title("3. Rata-Rata Konsumsi RAM Cluster\n(Megabytes, Footprint Shard Partisi)", fontsize=11, fontweight="semibold")
axes[0, 2].set_ylabel("RAM (MB)")
axes[0, 2].set_ylim(0, max(df_prep["avg_mem_mb"].fillna(0).max() * 1.22, 1000))
axes[0, 2].grid(axis="y", linestyle="--", alpha=0.5)
for bar in bars3:
    h = bar.get_height()
    txt = f"{h:,.0f} MB" if not np.isnan(h) else "N/A"
    axes[0, 2].text(bar.get_x() + bar.get_width() / 2.0, (h if not np.isnan(h) else 0) + 100, txt, ha="center", va="bottom", fontweight="bold", fontsize=9)

# -------------------------------------------------------------
# Panel 4: Throughput Komputasi Citra
# -------------------------------------------------------------
bars4 = axes[1, 0].bar(scenarios, df_prep["throughput"], color=colors, edgecolor="black", width=0.45)
axes[1, 0].set_title("4. Throughput Komputasi Citra\n(Citra/Detik, Lebih Tinggi = Efisien)", fontsize=11, fontweight="semibold")
axes[1, 0].set_ylabel("Citra / Detik")
axes[1, 0].set_ylim(0, max(df_prep["throughput"].max() * 1.25, 50))
axes[1, 0].grid(axis="y", linestyle="--", alpha=0.5)
for bar in bars4:
    h = bar.get_height()
    axes[1, 0].text(bar.get_x() + bar.get_width() / 2.0, h + 3.0, f"{h:.1f}", ha="center", va="bottom", fontweight="bold", fontsize=10)

# -------------------------------------------------------------
# Panel 5: Akurasi & Macro F1-Score Uji (Kualitas Model)
# -------------------------------------------------------------
train_scenarios = df_train["scenario"].tolist()
x = np.arange(len(train_scenarios))
w = 0.35

b_acc = axes[1, 1].bar(x - w / 2, df_train["accuracy"] * 100, width=w, label="Test Accuracy (%)", color="#1f77b4", edgecolor="black")
b_f1 = axes[1, 1].bar(x + w / 2, df_train["f1_score"] * 100, width=w, label="Macro F1 (%)", color="#2ca02c", edgecolor="black")
axes[1, 1].set_xticks(x)
axes[1, 1].set_xticklabels(train_scenarios)
axes[1, 1].set_title("5. Evaluasi Kualitas Model CNN ResNet-50\n(Test Accuracy vs Macro F1)", fontsize=11, fontweight="semibold")
axes[1, 1].set_ylabel("Persentase (%)")
axes[1, 1].set_ylim(0, 100)
axes[1, 1].legend(loc="lower right")
axes[1, 1].grid(axis="y", linestyle="--", alpha=0.5)

for bar in b_acc:
    h = bar.get_height()
    axes[1, 1].text(bar.get_x() + bar.get_width() / 2.0, h + 1.2, f"{h:.1f}%", ha="center", va="bottom", fontsize=9, fontweight="semibold")
for bar in b_f1:
    h = bar.get_height()
    axes[1, 1].text(bar.get_x() + bar.get_width() / 2.0, h + 1.2, f"{h:.1f}%", ha="center", va="bottom", fontsize=9, fontweight="semibold")

# -------------------------------------------------------------
# Panel 6: ROC-AUC Skor (OVR)
# -------------------------------------------------------------
bars6 = axes[1, 2].bar(train_scenarios, df_train["roc_auc"] * 100, color="#d95f02", edgecolor="black", width=0.45)
axes[1, 2].set_title("6. Skor Kemampuan Diskriminasi\n(ROC-AUC One-vs-Rest %)", fontsize=11, fontweight="semibold")
axes[1, 2].set_ylabel("ROC-AUC (%)")
axes[1, 2].set_ylim(0, 105)
axes[1, 2].grid(axis="y", linestyle="--", alpha=0.5)
for bar in bars6:
    h = bar.get_height()
    axes[1, 2].text(bar.get_x() + bar.get_width() / 2.0, h + 1.2, f"{h:.2f}%", ha="center", va="bottom", fontweight="bold", fontsize=10)

plt.tight_layout()
output_chart = PROJECT_DIR / "grafik_komparasi_lengkap_resource.png"
plt.savefig(output_chart, dpi=300, bbox_inches="tight")
print(f"Chart saved to {output_chart}")
