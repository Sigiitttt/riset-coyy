# 🔬 Data Understanding, Harmonisasi, & Modeling Dataset ISIC (2016–2024) & HAM10000

Repositori ini memuat seluruh pipeline kurasi data medis, deduplikasi terarah, partisi data bebas kebocoran lesi (*lesion-aware split*), telaah jurnal internasional (Scopus Q1), dan pipeline eksperimen baseline deep learning untuk klasifikasi lesi kulit (*dermoscopy skin lesion*).

---

## 📌 Gambaran Umum Riset

Riset ini mengintegrasikan repositori arsip lesi kulit internasional terbesar di dunia (**ISIC Archive 2016 s.d. 2024** dan **HAM10000**) ke dalam skenario diagnosis terstandarisasi:

### 1. Jalur Irisan 3 Kelas Multiclass (Pilihan Utama — Siap Latih)
* **Dataset Sumber:** HAM10000 $\cap$ ISIC 2017 $\cap$ ISIC 2019
* **Diagnosis Target:**
  * `NV` (0): Melanocytic Nevus *(Tahi Lalat Jinak)* — 14.148 citra (64,2%)
  * `MEL` (1): Melanoma *(Kanker Ganas Kulit)* — 4.895 citra (22,2%)
  * `BKL` (2): Benign Keratosis *(Keratosis Seboroik Jinak)* — 3.008 citra (13,6%)
* **Total Citra Bersih:** **22.051 citra** (100% bebas duplikat, 0 missing value)
* **Partisi Bebas Kebocoran Lesi (*Lesion-Aware Stratified Split 80:10:10*):**
  * `Train Set` (80,07%): 17.656 citra (`dataset_irisan_3kelas_train.csv`)
  * `Validation Set` (9,94%): 2.192 citra (`dataset_irisan_3kelas_val.csv`)
  * `Test Set` (9,99%): 2.203 citra (`dataset_irisan_3kelas_test.csv`)
  * *Audit Kebocoran Lesi:* **0 overlap lesi** antar-subset data.

### 2. Jalur Irisan 7 Kelas (Alternatif Benchmark Emas)
* **Dataset Sumber:** HAM10000 $\cap$ ISIC 2019 (Standar HAM10k / ISIC 2018 Task 3)
* **Diagnosis Target:** `NV`, `MEL`, `BCC`, `BKL`, `AKIEC`, `VASC`, `DF`
* **Total Citra Bersih:** **24.900 citra** (`dataset_irisan_7kelas_final.csv`)

### 3. Jalur Biner (Benign vs Malignant)
* **Total Citra Bersih:** **33.552 citra** (`dataset_binary_final.csv`)
  * Benign (0): 23.504 citra (70,0%) $\rightarrow$ `NV`, `BKL`, `DF`, `VASC`
  * Malignant (1): 10.048 citra (30,0%) $\rightarrow$ `MEL`, `BCC`, `AKIEC`, `SCC`

---

## 📂 Struktur Direktori Proyek

```text
├── Dataset/                                # Direktori CSV hasil kurasi & split siap latih
│   ├── dataset_irisan_multiclass_final.csv # Master dataset irisan 3 kelas (22.051 baris)
│   ├── dataset_irisan_3kelas_train.csv     # Training set 80% (17.656 baris)
│   ├── dataset_irisan_3kelas_val.csv       # Validation set 10% (2.192 baris)
│   ├── dataset_irisan_3kelas_test.csv      # Test set 10% (2.203 baris)
│   ├── dataset_irisan_7kelas_final.csv     # Master dataset 7 kelas (24.900 baris)
│   └── dataset_binary_final.csv            # Master dataset biner (33.552 baris)
├── kode/                                   # Direktori kode & notebook terstruktur rapi
│   ├── 1_data_understanding/               # Eksplorasi awal dataset ISIC & HAM10000
│   ├── 2_jalur_biner/                      # Pipeline pemetaan biner (33.552 citra)
│   ├── 3_jalur_irisan_3kelas/              # Pipeline irisan 3 kelas, modeling, & train_baseline.py
│   └── 4_jalur_irisan_7kelas/              # Pipeline irisan 7 kelas benchmark (24.900 citra)
├── notes jurnal/                           # Analisis literatur paper ilmiah Scopus Q1
│   ├── irisan/                             # Ringkasan paper pendukung jalur irisan
│   └── biner/                              # Ringkasan paper pendukung jalur biner
├── models/                                 # Direktori penyimpanan bobot model terbaik (.pth)
├── plan.text                               # Diagram konsep arsitektur alur penelitian
├── AGENTS.md                               # Protokol sesi otomatis AI (/start & /end)
├── CATATAN_MEMORI_PROYEK.md                # Dokumen memori proyek komprehensif
└── README.md                               # Dokumentasi repositori
```

---

## 🚀 Panduan Memulai & Menjalankan Kode

### 1. Kloning Repositori
```bash
git clone https://github.com/Sigiitttt/riset-coyy.git
cd riset-coyy
```

### 2. Menjalankan Notebook & Script
1. **Pemetaan & Partisi Data:** Buka [`kode/3_jalur_irisan_3kelas/irisan_mapping.ipynb`](kode/3_jalur_irisan_3kelas/irisan_mapping.ipynb) untuk melihat proses deduplikasi terarah dan pembentukan subset Train/Val/Test.
2. **Eksperimen Deep Learning (Jupyter):** Buka [`kode/3_jalur_irisan_3kelas/baseline_modeling_3kelas.ipynb`](kode/3_jalur_irisan_3kelas/baseline_modeling_3kelas.ipynb) untuk melatih model baseline (ResNet-50 / EfficientNet-B0).
3. **Eksekusi Pelatihan Cepat (Python CLI):** Jalankan [`kode/3_jalur_irisan_3kelas/train_baseline.py`](kode/3_jalur_irisan_3kelas/train_baseline.py):
   ```bash
   python kode/3_jalur_irisan_3kelas/train_baseline.py --model efficientnet_b0 --epochs 10
   ```

---

## 📚 Rujukan Ilmiah Utama
* **Codella et al. (IEEE ISBI 2018):** *Skin Lesion Analysis Toward Melanoma Detection: A Challenge at the 2017 International Symposium on Biomedical Imaging (ISBI).*
* **Tschandl et al. (Nature Scientific Data 2018):** *The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions.*
* **Azeem et al. (MDPI Cancers 2024):** *SkinLesNet: Deep Learning Approach for Skin Lesion Classification.*
* **Ichim et al. (MDPI Cancers 2023):** *Analysis and Removal of Dataset Overlap across Public Dermatological Archives.*
