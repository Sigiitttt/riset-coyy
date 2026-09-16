# 📊 REKAPITULASI & TABEL EKSTRAKSI DATA JURNAL ILMIAH (3 KELAS)
**Lokasi File:** `kode/3_jalur_irisan_3kelas/tabel_ekstraksi_jurnal_3kelas.md`  
**Jalur Riset:** Jalur Irisan Multiclass 3 Kelas (*Melanocytic Nevus* / `NV`, *Melanoma* / `MEL`, *Benign Keratosis* / `BKL`)  
**Tujuan:** Mendokumentasikan ekstraksi data terstruktur langsung dari teks/paragraf jurnal ilmiah acuan untuk integrasi mudah ke dalam naskah Skripsi / Tugas Akhir (Bab 2, Bab 3, dan Bab 4).

---

## 📌 DAFTAR ISI EKSTRAKSI
1. [Paper 1: ISIC 2017 Challenge (Codella et al., 2018) — Task 3 Disease Classification](#-paper-1-isic-2017-challenge-codella-et-al-2018)
2. *(Ruang siap pakai untuk teks potongan paper berikutnya dari Anda)*

---

<a id="paper-1"></a>
## 📄 Paper 1: ISIC 2017 Challenge (Codella et al., 2018)

### 1. Informasi Bibliografi Paper
* **Judul:** *Skin Lesion Analysis Toward Melanoma Detection: A Challenge at the 2017 International Symposium on Biomedical Imaging (ISBI), Hosted by the International Skin Imaging Collaboration (ISIC)*
* **Penulis:** Noel C. F. Codella, David Gutman, M. Emre Celebi, Brian Helba, Michael A. Marchetti, Stephen W. Dusza, Aadi Kalloo, Konstantinos Liopyris, Nabin Mishra, Harald Kittler, dan Allan Halpern
* **Publikasi:** *IEEE 15th International Symposium on Biomedical Imaging (ISBI 2018)*, pp. 168–172
* **Penerbit:** IEEE
* **DOI:** `10.1109/ISBI.2018.8363547`
* **File PDF Lokal:** [SKIN LESION ANALYSIS TOWARD MELANOMADETECTIONACHALLENGEATTHE.pdf](file:///c:/Users/ARII/Downloads/Data%20Understanding%20Isic%20&%20Ham10k/jurnal/multi/SKIN%20LESION%20ANALYSIS%20TOWARD%20MELANOMADETECTIONACHALLENGEATTHE.pdf)

---

### 2. Teks Asli yang Ditempel (*Raw Source Snippet*)
> *"Part 3: Disease Classification Task: Participants were asked to classify images as belonging to one of 3 categories (Fig. 3), including “melanoma” (374 training, 30 validation, 117 test), “seborrheic keratosis” (254, 42, and 90), and “benign nevi” (1372, 78, 393), with classification scores normalized between 0.0 to 1.0 for each category (and 0.5 as binary decision threshold). Lesion classification data included the original image paired with the gold standard diagnosis, as well as approximate age (5 year intervals) and gender when available."*

---

### 3. Tabel Ekstraksi Distribusi Data Resmi ISIC 2017 (Task 3)

Berikut adalah hasil ekstraksi matematis dan kategorisasi dari teks di atas:

| No | Kategori Diagnosis Asli | Kode Harmonisasi Medis | Definisi Klinis Singkat | Training Set | Validation Set | Test Set | Total Citra | Proporsi Total |
| :-: | :--- | :-: | :--- | :-: | :-: | :-: | :-: | :-: |
| 1 | **Melanocytic Nevi** | `NV` | Tahi lalat jinak berpigmen | 1.372 | 78 | 393 | **1.843** | 67,02% |
| 2 | **Melanoma** | `MEL` | Kanker ganas melanositik | 374 | 30 | 117 | **521** | 18,95% |
| 3 | **Seborrheic Keratosis** | `BKL` | Keratosis jinak (*peniru melanoma*) | 254 | 42 | 90 | **386** | 14,04% |
| **—** | **TOTAL KESELURUHAN** | — | **Partisi Resmi ISIC 2017** | **2.000**<br>*(72,73%)* | **150**<br>*(5,45%)* | **600**<br>*(21,82%)* | **2.750** | **100,0%** |

---

### 4. Parameter & Protokol Teknis yang Disebutkan
Dari paragraf tersebut, terdapat rincian protokol evaluasi yang dapat diadopsi langsung:
* **Format Output Model:** Skor probabilitas prediksi dinormalisasi pada rentang rentang $[0.0, 1.0]$ untuk setiap kategori kelas.
* **Ambang Batas Keputusan (*Decision Threshold*):** Digunakan nilai default $0.5$ sebagai *binary decision threshold* evaluasi per kelas.
* **Metadata Tambahan:** Citra lesi asli dipasangkan dengan:
  * *Gold standard diagnosis* (konfirmasi patologi / histopatologi).
  * Perkiraan usia pasien dalam interval rentang 5 tahunan (*approximate age in 5-year intervals*).
  * Jenis kelamin pasien (*gender: male / female*).

---

### 5. Komparasi Langsung dengan Dataset Riset Kita

Tabel di bawah ini menjelaskan bagaimana angka 2.750 citra ISIC 2017 pada kutipan di atas berhubungan langsung dengan dataset 22.051 citra yang kita bangun:

| Kategori Diagnosis | ISIC 2017 Asli (Paper Codella) | Sampel ISIC 2017 yang Dipertahankan Setelah Deduplikasi | Sampel ISIC 2017 yang Dieliminasi (Duplikat HAM10k / ISIC19) | Total Gabungan Akhir Dataset Riset Kita (HAM10k + ISIC19 + ISIC17) | Lonjakan Data terhadap ISIC 2017 Asli |
| :--- | :-: | :-: | :-: | :-: | :-: |
| **Melanocytic Nevus (`NV`)** | 1.843 | 1.373 | 470 | **14.148** | **+667% (7,6x lipat)** |
| **Melanoma (`MEL`)** | 521 | 373 | 148 | **4.895** | **+839% (9,4x lipat)** 🚀 |
| **Benign Keratosis (`BKL`)** | 386 | 284 | 102 | **3.008** | **+679% (7,8x lipat)** |
| **TOTAL** | **2.750** | **2.030** | **720** | **22.051** | **+701% (8x lipat)** |

> [!NOTE]
> **Penjelasan Deduplikasi:** Dari 2.750 citra asli ISIC 2017, sebanyak 720 citra merupakan duplikat identik yang sudah ada di HAM10000 dan ISIC 2019. Sesuai protokol anti-kebocoran data (*anti-leakage*), 720 duplikat tersebut dibersihkan dan 2.030 citra unik ISIC 2017 diserap ke dalam total **22.051 citra bersih**.

---

### 6. Contoh Kalimat Siap Pakai untuk Naskah Skripsi

* **Untuk Bab 3 (Metodologi Penelitian — Subbab Sumber Data ISIC 2017):**
  > *"Koleksi data ISIC 2017 yang digunakan dalam penelitian ini mengacu pada Task 3 (Disease Classification) dari kompetisi ISIC-ISBI 2017 (Codella et al., 2018). Pada rilis aslinya, dataset ini terdiri dari 2.750 citra yang terbagi menjadi 2.000 citra latih, 150 citra validasi, dan 600 citra uji, yang mencakup diagnosis Melanocytic Nevi (1.843 citra), Melanoma (521 citra), dan Seborrheic Keratosis (386 citra). Dalam pipeline penelitian ini, label Seborrheic Keratosis diselaraskan ke dalam kategori Benign Keratosis (BKL), dan seluruh sampel dibersihkan dari duplikasi terhadap HAM10000 serta ISIC 2019 sebelum dilakukan partisi ulang secara lesion-aware."*

* **Untuk Bab 4 (Hasil dan Pembahasan — Subbab Evaluasi Skala Data):**
  > *"Jika dibandingkan dengan dataset benchmark ISIC 2017 Task 3 (Codella et al., 2018) yang hanya memiliki 521 sampel melanoma dan 386 seborrheic keratosis, dataset terharmonisasi yang dibangun pada penelitian ini berhasil melipatgandakan jumlah sampel melanoma menjadi 4.895 citra (+839%) dan benign keratosis menjadi 3.008 citra (+679%). Peningkatan drastis representasi kelas minoritas ini memberikan dasar representasi fitur visual yang jauh lebih kaya bagi model deep learning."*

---

*(Silakan tempel teks paper berikutnya di obrolan, AI akan otomatis mengekstrak dan menambahkannya ke dokumen ini)*
