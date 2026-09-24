# 🤖 ATURAN KERJA & PROTOKOL SESI AGEN (AGENTS.md)

Dokumen ini adalah aturan otomatis yang wajib ditaati oleh AI/Agen dalam repositori **Data Understanding ISIC & HAM10000**.

---

## ⚡ PROTOKOL KHUSUS PERINTAH PENGGUNA

### 1. Perintah: `/start`
Ketika pengguna mengetik `/start`:
1. **BACA MEMORI UTAMA:** Agen wajib segera membaca file [`CATATAN_MEMORI_PROYEK.md`](CATATAN_MEMORI_PROYEK.md) dan mengidentifikasi:
   * Jalur riset aktif yang dipilih pengguna (misal: Jalur Irisan 7 Kelas).
   * Status terakhir notebook di folder [`kode/`](kode/).
   * Checklist pada Bagian 6 (Actionable Next Steps).
2. **RESTORE KONTEKS & LANGSUNG LANJUT:**
   * Tampilkan ringkasan singkat status terakhir dalam 3–4 poin.
   * **Langsung eksekusi tugas berikutnya** dari titik terakhir tanpa mengulang penjelasan dasar atau memulai dari awal.

---

### 2. Perintah: `/end`
Ketika pengguna mengetik `/end`:
1. **HENTIKAN TUGAS AKTIF DENGAN AMAN:** Pastikan seluruh proses atau komputasi yang sedang berjalan telah selesai atau tersimpan.
2. **PERBARUI MEMORI UTAMA:** Agen wajib memperbarui file [`CATATAN_MEMORI_PROYEK.md`](CATATAN_MEMORI_PROYEK.md):
   * Perbarui tanggal/waktu pada header dokumen.
   * Catat perubahan kode, notebook baru, atau dataset yang baru saja dibuat.
   * Perbarui status checklist tugas berikutnya.
3. **KONFIRMASI PENYIMPANAN:** Tampilkan rekapitulasi pekerjaan yang telah diselesaikan pada sesi ini dan laporkan bahwa memori telah tersimpan aman dan siap dilanjutkan dengan `/start`.

### 3. Aturan Penulisan Kode dan Dokumentasi
Agen wajib mengikuti panduan penulisan teks dan kode di seluruh pengerjaan:
1. **Kalimat Markdown**: Harus singkat, padat, dan jelas (tidak bertele-tele, langsung pada intinya). Jangan menggunakan narasi yang panjang.
2. **Gaya Kode (Code Style)**: Tulis kode layaknya manusia profesional (*human-like*).
3. **Komentar Kode (Comments)**: Harus sangat minimalis (hanya pada baris yang sangat krusial). Biarkan "*code speak for itself*".


### 4. Aturan Pembuatan Laporan Excel
Jika diminta membuat laporan dalam bentuk Excel (.xlsx), agen wajib mengikuti standar desain dan bahasa berikut:
1. **Desain Profesional & Minimalis**: Gunakan tema warna dasar (hitam-putih) atau maksimal 2-3 warna (misal abu-abu terang untuk header tabel). Beri *border* garis hitam tegas pada semua sel yang terisi data. Lebarkan *column width* agar tulisan tidak bertumpuk.
2. **Bahasa Natural (Human-Like)**: Gunakan gaya bahasa Indonesia tingkat menengah yang mudah dipahami (santai namun tetap akademis/profesional). Jangan kaku seperti robot, dan hindari kata asing/istilah rumit sebisa mungkin (contoh: 'Kumpulan Data', 'Tahi Lalat Jinak', bukan 'Dataset' atau 'Melanocytic Nevus' tanpa penjelasan). Kalimat harus langsung pada intinya (*to the point*).
3. **Ekstrak Gambar/Grafik Otomatis**: Jika kode yang dijalankan menghasilkan *plot* grafik (misal dari matplotlib di .ipynb), agen diwajibkan menyedot gambar *base64* dari luaran kode tersebut dan menyisipkannya langsung ke dalam sheet Excel.
