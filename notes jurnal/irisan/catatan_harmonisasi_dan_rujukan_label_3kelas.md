# 📋 CATATAN HARMONISASI LABEL MEDIS (JALUR IRISAN 3 KELAS)
**Dataset Riset:** HAM10000 ∩ ISIC 2017 ∩ ISIC 2019 (22.051 Citra Bersih)  
**Tujuan Dokumen:** Dokumentasi komprehensif landasan ilmiah, asal-usul kode label baku (`NV`, `MEL`, `BKL`), tabel komparasi sebelum-sesudah, serta rujukan resmi untuk integrasi naskah Skripsi (Bab 3) dan Notion.

---

## 🏛️ 1. Dari Mana Asal Kode Akhir "NV", "MEL", dan "BKL"? (Bukan Buat Sendiri)

Kode singkatan kapital **`NV`**, **`MEL`**, dan **`BKL`** adalah **standar resmi 100% yang ditetapkan oleh Konsorsium ISIC (*International Skin Imaging Collaboration*)** dan **Jurnal Ilmiah *Nature Scientific Data***:

1. **Standar File CSV Ground Truth Resmi ISIC 2019 Task 1:**
   * File sumber asli: `ISIC_2019_Training_GroundTruth.csv`
   * Baris header pertama (kolom diagnosis):
     ```csv
     image,MEL,NV,BCC,AK,BKL,DF,VASC,SCC,UNK
     ```
   * Konsorsium ISIC menetapkan singkatan resmi kapital 2–3 huruf: `NV` (Nevus), `MEL` (Melanoma), dan `BKL` (Benign Keratosis).

2. **Standar File CSV Ground Truth Resmi ISIC 2018 Task 3:**
   * File sumber asli: `ISIC2018_Task3_Training_GroundTruth.csv`
   * Baris header pertama (kolom diagnosis):
     ```csv
     image,MEL,NV,BCC,AKIEC,BKL,DF,VASC
     ```

3. **Standar Publikasi *Nature Scientific Data* (Tschandl et al., 2018):**
   * Di metadata HAM10000 (`HAM10000_metadata.csv`), kolom diagnosis menggunakan kode identik: `nv`, `mel`, `bkl`.
   * Pada teks paper **Halaman 7 (Sub-bab diagnosis)**, penulis mendefinisikan singkatan baku tersebut secara klinis.

---

## 📊 2. Tabel Komparasi: SEBELUM vs SESUDAH Harmonisasi

| Parameter | SEBELUM Harmonisasi | SESUDAH Harmonisasi | Manfaat & Justifikasi Medis |
| :--- | :--- | :--- | :--- |
| **Format & Gaya Penulisan Label** | **Heterogen & Terfragmentasi:**<br>• ISIC 2017: nama panjang huruf kecil (`nevus`, `melanoma`, `seborrheic_keratosis`)<br>• HAM10000: singkatan huruf kecil (`nv`, `mel`, `bkl`)<br>• ISIC 2019: kolom one-hot kapital (`NV`, `MEL`, `BKL`) | **Terstandardisasi 1 Format Konsisten:**<br>• Kode String: `NV`, `MEL`, `BKL`<br>• Target Encoding: `0`, `1`, `2` | Mencegah *label mismatch* atau galat *case-sensitivity* saat DataLoader PyTorch membaca multi-sumber dataset. |
| **Status Label Keratosis (`SK` vs `BKL`)** | **Terpisah & Tidak Seragam:**<br>• ISIC 2017 hanya melabeli `seborrheic keratosis`.<br>• HAM10000 & 2019 melabeli `bkl` / `BKL` (*Benign Keratosis*). | **Dilebur ke Kategori Payung `BKL`:**<br>Seluruh sampel `seborrheic keratosis` masuk ke kelas **`BKL` (2)**. | Sesuai bukti histopatologis di *Nature*: *seborrheic keratosis* secara biologis adalah varian utama dari proliferasi keratinosit jinak (`BKL`). |
| **Dimensi Jumlah Kelas** | **Beda Jumlah Antar-Dataset:**<br>• ISIC 2017: 3 kelas<br>• HAM10000: 7 kelas<br>• ISIC 2019: 8 kelas (+ UNK) | **Tepat 3 Kelas Multiclass Bersama:**<br>Hanya mengambil irisan 3 kelas diagnosis yang sama-sama dimiliki ketiga dataset. | Mengeksklusi kelas yang tidak ada di ISIC 2017 (seperti `DF`, `VASC`, `BCC`, `AKIEC`) agar evaluasi model adil dan terarah. |
| **Integritas Citra & Duplikasi** | **38.096 citra mentah:**<br>Mengandung 10.735 duplikat identik antar-arsip dan citra non-irisan. | **22.051 citra bersih:**<br>100% bebas duplikasi dan dipartisi bebas kebocoran lesi pasien (*0 lesion leakage*). | Menghilangkan bias evaluasi, kebocoran data (*data leakage*), dan *overfitting* palsu. |

---

## 🔬 3. Matriks Pemetaan Rinci per Kelas Diagnosis

| Kode Baku Final | Target Numerik | Nama Diagnosis Medis Lengkap | Sifat Patologis | Label di ISIC 2017 | Label di HAM10000 | Label di ISIC 2019 | Jumlah Citra Bersih | Persentase | Rujukan Utama |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`NV`** | `0` | **Melanocytic Nevus**<br>*(Tahi Lalat Jinak)* | Jinak (*Benign*) | `benign nevi` / `nevus` | `nv` | `NV` | 14.148 | 64,16% | Codella et al. (2018); Tschandl et al. (2018) |
| **`MEL`** | `1` | **Melanoma**<br>*(Kanker Kulit Ganas)* | **Ganas (*Malignant*)** | `melanoma` | `mel` | `MEL` | 4.895 | 22,20% | Codella et al. (2018); Tschandl et al. (2018) |
| **`BKL`** | `2` | **Benign Keratosis**<br>*(Keratosis Seboroik Jinak)* | Jinak (*Benign*) | `seborrheic keratosis` | `bkl` | `BKL` | 3.008 | 13,64% | Tschandl et al. (Nature 2018, hal. 7); Baig et al. (2023) |
| **TOTAL** | — | — | — | — | — | — | **22.051** | **100,0%** | Konsensus 3 Dataset |

