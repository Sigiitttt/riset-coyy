# Rencana Implementasi: Pembuatan Notebook Jalur Irisan (`irisan_mapping.ipynb`)

Sesuai diagram alur [p.text](file:///c:/Users/ARII/Downloads/Data%20Understanding%20Isic%20&%20Ham10k/p.text) dan hasil eksplorasi data di [1-data_understanding_isic.ipynb](file:///c:/Users/ARII/Downloads/Data%20Understanding%20Isic%20&%20Ham10k/kode/1-data_understanding_isic.ipynb), kita akan menyusun rencana untuk membangun notebook **Jalur Irisan**.

```
                        BAGAN ALUR JALUR IRISAN (p.text)
                                       │
                                       ▼
                         Lihat label asli tiap dataset
                                       │
                                       ▼
                         Bandingkan label antar-dataset
                                       │
                                       ▼
                         Cari label yang sama / ekuivalen
                                       │
                                       ▼
                         Verifikasi definisi diagnosis
                                       │
                                       ▼
                                  HARMONISASI
                                       │
                                       ▼
                         Tentukan label standar bersama
                                       │
                                       ▼
                                  AMBIL IRISAN
                     (Kelas yang ada di SELURUH dataset)
                                       │
                                       ▼
                         Hitung jumlah kelas hasil irisan
                                       │
                                 ┌─────┴─────┐
                                 │           │
                                 ▼           ▼
                              2 kelas     >2 kelas
                                 │           │
                                 ▼           ▼
                               BINARY    MULTICLASS (3 KELAS)
                                             │
                                             ▼
                                         DATA SIAP
```

---

## 1. Analisis Perbandingan & Harmonisasi Label Antar-Dataset

Kita menganalisis 3 dataset utama yang digunakan (**HAM10000, ISIC 2017, dan ISIC 2019**):

| Label Standar (Harmonisasi) | Definisi Medis | HAM10000 (7 Kelas) | ISIC 2017 (3 Kelas) | ISIC 2019 (8 Kelas) | Status Irisan (Ada di Seluruh Dataset?) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`NV`** | *Melanocytic Nevus* (Tahi Lalat) | `nv` (6.705) | `nevus` (1.273) | `NV` (12.875) | ✅ **ADA DI KETIGANYA (IRISAN)** |
| **`MEL`** | *Melanoma Maligna* (Kanker Ganas) | `mel` (1.113) | `melanoma` (373) | `MEL` (4.522) | ✅ **ADA DI KETIGANYA (IRISAN)** |
| **`BKL`** | *Benign Keratosis* (Keratosis Seboroik) | `bkl` (1.099) | `seborrheic_keratosis` (384) | `BKL` (2.624) | ✅ **ADA DI KETIGANYA (IRISAN)** |
| **`BCC`** | *Basal Cell Carcinoma* | `bcc` (514) | ❌ Tidak ada | `BCC` (3.323) | ❌ Gugur (Tidak ada di ISIC 2017) |
| **`AKIEC`** | *Actinic Keratosis* | `akiec` (327) | ❌ Tidak ada | `AK` (867) | ❌ Gugur (Tidak ada di ISIC 2017) |
| **`VASC`** | *Vascular Lesion* | `vasc` (142) | ❌ Tidak ada | `VASC` (253) | ❌ Gugur (Tidak ada di ISIC 2017) |
| **`DF`** | *Dermatofibroma* | `df` (115) | ❌ Tidak ada | `DF` (239) | ❌ Gugur (Tidak ada di ISIC 2017) |
| **`SCC`** | *Squamous Cell Carcinoma* | ❌ Tidak ada | ❌ Tidak ada | `SCC` (628) | ❌ Gugur (Hanya ada di ISIC 2019) |

---

## 2. Hasil Ekstraksi Kelas Irisan (Jawaban: Kita Mau Ambil Kelas Apa?)

Sesuai diagram alur `p.text`:
1. **Hasil Irisan (Intersection):**
   * Kelas yang **terdapat pada SELURUH ketiga dataset** tepat menghasilkan **3 KELAS**:
     1. **`NV`** (*Melanocytic Nevus* / Tahi Lalat Jinak)
     2. **`MEL`** (*Melanoma* / Kanker Kulit Ganas)
     3. **`BKL`** (*Benign Keratosis* / Keratosis Seboroik Jinak)
2. **Kategori Hasil Irisan:**
   * Karena jumlah kelas = 3 (yaitu **> 2 kelas**), maka berdasarkan percabangan `p.text`, jalur yang diambil adalah **MULTICLASS (3 KELAS)**!
3. **Kuantitas Data Bersih Hasil Irisan (Bebas Duplikat):**
   * Dari total 27.361 citra bersih unik 3 dataset:
     * **`NV`** : **14.148 citra** (64.2%)
     * **`MEL`** : **4.895 citra** (22.2%)
     * **`BKL`** : **3.008 citra** (13.6%)
   * **Total Dataset Bersih Hasil Irisan:** **22.051 citra** (100% lengkap berlabel di ketiga dataset).

> [!NOTE]
> **Opsi Tambahan (Fleksibilitas Riset):**
> * **Skenario Utama (3 Dataset: HAM10k ∩ ISIC 2017 ∩ ISIC 2019):** Menghasilkan **3 Kelas** (`NV`, `MEL`, `BKL`) total **22.051 citra**.
> * **Skenario Alternatif (2 Dataset: HAM10k ∩ ISIC 2019):** Jika ISIC 2017 tidak diikutkan, irisannya menghasilkan **7 Kelas** (`NV`, `MEL`, `BKL`, `BCC`, `AKIEC`, `VASC`, `DF`) total **26.733 citra**.
> * Notebook akan fokus pada **Skenario Utama (3 Kelas)** sesuai alur 3 dataset, dan menyertakan tabel pembandingnya secara transparan.

---

## 3. Struktur Notebook yang Akan Dibuat

Notebook baru: [`kode/irisan_mapping.ipynb`](file:///c:/Users/ARII/Downloads/Data%20Understanding%20Isic%20&%20Ham10k/kode/irisan_mapping.ipynb) akan disusun ke dalam **8 Langkah Singkat (*Like Human*)**:

1. **Langkah 1 — Setup Folder & Load 3 Dataset Pilihan:**
   - Memuat data fisik dan ground truth dari HAM10000, ISIC 2017, dan ISIC 2019.
2. **Langkah 2 — Deduplikasi Terarah (HAM10000 Basis Utama):**
   - Menghilangkan duplikasi antar dataset (HAM10000 100% utuh, ISIC 2019 sisa 15.316 unik, ISIC 2017 sisa 1.283 unik).
3. **Langkah 3 — Analisis & Komparasi Label Antar-Dataset:**
   - Menampilkan tabel perbandingan label asli dari masing-masing dataset berdampingan.
4. **Langkah 4 — Harmonisasi & Ekuivalensi Definisi Diagnosis Medis:**
   - Memetakan sinonim medis (misal: `seborrheic_keratosis` ≡ `bkl`, `melanoma` ≡ `mel`, `nevus` ≡ `nv`) ke label standar bersama.
5. **Langkah 5 — Pengambilan Irisan (Intersection 3 Dataset):**
   - Mengambil kelas yang terdapat pada seluruh dataset (`NV`, `MEL`, `BKL`).
   - Menghitung jumlah kelas: 3 kelas (`> 2 kelas`) -> Masuk ke jalur **MULTICLASS (3 KELAS)**.
6. **Langkah 6 — Eksekusi Filtering Data & Validasi:**
   - Memfilter dataset hanya pada sampel 3 kelas irisan (22.051 citra).
   - Validasi bahwa tidak ada sampel yang memiliki label kosong atau anomali.
7. **Langkah 7 — Analisis Distribusi & Visualisasi Grafik Batang:**
   - Visualisasi distribusi 3 kelas irisan per dataset dan total gabungan dengan label angka dan persentase yang jelas.
8. **Langkah 8 — DATA SIAP (Simpan Dataset Final Irisan):**
   - Menyimpan metadata final ke `Dataset/dataset_irisan_multiclass_final.csv`.

---

## Verification Plan

### Automated Tests
- Validasi sintaks kode notebook menggunakan `compile(..., 'exec')`.
- Memastikan total baris data hasil irisan tepat berjumlah 22.051 citra unik.
- Memastikan kolom target hanya berisi 3 kelas: `NV`, `MEL`, `BKL`.

### Manual Verification
- Memastikan visualisasi grafik batang memuat angka jumlah dan persentase yang jelas di atas setiap batang.
- Memastikan penjelasan pada tiap langkah singkat, padat, dan manusiawi (*like human*).
