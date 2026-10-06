import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

# Path file log resmi
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

# Filter stage dan ambil eksekusi terbaru per skenario
df_prep = df[df["stage"] == "preprocessing"].drop_duplicates(subset=["scenario"], keep="last").copy()
df_train = df[df["stage"] == "training_centralized_gpu"].drop_duplicates(subset=["scenario"], keep="last").copy()

# Setup Grid 5 Panel: Baris 1 (3 grafik resource) & Baris 2 (2 grafik evaluasi)
fig = plt.figure(figsize=(18, 10))
gs = fig.add_gridspec(2, 6, hspace=0.35, wspace=0.6)
fig.suptitle(
    "Komparasi Kinerja Matriks PySpark on YARN: Durasi, Resource (CPU & RAM), dan Evaluasi Model (Akurasi & AUC)",
    fontsize=14,
    fontweight="bold",
    y=0.98,
)

# Palet warna profesional untuk skenario
palette = ["#2b5c8f", "#3b8b88", "#d95f02", "#7570b3"]
scenarios = df_prep["scenario"].tolist()
colors = [palette[i % len(palette)] for i in range(len(scenarios))]

# -------------------------------------------------------------
# Panel 1: Durasi Prapemrosesan Spark (Detik)
# -------------------------------------------------------------
ax1 = fig.add_subplot(gs[0, 0:2])
bars1 = ax1.bar(scenarios, df_prep["elapsed_sec"], color=colors, edgecolor="black", width=0.45)
ax1.set_title("1. Durasi Prapemrosesan Spark\n(Detik, Lebih Rendah = Cepat)", fontsize=11, fontweight="semibold")
ax1.set_ylabel("Waktu (detik)")
ax1.set_ylim(0, max(df_prep["elapsed_sec"].max() * 1.22, 10))
ax1.grid(axis="y", linestyle="--", alpha=0.5)
for bar in bars1:
    h = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width() / 2.0, h + 1.5, f"{h:.1f}s", ha="center", va="bottom", fontweight="bold", fontsize=10)

# -------------------------------------------------------------
# Panel 2: Rata-Rata Beban CPU Cluster (%)
# -------------------------------------------------------------
ax2 = fig.add_subplot(gs[0, 2:4])
bars2 = ax2.bar(scenarios, df_prep["avg_cpu_percent"], color=colors, edgecolor="black", width=0.45)
ax2.set_title("2. Rata-Rata Beban CPU Cluster (%)\n(Persentase Utilisasi Core)", fontsize=11, fontweight="semibold")
ax2.set_ylabel("CPU Usage (%)")
ax2.set_ylim(0, max(df_prep["avg_cpu_percent"].fillna(0).max() * 1.22, 110))
ax2.axhline(100, color="red", linestyle=":", alpha=0.7, label="Kapasitas Maksimal (100%)")
ax2.legend(loc="upper left", fontsize=8)
ax2.grid(axis="y", linestyle="--", alpha=0.5)
for bar in bars2:
    h = bar.get_height()
    txt = f"{h:.1f}%" if not np.isnan(h) else "N/A"
    ax2.text(bar.get_x() + bar.get_width() / 2.0, (h if not np.isnan(h) else 0) + 1.5, txt, ha="center", va="bottom", fontweight="bold", fontsize=10)

# -------------------------------------------------------------
# Panel 3: Rata-Rata Konsumsi RAM Cluster (MB & GB)
# -------------------------------------------------------------
ax3 = fig.add_subplot(gs[0, 4:6])
bars3 = ax3.bar(scenarios, df_prep["avg_mem_mb"], color=colors, edgecolor="black", width=0.45)
ax3.set_title("3. Rata-Rata Konsumsi RAM Cluster\n(Megabytes & Gigabytes)", fontsize=11, fontweight="semibold")
ax3.set_ylabel("RAM (MB)")
ax3.set_ylim(0, max(df_prep["avg_mem_mb"].fillna(0).max() * 1.25, 1000))
ax3.grid(axis="y", linestyle="--", alpha=0.5)
for bar in bars3:
    h = bar.get_height()
    gb = h / 1024.0 if not np.isnan(h) else 0
    txt = f"{h:,.0f} MB\n({gb:.1f} GB)" if not np.isnan(h) else "N/A"
    ax3.text(bar.get_x() + bar.get_width() / 2.0, (h if not np.isnan(h) else 0) + 200, txt, ha="center", va="bottom", fontweight="bold", fontsize=9)

# -------------------------------------------------------------
# Panel 4: Evaluasi Kualitas Model (Akurasi & Macro F1 %)
# -------------------------------------------------------------
ax4 = fig.add_subplot(gs[1, 0:3])
train_scenarios = df_train["scenario"].tolist()
x = np.arange(len(train_scenarios))
w = 0.35

b_acc = ax4.bar(x - w / 2, df_train["accuracy"] * 100, width=w, label="Test Accuracy (%)", color="#1f77b4", edgecolor="black")
b_f1 = ax4.bar(x + w / 2, df_train["f1_score"] * 100, width=w, label="Macro F1 (%)", color="#2ca02c", edgecolor="black")
ax4.set_xticks(x)
ax4.set_xticklabels(train_scenarios)
ax4.set_title("4. Evaluasi Kualitas Model Deep Learning ResNet-50\n(Test Accuracy vs Macro F1)", fontsize=11, fontweight="semibold")
ax4.set_ylabel("Persentase (%)")
ax4.set_ylim(0, 105)
ax4.legend(loc="lower right")
ax4.grid(axis="y", linestyle="--", alpha=0.5)
for bar in b_acc:
    h = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width() / 2.0, h + 1.2, f"{h:.1f}%", ha="center", va="bottom", fontsize=9, fontweight="semibold")
for bar in b_f1:
    h = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width() / 2.0, h + 1.2, f"{h:.1f}%", ha="center", va="bottom", fontsize=9, fontweight="semibold")

# -------------------------------------------------------------
# Panel 5: Skor Kemampuan Diskriminasi (ROC-AUC One-vs-Rest %)
# -------------------------------------------------------------
ax5 = fig.add_subplot(gs[1, 3:6])
bars5 = ax5.bar(train_scenarios, df_train["roc_auc"] * 100, color="#d95f02", edgecolor="black", width=0.40)
ax5.set_title("5. Kemampuan Diskriminasi Klinis\n(Skor ROC-AUC One-vs-Rest %)", fontsize=11, fontweight="semibold")
ax5.set_ylabel("ROC-AUC (%)")
ax5.set_ylim(0, 105)
ax5.grid(axis="y", linestyle="--", alpha=0.5)
for bar in bars5:
    h = bar.get_height()
    ax5.text(bar.get_x() + bar.get_width() / 2.0, h + 1.2, f"{h:.2f}%", ha="center", va="bottom", fontweight="bold", fontsize=10)

plt.tight_layout()
output_chart = PROJECT_DIR / "grafik_komparasi_5metrik_excel.png"
plt.savefig(output_chart, dpi=300, bbox_inches="tight")
print(f"Grafik 5 panel berhasil disimpan di: {output_chart}")
