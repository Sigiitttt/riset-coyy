import pandas as pd
import os

ROOT = r"C:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\Dataset"
p17_train = os.path.join(ROOT, "isic 2017", "ISIC-2017_Training_Data", "ISIC-2017_Training_Part3_GroundTruth.csv")
p17_val = os.path.join(ROOT, "isic 2017", "ISIC-2017_Validation_Data", "ISIC-2017_Validation_Part3_GroundTruth.csv")
p17_test = os.path.join(ROOT, "isic 2017", "ISIC-2017_Test_v2_Data", "ISIC-2017_Test_v2_Part3_GroundTruth.csv")

p19_train = os.path.join(ROOT, "isic 2019", "ISIC_2019_Training_Input", "ISIC_2019_Training_GroundTruth.csv")
p19_test = os.path.join(ROOT, "isic 2019", "ISIC_2019_Test_Input", "ISIC_2019_Test_Metadata.csv")

df17_tr = pd.read_csv(p17_train)
df17_va = pd.read_csv(p17_val)
df17_te = pd.read_csv(p17_test)

ids17_all = set(df17_tr.iloc[:, 0].str.replace('.jpg', '')) | \
            set(df17_va.iloc[:, 0].str.replace('.jpg', '')) | \
            set(df17_te.iloc[:, 0].str.replace('.jpg', ''))

print("Total citra ISIC 2017 (Train+Val+Test):", len(ids17_all))

df19_tr = pd.read_csv(p19_train)
ids19_tr = set(df19_tr['image'])

df19_te_meta = pd.read_csv(p19_test)
ids19_te = set(df19_te_meta['image'])

print("Total ISIC 2019 Train IDs:", len(ids19_tr))
print("Total ISIC 2019 Test IDs :", len(ids19_te))

ids19_all = ids19_tr | ids19_te

print("--- Hasil Pencocokan ISIC 2017 ke ISIC 2019 ---")
print("1. Cocok persis di ISIC 2019 Train saja       :", len(ids17_all.intersection(ids19_tr)))
print("2. Cocok persis di ISIC 2019 Test saja        :", len(ids17_all.intersection(ids19_te)))
print("3. Total cocok persis di ISIC 2019 (Train+Test):", len(ids17_all.intersection(ids19_all)))

unmatched = ids17_all - ids19_all
print("4. Tidak cocok persis (unmatched)             :", len(unmatched))

# Cek base_id tanpa downsampled
ids19_base = {x.split('_downsampled')[0] for x in ids19_all}
print("5. Cocok jika _downsampled diabaikan          :", len(ids17_all.intersection(ids19_base)))
unmatched_base = ids17_all - ids19_base
print("6. Tetap tidak cocok setelah base_id          :", len(unmatched_base))
print("Sisa yang tidak cocok sama sekali             :", list(unmatched_base)[:10])
