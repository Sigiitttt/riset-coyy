"""
Script Pelatihan Baseline Deep Learning 3 Kelas (Multiclass)
Dataset Irisan Bebas Kebocoran: HAM10000 ∩ ISIC 2017 ∩ ISIC 2019 (22.051 Citra)
Target: NV (0), MEL (1), BKL (2)
"""

import os
import sys
import time
import argparse
import random
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns

# Pastikan UTF-8 encoding untuk stdout/stderr
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
import torchvision.models as models

from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score,
    precision_recall_fscore_support, confusion_matrix,
    roc_auc_score, roc_curve
)

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]
CLASS_NAMES = ["NV", "MEL", "BKL"]
CLASS_FULLNAMES = ["Melanocytic Nevus", "Melanoma", "Benign Keratosis"]


class SkinLesionDataset(Dataset):
    def __init__(self, df, transform=None, base_dir=None):
        self.df = df.reset_index(drop=True)
        self.transform = transform
        self.base_dir = base_dir

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = str(row['filepath'])

        # Fallback jika path absolut dari machine lain
        if not os.path.exists(img_path):
            filename = os.path.basename(img_path)
            if self.base_dir:
                candidate = os.path.join(self.base_dir, filename)
                if os.path.exists(candidate):
                    img_path = candidate
                else:
                    for root, _, files in os.walk(self.base_dir):
                        if filename in files:
                            img_path = os.path.join(root, filename)
                            break

        image = Image.open(img_path).convert("RGB")
        target = int(row['target_multiclass'])

        if self.transform:
            image = self.transform(image)

        return image, target


def build_baseline_model(model_name="resnet50", num_classes=3, pretrained=True):
    if model_name == "resnet50":
        weights = models.ResNet50_Weights.DEFAULT if pretrained else None
        model = models.resnet50(weights=weights)
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, num_classes)
    elif model_name == "efficientnet_b0":
        weights = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
        model = models.efficientnet_b0(weights=weights)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, num_classes)
    else:
        raise ValueError(f"Model {model_name} belum didukung.")
    return model


def train_one_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    all_preds = []
    all_targets = []

    for images, targets in dataloader:
        images = images.to(device)
        targets = targets.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, preds = torch.max(outputs, 1)

        all_preds.extend(preds.cpu().numpy())
        all_targets.extend(targets.cpu().numpy())

    epoch_loss = running_loss / len(dataloader.dataset)
    epoch_acc = accuracy_score(all_targets, all_preds)
    _, _, epoch_f1_macro, _ = precision_recall_fscore_support(all_targets, all_preds, average='macro', zero_division=0)

    return epoch_loss, epoch_acc, epoch_f1_macro


def validate(model, dataloader, criterion, device):
    model.eval()
    running_loss = 0.0
    all_preds = []
    all_targets = []
    all_probs = []

    with torch.no_grad():
        for images, targets in dataloader:
            images = images.to(device)
            targets = targets.to(device)

            outputs = model(images)
            loss = criterion(outputs, targets)

            running_loss += loss.item() * images.size(0)
            probs = torch.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)

            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(targets.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())

    val_loss = running_loss / len(dataloader.dataset)
    val_acc = accuracy_score(all_targets, all_preds)
    val_bal_acc = balanced_accuracy_score(all_targets, all_preds)
    _, _, val_f1_macro, _ = precision_recall_fscore_support(all_targets, all_preds, average='macro', zero_division=0)

    return val_loss, val_acc, val_bal_acc, val_f1_macro, np.array(all_targets), np.array(all_preds), np.array(all_probs)


