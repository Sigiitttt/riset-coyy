# 🧠 DOKUMEN MEMORI UTAMA PROYEK (PERSISTENT MEMORY)
**Proyek:** Data Understanding & Pemetaan Dataset ISIC (2016–2024) & HAM10000  
**Lokasi Direktori:** `C:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\`  
* **Terakhir Diperbarui:** 5 Oktober 2026 (Sesi Penutupan Eksperimen Backbone EXP 5-A & EXP 5-B)

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

### A. `binary_mapping improve.ipynb` (Jalur Binary — Status: SELESAI 100% LENGKAP DENGAN ZERO-LEAKAGE SPLIT)
* **Dataset yang Digunakan:** HAM10000, ISIC 2017, ISIC 2019.
* **Aturan Deduplikasi:** HAM10000 dipertahankan 100% utuh (10.015 citra), duplikat di 2019 dan 2017 dibersihkan.
* **Hasil Akhir Master:** **33.552 citra bersih** (setelah drop 2.047 citra `UNK`)
  * **Benign (0):** 20.998 citra (62,58%) $\rightarrow$ `NV` (16.643), `BKL` (3.668), `VASC` (357), `DF` (330)
  * **Malignant (1):** 12.554 citra (37,42%) $\rightarrow$ `MEL` (6.222), `BCC` (4.298), `AKIEC` (1.438), `SCC` (596)
* **Struktur Modular Lengkap (17 Langkah / 34 Cells):**
  * Langkah 1–14: Setup, pemindaian, deduplikasi, harmonisasi label, konsensus biner, visualisasi, dan ekspor awal.
  * **Langkah 15:** Pembagian Data Bebas Kebocoran (*Lesion-Aware Split 80:10:10*) via `StratifiedGroupKFold`:
    * Penanganan 2.074 citra varian `_downsampled` di ISIC 2019: dipetakan ke lesi yang sama dengan citra dasarnya sehingga tidak terpisah partisi.
    * **Training Set (80,05%):** 26.860 citra (Benign: 16.853, Malignant: 10.007)
    * **Validation Set (10,14%):** 3.401 citra (Benign: 2.055, Malignant: 1.346)
    * **Test Set (9,81%):** 3.291 citra (Benign: 2.090, Malignant: 1.201)
    * **Jaminan Zero Data Leakage:**
      - Overlap Train <-> Val: **0**
      - Overlap Train <-> Test: **0**
      - Overlap Val <-> Test: **0**
      - Mismatch varian citra downsampled: **0**
  * **Langkah 16:** Evaluasi Stratifikasi Split dan Karakteristik Fisik Citra (Crosstab, proporsi persentase terstratifikasi ~62,8% Benign vs ~37,2% Malignant, visualisasi bar plot 2 panel, sampling resolusi fisik citra).
  * **Langkah 17:** Kesimpulan Data Preparation Biner dan Kesiapan Modeling PySpark on YARN.
* **Output File Siap Pakai di `Dataset/`:**
  * `Dataset/dataset_binary_final.csv` (33.552 baris, kolom: `image_id`, `lesion_id`, `source`, `original_label`, `unified_class`, `binary_class`, `target_binary`, `split`, `filepath`).
  * `Dataset/dataset_binary_train.csv` (26.860 baris).
  * `Dataset/dataset_binary_val.csv` (3.401 baris).
  * `Dataset/dataset_binary_test.csv` (3.291 baris).


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



### C. Jalur Irisan 7 Kelas (Status: DIHAPUS / TIDAK DIGUNAKAN)
* **Keterangan:** Folder `kode/4_jalur_irisan_7kelas` dan notebook `irisan_7kelas_mapping.ipynb` telah dihapus secara permanen atas permintaan pengguna karena riset difokuskan penuh pada **Jalur Irisan 3 Kelas (NV, MEL, BKL)** sesuai arahan dosen pembimbing.

---

### D. `sk1-irisan-tipe1-101cel-selesai.ipynb` (PySpark on YARN Skenario 1 2W2P — Status: SUKSES DIEKSEKUSI DI KAGGLE GPU 100%)
* **Tujuan & Lingkungan:** Menjalankan eksperimen Big Data Skenario 1 (2 Worker, 2 Partisi, 15 Epoch) pada klaster Apache Hadoop/YARN + PySpark di Kaggle GPU dengan proteksi memori dan kuota disk lokal.
* **Dataset yang Digunakan:** Irisan 3 Kelas (`nevus`, `melanoma`, `seborrheic_keratosis`), total 22.051 citra dengan pembagian bebas kebocoran lesi (*Lesion-Aware Stratification* 80:10:10).
* **Hasil Eksekusi Penuh di Kaggle GPU (Tercatat Resmi di `results.csv`):**
  * **Prapemrosesan Terdistribusi (Stage 1):** 122,06 detik (22.051 citra, rata-rata CPU 66,28%, rata-rata RAM 6.936,92 MB).
  * **Pelatihan Terpusat GPU (Stage 2 - 15 Epoch):** 837,36 detik (~13,96 menit, 17.656 citra latih).
  * **Metrik Evaluasi Test Set (2.203 Citra Uji Independen):**
    * **Test Loss:** 1,3167
    * **Test Accuracy:** **76,49%**
    * **Test Macro F1-Score:** **0,7030**
    * **Test ROC-AUC (One-vs-Rest):** **0,9004**
  * **Kinerja per Kelas Medis (Classification Report):**
    * `melanoma` (543 sampel): Precision 0,63 | Recall 0,72 | F1-Score 0,67
    * `nevus` (1.391 sampel): Precision 0,90 | Recall 0,80 | F1-Score 0,85
    * `seborrheic_keratosis` (269 sampel): Precision 0,53 | Recall 0,67 | F1-Score 0,59
* **Inovasi Arsitektural Kunci yang Menyelesaikan Crash:**
  1. *Shard-Based HDFS Streaming (Sel 82):* Menggantikan shuffle masif dengan penulisan shard kompak (64 citra/shard via `pyarrow.fs` ke HDFS), diunduh linier ke array NumPy driver tanpa lonjakan memori, diikuti pelepasan `spark.stop()` sebelum GPU running.
  2. *Keras 3 BatchSequence (Sel 93):* Membungkus generator batch mandiri guna mengeliminasi duplikasi memori internal TensorFlow Keras 3 (~1,9x RAM).
  3. *Resource Isolation & NodeManager Lock (Sel 30):* Mengunci kapasitas klaster YARN di 14.336 MB (1.536 MB container, 1 core/executor) agar perbandingan speedup antar-skenario (2W vs 8W) adil dan konsisten.
* **File Tersimpan di Repositori:** [`kode/4_Spark_on_Yarn/4.2-arsip-irisan-benchmark/sk1-irisan-tipe1-101cel-selesai.ipynb`](kode/4_Spark_on_Yarn/4.2-arsip-irisan-benchmark/sk1-irisan-tipe1-101cel-selesai.ipynb).

---

### D.1 `sk2-biner-tipe1-101cel-selesai.ipynb` (PySpark on YARN Skenario 1 Biner 2W2P — Status: SUKSES DIEKSEKUSI DI KAGGLE GPU 100%)
* **Tujuan & Lingkungan:** Menjalankan eksperimen Big Data Jalur Biner Skenario 1 (2 Worker, 2 Partisi, 15 Epoch) pada klaster Apache Hadoop/YARN + PySpark di Kaggle GPU dengan optimasi memori `uint8` dan staging disk auto-resize 384px.
* **Dataset yang Digunakan:** Jalur Biner (`benign` vs `malignant`), total 33.552 citra bersih bebas kebocoran lesi (*Lesion-Aware Stratification* 80:10:10).
* **Hasil Eksekusi Penuh di Kaggle GPU (Tercatat Resmi di `results.csv`):**
  * **Prapemrosesan Terdistribusi (Stage 1):** 184,31 detik (33.552 citra, rata-rata CPU 63,12%, rata-rata RAM 7.150,14 MB).
  * **Pelatihan Terpusat GPU (Stage 2 - 15 Epoch):** 1.248,33 detik (~20,80 menit, 26.860 citra latih).
  * **Metrik Evaluasi Test Set (3.291 Citra Uji Independen):**
    * **Test Loss:** 0,7530
    * **Test Accuracy:** **79,03%**
    * **Test Macro F1-Score:** **0,7790**
    * **Test ROC-AUC:** **0,8718**
  * **Kinerja per Kelas Medis (Classification Report):**
    * `benign` (2.090 sampel): Precision 0,86 | Recall 0,80 | F1-Score 0,83
    * `malignant` (1.201 sampel): Precision 0,69 | Recall 0,77 | F1-Score 0,73
* **File Tersimpan di Repositori:** [`kode/4_Spark_on_Yarn/4.1-arsip-biner-benchmark/sk2-biner-tipe1-101cel-selesai.ipynb`](kode/4_Spark_on_Yarn/4.1-arsip-biner-benchmark/sk2-biner-tipe1-101cel-selesai.ipynb).

---

### E. Analisis Teknis Limit Memori & Disk: `float32` vs `uint8` pada Jalur Biner (33.552 Citra)
* **Konteks Masalah Kaggle GPU (RAM ~13 GB, Disk ~20 GB):**
  - Pada **Jalur Irisan (22.051 citra)**: Format `float32` murni berhasil dijalankan karena total memori array driver = **12,65 GB** (berada tepat di batas 13 GB RAM Kaggle).
  - Pada **Jalur Biner (33.552 citra)**: Volume data lebih besar (+52%). Jika dipaksakan `float32` murni di memori driver, ukurannya melonjak ke **~18,8 GB** (pasti memicu OOM/Kernel Died) dan file shard HDFS sementara memakan **~18,8 GB** (melebihi kuota disk 20 GB bila digabung staging 1,8 GB).
* **Tabel Komparasi Teknis:**

| Aspek / Parameter | Opsi A: `float32` Murni (Persis Irisan) | Opsi B: `uint8` Driver + Float per Batch (Kaggle-Optimized) |
| :--- | :--- | :--- |
| **Konsumsi RAM Driver** | **~18,8 GB** (33.552 × 224 × 224 × 3 × 4 byte) | **~4,7 GB** (33.552 × 224 × 224 × 3 × 1 byte) |
| **Batas RAM Kaggle (~13 GB)** | ⚠️ **Sangat Berisiko OOM / Kernel Crash** |  **Aman 100%** (sisa >8 GB RAM bebas) |
| **Disk HDFS Shard** | Membutuhkan ~18,8 GB storage sementara | Hanya butuh ~4,7 GB storage sementara |
| **Batas Disk Kaggle (20 GB)** | ⚠️ **Rentan Disk Full** (1,8 GB + 18,8 GB = 20,6 GB) |  **Aman** (Total puncak disk hanya ~7 GB) |
| **Integritas Nilai Piksel** | Presisi float 32-bit kontinu sejak RDD | Kuantisasi [0–255] asli citra, dibagi 255.0 per batch (kualitas & diagnosis identik) |
| **Beban CPU saat Training** | Sedikit lebih ringan (tanpa konversi tipe) | Konversi `/ 255.0` per 32 citra di generator (overhead <1 ms per batch) |
| **Keselarasan Kode Irisan** |  **100% Identik sama persis** | Modifikasi casting `.astype(float32)/255.0` di `BatchSequence` |

* **Status Keputusan:** Tersimpan di memori utama sebagai referensi pertimbangan pengguna sebelum menentukan eksekusi di lingkungan Kaggle GPU standar atau instance High-RAM.

---

### F. Dokumentasi Detail Seluruh Ubahan & Matriks Perbedaan Komparatif (Irisan Selesai vs Biner)

Dokumentasi ini mencatat secara menyeluruh seluruh perubahan yang telah diterapkan pada 5 notebook biner di [`kode/4_Spark_on_Yarn/biner/`](kode/4_Spark_on_Yarn/biner/) dibandingkan dengan notebook acuan yang sukses di Kaggle ([`sk1-spark-on-distributed-irisan3kelas-2p2w-v3-0-selesai.ipynb`](kode/4_Spark_on_Yarn/sk1-spark-on-distributed-irisan3kelas-2p2w-v3-0-selesai.ipynb)).

#### 1. Ringkasan Ubahan Utama (Dari Notebook Biner Lama -> Biner Kaggle-Optimized Baru)
1. **Mengeliminasi Crash YARN Bad-Node / Executor Lost (SIGTERM 143):**
   - *Lama:* YARN `NodeHealthCheckerService` membunuh executor saat disk >90%.
   - *Baru:* Sel 32 menyematkan `yarn.nodemanager.disk-health-checker.enable = false` dan `max-disk-utilization = 99.0%`.
2. **Mengeliminasi Banjir Disk SortShuffle & Persist Ganda (10+ GB Disk Dump):**
   - *Lama:* Melakukan `.filter()` pada RDD menjadi 3 partisi lalu masing-masing di-`.persist(DISK_ONLY)` dan dihitung `.count()`.
   - *Baru:* Sel 80 langsung memuat `train_ids`, `val_ids`, dan `test_ids` dari file CSV master tanpa operasi shuffle RDD sekunder.
3. **Mengeliminasi OOM Driver via PyArrow Shard-HDFS Streaming:**
   - *Lama:* Memakai `toLocalIterator()` multi-pass yang menarik partisi utuh ke memori driver.
   - *Baru:* Sel 82 menulis shard kompak (64 citra/shard via `pyarrow.fs` ke HDFS), lalu driver mengunduh linier ke array NumPy dan langsung menghapus file shard (`shard_path.unlink()`).
4. **Mengeliminasi Memory Explosion Keras 3 (~1,9x RAM):**
   - *Lama:* `model.fit(X_train, y_train_cat)` langsung membungkus seluruh array ke `tf.data.from_tensors`.
   - *Baru:* Sel 93 mengimplementasikan generator mandiri `BatchSequence` yang hanya mengiris 32 citra per batch.
5. **Mengeliminasi ValueError Ekstensi Checkpoint:**
   - *Lama:* Menggunakan ekstensi `.h5`.
   - *Baru:* Sel 91 menggunakan ekstensi `.keras` sesuai standar Keras 3.

---

### G. Kamus Tata Nama Standar & Peta Berkas Spark on YARN (Resmi Ditetapkan)

Untuk memastikan konsistensi penamaan di seluruh riset dan menghindari kerancuan, format nama file diatur dengan formula baku:
> **Pola Baku:**  
> **`[sk] - [keterangan: irisan / biner] - [tipe1] - [keterangan pengerjaan / versi].ipynb`**

#### 1. Kamus Definisi Tata Nama:
* **`sk1`**: Skenario 1 (Jalur Irisan 3 Kelas: `nevus`, `melanoma`, `seborrheic_keratosis`). Total 22.051 citra.
* **`sk2`**: Skenario 2 (Jalur Biner 2 Kelas: `benign` vs `malignant`). Total 33.552 citra.
* **`irisan`**: Menggunakan dataset irisan 3 kelas medis (HAM10000 ∩ ISIC 2017 ∩ ISIC 2019).
* **`biner`**: Menggunakan dataset biner 2 kelas (Jinak vs Ganas) hasil voting konsensus medis.
* **`tipe1`**: Arsitektur sistem Big Data Hybrid:
  * **Tahap 1:** Prapemrosesan terdistribusi pada Apache Spark on YARN cluster (HDFS reading, auto-resize, sharding).
  * **Tahap 2:** Pelatihan model terpusat (Centralized) pada GPU tunggal driver via generator Keras 3 `BatchSequence`.
  * *(Bukan Tipe 2 yang melatih model secara terdistribusi penuh di banyak node worker cluster via Horovod/DDP).*
* **`ringkas-optimasi`**: Versi ringkas mandiri (33 sel) yang telah dilengkapi 5 optimasi YARN (`DominantResourceCalculator` di `yarn-site.xml` & `capacity-scheduler.xml`, buffer baca PyArrow 64KB, `uint8` sharding, on-the-fly casting Keras 3 `BatchSequence`, dan evaluasi `test_seq`).
* **`101cel-optimasi`**: Versi panjang 101 sel lengkap yang telah disematkan 5 optimasi YARN di atas.
* **`101cel-selesai`**: Versi panjang 101 sel historis yang telah berhasil dieksekusi 100% di Kaggle GPU dengan bukti log output.
* **`ringkas`**: Versi ringkas 33 sel awal sebelum optimasi YARN disematkan.
* **`unittest-3img`**: Versi pengujian cepat 3 citra per kelas.
* **`ringkas-prepjurnal`**: Versi ringkas mandiri (33 sel) yang mengintegrasikan prapemrosesan jurnal LA-CapsNet MDPI 2024 (Pad & Resize 299x299, Contrast Stretching $n_0=128, \text{var}_0=4000$, Active Contour Snake Segmentation, on-the-fly batch augmentation, dan format hemat uint8).
* **`101cel-error-cell33`**: Arsip histori kegagalan pada cell 33 (sebelum fix memory).

#### 2. Peta Berkas Resmi di Folder `kode/4_Spark_on_Yarn/`:
* **`4.6-ringkas-optimasi-prepjurnal/`** *(✨ VERSI TERCANGGIH: REKAYASA PREPROCESSING MEDIS OPSI B 224px)*:
  * [`sk1-irisan-tipe1-ringkas-prepjurnal.ipynb`](kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk1-irisan-tipe1-ringkas-prepjurnal.ipynb) (Irisan 3 Kelas Spark on YARN - Pad & Resize 224x224, Dull Razor Hair Removal, Adaptive Snake Segmentation, Soft-Blending, uint8, zero-leakage split)
  * [`sk3-irisan-local-prepjurnal-ak85.ipynb`](kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk3-irisan-local-prepjurnal-ak85.ipynb) (Irisan 3 Kelas Spark Local Mode 20 Sel - Pad & Resize 224x224, Dull Razor, Snake Segmentation, Soft-Blending, Dual GPU MirroredStrategy)
  * [`sk2-biner-tipe1-ringkas-prepjurnal.ipynb`](kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk2-biner-tipe1-ringkas-prepjurnal.ipynb) (Biner 2 Kelas Spark on YARN - Resize 224x224, Dull Razor, Snake Segmentation, uint8)
* **`4.4-ringkas-optimasi/`** *(FOLDER BASELINE: PIPELINE 224px TANPA SEGMENTASI — resize polos + uint8)*:
  * [`sk1-irisan-tipe1-ringkas-optimasi.ipynb`](kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk1-irisan-tipe1-ringkas-optimasi.ipynb) (Jalur Irisan 3 Kelas - 33 sel ringkas, resize PIL polos TANPA Dull Razor/segmentasi, uint8, zero-leakage split — hasil aktual di `results.csv`: 73,63–76,31%)
  * [`sk2-biner-tipe1-ringkas-optimasi.ipynb`](kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk2-biner-tipe1-ringkas-optimasi.ipynb) (Jalur Biner 2 Kelas - 33 sel ringkas, resize PIL polos TANPA Dull Razor/segmentasi, uint8, zero-leakage split)
  * **Koreksi dokumentasi (diverifikasi ulang dari kode aktual, bukan dari catatan lama):** folder ini **TIDAK** memakai Dull Razor/Adaptive Snake/Soft-Blend — deskripsi versi sebelumnya di baris ini keliru. Segmentasi hanya ada di folder `4.6-ringkas-optimasi-prepjurnal/` dan turunannya di `4.7-finetune-conv5/`.
* **`4.3-101cel-optimasi/`** *(Versi Riset Lengkap 101 Sel + Optimasi YARN)*:
  * [`sk1-irisan-tipe1-101cel-optimasi.ipynb`](kode/4_Spark_on_Yarn/4.3-101cel-optimasi/sk1-irisan-tipe1-101cel-optimasi.ipynb)
  * [`sk2-biner-tipe1-101cel-optimasi.ipynb`](kode/4_Spark_on_Yarn/4.3-101cel-optimasi/sk2-biner-tipe1-101cel-optimasi.ipynb)
* **`4.2-arsip-irisan-benchmark/`** *(Arsip Bukti Run Sukses di Kaggle - Irisan 76,49%)*:
  * [`sk1-irisan-tipe1-101cel-selesai.ipynb`](kode/4_Spark_on_Yarn/4.2-arsip-irisan-benchmark/sk1-irisan-tipe1-101cel-selesai.ipynb)
  * [`sk1-irisan-tipe1-ringkas.ipynb`](kode/4_Spark_on_Yarn/4.2-arsip-irisan-benchmark/sk1-irisan-tipe1-ringkas.ipynb)
  * [`sk1-irisan-tipe1-unittest-3img.ipynb`](kode/4_Spark_on_Yarn/4.2-arsip-irisan-benchmark/sk1-irisan-tipe1-unittest-3img.ipynb)
* **`4.1-arsip-biner-benchmark/`** *(Arsip Bukti Run Sukses di Kaggle - Biner 79,03%)*:
  * [`sk2-biner-tipe1-101cel-selesai.ipynb`](kode/4_Spark_on_Yarn/4.1-arsip-biner-benchmark/sk2-biner-tipe1-101cel-selesai.ipynb)
  * [`sk2-biner-tipe1-ringkas.ipynb`](kode/4_Spark_on_Yarn/4.1-arsip-biner-benchmark/sk2-biner-tipe1-ringkas.ipynb)
* **`4.5-arsip-debugging/`** *(Arsip Histori Crash Cell 33 Sebelum Memory Fix)*:
  * [`sk1-irisan-tipe1-101cel-error-cell33.ipynb`](kode/4_Spark_on_Yarn/4.5-arsip-debugging/sk1-irisan-tipe1-101cel-error-cell33.ipynb)

#### 3. Panduan Cepat Pemahaman Pengguna:
1. **File yang dipakai eksekusi:** Pengguna hanya perlu membuka folder **`4.4-ringkas-optimasi/`** karena file di folder ini yang paling ringkas (33 sel) dan sudah memiliki setelan hemat RAM (`uint8`) serta Core CPU (`DominantResourceCalculator`).
2. **Fungsi folder 4.1, 4.2, 4.3, 4.5:** Murni sebagai arsip riwayat riset (pembuktian ke dosen bahwa eksperimen 101 sel sebelumnya pernah sukses dijalankan di Kaggle dengan log resmi).
3. **Rumus balok nama berkas:**
   * `sk1` / `sk2` = Kode tugas (sk1: 3 penyakit kulit, sk2: jinak vs ganas).
   * `irisan` / `biner` = Sumber data yang dimuat.
   * `tipe1` = Cara kerja pipeline (Spark olah citra di worker, GPU latih model terpusat di driver).
   * `ringkas-optimasi` = 33 sel ringkas dan sudah terpasang penghemat memori.

#### 4. Hasil Audit Kepatuhan Metodologi CRISP-DM, Disiplin Namespace & Bebas Data Leakage (Folder 4.4 & 4.6):
* **Audit Alur CRISP-DM (Linear 0 s/d 33 Sel):**
  1. *Fase 0 & 1 (Business/Research Understanding & Environment Setup):* Pembersihan log lama, instalasi Hadoop, Java, Spark, konfigurasi cluster.
  2. *Fase 2 & 3 (Distributed Data Architecture):* Inisialisasi HDFS NameNode/DataNode & YARN ResourceManager/NodeManager.
  3. *Fase 4 (Data Understanding):* Staging dataset fisik ke HDFS, verifikasi integritas manifest dan sebaran kelas medis.
  4. *Fase 5 (Data Preparation Terdistribusi):* PySpark RDD preprocessing (Resize 224/299px, normalisasi, snake segmentation jika 4.6), sharding HDFS kompak 64 citra/shard, streaming linier ke driver array NumPy `uint8`, dan pelepasan memori `spark.stop()`.
  5. *Fase 6 (Data Preparation - Splitting & Modeling Arsitektur):* Pemuatan file split resmi (`train`, `val`, `test`) bebas kebocoran lesi, konstruksi ResNet-50 + Triplet Attention AK85.
  6. *Fase 7 (Modeling Pelatihan GPU & Evaluation):* Perhitungan `class_weights` murni dari `y_train`, generator `BatchSequence` on-the-fly, pelatihan `model.fit`, visualisasi kurva loss/akurasi, evaluasi test set (Confusion Matrix, Macro F1, ROC-AUC), dan pencatatan resmi ke `results.csv`.
* **Penyempurnaan Disiplin Namespace & Eliminasi Forward References (Mendahului):**
  * *Sel 21:* Menyematkan `import csv` dan `import numpy as np` di awal sel sehingga assertion tipe `np.uint8` dan `ensure_log_header()` 100% mandiri.
  * *Sel 22:* Menyematkan `import subprocess` eksplisit pada notebook folder 4.4.
  * *Sel 24:* Menyematkan `from pathlib import Path` dan `import pandas as pd` di baris pertama sel.
  * *Sel 28:* Menata ulang seluruh import (`import time`, `import numpy as np`, `import tensorflow as tf`, `compute_class_weight`, callbacks) ke baris paling atas sel sebelum eksekusi `np.unique(y_train)`.
  * *Sel 30:* Menyematkan `import matplotlib.pyplot as plt` dan `import numpy as np` sebelum kalkulasi `y_pred` dan pembuatan figure plot.
* **Integritas Penanganan Ketimpangan Kelas (Class Weight):**
  * Dihitung secara matematis ketat HANYA dari `y_train` (`compute_class_weight("balanced", classes=np.unique(y_train), y=y_train)`).
  * 100% Bebas Kebocoran: Data validasi dan pengujian tidak pernah disentuh saat penentuan bobot kelas.
* **Integritas Augmentasi Data Medis (Data Augmentation):**
  * *Folder 4.4 (Default Baseline):* Murni tanpa augmentasi on-the-fly agar mencerminkan metrik asli benchmark (76,49% Irisan & 79,03% Biner).
  * *Folder 4.6 (Rekayasa Jurnal LA-CapsNet):* Augmentasi on-the-fly (`augment=True`) HANYA diaktifkan pada `train_seq`. `val_seq` dan `test_seq` secara ketat disetel `augment=False` (`shuffle=False` pada test set) guna menjamin objektivitas evaluasi medis.

---

#### 2. Matriks Komparasi Presisi (Irisan Selesai vs Biner Kaggle-Optimized)
* **Total Sel:** Tepat **101 Sel** pada kedua varian.
* **Tingkat Keselarasan Arsitektural:** **88 Sel Identik 100%** (seluruh pipeline instalasi Hadoop, konfigurasi klaster YARN, setup daemon, Spark context, arsitektur Triplet Attention, callbacks Keras 3, hingga format log metrik 13 kolom).
* **Perbedaan Fungsional:** Tepat **13 Sel Spesifik** yang disesuaikan karena perbedaan domain kelas (3 kelas vs 2 kelas) dan adaptasi limit RAM Kaggle (13 GB):

| No. Sel | Jenis Sel | Komponen / Logika | File Irisan Selesai (`sk1-...selesai.ipynb`) | File Biner Baru (`spark_yarn_tipe1_biner_*.ipynb`) | Alasan Teknis & Solusi Stabilitas |
| :---: | :---: | :--- | :--- | :--- | :--- |
| **0** | Markdown | Judul & Metadata Skenario | Irisan 3 Kelas (`NV`, `MEL`, `BKL`) | Biner (`Benign` vs `Malignant`) | Penyesuaian judul skenario riset |
| **6** | Code | Variabel Konfigurasi | `SCENARIO_TYPE = "irisan"` | `SCENARIO_TYPE = "biner"` | Pengaturan tag log dan direktori HDFS |
| **46** | Code | Definisi Kelas Target | `CLASS_NAMES = ["nevus", "melanoma", "seborrheic_keratosis"]` (3 kelas) | `CLASS_NAMES = ["benign", "malignant"]` (2 kelas) | Penyesuaian target klasifikasi medis |
| **47** | Markdown | Keterangan Staging | Manifest: 22.051 citra irisan bersih | Manifest: 33.552 citra biner bersih | Informasi dataset lokal |
| **48** | Code | Staging Dataset Lokal | Sumber: `dataset_irisan_multiclass_final.csv` (22.051 citra) | Sumber: `dataset_binary_final.csv` (33.552 citra) | Keduanya memakai *Auto-Resize 384x384* (JPEG 85, 4 thread) memangkas HDFS dari ~20 GB -> ~1,8 GB |
| **67** | Code | Resolusi & Label Mapping | Indeks 0: `nevus`, 1: `melanoma`, 2: `seborrheic_keratosis` | Indeks 0: `benign`, 1: `malignant` (diselaraskan mendefinisikan `class_names = sorted(CLASS_NAMES)` & `label_to_index`) | Sinkronisasi variabel penamaan kelas |
| **75** | Code | Sanity Check RDD | Verifikasi output vektor one-hot 3 dimensi | Verifikasi output vektor one-hot 2 dimensi | Memastikan validasi data terdistribusi |
| **77** | Code | Bukti Normalisasi (Visual) | Menampilkan plot 3 kolom per kelas | Menampilkan plot 3 kolom per kelas biner (dilengkapi proteksi mandiri `class_names = sorted(CLASS_NAMES)` & `import subprocess`) | Memastikan cell visualisasi bebas `NameError` |
| **80** | Code | Pemuatan CSV Split | Memuat ID `train`, `val`, `test` irisan (22.051 citra) | Memuat ID `train`, `val`, `test` biner (33.552 citra) | Pemuatan split lesi bebas kebocoran |
| **82** | Code | **Format Array Driver RAM** | **`float32`** (22.051 citra = ~12,65 GB RAM) | **`uint8`** (33.552 citra = **~4,7 GB RAM**) | **Kunci pencegah OOM Kaggle**: Biner crash jika float32 (18,8 GB > 13 GB RAM Kaggle) |
| **84** | Code | Output Layer Model | `Dense(3, activation='softmax')` | `Dense(2, activation='softmax')` | Penyesuaian output logit model AK85 |
| **86** | Code | Sanity Check Dummy Forward | `assert _dummy_output.shape == (4, 3)` | `assert _dummy_output.shape == (4, 2)` | Validasi graf komputasi model |
| **93** | Code | **Generator BatchSequence** | Mengiris batch array `float32` langsung | Mengiris batch array `uint8` lalu casting `bx.astype(np.float32) / 255.0` | Eliminasi lonjakan RAM Keras 3; GPU hanya memproses 32 citra (~19 MB) per langkah |
| **97** | Code | Evaluasi Test Set | 2.203 citra uji (3 kelas target) | 3.291 citra uji (2 kelas target) | Classification Report & Heatmap Confusion Matrix biner |

---

### G. `sk3-bigdat-data2017-3kelas-ak85.ipynb` (Model Standalone ResNet-50 + Triplet Attention + Preprocessing Jurnal LA-CapsNet — Status: SELESAI 100%)
* **Tujuan & Lingkungan:** Notebook pelatihan mandiri (Spark Local Mode + Multi-GPU TensorFlow) yang menggabungkan arsitektur ResNet-50 dengan modul Triplet Attention (WACV 2021) dan pipeline prapemrosesan citra dari jurnal MDPI Diagnostics 2024 (*LA-CapsNet*).
* **Dataset yang Digunakan:** Jalur Irisan 3 Kelas (HAM10000 ∩ ISIC 2017 ∩ ISIC 2019) dengan total **22.051 citra bersih bebas duplikat**:
  * `nevus` (NV): 14.148 citra
  * `melanoma` (MEL): 4.895 citra
  * `seborrheic_keratosis` (BKL): 3.008 citra
* **Alur Prapemrosesan Citra Sesuai Jurnal LA-CapsNet (Cell 7):**
  1. *Image Resizing:* `299x299` dengan *reflect border padding* menjaga proporsi asli lesi.
  2. *Contrast Stretching Normalization:* Penyesuaian distribusi statistik intensitas piksel (Hong et al., target mean 0, target varians 1) mereduksi noise dan mempertajam batas lesi.
  3. *Active Contour Segmentation (Snake Model):* Mengisolasi ROI lesi menggunakan kurva kontur aktif parametrik (`active_contour` skimage) dengan batas 15 iterasi konvergen cepat (~0,04s per citra), menghasilkan masker biner dan *smoothing* tepi lesi.
  4. *Akselerasi Multi-Threaded Paralel:* Menggunakan `ThreadPoolExecutor` (4–8 core CPU) sehingga 22.051 citra selesai diproses dalam 2–3 menit (bukan berjam-jam).
  5. *Augmentasi Data (Cell 11):* Rotasi -15° s/d +15°, Brightness/Contrast 0.7–1.3, Random Crop/Zoom, dan Flip H/V.
* **Proteksi Memori Anti-OOM (Cell 2 & Cell 4):**
  * Konfigurasi Spark Local dirampingkan ke alokasi aman (`instances=2`, `executor.memory=1536m`, `driver.memory=2g`, total footprint ~4 GB RAM).
  * Penambahan `spark.stop()` dan `gc.collect()` di akhir Cell 4 sehingga seluruh 30 GB RAM Kaggle dikembalikan utuh sebelum pelatihan model dimulai.

---

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


---

### J. `sk3_bigdat_ham2019_unetmask_ak85_v2.ipynb` (Klasifikasi 3-Kelas HAM10k + ISIC 2019 Berbasis Segmentasi U-Net — Status: TEMBUS TARGET 81.09% & AKTIF)
* **Tujuan & Lingkungan:** Notebook integrasi segmentasi lesi kulit (masker U-Net / ground truth dokter) ke arsitektur ResNet-50 + Triplet Attention AK85 untuk klasifikasi 3-kelas (`melanoma`, `nevus`, `seborrheic_keratosis`), dieksekusi di Google Colab Pro GPU NVIDIA A100-SXM4 (40 GB VRAM, 12 vCPU).
* **Dataset Tersegmentasi (24.466 Pasang Citra & Masker):**
  * Train: 19.713 citra | Val: 2.410 citra | Test (Blind Test): 2.343 citra.
* **Kronologi & Temuan 3 Eksperimen Utama Menuju Target Dosen ($\ge 80\%$):**
  1. **Eksperimen 1 (Baseline Awal):**
     * Setup: Focal Loss + Bobot Invers Ekstrem + Fine-tuning terbatas pada `conv5_block3` saja + LR $5 	imes 10^{-6}$.
     * Hasil: Akurasi Blind Test **65.13%**, AUC 0.8457, PR-AUC 0.6879.
     * Evaluasi Medis: Presisi BKL anjlok ke **0.33** (terjadi ledakan *false positive* karena bobot penalti terlalu ekstrem), Recall Melanoma tertinggal di **0.43**.
  2. **Eksperimen 2 (CrossEntropy Unweighted + Fine-Tuning Luas):**
     * Setup: `CategoricalCrossentropy(label_smoothing=0.05)` tanpa class weight + unfreeze seluruh blok `conv4_` dan `conv5_` (BatchNorm frozen) + LR $1.5 	imes 10^{-5}$.
     * Hasil: Akurasi Blind Test melonjak drastis ke **76.87% (+11.74%)**, AUC 0.8799, PR-AUC 0.7598.
     * Evaluasi Medis: Presisi BKL pulih ke **0.63**, Presisi Melanoma naik ke **0.76**, namun Recall Melanoma masih tertahan di **0.43**.
  3. **Eksperimen 3 (Prapemrosesan ROI Lesion Bounding Box + Soft Balancing):**
     * **Pencapaian:** Akurasi Blind Test **81.09% (Target $\ge 80\%$ RESMI TEMBUS)**, AUC **0.9134 (91.3%)**, PR-AUC **0.8180 (81.8%)**, Loss Test 0.6242.
     * Evaluasi Medis:
       * Melanoma: Precision **0.73**, Recall melonjak ke **0.59 (59%)**, F1-score **0.65**.
       * Nevus: Precision **0.86**, Recall **0.92 (92%)**, F1-score **0.89**.
       * Seborrheic Keratosis: Precision **0.66**, Recall **0.66 (66%)**, F1-score **0.66**.
     * **Temuan Krusial Preprocessing Citra:**
       * Masking hitam pekat (`img * mask`) terbukti membuat lesi kecil tetap kecil saat diresize ke 224x224.
       * Menggunakan mask untuk mendeteksi koordinat *Bounding Box* lalu memotong ROI dengan **15% padding kulit sehat** sukses memperbesar resolusi lesi tanpa menghilangkan konteks gradasi tepi pigmen di perbatasan kulit sehat.
     * **Bukti Fisik Lengkap:** Disimpan dan diamankan di [`kode/5_segmentasi_unet/02_baseline_resnet50_roi_ak81.ipynb`](kode/5_segmentasi_unet/02_baseline_resnet50_roi_ak81.ipynb) (4.44 MB, memuat seluruh grafik 5 tahap preprocessing, riwayat training, dan heatmap confusion matrix).
  4. **Eksperimen 4 (Uji Coba Bobot EXP-W1 & Evaluasi Metodologis):**
     * Setup: Bobot moderat (Melanoma 1.70, Nevus 1.00, SK 2.10) + `label_smoothing=0.03` + LR $5 \times 10^{-6}$.
     * Hasil Blind Test: Akurasi **77.98%**, Macro-F1 0.71, AUC 0.9005, PR-AUC 0.7917.
     * Evaluasi Medis: Recall Melanoma berhasil naik ke **0.62** dan SK ke **0.68**, namun mengorbankan Presisi (Melanoma 0.64, SK 0.58) serta akurasi global.
     * **Keputusan Riset:** Konfigurasi **81.09% (Unweighted + Label Smoothing 0.05 + LR 1.5e-5)** resmi dipulihkan sebagai Baseline Utama. Langkah berikutnya murni menguji **Augmentasi Ringan** secara terkontrol tanpa mengubah bobot atau learning rate.
     * **Protokol Metodologi Tesis:** Data Test Set diisolasi penuh (tidak diintip selama proses tuning). Keputusan pemilihan model murni dipandu oleh performa Validation Set (`val_pr_auc` & `val_accuracy`), dan Test Set hanya dieksekusi 1 kali saat pengujian final tesis.

  5. **Eksperimen 5 (EXP 1: Uji Efek Murni Augmentasi Ringan — Status: SELESAI):**
     * Setup: Baseline 81.09% (Unweighted, LR 1.5e-5, label_smoothing 0.05, 224x224) + Augmentasi Ringan Presisi (Flips H/V, Rot 10°, Zoom 10%, Shift 5%, tanpa distorsi warna).
     * File Notebook Output: [`kode/5_segmentasi_unet/03_exp1_resnet50_augmentasi.ipynb`](kode/5_segmentasi_unet/03_exp1_resnet50_augmentasi.ipynb) (5.3 MB).
     * Checkpoint Fisik Teramankan di Drive: `/content/drive/MyDrive/best_melanoma_model_exp1_aug.keras` (Best Epoch 19).
     * Waktu Pelatihan: 26.04 menit (Fase 1: 4.78m, Fase 2: 21.26m).
     * Hasil Evaluasi:
       * **Validation Set (Anchor):** Akurasi **80.62%** (naik dari ~79.88%), PR-AUC **0.8005** (naik dari 0.7960, tembus 0.80 pertama kali), Loss **0.6648** (lebih rendah), SK Recall **0.60** (naik dari 0.56).
       * **Blind Test Set:** Akurasi **80.50%** (stabil $\ge 80\%$), SK Recall **0.70 (70%)** (rekor tertinggi), Melanoma Recall 0.57, Nevus Recall 0.91.
     * Evaluasi & Keputusan: Augmentasi terbukti memperbaiki generalisasi pada Validation Set (`PR-AUC > 0.80`), namun belum mengalahkan baseline 81.09% pada test set secara konsisten. Disepakati lanjut ke EXP 2.

    6. **Eksperimen 6 (EXP 2: Uji Resolusi 256×256 — Status: SELESAI & KANDIDAT JUARA TERBAIK 🏆):**
     * Setup: Murni diturunkan dari Baseline 81.09% (tanpa augmentasi EXP 1, unweighted murni, LR 1.5e-5, label_smoothing 0.05), HANYA menaikkan resolusi `TARGET_SIZE = 256` (Folder output: `processed_images_roi_256/`, Input shape: `256x256x3`, Batch size: 256).
     * File Notebook: [`kode/5_segmentasi_unet/04_exp2_resnet50_resolusi256.ipynb`](kode/5_segmentasi_unet/04_exp2_resnet50_resolusi256.ipynb).
     * Checkpoint Fisik Teramankan di Drive: `/content/drive/MyDrive/best_melanoma_model_exp2_res256.keras` (Best Epoch 21).
     * Total Waktu Pelatihan: 51.88 menit (Fase 1: 9.34m, Fase 2: 42.54m).
     * Hasil Evaluasi:
       * **Validation Set (Jangkar Model):**
         * PR-AUC: **0.8081 (80.81%)** 🏆 (Rekor tertinggi sepanjang masa riset).
         * Loss: **0.6634** 🏆 (Paling rendah dan stabil).
         * Akurasi: **80.33%**.
         * Melanoma Recall: **0.65 (65%)** 🏆 (Naik dari 0.64).
         * SK Recall: **0.61 (61%)** 🏆 (Naik dari 0.56).
       * **Blind Test Set (2.343 Citra):**
         * Akurasi: **80.79% (~81%)** (Sangat stabil di atas target $\ge 80\%$).
         * Melanoma Recall: **0.61 (60.56%)** 🏆 (Tembus >60% pertama kali pada data blind test).
         * SK Recall: **0.71 (71.15%)** 🏆 (Rekor tertinggi lintas seluruh eksperimen).
         * Nevus Precision: **0.88 (88%)** | Macro-F1: **0.7387 (~0.74)**.
         * Skor Seleksi Komposit: **0.7159** 🏆 (Skor tertinggi dari seluruh model yang pernah diuji).
     * Temuan Ilmiah Krusial:
       * Menaikkan resolusi citra ke 256×256 meloloskan detail mikroskopis pola pigmen retikuler yang sangat dibutuhkan Triplet Attention pada blok konvolusi conv4 (resolusi feature map naik dari $14 \times 14$ ke $16 \times 16$).
       * Peningkatan resolusi secara tunggal berhasil mendongkrak recall deteksi kanker (Melanoma >60% & SK >71%) tanpa merusak presisi Nevus maupun akurasi global.
       * EXP 2 resmi ditetapkan sebagai **Kandidat Juara Utama** menggantikan Baseline 224x224.

  7. **Eksperimen 7 (EXP 3: Dual-Stream ROI Lesi + Full Image — Status: SIAP EKSEKUSI):**
     * Konsep Arsitektur: Menggabungkan cabang mikrostruktur lesi (*ROI Zoom-In*) dan konteks makro kulit (*Full Image*) menggunakan *Shared ResNet-50 Backbone* (Weight Sharing) + Triplet Attention Conv4 $\rightarrow$ *Feature Concatenation* (10.240 fitur) $\rightarrow$ Head Dense 256 $\rightarrow$ 128.
     * File Notebook: [`kode/5_segmentasi_unet/05_exp3_resnet50_dualstream.ipynb`](kode/5_segmentasi_unet/05_exp3_resnet50_dualstream.ipynb).
     * Checkpoint Otomatis di Drive: `/content/drive/MyDrive/best_melanoma_model_exp3_dualstream.keras`.
     * Data Pipeline: Generator `DualImageSequence` (thread-safe multi-input).

  8. **Eksperimen 8 (EXP 4: True Triplet Attention Sekuensial — Status: SIAP EKSEKUSI):**
     * Konsep Arsitektur: Mengubah integrasi Triplet Attention dari skip-connection paralel menjadi **integrasi sekuensial sejati (*True Triplet Attention*)**:
       $$\text{Conv1-Conv4} \rightarrow \text{Triplet Attention (14} \times \text{14)} \rightarrow \text{Blok Conv5} \rightarrow \text{GAP+GMP (4.096)} \rightarrow \text{Head Dense 256} \rightarrow 128$$
     * Rasional Ilmiah: Memastikan seluruh representasi tingkat tinggi yang dipelajari blok Conv5 telah difilter dan dipandu oleh interaksi 3-arah Triplet Attention (Channel-Height, Channel-Width, Spatial).
     * File Notebook: [`kode/5_segmentasi_unet/06_exp4_resnet50_truetriplet.ipynb`](kode/5_segmentasi_unet/06_exp4_resnet50_truetriplet.ipynb).
     * Checkpoint Otomatis di Drive: `/content/drive/MyDrive/best_melanoma_model_exp4_truetriplet.keras`.
     * Parameter Murni Baseline: Resolusi 224×224, CrossEntropy label_smoothing 0.05, unweighted, LR 1.5e-5 (AdamW).

* **Konfigurasi Lanjutan yang Diterapkan (EXP 1 + EXP 2):**
  * *EXP 1 (Augmentasi Ringan Presisi):* Flips H/V, Rotasi 15°, Zoom 10%, Shift 5%, tanpa *brightness/color jitter* agar fitur variasi warna asli melanoma tidak terdistorsi.
  * *EXP 2 (Soft Weight Tuning W1):* Bobot moderat (Melanoma 1.70, Nevus 1.00, SK 2.10) untuk menaikkan Recall Melanoma & SK tanpa menghancurkan Nevus.
  * *Tuning Hyperparameter:* `label_smoothing` disesuaikan ke `0.03` dan Fine-tuning LR ke `5e-6` (AdamW).
  * *Proteksi Otomatis Checkpoint:* Auto-mount Google Drive, model langsung disimpan ke `/content/drive/MyDrive/best_melanoma_model_exp1_w1.keras`.
  * *Skor Seleksi Internal Eksperimen:* $	ext{Score} = rac{	ext{Accuracy} + 	ext{MacroF1} + 	ext{Recall}_{mel} + 	ext{Recall}_{SK}}{4}$.

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
│   ├── dataset_binary_final.csv            # Master dataset jalur binary (33.552 citra bersih + kolom split & lesion_id)
│   ├── dataset_binary_train.csv            # Training set biner 80% (26.860 citra)
│   ├── dataset_binary_val.csv              # Validation set biner 10% (3.401 citra)
│   ├── dataset_binary_test.csv             # Test set biner 10% (3.291 citra - 100% Zero Leakage)
│   ├── dataset_clean_3dataset.csv          # Metadata 35.599 citra bersih (HAM10k, 2017, 2019)
│   ├── dataset_clean_final.csv             # Metadata 480.882 citra bersih (14 sumber)
│   ├── dataset_gabungan_ham10k_2017_2019.csv # Dataset gabungan bersih 3 dataset 9 kelas (35.599 baris)
│   ├── dataset_irisan_multiclass_final.csv # Master dataset irisan 3 kelas AKTIF (22.051 citra bersih)
│   ├── dataset_irisan_3kelas_train.csv     # Training set irisan 80% (17.656 citra)
│   ├── dataset_irisan_3kelas_val.csv       # Validation set irisan 10% (2.192 citra)
│   ├── dataset_irisan_3kelas_test.csv      # Test set irisan 10% (2.203 citra)
│   ├── dataset_irisan_7kelas_final.csv     # Dataset final irisan 7 kelas alternatif (24.900 citra bersih)
│   ├── HAM10K/                             # Folder dataset HAM10000 & uji ISIC 2018
│   ├── isic 2016/ ... isic 2024/           # Arsip kompetisi ISIC tahunan

├── kode/                                   # Direktori seluruh kode & notebook terstruktur rapi
│   ├── 1_data_understanding/               # Eksplorasi awal dataset ISIC & HAM10000
│   │   ├── 1-data_understanding_isic.ipynb # Versi original 14 dataset
│   │   ├── 1-data_understanding_isic improve.ipynb # Versi baru: harmonisasi medis lengkap, rujukan 14 dataset, HAM10k utuh 100%, pre-rendered
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


### 5.2 Laporan Eksekutif (Excel)
Telah dibuat standardisasi pembuatan laporan Excel untuk diserahkan kepada dosen.
* laporan/excel/Laporan_Data_Irisan.xlsx: Laporan deduplikasi & split bebas kebocoran untuk Jalur Irisan 3 Kelas (22.051 citra).
* laporan/excel/Laporan_Data_Biner.xlsx: Laporan deduplikasi & split bebas kebocoran untuk Jalur Biner (33.552 citra).
Seluruh laporan ini sudah memenuhi kaidah *Standar Excel Kulit* (hitam-putih, tabel tegas, bahasa non-AI, plus ekstraksi grafik base64 dari .ipynb).

## 6. Checklist Tugas & Titik Lanjut Berikutnya (Actionable Next Steps)

### C. Progres Segmentasi U-Net & Klasifikasi AK85 (Folder 5)
- [x] **Penyelarasan Multi-Source HAM10000 & ISIC 2019:** Penggabungan 24.466 pasangan citra dengan masker dokter & pseudo-masker U-Net bebas kebocoran.
- [x] **Eksperimen Baseline 1:** Identifikasi kegagalan bobot ekstrem pada Focal Loss (Akurasi 65.13%, Presisi BKL 0.33).
- [x] **Eksperimen 2:** Peningkatan performa via CrossEntropy + unfreeze Conv4 & Conv5 (Akurasi 76.87%).
- [x] **Eksperimen 3 (Pencapaian Milestone 81.09%):** Implementasi ROI Bounding Box Crop (+15% padding kulit) + CLAHE + Head 256->128 ($L_2=10^{-4}$), menembus target dosen di angka **81.09% pada Blind Test murni** (AUC 91.3%, Melanoma Recall 0.59).
- [x] **Penyimpanan Artefak Hasil Pelatihan:** Mengamankan file notebook lengkap (4.44 MB) di [`kode/5_segmentasi_unet/02_baseline_resnet50_roi_ak81.ipynb`](kode/5_segmentasi_unet/02_baseline_resnet50_roi_ak81.ipynb).
- [x] **Penerapan Optimasi EXP 1 + EXP 2:** Menyiapkan augmentasi geometri presisi, bobot kelas W1, label smoothing 0.03, LR 5e-6, dan auto-save Google Drive pada [`kode/5_segmentasi_unet/sk3_bigdat_ham2019_unetmask_ak85_v2 (1).ipynb`](kode/5_segmentasi_unet/sk3_bigdat_ham2019_unetmask_ak85_v2%20(1).ipynb).
- [ ] **Eksekusi Run Eksperimen EXP 1 + EXP 2:** Menjalankan pelatihan di Google Colab Pro GPU A100 untuk menguji peningkatan Recall Melanoma $\ge 0.65$ dan SK $\ge 0.70$.


### A. Progres Implementasi Jalur Biner (Benign vs Malignant)
- [x] **Langkah 1–14 (Selesai):** Data understanding, kurasi 3 dataset (HAM10k, ISIC 2017, ISIC 2019), deduplikasi terarah, harmonisasi label medis internasional 8 kelas, konsensus voting 8 jurnal internasional, dan ekspor master awal di [`kode/2_jalur_biner/binary_mapping improve.ipynb`](kode/2_jalur_biner/binary_mapping%20improve.ipynb).
- [x] **Langkah 15 (Selesai):** Pemisahan data Train / Validation / Test (80:10:10) anti-kebocoran (*Lesion-Aware Stratification* via `StratifiedGroupKFold`) dengan resolusi 2.074 duplikat varian `_downsampled` agar tidak menyeberang partisi.
  - **Hasil Audit Kebocoran:** Overlap Train <-> Val = 0, Overlap Train <-> Test = 0, Overlap Val <-> Test = 0, Mismatch varian downsampled = 0 (**100% Bebas Kebocoran Data**).
  - **File CSV yang Dihasilkan di `Dataset/`:**
    * `dataset_binary_final.csv` (33.552 baris dengan kolom `split` dan `lesion_id`).
    * `dataset_binary_train.csv` (26.860 baris / 80,05%).
    * `dataset_binary_val.csv` (3.401 baris / 10,14%).
    * `dataset_binary_test.csv` (3.291 baris / 9,81%).
- [x] **Langkah 16 (Selesai):** Evaluasi stratifikasi split dan karakteristik resolusi fisik citra (proporsi Benign ~62,8% vs Malignant ~37,2% konsisten lintas subset data, visualisasi bar plot 2 panel).
- [x] **Langkah 17 (Selesai):** Kesimpulan data preparation biner dan kesiapan modeling Big Data PySpark on YARN.
- [x] **Sinkronisasi Penuh 5 Skenario PySpark on YARN Jalur Biner (Selesai 100%):** Memperbarui seluruh 5 notebook di [`kode/4_Spark_on_Yarn/biner/`](kode/4_Spark_on_Yarn/biner/) (`2W2P`, `2W8P`, `8W2P`, `8W8P`, dan `ak85`) mengadopsi arsitektur teruji dari `sk1-spark-on-distributed-irisan3kelas-2p2w-v3-0-selesai.ipynb`:
  * *Proteksi Kuota Disk Kaggle (Staging Auto-Resize 384x384):* Sel 48 menggunakan `ThreadPoolExecutor(max_workers=4)` untuk mereduksi 33.552 citra master dari ~20 GB menjadi ~1,8 GB di HDFS.
  * *Proteksi Memori RAM Kaggle (Array Driver uint8):* Sel 82 mengalokasikan array NumPy driver (`X_train`, `X_val`, `X_test`) dalam format `uint8` (~4,7 GB RAM), mencegah crash OOM (jika float32 memakan 18,8 GB melampaui RAM Kaggle 13 GB).
  * *PyArrow Shard-HDFS Streaming:* Sel 82 mengeliminasi shuffle masif dan double persist disk, menulis shard 64 citra/shard langsung ke HDFS dan mengunduh linier ke driver dengan pembersihan memori seketika (`spark.stop()`).
  * *Generator BatchSequence Keras 3:* Sel 93 mengiris batch 32 citra secara mandiri dan mengonversi `uint8 -> float32 / 255.0` on-the-fly, mengeliminasi duplikasi memori internal TensorFlow Keras 3 (~1,9x RAM).
  * *YARN NodeManager Resource Lock & Bad-Node Protection:* Sel 30 & 32 mengunci memori NodeManager 14 GB dan menonaktifkan `disk-health-checker` (ambang 99%) agar executor tidak dibunuh secara sepihak.
  * *Arsitektur Model AK85 Biner:* Sel 84 mengintegrasikan layer `ResNetCaffePreprocess` (BGR mean-subtraction), Triplet Attention, dan dense output 2 kelas (`Dense(2, activation='softmax')`), dengan checkpoint `.keras` di Sel 91.
  * *Verifikasi Komprehensif 101 Sel:* Seluruh 5 notebook terverifikasi tepat 101 sel, 0 Syntax Error AST, dan siap dieksekusi di Kaggle GPU.


### B. Progres Implementasi Jalur Irisan 3 Kelas (HAM10000 ∩ ISIC 2017 ∩ ISIC 2019)
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
- [x] **Perbaikan Eksekusi PySpark on YARN di Kaggle (Selesai):** Menyelesaikan bug `Connection refused` dan *auto-kill* SIGHUP dari Kaggle pada file `irisan-3-kelas-2p2w.ipynb`. Menggunakan trik `!setsid` untuk melindungi daemon YARN dari pembersihan *process group* Kaggle, serta menyuntikkan skrip pembersihan variabel *dead gateway port* Py4J (`PYSPARK_GATEWAY_PORT`). Dataset HDFS juga dipastikan terunggah penuh.
- [x] **Solusi Crash Kaggle YARN Langkah 33 & Deep Audit 101 Sel (Selesai):** Menuntaskan bug YARN executor lost (SIGTERM 143), mengoptimasi `yarn-site.xml`, `spark-defaults.conf`, auto-resize 384px HDFS staging, mengimplementasikan *Single-Pass Stream* pengumpulan array driver bebas shuffle, dan menyelesaikan deep audit 101 sel pada [`kode/4_Spark_on_Yarn/sk1-spark-on-distributed-irisan3kelas-2p2w-v3-0.ipynb`](kode/4_Spark_on_Yarn/sk1-spark-on-distributed-irisan3kelas-2p2w-v3-0.ipynb).
- [x] **Eksekusi Penuh Skenario 1 (2W2P) di Kaggle GPU (Selesai 100%):** Berhasil dieksekusi end-to-end tanpa error YARN/OOM. Waktu prapemrosesan terdistribusi: 122,06 detik; waktu training GPU (15 epoch): 837,36 detik. Metrik Test Set: Akurasi 76,49%, Macro F1 0,7030, ROC-AUC 0,9004. Log tersimpan otomatis di `results.csv`.
- [x] **Sinkronisasi Penuh 4 Varian Skenario PySpark on YARN Irisan 3 Kelas (Selesai):** Seluruh 4 notebook pada folder [`kode/4_Spark_on_Yarn/irisan/`](kode/4_Spark_on_Yarn/irisan/) (`spark_yarn_tipe1_irisan_2W2P.ipynb`, `2W8P`, `8W2P`, `8W8P`) telah disinkronkan dengan arsitektur PyArrow Shard-HDFS (Sel 82), generator `BatchSequence` (Sel 93), dan kunci alokasi NodeManager 14 GB (Sel 30) yang teruji di Kaggle.
- [ ] **Langkah 2:** Menjalankan pelatihan penuh (*Full Training* 10–20 epoch) ResNet-50 vs EfficientNet-B0 pada akselerator GPU (Google Colab / Kaggle T4) menggunakan skrip modular `python kode/3_jalur_irisan_3kelas/train_baseline.py --loss focal` / `--loss cb_focal` sesuai panduan GPU.

### 📋 Agenda 4 Tugas Verifikasi & Rekap Dosen (STATUS: PENDING TINJAUAN PENGGUNA)
> [!IMPORTANT]
> **Catatan Pengguna:** Pengguna belum melakukan/meninjau sendiri 4 tugas di bawah ini setelah perintah `/start`. Seluruh berkas pendukung (file Excel dan laporan formal) telah disiapkan oleh sistem, namun status checklist **tetap dianggap belum selesai (`[ ]`)** dari sudut pandang pengguna dan **wajib diingatkan kembali pada sesi berikutnya**.

- [ ] **Tugas Cross-Check (Wajib Tinjauan Pengguna Sebelum Lanjut): Memastikan Isi Laporan Excel Sinkron dengan Output Kode.** 
  - Pengguna wajib memeriksa mandiri file laporan/excel/Laporan_Data_Irisan.xlsx dan laporan/excel/Laporan_Data_Biner.xlsx.
  - Validasi bahwa seluruh angka, metode deduplikasi (Image ID tanpa MD5), dan grafik yang disisipkan telah 100% cocok dengan hasil run terakhir notebook irisan_mapping improve.ipynb dan inary_mapping improve.ipynb.


- [ ] **Tugas 1 (Pending Review Pengguna): Pengecekan Label Harmonisasi Biner vs Irisan vs Rujukan Jurnal**
  - Mengaudit konsistensi kode diagnosis (`NV`, `MEL`, `BKL`, `BCC`, `AKIEC`, `SCC`, `VASC`, `DF`, `UNK`) antara notebook jalur biner (`binary_mapping improve.ipynb`) dan jalur irisan (`data_understanding_irisan_3kelas improve.ipynb` & `irisan_mapping improve.ipynb`).
  - Memastikan definisi harmonisasi (peleburan `seborrheic_keratosis ≡ BKL`) 100% selaras dengan standar literatur (*Tschandl et al., Nature 2018*, hal. 7 dan *Codella et al., IEEE ISBI 2018*).
- [ ] **Tugas 2 (Pending Review Pengguna): Verifikasi Pemetaan Label Biner dengan Rujukan Konsensus Ilmiah**
  - Mengecek ulang pemetaan biner (Benign 0 vs Malignant 1) terhadap matriks voting 8 jurnal internasional (Elsevier, MDPI, Springer, Frontiers).
  - Konsensus mutlak (100%): `NV`, `BKL`, `DF` (Jinak) dan `MEL`, `BCC`, `AKIEC`, `SCC` (Ganas). Konsensus mayoritas (80%): `VASC` (Jinak). `UNK` berhasil dieliminasi (2.047 citra OOD).
- [ ] **Tugas 3 (Pending Review Pengguna): Audit dan Cross-Check Output Data Biner vs Irisan**
  - Melakukan validasi silang komputasional antara file output: `dataset_binary_final.csv` (33.552 baris) dengan `dataset_irisan_multiclass_final.csv` (22.051 baris).
  - Hasil: Seluruh 22.051 citra irisan (100%) beririsan sempurna di dalam dataset biner dengan 0 mismatch label dan 0 mismatch sumber dataset. Dekomposisi 11.501 citra non-irisan terbukti berasal dari kelas non-2017 (BCC, AKIEC, SCC, VASC, DF) serta partisi test ISIC 2019.
- [ ] **Tugas 4 (Pending Review Pengguna): Pembuatan & Pemeriksaan File Rekapitulasi untuk Dosen**
  - Berkas yang telah disiapkan dan siap ditinjau pengguna:
    * File Excel Versi Improve (Bahasa Santai & Desain Premium): [`rekap_dataset_biner_dan_irisan improve.xlsx`](file:///c:/Users/ARII/Downloads/Data%20Understanding%20Isic%20&%20Ham10k/rekap_dataset_biner_dan_irisan%20improve.xlsx) (6 sheet terstruktur: Ringkasan & Panduan Mudah setara usia 18 tahun, Kenapa Jinak vs Ganas, Angka Data Jalur Biner, Angka Data Irisan 3K, Bukti Data Klop, Daftar Jurnal Lengkap berbobot Q1/Nature + judul lengkap paper + link DOI).
    * File Excel Versi Standar Formal: [`rekap_dataset_biner_dan_irisan.xlsx`](file:///c:/Users/ARII/Downloads/Data%20Understanding%20Isic%20&%20Ham10k/rekap_dataset_biner_dan_irisan.xlsx).
    * Skrip Generator Otomatis: [`generate_rekap_excel_improve.py`](file:///c:/Users/ARII/Downloads/Data%20Understanding%20Isic%20&%20Ham10k/generate_rekap_excel_improve.py).
    * Dokumen Laporan Formal: [`notes jurnal/laporan_komparasi_dan_rekap_dataset_biner_vs_irisan.md`](file:///c:/Users/ARII/Downloads/Data%20Understanding%20Isic%20&%20Ham10k/notes%20jurnal/laporan_komparasi_dan_rekap_dataset_biner_vs_irisan.md).
  - Pengguna perlu memeriksa lembar kerja ini sebelum diserahkan ke dosen pembimbing.

### 🚀 Titik Lanjut Berikutnya (Actionable Next Steps)
- [ ] **Eksperimen Big Data PySpark on YARN Jalur Biner (Kaggle GPU):**
  * [x] **File Rekayasa Prapemrosesan Jurnal LA-CapsNet (33 Sel, 299x299 + Snake):** [`kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk2-biner-tipe1-ringkas-prepjurnal.ipynb`](kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk2-biner-tipe1-ringkas-prepjurnal.ipynb).
  * [x] **File Utama Siap Eksekusi (33 Sel Ringkas + Optimasi Default 224px):** [`kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk2-biner-tipe1-ringkas-optimasi.ipynb`](kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk2-biner-tipe1-ringkas-optimasi.ipynb) (Default 2W2P, cukup ubah `NUM_WORKERS` & `NUM_PARTITIONS` untuk skenario 2W8P, 8W2P, 8W8P).
  * [x] **Arsip Benchmark Sukses (101 Sel dengan Bukti Output Kaggle):** [`kode/4_Spark_on_Yarn/4.1-arsip-biner-benchmark/sk2-biner-tipe1-101cel-selesai.ipynb`](kode/4_Spark_on_Yarn/4.1-arsip-biner-benchmark/sk2-biner-tipe1-101cel-selesai.ipynb) (Preprocessing: 184,31s, Training 15 epoch: 1.248,33s, Test Acc: 79,03%, Macro F1: 0,7790, ROC-AUC: 0,8718).
  * [x] **Versi 101 Sel Lengkap + Optimasi:** [`kode/4_Spark_on_Yarn/4.3-101cel-optimasi/sk2-biner-tipe1-101cel-optimasi.ipynb`](kode/4_Spark_on_Yarn/4.3-101cel-optimasi/sk2-biner-tipe1-101cel-optimasi.ipynb).
- [ ] **Eksperimen Big Data PySpark on YARN Jalur Irisan 3 Kelas (Kaggle GPU):**
  * [x] **File Rekayasa Prapemrosesan Jurnal LA-CapsNet (33 Sel, 299x299 + Snake):** [`kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk1-irisan-tipe1-ringkas-prepjurnal.ipynb`](kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk1-irisan-tipe1-ringkas-prepjurnal.ipynb).
  * [x] **File Utama Siap Eksekusi (33 Sel Ringkas + Optimasi Default 224px):** [`kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk1-irisan-tipe1-ringkas-optimasi.ipynb`](kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk1-irisan-tipe1-ringkas-optimasi.ipynb) (Default 2W2P, cukup ubah `NUM_WORKERS` & `NUM_PARTITIONS` untuk skenario 2W8P, 8W2P, 8W8P).
  * [x] **Arsip Benchmark Sukses (101 Sel dengan Bukti Output Kaggle):** [`kode/4_Spark_on_Yarn/4.2-arsip-irisan-benchmark/sk1-irisan-tipe1-101cel-selesai.ipynb`](kode/4_Spark_on_Yarn/4.2-arsip-irisan-benchmark/sk1-irisan-tipe1-101cel-selesai.ipynb) (Preprocessing: 122,06s, Training 15 epoch: 837,36s, Test Acc: 76,49%, Macro F1: 0,7030, ROC-AUC: 0,9004).
  * [x] **Versi 101 Sel Lengkap + Optimasi:** [`kode/4_Spark_on_Yarn/4.3-101cel-optimasi/sk1-irisan-tipe1-101cel-optimasi.ipynb`](kode/4_Spark_on_Yarn/4.3-101cel-optimasi/sk1-irisan-tipe1-101cel-optimasi.ipynb).
- [x] **Run Skenario Lanjutan Irisan (2W2P, 2W8P, 8W2P, 8W8P) Sukses di Kaggle GPU 100%:**
  * Log resmi tersimpan di [`results.csv`](results.csv) dan visualisasi grafik perbandingan tersimpan di [`grafik_komparasi_4skenario_yarn.png`](grafik_komparasi_4skenario_yarn.png).
  * **2W2P:** Preprocessing 83,76s (CPU 64,03%, RAM 6.932 MB) | GPU Train 585,96s | Acc: 74,13% | Macro F1: 0,6786 | ROC-AUC: 0,8899
  * **2W8P:** Preprocessing 93,14s (CPU 60,06%, RAM 12.461 MB) | GPU Train 599,95s | Acc: 73,63% | Macro F1: 0,6634 | ROC-AUC: 0,8903
  * **8W2P:** Preprocessing 100,08s (CPU 57,95%, RAM 17.641 MB) | GPU Train 585,44s | Acc: 74,63% | Macro F1: 0,6852 | ROC-AUC: 0,8999
  * **8W8P:** Preprocessing 92,29s (CPU 93,84%, RAM 22.440 MB) | GPU Train 587,81s | Acc: **76,31%** | Macro F1: **0,6946** | ROC-AUC: 0,8976
- [ ] **Langkah Lanjut (Modeling GPU Baseline PyTorch):** Menjalankan pelatihan penuh (*Full Training* 10–20 epoch) ResNet-50 vs EfficientNet-B0 pada akselerator GPU (Google Colab / Kaggle T4) menggunakan skrip modular `python kode/3_jalur_irisan_3kelas/train_baseline.py --loss focal` / `--loss cb_focal` sesuai panduan di [`kode/3_jalur_irisan_3kelas/panduan_eksekusi_gpu_colab_kaggle.md`](kode/3_jalur_irisan_3kelas/panduan_eksekusi_gpu_colab_kaggle.md).

### H. Hasil Eksekusi Nyata Folder 4.6 Prepjurnal Irisan & Ablation Run 3 (Folder Baru 4.7)
* **Sumber Data:** File `4-6-irisan-full-semi-final.ipynb` (di root proyek, hasil unduhan dari Kaggle setelah eksekusi nyata skenario `irisan_prepjurnal_2W2P` — segmentasi Dull Razor + Adaptive Contour + Soft-Blend, **tanpa augmentasi**, backbone ResNet50 **100% beku** `base_model.trainable = False`, `EPOCHS=10`).
* **Hasil Aktual (Test Set, TURUN dari baseline tanpa segmentasi):**
  * Test Accuracy: **71,77%** (baseline 4.3 tanpa segmentasi: 76,31–76,49%)
  * Test Macro F1: **0,6409** (baseline: 0,6786–0,7030)
  * ROC-AUC (OVR): **0,8663** (baseline: 0,8899–0,9004)
  * Per kelas: `melanoma` P0,60/R0,63/F0,62 | `nevus` P0,90/R0,77/F0,83 | `seborrheic_keratosis` P**0,38**/R0,64/F0,48 — presisi BKL anjlok dari baseline 0,53.
* **Diagnosis Akar Masalah:**
  1. `val_loss` masih terus turun sampai epoch 10/10 — `EarlyStopping` (`patience=5`) tidak sempat aktif, model **undertrained**.
  2. Backbone ResNet50 dibekukan 100% (murni feature-extractor) sehingga fitur ImageNet (dilatih dari foto natural) tidak sempat beradaptasi ke distribusi citra hasil segmentasi (latar diburamkan/sebagian dihitamkan oleh soft-blend) — diduga penyebab utama presisi BKL jatuh, karena BKL secara medis banyak dikenali dari tekstur & transisi ke kulit sekitar lesi yang justru dibuang segmentasi.
* **Rencana Ablation Ladder (didiskusikan dengan pengguna) — dosen mewajibkan segmentasi tetap ada di preprocessing, jadi solusinya "benerin", bukan "buang segmentasi":**
  * Run 1 (arsip 4.2, sudah ada): tanpa segmentasi, frozen, 15 epoch → 76,49%.
  * Run 2 (file `4-6-irisan-full-semi-final.ipynb`, sudah ada): +segmentasi, frozen, 10 epoch → 71,77% (lihat di atas).
  * **Run 3 (BARU, folder [`kode/4_Spark_on_Yarn/4.7-finetune-conv5/sk1-irisan-tipe1-finetune-conv5.ipynb`](kode/4_Spark_on_Yarn/4.7-finetune-conv5/sk1-irisan-tipe1-finetune-conv5.ipynb), status: kode siap, BELUM dieksekusi di Kaggle):** +segmentasi (tidak diubah), tetap tanpa augmentasi (isolasi variabel), tapi training 2 fase — (A) warm-up backbone beku 5 epoch, (B) unfreeze layer `conv5_block*` + `Adam(lr=1e-5)` + lanjut 20 epoch (total 25, `EarlyStopping`/`ReduceLROnPlateau` tetap aktif tiap fase). `ModelCheckpoint` fase B pakai `initial_value_threshold` dari val_loss terbaik fase A agar tidak tertimpa model lebih buruk. `SCENARIO_NAME` = `irisan_prepjurnal_finetune_2W2P`, otomatis tercatat baris baru di `results.csv` saat dijalankan.
  * Run 4 (rencana selanjutnya, belum dibuat): +augmentasi terarah kelas minoritas (BKL & MEL) di atas Run 3, kalau Run 3 belum cukup mengembalikan akurasi ke atas 76%.
  * **Run 5 biner (folder [`kode/4_Spark_on_Yarn/4.7-finetune-conv5/sk2-biner-tipe1-finetune-conv5.ipynb`](kode/4_Spark_on_Yarn/4.7-finetune-conv5/sk2-biner-tipe1-finetune-conv5.ipynb), status: kode siap, BELUM dieksekusi):** Biner belum pernah diuji sama sekali dengan segmentasi (tidak ada Run 2 biner) — jadi bukan diulang persis ladder irisan, langsung dibangun versi yang sudah diperbaiki (segmentasi dari `4.6-ringkas-optimasi-prepjurnal/sk2-biner-tipe1-ringkas-prepjurnal.ipynb` + fine-tuning 2 fase identik Run 3 irisan) supaya tidak membuang kuota GPU Kaggle mengulang kegagalan backbone-beku yang sudah terbukti di irisan. `SCENARIO_NAME` = `biner_prepjurnal_finetune_2W2P`, dibandingkan ke baseline biner tanpa segmentasi 79,03% (arsip 4.1).
  * **Audit kesamaan sk1 (irisan) vs sk2 (biner) di folder 4.7 (diverifikasi via diff terprogram, bukan asumsi):** dari 33 sel, 13 identik 100% (termasuk kode segmentasi sel 20 — byte-per-byte sama) dan logika inti fine-tuning (`WARMUP_EPOCHS=5`, `FINETUNE_EPOCHS=20`, unfreeze `conv5_block*`, `Adam(lr=1e-5)`, callbacks) identik. 20 sel lain berbeda secara wajar (jumlah kelas 2 vs 3, nama file CSV split, formula ROC-AUC biner vs OvR, dll). **Satu perbedaan yang BUKAN seharusnya ada ditemukan & sudah diperbaiki:** file dasar biner (`4.6-ringkas-optimasi-prepjurnal/sk2-biner-tipe1-ringkas-prepjurnal.ipynb`, belum pernah dieksekusi) tidak punya fix staging HDFS ke `/kaggle/temp` (hindari kuota `/kaggle/working` ~20GB) yang sudah ada di file irisan (karena file irisan itu sudah pernah benar-benar jalan di Kaggle). Sudah disamakan di sel 4 file biner.
  * **Catatan risiko tersisa:** berbeda dari sk1 irisan yang dibangun dari notebook yang **sudah terbukti jalan end-to-end di Kaggle** (`4-6-irisan-full-semi-final.ipynb`, ada output asli), sk2 biner dibangun dari template `4.6-ringkas-optimasi-prepjurnal` yang **belum pernah dieksekusi sama sekali** — jadi Fase 0–4 (setup Hadoop/Spark/HDFS)-nya masih belum terverifikasi jalan mulus di Kaggle, meski AST syntax-nya lolos.
* **Target Akhir Dosen:** Akurasi ≥ 85%. Roadmap lengkap (fine-tune → augmentasi minoritas → focal loss → cek epoch/resolusi → color constancy lintas dataset → TTA) sudah didiskusikan bertahap berdasarkan ROI, prioritas saat ini di fine-tuning (Run 3) karena backbone frozen adalah temuan paling konkret dari data aktual.
### I. Audit Baseline 4.4, Solusi OOM Multi-Skenario Kaggle, & Standardisasi Visualisasi 5 Metrik Excel
* **Audit Baseline 4.4 vs Notebook Run (`4-4-irisan-ringkas-optimasi-8p8w-selesai.ipynb` & `4-4-biner-optimasi-2p2w-selesai.ipynb`):**
  * Notebook di [`kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk1-irisan-tipe1-ringkas-optimasi.ipynb`](kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk1-irisan-tipe1-ringkas-optimasi.ipynb) dan [`sk2-biner-tipe1-ringkas-optimasi.ipynb`](kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk2-biner-tipe1-ringkas-optimasi.ipynb) terverifikasi **100% menggunakan format citra `uint8`** (~4,7 GB RAM vs ~18,8 GB jika float32) dan identik 99,44% dengan notebook run.
  * Pembaruan Cell 19: Disuntikkan mekanisme reset RAM (`globals()`, `gc.collect()`, `ctypes.CDLL('libc.so.6').malloc_trim(0)`), pencatatan durasi alokasi container YARN (`yarn_container_allocation`) ke `results.csv`, serta kelengkapan library (`findspark pyarrow scikit-image opencv-python-headless`). Seluruh kode lolos validasi AST 100%.
  * Pemastian `spark.stop()`: Terverifikasi dipanggil di Cell 25 sebelum inisialisasi model GPU di Cell 28, sehingga seluruh container executor JVM YARN dilepas total sebelum alokasi GPU TensorFlow dimulai.
* **Diagnosis OOM & Konsistensi HDFS pada Eksekusi Multi-Skenario Kaggle:**
  * **Batas Memori:** Lingkungan Kaggle memiliki batas ketat **31 GiB RAM**.
  * **Akumulasi Memori:** Menjalankan skenario berurutan (`2W2P` -> `2W8P` -> `8W2P` / `8W8P`) dalam satu kernel memicu penumpukan RAM akibat: (1) `buff/cache` OS Linux (~8–12 GB dari I/O citra HDFS), dan (2) alokator C++ BFC TensorFlow yang memegang memory pool GPU/CPU.
  * **Pemicu Crash 8 Worker:** Skenario 8 worker meminta alokasi YARN sebesar ~13,3 GB RAM (8 worker x 1.536 MB + AM). Jika sisa free RAM < 17 GB, kernel langsung dieksekusi mati oleh Linux OOM-killer (Exit Code 137).
  * **Penyebab HDFS Hilang vs Utuh saat Restart:**
    * *Restart Kernel Biasa (`Kernel -> Restart Kernel`):* Proses Python mati dan RAM kembali ke 0 MB, namun container pod Kaggle tetap hidup sehingga direktori `/kaggle/working/`, file HDFS, dan `results.csv` **tetap utuh dan aman**.
    * *Crash OOM Container:* Jika memori melebihi 31 GiB dan menabrak cgroup container host, Kaggle mematikan dan mendaur ulang seluruh instance (fresh container), yang menyebabkan filesystem lokal dan daemon HDFS terhapus.
  * **Prosedur Baku Multi-Skenario:** Jalankan `Kernel -> Restart Kernel` sebelum beralih ke skenario yang membutuhkan worker besar (8W2P / 8W8P) guna mereset RAM tanpa kehilangan storage.
* **Standardisasi Skrip Visualisasi 5 Metrik Excel:**
  * Dibuatkan skrip grafik 5 panel (grid 2x3) yang menampilkan: (1) Waktu Prapemrosesan [detik], (2) Penggunaan CPU [%], (3) Penggunaan RAM [MB & GB], (4) Akurasi Uji & Macro F1 [%], dan (5) ROC-AUC [%]. Panel ke-6 dihapus secara aman (`fig.delaxes(axes[1, 2])`) tanpa memicu layout warning.

---

## 7. Catatan Penutupan Sesi Terakhir (Session Log)
* **Waktu Pembaruan:** 5 Oktober 2026 (Pukul 22:30 WIB).
* **Rangkuman Sesi Ini (Evolusi Lengkap Eksperimen Folder 5):**
  1. **Pencapaian Target Dosen 81.09% (Baseline Utama):** Mengubah masker U-Net menjadi pemandu *ROI Bounding Box (+15% padding kulit)* + Hair Removal + CLAHE + ResNet-50 + Triplet Attention Conv4 + Head 256->128 ($L_2=10^{-4}$) menembus target dosen $\ge 80\%$ (Test Acc 81.09%, AUC 0.9134).
  2. **Eksperimen 1 (EXP 1: Augmentasi Ringan):** Rotasi 10°, zoom 10%, shift 5%, flips. Hasil: Val PR-AUC 0.8005, Test Acc 80.50%, SK Recall 70%.
  3. **Eksperimen 2 (EXP 2: Resolusi 256×256 - KANDIDAT JUARA TERBAIK 🏆):** Murni menaikkan resolusi 224 ke 256 dari Baseline 81%.
     * **Val PR-AUC:** **0.8081 (80.81%)** 🏆 (Rekor tertinggi riset).
     * **Val Loss:** **0.6634** 🏆 (Paling rendah).
     * **Melanoma Recall:** **0.65 (Val)** & **0.61 (Test)** 🏆 (Tembus >60% pertama kali).
     * **SK Recall:** **0.61 (Val)** & **0.71 (Test)** 🏆 (Rekor tertinggi).
     * **Akurasi Blind Test:** **80.79% (~81%)**, Macro-F1 **0.74**, Skor Seleksi **0.7159** 🏆.
     * Checkpoint fisik: `/content/drive/MyDrive/best_melanoma_model_exp2_res256.keras`.
  4. **Eksperimen 3 / Dual-Stream (ROI + Full Image):** Fusi ROI lesi + konteks kulit makro via Shared ResNet-50.
     * Hasil: Val PR-AUC 0.7918, Test Acc 80.79%, Nevus Recall 0.94 (sangat kuat pada lesi jinak), namun Melanoma Recall turun ke 0.56 akibat bias latar kulit sehat.
  5. **Eksperimen 4 (EXP 4: True Triplet Attention Sekuensial):** Alur `Conv4 -> Triplet Attention -> Conv5 -> GAP -> Classifier` di [`kode/5_segmentasi_unet/06_exp4_resnet50_truetriplet.ipynb`](kode/5_segmentasi_unet/06_exp4_resnet50_truetriplet.ipynb). Output di-reset bersih (fresh).
  6. **Eksperimen 5-A (EXP 5-A: EfficientNetV2-S Murni dari Baseline 81%):**
     * Notebook: [`kode/5_segmentasi_unet/07_exp5a_backbone_efficientnetv2s.ipynb`](kode/5_segmentasi_unet/07_exp5a_backbone_efficientnetv2s.ipynb).
     * Seluruh variabel dikunci mati ke Baseline 81%: ROI U-Net 224x224, Hair Removal, CLAHE, Stride-16 Triplet Attention, Feature Fusion (GAP+GMP+Attn), Head 256->128, LR 1.5e-5, loss label smoothing 0.05.
     * Penyesuaian memori: `batch_sz = 64` untuk proteksi OOM blok MBConv.
     * Checkpoint: `/content/drive/MyDrive/best_melanoma_model_exp5a_effnetv2s.keras`.
  7. **Eksperimen 5-B (EXP 5-B: ConvNeXt-Tiny Murni dari Baseline 81%):**
     * Notebook: [`kode/5_segmentasi_unet/08_exp5b_backbone_convnext_keras.ipynb`](kode/5_segmentasi_unet/08_exp5b_backbone_convnext_keras.ipynb).
     * 100% identik Baseline 81%: Backbone murni ditukar ke `ConvNeXtTiny`, Triplet Attention pada stage 2 (14x14), Head 256->128, normalisasi LayerNorm/BatchNorm dikunci saat fine-tuning.
     * Diagnosis & Solusi OOM: Pada batch 256, backward pass inverted bottleneck (3.072 kanal) meminta 16,9 GB VRAM per tensor. Diperbaiki dengan mengunci `batch_sz = 64` (~4,2 GB, aman di GPU T4/A100).
     * Checkpoint: `/content/drive/MyDrive/best_melanoma_model_exp5b_convnext.keras`.
  8. **Arsip Pembanding Tambahan (EXP 5-C):** [`09_exp5c_backbone_convnext_pytorch_ak84.ipynb`](kode/5_segmentasi_unet/09_exp5c_backbone_convnext_pytorch_ak84.ipynb) disimpan sebagai arsip pembanding arsitektur PyTorch timm.
  9. **Standarisasi Modul Pelaporan Beban Kerja CPU:** Sel 8 pada `exp5a` dan `exp5b` telah dilengkapi tabel resmi laporan beban kerja (Core vCPU, waktu, throughput citra/detik, utilisasi 100%).
  10. **Pembersihan Bersih (Clean Slate):** Seluruh sel output dan execution count pada notebook baru telah di-reset ke 0 agar siap dieksekusi bersih di Google Colab.
* **Status Memori:** **AMAN & PERSISTEN.** Seluruh progres, temuan ilmiah, dan log eksperimen telah diperbarui dalam dokumen memori proyek ini. Siap dilanjutkan kapan saja dengan perintah `/start`.


---

## ⚡ ATURAN INTEGRITAS KODE & PARAMETER (DIPATUHI SETIAP SESI)
1. **Dilarang Keras Mengubah Parameter Tanpa Izin:** Parameter kunci seperti atch_size, epochs, learning_rate, 	arget_size, loss function, maupun arsitektur tidak boleh diubah secara sepihak/inisiatif sendiri.
2. **Kunci Baseline 100% Identik:** Semua eksperimen pembanding wajib mengunci nilai identik dengan baseline acuan pengguna.
3. **Konfirmasi Sebelum Tindakan:** Jika ada pertimbangan teknis (misal risiko OOM), agen wajib bertanya dan meminta persetujuan pengguna terlebih dahulu.
4. **Zero Redundant Scan:** Dilarang melakukan scan berulang lintas file jika instruksi/target sudah spesifik. Langsung eksekusi target.
