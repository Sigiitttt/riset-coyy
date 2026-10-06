import json
from pathlib import Path

def update_markdowns_in_46():
    # 1. Update sk1-irisan
    p1 = Path("kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk1-irisan-tipe1-ringkas-prepjurnal.ipynb")
    with open(p1, "r", encoding="utf-8") as f:
        nb1 = json.load(f)

    c0_sk1 = """# **SPARK ON YARN - TIPE 1: REKAYASA PRAPEMROSESAN MEDIS & PELATIHAN TERPUSAT GPU**
## **SKENARIO IRISAN 3 KELAS (NEVUS, MELANOMA, SEBORRHEIC KERATOSIS)**
### **Pipeline Terpilih: Aspect Pad & Resize 224x224, Dull Razor Hair Removal, Adaptive Snake Segmentation, & Soft-Blending**

Notebook ini mengimplementasikan pipeline hybrid Big Data Spark on YARN **Tipe 1** yang disempurnakan dengan prapemrosesan citra dermatologi medis terpilih:
1. **Prapemrosesan Terdistribusi (PySpark on YARN Klaster):**
   - **Aspect Pad & Resize (224×224 px):** Menjaga rasio aspek asli lesi via *reflection border padding* agar kriteria klinis asimetri tidak terdistorsi.
   - **Hair Removal (Dull Razor):** Menghilangkan serat rambut menggunakan morfologi *Black-Hat* ($17 \\times 17$) dan *Telea Inpainting* agar permukaan lesi bersih sebelum segmentasi.
   - **Adaptive Active Contour (Snake Model):** Kurva parametrik adaptif (inisialisasi Otsu multi-polaritas) mengunci batas nyata lesi ROI.
   - **Soft-Blending (Alpha Feathering):** Latar belakang diburamkan secara halus untuk memusatkan perhatian CNN pada lesi tanpa menghasilkan artefak garis hitam kaku.
   - **Integritas Warna Murni 100%:** Formula *Contrast Stretching* ditiadakan secara sengaja agar nilai pigmen biologis lesi tetap orisinal sesuai pengamatan dokter.
   - **Format uint8 [0, 255]:** Disimpan kompak sebagai uint8 guna memangkas kuota HDFS dan memori RAM driver hingga 75% (~3,3 GB).
2. **Pelatihan Terpusat (Centralized Deep Learning GPU):**
   - Model AK85 (ResNet-50 + Triplet Attention pada conv4 14×14) dengan input 224×224×3.
   - Generator `BatchSequence` dengan konversi on-the-fly dan augmentasi medis dinamis (rotasi $\\pm 15^\\circ$, flip, variasi kecerahan).
"""
    nb1["cells"][0]["source"] = [l + "\n" for l in c0_sk1.splitlines()]

    c18_sk1 = """## Fase 5 - Preprocessing Terdistribusi PySpark & Sharding HDFS
PySpark RDD membaca citra dari HDFS, membagi beban kerja ke `NUM_PARTITIONS` partisi, mengeksekusi pipeline Pad & Resize 224px, Dull Razor, Active Contour Snake, dan Soft-Blending, lalu menulis shard `.npz` kompak format `uint8` ke HDFS. Throughput CPU dan RAM dicatat otomatis."""
    nb1["cells"][18]["source"] = [l + "\n" for l in c18_sk1.splitlines()]

    with open(p1, "w", encoding="utf-8") as f:
        json.dump(nb1, f, indent=1, ensure_ascii=False)
    print("Updated markdown headers for sk1 in 4.6")

    # 2. Update sk2-biner
    p2 = Path("kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk2-biner-tipe1-ringkas-prepjurnal.ipynb")
    with open(p2, "r", encoding="utf-8") as f:
        nb2 = json.load(f)

    c0_sk2 = """# **SPARK ON YARN - TIPE 1: REKAYASA PRAPEMROSESAN MEDIS & PELATIHAN TERPUSAT GPU**
## **SKENARIO BINER (BENIGN VS MALIGNANT)**
### **Pipeline Terpilih: Aspect Pad & Resize 224x224, Dull Razor Hair Removal, Adaptive Snake Segmentation, & Soft-Blending**

Notebook ini mengimplementasikan pipeline hybrid Big Data Spark on YARN **Tipe 1** yang disempurnakan dengan prapemrosesan citra dermatologi medis terpilih:
1. **Prapemrosesan Terdistribusi (PySpark on YARN Klaster):**
   - **Aspect Pad & Resize (224×224 px):** Menjaga rasio aspek asli lesi via *reflection border padding* agar kriteria klinis asimetri tidak terdistorsi.
   - **Hair Removal (Dull Razor):** Menghilangkan serat rambut menggunakan morfologi *Black-Hat* ($17 \\times 17$) dan *Telea Inpainting* agar permukaan lesi bersih sebelum segmentasi.
   - **Adaptive Active Contour (Snake Model):** Kurva parametrik adaptif (inisialisasi Otsu multi-polaritas) mengunci batas nyata lesi ROI.
   - **Soft-Blending (Alpha Feathering):** Latar belakang diburamkan secara halus untuk memusatkan perhatian CNN pada lesi tanpa menghasilkan artefak garis hitam kaku.
   - **Integritas Warna Murni 100%:** Formula *Contrast Stretching* ditiadakan secara sengaja agar nilai pigmen biologis lesi tetap orisinal sesuai pengamatan dokter.
   - **Format uint8 [0, 255]:** Disimpan kompak sebagai uint8 guna memangkas kuota HDFS dan memori RAM driver hingga 75% (~5,0 GB).
2. **Pelatihan Terpusat (Centralized Deep Learning GPU):**
   - Model AK85 (ResNet-50 + Triplet Attention pada conv4 14×14) dengan input 224×224×3.
   - Generator `BatchSequence` dengan konversi on-the-fly dan augmentasi medis dinamis (rotasi $\\pm 15^\\circ$, flip, variasi kecerahan).
"""
    nb2["cells"][0]["source"] = [l + "\n" for l in c0_sk2.splitlines()]

    c18_sk2 = """## Fase 5 - Preprocessing Terdistribusi PySpark & Sharding HDFS
PySpark RDD membaca citra dari HDFS, membagi beban kerja ke `NUM_PARTITIONS` partisi, mengeksekusi pipeline Pad & Resize 224px, Dull Razor, Active Contour Snake, dan Soft-Blending, lalu menulis shard `.npz` kompak format `uint8` ke HDFS. Throughput CPU dan RAM dicatat otomatis."""
    nb2["cells"][18]["source"] = [l + "\n" for l in c18_sk2.splitlines()]

    with open(p2, "w", encoding="utf-8") as f:
        json.dump(nb2, f, indent=1, ensure_ascii=False)
    print("Updated markdown headers for sk2 in 4.6")

if __name__ == "__main__":
    update_markdowns_in_46()
