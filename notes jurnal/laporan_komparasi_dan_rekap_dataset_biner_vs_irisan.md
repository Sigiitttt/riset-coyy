# 📑 LAPORAN RESMI AUDIT & REKAPITULASI KOMPARATIF DATASET
## Jalur Biner (Benign vs Malignant) vs Jalur Irisan 3 Kelas (Multiclass)
**Repositori Riset:** Data Understanding ISIC (2016–2024) & HAM10000  
**Tanggal Audit & Sinkronisasi:** 18 September 2026  
**File Rekapitulasi Excel:** [`rekap_dataset_biner_dan_irisan.xlsx`](file:///c:/Users/ARII/Downloads/Data%20Understanding%20Isic%20&%20Ham10k/rekap_dataset_biner_dan_irisan.xlsx)

---

## Executive Summary (Ringkasan Eksekutif)

Dokumen ini disusun sebagai laporan formal komprehensif untuk mendokumentasikan verifikasi silang (*cross-validation audit*), konsistensi kode harmonisasi medis, validitas ilmiah konsensus pemetaan biner, serta struktur partisi data anti-kebocoran lesi (*zero lesion leakage*) antara dua jalur riset utama dalam repositori ini:

1. **Jalur Biner (Global Union — 33.552 Citra Bersih):**
   * **Tujuan Klinis:** Skrining awal kanker kulit global (Jinak / *Benign* [0] vs Ganas / *Malignant* [1]).
   * **Dataset Sumber:** HAM10000 (10.015), ISIC 2019 (15.316 train + 6.191 test), dan ISIC 2017 (1.283 train + 599 test + 148 val).
   * **Proporsi Target:** Benign = 20.998 citra (62,58%) vs Malignant = 12.554 citra (37,42%).
   * **Konsensus Ilmiah:** Mengadopsi matriks voting 8 paper internasional bereputasi (Elsevier, MDPI, Springer, Frontiers).

2. **Jalur Irisan 3 Kelas (Intersection Multiclass — 22.051 Citra Bersih):**
   * **Tujuan Klinis:** Klasifikasi diagnosis dermatologi spesifik pada 3 entitas lesi kulit berpigmen paling dominan di dunia.
   * **Dataset Sumber:** HAM10000 (8.917), ISIC 2019 Training Data (11.104), dan ISIC 2017 (2.030).
   * **Distribusi Kelas:** `NV` = 14.148 citra (64,16%), `MEL` = 4.895 citra (22,20%), dan `BKL` = 3.008 citra (13,64%).
   * **Partisi Data Anti-Kebocoran (*Lesion-Aware Stratified Split 80:10:10*):**
     * Train: 17.656 citra (80,07%)
     * Validation: 2.192 citra (9,94%)
     * Test: 2.203 citra (9,99%)
     * **Audit Kebocoran Pasien/Lesi:** Overlap antar-subset = **0 lesi (100% Bebas Kebocoran Data)**.

3. **Hasil Verifikasi Silang (Cross-Check Audit):**
   * **100% Konsistensi ID Citra:** Seluruh 22.051 citra pada Jalur Irisan berada di dalam master dataset Jalur Biner (33.552 baris).
   * **0% Label Mismatch:** Tidak ditemukan kontradiksi label diagnosis antara kode harmonisasi biner dan irisan.
   * **Dekonsentrasi 11.501 Citra Non-Irisan:** Terbukti secara komputasional berasal dari kelas di luar irisan ISIC 2017 (BCC, AKIEC, SCC, VASC, DF) serta partisi ISIC 2019 Test.

---

## 1. Matriks Perbandingan Strategis: Biner vs Irisan 3 Kelas

| Dimensi Evaluasi | Jalur Biner (Global Union) | Jalur Irisan 3 Kelas (Intersection) | Justifikasi Medis & Akademis |
| :--- | :--- | :--- | :--- |
| **Kebutuhan Klinis** | Skrining triase cepat: membedakan lesi aman vs lesi berbahaya yang butuh rujukan biopsi segera. | Diagnosis diferensial definitif: membedakan jenis lesi berpigmen yang sering menyerupai melanoma. | Menjawab 2 skenario klinis komplementer di dunia nyata kedokteran. |
| **Format Target** | Biner (2 Kelas):<br>• `0`: Benign (Jinak)<br>• `1`: Malignant (Ganas) | Multiclass (3 Kelas):<br>• `0`: `NV` (Melanocytic Nevus)<br>• `1`: `MEL` (Melanoma)<br>• `2`: `BKL` (Benign Keratosis) | Biner menyatukan 8 penyakit ke 2 kategori besar; Irisan mengambil irisan diagnosis bersama 3 dataset. |
| **Total Citra Bersih** | **33.552 citra** (bebas duplikat & drop 2.047 UNK). | **22.051 citra** (100% bebas duplikat & 0 missing). | Irisan (22.051) merupakan subset konsisten 100% dari Biner (33.552). |
| **Dataset Sumber** | HAM10000 + ISIC 2019 (Train & Test) + ISIC 2017 (Train, Val, Test). | HAM10000 + ISIC 2019 (Train) + ISIC 2017 (Train, Val, Test). | ISIC 2019 Test dikecualikan pada irisan 3 kelas agar tidak merusak ground truth asli 3 senter. |
| **Deduplikasi Citra** | HAM10000 100% utuh (10.015); 10.735 duplikat di 2019 & 2017 dibersihkan. | HAM10000 100% utuh (8.917 NV/MEL/BKL); 10.735 duplikat dibersihkan. | Mencegah overfitting palsu dan bias evaluasi akibat citra kembar antar-arsip. |
| **Partisi Data** | Stratified Random Split / K-Fold. | Lesion-Aware Stratified Split (80:10:10) via `StratifiedGroupKFold`. | Menjamin tidak ada citra dari pasien atau lesi yang sama di Train dan Test. |
| **Ketimpangan Kelas** | Benign: 62,6% vs Malignant: 37,4% (Rasio ~1,67 : 1). | NV: 64,2% \| MEL: 22,2% \| BKL: 13,6%. | Ditangani dengan *Inverse Class Weights*, Focal Loss, atau Class-Balanced Loss. |
| **Paper Acuan Utama** | Konsensus Voting 8 Paper Internasional (Elsevier, MDPI, Springer, Frontiers). | Codella et al. (ISBI 2018), Tschandl et al. (Nature 2018), Baig (2023), Ichim (2023). | Memiliki landasan sitasi Scopus Q1 dan Nature Scientific Data. |

---

## 2. Harmonisasi Label Medis & Konsensus Ilmiah

### A. Standarisasi Kode Harmonisasi (8 Kelas Medis)

| Kode Baku | Nama Diagnosis Medis Lengkap | Label di HAM10000 | Label di ISIC 2019 | Label di ISIC 2017 | Sifat Medis | Pemetaan Biner |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **`NV`** | Melanocytic Nevus *(Tahi Lalat Jinak)* | `nv` | `NV` | `nevus` | Jinak | **Benign (0)** |
| **`MEL`** | Melanoma *(Kanker Ganas Melanosit)* | `mel` | `MEL` | `melanoma` | Ganas | **Malignant (1)** |
| **`BKL`** | Benign Keratosis *(Keratosis Seboroik)* | `bkl` | `BKL` | `seborrheic_keratosis` | Jinak | **Benign (0)** |
| **`BCC`** | Basal Cell Carcinoma *(Karsinoma Sel Basal)* | `bcc` | `BCC` | - | Ganas | **Malignant (1)** |
| **`AKIEC`** | Actinic Keratosis / Bowen's Disease | `akiec` | `AK` | - | Pre-kanker | **Malignant (1)** |
| **`SCC`** | Squamous Cell Carcinoma *(Sel Skuamosa)* | - | `SCC` | - | Ganas | **Malignant (1)** |
| **`VASC`** | Vascular Lesion *(Hemangioma / Angioma)* | `vasc` | `VASC` | - | Jinak | **Benign (0)** |
| **`DF`** | Dermatofibroma *(Nodul Histiositik)* | `df` | `DF` | - | Jinak | **Benign (0)** |

### B. Bukti Histopatologis Peleburan `seborrheic_keratosis` ke `BKL`
Peleburan label `seborrheic_keratosis` dari ISIC 2017 ke dalam kode payung `BKL` didasarkan pada standar resmi Konsorsium ISIC dan publikasi jurnal **Nature Scientific Data** (*Tschandl et al., 2018*, hal. 7):
> *"bkl: 'Benign keratosis' is a generic class that includes seborrheic keratoses ('senile wart'), solar lentigo - which can be regarded a flat variant of seborrheic keratosis - and lichen-planus like keratoses (LPLK)... we grouped them together because they are similar biologically and often reported under the same generic term histopathologically."*

### C. Matriks Konsensus Voting 8 Paper Internasional (Pemetaan Biner)

| Paper Rujukan | Penerbit & Tahun | Dataset | NV | BKL | DF | VASC | MEL | BCC | AKIEC | SCC |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Kousis et al.** | MDPI Electronics (2022) | HAM10000 | Jinak | Jinak | Jinak | Jinak | Ganas | Ganas | Ganas | - |
| **SkinNet-16 / Ghosh et al.** | Frontiers in Oncology (2022) | HAM10000 | Jinak | Jinak | Jinak | Jinak | Ganas | Ganas | Ganas | - |
| **Harangi et al.** | Elsevier BSPC (2020) | HAM10k / 2018 | Jinak | Jinak | Jinak | Ganas* | Ganas | Ganas | Ganas | - |
| **Ameri** | JBPE (2020) | HAM10000 | Jinak | Jinak | Jinak | Exclude | Ganas | Ganas | Ganas | - |
| **Barata et al.** | Elsevier Pattern Rec. (2020) | ISIC 2017 | Jinak | Jinak | - | - | Ganas | - | - | - |
| **Jojoa Acosta et al.** | Springer BMC Med. Img (2021) | ISIC 2017 | Jinak | Jinak | - | - | Ganas | - | - | - |
| **MorphoNet / Yao et al.** | MDPI Bioengineering (2026) | HAM10k & 2019 | Jinak | Jinak | Jinak | Jinak | Ganas | Ganas | Ganas | Ganas |
| **Venugopal et al.** | Elsevier DAJ (2023) | ISIC 2019 | Jinak | Jinak | Jinak | Jinak | Ganas | Ganas | Ganas | Ganas |
| **KONSENSUS AKHIR (VOTING)** | **Mayoritas Literatur** | **Semua Sumber** | **JINAK (100%)** | **JINAK (100%)** | **JINAK (100%)** | **JINAK (80%)** | **GANAS (100%)** | **GANAS (100%)** | **GANAS (100%)** | **GANAS (100%)** |

*Catatan VASC:* Harangi et al. mengelompokkan VASC ke kelas positif/abnormal karena fokus deteksi lesi vaskular. Namun, secara patologis medis dan 4 dari 5 literatur lainnya, VASC adalah lesi jinak vaskular (*benign angioma*). Konsensus 80% menetapkan VASC sebagai **Benign (0)**.

---

## 3. Rincian Statistik Dataset Jalur Biner (33.552 Citra)

### A. Tabel Deduplikasi Multi-Dataset Jalur Biner
* **Total Citra Mentah Dipindai:** 46.334 citra
* **Total Duplikat Dibuang:** 10.735 citra (HAM10000 dipertahankan 100% utuh)
* **Total Citra Bersih Pre-Filter:** 35.599 citra
* **Citra UNK Dieliminasi (OOD ISIC 2019 Test):** 2.047 citra
* **Citra Bersih Final Siap Latih:** **33.552 citra**

| Sumber Dataset | Partisi Data | Mentah | Duplikat Dibuang | Bersih Final | Kontribusi |
| :--- | :--- | :---: | :---: | :---: | :---: |
| HAM10000 | Part 1 & 2 | 10.015 | 0 | 10.015 | 29,85% |
| ISIC 2019 | Training Input | 25.331 | 10.015 | 15.316 | 45,65% |
| ISIC 2019 | Test Input | 8.238 | 2.047 (UNK) | 6.191 | 18,45% |
| ISIC 2017 | Training Data | 2.000 | 717 | 1.283 | 3,82% |
| ISIC 2017 | Test Data | 600 | 1 | 599 | 1,79% |
| ISIC 2017 | Validation Data | 150 | 2 | 148 | 0,44% |
| **TOTAL GABUNGAN** | **6 Partisi** | **46.334** | **12.782** | **33.552** | **100,00%** |

### B. Distribusi 8 Kelas Harmonisasi Medis
| Kode Kelas | Nama Diagnosis Medis | HAM10k | 2019 Train | 2019 Test | 2017 Train | 2017 Test | 2017 Val | Total Bersih | % Proporsi | Status Biner |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **NV** | Melanocytic Nevus | 6.705 | 6.170 | 2.495 | 804 | 393 | 76 | 16.643 | 49,60% | Benign (0) |
| **MEL** | Melanoma | 1.113 | 3.409 | 1.327 | 227 | 116 | 30 | 6.222 | 18,54% | Malignant (1) |
| **BCC** | Basal Cell Carcinoma | 514 | 2.809 | 975 | 0 | 0 | 0 | 4.298 | 12,81% | Malignant (1) |
| **BKL** | Benign Keratosis | 1.099 | 1.525 | 660 | 252 | 90 | 42 | 3.668 | 10,93% | Benign (0) |
| **AKIEC** | Actinic Keratosis | 327 | 737 | 374 | 0 | 0 | 0 | 1.438 | 4,29% | Malignant (1) |
| **SCC** | Squamous Cell Carcinoma | 0 | 431 | 165 | 0 | 0 | 0 | 596 | 1,78% | Malignant (1) |
| **VASC** | Vascular Lesion | 142 | 111 | 104 | 0 | 0 | 0 | 357 | 1,06% | Benign (0) |
| **DF** | Dermatofibroma | 115 | 124 | 91 | 0 | 0 | 0 | 330 | 0,98% | Benign (0) |
| **TOTAL** | **8 Diagnosis Medis** | **10.015** | **15.316** | **6.191** | **1.283** | **599** | **148** | **33.552** | **100,00%** | **Siap Latih** |

### C. Sebaran Target Biner Akhir
* **Benign (Jinak / Target 0):** **20.998 citra (62,58%)**
  * Terdiri dari: `NV` (16.643) + `BKL` (3.668) + `VASC` (357) + `DF` (330).
* **Malignant (Ganas / Target 1):** **12.554 citra (37,42%)**
  * Terdiri dari: `MEL` (6.222) + `BCC` (4.298) + `AKIEC` (1.438) + `SCC` (596).
* **Rasio Imbalance:** ~1,67 : 1 (Kategori ketimpangan moderat, sangat representatif dengan populasi klinis).

---

## 4. Rincian Statistik Dataset Jalur Irisan 3 Kelas (22.051 Citra)

### A. Sebaran per Sumber Dataset
| Sumber Dataset | Partisi Data | NV (Nevus) | MEL (Melanoma) | BKL (Keratosis) | Total 3 Kelas | % Kontribusi |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| HAM10000 | Part 1 & 2 (100% Utuh) | 6.705 | 1.113 | 1.099 | 8.917 | 40,44% |
| ISIC 2019 | Training (Non-HAM) | 6.170 | 3.409 | 1.525 | 11.104 | 50,36% |
| ISIC 2017 | Training Data | 804 | 227 | 252 | 1.283 | 5,82% |
| ISIC 2017 | Test Data | 393 | 116 | 90 | 599 | 2,72% |
| ISIC 2017 | Validation Data | 76 | 30 | 42 | 148 | 0,67% |
| **TOTAL IRISAN** | **3 Dataset Acuan** | **14.148** | **4.895** | **3.008** | **22.051** | **100,00%** |

### B. Karakteristik 3 Kelas Multiclass & Rekomendasi Bobot Loss
* **`NV` (Target 0):** 14.148 citra (64,16%) — *Bobot Inverse Class: 0.52*
* **`MEL` (Target 1):** 4.895 citra (22,20%) — *Bobot Inverse Class: 1.50*
* **`BKL` (Target 2):** 3.008 citra (13,64%) — *Bobot Inverse Class: 2.44*

### C. Partisi Bebas Kebocoran Lesi (*Lesion-Aware Stratified Split 80:10:10*)
Partisi dilakukan menggunakan algoritma `StratifiedGroupKFold` dengan pengelompokan berbasis `lesion_id` pasien untuk memastikan citra dari lesi/pasien yang sama tidak terbelah ke dalam Train dan Test:
* **Training Set (80,07%):** 17.656 citra (`NV`: 11.302, `MEL`: 3.902, `BKL`: 2.452)
* **Validation Set (9,94%):** 2.192 citra (`NV`: 1.455, `MEL`: 450, `BKL`: 287)
* **Test Set (9,99%):** 2.203 citra (`NV`: 1.391, `MEL`: 543, `BKL`: 269)
* **Audit Kebocoran Lesi Pasien:**
  * Train $\cap$ Validation: **0 lesi (0%)**
  * Train $\cap$ Test: **0 lesi (0%)**
  * Validation $\cap$ Test: **0 lesi (0%)**
  * **Garansi Ilmiah: 100% Bebas Kebocoran Data (Zero Data Leakage).**

---

## 5. Audit Validasi Silang (Cross-Check Biner vs Irisan)

### A. Tabel Validasi Silang Komputasional
Berdasarkan eksekusi skrip audit komputasional pada file CSV master:

| Parameter Pengujian | Hasil Audit Aktual | Target Standar | Status Integritas | Keterangan Evaluasi |
| :--- | :---: | :---: | :---: | :--- |
| **Kesesuaian ID Citra** | 22.051 / 22.051 (100%) | 100% Wajib Ada | **LOLOS (100%)** | Semua citra irisan tercakup dalam biner. |
| **Ketidakcocokan Label (Mismatch)** | 0 Kasus (0%) | 0 Kasus | **LOLOS (100%)** | Kode `NV`, `MEL`, `BKL` identik di kedua dataset. |
| **Ketidakcocokan Sumber Dataset** | 0 Kasus (0%) | 0 Kasus | **LOLOS (100%)** | Asal file sumber 100% konsisten. |
| **Integritas Path File Fisik Citra** | 1.000 / 1.000 sampel ada | 100% Valid | **LOLOS (100%)** | File citra JPG terverifikasi fisik di storage. |
| **Kebocoran Lesi Antar-Subset** | 0 Lesi Overlap | 0 Overlap | **LOLOS (100%)** | Generalisasi model klinis terlindungi. |
| **Missing Values (Nilai NaN)** | 0 Missing Values | 0 NaN | **LOLOS (100%)** | Metadata lengkap tanpa sel kosong. |

### B. Dekomposisi 11.501 Citra Biner Non-Irisan
Pertanyaan krusial dosen: *"Mengapa jumlah citra biner 33.552 sedangkan irisan hanya 22.051? Kemana 11.501 citra lainnya?"*

Jawabannya terurai secara matematis dan patologis dalam tabel berikut:
$$33.552 \text{ (Biner)} - 22.051 \text{ (Irisan)} = 11.501 \text{ Citra}$$

| Sumber Dataset | AKIEC | BCC | BKL | DF | MEL | NV | SCC | VASC | Total Non-Irisan | Alasan Mengapa Tidak Masuk Jalur Irisan 3 Kelas |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **HAM10000** | 327 | 514 | 0 | 115 | 0 | 0 | 0 | 142 | **1.098** | Diagnosis ini (`DF`, `VASC`, `BCC`, `AKIEC`) tidak disediakan di ISIC 2017. |
| **ISIC 2019 Train** | 737 | 2.809 | 0 | 124 | 0 | 0 | 431 | 111 | **4.212** | Diagnosis ini (`BCC`, `AKIEC`, `SCC`, `DF`, `VASC`) tidak disediakan di ISIC 2017. |
| **ISIC 2019 Test** | 374 | 975 | 660 | 91 | 1.327 | 2.495 | 165 | 104 | **6.191** | Partisi Test ISIC 2019 tidak dimasukkan ke irisan untuk menjaga protokol benchmark 3 senter primer. |
| **TOTAL** | **1.438** | **4.298** | **660** | **330** | **1.327** | **2.495** | **596** | **357** | **11.501** | **$11.501 + 22.051 = 33.552$ (Konsisten 100%)** |

---

## 6. Daftar Pustaka Utama (Format APA 7th Edition)

1. **Tschandl, P., Rosendahl, C., & Kittler, H. (2018).** The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions. *Scientific Data*, 5(1), 180161. https://doi.org/10.1038/sdata.2018.161 *(Landasan ontologi kode NV, MEL, BKL & justifikasi histopatologis BKL)*.
2. **Codella, N. C. F., Gutman, D., Celebi, M. E., et al. (2018).** Skin lesion analysis toward melanoma detection: A challenge at the 2017 International Symposium on Biomedical Imaging (ISBI). *2018 IEEE 15th ISBI*, 168–172. https://doi.org/10.1109/ISBI.2018.8363547 *(Landasan formulasi 3 kelas ISIC 2017)*.
3. **Baig, A. R., Abbas, Q., Almakki, R., et al. (2023).** Light-Dermo: A lightweight pretrained convolution neural network for the diagnosis of multiclass skin lesions. *Diagnostics*, 13(3), 385. https://doi.org/10.3390/diagnostics13030385 *(Rujukan harmonisasi multi-dataset HAM10000 & ISIC 2019)*.
4. **Ichim, L., Mitrica, R. I., Serghei, M. O., & Popescu, D. (2023).** Detection of malignant skin lesions based on decision fusion of ensembles of neural networks. *Cancers*, 15(20), 4946. https://doi.org/10.3390/cancers15204946 *(Rujukan protokol pembersihan duplikasi lesi antar-arsip ISIC)*.
5. **Barata, C., Celebi, M. E., & Marques, J. S. (2020).** Explainable skin lesion diagnosis using taxonomies. *Pattern Recognition*, 110, 107413. https://doi.org/10.1016/j.patcog.2020.107413 *(Konsensus biner ISIC 2017)*.
6. **Jojoa Acosta, M. F., Caballero Tovar, L. Y., et al. (2021).** Melanoma diagnosis using deep learning techniques on dermatoscopic images. *BMC Medical Imaging*, 21, Art. 6. https://doi.org/10.1186/s12880-020-00534-8 *(Rujukan pemetaan biner ISIC 2017)*.
7. **Kousis, I., Perikos, I., Hatzilygeroudis, I., & Virvou, M. (2022).** Deep Learning Methods for Accurate Skin Cancer Recognition and Mobile Application. *Electronics*, 11(9), 1294. https://doi.org/10.3390/electronics11091294 *(Konsensus biner HAM10000)*.
8. **Ghosh, P., Azam, S., Quadir, R., Karim, A., et al. (2022).** SkinNet-16: A deep learning approach to identify benign and malignant skin lesions. *Frontiers in Oncology*, 12, 931141. https://doi.org/10.3389/fonc.2022.931141 *(Konsensus biner HAM10000)*.
9. **Harangi, B., Baran, A., & Hajdu, A. (2020).** Assisted deep learning framework for multi-class skin lesion classification considering a binary classification support. *Biomedical Signal Processing and Control*, 62, 102041. https://doi.org/10.1016/j.bspc.2020.102041 *(Konsensus biner ISIC 2018/HAM10k)*.
10. **Yao, B., Jin, A., Liu, H., & Li, Q. (2026).** MorphoNet: An Interpretable Hierarchical Deep Learning Framework for Multi-Class Skin Lesion Classification Using Dermoscopic Morphology. *Bioengineering*, 13(9), 989. https://doi.org/10.3390/bioengineering13090989 *(Konsensus biner 8 kelas ISIC 2019)*.
