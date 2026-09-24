# 📋 Catatan Metodologi Eksperimen: Variabel Pengujian Spark on YARN vs Spark Standalone

Dokumen ini mendokumentasikan klasifikasi variabel penelitian komparasi lingkungan kluster terdistribusi pada klasifikasi citra kanker kulit, sesuai kaidah metodologi ilmiah (*Ceteris Paribus* / Apple-to-Apple).

---

## 1. Variabel Kontrol (Variabel Terkunci)
Seluruh parameter ini **dikunci 100% sama** antara pengujian Spark on YARN (Saya) dan Spark Standalone (Teman) agar performa model dan kualitas data bersifat identik:

| Kategori | Parameter | Nilai / Spesifikasi yang Dikunci |
| :--- | :--- | :--- |
| **Data** | Dataset Sumber | Irisan ISIC & HAM10000 (3 Kelas: NV, MEL, BKL) |
| | Total Citra | **22.051 citra** |
| | Skema Split | **80 : 10 : 10** (*Lesion-Aware Stratified Split*) |
| | Rincian Subset | **Train:** 17.656 citra \| **Val:** 2.192 citra \| **Test:** 2.203 citra |
| **Pipeline Prapemrosesan** | Pra-Resize Staging | 384 × 384 piksel (JPEG Quality 85) sebelum masuk HDFS |
| | Resolusi Target Spark | **224 × 224 piksel** (Bilinear Interpolation) |
| | Format Data & Skala | 3 Channel RGB, tipe `float32`, skala ternormalisasi `[0, 1]` |
| | Format Shard HDFS | **64 citra per file `.npz`** (kunci array: `x`, `y`, `ids`) |
| **Arsitektur Model** | Backbone Base | **ResNet-50** ImageNet (Bobot dibekukan / `trainable=False`) |
| | Penyelarasan Input | `ResNetCaffePreprocess` (RGB $\to$ BGR, dikali 255, kurangi mean Caffe) |
| | Modul Perhatian | **Triplet Attention Module** pada `conv4_block6_out` (14×14×1024) |
| | Head Klasifikasi | Multi-pooling (GAP + GMP + Attn) $\to$ BN $\to$ Dense 512 $\to$ Dense 256 $\to$ Dense 3 |
| **Pelatihan & Evaluasi** | Hyperparameter | Optimizer Adam ($10^{-4}$), Loss `categorical_crossentropy` |
| | Batch & Epoch | Batch Size: **32**, Maksimal Epoch: **15** |
| | Bobot Kelas | `compute_class_weight('balanced')` pada data latih |
| | Batch Generator | Custom `BatchSequence` (Aman dari kebocoran memori Keras 3) |
| | Data Evaluasi | Dievaluasi pada **Test Set murni (2.203 citra)** yang tidak disentuh saat training |
| **Hardware Dasar** | Platform Eksekusi | Kaggle Environment (2× vCPU Intel Xeon, ~30 GB RAM, GPU NVIDIA Tesla T4) |

---

## 2. Variabel Bebas (Variabel Uji / Independen)
Satu-satunya aspek yang **sengaja dibedakan** untuk menguji efisiensi arsitektur pengelolaan sumber daya kluster:

| Parameter Uji | Spark on YARN (Saya) | Spark Standalone (Teman) | Justifikasi Metodologis |
| :--- | :--- | :--- | :--- |
| **Cluster Manager** | **Apache Hadoop YARN** (`spark.master = "yarn"`) | **Spark Standalone** (`spark.master = "spark://localhost:7077"`) | Menguji efisiensi orkestrasi resource manager industri (YARN) vs bawaan Spark (Standalone). |
| **Mekanisme Eksekutor** | Dikelola dalam **YARN Container** oleh NodeManager & ApplicationMaster | Dikelola langsung sebagai proses worker JVM di bawah Spark Master daemon | Meneliti dampak isolasi container YARN terhadap performa komputasi terdistribusi. |
| **Konfigurasi Memori Eksekutor** | 1024 MB heap + 512 MB *memoryOverhead* (Total container 1536 MB) | 1024 MB heap langsung (tanpa overhead container) | Kapasitas heap bersih pemrosesan data **setara (~1 GB)**; overhead 512 MB di YARN adalah syarat batas toleransi container YARN. |
| **Distribusi Engine Spark** | `spark-jars.zip` dikompres dan didistribusikan via HDFS | Dibaca langsung dari instalasi lokal Spark (`$SPARK_HOME/jars`) | Menguji kesiapan deployment pada multi-node sejati (YARN) vs single/shared node (Standalone). |
| **Matriks Skenario Skalabilitas** | Kombinasi Worker ($W \in \{2, 8\}$) dan Partisi ($P \in \{2, 8\}$) | Kombinasi Worker ($W \in \{2, 8\}$) dan Partisi ($P \in \{2, 8\}$) | Menguji *scalability speedup* pada matriks 2W2P, 2W8P, 8W2P, dan 8W8P. |

---

## 3. Variabel Terikat (Variabel Respon / Dependen)
Indikator hasil dan metrik kinerja yang diukur untuk membandingkan kedua lingkungan:

1. **Metrik Komputasi Kluster (Kinerja Distribusi):**
   * **Durasi Prapemrosesan Spark (`elapsed_sec`):** Waktu komputasi pembacaan HDFS, transformasi 224px, dan normalisasi.
   * **Rata-rata Utilisasi CPU (`avg_cpu_percent`):** Beban kerja prosesor selama tahap terdistribusi.
   * **Rata-rata Konsumsi RAM (`avg_mem_mb`):** Footprint memori sistem selama eksekusi kluster.
   * **Throughput:** Jumlah citra yang berhasil diproses per detik (`citra/detik`).

2. **Metrik Model Deep Learning (Validasi Konvergensi):**
   * **Test Accuracy:** Tingkat akurasi prediksi pada 2.203 citra test.
   * **Test Macro F1-Score:** Rata-rata harmonis presisi dan recall per kelas.
   * **Test ROC-AUC (OvR):** Area under curve multi-kelas satu lawan semua.
   * **Durasi Pelatihan GPU:** Waktu penyelesaian 15 epoch di GPU Tesla T4.

---

## 4. Kesimpulan Keabsahan Ilmiah
* Pengujian ini **sah secara kaidah ilmiah (*Apple-to-Apple*)** karena seluruh variabel yang mempengaruhi kualitas model (data, praproses, bobot, arsitektur, evaluasi) telah **dikunci secara mutlak**.
* Perbedaan hasil waktu komputasi murni merepresentasikan **efisiensi arsitektur pengelolaan lingkungan kluster (YARN vs Standalone)**.
