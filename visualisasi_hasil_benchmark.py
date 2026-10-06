import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Path file CSV lokal & direktori output grafik
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "results.csv"
OUTPUT_IMG = BASE_DIR / "grafik_komparasi_4skenario_yarn.png"

# 1. Baca data dari CSV
df = pd.read_csv(CSV_PATH)

# Konversi tipe data numerik
numeric_cols = ["elapsed_sec", "avg_cpu_percent", "avg_mem_mb", "accuracy", "f1_score", "loss", "roc_auc"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Hapus duplikasi jika ada (ambil kemunculan pertama) & urutkan skenario secara baku
df = df.drop_duplicates(subset=["scenario", "stage"], keep="first")
scenario_order = ["irisan_2W2P", "irisan_2W8P", "irisan_8W2P", "irisan_8W8P"]
df["order"] = df["scenario"].map({name: idx for idx, name in enumerate(scenario_order)})
df = df.sort_values("order").drop(columns=["order"])

# Filter stage
df_prep = df[df["stage"] == "preprocessing"].copy()
df_prep["throughput"] = df_prep["image_count"] / df_prep["elapsed_sec"]
df_train = df[df["stage"] == "training_centralized_gpu"].copy()

scenarios = df_prep["scenario"].tolist()
palette = ["#2b5c8f", "#3b8b88", "#d95f02", "#7570b3"]

# 2. Setup Figure Grid 2 x 2
fig, axes = plt.subplots(2, 2, figsize=(16, 11))
fig.suptitle(
    "Analisis Komprehensif Skenario Big Data PySpark on YARN (2W2P, 2W8P, 8W2P, 8W8P)",
    fontsize=15,
    fontweight="bold",
    y=0.99
)

# -------------------------------------------------------------
# Panel (0, 0): Durasi Prapemrosesan (Detik)
# -------------------------------------------------------------
bars1 = axes[0, 0].bar(
    scenarios,
    df_prep["elapsed_sec"],
    color=palette[:len(scenarios)],
    edgecolor="black",
    width=0.45
)
axes[0, 0].set_title(
    "1. Durasi Prapemrosesan Spark (Detik)\n(Lebih Rendah = Lebih Cepat)",
    fontsize=11,
    fontweight="semibold"
)
axes[0, 0].set_ylabel("Waktu (detik)")
axes[0, 0].set_ylim(0, max(df_prep["elapsed_sec"]) * 1.18)
axes[0, 0].grid(axis="y", linestyle="--", alpha=0.5)
for bar in bars1:
    h = bar.get_height()
    axes[0, 0].text(
        bar.get_x() + bar.get_width() / 2.0,
        h + 1.5,
        f"{h:.1f}s",
        ha="center",
        va="bottom",
        fontweight="bold"
    )

# -------------------------------------------------------------
# Panel (0, 1): Rata-rata Utilisasi CPU Sistem (%)
# -------------------------------------------------------------
bars2 = axes[0, 1].bar(
    scenarios,
    df_prep["avg_cpu_percent"],
    color=palette[:len(scenarios)],
    edgecolor="black",
    width=0.45
)
axes[0, 1].set_title(
    "2. Rata-rata Beban CPU Selama Prapemrosesan (%)\n(Tinggi = Utilisasi Paralel Optimal)",
    fontsize=11,
    fontweight="semibold"
)
axes[0, 1].set_ylabel("CPU Usage (%)")
axes[0, 1].set_ylim(0, 110)
axes[0, 1].axhline(100, color="red", linestyle=":", alpha=0.7, label="Kapasitas Maksimal (100%)")
axes[0, 1].legend(loc="upper left")
axes[0, 1].grid(axis="y", linestyle="--", alpha=0.5)
for bar in bars2:
    h = bar.get_height()
    axes[0, 1].text(
        bar.get_x() + bar.get_width() / 2.0,
        h + 2.0,
        f"{h:.1f}%",
        ha="center",
        va="bottom",
        fontweight="bold"
    )

# -------------------------------------------------------------
# Panel (1, 0): Rata-rata Konsumsi RAM Sistem (MB & GB)
# -------------------------------------------------------------
bars3 = axes[1, 0].bar(
    scenarios,
    df_prep["avg_mem_mb"],
    color=palette[:len(scenarios)],
    edgecolor="black",
    width=0.45
)
axes[1, 0].set_title(
    "3. Rata-rata Footprint RAM Sistem (MB)\n(Menunjukkan Akumulasi Memori per Run)",
    fontsize=11,
    fontweight="semibold"
)
axes[1, 0].set_ylabel("RAM (Megabytes)")
axes[1, 0].set_ylim(0, max(df_prep["avg_mem_mb"]) * 1.18)
axes[1, 0].grid(axis="y", linestyle="--", alpha=0.5)
for bar in bars3:
    h = bar.get_height()
    gb = h / 1024.0
    axes[1, 0].text(
        bar.get_x() + bar.get_width() / 2.0,
        h + 400,
        f"{h:.0f} MB\n({gb:.1f} GB)",
        ha="center",
        va="bottom",
        fontweight="bold",
        fontsize=9
    )

# -------------------------------------------------------------
# Panel (1, 1): Kualitas Model Test Set (Accuracy vs F1-score %)
# -------------------------------------------------------------
train_scenarios = df_train["scenario"].tolist()
x = np.arange(len(train_scenarios))
w = 0.35

b_acc = axes[1, 1].bar(
    x - w / 2,
    df_train["accuracy"] * 100,
    width=w,
    label="Test Accuracy (%)",
    color="#1f77b4",
    edgecolor="black"
)
b_f1 = axes[1, 1].bar(
    x + w / 2,
    df_train["f1_score"] * 100,
    width=w,
    label="Macro F1 (%)",
    color="#2ca02c",
    edgecolor="black"
)

axes[1, 1].set_xticks(x)
axes[1, 1].set_xticklabels(train_scenarios)
axes[1, 1].set_title(
    "4. Kualitas Model Deep Learning ResNet-50\n(Test Accuracy vs Macro F1)",
    fontsize=11,
    fontweight="semibold"
)
axes[1, 1].set_ylabel("Persentase (%)")
axes[1, 1].set_ylim(0, 100)
axes[1, 1].legend(loc="lower right")
axes[1, 1].grid(axis="y", linestyle="--", alpha=0.5)

for bar in b_acc:
    h = bar.get_height()
    axes[1, 1].text(
        bar.get_x() + bar.get_width() / 2.0,
        h + 1.2,
        f"{h:.1f}%",
        ha="center",
        va="bottom",
        fontsize=9,
        fontweight="semibold"
    )
for bar in b_f1:
    h = bar.get_height()
    axes[1, 1].text(
        bar.get_x() + bar.get_width() / 2.0,
        h + 1.2,
        f"{h:.1f}%",
        ha="center",
        va="bottom",
        fontsize=9,
        fontweight="semibold"
    )

plt.tight_layout()
plt.savefig(OUTPUT_IMG, dpi=300, bbox_inches="tight")
print(f"Sukses! Gambar grafik tersimpan di: {OUTPUT_IMG}")
