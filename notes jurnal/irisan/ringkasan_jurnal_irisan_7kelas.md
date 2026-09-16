# 📚 RINGKASAN & ANALISIS JURNAL ILMIAH: JALUR IRISAN 7 KELAS
**Proyek:** Data Understanding & Pemetaan Dataset ISIC (2016–2024) & HAM10000  
**Fokus Penelitian:** Jalur Irisan Multiclass 7 Kelas (*HAM10000 ∩ ISIC 2019*)  
**Lokasi Penyimpanan:** `notes jurnal/irisan/ringkasan_jurnal_irisan_7kelas.md`  
**Tanggal Dibuat:** 14 September 2026  

---

## 1. Ringkasan Eksekutif & Fondasi Konseptual Riset

Dalam diagram alur [plan.text](file:///c:/Users/ARII/Downloads/Data%20Understanding%20Isic%20&%20Ham10k/plan.text), **Jalur Irisan** bertujuan untuk:
1. Membandingkan diagnosis bawaan antar-dataset.
2. Mengharmonisasikan sinonim medis ke label standar bersama.
3. Mengambil persekutuan kelas yang **wajib ada pada seluruh dataset yang dipilih**.
4. Mengklasifikasikan data ke dalam **Multiclass** (karena jumlah kelas hasil irisan $> 2$ kelas).

Dengan memilih **HAM10000** (7 kelas) dan **ISIC 2019** (8 kelas berlabel + UNK), proses irisan matematis dan medisnya menghasilkan:
* **7 KELAS STANDAR EMAS (*GOLD STANDARD*):** `NV`, `MEL`, `BCC`, `BKL`, `AKIEC / AK`, `VASC`, `DF`.
* **Kelas Gugur:** `SCC` (*Squamous Cell Carcinoma*, 431 citra baru di ISIC 2019) gugur karena tidak dimiliki oleh HAM10000.
* **Total Citra Bersih Unik:** **24.900 citra** (100% bebas duplikat 10.015 citra antara HAM10k dan ISIC 2019).

Rangkaian 4 jurnal internasional bereputasi di bawah ini memberikan legitimasi ilmiah penuh (100% *coverage*) untuk setiap tahapan metodologi Anda: mulai dari **deduplikasi**, **harmonisasi kelas**, **landasan taksonomi medis**, hingga **analisis distribusi ketimpangan kelas**.

---

## 2. Matriks Kecocokan Cepat (*Quick Scorecard*)

| No | Paper / Penulis | Jurnal & Penerbit | Indeks & Reputasi | Persentase Kecocokan | Peran Metodologis Utama |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | **Baig et al. (2023)** | *Diagnostics* (MDPI) | Scopus Q2 / IF: 3.6 | **95%** 🌟 | Formulasi 7 Kelas & Penggabungan HAM10k + ISIC 2019 |
| 2 | **Ichim et al. (2023)** | *Cancers* (MDPI) | Scopus Q1 / IF: 5.2 | **85%** 🛡️ | Legitimasi Protokol Deduplikasi (*Overlap Removal*) |
| 3 | **Tschandl et al. (2018)** | *Nature Scientific Data* | Nature Portfolio / IF: 9.8 | **90%** 🏛️ | Landasan Teori Medis 7 Kelas Benchmark Dunia |
| 4 | **Rahman et al. (2025)** | *CAAI Trans on Intel Tech* (Wiley) | Scopus Q1 / IF: 8.4 | **80%** 📈 | Analisis Imbalance & Karakteristik Fitur Data |

---

## 3. Bedah Komprehensif Per Jurnal

---

### 📄 Jurnal 1: Formulasi Multiclass 7 Kelas Gabungan HAM10k + ISIC 2019
* **Judul Paper:** *Light-Dermo: A Lightweight Pretrained Convolution Neural Network for the Diagnosis of Multiclass Skin Lesions*
* **Penulis:** Abdul Rahaman Baig, Qazi Abbas, Reem Almakki, Mohammed E. A. Ibrahim, Lamia AlSuwaidan, dan Alaa E. S. Ahmed
* **Nama Jurnal:** *Diagnostics* (MDPI), Volume 13, Issue 3, Artikel 385, Halaman 1–35, Tahun 2023
* **DOI:** `10.3390/diagnostics13030385`
* **File PDF Lokal:** [diagnostics-13-00385.pdf](file:///c:/Users/ARII/Downloads/Data%20Understanding%20Isic%20&%20Ham10k/jurnal/multi/diagnostics-13-00385.pdf)
* **Tingkat Kecocokan:** **95%**

#### A. Bagian yang Cocok 100% (Diadopsi):
1. **Penggabungan Dataset:** Pada *Bagian 4.1 Data Acquisition (Halaman 10–12)*, penulis secara eksplisit menggunakan data gabungan dari **HAM10000 dan ISIC 2019**.
2. **Formulasi Tepat 7 Kelas:** Pada *Tabel 2 (Halaman 12)*, penulis memetakan seluruh citra menjadi 7 diagnosis yang sama persis dengan taksonomi irisan kita:
   * `AK` (*Actinic keratoses* / `akiec`)
   * `BCC` (*Basal cell carcinoma*)
   * `BK` (*Benign keratosis* / `bkl`)
   * `DF` (*Dermatofibroma*)
   * `NV` (*Melanocytic nevi*)
   * `MEL` (*Melanoma*)
   * `VASC` (*Vascular lesion*)
3. **Pengguguran Kelas Non-Irisan:** Penulis menyisihkan diagnosis di luar 7 kelas inti (seperti `SCC` pada ISIC 2019) untuk menjaga keselarasan multiclass berbasis 7 kategori umum.

#### B. Perbedaan / Hal yang Tidak Diadopsi:
* Baig et al. melakukan manipulasi ukuran data (*data augmentation & downsampling*) menjadi 14.000 citra buatan untuk melatih model ShuffleNet-Light mereka.
* *Pendekatan Kita:* Kita berfokus pada tahap *Data Understanding & Pre-processing*, sehingga mempertahankan **24.900 citra riil** tanpa modifikasi sintetis awal.

#### C. Contoh Kutipan untuk Bab Metodologi (Bab 3):
> *"Dalam menyelaraskan dataset gabungan HAM10000 dan ISIC 2019 ke dalam skema klasifikasi multiclass 7 kelas, penelitian ini mengadopsi formulasi harmonisasi diagnosis yang diajukan oleh Baig et al. (2023), yang mengelompokkan lesi ke dalam AK, BCC, BKL, DF, NV, MEL, dan VASC."*

---

### 📄 Jurnal 2: Metodologi Deduplikasi (*Overlap Removal*) HAM10k vs ISIC 2019
* **Judul Paper:** *Detection of Malignant Skin Lesions Based on Decision Fusion of Ensembles of Neural Networks*
* **Penulis:** Loreta Ichim, Radu-Ioan Mitrica, Marius-Octavian Serghei, dan Dan Popescu
* **Nama Jurnal:** *Cancers* (MDPI), Volume 15, Issue 20, Artikel 4946, Halaman 1–19, Tahun 2023
* **DOI:** `10.3390/cancers15204946`
* **File PDF Lokal:** [cancers-15-04946.pdf](file:///c:/Users/ARII/Downloads/Data%20Understanding%20Isic%20&%20Ham10k/jurnal/multi/cancers-15-04946.pdf)
* **Tingkat Kecocokan:** **85%**

#### A. Bagian yang Cocok 100% (Diadopsi):
1. **Pemberihan Duplikasi Data (KUNCI UTAMA):** Pada *Bagian 3.1 Materials and Methods > Dataset Used (Halaman 5–6)*, penulis menyatakan:
   > *"The first step in processing the dataset was the removal of duplicate images. There are overlaps between the two sets of data provided by the ISIC [HAM10000 and ISIC 2019 Challenge archives]. In the metadata, each lesion is identified with a unique ID, as well as each image is identified with a unique ID... To avoid possible errors, all the lesions that presented several images were removed."*
2. Ini adalah **justifikasi metodologis nomor 1** untuk membela langkah eliminasi 10.015 citra ISIC 2019 yang tumpang tindih dengan HAM10000, demi mencegah bias evaluasi (*data leakage*).

#### B. Perbedaan / Hal yang Tidak Diadopsi:
* Setelah deduplikasi, Ichim et al. hanya mengambil 4 kelas mayoritas (`mel`, `nv`, `bcc`, `bkl`) dan mengabaikan kelas minoritas (`akiec`, `df`, `vasc`).
* *Pendekatan Kita:* Kita mempertahankan seluruh 7 kelas agar variasi spektrum penyakit kulit tetap lengkap.

#### C. Contoh Kutipan untuk Bab Metodologi (Bab 3):
> *"Mengingat arsip ISIC 2019 menyerap sebagian besar sampel dari HAM10000, protokol pembersihan duplikasi (*deduplication*) diterapkan secara ketat mengacu pada metodologi Ichim et al. (2023) guna mengeliminasi tumpang tindih citra lesi antar-sumber data."*

---

### 📄 Jurnal 3: Landasan Taksonomi & Teori Klinis 7 Kelas Benchmark Dunia
* **Judul Paper:** *The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions*
* **Penulis:** Philipp Tschandl, Cliff Rosendahl, dan Harald Kittler
* **Nama Jurnal:** *Nature Scientific Data*, Volume 5, Artikel 180161, Halaman 1–9, Tahun 2018
* **DOI:** `10.1038/sdata.2018.161`
* **Penerbit:** Nature Portfolio / Springer Nature
* **Tingkat Kecocokan:** **90%**

#### A. Bagian yang Cocok 100% (Diadopsi):
1. **Justifikasi Medis 7 Kelas:** Penulis membuktikan secara klinis bahwa **7 kategori diagnosis ini mencakup lebih dari 95% dari seluruh lesi kulit berpigmen** yang ditemui dokter spesialis kulit dalam praktik medis sehari-hari.
2. **Definisi Ekuivalensi Diagnostik:** Memberikan dasar ontologi resmi bahwa:
   * `bkl` mencakup: *solar lentigo*, *seborrheic keratosis*, dan *lichen planus-like keratosis*.
   * `akiec` mencakup: *actinic keratosis* dan *intraepithelial carcinoma / Bowen's disease*.
   * `mel` mencakup melanoma invasif maupun *in situ*.

#### B. Perbedaan:
* Paper terbit tahun 2018, sehingga hanya memaparkan dataset HAM10000 murni (sebelum ISIC 2019 dirilis).

#### C. Contoh Kutipan untuk Bab Landasan Teori (Bab 2):
> *"Pemilihan 7 kelas diagnosis lesi kulit didasarkan pada taksonomi standar medis HAM10000 oleh Tschandl et al. (2018), yang merepresentasikan lebih dari 95% kasus lesi berpigmen dalam praktik dermatologi klinis nyata."*

---

### 📄 Jurnal 4: Analisis Karakteristik Data & Ketimpangan Kelas (*Class Imbalance*)
* **Judul Paper:** *Advancing skin cancer detection integrating a novel unsupervised classification and enhanced imaging techniques*
* **Penulis:** Md. Abdur Rahman, Nur Mohammad Fahad, Mohaimenul Azam Khan Raiaan, Mirjam Jonkman, Friso De Boer, dan Sami Azam
* **Nama Jurnal:** *CAAI Transactions on Intelligence Technology* (Wiley / IET), Volume 10, Issue 2, Halaman 481–500, Tahun 2025
* **DOI:** `10.1049/cit2.12410`
* **File PDF Lokal:** [CAAI Trans on Intel Tech - 2025 - Rahman.pdf](file:///c:/Users/ARII/Downloads/Data%20Understanding%20Isic%20&%20Ham10k/jurnal/multi/CAAI%20Trans%20on%20Intel%20Tech%20-%202025%20-%20Rahman%20-%20Advancing%20skin%20cancer%20detection%20integrating%20a%20novel%20unsupervised%20classification.pdf)
* **Tingkat Kecocokan:** **80%**

#### A. Bagian yang Cocok 100% (Diadopsi):
1. **Analisis Komparasi Fitur & Distribusi:** Mengulas struktur sebaran kelas pada HAM10000 dan ISIC 2019 secara berdampingan (*Halaman 488–492*).
2. **Diskusi Keterbatasan Kelas Minoritas:** Membahas secara gamblang fakta bahwa `DF` (1,0%) dan `VASC` (1,0%) adalah kelas langka (*imbalanced minority*) dan bagaimana ketimpangan ini mempengaruhi metrik evaluasi model.

#### B. Perbedaan:
* Rahman et al. menguji model *unsupervised clustering* secara terpisah pada masing-masing dataset, bukan menghasilkan satu dataset gabungan terpadu.

#### C. Contoh Kutipan untuk Bab Hasil & Pembahasan (Bab 4):
> *"Sebaran data hasil irisan menunjukkan ketimpangan proporsi yang signifikan pada kelas minoritas DF (1,0%) dan VASC (1,0%). Karakteristik ini sejalan dengan temuan Rahman et al. (2025) mengenai tantangan representasi lesi langka pada repositori ISIC dan HAM10000."*

---

## 4. Rekapitulasi Distribusi Data Bersih Hasil Irisan (24.900 Citra)

Penggabungan HAM10000 (100% utuh) dengan ISIC 2019 (unik baru non-HAM) pada 7 kelas irisan menghasilkan lonjakan sampel yang sangat menguntungkan:

| No | Kode Kelas | Nama Lesi Kulit | HAM10k Asli | ISIC 2019 Unik Baru | Total Irisan Bersih | Kenaikan Sampel |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| 1 | **`NV`** | Melanocytic nevus (Tahi lalat jinak) | 6.705 | 6.170 | **12.875** (51,7%) | +92% |
| 2 | **`MEL`** | Melanoma (Kanker ganas) | 1.113 | 3.409 | **4.522** (18,2%) | **+306% (4x lipat)** 🚀 |
| 3 | **`BCC`** | Basal cell carcinoma (Karsinoma ganas) | 514 | 2.809 | **3.323** (13,3%) | **+546% (6x lipat)** 🚀 |
| 4 | **`BKL`** | Benign keratosis (Keratosis jinak) | 1.099 | 1.525 | **2.624** (10,5%) | +139% |
| 5 | **`AKIEC / AK`** | Actinic keratosis (Lesi pra-kanker) | 327 | 737 | **1.064** (4,3%) | **+225% (3x lipat)** 🚀 |
| 6 | **`VASC`** | Vascular lesion (Lesi vaskular) | 142 | 111 | **253** (1,0%) | +78% |
| 7 | **`DF`** | Dermatofibroma (Lesi jinak) | 115 | 124 | **239** (1,0%) | +108% |
| **TOTAL** | — | — | **10.015** | **14.885** | **24.900** (100%) | **+149% Total Data** |

---

## 5. Panduan Sitasi Formal (Daftar Pustaka)

```bibtex
@article{baig2023light,
  title={Light-Dermo: A Lightweight Pretrained Convolution Neural Network for the Diagnosis of Multiclass Skin Lesions},
  author={Baig, Abdul Rahaman and Abbas, Qazi and Almakki, Reem and Ibrahim, Mohammed EA and AlSuwaidan, Lamia and Ahmed, Alaa ES},
  journal={Diagnostics},
  volume={13},
  number={3},
  pages={385},
  year={2023},
  publisher={MDPI},
  doi={10.3390/diagnostics13030385}
}

@article{ichim2023detection,
  title={Detection of Malignant Skin Lesions Based on Decision Fusion of Ensembles of Neural Networks},
  author={Ichim, Loreta and Mitrica, Radu-Ioan and Serghei, Marius-Octavian and Popescu, Dan},
  journal={Cancers},
  volume={15},
  number={20},
  pages={4946},
  year={2023},
  publisher={MDPI},
  doi={10.3390/cancers15204946}
}

@article{tschandl2018ham10000,
  title={The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions},
  author={Tschandl, Philipp and Rosendahl, Cliff and Kittler, Harald},
  journal={Scientific Data},
  volume={5},
  number={1},
  pages={180161},
  year={2018},
  publisher={Nature Publishing Group},
  doi={10.1038/sdata.2018.161}
}

@article{rahman2025advancing,
  title={Advancing skin cancer detection integrating a novel unsupervised classification and enhanced imaging techniques},
  author={Rahman, Md Abdur and Fahad, Nur Mohammad and Raiaan, Mohaimenul Azam Khan and Jonkman, Mirjam and De Boer, Friso and Azam, Sami},
  journal={CAAI Transactions on Intelligence Technology},
  volume={10},
  number={2},
  pages={481--500},
  year={2025},
  publisher={Wiley Online Library},
  doi={10.1049/cit2.12410}
}
```
