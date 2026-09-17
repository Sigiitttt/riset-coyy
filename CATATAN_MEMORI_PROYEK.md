# 🧠 DOKUMEN MEMORI UTAMA PROYEK (PERSISTENT MEMORY)
**Proyek:** Data Understanding & Pemetaan Dataset ISIC (2016–2024) & HAM10000  
**Lokasi Direktori:** `C:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\`  
* **Terakhir Diperbarui:** 17 September 2026, Pukul 22:45 WIB (Sesi Aktif)  


---

## ⚡ PROTOKOL PERINTAH SESI KERJA

* **`/start`** $\rightarrow$ **Pulihkan Memori & Langsung Lanjut:**  
  Agen wajib membaca dokumen ini, memulihkan status kerja terakhir, dan langsung melanjutkan langkah berikutnya dari checklist tanpa mengulang dari awal.
* **`/end`** $\rightarrow$ **Sesi Selesai & Simpan Memori:**  
  Agen menghentikan pekerjaan secara aman, memperbarui dokumen ini dengan progres terbaru, memperbarui checklist, dan menyimpan status proyek.


---

## 1. Konsep & Arsitektur Alur Riset (`plan.text`)

Riset ini terbagi menjadi 2 jalur independen:
1. **JALUR BINARY (Deteksi Kanker Kulit: Benign vs Malignant)**
   * Mengelompokkan seluruh diagnosis ke dalam 2 kelas: Jinak (0) vs Ganas (1).
   * Didasarkan pada 1 paper rujukan utama per dataset + konsensus voting literatur internasional.
2. **JALUR IRISAN (Harmonisasi Multiclass Diagnosis Spesifik)**
   * Membandingkan label asli antar-dataset.
   * Melakukan harmonisasi sinonim medis (`seborrheic_keratosis` ≡ `bkl`, `nevus` ≡ `nv`, `melanoma` ≡ `mel`).
   * Mengambil irisan kelas yang terdapat pada seluruh dataset yang dipilih.
   * Percabangan: jika irisan menghasilkan 2 kelas $\rightarrow$ *Binary*, jika $> 2$ kelas $\rightarrow$ *Multiclass*.

---

## 2. Status Implementasi Notebook di Folder `kode/`

### A. `binary_mapping.ipynb` (Jalur Binary — Status: SELESAI 100% & DIRESTRUKTURISASI)
* **Dataset yang Digunakan:** HAM10000, ISIC 2017, ISIC 2019.
* **Aturan Deduplikasi:** HAM10000 dipertahankan 100% utuh (10.015 citra), duplikat di 2019 dan 2017 dibersihkan.
* **Hasil Akhir:** **33.552 citra bersih** (setelah drop 2.047 citra `UNK`)
  * **Benign (0):** 20.998 citra (62,6%) $\rightarrow$ `NV` (16.643), `BKL` (3.668), `VASC` (357), `DF` (330)
  * **Malignant (1):** 12.554 citra (37,4%) $\rightarrow$ `MEL` (6.222), `BCC` (4.298), `AKIEC` (1.438), `SCC` (596)
* **Restrukturisasi Profesional (Versi Baru — 13 Langkah Modular / 29 Cells):**
  * Penjelasan markdown dirapikan menjadi singkat, padat, mudah dipahami (setara usia 17 tahun/SMA), komunikatif dan *like human*.
  * Pemisahan Cell 3 menjadi dua langkah mandiri: Langkah 2 (Scan citra fisik $\rightarrow$ 46.334 citra) dan Langkah 3 (Pemasangan label CSV ground truth $\rightarrow$ 46.334 citra berlabel).
  * Menambahkan markdown penjelas independen untuk harmonisasi label, visualisasi sebaran 8 kelas, pemisah grafik biner, dan ekspor.
  * 100% output eksekusi (tabel HTML, grafik PNG, print log) tetap utuh dipertahankan. Salinan cadangan aman tersimpan di `binary_mapping.ipynb.bak`.
* **Output File:** `Dataset/dataset_binary_final.csv` (33.552 baris, kolom: `image_id`, `source`, `original_label`, `unified_class`, `binary_class`, `target_binary`, `filepath`).


---

### A.1 `gabungan_ham10k_2017_2019.ipynb` (Analisis Penggabungan 3 Dataset & 9 Kelas Medis — Status: SELESAI 100%)
* **Dataset yang Digunakan:** HAM10000, ISIC 2017 (Train/Val/Test), ISIC 2019 (Train/Test) — total 6 partisi data.
* **Hasil Penggabungan:** Menghasilkan **9 KELAS MEDIS HARMONISASI** (`NV`, `MEL`, `BCC`, `BKL`, `AKIEC`, `SCC`, `VASC`, `DF`, dan `UNK`).
* **Kuantitas Citra:**
  * **RAW (Mentah):** **46.334 citra** (HAM10k: 10.015, ISIC 2019: 33.569, ISIC 2017: 2.750).
  * **BERSIH (Bebas Duplikat):** **35.599 citra** (10.735 duplikat dibuang dengan mempertahankan HAM10000 100% utuh).
  * **BERSIH Tanpa UNK:** **33.552 citra** (siap klasifikasi biner maupun multiclass).
* **Output File:** `Dataset/dataset_gabungan_ham10k_2017_2019.csv` (35.599 baris).
* **Status Git:** Telah di-commit dan tersinkronisasi ke remote `origin/main` (`df7999d`).

---

### B. `irisan_mapping.ipynb` (Jalur Irisan 3 Kelas: HAM10k ∩ ISIC 2017 ∩ ISIC 2019 — Status: PILIHAN AKTIF & SELESAI 100%)
* **Dataset yang Digunakan:** HAM10000, ISIC 2017 (Train/Val/Test), ISIC 2019 (Training Data).
* **Hasil Irisan Bersama:** Tepat menghasilkan **3 KELAS MULTICLASS**:
  * **`NV` (0):** 14.148 citra (64,2%) — *Melanocytic Nevus (Tahi Lalat Jinak)*
  * **`MEL` (1):** 4.895 citra (22,2%) — *Melanoma (Kanker Ganas)*
  * **`BKL` (2):** 3.008 citra (13,6%) — *Benign Keratosis (Keratosis Seboroik Jinak)*
* **Total Citra Bersih:** **22.051 citra** (100% bebas dari duplikat, 0 missing values).
* **Sebaran Sumber Citra:**
  * ISIC 2019 Training: 11.104 citra
  * HAM10000: 8.917 citra (100% sampel NV, MEL, BKL pada HAM10k dipertahankan utuh)
  * ISIC 2017 Training: 1.283 citra
  * ISIC 2017 Test: 599 citra
  * ISIC 2017 Validation: 148 citra
* **Pemisahan Data Bebas Kebocoran (*Lesion-Aware Stratified Split 80:10:10*):**
  * **Algoritma:** `StratifiedGroupKFold` dengan pengelompokan `lesion_id` dan seed acak (`random_state=42`).
  * **Training Set (80,07%):** 17.656 citra (NV: 11.302, MEL: 3.902, BKL: 2.452)
  * **Validation Set (9,94%):** 2.192 citra (NV: 1.455, MEL: 450, BKL: 287)
  * **Test Set (9,99%):** 2.203 citra (NV: 1.391, MEL: 543, BKL: 269)
  * **Audit Kebocoran Lesi (*Lesion Leakage*):** 0 overlap antara Train, Val, dan Test (100% bebas kebocoran lesi pasien).
* **Output File Siap Pakai:**
  * `Dataset/dataset_irisan_multiclass_final.csv` (4,88 MB, 22.051 baris dengan kolom `split` dan `lesion_id`).
  * `Dataset/dataset_irisan_3kelas_train.csv` (3,92 MB, 17.656 baris).
  * `Dataset/dataset_irisan_3kelas_val.csv` (482 KB, 2.192 baris).
  * `Dataset/dataset_irisan_3kelas_test.csv` (486 KB, 2.203 baris).
* **Status:** **PILIHAN AKTIF & DIEKSEKUSI PENUH HINGGA TAHAP SIAP LATIH** — Lengkap dengan Langkah 1–10.

---

### B.1 `data_understanding_irisan_3kelas improve.ipynb` (Data Understanding Irisan 3 Kelas — Status: SELESAI 100%)
* **Dataset yang Digunakan:** HAM10000 (10.015), ISIC 2017 (2.750), ISIC 2019 (25.331).
* **Struktur Modular:** 12 Langkah terstruktur (24 sel: 12 Markdown ringkas + 11 Code sel + 1 Header) dengan standar metodologi CRISP-DM tanpa kebocoran logika.
* **Kalkulasi Dinamis Penuh:** Seluruh angka irisan dihitung secara dinamis dari data mentah dan eliminasi duplikat tanpa *hardcoding* data.
* **Hasil Irisan 3 Kelas Bersih:**
  * **`NV`:** 14.148 citra (64,2%)
  * **`MEL`:** 4.895 citra (22,2%)
  * **`BKL`:** 3.008 citra (13,6%)
  * **Total Bersih:** **22.051 citra** (100% bebas duplikat)
* **Gaya Penulisan & Visual:** Singkat, padat, jelas, 100% bebas emoji, tabel deduplikasi lengkap dengan kolom `Duplikat dengan Dataset Mana`, serta output visual grafik 4 kuadran dan sampel fisik pre-rendered utuh.

---

### B.2 `irisan_mapping improve.ipynb` (Data Preparation Irisan 3 Kelas — Status: SELESAI 100%)
* **Dataset yang Digunakan:** HAM10000, ISIC 2017 (Train/Val/Test), ISIC 2019 (Training Data).
* **Struktur Modular:** 11 Langkah terstruktur (22 sel: 11 Markdown ringkas + 10 Code sel + 1 Header), sel kosong Cell 22 lama telah dihapus dan diganti kesimpulan kesiapan modeling.
* **Proses Kunci yang Dilakukan:**
  1. Pemindaian 38.096 citra fisik dan pemasangan ground truth asli.
  2. Deduplikasi terarah (HAM10000 100% utuh, 10.735 dibuang, tabel dilengkapi kolom `Duplikat dengan Dataset Mana`).
  3. Harmonisasi label medis internasional dan seleksi 3 kelas bersama (`NV`, `MEL`, `BKL`).
  4. Validasi integritas tepat **22.051 citra bersih** (NV: 14.148, MEL: 4.895, BKL: 3.008) dengan 0 missing values.
  5. Ekspor master dataset ke `Dataset/dataset_irisan_multiclass_final.csv`.
  6. Pembagian data anti-kebocoran (*Lesion-Aware Stratified Split 80:10:10*) via `StratifiedGroupKFold`:
     * **Training:** 17.656 citra (80,07%)
     * **Validation:** 2.192 citra (9,94%)
     * **Test:** 2.203 citra (9,99%)
     * **Overlap Lesi Pasien:** **0 (100% Bebas Kebocoran Data)**
* **Gaya Penulisan & Visual:** Singkat, padat, jelas, 100% bebas emoji, tabel HTML, grafik batang ganda base64 PNG pre-rendered utuh.

---



### C. `irisan_7kelas_mapping.ipynb` (Jalur Irisan 7 Kelas: HAM10k ∩ ISIC 2019 — Status: ALTERNATIF SELESAI 100%)
* **Konsep:** Menggabungkan HAM10000 dan ISIC 2019 (tanpa ISIC 2017) untuk mempertahankan 7 kelas standar emas benchmark medis dunia.
* **Hasil Irisan (Standar Emas Benchmark HAM10000 / ISIC 2018 Task 3):**
  1. `NV`: 12.875 citra (51,7%) | 2. `MEL`: 4.522 citra (18,2%) | 3. `BCC`: 3.323 citra (13,3%) | 4. `BKL`: 2.624 citra (10,5%) | 5. `AKIEC`: 1.064 citra (4,3%) | 6. `VASC`: 253 citra (1,0%) | 7. `DF`: 239 citra (1,0%)
* **Total Citra Bersih:** **24.900 citra** (100% bebas dari duplikat, 0 missing values).
* **Output File:** `Dataset/dataset_irisan_7kelas_final.csv` (4,39 MB, 24.900 baris).
* **Status:** **SELESAI & TERSIMPAN** — Tersedia sebagai alternatif benchmark komparasi 7 kelas.

### A.2 `data understanding biner improve.ipynb` (Data Understanding Biner 3 Dataset — Status: SELESAI 100%)
* **Fokus Riset:** Khusus pada 3 dataset acuan Jalur Biner: HAM10000, ISIC 2017, dan ISIC 2019 (6 partisi data).
* **Struktur Modular:** 12 Langkah terstruktur (25 sel) dengan format 1 Markdown ringkas + 1 Code sel.
* **Gaya Penulisan:** Singkat, padat, jelas, tanpa emoji, komentar kode bersih dan secukupnya, mudah dipahami (setara usia 17 tahun/SMA).
* **Kuantitas Citra:**
  * **Data Mentah:** 46.334 citra fisik (HAM10k: 10.015, ISIC 2019: 33.569, ISIC 2017: 2.750).
  * **Duplikat Dibuang:** 10.735 citra kembar (protokol prioritas HAM10000 100% utuh).
  * **Data Bersih Final:** 35.599 citra unik siap masuk ke tahap harmonisasi dan pemetaan biner.
* **Output Lengkap:** Seluruh grafik PNG visualisasi kelas asli dan komparasi deduplikasi, tabel HTML, dan log print ter-render utuh.



### ISIC 2020 (`ISIC_2020_Training_GroundTruth_v2.csv` — 33.126 citra)
* **`unknown`:** 27.124 (81,88%) — Skrining tele-dermatologi non-biopsi (Jinak / 0)
* **`nevus`:** 5.193 (15,68%) — Jinak / 0
* **`melanoma`:** 584 (1,76%) — **Satu-satunya kelas GANAS (1) di ISIC 2020**
* **`seborrheic keratosis`:** 135 (0,41%) — Jinak / 0
* **`lentigo NOS`:** 44 (0,13%) — Jinak / 0
* **`lichenoid keratosis`:** 37 (0,11%) — Jinak / 0
* **`solar lentigo`:** 7 (0,02%) — Jinak / 0
* **`cafe-au-lait macule`:** 1 (0,003%) — Jinak / 0
* **`atypical melanocytic proliferation`:** 1 (0,003%) — Jinak / 0

### ISIC 2024 (`ISIC_2024_Training_Supplement.csv` — 401.059 citra)
* **`iddx_1`:** `Benign` (400.552), `Indeterminate` (114), `Malignant` (393).
* **`iddx_2`:** 14 kategori jaringan/histopatologi untuk 1.068 sampel biopsi.
* **`iddx_3`:** 24 diagnosis spesifik untuk 1.065 sampel biopsi.
  * 393 kasus kanker ganas terbagi tepat menjadi: Basal cell carcinoma (163), Melanoma in situ (80), Melanoma invasive (63), Melanoma NOS (13), Melanoma metastasis (1), SCC in situ (49), SCC invasive (22), SCC NOS (2) = **393**.

---

## 4. Rujukan Paper Utama & Konsensus Ilmiah

### A. Rujukan Jalur Biner (Benign 0 vs Malignant 1)
1. **HAM10000:** Ioannis Kousis et al. (*MDPI Electronics 2022*), SkinNet-16 (*Frontiers 2022*), Harangi et al. (*BSPC Elsevier 2020*), Ameri (*JBPE 2020*).
2. **ISIC 2017:** Catarina Barata et al. (*Pattern Recognition Elsevier 2020*) & Jojoa Acosta et al. (*Springer 2021*).
3. **ISIC 2019:** MorphoNet / Bradley Yao et al. (*MDPI Bioengineering 2026*), Venugopal et al. (*DAJ Elsevier 2023*).
4. **Konsensus 8 Kelas Medis:**
   * Benign (0): NV (100%), BKL (100%), DF (100%), VASC (80%).
   * Malignant (1): MEL (100%), BCC (100%), SCC (100%), AKIEC (83%).

### B. Rujukan Jalur Irisan 7 Kelas (HAM10000 ∩ ISIC 2019 — Alternatif Benchmark)
1. **Baig et al. (MDPI Diagnostics 2023 - Kecocokan 95%):** Formulasi tepat 7 kelas multiclass dari gabungan HAM10k + ISIC 2019 (`AK`, `BCC`, `BK/BKL`, `DF`, `NV`, `MEL`, `VASC`).
2. **Ichim et al. (MDPI Cancers 2023 - Kecocokan 85%):** Protokol eliminasi duplikasi (*overlap removal*) citra lesi antar-arsip ISIC dan HAM10000.
3. **Tschandl et al. (Nature Scientific Data 2018 - Kecocokan 90%):** Taksonomi medis dan bukti klinis bahwa 7 kelas mencakup >95% lesi kulit berpigmen dunia.
4. **Rahman et al. (Wiley CAAI Trans 2025 - Kecocokan 80%):** Analisis sebaran fitur komparatif dan penanganan ketimpangan kelas minoritas (`DF` & `VASC`).
5. **Rujukan Elsevier & IEEE Q1 Tambahan:**
   * *Gessert et al. (Elsevier Computers in Biology and Medicine 2020)* — Transisi 7 kelas HAM10k ke ISIC 2019.
   * *Nigar et al. (IEEE Access 2022)* — Evaluasi multiclass 8 kelas ISIC 2019 dan distribusi HAM10000.

### C. Rujukan Jalur Irisan 3 Kelas (HAM10k ∩ ISIC 2017 ∩ ISIC 2019 — PILIHAN AKTIF)
1. **Codella et al. (IEEE ISBI 2018 - Sitasi >1.200+):** Paper resmi kompetisi ISIC 2017 yang menetapkan benchmark 3 kelas standar dunia: Melanoma (`MEL`), Melanocytic Nevus (`NV`), dan Seborrheic Keratosis (`BKL`).
2. **Al-Masni et al. (Elsevier Medical Image Analysis 2018 - Scopus Q1 IF: 10.9):** Segmentasi dan klasifikasi simultan 3 kelas diagnosis lesi kulit menggunakan full resolution CNN.
3. **Bi et al. (IEEE Transactions on Medical Imaging 2020 - Scopus Q1 IF: 10.6):** Multi-stage ResNets untuk klasifikasi 3 kelas ISIC 2017.
4. **Matsunaga et al. (IEEE Challenge Proceedings 2017):** Pemenang Juara 1 Dunia ISIC 2017 Task 3 khusus klasifikasi 3 kelas (`MEL`, `NV`, `BKL`) dengan *balanced mini-batch ensembling*.
5. **Harangi (Elsevier BSPC 2018 - Scopus Q1) & Mahbod et al. (Elsevier CBM 2020 - Scopus Q1):** Pengujian ensemble deep learning pada 3 kelas lesi kulit dan transfer fitur lintas-dataset dari ISIC 2017 ke HAM10000.
6. **Ichim et al. (MDPI Cancers 2023 - Scopus Q1):** Protokol eliminasi duplikasi (*overlap removal*) citra lesi antar-arsip ISIC.

---

## 5. Struktur Folder & Manajemen Catatan Ilmiah (`notes jurnal/`)

Repositori ditata rapi ke dalam direktori tematik untuk memudahkan penulisan skripsi/paper:

```text
Data Understanding Isic & Ham10k/
├── Dataset/                                # Direktori data citra dan ground truth CSV
│   ├── dataset_binary_final.csv            # Dataset final jalur binary (33.552 citra bersih)
│   ├── dataset_clean_3dataset.csv          # Metadata 35.599 citra bersih (HAM10k, 2017, 2019)
│   ├── dataset_clean_final.csv             # Metadata 480.882 citra bersih (14 sumber)
│   ├── dataset_gabungan_ham10k_2017_2019.csv # Dataset gabungan bersih 3 dataset 9 kelas (35.599 baris)
│   ├── dataset_irisan_multiclass_final.csv # Master dataset irisan 3 kelas AKTIF (22.051 citra bersih)
│   ├── dataset_irisan_3kelas_train.csv     # Training set 80% (17.656 citra)
│   ├── dataset_irisan_3kelas_val.csv       # Validation set 10% (2.192 citra)
│   ├── dataset_irisan_3kelas_test.csv      # Test set 10% (2.203 citra)
│   ├── dataset_irisan_7kelas_final.csv     # Dataset final irisan 7 kelas alternatif (24.900 citra bersih)
│   ├── HAM10K/                             # Folder dataset HAM10000 & uji ISIC 2018
│   ├── isic 2016/ ... isic 2024/           # Arsip kompetisi ISIC tahunan

