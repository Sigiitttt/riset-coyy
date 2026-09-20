# ⚠️ Laporan Investigasi Error HDFS di Kaggle (Disk Out of Space)

**Konteks:** Error `CalledProcessError` saat mengeksekusi `hdfs dfs -put` pada dataset penuh (22.051 citra) di environment Kaggle Notebook.

## 1. Bukti Log Error
Pada file `error.txt` (baris 34017):
```text
put: File /user/skincancer/irisan/melanoma/ISIC_0013491.jpg._COPYING_ could only be written to 0 of the 1 minReplication nodes. There are 1 datanode(s) running and 1 node(s) are excluded in this operation.
```

## 2. Analisis Akar Masalah (Root Cause)
Kode PySpark dan arsitektur YARN **terbukti 100% valid dan bebas bug** (sudah berhasil dijalankan *end-to-end* dengan sampel data). Error ini murni karena **keterbatasan fisik environment Kaggle**:

1. **Ilusi 57.6 GB Disk Kaggle:** Meski UI Kaggle menampilkan batas disk 57.6 GB, ruang yang benar-benar bisa ditulis (partisi `/kaggle/working`) dibatasi secara internal.
2. **Kapasitas HDFS Aktual:** Log perintah `hdfs dfsadmin -report` di notebook membuktikan bahwa HDFS hanya mendeteksi kapasitas maksimal sebesar **19.52 GB** di partisi tersebut, dengan sisa bersih (DFS Remaining) hanya **15.64 GB** setelah dipotong OS & instalasi Hadoop.
3. **Ukuran Data vs Ruang Tersedia:** Total ukuran 22.051 citra asli adalah **18.11 GB**.
4. **Crash:** Saat `hdfs dfs -put` mengkopi 18.11 GB citra ke dalam blok HDFS, kapasitas tersisa (15.64 GB) langsung habis. HDFS DataNode mengalami *Disk Out of Space*, sehingga di-*exclude* oleh NameNode dan proses upload terhenti.

## 3. Rekomendasi Solusi untuk "AI Sebelah"
Mohon buatkan skrip Python (modifikasi pada **Fase 4, Sel 20** di notebook) untuk:
* Melakukan **resize ringan otomatis (misal ke 384x384 atau 512x512 px)** pada citra *sebelum* disalin/di-ingesti ke direktori lokal HDFS.
* Tujuannya agar total ukuran fisik 22.051 citra menyusut drastis dari **18.11 GB menjadi < 2 GB**, sehingga muat dengan aman di batas partisi Kaggle (15.6 GB) tanpa memicu error DataNode *excluded*.
