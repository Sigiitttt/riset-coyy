import json
from pathlib import Path

# Load template from 00_baseline_convnext_tiny_ak84.ipynb
src_path = Path("kode/6_backbone_convnext/00_baseline_convnext_tiny_ak84.ipynb")
src = json.load(open(src_path, encoding="utf-8"))

# 1. Update Cell 0: Markdown Title & Description
cell_0_text = """# EXP 5-H: ConvNeXt-Tiny (PyTorch/timm) + Test-Time Augmentation (TTA 4-Arah)

Melanjutkan Baseline Juara **File 09 / 00 (Akurasi 83.87% | Macro-F1 0.7867 | AUC 93.60%)**.
Pada eksperimen ini, kita menguji hipotesis **Test-Time Augmentation (TTA 4-Arah)** pada inferensi:
- Citra lesi kulit dermatoskopi bersifat **invarian rotasi dan refleksi** (tidak memiliki orientasi vertikal/horizontal mutlak).
- TTA mengevaluasi 4 variasi geometris untuk setiap citra uji:
  1. $T_0(x) = x$ (Original)
  2. $T_1(x) = \\text{Horizontal Flip}(x)$
  3. $T_2(x) = \\text{Vertical Flip}(x)$
  4. $T_3(x) = \\text{Horizontal Flip}(\\text{Vertical Flip}(x))$
- Probabilitas akhir: $P_{\\text{TTA}}(x) = \\frac{1}{4} \\sum_{i=0}^3 P(T_i(x))$.

**Fitur & Kemudahan Eksekusi:**
- **Zero Re-training Mode (Default):** Jika checkpoint terbaik baseline (`best_melanoma_model_exp5c_convnext_tiny.pt`) sudah ada di Google Drive, evaluasi TTA dapat langsung dijalankan dalam **~1-2 menit** tanpa menghabiskan kuota GPU untuk pelatihan ulang 12 menit.
- **Tabel Komparasi Head-to-Head:** Menampilkan perbandingan metrik langsung: Single Pass (Baseline) vs TTA 4-Arah pada Test Set (2.343 citra) dan Validation Set (2.410 citra).
- **Confusion Matrix Komparatif:** Membandingkan matriks kebingungan sebelum vs sesudah TTA.
"""

src["cells"][0]["source"] = [l + "\n" for l in cell_0_text.strip().split("\n")]