---

## 📖 4. Daftar Rujukan Ilmiah Baku (Format Sitasi APA 7th Edition)

### 1. Rujukan Ontologi Medis & Peleburan `BKL` (Paper Primer HAM10000)
> **Tschandl, P., Rosendahl, C., & Kittler, H. (2018).** The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions. *Scientific Data*, 5(1), 180161. https://doi.org/10.1038/sdata.2018.161  
> * **Lokasi Bukti di PDF Lokal:** `jurnal irisan 3 kelas/ham10k.pdf` (Halaman 7, Kolom Kiri, Sub-bab `bkl`).
> * **Kutipan Verbatim:**  
>   *"bkl: 'Benign keratosis' is a generic class that includes seborrheic keratoses ('senile wart'), solar lentigo - which can be regarded a flat variant of seborrheic keratosis - and lichen-planus like keratoses (LPLK)... we grouped them together because they are similar biologically and often reported under the same generic term histopathologically."*

### 2. Rujukan Formulasi 3 Kelas Standar Dunia (Paper Primer ISIC 2017)
> **Codella, N. C. F., Gutman, D., Celebi, M. E., Helba, B., Marchetti, M. A., Dusza, S. W., ... & Halpern, A. (2018).** Skin lesion analysis toward melanoma detection: A challenge at the 2017 International Symposium on Biomedical Imaging (ISBI), hosted by the International Skin Imaging Collaboration (ISIC). *2018 IEEE 15th International Symposium on Biomedical Imaging (ISBI 2018)*, 168–172. https://doi.org/10.1109/ISBI.2018.8363547  
> * **Lokasi Bukti di PDF Lokal:** `jurnal irisan 3 kelas/isic 2017.pdf`.

### 3. Rujukan Harmonisasi Multi-Dataset HAM10000 + ISIC (Paper Pendukung)
> **Baig, A. R., Abbas, Q., Almakki, R., Ibrahim, M. E. A., AlSuwaidan, L., & Ahmed, A. E. S. (2023).** Light-Dermo: A lightweight pretrained convolution neural network for the diagnosis of multiclass skin lesions. *Diagnostics*, 13(3), 385. https://doi.org/10.3390/diagnostics13030385  
> * **Lokasi Bukti di PDF Lokal:** `jurnal/multi/Light-Dermo A Lightweight Pretrained Convolution Neural.pdf` (Halaman 10–11, Bagian 4.1 Data Acquisition & Tabel 2).  
> * **Bukti Integrasi:** Mendemonstrasikan penggabungan HAM10000 dan ISIC 2019 menggunakan ekuivalensi kode `BK` / `BKL` serta eliminasi duplikasi lesi.

### 4. Rujukan Protokol Eliminasi Duplikasi & Anti-Leakage (Paper Pendukung)
> **Ichim, L., Mitrica, R. I., Serghei, M. O., & Popescu, D. (2023).** Detection of malignant skin lesions based on decision fusion of ensembles of neural networks. *Cancers*, 15(20), 4946. https://doi.org/10.3390/cancers15204946  
> * **Lokasi Bukti di PDF Lokal:** `jurnal/multi/Detection of Malignant Skin Lesions Based on Decision Fusion.pdf` (Halaman 5–6, Bagian 3.1 Dataset Used).  
> * **Bukti Protokol:** Menetapkan aturan bahwa citra lesi ganda (*multiple images per lesion*) wajib dibersihkan antar-arsip repositori ISIC untuk mencegah bias evaluasi.

---

## 🎯 5. Cheat Sheet Tanya-Jawab Sidang Skripsi (Q&A Defense)

* **Q: "Mengapa Anda menggunakan singkatan NV, MEL, dan BKL?"**  
  * **A:** *"Singkatan tersebut bukan buatan saya pribadi, melainkan mengadopsi standar resmi tata nama Konsorsium ISIC pada kompetisi ISIC 2018 dan 2019, serta taksonomi medis internasional Tschandl et al. (2018) pada jurnal Nature Scientific Data."*

* **Q: "Apakah valid secara medis menggabungkan 'Seborrheic Keratosis' (ISIC 2017) ke dalam 'BKL'?"**  
  * **A:** *"Sangat valid, Pak/Bu. Dalam histopatologi dermatologi menurut Tschandl et al. (Nature 2018), Seborrheic Keratosis adalah varian lesi jinak utama dari keluarga besar Benign Keratosis (BKL). Konsorsium ISIC sejak 2018 secara resmi menyatukan Seborrheic Keratosis, Solar Lentigo, dan LPLK ke dalam satu kategori payung BKL."*

* **Q: "Mengapa tidak menggunakan seluruh 8 kelas di ISIC 2019 atau 7 kelas di HAM10000?"**  
  * **A:** *"Karena penelitian ini menggunakan irisan bersama (intersection) 3 dataset (ISIC 2017, HAM10000, ISIC 2019). Dataset ISIC 2017 hanya menyediakan 3 diagnosis. Mengambil 3 kelas bersama ini menghasilkan dataset dengan keragaman sumber citra tertinggi (multi-senter 4 negara) tanpa menyisakan label kosong (missing ground truth)."*
