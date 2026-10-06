# Audit Menyeluruh Notebook PySpark Tipe 1 (Jalur Irisan 3 Kelas)

**Berkas yang diaudit:** `kode/4_Spark_on_Yarn/spark_yarn_tipe1_irisan_ak85.ipynb`
**Tanggal Audit:** 19 September 2026

## 1. Tujuan Audit
Memastikan bahwa notebook PySpark Tipe 1 untuk Jalur Irisan 3 Kelas (`spark_yarn_tipe1_irisan_ak85.ipynb`) **100% bebas dari kebocoran data (data leakage)** dan telah selaras dengan metodologi pembagian data (*Lesion-Aware Stratified Split*) yang telah dipersiapkan sebelumnya, serta tidak lagi menggunakan `train_test_split` acak yang bisa menyebabkan kebocoran lesi pasien.

## 2. Poin-Poin Pengecekan

*   **Pengecekan Penggunaan `train_test_split` Acak:**
    *   **Hasil Pengecekan:** Ditemukan bahwa modul `train_test_split` dari `sklearn.model_selection` **tidak lagi digunakan** dalam notebook ini untuk pembagian set pelatihan dan pengujian.
*   **Pengecekan Pembacaan File Split Resmi:**
    *   **Hasil Pengecekan:** Kode pada cell 78 & 79 secara eksplisit memuat file split resmi:
        *   `dataset_irisan_3kelas_train.csv`
        *   `dataset_irisan_3kelas_val.csv`
        *   `dataset_irisan_3kelas_test.csv`
    *   **Kesimpulan:** Pemisahan telah mengikuti distribusi `StratifiedGroupKFold` berdasarkan `lesion_id` yang telah dipersiapkan pada notebook data prep, menjamin **zero lesion leakage**.
*   **Pengecekan Variabel Lingkungan & Model:**
    *   Skenario irisan sudah diatur dengan variabel dinamis dan konfigurasi yang tepat. Parameter memori, worker, dan konfigurasi HDFS (Phase 1-3) berfungsi sebagaimana mestinya tanpa ada modifikasi data (Phase 5).
*   **Pengecekan Sinkronisasi Jalur Dataset:**
    *   Akses dataset menunjuk pada root dataset irisan yang sama dengan yang dihasilkan di notebook `irisan_mapping improve.ipynb`.

## 3. Kesimpulan Akhir
Notebook `spark_yarn_tipe1_irisan_ak85.ipynb` telah **LOLOS AUDIT**. Notebook ini sudah mengadopsi mekanisme *Anti-Leakage* yang ketat (membaca file split yang terstratifikasi per grup lesi) dan siap dieksekusi di YARN Cluster maupun Single Node (Kaggle/Colab) tanpa ancaman terjadinya kebocoran data validasi/pengujian ke siklus pelatihan.
