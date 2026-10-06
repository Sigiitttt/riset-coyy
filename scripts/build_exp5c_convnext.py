import json
from pathlib import Path

BASE = Path("kode/5_segmentasi_unet")
src = json.load(open(BASE / "sk3_bigdat_ham2019_unetmask_ak85_v2_exp2.ipynb", encoding="utf-8"))
cells_src = ["".join(c["source"]) for c in src["cells"]]


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip("\n").splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": text.strip("\n").splitlines(keepends=True)}


# --- sel data: ambil dari exp2, buang bagian Spark ---
lines = cells_src[5].split("\n")
cut = next(i for i, l in enumerate(lines) if l.startswith("# 4. Verifikasi dan Pelacakan"))
drop = ("from pyspark", "spark.sparkContext")
data_cell = "\n".join(l for l in lines[:cut] if not l.startswith(drop))

# --- sel preprocessing: ambil dari exp2, ubah ke 224 ---
prep_cell = (cells_src[8]
             .replace("TARGET_SIZE = 256", "TARGET_SIZE = 224")
             .replace("processed_images_roi_256", "processed_images_roi_224")
             .replace("(256x256)", "(224x224)")
             .replace("PAD & RESIZE 224", "PAD & RESIZE 224"))

setup_cell = '''
import os
os.system("pip install -q kagglehub timm")
'''

cache_cell = '''
# ==========================================
# CACHE CITRA ROI KE ARRAY uint8 (SEKALI BACA)
# ==========================================
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor

class_names = sorted(df_final["label"].unique())
class_to_id = {c: i for i, c in enumerate(class_names)}
print("Kelas:", class_to_id)

def load_rgb(path):
    img = cv2.imread(path)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def build_split(split):
    part = df_final[df_final["split"] == split].reset_index(drop=True)
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as ex:
        imgs = list(ex.map(load_rgb, part["filepath"]))
    X = np.stack(imgs).astype(np.uint8)
    y = part["label"].map(class_to_id).to_numpy()
    return X, y, part

X_train, y_train, train_df = build_split("train")
X_val, y_val, val_df = build_split("val")
X_test, y_test, test_df = build_split("test")

for name, X, y in [("train", X_train, y_train), ("val", X_val, y_val), ("test", X_test, y_test)]:
    print(f"{name:<5}: {X.shape} | distribusi kelas: {np.bincount(y).tolist()}")
'''

model_cell = '''
# ==========================================
# EXP 5-C: CONVNEXT-TINY (timm) + PREPROCESSING ROI U-NET
# RESEP LATIH: 2 FASE, COSINE LR, CLASS WEIGHT, AUGMENTASI WARNA
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

CFG = dict(arch="convnext_tiny", img=224, bs=64, wd=1e-4, workers=4, seed=42,
           stage1_lr=3e-4, stage1_epochs=4, stage2_lr=2e-5, stage2_epochs=15, patience=4)

dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
AMP = dev.type == "cuda"

def seed_all(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)

seed_all(CFG["seed"])
print("Device:", dev, torch.cuda.get_device_name(0) if AMP else "", "| torch", torch.__version__, "| timm", timm.__version__)


class ColorTemp:
    """Geser suhu warna: R dikali g, B dibagi g, g ~ U(1-s, 1+s)."""
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
    model.eval()
    out = []
    for x, _ in loader:
        with torch.autocast(dev.type, enabled=AMP):
            out.append(model(x.to(dev, non_blocking=True)).float().softmax(1).cpu())
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
best_model_path = str(ckpt_dir / "best_melanoma_model_exp5c_convnext_tiny.pt")
print("Checkpoint terbaik:", best_model_path)

fe, fte = CFG["stage1_epochs"], CFG["stage2_epochs"]
best, bad, history = -1.0, 0, []
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
        torch.save(model.state_dict(), best_model_path)
    elif stage == 2:
        bad += 1
        if bad >= CFG["patience"]:
            print("[INFO] Early stopping")
            break

waktu_total = (time.time() - t_start) / 60
print(f"\\n[HASIL] Total Waktu Pelatihan: {waktu_total:.2f} menit | Val Macro-F1 terbaik: {best:.4f}")
'''