├── kode/                                   # Direktori seluruh kode & notebook terstruktur rapi
│   ├── 1_data_understanding/               # Eksplorasi awal dataset ISIC & HAM10000
│   │   ├── 1-data_understanding_isic.ipynb
│   │   ├── 1.1-data_understanding_isic copy.ipynb
│   │   ├── 1.1-data_understanding_isic.ipynb.bak
│   │   ├── 1.1-data_understanding_isic_exclude isic 20.ipynb
│   │   └── kaggle isic CLI  16-24-ham10k.ipynb
│   ├── 2_jalur_biner/                      # Jalur Biner (Benign 0 vs Malignant 1 - Global Union)
│   │   ├── binary_mapping.ipynb            # Versi original (29 sel)
│   │   ├── binary_mapping improve.ipynb    # Versi baru: ringkas, tanpa emoji, tabel asal duplikat, pre-rendered
│   │   ├── data understanding biner.ipynb  # Versi original (25 sel)
│   │   ├── data understanding biner improve.ipynb # Versi baru: 12 langkah fokus 3 dataset, tabel asal duplikat
│   │   └── gabungan_ham10k_2017_2019.ipynb # Analisis penggabungan 3 dataset 9 kelas

│   ├── 3_jalur_irisan_3kelas/              # Jalur Irisan 3 Kelas (NV, MEL, BKL - Sesuai Dosen)
│   │   ├── data_understanding_irisan_3kelas.ipynb # Data Understanding & audit 10 kolom 2019, HAM10k, 2017
│   │   ├── data_understanding_irisan_3kelas improve.ipynb # Versi baru: 12 langkah terstruktur, dinamis tanpa hardcode, 100% bebas emoji, pre-rendered
│   │   ├── irisan_mapping.ipynb            # Versi original: data preparation & lesion-aware split 80:10:10
│   │   ├── irisan_mapping improve.ipynb    # Versi baru: 11 langkah terstruktur, tanpa emoji, tabel deduplikasi informatif, split 80:10:10 bebas kebocoran, pre-rendered
│   │   ├── tabel_ekstraksi_jurnal_3kelas.md # Matriks komparasi jurnal & harmonisasi medis
│   │   ├── baseline_modeling_3kelas.ipynb  # Notebook baseline modeling PyTorch 3 kelas
│   │   ├── train_baseline.py               # Skrip eksekusi pelatihan modular (ResNet-50 & EfficientNet-B0)
│   │   ├── eksekusi_full_training_gpu.ipynb # Notebook siap jalan untuk Kaggle/Colab T4
│   │   └── panduan_eksekusi_gpu_colab_kaggle.md # Panduan komprehensif eksekusi cloud GPU
│   └── 4_jalur_irisan_7kelas/              # Jalur Irisan 7 Kelas (HAM10k ∩ ISIC 2019 - Alternatif)
│       └── irisan_7kelas_mapping.ipynb
├── notes jurnal/                           # Direktori catatan, analisis, & ringkasan jurnal
│   ├── biner/                              # Catatan riset jalur biner
│   │   ├── ringkasan jurnal biner saya.txt                # Catatan ringkasan paper rujukan biner
│   │   └── ringkasan_ekstraksi_lengkap_jurnal_biner.txt   # Ekstraksi teks mendalam seluruh paper biner
│   └── irisan/                             # Catatan riset jalur irisan
│       ├── ringkasan_jurnal_irisan_3kelas.md              # Analisis komprehensif 5 jurnal irisan 3 kelas (PILIHAN AKTIF)
│       └── ringkasan_jurnal_irisan_7kelas.md              # Analisis kecocokan 4 jurnal irisan 7 kelas
├── models/                                 # Direktori penyimpanan bobot model PyTorch (.pth)
├── jurnal/ & Jurnal biner/                 # Repositori file PDF jurnal ilmiah asli
├── plan.text                               # Diagram alur konsep arsitektur riset
├── AGENTS.md                               # Protokol sesi kerja otomatis AI (/start & /end)
├── .gitignore                              # Konfigurasi proteksi file citra mentah untuk GitHub
├── README.md                               # Dokumentasi repositori GitHub (riset-coyy)
└── CATATAN_MEMORI_PROYEK.md                # Dokumen memori utama (persistent memory)
```

---

### 5.1 Rincian Path Fisik Dataset 3 Sumber (HAM10000, ISIC 2017, ISIC 2019)

Semua path berada di bawah root direktori: `Dataset/` (`C:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\Dataset\`)

| Dataset & Partisi | Direktori Citra Fisik | File Ground Truth CSV | File Metadata Pasien CSV |
| :--- | :--- | :--- | :--- |
| **HAM10000** | `HAM10K/HAM10000_images_part_1`<br>`HAM10K/HAM10000_images_part_2` | `HAM10K/HAM10000_metadata` | `HAM10K/HAM10000_metadata`<br>*(kolom: lesion_id, dx_type, age, sex, localization)* |
| **ISIC 2019 Training** | `isic 2019/ISIC_2019_Training_Input/ISIC_2019_Training_Input/` | `isic 2019/ISIC_2019_Training_Input/ISIC_2019_Training_GroundTruth.csv` | `isic 2019/ISIC_2019_Training_Input/ISIC_2019_Training_Metadata.csv`<br>*(kolom: age_approx, sex, anatom_site_general, lesion_id)* |
| **ISIC 2019 Test** | `isic 2019/ISIC_2019_Test_Input/ISIC_2019_Test_Input/` | `isic 2019/ISIC_2019_Test_Input/ISIC_2019_Test_GroundTruth.csv` | *- (tidak dirilis panitia)* |
| **ISIC 2017 Training** | `isic 2017/ISIC-2017_Training_Data/ISIC-2017_Training_Data/` | `isic 2017/ISIC-2017_Training_Data/ISIC-2017_Training_Part3_GroundTruth.csv` | `isic 2017/ISIC-2017_Training_Data/ISIC-2017_Training_Data/ISIC-2017_Training_Data_metadata.csv`<br>*(kolom: age_approximate, sex)* |
| **ISIC 2017 Validation** | `isic 2017/ISIC-2017_Validation_Data/ISIC-2017_Validation_Data/` | `isic 2017/ISIC-2017_Validation_Data/ISIC-2017_Validation_Part3_GroundTruth.csv` | `isic 2017/ISIC-2017_Validation_Data/ISIC-2017_Validation_Data/ISIC-2017_Validation_Data_metadata.csv`<br>*(kolom: age_approximate, sex)* |
| **ISIC 2017 Test** | `isic 2017/ISIC-2017_Test_v2_Data/ISIC-2017_Test_v2_Data/` | `isic 2017/ISIC-2017_Test_v2_Data/ISIC-2017_Test_v2_Part3_GroundTruth.csv` | `isic 2017/ISIC-2017_Test_v2_Data/ISIC-2017_Test_v2_Data/ISIC-2017_Test_v2_Data_metadata.csv`<br>*(kolom: age_approximate, sex)* |


---

## 6. Checklist Tugas & Titik Lanjut Berikutnya (Actionable Next Steps)

Progres implementasi Jalur Irisan 3 Kelas (HAM10000 ∩ ISIC 2017 ∩ ISIC 2019):
- [x] **Langkah 1:** Bangun dan perbarui notebook [`kode/irisan_mapping.ipynb`](kode/irisan_mapping.ipynb) dengan 10 langkah modular.
- [x] **Langkah 2:** Muat 3 dataset: HAM10000 (10.015), ISIC 2019 Training (25.331), dan ISIC 2017 (2.750).
- [x] **Langkah 3:** Deduplikasi terarah (HAM10000 100% utuh, buang duplikat di ISIC 2019 dan 2017).
- [x] **Langkah 4:** Harmonisasi dan filter hanya pada **3 Kelas Multiclass Bersama** (`NV`, `MEL`, `BKL`).
- [x] **Langkah 5:** Validasi total baris bersih tepat **22.051 citra** (0 missing values).
- [x] **Langkah 6:** Render visualisasi grafik batang distribusi 3 kelas dan sebaran per sumber dataset.
- [x] **Langkah 7:** Ekspor file master awal ke [`Dataset/dataset_irisan_multiclass_final.csv`](Dataset/dataset_irisan_multiclass_final.csv).
- [x] **Langkah 8:** Konfirmasi validasi integrasi data dan status pipeline SELESAI 100%.
- [x] **Langkah 9 (Tugas 1 Selesai):** Pemisahan data Train / Validation / Test (80:10:10) dengan stratifikasi 3 kelas dan pencegahan kebocoran lesi (*Lesion-Aware Stratification* via `StratifiedGroupKFold`). Overlap antar-subset = **0 lesi (100% Bebas Kebocoran)**. Menghasilkan file split mandiri: `train.csv` (17.656 citra), `val.csv` (2.192 citra), dan `test.csv` (2.203 citra).
- [x] **Langkah 10 (Tugas 2 Selesai):** Analisis karakteristik resolusi citra fisik (HAM10000 600×450 px, ISIC 2019 ~1022×767 px, ISIC 2017 hingga 4288×2848 px), visualisasi distribusi split, dan perumusan rekomendasi pipeline preprocessing/augmentasi (224×224 px / 384×384 px, ImageNet norm, RandomFlip, Rotation, ColorJitter, Focal Loss).

- [x] **Tugas 3 (Selesai):** Membangun pipeline DataLoader (PyTorch) dan arsitektur eksperimen baseline deep learning multiclass transfer learning (ResNet-50 & EfficientNet-B0) pada dataset 3 kelas bebas kebocoran di [`kode/baseline_modeling_3kelas.ipynb`](kode/baseline_modeling_3kelas.ipynb). Lengkap dengan:
  - *Balanced Inverse Class Weights* untuk mitigasi ketimpangan kelas.
  - Pipeline augmentasi citra dermatologi medis (spatial rotation, flip, jitter, ImageNet norm).
  - Checkpointing otomatis berbasis *Validation Macro F1-Score*.
  - Evaluasi klinis menyeluruh pada Test Set (Accuracy, Balanced Acc, Sensitivity, Specificity, Precision, Macro ROC-AUC).
  - Visualisasi diagnostik *Normalized Confusion Matrix* & *Multi-Class ROC Curves (One-vs-Rest)*.

- [x] **Tugas 4 (Selesai):** Pembangunan mesin pelatihan modular [`kode/3_jalur_irisan_3kelas/train_baseline.py`](kode/3_jalur_irisan_3kelas/train_baseline.py) dan verifikasi *end-to-end smoke test* (EfficientNet-B0 & ResNet-50) berhasil 100%. Lengkap dengan loss berbobot (*Inverse Class Weights*), checkpointing otomatis (`best_val_f1`), evaluasi komprehensif test set, confusion matrix (`models/cm_*.png`), dan rekapitulasi metrik ke [`models/baseline_comparison_results.csv`](models/baseline_comparison_results.csv).
- [x] **Tugas 5 (Selesai):** Restrukturisasi folder `kode/` menjadi 4 subdirektori tematik modular (`1_data_understanding/`, `2_jalur_biner/`, `3_jalur_irisan_3kelas/`, `4_jalur_irisan_7kelas/`) dengan path resolution adaptif (`../../Dataset` dan `../../models`) serta sinkronisasi penuh ke GitHub.
- [x] **Tugas 6 (Selesai):** Perumusan dan pematangan strategi pencarian literatur paper ilmiah Jalur Irisan 3 Kelas (Harmonisasi Opsi C: Sumber Primer Label + Pendukung Multi-Dataset & Anti-Leakage).

- [x] **Langkah 1 (Selesai):** Menuliskan rangkuman dan tabel sitasi 5 paper ilmiah terpilih (Kelompok 1 Primer: Codella 2018, Tschandl 2018, Combalia 2019; Kelompok 2 Pendukung: Baig 2023, Ichim 2023) ke dalam file catatan [`notes jurnal/irisan/ringkasan_jurnal_irisan_3kelas.md`](notes%20jurnal/irisan/ringkasan_jurnal_irisan_3kelas.md) lengkap dengan ontologi medis `SK ≡ BKL`, diagram alur justifikasi Bab 2/3, tabel sebaran data, format APA 7th, dan BibTeX.
- [x] **Langkah 1.1 (Selesai):** Menyusun dan mengeksekusi penuh notebook [`kode/3_jalur_irisan_3kelas/data_understanding_irisan_3kelas.ipynb`](kode/3_jalur_irisan_3kelas/data_understanding_irisan_3kelas.ipynb) dengan gaya akademis manusiawi (*like human*), memeriksa mendalam 10 kolom asli ISIC 2019 (`image, MEL, NV, BCC, AK, BKL, DF, VASC, SCC, UNK`), 7 kelas HAM10000, 3 kelas 2017, audit tumpang tindih citra dan duplikasi lesi pasien, pembuktian medis peleburan `SK ≡ BKL`, serta visualisasi contoh dermatoskopi nyata.
- [x] **Langkah 3 (Selesai):** Eksplorasi & implementasi penanganan ketimpangan data lanjutan:
  - **Focal Loss ($\gamma=2.0$, alpha-weighted):** Diintegrasikan ke [`train_baseline.py`](kode/3_jalur_irisan_3kelas/train_baseline.py) dan [`baseline_modeling_3kelas.ipynb`](kode/3_jalur_irisan_3kelas/baseline_modeling_3kelas.ipynb) mengacu pada formulasi Lin et al. (ICCV 2017) dan notebook acuan dosen (`Eksperimen_Skenario1_Spark.ipynb`).
  - **Class-Balanced Focal Loss ($\beta=0.999$):** Mengadopsi prinsip *Effective Number of Samples* (Cui et al., CVPR 2019) untuk normalisasi bobot dinamis pada kelas minoritas (`MEL` & `BKL`).
  - **Verifikasi End-to-End Smoke Test:** Sukses dieksekusi untuk `efficientnet_b0_focal` dan `resnet50_cb_focal`, menghasilkan model checkpoint `.pth`, diagram confusion matrix, serta pembaruan otomatis ke [`models/baseline_comparison_results.csv`](models/baseline_comparison_results.csv).
  - **Panduan GPU Eksekusi:** Disediakan panduan siap eksekusi di [`kode/3_jalur_irisan_3kelas/panduan_eksekusi_gpu_colab_kaggle.md`](kode/3_jalur_irisan_3kelas/panduan_eksekusi_gpu_colab_kaggle.md).
- [ ] **Langkah 2:** Menjalankan pelatihan penuh (*Full Training* 10–20 epoch) ResNet-50 vs EfficientNet-B0 pada akselerator GPU (Google Colab / Kaggle T4) menggunakan skrip modular `python kode/3_jalur_irisan_3kelas/train_baseline.py --loss focal` / `--loss cb_focal` sesuai panduan GPU.

### 📋 Agenda Tugas Besok (Verifikasi Komparatif Biner vs Irisan & Laporan Dosen)
- [ ] **Tugas 1: Pengecekan Label Harmonisasi Biner vs Irisan vs Rujukan Jurnal**
  - Mengaudit konsistensi kode diagnosis (`NV`, `MEL`, `BKL`, `BCC`, `AKIEC`, `SCC`, `VASC`, `DF`, `UNK`) antara notebook jalur biner (`binary_mapping improve.ipynb`) dan jalur irisan (`data_understanding_irisan_3kelas improve.ipynb` & `irisan_mapping.ipynb`).
  - Memastikan definisi harmonisasi (seperti peleburan `seborrheic_keratosis ≡ BKL`) 100% selaras dengan standar literatur (*Tschandl et al., Nature 2018* dan *Codella et al., IEEE ISBI 2018*).
- [ ] **Tugas 2: Verifikasi Pemetaan Label Biner dengan Rujukan Konsensus Ilmiah**
  - Mengecek ulang pemetaan biner (Benign 0 vs Malignant 1) terhadap matriks voting 8 jurnal internasional.
  - Memvalidasi ketepatan klasifikasi kelas perbatasan (`AKIEC` sebagai ganas/pre-malignant, `VASC` sebagai jinak) dan eliminasi `UNK`.
- [ ] **Tugas 3: Audit dan Cross-Check Output Data Biner vs Irisan**
  - Melakukan validasi silang antara file output: `dataset_binary_final.csv` (33.552 baris) dengan `dataset_irisan_multiclass_final.csv` (22.051 baris).
  - Memastikan subset 3 kelas irisan konsisten dan tidak memiliki anomali/bentrok label terhadap master dataset biner.
- [ ] **Tugas 4: Pembuatan File Rekapitulasi untuk Dosen (File Excel `.xlsx` / Catatan Laporan Formal)**
  - Menyusun file Excel (`rekap_dataset_biner_dan_irisan.xlsx`) dan catatan ringkasan yang rapi, profesional, dan mudah dipahami dosen pembimbing.
  - Memuat lembar kerja komparasi: ringkasan kuantitas citra, matriks deduplikasi, perbandingan distribusi kelas biner vs irisan, serta daftar sitasi jurnal pendukung.

---

## 7. Catatan Penutupan Sesi Terakhir (Session Log via `/end`)
* **Waktu Penutupan:** 17 September 2026, Pukul 22:50 WIB.
* **Rangkuman Sesi Ini:**
  1. **Pembangunan 4 Notebook Versi Improve Baru (Standar CRISP-DM & Like Human):**
     * [`kode/2_jalur_biner/data understanding biner improve.ipynb`](kode/2_jalur_biner/data%20understanding%20biner%20improve.ipynb) — 12 langkah modular eksplorasi 3 dataset biner (HAM10k, 2019, 2017).
     * [`kode/2_jalur_biner/binary_mapping improve.ipynb`](kode/2_jalur_biner/binary_mapping%20improve.ipynb) — 14 langkah modular tanpa kebocoran target biner dini, didasarkan pada matriks konsensus voting 8 paper internasional.
     * [`kode/3_jalur_irisan_3kelas/data_understanding_irisan_3kelas improve.ipynb`](kode/3_jalur_irisan_3kelas/data_understanding_irisan_3kelas%20improve.ipynb) — 12 langkah modular komputasi irisan dinamis 22.051 citra bersih.
     * [`kode/3_jalur_irisan_3kelas/irisan_mapping improve.ipynb`](kode/3_jalur_irisan_3kelas/irisan_mapping%20improve.ipynb) — 11 langkah modular data preparation dan partisi anti-kebocoran lesi (*Lesion-Aware Split 80:10:10*), sel kosong lama dibersihkan.
  2. **Kualitas Teknis & Standar Akademis:**
     * **100% Bebas Emoji:** Seluruh teks markdown, komentar, grafik, dan log printout bersih tanpa emoji.
     * **Bahasa Ringkas & Ramah (Setara 17 Tahun):** Penjelasan sel 1–2 kalimat langsung ke inti, komunikatif, dan bernada alami (*like human*).
     * **Kode Bersih Tanpa Banner:** Menghilangkan sekat dekoratif berlebih (`# =====`).
     * **Tabel Deduplikasi Informatif:** Dilengkapi kolom **`Duplikat dengan Dataset Mana`**.
     * **Pre-rendered Outputs:** Seluruh output tabel HTML, log print, dan grafik base64 PNG telah terisi lengkap.
     * **File Asli Aman:** Seluruh 4 notebook versi asli tetap terjaga utuh untuk perbandingan.
  3. **Pencatatan 4 Agenda Tugas Sesi Berikutnya (Bagian 6):**
     * Tugas 1: Pengecekan label harmonisasi biner vs irisan vs rujukan jurnal.
     * Tugas 2: Verifikasi pemetaan label biner dengan rujukan konsensus ilmiah.
     * Tugas 3: Audit dan cross-check output data biner (33.552) vs irisan (22.051).
     * Tugas 4: Pembuatan file rekapitulasi untuk dosen (file Excel `.xlsx` / catatan laporan formal).
  4. **Sinkronisasi Git & GitHub:**
     * Seluruh perubahan telah di-commit dan di-push sukses ke repositori GitHub `https://github.com/Sigiitttt/riset-coyy.git` (commit `35b6709`). Working tree 100% clean.
* **Status Memori:** **AMAN, PERSISTEN, & TERSINKRONISASI.** Seluruh pekerjaan sesi ini tersimpan rapi. Sesi berikutnya siap dibuka kembali kapan saja dengan perintah **`/start`**.

