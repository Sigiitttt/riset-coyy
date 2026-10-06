# Rencana Implementasi: Pembuatan Notebook Jalur Binary (`binary_mapping.ipynb`)

Sesuai instruksi dan analisis terhadap file dalam folder [`to biner`](file:///c:/Users/ARII/Downloads/Data%20Understanding%20Isic%20&%20Ham10k/to%20biner) serta bagan alur [p.text](file:///c:/Users/ARII/Downloads/Data%20Understanding%20Isic%20&%20Ham10k/p.text), notebook ini secara khusus akan memproses **3 Dataset Pilihan: HAM10000, ISIC 2017, dan ISIC 2019** dengan mekanisme deduplikasi terarah dan pemetaan biner berbasis konsensus voting paper rujukan.

---

## 1. Strategi Seleksi Dataset & Deduplikasi (HAM10000 Prioritas Utama)

Antara HAM10000, ISIC 2017, dan ISIC 2019 terdapat duplikasi citra yang signifikan (ISIC 2019 memuat sebagian besar data HAM10000, dan ISIC 2017 juga memiliki irisan).

Sesuai arahan:
1. **Pertahankan HAM10000 100% utuh** (10.015 citra sebagai basis prioritas tertinggi).
2. **ISIC 2019:** Buang 10.015 citra yang duplikat dengan HAM10000, sehingga hanya mengambil **15.316 citra unik baru**.
3. **ISIC 2017:** Buang citra yang duplikat dengan HAM10000 dan ISIC 2019, sehingga hanya mengambil **1.283 citra unik baru** (train).
4. Hasil seleksi menghasilkan **dataset gabungan yang 100% bersih dan bebas dari duplikasi**.

---

## 2. Hasil Analisis Suara Terbanyak (Voting) Paper per Folder

Saya telah membedah seluruh paper ilmiah yang berada di subfolder `to biner`:

### A. Folder `to biner/ham10k` (5 Paper)
* **Kousis et al. (MDPI Electronics 2022):** Benign (`nv`, `bkl`, `vasc`, `df`) | Malignant (`mel`, `bcc`, `akiec`)
* **IEEE Access (2020 - AlexNet):** Benign (`nv`, `bkl`, `df`) | Malignant (`mel`, `bcc`, `akiec`)
* **SkinNet-16 (2021):** Benign (`nv`, `bkl`, `vasc`, `df`) | Malignant (`mel`, `bcc`, `akiec`)
* **Harangi et al. (Elsevier BSPC 2020):** Benign (`bkl`, `df`, `nv`) | Malignant (`akiec`, `bcc`, `mel`, `vasc`)
* **Nigar et al. (IEEE Access 2022):** Studi XAI multi-class.
* 🏆 **Suara Terbanyak (Konsensus Bulat):**
  * **Benign:** `nv`, `bkl`, `df`, `vasc`
  * **Malignant:** `mel`, `bcc`, `akiec`

### B. Folder `to biner/isic 2017` (2 Paper)
* **EL Q1 (Explainable Taxonomies):** Melanoma -> Malignant | Nevus & Seborrheic Keratosis -> Benign
* **SP Q1 (ResNet152 Melanoma Diagnosis):** Melanoma -> Malignant | Nevus & Keratosis -> Benign
* 🏆 **Suara Terbanyak (100% Bulat):**
  * **Benign:** `nevus`, `seborrheic_keratosis`
  * **Malignant:** `melanoma`

### C. Folder `to biner/isic 2019` (3 Paper)
* **MDPI Bioengineering (Hierarchical Framework):** Benign (`NV`, `BKL`, `DF`, `VASC`) | Malignant (`MEL`, `BCC`, `AKIEC`, `SCC`)
* **MDPI Electronics (electronics-11-01294):** Benign (`NV`, `BKL`, `DF`, `VASC`) | Malignant (`MEL`, `BCC`, `AKIEC`, `SCC`)
* **Elsevier DAJ (2023 - Modified EfficientNet):** Benign (`NV`, `BKL`, `AK`, `UNK`) | Malignant (`MEL`, `BCC`, `SCC`)
* 🏆 **Suara Terbanyak (Mayoritas 2 vs 1):**
  * **Benign:** `NV`, `BKL`, `DF`, `VASC`
  * **Malignant:** `MEL`, `BCC`, `SCC`, `AKIEC / AK`
  * **UNK:** Ditandai terpisah (*out-of-distribution* / tanpa diagnosis definitif).

> [!TIP]
> **Harmonisasi Sempurna:** Ketiga folder secara konsisten menyepakati aturan yang sama persis:
> * **BENIGN (0):** `NV` / `nevus`, `BKL` / `seborrheic_keratosis`, `DF`, `VASC`.
> * **MALIGNANT (1):** `MEL` / `melanoma`, `BCC`, `SCC`, `AKIEC` / `AK`.

---

## 3. Struktur Notebook yang Akan Dibuat

Notebook baru: [`kode/binary_mapping.ipynb`](file:///c:/Users/ARII/Downloads/Data%20Understanding%20Isic%20&%20Ham10k/kode/binary_mapping.ipynb) disusun dalam **8 Langkah Singkat & Terarah (Like Human)**:

1. **Langkah 1 — Setup & Pemuatan 3 Dataset Pilihan:**
   - Memuat data fisik dan ground truth dari HAM10000, ISIC 2019, dan ISIC 2017.
2. **Langkah 2 — Deduplikasi Terarah (Pertahankan HAM10000):**
   - Mengeliminasi duplikat pada ISIC 2019 dan ISIC 2017 terhadap HAM10000.
   - Menampilkan tabel Before vs After eliminasi khusus 3 dataset ini.
3. **Langkah 3 — Inventarisasi Label Diagnosis Asli:**
   - Menampilkan tabel kelas asli yang tersisa dari data gabungan 3 dataset.
4. **Langkah 4 — Rangkuman Paper Rujukan & Tabel Hasil Voting:**
   - Menyajikan rekapitulasi 10 paper rujukan dari folder `to biner` beserta hasil suara terbanyak per kelas.
5. **Langkah 5 — Formulasi Aturan Pemetaan Biner Final:**
   - Menetapkan kamus mapping resmi (`BINARY_RULES`): Benign (0) vs Malignant (1).
6. **Langkah 6 — Eksekusi Pemetaan Biner & Validasi:**
   - Mentransformasi label asli ke kolom `binary_target`.
   - Validasi bahwa seluruh citra berlabel terpetakan 100% tanpa ada yang tertinggal.
7. **Langkah 7 — Analisis Sebaran Biner & Visualisasi Grafik Batang:**
   - Visualisasi bar chart sebelum (multiclass) vs sesudah (biner) dengan angka dan persentase yang jelas.
8. **Langkah 8 — DATA SIAP (Simpan Dataset Final):**
   - Menyimpan metadata final ke `Dataset/dataset_binary_ham10k_isic17_isic19.csv`.

---

## Verification Plan

### Automated Tests
- Validasi sintaks kode notebook menggunakan `compile(..., 'exec')`.
- Verifikasi bahwa total baris data bersih sesuai dengan kalkulasi (HAM10000 utuh 10.015, ISIC 2019 unik 15.316, ISIC 2017 unik 1.283).
- Verifikasi nilai kolom target hanya berisi `0` (Benign) dan `1` (Malignant).

### Manual Verification
- Meninjau visualisasi grafik batang agar angka dan persentase tampil jelas di atas batang.
- Memastikan bahasa penjelasan singkat, ringkas, dan manusiawi (*like human*).