def evaluate_test(model, test_loader, criterion, device, output_dir, model_name):
    test_loss, test_acc, test_bal_acc, test_f1_macro, targets, preds, probs = validate(
        model, test_loader, criterion, device
    )

    try:
        macro_roc_auc = roc_auc_score(targets, probs, multi_class='ovr', average='macro')
    except Exception:
        macro_roc_auc = 0.0

    cm = confusion_matrix(targets, preds)
    per_class_p, per_class_r, per_class_f1, support = precision_recall_fscore_support(targets, preds, zero_division=0)

    print("\n" + "=" * 78)
    print(f"        HASIL EVALUASI TEST SET ({model_name.upper()})")
    print("=" * 78)
    print(f"  Overall Accuracy        : {test_acc * 100:.2f}%")
    print(f"  Balanced Accuracy       : {test_bal_acc * 100:.2f}%")
    print(f"  Macro Average F1-Score  : {test_f1_macro * 100:.2f}%")
    print(f"  Macro ROC-AUC (OvR)     : {macro_roc_auc * 100:.2f}%")
    print(f"  Melanoma Sensitivity    : {per_class_r[1] * 100:.2f}% (Deteksi Kanker Ganas)")
    print("-" * 78)

    rows = []
    for i, (code, desc) in enumerate(zip(CLASS_NAMES, CLASS_FULLNAMES)):
        tn = np.sum(np.delete(np.delete(cm, i, axis=0), i, axis=1))
        fp = np.sum(np.delete(cm[:, i], i))
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        rows.append({
            "Class": code,
            "Diagnosis": desc,
            "Samples": support[i],
            "Recall_Sensitivity": f"{per_class_r[i]*100:.2f}%",
            "Specificity": f"{spec*100:.2f}%",
            "Precision": f"{per_class_p[i]*100:.2f}%",
            "F1_Score": f"{per_class_f1[i]*100:.2f}%"
        })
    df_metrics = pd.DataFrame(rows)
    print(df_metrics.to_string(index=False))
    print("=" * 78)

    # Plot Confusion Matrix
    fig, ax = plt.subplots(figsize=(7, 6))
    cm_norm = cm.astype('float') / np.maximum(cm.sum(axis=1)[:, np.newaxis], 1e-12)
    labels_display = [f"{c}\n({f})" for c, f in zip(CLASS_NAMES, CLASS_FULLNAMES)]
    sns.heatmap(cm_norm, annot=True, fmt=".2%", cmap="Blues", cbar=True,
                xticklabels=labels_display, yticklabels=labels_display, ax=ax,
                annot_kws={"size": 10, "weight": "bold"})
    ax.set_title(f"Normalized Confusion Matrix - {model_name.upper()}", fontsize=12, fontweight='bold')
    ax.set_xlabel("Prediksi Model", fontweight='bold')
    ax.set_ylabel("Ground Truth Medis", fontweight='bold')
    plt.tight_layout()
    cm_path = os.path.join(output_dir, f"cm_{model_name}.png")
    plt.savefig(cm_path, dpi=200)
    plt.close()
    print(f"[SAVE] Confusion matrix tersimpan ke: {cm_path}")

    return {
        "model": model_name,
        "test_acc": test_acc,
        "test_bal_acc": test_bal_acc,
        "test_f1_macro": test_f1_macro,
        "macro_roc_auc": macro_roc_auc,
        "mel_sensitivity": per_class_r[1],
        "mel_f1": per_class_f1[1],
        "nv_f1": per_class_f1[0],
        "bkl_f1": per_class_f1[2]
    }