# 2. Update Cell 9: Code Modeling & Training + TTA Prediction
cell_9_code = """# ==========================================
# EXP 5-H: CONVNEXT-TINY (timm) + TEST-TIME AUGMENTATION (TTA)
# ==========================================
import random
import time
import numpy as np
import torch
import torch.nn as nn
import timm
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms as T
from sklearn.metrics import f1_score, balanced_accuracy_score, roc_auc_score

CFG = dict(
    arch="convnext_tiny",
    img=224,
    bs=64,
    wd=1e-4,
    workers=4,
    seed=42,
    stage1_lr=3e-4,
    stage1_epochs=4,
    stage2_lr=2e-5,
    stage2_epochs=15,
    patience=4,
    train_from_scratch=False,  # Set False untuk evaluasi langsung checkpoint yang sudah ada di Drive
)

dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
AMP = dev.type == "cuda"


def seed_all(s):
    random.seed(s)
    np.random.seed(s)
    torch.manual_seed(s)
    torch.cuda.manual_seed_all(s)


seed_all(CFG["seed"])
print("Device:", dev, torch.cuda.get_device_name(0) if AMP else "", "| torch", torch.__version__, "| timm", timm.__version__)


class ColorTemp:
    \"\"\"Geser suhu warna: R dikali g, B dibagi g, g ~ U(1-s, 1+s).\"\"\"
    def __init__(self, s):
        self.s = s

    def __call__(self, im):
        g = random.uniform(1 - self.s, 1 + self.s)
        r, gg, b = im.split()
        return Image.merge("RGB", (r.point(lambda v: min(255, v * g)), gg, b.point(lambda v: min(255, v / g))))


class ArrayDS(Dataset):
    def __init__(self, X, y, tf):
        self.X, self.y, self.tf = X, y, tf

    def __len__(self):
        return len(self.y)

    def __getitem__(self, i):
        return self.tf(Image.fromarray(self.X[i])), int(self.y[i])


K = len(class_names)
model = timm.create_model(CFG["arch"], pretrained=True, num_classes=K).to(dev)
pc = model.pretrained_cfg
norm = T.Normalize(pc.get("mean", (0.485, 0.456, 0.406)), pc.get("std", (0.229, 0.224, 0.225)))

tf_train = T.Compose([
    T.RandomHorizontalFlip(), T.RandomVerticalFlip(), T.RandomRotation(20),
    T.ColorJitter(0.3, 0.3, 0.3, 0.03), ColorTemp(0.1), T.ToTensor(), norm,
])
tf_eval = T.Compose([T.ToTensor(), norm])

gen = torch.Generator().manual_seed(CFG["seed"])
mk = lambda X, y, tf, shuffle: DataLoader(
    ArrayDS(X, y, tf), CFG["bs"], shuffle=shuffle, drop_last=shuffle,
    num_workers=CFG["workers"], pin_memory=AMP, persistent_workers=True, generator=gen)
dl_train, dl_val, dl_test = mk(X_train, y_train, tf_train, True), mk(X_val, y_val, tf_eval, False), mk(X_test, y_test, tf_eval, False)

cnt = np.bincount(y_train, minlength=K)
class_w = torch.tensor(cnt.sum() / (K * cnt), dtype=torch.float32, device=dev)
print("Bobot kelas:", {c: round(float(w), 3) for c, w in zip(class_names, class_w.cpu())})
criterion = nn.CrossEntropyLoss(weight=class_w)


@torch.no_grad()
def predict(loader):
    \"\"\"Prediksi single-pass standar (tanpa TTA).\"\"\"
    model.eval()
    out = []
    for x, _ in loader:
        with torch.autocast(dev.type, enabled=AMP):
            out.append(model(x.to(dev, non_blocking=True)).float().softmax(1).cpu())
    return torch.cat(out).numpy()


@torch.no_grad()
def predict_tta(loader, num_tta=4):
    \"\"\"Prediksi Test-Time Augmentation (TTA).
    num_tta=1: Original
    num_tta=2: Original + Horizontal Flip
    num_tta=4: Original + H-Flip + V-Flip + HV-Flip
    \"\"\"
    model.eval()
    out = []
    for x, _ in loader:
        x = x.to(dev, non_blocking=True)
        batch_probs = []
        # 1. Original
        with torch.autocast(dev.type, enabled=AMP):
            batch_probs.append(model(x).float().softmax(1))
        # 2. Horizontal Flip
        if num_tta >= 2:
            with torch.autocast(dev.type, enabled=AMP):
                batch_probs.append(model(torch.flip(x, dims=[-1])).float().softmax(1))
        # 3. Vertical Flip & 4. HV-Flip
        if num_tta >= 4:
            with torch.autocast(dev.type, enabled=AMP):
                batch_probs.append(model(torch.flip(x, dims=[-2])).float().softmax(1))
                batch_probs.append(model(torch.flip(x, dims=[-2, -1])).float().softmax(1))
        # Rata-rata ensemble TTA
        avg_prob = torch.stack(batch_probs, dim=0).mean(dim=0).cpu()
        out.append(avg_prob)
    return torch.cat(out).numpy()


def freeze_backbone():
    for p in model.parameters():
        p.requires_grad = False
    for p in model.get_classifier().parameters():
        p.requires_grad = True


def unfreeze_all():
    for p in model.parameters():
        p.requires_grad = True


drive_dir = Path("/content/drive/MyDrive")
ckpt_dir = drive_dir if drive_dir.exists() else WORK_DIR
# Opsi checkpoint: Gunakan checkpoint baseline 83.87% jika ada
best_model_path = str(ckpt_dir / "best_melanoma_model_exp5c_convnext_tiny.pt")
exp5h_model_path = str(ckpt_dir / "best_melanoma_model_exp5h_convnext_tta.pt")
print("Target checkpoint:", best_model_path)

history = []
if CFG["train_from_scratch"] or not Path(best_model_path).exists():
    print("[INFO] Melakukan pelatihan dari awal (Train from Scratch)...")
    fe, fte = CFG["stage1_epochs"], CFG["stage2_epochs"]
    best, bad = -1.0, 0
    t_start = time.time()

    for ep in range(fe + fte):
        stage = 1 if ep < fe else 2
        if ep == 0:
            freeze_backbone()
            opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=CFG["stage1_lr"], weight_decay=CFG["wd"])
            sched = None
            scaler = torch.amp.GradScaler(dev.type, enabled=AMP)
            print(f"[INFO] Fase 1: head saja, {fe} epoch, LR {CFG['stage1_lr']}")
        elif ep == fe:
            unfreeze_all()
            opt = torch.optim.AdamW(model.parameters(), lr=CFG["stage2_lr"], weight_decay=CFG["wd"])
            sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=fte)
            scaler = torch.amp.GradScaler(dev.type, enabled=AMP)
            bad = 0
            print(f"[INFO] Fase 2: fine-tuning penuh, maks {fte} epoch, LR {CFG['stage2_lr']} + cosine")

        model.train() if stage == 2 else model.eval()
        t0, total_loss, n = time.time(), 0.0, 0
        for x, y in dl_train:
            x, y = x.to(dev, non_blocking=True), y.to(dev, non_blocking=True)
            opt.zero_grad(set_to_none=True)
            with torch.autocast(dev.type, enabled=AMP):
                loss = criterion(model(x), y)
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            total_loss += loss.item() * len(y)
            n += len(y)
        if sched:
            sched.step()

        P = predict(dl_val)
        pred = P.argmax(1)
        val_acc = float((pred == y_val).mean())
        val_f1 = f1_score(y_val, pred, average="macro")
        val_bal = balanced_accuracy_score(y_val, pred)
        val_auc = roc_auc_score(y_val, P, multi_class="ovr", average="macro")
        val_loss = float(-np.log(P[np.arange(len(y_val)), y_val] + 1e-12).mean())
        history.append(dict(epoch=ep + 1, stage=stage, train_loss=total_loss / n, val_loss=val_loss,
                            val_acc=val_acc, val_macro_f1=val_f1, val_bal_acc=val_bal, val_auc=val_auc))
        print(f"ep {ep + 1:02d} [fase {stage}] | train loss {total_loss / n:.4f} | val loss {val_loss:.4f} "
              f"acc {val_acc:.4f} AUC {val_auc:.4f} macroF1 {val_f1:.4f} balAcc {val_bal:.4f} | {time.time() - t0:.0f}s")

        if val_f1 > best:
            best, bad = val_f1, 0
            torch.save(model.state_dict(), exp5h_model_path)
            best_model_path = exp5h_model_path
        elif stage == 2:
            bad += 1
            if bad >= CFG["patience"]:
                print("[INFO] Early stopping")
                break

    waktu_total = (time.time() - t_start) / 60
    print(f"\\n[HASIL] Total Waktu Pelatihan: {waktu_total:.2f} menit | Val Macro-F1 terbaik: {best:.4f}")
else:
    print(f"[INFO] Checkpoint ditemukan di {best_model_path}. Melompat ke evaluasi inferensi langsung (Zero Re-training).")
"""

