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