def main():
    parser = argparse.ArgumentParser(description="Pelatihan Baseline Deep Learning 3 Kelas")
    parser.add_argument("--model", type=str, default="resnet50", choices=["resnet50", "efficientnet_b0"])
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--weight_decay", type=float, default=1e-2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--smoke_test", action="store_true", help="Uji coba cepat 64 sampel untuk validasi pipeline")
    parser.add_argument("--num_workers", type=int, default=0)
    args = parser.parse_args()

    # Reproducibility
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[DEVICE] Menggunakan Perangkat Komputasi: {device}")
    if device.type == "cuda":
        print(f"         GPU: {torch.cuda.get_device_name(0)}")

    # Cari file CSV (Adaptif terhadap working directory root, kode/, maupun subfolder)
    data_dir = None
    for cand in ["Dataset", "../Dataset", "../../Dataset"]:
        if os.path.exists(cand):
            data_dir = cand
            break
    if data_dir is None:
        raise FileNotFoundError("Direktori 'Dataset' tidak ditemukan!")

    train_csv = os.path.join(data_dir, "dataset_irisan_3kelas_train.csv")
    val_csv   = os.path.join(data_dir, "dataset_irisan_3kelas_val.csv")
    test_csv  = os.path.join(data_dir, "dataset_irisan_3kelas_test.csv")

    output_dir = None
    for cand in ["models", "../models", "../../models"]:
        if os.path.exists(cand):
            output_dir = cand
            break
    if output_dir is None:
        output_dir = "models"
    os.makedirs(output_dir, exist_ok=True)

    df_train = pd.read_csv(train_csv)
    df_val   = pd.read_csv(val_csv)
    df_test  = pd.read_csv(test_csv)

    if args.smoke_test:
        print("[INFO] Mode SMOKE TEST diaktifkan: Membatasi 64 sampel per split untuk verifikasi cepat.")
        df_train = df_train.sample(n=min(64, len(df_train)), random_state=args.seed)
        df_val   = df_val.sample(n=min(32, len(df_val)), random_state=args.seed)
        df_test  = df_test.sample(n=min(32, len(df_test)), random_state=args.seed)
        args.epochs = 1

    # Class Weights
    cls_counts = df_train['target_multiclass'].value_counts().sort_index()
    total_samples = len(df_train)
    n_classes = 3
    class_weights = [total_samples / (n_classes * cls_counts.get(c, 1)) for c in range(n_classes)]
    weights_tensor = torch.tensor(class_weights, dtype=torch.float32).to(device)

    # Transforms
    train_transforms = transforms.Compose([
        transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(degrees=20),
        transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

    eval_transforms = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

    train_ds = SkinLesionDataset(df_train, transform=train_transforms, base_dir=data_dir)
    val_ds   = SkinLesionDataset(df_val, transform=eval_transforms, base_dir=data_dir)
    test_ds  = SkinLesionDataset(df_test, transform=eval_transforms, base_dir=data_dir)

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                              num_workers=args.num_workers, pin_memory=(device.type == 'cuda'))
    val_loader   = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False,
                              num_workers=args.num_workers, pin_memory=(device.type == 'cuda'))
    test_loader  = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False,
                              num_workers=args.num_workers, pin_memory=(device.type == 'cuda'))

    # Build Model
    model = build_baseline_model(model_name=args.model, num_classes=3, pretrained=True).to(device)
    criterion = nn.CrossEntropyLoss(weight=weights_tensor)
    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-6)

    best_val_f1 = -1.0
    best_checkpoint_path = os.path.join(output_dir, f"best_{args.model}_baseline.pth")

    print(f"\n[TRAIN] Memulai Pelatihan Model: {args.model.upper()} ({args.epochs} Epochs)...")
    start_time = time.time()

    for epoch in range(1, args.epochs + 1):
        ep_start = time.time()
        tr_loss, tr_acc, tr_f1 = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc, val_bal_acc, val_f1, _, _, _ = validate(model, val_loader, criterion, device)
        scheduler.step()
        ep_time = time.time() - ep_start

        improved = ""
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "val_f1_macro": val_f1,
                "val_balanced_acc": val_bal_acc,
                "config": vars(args)
            }, best_checkpoint_path)
            improved = " [BEST CHECKPOINT]"

        print(f"Epoch [{epoch:02d}/{args.epochs:02d}] ({ep_time:.1f}s) | "
              f"Train Loss: {tr_loss:.4f} Acc: {tr_acc*100:.1f}% F1: {tr_f1*100:.1f}% | "
              f"Val Loss: {val_loss:.4f} Acc: {val_acc*100:.1f}% BalAcc: {val_bal_acc*100:.1f}% F1: {val_f1*100:.1f}%{improved}")

    total_time = time.time() - start_time
    print(f"\n[DONE] Pelatihan Selesai dalam {total_time/60:.2f} menit. Best Val Macro F1: {best_val_f1*100:.2f}%")

    # Muat Best Model untuk Evaluasi Test Set
    if os.path.exists(best_checkpoint_path):
        chk = torch.load(best_checkpoint_path, map_location=device, weights_only=False)
        model.load_state_dict(chk['model_state_dict'])

    res = evaluate_test(model, test_loader, criterion, device, output_dir, args.model)

    # Simpan ke tabel ringkasan perbandingan
    summary_csv = os.path.join(output_dir, "baseline_comparison_results.csv")
    df_new = pd.DataFrame([res])
    if os.path.exists(summary_csv):
        df_exist = pd.read_csv(summary_csv)
        df_exist = df_exist[df_exist['model'] != args.model] # timpa jika model sama
        df_combined = pd.concat([df_exist, df_new], ignore_index=True)
    else:
        df_combined = df_new
    df_combined.to_csv(summary_csv, index=False)
    print(f"[SUMMARY] Hasil komparasi diperbarui di: {summary_csv}")


if __name__ == "__main__":
    main()
