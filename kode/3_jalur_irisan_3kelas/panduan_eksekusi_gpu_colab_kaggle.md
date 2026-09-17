# 🚀 Panduan Eksekusi Pelatihan Penuh (*Full Training*) GPU (Colab & Kaggle T4)
**Dataset Irisan 3 Kelas Bebas Kebocoran:** HAM10000 ∩ ISIC 2017 ∩ ISIC 2019 (22.051 Citra)  
**Target Diagnosis Medis:** `NV` (0), `MEL` (1), `BKL` (2)

Dokumen ini adalah panduan praktis untuk mengeksekusi pelatihan deep learning (*Full Training* 10–20 epoch) menggunakan GPU accelerator (Google Colab / Kaggle T4) dengan skrip modular [`train_baseline.py`](train_baseline.py).

---

## ⚙️ Ringkasan Konfigurasi & Variasi Eksperimen

Pipeline mendukung kombinasi arsitektur dan loss function untuk publikasi ilmiah:

| No | Nama Eksperimen | Arsitektur Backbone | Loss Function & Hyperparameter | Tujuan Eksperimen |
|:---|:---|:---|:---|:---|
| 1 | `resnet50_ce` | ResNet-50 | Weighted Cross-Entropy Loss | Baseline standar arsitektur residual |
| 2 | `efficientnet_b0_ce` | EfficientNet-B0 | Weighted Cross-Entropy Loss | Baseline model efisiensi tinggi |
| 3 | `resnet50_focal` | ResNet-50 | Focal Loss ($\gamma=2.0$, Inverse Alpha) | Evaluasi focusing sample sulit & imbalansi |
| 4 | `efficientnet_b0_focal` | EfficientNet-B0 | Focal Loss ($\gamma=2.0$, Inverse Alpha) | Benchmark identik referensi dosen |
| 5 | `resnet50_cb_focal` | ResNet-50 | Class-Balanced Focal Loss ($\gamma=2.0, \beta=0.999$) | Mitigasi imbalansi berbasis Effective Number |
| 6 | `efficientnet_b0_cb_focal` | EfficientNet-B0 | Class-Balanced Focal Loss ($\gamma=2.0, \beta=0.999$) | Benchmark optimal multiskala |

---

## 💡 Opsi A: Menggunakan Notebook Siap Jalan (*One-Click Notebook*) ⭐⭐⭐

Telah disediakan notebook khusus yang dapat langsung dibuka dan dijalankan pada Kaggle maupun Google Colab:
[`kode/3_jalur_irisan_3kelas/eksekusi_full_training_gpu.ipynb`](eksekusi_full_training_gpu.ipynb)

* **Di Kaggle:** Klik **File** $\rightarrow$ **Upload Notebook** $\rightarrow$ Pilih file `eksekusi_full_training_gpu.ipynb`.
  * Tambahkan input dataset: Klik **+ Add Input** di panel kanan $\rightarrow$ Cari dataset `nadiraanindita/skin-lesion-data` $\rightarrow$ Klik **Add**.
  * Aktifkan: **Accelerator: GPU T4 x2** dan **Internet: On**.
  * Jalankan seluruh cell (Run All)! Seluruh indexing citra, training 15 epoch kedua model, evaluasi test set, dan plotting tabel komparasi berjalan otomatis.
* **Di Google Colab:** Buka [Google Colab](https://colab.research.google.com) $\rightarrow$ Klik tab **Upload** $\rightarrow$ Pilih file `eksekusi_full_training_gpu.ipynb`.
  * Ubah runtime: **Runtime** $\rightarrow$ **Change runtime type** $\rightarrow$ **T4 GPU**.
  * Jalankan seluruh cell secara berurutan!

---

## 💻 Opsi B: Menjalankan via Skrip Modular Terminal / Bash

### 1. Di Kaggle Notebook (GPU T4 x2)

1. **Buat Notebook Baru di Kaggle:**
   * Masuk ke [Kaggle](https://www.kaggle.com) $\rightarrow$ Klik **+ Create** $\rightarrow$ **New Notebook**.
   * Di panel kanan (Settings):
     * **Accelerator: GPU T4 x2**
     * **Internet: On**
     * Klik **+ Add Input** $\rightarrow$ Cari `nadiraanindita/skin-lesion-data` $\rightarrow$ Klik **Add**.

2. **Clone Repositori:**
   Jalankan cell pertama:
   ```bash
   !git clone https://github.com/Sigiitttt/riset-coyy.git
   %cd riset-coyy
   ```

3. **Eksekusi Pelatihan EfficientNet-B0 + Focal Loss:**
   ```bash
   !python kode/3_jalur_irisan_3kelas/train_baseline.py \
       --model efficientnet_b0 \
       --loss focal \
       --gamma 2.0 \
       --epochs 15 \
       --batch_size 64 \
       --lr 1e-4 \
       --num_workers 2
   ```

4. **Eksekusi Pelatihan ResNet-50 + Class-Balanced Focal Loss:**
   ```bash
   !python kode/3_jalur_irisan_3kelas/train_baseline.py \
       --model resnet50 \
       --loss cb_focal \
       --gamma 2.0 \
       --beta 0.999 \
       --epochs 15 \
       --batch_size 64 \
       --lr 1e-4 \
       --num_workers 2
   ```

---

### 2. Di Google Colab (GPU T4)

1. Buka [Google Colab](https://colab.research.google.com) $\rightarrow$ Ubah Runtime: **Runtime** $\rightarrow$ **Change runtime type** $\rightarrow$ Pilih **T4 GPU**.
2. Clone repositori riset:
   ```python
   !git clone https://github.com/Sigiitttt/riset-coyy.git
   %cd riset-coyy
   ```
3. Install dependensi (jika diperlukan):
   ```python
   !pip install -q timm torchvision scikit-learn seaborn matplotlib
   ```
4. Jalankan script pelatihan modular langsung:
   ```python
   !python kode/3_jalur_irisan_3kelas/train_baseline.py --model efficientnet_b0 --loss focal --epochs 15 --batch_size 64
   ```

---

## 3. Hasil & Artefak yang Dihasilkan Otomatis

Setiap run secara otomatis menghasilkan:
1. **Model Checkpoint Optimal (`models/best_{model}_{loss}_baseline.pth`):**
   * Disimpan otomatis berdasarkan skor tertinggi *Validation Macro F1-Score* (bukan akurasi bias).
2. **Visualisasi Normalized Confusion Matrix (`models/cm_{model}_{loss}.png`):**
   * Menampilkan evaluasi visual akurat per kelas: `NV`, `MEL` (Sensitivitas kanker ganas), dan `BKL`.
3. **Tabel Rekapitulasi Metrik (`models/baseline_comparison_results.csv`):**
   * Menyimpan metrik lengkap: `Overall Accuracy`, `Balanced Accuracy`, `Macro F1-Score`, `Macro ROC-AUC`, serta `Melanoma Sensitivity` untuk perbandingan langsung pada Bab 4 skripsi/jurnal.
