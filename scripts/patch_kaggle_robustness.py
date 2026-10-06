import json
from pathlib import Path

def patch_robustness():
    # 1. Patch sk1-irisan
    p1 = Path("kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk1-irisan-tipe1-ringkas-prepjurnal.ipynb")
    with open(p1, "r", encoding="utf-8") as f:
        nb1 = json.load(f)

    # Patch Cell 16: ensure import subprocess is at the top of cell 16
    c16 = nb1["cells"][16]
    c16_str = "".join(c16["source"])
    if "import subprocess" not in c16_str:
        c16_str = "import subprocess\n" + c16_str
        c16["source"] = [l + "\n" for l in c16_str.splitlines()]
        print("Patched Cell 16 with import subprocess in sk1")

    # Patch Cell 24: rglob and auto-split fallback
    c24_src = """from pathlib import Path
import pandas as pd

split_dir = csv_path.parent
train_csv_path = split_dir / "dataset_irisan_3kelas_train.csv"
val_csv_path = split_dir / "dataset_irisan_3kelas_val.csv"
test_csv_path = split_dir / "dataset_irisan_3kelas_test.csv"

# Pencarian rekursif jika letak file CSV split berada di subfolder Kaggle
if not train_csv_path.exists():
    search_roots = [
        csv_path.parent,
        PROJECT_DIR / "Dataset" / "csv_irisan_3kelas",
        PROJECT_DIR / "Dataset",
        Path("Dataset/csv_irisan_3kelas"),
        Path("Dataset"),
        Path("/kaggle/input"),
        Path(".")
    ]
    for search_p in search_roots:
        if not search_p.exists():
            continue
        cand_train = search_p / "dataset_irisan_3kelas_train.csv"
        if cand_train.exists():
            split_dir = search_p
            train_csv_path = split_dir / "dataset_irisan_3kelas_train.csv"
            val_csv_path = split_dir / "dataset_irisan_3kelas_val.csv"
            test_csv_path = split_dir / "dataset_irisan_3kelas_test.csv"
            break
        matches = list(search_p.rglob("dataset_irisan_3kelas_train.csv"))
        if matches:
            split_dir = matches[0].parent
            train_csv_path = split_dir / "dataset_irisan_3kelas_train.csv"
            val_csv_path = split_dir / "dataset_irisan_3kelas_val.csv"
            test_csv_path = split_dir / "dataset_irisan_3kelas_test.csv"
            break

if train_csv_path.exists() and val_csv_path.exists() and test_csv_path.exists():
    print(f"Memuat partisi split anti-kebocoran dari file CSV resmi: {split_dir}")
    df_train_csv = pd.read_csv(train_csv_path)
    df_val_csv = pd.read_csv(val_csv_path)
    df_test_csv = pd.read_csv(test_csv_path)

    train_ids = set(df_train_csv["image_id"].astype(str))
    val_ids = set(df_val_csv["image_id"].astype(str))
    test_ids = set(df_test_csv["image_id"].astype(str))

    print(f"  - Train Set : {len(train_ids)} citra")
    print(f"  - Val Set   : {len(val_ids)} citra")
    print(f"  - Test Set  : {len(test_ids)} citra (100% Bebas Kebocoran)")
    
    print("\\nDistribusi label medis pada CSV split:")
    print(f"  - Train Set : {df_train_csv['harmonized_label'].value_counts().to_dict()}")
    print(f"  - Val Set   : {df_val_csv['harmonized_label'].value_counts().to_dict()}")
    print(f"  - Test Set  : {df_test_csv['harmonized_label'].value_counts().to_dict()}")
else:
    print("[INFO] CSV split terpisah tidak ditemukan, menghasilkan partisi Stratified 80:10:10 otomatis...")
    from sklearn.model_selection import train_test_split
    target_strat = df_master["target_folder"] if "target_folder" in df_master.columns else df_master["harmonized_label"]
    df_tr, df_tmp = train_test_split(df_master, test_size=0.20, random_state=42, stratify=target_strat)
    df_va, df_te = train_test_split(df_tmp, test_size=0.50, random_state=42, stratify=df_tmp["target_folder"] if "target_folder" in df_tmp.columns else df_tmp["harmonized_label"])
    train_ids = set(df_tr["image_id"].astype(str))
    val_ids = set(df_va["image_id"].astype(str))
    test_ids = set(df_te["image_id"].astype(str))
    print(f"Auto-split siap: Train={len(train_ids)}, Val={len(val_ids)}, Test={len(test_ids)}")
"""
    nb1["cells"][24]["source"] = [l + "\n" for l in c24_src.splitlines()]
    print("Patched Cell 24 with robust search and auto-split fallback in sk1")

    with open(p1, "w", encoding="utf-8") as f:
        json.dump(nb1, f, indent=1, ensure_ascii=False)

if __name__ == "__main__":
    patch_robustness()