src["cells"][9]["source"] = [l + "\n" for l in cell_9_code.strip().split("\n")]

# 3. Update Cell 11: Code Evaluasi Head-to-Head (Single-Pass vs TTA)
cell_11_code = """# ==========================================
# EVALUASI KOMPARATIF: SINGLE-PASS VS TTA 4-ARAH (VAL & BLIND TEST)
# ==========================================
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

if history:
    hist = pd.DataFrame(history)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    hist.plot(x="epoch", y=["train_loss", "val_loss"], ax=axes[0], title="Loss")
    hist.plot(x="epoch", y=["val_acc", "val_macro_f1", "val_auc"], ax=axes[1], title="Metrik Validasi")
    for ax in axes:
        ax.axvline(CFG["stage1_epochs"] + 0.5, ls="--", c="red")
    plt.tight_layout()
    plt.show()

# Muat checkpoint model terbaik
model.load_state_dict(torch.load(best_model_path, map_location=dev))
print(f"[INFO] Model terbaik berhasil dimuat dari: {best_model_path}")

print("\\n" + "=" * 60)
print("[1/2] MENJALANKAN INFERENSI SINGLE-PASS (BASELINE)...")
P_val_orig = predict(dl_val)
P_test_orig = predict(dl_test)
pred_val_orig = P_val_orig.argmax(1)
pred_test_orig = P_test_orig.argmax(1)

print("[2/2] MENJALANKAN INFERENSI TEST-TIME AUGMENTATION (TTA 4-ARAH)...")
P_val_tta = predict_tta(dl_val, num_tta=4)
P_test_tta = predict_tta(dl_test, num_tta=4)
pred_val_tta = P_val_tta.argmax(1)
pred_test_tta = P_test_tta.argmax(1)
print("=" * 60)

# Laporan Klasifikasi
print("\\n=== CLASSIFICATION REPORT: TEST SET (SINGLE-PASS BASELINE) ===")
print(classification_report(y_test, pred_test_orig, target_names=class_names))

print("\\n=== CLASSIFICATION REPORT: TEST SET (TTA 4-ARAH) ===")
print(classification_report(y_test, pred_test_tta, target_names=class_names))

# Ringkasan Ekstraksi Metrik
rep_orig = classification_report(y_test, pred_test_orig, target_names=class_names, output_dict=True)
rep_tta = classification_report(y_test, pred_test_tta, target_names=class_names, output_dict=True)

auc_orig = roc_auc_score(y_test, P_test_orig, multi_class="ovr", average="macro")
auc_tta = roc_auc_score(y_test, P_test_tta, multi_class="ovr", average="macro")

acc_orig, acc_tta = rep_orig["accuracy"] * 100, rep_tta["accuracy"] * 100
f1_orig, f1_tta = rep_orig["macro avg"]["f1-score"], rep_tta["macro avg"]["f1-score"]
mel_r_orig, mel_r_tta = rep_orig["melanoma"]["recall"] * 100, rep_tta["melanoma"]["recall"] * 100
sk_r_orig, sk_r_tta = rep_orig["seborrheic_keratosis"]["recall"] * 100, rep_tta["seborrheic_keratosis"]["recall"] * 100
nv_p_orig, nv_p_tta = rep_orig["nevus"]["precision"] * 100, rep_tta["nevus"]["precision"] * 100

score_orig = (rep_orig["accuracy"] + f1_orig + rep_orig["melanoma"]["recall"] + rep_orig["seborrheic_keratosis"]["recall"]) / 4.0
score_tta = (rep_tta["accuracy"] + f1_tta + rep_tta["melanoma"]["recall"] + rep_tta["seborrheic_keratosis"]["recall"]) / 4.0

# Tabel Ringkasan Komparasi
df_comp = pd.DataFrame({
    "Metrik Pengujian": [
        "Akurasi Test Set (%)",
        "Macro F1-Score",
        "ROC-AUC (One-vs-Rest)",
        "Melanoma Recall (%)",
        "SK Recall (%)",
        "Nevus Precision (%)",
        "Skor Seleksi Internal",
    ],
    "Single-Pass (Baseline)": [
        f"{acc_orig:.2f}%",
        f"{f1_orig:.4f}",
        f"{auc_orig:.4f}",
        f"{mel_r_orig:.2f}%",
        f"{sk_r_orig:.2f}%",
        f"{nv_p_orig:.2f}%",
        f"{score_orig:.4f}",
    ],
    "TTA 4-Arah (Ensemble)": [
        f"{acc_tta:.2f}%",
        f"{f1_tta:.4f}",
        f"{auc_tta:.4f}",
        f"{mel_r_tta:.2f}%",
        f"{sk_r_tta:.2f}%",
        f"{nv_p_tta:.2f}%",
        f"{score_tta:.4f}",
    ],
    "Delta / Perubahan": [
        f"{acc_tta - acc_orig:+.2f}%",
        f"{f1_tta - f1_orig:+.4f}",
        f"{auc_tta - auc_orig:+.4f}",
        f"{mel_r_tta - mel_r_orig:+.2f}%",
        f"{sk_r_tta - sk_r_orig:+.2f}%",
        f"{nv_p_tta - nv_p_orig:+.2f}%",
        f"{score_tta - score_orig:+.4f}",
    ]
})

print("\\n" + "=" * 55)
print("=== TABEL KOMPARASI HEAD-TO-HEAD: BASELINE VS TTA ===")
print("=" * 55)
print(df_comp.to_string(index=False))
print("=" * 55)

# Visualisasi Confusion Matrix Komparatif
fig, axes = plt.subplots(1, 2, figsize=(15, 6))
cm_orig = confusion_matrix(y_test, pred_test_orig)
cm_tta = confusion_matrix(y_test, pred_test_tta)

sns.heatmap(cm_orig, annot=True, fmt="d", cmap="Blues",
            xticklabels=class_names, yticklabels=class_names, annot_kws={"size": 12}, ax=axes[0])
axes[0].set_title(f"Baseline Single-Pass (Acc: {acc_orig:.2f}%)", fontsize=13)
axes[0].set_ylabel("Label Aktual")
axes[0].set_xlabel("Label Prediksi")

sns.heatmap(cm_tta, annot=True, fmt="d", cmap="Greens",
            xticklabels=class_names, yticklabels=class_names, annot_kws={"size": 12}, ax=axes[1])
axes[1].set_title(f"TTA 4-Arah Ensemble (Acc: {acc_tta:.2f}%)", fontsize=13)
axes[1].set_ylabel("Label Aktual")
axes[1].set_xlabel("Label Prediksi")

plt.tight_layout()
plt.show()

# Evaluasi Per Sumber Data
print("\\n=== PERFORMA TEST PER SUMBER DATA (TTA 4-ARAH) ===")
for src_name in test_df["source"].unique():
    mask = (test_df["source"] == src_name).to_numpy()
    yt_sub, yp_sub = y_test[mask], pred_test_tta[mask]
    n_sub = len(yt_sub)
    acc_sub = float((yt_sub == yp_sub).mean())
    f1_sub = f1_score(yt_sub, yp_sub, average="macro", zero_division=0)
    mel_mask = yt_sub == class_to_id["melanoma"]
    mel_rec = float((yp_sub[mel_mask] == class_to_id["melanoma"]).mean()) if mel_mask.sum() > 0 else 0.0
    print(f"{src_name:<10} n={n_sub:<4} acc={acc_sub:.4f} macroF1={f1_sub:.4f} melRecall={mel_rec:.4f} (n_mel={mel_mask.sum()})")
"""

src["cells"][11]["source"] = [l + "\n" for l in cell_11_code.strip().split("\n")]

# Clean all execution count and outputs
for cell in src["cells"]:
    if cell["cell_type"] == "code":
        cell["execution_count"] = None
        cell["outputs"] = []

# Write to target notebook
out_path = Path("kode/6_backbone_convnext/05_exp5h_convnext_tta.ipynb")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(src, f, indent=2, ensure_ascii=False)

print(f"Successfully created: {out_path} (cells: {len(src['cells'])})")