eval_cell = '''
# ==========================================
# EVALUASI MODEL CONVNEXT-TINY (VALIDATION & BLIND TEST)
# ==========================================
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix

hist = pd.DataFrame(history)
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
hist.plot(x="epoch", y=["train_loss", "val_loss"], ax=axes[0], title="Loss")
hist.plot(x="epoch", y=["val_acc", "val_macro_f1", "val_auc"], ax=axes[1], title="Metrik Validasi")
for ax in axes:
    ax.axvline(CFG["stage1_epochs"] + 0.5, ls="--", c="red")
plt.tight_layout()
plt.show()

model.load_state_dict(torch.load(best_model_path, map_location=dev))
print(f"[INFO] Model terbaik dimuat dari {best_model_path}")

P_val, P_test = predict(dl_val), predict(dl_test)
pred_val, pred_test = P_val.argmax(1), P_test.argmax(1)

print("=== CLASSIFICATION REPORT (VALIDATION SET - EXP 5-C) ===")
print(classification_report(y_val, pred_val, target_names=class_names))
print("=== CLASSIFICATION REPORT (TEST SET - EXP 5-C) ===")
print(classification_report(y_test, pred_test, target_names=class_names))

rep = classification_report(y_test, pred_test, target_names=class_names, output_dict=True)
acc_test = rep["accuracy"]
macro_f1 = rep["macro avg"]["f1-score"]
mel_recall = rep["melanoma"]["recall"]
sk_recall = rep["seborrheic_keratosis"]["recall"]
score = (acc_test + macro_f1 + mel_recall + sk_recall) / 4.0

print("=== SKOR SELEKSI INTERNAL EKSPERIMEN 5-C ===")
print(f"Val Loss     : {hist.loc[hist.val_macro_f1.idxmax(), 'val_loss']:.4f}")
print(f"Test AUC     : {roc_auc_score(y_test, P_test, multi_class='ovr', average='macro'):.4f}")
print(f"Accuracy     : {acc_test * 100:.2f}%")
print(f"Macro-F1     : {macro_f1:.4f}")
print(f"Mel Recall   : {mel_recall:.4f}")
print(f"SK Recall    : {sk_recall:.4f}")
print(f"Score Seleksi: {score:.4f}")
print("==========================================")

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, (title, yt, yp, cmap) in zip(axes, [("Validation", y_val, pred_val, "Blues"), ("Test", y_test, pred_test, "Greens")]):
    sns.heatmap(confusion_matrix(yt, yp), annot=True, fmt="d", cmap=cmap,
                xticklabels=class_names, yticklabels=class_names, annot_kws={"size": 12}, ax=ax)
    ax.set_title(f"Confusion Matrix - {title} (EXP 5-C)", fontsize=14)
    ax.set_ylabel("Label Aktual")
    ax.set_xlabel("Label Prediksi")
plt.tight_layout()
plt.show()
'''

nb = {
    "cells": [
        md("# EXP 5-C: ConvNeXt-Tiny (PyTorch/timm) + Preprocessing ROI U-Net\n\n"
           "- **Preprocessing (milik sendiri):** Hair Removal → ROI Crop U-Net (+15%) → CLAHE → Pad reflect & resize 224.\n"
           "- **Model & resep latih (dari teman):** `convnext_tiny`, 2 fase (4 + maks 15 epoch), cosine LR, class weight, augmentasi warna + `ColorTemp`.\n"
           "- Seleksi model: Val Macro-F1. Test hanya dievaluasi sekali di akhir."),
        code(setup_cell),
        md("# Load dataset"),
        code(data_cell),
        md("# Preprocessing citra"),
        code(prep_cell),
        md("# Cache array"),
        code(cache_cell),
        md("# Modeling & training"),
        code(model_cell),
        md("# Evaluasi"),
        code(eval_cell),
    ],
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                 "language_info": {"name": "python"}, "accelerator": "GPU"},
    "nbformat": 4, "nbformat_minor": 5,
}

out = BASE / "sk3_bigdat_ham2019_unetmask_ak85_v2_exp5c_convnext_pytorch.ipynb"
json.dump(nb, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("SUCCESS:", out)
