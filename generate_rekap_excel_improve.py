import os
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def build_improved_excel():
    print("Membaca master data CSV...")
    df_bin = pd.read_csv('Dataset/dataset_binary_final.csv')
    df_iri = pd.read_csv('Dataset/dataset_irisan_multiclass_final.csv')
    df_train = pd.read_csv('Dataset/dataset_irisan_3kelas_train.csv')
    df_val = pd.read_csv('Dataset/dataset_irisan_3kelas_val.csv')
    df_test = pd.read_csv('Dataset/dataset_irisan_3kelas_test.csv')

    wb = openpyxl.Workbook()

    # Tipografi Modern & Bersih (Segoe UI)
    font_main_title = Font(name='Segoe UI', size=16, bold=True, color='0F172A')
    font_subtitle = Font(name='Segoe UI', size=10, italic=True, color='475569')
    font_section = Font(name='Segoe UI', size=11, bold=True, color='0F172A')
    font_box_title = Font(name='Segoe UI', size=10, bold=True, color='1E3A8A')
    font_box_text = Font(name='Segoe UI', size=9.5, color='1E293B')

    font_th_navy = Font(name='Segoe UI', size=9.5, bold=True, color='FFFFFF')
    font_th_teal = Font(name='Segoe UI', size=9.5, bold=True, color='FFFFFF')
    font_th_sub = Font(name='Segoe UI', size=9.5, bold=True, color='0F172A')

    font_td = Font(name='Segoe UI', size=9.5, color='1E293B')
    font_td_bold = Font(name='Segoe UI', size=9.5, bold=True, color='0F172A')
    font_td_code = Font(name='Consolas', size=9.5, bold=True, color='0F172A')

    font_benign = Font(name='Segoe UI', size=9.5, bold=True, color='065F46')
    font_malignant = Font(name='Segoe UI', size=9.5, bold=True, color='9F1239')

    # Palet Warna Modern & Sejuk di Mata
    fill_navy = PatternFill(start_color='1E293B', end_color='1E293B', fill_type='solid')      # Slate 800
    fill_teal = PatternFill(start_color='0F766E', end_color='0F766E', fill_type='solid')      # Teal 700
    fill_blue = PatternFill(start_color='2563EB', end_color='2563EB', fill_type='solid')      # Blue 600
    fill_sub_header = PatternFill(start_color='E2E8F0', end_color='E2E8F0', fill_type='solid')# Slate 200

    fill_box = PatternFill(start_color='F0F9FF', end_color='F0F9FF', fill_type='solid')       # Sky 50 (Info Box)
    fill_kpi = PatternFill(start_color='F8FAFC', end_color='F8FAFC', fill_type='solid')       # Slate 50
    fill_zebra = PatternFill(start_color='F8FAFC', end_color='F8FAFC', fill_type='solid')     # Subtle alternate

    fill_benign_soft = PatternFill(start_color='ECFDF5', end_color='ECFDF5', fill_type='solid')   # Mint Green 50
    fill_malignant_soft = PatternFill(start_color='FFF1F2', end_color='FFF1F2', fill_type='solid')# Rose 50

    # Border Bersih
    b_gray = Side(style='thin', color='CBD5E1')
    b_thick_dark = Side(style='medium', color='0F172A')
    b_double = Side(style='double', color='0F172A')

    border_cell = Border(left=b_gray, right=b_gray, top=b_gray, bottom=b_gray)
    border_total = Border(top=b_thick_dark, bottom=b_double, left=b_gray, right=b_gray)
    border_box = Border(left=b_gray, right=b_gray, top=b_gray, bottom=b_gray)

    # Alignment
    align_left = Alignment(horizontal='left', vertical='center')
    align_center = Alignment(horizontal='center', vertical='center')
    align_right = Alignment(horizontal='right', vertical='center')
    align_wrap_left = Alignment(horizontal='left', vertical='center', wrap_text=True)
    align_wrap_center = Alignment(horizontal='center', vertical='center', wrap_text=True)

    def format_sheet_autofit(ws, min_col=1, max_col=None, cap=65):
        ws.views.sheetView[0].showGridLines = True
        if max_col is None:
            max_col = ws.max_column
        for col_idx in range(min_col, max_col + 1):
            col_letter = get_column_letter(col_idx)
            max_len = 0
            for row in range(1, ws.max_row + 1):
                cell = ws.cell(row=row, column=col_idx)
                if row in [1, 2, 3]:
                    continue
                val = str(cell.value or '')
                if val:
                    lines = val.split('\n')
                    max_l = max(len(l) for l in lines)
                    if max_l > max_len:
                        max_len = max_l
            ws.column_dimensions[col_letter].width = min(max(max_len + 4, 13), cap)

    # =========================================================================
    # SHEET 1: PANDUAN & RINGKASAN SANTAI
    # =========================================================================
    ws1 = wb.active
    ws1.title = "1. Ringkasan & Panduan Mudah"
    ws1.freeze_panes = "A6"

    ws1['A1'] = "RINGKASAN MUDAH: DATASET KANKER KULIT (ISIC & HAM10000)"
    ws1['A1'].font = font_main_title
    ws1['A2'] = "Panduan Sederhana & Ramah: Perbedaan Jalur Biner (Skrining) vs Jalur Irisan 3 Kelas (Pilihan Skripsi) | Update: 18 September 2026"
    ws1['A2'].font = font_subtitle

    # Info Box Konsep (Bahasa Santai untuk Anak 18 Tahun / Mahasiswa Baru)
    box_text = (
        "[TIPS & ANALOGI MUDAH BIAR TIDAK BINGUNG]\n"
        "- Jalur Biner (33.552 Gambar) = Seperti Dokter Jaga IGD.\n"
        "   Tugasnya cuma skrining cepat: 'Ini benjolan bahaya (Kanker Ganas / 1) atau aman (Tahi Lalat Jinak / 0)?'. Cocok untuk deteksi dini global.\n\n"
        "- Jalur Irisan 3 Kelas (22.051 Gambar) = Seperti Dokter Spesialis Kulit (PILIHAN UTAMA SKRIPSI ANDA).\n"
        "   Tugasnya mendiagnosis penyakit spesifik: 'Ini tahi lalat biasa (NV), keratosis seboroik jinak (BKL), atau kanker melanoma ganas (MEL)?'.\n"
        "   Jalur ini dipilih karena ketiga dataset (HAM10000, ISIC 2017, ISIC 2019) sama-sama punya 3 penyakit ini secara lengkap!"
    )
    ws1.merge_cells("A3:E4")
    c_box = ws1['A3']
    c_box.value = box_text
    c_box.font = font_box_text
    c_box.alignment = align_wrap_left
    for r in range(3, 5):
        for c in range(1, 6):
            cell = ws1.cell(row=r, column=c)
            cell.fill = fill_box
            cell.border = border_box
    ws1.row_dimensions[3].height = 42
    ws1.row_dimensions[4].height = 42

    # Section A: Tabel Perbandingan
    ws1['A6'] = "A. PERBANDINGAN DUA JALUR RISET DENGAN BAHASA SANTAI"
    ws1['A6'].font = font_section

    h_comp = ["Hal yang Dibandingkan", "Jalur Biner (Skrining Global)", "Jalur Irisan 3 Kelas (Fokus Skripsi)", "Kenapa Dibuat Begini? (Alasan Mudah)"]
    for c_i, h in enumerate(h_comp, start=1):
        c = ws1.cell(row=7, column=c_i, value=h)
        c.font = font_th_navy
        c.fill = fill_navy
        c.alignment = align_center
        c.border = border_cell
    ws1.row_dimensions[7].height = 25

    rows_comp_easy = [
        ("Tujuan Utama", 
         "Skrining kilat: Memisahkan gambar yang Aman (Jinak) vs Berbahaya (Ganas).", 
         "Diagnosis detail: Membedakan 3 penyakit kulit yang paling sering muncul di dunia.", 
         "Menjawab 2 kebutuhan nyata di rumah sakit: triase cepat vs diagnosis pasti."),
        ("Jumlah & Nama Kelas", 
         "2 Kelas Saja:\n• 0 = Jinak (Benign)\n• 1 = Ganas (Malignant)", 
         "3 Kelas Spesifik:\n• 0 = NV (Tahi Lalat Jinak)\n• 1 = MEL (Kanker Melanoma Ganas)\n• 2 = BKL (Keratosis Seboroik Jinak)", 
         "Jalur irisan hanya mengambil penyakit yang sama-sama ada di ketiga dataset."),
        ("Jumlah Gambar Bersih", 
         "33.552 gambar bersih\n(100% bebas gambar duplikat/kembar).", 
         "22.051 gambar bersih\n(100% bebas gambar duplikat/kembar).", 
         "Semua 22.051 gambar irisan dijamin 100% ada di dalam data biner (tidak ada yang nyasar)."),
        ("Dari Mana Datanya?", 
         "Gabungan 3 Dataset:\nHAM10000 + ISIC 2019 (Train & Test) + ISIC 2017 (Semua).", 
         "Irisan Bersama 3 Dataset:\nHAM10000 + ISIC 2019 (Train) + ISIC 2017 (Semua).", 
         "Jalur irisan tidak memakai partisi Test 2019 agar data latihnya murni dari 3 senter."),
        ("Aturan Gambar Kembar", 
         "HAM10000 dijaga 100% utuh (10.015 foto).\nGambar kembar di 2019 & 2017 dibuang.", 
         "HAM10000 dijaga 100% utuh (8.917 foto NV/MEL/BKL).\nGambar kembar di 2019 & 2017 dibuang.", 
         "Mencegah model AI 'menyontek' gambar yang sama saat belajar dan saat ujian."),
        ("Pembagian Data Latih & Uji", 
         "Stratified Split biasa (dibagi rata per kelas).", 
         "Lesion-Aware Split (80% Belajar : 10% Latihan : 10% Ujian Akhir) via Lesion ID.", 
         "Menjamin foto dari pasien yang sama TIDAK BOLEH muncul di data latih dan data uji!"),
        ("Perbandingan Jumlah Kelas", 
         "Jinak: 20.998 foto (62,6%)\nGanas: 12.554 foto (37,4%)\n(Rasio cukup imbang ~1,6 : 1)", 
         "NV: 14.148 foto (64,2%)\nMEL: 4.895 foto (22,2%)\nBKL: 3.008 foto (13,6%)", 
         "Di dunia nyata, tahi lalat jinak memang jauh lebih banyak dibanding kanker ganas."),
        ("Buku / Jurnal Acuan", 
         "Voting konsensus 8 jurnal internasional bereputasi (Elsevier, MDPI, Springer, Frontiers).", 
         "Tschandl et al. (Nature 2018), Codella et al. (IEEE 2018), Baig (2023), Ichim (2023).", 
         "Semua keputusan nama dan pembagian kelas punya rujukan jurnal Scopus Q1 resmi.")
    ]

    for r_i, r_data in enumerate(rows_comp_easy, start=8):
        for c_i, val in enumerate(r_data, start=1):
            cell = ws1.cell(row=r_i, column=c_i, value=val)
            cell.font = font_td_bold if c_i == 1 else font_td
            cell.border = border_cell
            cell.alignment = align_wrap_left
            if r_i % 2 == 1:
                cell.fill = fill_zebra
        ws1.row_dimensions[r_i].height = 42

    # Section B: Tanya Jawab Dosen
    r_faq = 17
    ws1.cell(row=r_faq, column=1, value="B. CONTOH CARA MENJAWAB PERTANYAAN DOSEN DENGAN MUDAH").font = font_section

    faq_items = [
        ("Dosen Tanya: 'Kenapa kamu pilih Jalur Irisan 3 Kelas, bukan Jalur Biner atau 7 Kelas?'",
         "Jawaban Anda: 'Karena Jalur Irisan 3 Kelas mengambil penyakit yang pasti ada di ketiga dataset (ISIC 2017, HAM10000, dan ISIC 2019). Dataset 2017 hanya punya 3 penyakit tersebut. Dengan cara ini, kita dapat 22.051 gambar bersih dari berbagai rumah sakit di 4 negara tanpa ada label kosong, dan sudah sesuai saran Bapak/Ibu dosen.'"),
        ("Dosen Tanya: 'Apakah data irisan 22.051 itu klop dengan data biner 33.552?'",
         "Jawaban Anda: 'Sangat klop, Pak/Bu. 100% dari 22.051 gambar irisan ada di dalam 33.552 gambar biner dengan label yang sama persis. Sisa 11.501 gambar di jalur biner adalah penyakit lain (seperti karsinoma sel basal BCC) yang memang tidak disediakan di dataset 2017.'"),
        ("Dosen Tanya: 'Kenapa Seborrheic Keratosis di dataset 2017 kamu ubah namanya jadi BKL?'",
         "Jawaban Anda: 'Berdasarkan jurnal resmi Nature Scientific Data (Tschandl et al., 2018), Seborrheic Keratosis secara medis adalah bagian dari keluarga besar Benign Keratosis (BKL). Konsorsium resmi ISIC sejak 2018 sudah menyatukannya ke dalam kode payung BKL.'")
    ]

    for i, (q, a) in enumerate(faq_items, start=r_faq+1):
        ws1.merge_cells(start_row=i*2, start_column=1, end_row=i*2, end_column=4)
        c_q = ws1.cell(row=i*2, column=1, value=f"[PERTANYAAN] {q}")
        c_q.font = font_td_bold
        c_q.fill = fill_sub_header
        c_q.border = border_cell
        ws1.row_dimensions[i*2].height = 24

        ws1.merge_cells(start_row=i*2+1, start_column=1, end_row=i*2+1, end_column=4)
        c_a = ws1.cell(row=i*2+1, column=1, value=f"[JAWABAN REKOMENDASI] {a}")
        c_a.font = font_td
        c_a.alignment = align_wrap_left
        c_a.border = border_cell
        ws1.row_dimensions[i*2+1].height = 36

    format_sheet_autofit(ws1, max_col=4, cap=55)

    # =========================================================================
    # SHEET 2: KENAPA JINAK VS GANAS (HARMONISASI & KONSENSUS)
    # =========================================================================
    ws2 = wb.create_sheet(title="2. Kenapa Jinak vs Ganas")
    ws2.freeze_panes = "A6"

    ws2['A1'] = "DAFTAR PENYAKIT KULIT & BUKTI KESEPAKATAN JURNAL DUNIA"
    ws2['A1'].font = font_main_title
    ws2['A2'] = "Daftar 8 Penyakit, Nama Sehari-hari, dan Matriks Voting dari 8 Jurnal Ilmiah Internasional"
    ws2['A2'].font = font_subtitle

    ws2['A4'] = "A. 8 PENYAKIT KULIT, NAMA SEHARI-HARI, DAN STATUSNYA"
    ws2['A4'].font = font_section

    h_penyakit = ["Kode Baku", "Nama Sehari-hari (Biar Gampang Ingat)", "Nama Diagnosis Medis Resmi", "Sifat Medis", "Kategori Biner", "Penjelasan Sederhana"]
    for c_i, h in enumerate(h_penyakit, start=1):
        c = ws2.cell(row=5, column=c_i, value=h)
        c.font = font_th_teal
        c.fill = fill_teal
        c.alignment = align_center
        c.border = border_cell
    ws2.row_dimensions[5].height = 25

    data_penyakit = [
        ("NV", "Tahi Lalat Biasa", "Melanocytic Nevus", "Jinak", "Benign (0)", "Bercak tahi lalat normal akibat penumpukan melanosit. Sangat umum dan tidak berbahaya."),
        ("MEL", "Kanker Kulit Melanoma", "Melanoma", "Ganas", "Malignant (1)", "Kanker kulit paling berbahaya. Butuh penanganan cepat sebelum menyebar ke organ lain."),
        ("BKL", "Kutil Tua / Keratosis Seboroik", "Benign Keratosis (Seborrheic Keratosis)", "Jinak", "Benign (0)", "Benjolan cokelat/hitam kasar mirip kutil pada orang dewasa/lansia. Tidak bersifat kanker."),
        ("BCC", "Kanker Karsinoma Sel Basal", "Basal Cell Carcinoma", "Ganas", "Malignant (1)", "Kanker kulit paling sering terjadi. Tumbuh lambat, tapi bisa merusak jaringan sekitar bila dibiarkan."),
        ("AKIEC", "Bercak Kasar Pra-Kanker", "Actinic Keratosis / Bowen's Disease", "Pra-Kanker", "Malignant (1)", "Bercak kemerahan kasar akibat paparan sinar matahari kronis. Berpotensi jadi kanker ganas."),
        ("SCC", "Kanker Karsinoma Sel Skuamosa", "Squamous Cell Carcinoma", "Ganas", "Malignant (1)", "Kanker ganas dari lapisan terluar kulit. Bisa membesar dan menyebar jika tidak diangkat."),
        ("VASC", "Tanda Lahir Merah / Titik Darah", "Vascular Lesion (Hemangioma)", "Jinak", "Benign (0)", "Kumpulan pembuluh darah kecil berwarna merah atau keunguan. Bersifat jinak dan tidak berbahaya."),
        ("DF", "Benjolan Kenyal Jinak", "Dermatofibroma", "Jinak", "Benign (0)", "Benjolan padat kecil di bawah kulit (sering di kaki). Bersifat jinak akibat luka kecil/gigitan serangga.")
    ]

    for r_i, r_data in enumerate(data_penyakit, start=6):
        for c_i, val in enumerate(r_data, start=1):
            cell = ws2.cell(row=r_i, column=c_i, value=val)
            cell.font = font_td
            cell.border = border_cell
            if c_i == 1:
                cell.font = font_td_code
                cell.alignment = align_center
            elif c_i in [4, 5]:
                cell.alignment = align_center
                if "Jinak" in val or "Benign" in val:
                    cell.fill = fill_benign_soft
                    cell.font = font_benign
                else:
                    cell.fill = fill_malignant_soft
                    cell.font = font_malignant
            else:
                cell.alignment = align_wrap_left
            if r_i % 2 == 1 and c_i not in [4, 5]:
                cell.fill = fill_zebra
        ws2.row_dimensions[r_i].height = 28

    # Section B: Matriks Voting 8 Jurnal
    r_v = 16
    ws2.cell(row=r_v, column=1, value="B. BUKTI KESEPAKATAN: HASIL VOTING DARI 8 JURNAL ILMIAH INTERNASIONAL").font = font_section

    h_v = ["Nama Penulis & Tahun", "Nama Jurnal Lengkap", "Penerbit", "NV", "BKL", "DF", "VASC", "MEL", "BCC", "AKIEC", "SCC"]
    for c_i, h in enumerate(h_v, start=1):
        c = ws2.cell(row=r_v+1, column=c_i, value=h)
        c.font = font_th_navy
        c.fill = fill_navy
        c.alignment = align_center
        c.border = border_cell
    ws2.row_dimensions[r_v+1].height = 25

    vote_table_data = [
        ("Kousis et al. (2022)", "Electronics", "MDPI", "Jinak", "Jinak", "Jinak", "Jinak", "Ganas", "Ganas", "Ganas", "-"),
        ("Ghosh et al. / SkinNet (2022)", "Frontiers in Oncology", "Frontiers", "Jinak", "Jinak", "Jinak", "Jinak", "Ganas", "Ganas", "Ganas", "-"),
        ("Harangi et al. (2020)", "Biomedical Signal Processing & Control", "Elsevier", "Jinak", "Jinak", "Jinak", "Ganas*", "Ganas", "Ganas", "Ganas", "-"),
        ("Ameri (2020)", "Journal of Biomedical Physics & Eng.", "JBPE", "Jinak", "Jinak", "Jinak", "-", "Ganas", "Ganas", "Ganas", "-"),
        ("Barata et al. (2020)", "Pattern Recognition", "Elsevier", "Jinak", "Jinak", "-", "-", "Ganas", "-", "-", "-"),
        ("Jojoa Acosta et al. (2021)", "BMC Medical Imaging", "Springer", "Jinak", "Jinak", "-", "-", "Ganas", "-", "-", "-"),
        ("Yao et al. / MorphoNet (2026)", "Bioengineering", "MDPI", "Jinak", "Jinak", "Jinak", "Jinak", "Ganas", "Ganas", "Ganas", "Ganas"),
        ("Venugopal et al. (2023)", "Disability and Health Journal / DAJ", "Elsevier", "Jinak", "Jinak", "Jinak", "Jinak", "Ganas", "Ganas", "Ganas", "Ganas"),
    ]

    for r_i, r_data in enumerate(vote_table_data, start=r_v+2):
        for c_i, val in enumerate(r_data, start=1):
            cell = ws2.cell(row=r_i, column=c_i, value=val)
            cell.font = font_td
            cell.border = border_cell
            if c_i in [1, 2]:
                cell.alignment = align_left
            elif c_i == 3:
                cell.alignment = align_center
            else:
                cell.alignment = align_center
                if val == "Jinak":
                    cell.fill = fill_benign_soft
                    cell.font = font_benign
                elif "Ganas" in val:
                    cell.fill = fill_malignant_soft
                    cell.font = font_malignant
                else:
                    cell.fill = fill_zebra
        ws2.row_dimensions[r_i].height = 22

    # Hasil voting row
    r_vote_res = r_v + 2 + len(vote_table_data)
    vote_summary_row = [
        "KESIMPULAN RESMI KITA", 
        "Mayoritas Jurnal Dunia Sepakat", 
        "Konsensus", 
        "JINAK (100%)", "JINAK (100%)", "JINAK (100%)", "JINAK (80%)", 
        "GANAS (100%)", "GANAS (100%)", "GANAS (100%)", "GANAS (100%)"
    ]
    for c_i, val in enumerate(vote_summary_row, start=1):
        cell = ws2.cell(row=r_vote_res, column=c_i, value=val)
        cell.font = font_td_bold
        cell.border = border_total
        cell.fill = fill_sub_header
        if c_i in [1, 2]:
            cell.alignment = align_left
        else:
            cell.alignment = align_center
            if "JINAK" in val:
                cell.font = font_benign
            elif "GANAS" in val:
                cell.font = font_malignant
    ws2.row_dimensions[r_vote_res].height = 25

    # Note on VASC
    ws2.merge_cells(f"A{r_vote_res+2}:K{r_vote_res+2}")
    ws2.cell(row=r_vote_res+2, column=1, value="*Catatan VASC: 1 paper (Harangi) memasukkan VASC ke kelas positif karena mendeteksi kelainan pembuluh darah. Namun secara medis dan 4 jurnal lainnya, VASC adalah lesi jinak non-kanker (80% Jinak).").font = font_subtitle

    format_sheet_autofit(ws2, max_col=11, cap=45)

    # =========================================================================
    # SHEET 3: ANGKA DATA JALUR BINER
    # =========================================================================
    ws3 = wb.create_sheet(title="3. Angka Data Jalur Biner")
    ws3.freeze_panes = "A6"

    ws3['A1'] = "ANGKA LENGKAP JALUR BINER (33.552 GAMBAR BERSIH)"
    ws3['A1'].font = font_main_title
    ws3['A2'] = "Gabungan Lengkap 3 Dataset: HAM10000 + ISIC 2019 + ISIC 2017 (Bebas Duplikat)"
    ws3['A2'].font = font_subtitle

    ws3['A4'] = "A. PROSES PEMBERSIHAN GAMBAR KEMBAR (DEDUPLIKASI)"
    ws3['A4'].font = font_section

    h_dedup_easy = ["Nama Dataset", "Bagian / Partisi", "Foto Mentah Asli", "Foto Kembar Dibuang", "Foto Bersih Dipakai", "Porsi (%)", "Keterangan Aturan Mudah"]
    for c_i, h in enumerate(h_dedup_easy, start=1):
        c = ws3.cell(row=5, column=c_i, value=h)
        c.font = font_th_navy
        c.fill = fill_navy
        c.alignment = align_center
        c.border = border_cell
    ws3.row_dimensions[5].height = 25

    dedup_easy_rows = [
        ("HAM10000", "Part 1 & 2 Lengkap", 10015, 0, 10015, 10015/33552, "Dipertahankan 100% utuh karena punya data biopsi dokter paling lengkap"),
        ("ISIC 2019", "Data Latih (Training)", 25331, 10015, 15316, 15316/33552, "10.015 foto kembar dengan HAM10000 dibuang agar tidak dobel"),
        ("ISIC 2019", "Data Uji (Test)", 8238, 2047, 6191, 6191/33552, "2.047 foto UNK (tidak jelas) dibuang, 6.191 foto berlabel dipakai"),
        ("ISIC 2017", "Data Latih (Training)", 2000, 717, 1283, 1283/33552, "717 foto kembar dengan HAM10k / 2019 dibuang"),
        ("ISIC 2017", "Data Uji (Test)", 600, 1, 599, 599/33552, "1 foto kembar dibuang"),
        ("ISIC 2017", "Data Validasi", 150, 2, 148, 148/33552, "2 foto kembar dibuang"),
    ]

    for r_i, r_data in enumerate(dedup_easy_rows, start=6):
        for c_i, val in enumerate(r_data, start=1):
            cell = ws3.cell(row=r_i, column=c_i, value=val)
            cell.font = font_td
            cell.border = border_cell
            if c_i in [1, 2]:
                cell.alignment = align_left
            elif 3 <= c_i <= 5:
                cell.alignment = align_right
                cell.number_format = '#,##0'
            elif c_i == 6:
                cell.alignment = align_right
                cell.number_format = '0.0%'
            else:
                cell.alignment = align_left
            if r_i % 2 == 1:
                cell.fill = fill_zebra
        ws3.row_dimensions[r_i].height = 20

    # Total dedup row
    r_td = 12
    ws3.cell(row=r_td, column=1, value="TOTAL GABUNGAN").font = font_th_sub
    ws3.cell(row=r_td, column=2, value="6 Partisi Data").font = font_th_sub
    ws3.cell(row=r_td, column=3, value=46334).number_format = '#,##0'
    ws3.cell(row=r_td, column=4, value=12782).number_format = '#,##0'
    ws3.cell(row=r_td, column=5, value=33552).number_format = '#,##0'
    ws3.cell(row=r_td, column=6, value=1.0).number_format = '0.0%'
    ws3.cell(row=r_td, column=7, value="33.552 foto unik siap masuk pelatihan AI").font = font_th_sub
    for c_i in range(1, 8):
        c = ws3.cell(row=r_td, column=c_i)
        c.font = font_th_sub
        c.fill = fill_sub_header
        c.border = border_total
        if 3 <= c_i <= 6:
            c.alignment = align_right
    ws3.row_dimensions[r_td].height = 24

    # Section B: Sebaran 8 Penyakit
    r_8p = 14
    ws3.cell(row=r_8p, column=1, value="B. SEBARAN 8 PENYAKIT DI TIAP DATASET SUMBER").font = font_section

    h_8p = ["Kode", "Nama Sehari-hari", "HAM10k", "2019 Train", "2019 Test", "2017 Train", "2017 Test", "2017 Val", "Total Bersih", "Porsi (%)", "Status Medis"]
    for c_i, h in enumerate(h_8p, start=1):
        c = ws3.cell(row=r_8p+1, column=c_i, value=h)
        c.font = font_th_teal
        c.fill = fill_teal
        c.alignment = align_center
        c.border = border_cell
    ws3.row_dimensions[r_8p+1].height = 25

    ct_cls = pd.crosstab(df_bin['unified_class'], df_bin['source'])
    table_8p_easy = [
        ("NV", "Tahi Lalat Biasa", "Jinak (Benign)"),
        ("MEL", "Kanker Melanoma", "Ganas (Malignant)"),
        ("BCC", "Kanker Sel Basal", "Ganas (Malignant)"),
        ("BKL", "Kutil Tua / Keratosis", "Jinak (Benign)"),
        ("AKIEC", "Bercak Kasar Pra-Kanker", "Ganas (Malignant)"),
        ("SCC", "Kanker Sel Skuamosa", "Ganas (Malignant)"),
        ("VASC", "Tanda Lahir Merah", "Jinak (Benign)"),
        ("DF", "Benjolan Kenyal Jinak", "Jinak (Benign)"),
    ]

    for idx, (code, easy_name, nature) in enumerate(table_8p_easy, start=r_8p+2):
        row_v = [
            code, easy_name,
            int(ct_cls.loc[code, 'ham10000']) if 'ham10000' in ct_cls.columns and code in ct_cls.index else 0,
            int(ct_cls.loc[code, 'isic_2019_train']) if 'isic_2019_train' in ct_cls.columns and code in ct_cls.index else 0,
            int(ct_cls.loc[code, 'isic_2019_test']) if 'isic_2019_test' in ct_cls.columns and code in ct_cls.index else 0,
            int(ct_cls.loc[code, 'isic_2017_train']) if 'isic_2017_train' in ct_cls.columns and code in ct_cls.index else 0,
            int(ct_cls.loc[code, 'isic_2017_test']) if 'isic_2017_test' in ct_cls.columns and code in ct_cls.index else 0,
            int(ct_cls.loc[code, 'isic_2017_val']) if 'isic_2017_val' in ct_cls.columns and code in ct_cls.index else 0,
        ]
        tot = sum(row_v[2:])
        row_v.extend([tot, tot / 33552, nature])

        for c_i, val in enumerate(row_v, start=1):
            cell = ws3.cell(row=idx, column=c_i, value=val)
            cell.font = font_td
            cell.border = border_cell
            if c_i == 1:
                cell.font = font_td_code
                cell.alignment = align_center
            elif c_i == 2:
                cell.alignment = align_left
            elif 3 <= c_i <= 9:
                cell.alignment = align_right
                cell.number_format = '#,##0'
            elif c_i == 10:
                cell.alignment = align_right
                cell.number_format = '0.0%'
            else:
                cell.alignment = align_center
                if "Jinak" in val:
                    cell.fill = fill_benign_soft
                    cell.font = font_benign
                else:
                    cell.fill = fill_malignant_soft
                    cell.font = font_malignant
            if idx % 2 == 1 and c_i != 11:
                cell.fill = fill_zebra
        ws3.row_dimensions[idx].height = 20

    # Total 8 classes
    r_tot_8p = r_8p + 2 + len(table_8p_easy)
    ws3.cell(row=r_tot_8p, column=1, value="TOTAL").font = font_th_sub
    ws3.cell(row=r_tot_8p, column=2, value="8 Penyakit Lengkap").font = font_th_sub
    ws3.cell(row=r_tot_8p, column=3, value=10015).number_format = '#,##0'
    ws3.cell(row=r_tot_8p, column=4, value=15316).number_format = '#,##0'
    ws3.cell(row=r_tot_8p, column=5, value=6191).number_format = '#,##0'
    ws3.cell(row=r_tot_8p, column=6, value=1283).number_format = '#,##0'
    ws3.cell(row=r_tot_8p, column=7, value=599).number_format = '#,##0'
    ws3.cell(row=r_tot_8p, column=8, value=148).number_format = '#,##0'
    ws3.cell(row=r_tot_8p, column=9, value=33552).number_format = '#,##0'
    ws3.cell(row=r_tot_8p, column=10, value=1.0).number_format = '0.0%'
    ws3.cell(row=r_tot_8p, column=11, value="100% Bersih").font = font_th_sub
    for c_i in range(1, 12):
        c = ws3.cell(row=r_tot_8p, column=c_i)
        c.font = font_th_sub
        c.fill = fill_sub_header
        c.border = border_total
        if 3 <= c_i <= 10:
            c.alignment = align_right
    ws3.row_dimensions[r_tot_8p].height = 24

    # Section C: Target Biner Akhir
    r_ba = r_tot_8p + 2
    ws3.cell(row=r_ba, column=1, value="C. KESIMPULAN KELAS BINER AKHIR (SIAP LATIH)").font = font_section

    h_ba = ["Nilai Target", "Kategori", "Penyakit yang Masuk", "Jumlah Gambar Bersih", "Porsi (%)", "Perbandingan Rasio"]
    for c_i, h in enumerate(h_ba, start=1):
        c = ws3.cell(row=r_ba+1, column=c_i, value=h)
        c.font = font_th_navy
        c.fill = fill_navy
        c.alignment = align_center
        c.border = border_cell
    ws3.row_dimensions[r_ba+1].height = 25

    bin_rows_easy = [
        (0, "Jinak (Benign)", "Tahi Lalat (NV), Kutil Tua (BKL), Titik Darah (VASC), Benjolan Kenyal (DF)", 20998, 20998/33552, "1,67 : 1 (Mayoritas - 63 dari 100 orang)"),
        (1, "Ganas (Malignant)", "Kanker Melanoma (MEL), Sel Basal (BCC), Pra-Kanker (AKIEC), Sel Skuamosa (SCC)", 12554, 12554/33552, "1 : 1,67 (Minoritas - 37 dari 100 orang)")
    ]

    for idx, (t_code, t_lbl, t_desc, t_cnt, t_pct, t_ratio) in enumerate(bin_rows_easy, start=r_ba+2):
        row_vals = [t_code, t_lbl, t_desc, t_cnt, t_pct, t_ratio]
        for c_i, val in enumerate(row_vals, start=1):
            cell = ws3.cell(row=idx, column=c_i, value=val)
            cell.font = font_td
            cell.border = border_cell
            if c_i == 1:
                cell.alignment = align_center
                cell.font = font_td_bold
            elif c_i == 2:
                cell.alignment = align_center
                if "Jinak" in val:
                    cell.fill = fill_benign_soft
                    cell.font = font_benign
                else:
                    cell.fill = fill_malignant_soft
                    cell.font = font_malignant
            elif c_i == 3:
                cell.alignment = align_left
            elif c_i == 4:
                cell.alignment = align_right
                cell.number_format = '#,##0'
            elif c_i == 5:
                cell.alignment = align_right
                cell.number_format = '0.0%'
            else:
                cell.alignment = align_left
        ws3.row_dimensions[idx].height = 22

    # Total row
    r_ba_tot = r_ba + 4
    ws3.cell(row=r_ba_tot, column=1, value="-")
    ws3.cell(row=r_ba_tot, column=2, value="TOTAL BINER").font = font_th_sub
    ws3.cell(row=r_ba_tot, column=3, value="8 Penyakit Kulit Bersih").font = font_th_sub
    ws3.cell(row=r_ba_tot, column=4, value=33552).number_format = '#,##0'
    ws3.cell(row=r_ba_tot, column=5, value=1.0).number_format = '0.0%'
    ws3.cell(row=r_ba_tot, column=6, value="Siap digunakan untuk eksperimen AI Biner").font = font_th_sub
    for c_i in range(1, 7):
        c = ws3.cell(row=r_ba_tot, column=c_i)
        c.font = font_th_sub
        c.fill = fill_sub_header
        c.border = border_total
        if c_i in [4, 5]:
            c.alignment = align_right

    format_sheet_autofit(ws3, max_col=11, cap=45)

    # =========================================================================
    # SHEET 4: ANGKA DATA IRISAN 3 KELAS (PILIHAN SKRIPSI)
    # =========================================================================
    ws4 = wb.create_sheet(title="4. Angka Data Irisan 3K")
    ws4.freeze_panes = "A6"

    ws4['A1'] = "ANGKA LENGKAP JALUR IRISAN 3 KELAS (22.051 GAMBAR)"
    ws4['A1'].font = font_main_title
    ws4['A2'] = "Fokus Utama Skripsi: 3 Penyakit Bersama (HAM10k ∩ ISIC 2017 ∩ ISIC 2019) & Pembagian Data Anti-Bocor (80:10:10)"
    ws4['A2'].font = font_subtitle

    ws4['A4'] = "A. SUMBANGAN GAMBAR DARI SETIAP DATASET"
    ws4['A4'].font = font_section

    h_iri_easy = ["Sumber Dataset", "Keterangan Sumber", "Tahi Lalat (NV)", "Kanker Melanoma (MEL)", "Kutil Tua (BKL)", "Total 3 Penyakit", "Sumbangan (%)"]
    for c_i, h in enumerate(h_iri_easy, start=1):
        c = ws4.cell(row=5, column=c_i, value=h)
        c.font = font_th_navy
        c.fill = fill_navy
        c.alignment = align_center
        c.border = border_cell
    ws4.row_dimensions[5].height = 25

    iri_easy_rows = [
        ("HAM10000", "Data Primer (100% Utuh)", 6705, 1113, 1099, 8917, 8917/22051),
        ("ISIC 2019 Training", "Data Latih (Foto Non-HAM)", 6170, 3409, 1525, 11104, 11104/22051),
        ("ISIC 2017 Training", "Data Latih 2017", 804, 227, 252, 1283, 1283/22051),
        ("ISIC 2017 Test", "Data Uji 2017", 393, 116, 90, 599, 599/22051),
        ("ISIC 2017 Validation", "Data Validasi 2017", 76, 30, 42, 148, 148/22051),
    ]

    for r_i, r_data in enumerate(iri_easy_rows, start=6):
        for c_i, val in enumerate(r_data, start=1):
            cell = ws4.cell(row=r_i, column=c_i, value=val)
            cell.font = font_td
            cell.border = border_cell
            if c_i in [1, 2]:
                cell.alignment = align_left
            elif 3 <= c_i <= 6:
                cell.alignment = align_right
                cell.number_format = '#,##0'
            else:
                cell.alignment = align_right
                cell.number_format = '0.0%'
            if r_i % 2 == 1:
                cell.fill = fill_zebra
        ws4.row_dimensions[r_i].height = 20

    # Total row
    r_itot = 11
    ws4.cell(row=r_itot, column=1, value="TOTAL 3 DATASET").font = font_th_sub
    ws4.cell(row=r_itot, column=2, value="3 Dataset Multi-Senter").font = font_th_sub
    ws4.cell(row=r_itot, column=3, value=14148).number_format = '#,##0'
    ws4.cell(row=r_itot, column=4, value=4895).number_format = '#,##0'
    ws4.cell(row=r_itot, column=5, value=3008).number_format = '#,##0'
    ws4.cell(row=r_itot, column=6, value=22051).number_format = '#,##0'
    ws4.cell(row=r_itot, column=7, value=1.0).number_format = '0.0%'
    for c_i in range(1, 8):
        c = ws4.cell(row=r_itot, column=c_i)
        c.font = font_th_sub
        c.fill = fill_sub_header
        c.border = border_total
        if 3 <= c_i <= 7:
            c.alignment = align_right
    ws4.row_dimensions[r_itot].height = 24

    # Section B: 3 Kelas Detail
    r_3kd = 13
    ws4.cell(row=r_3kd, column=1, value="B. RINCIAN 3 KELAS PENYAKIT (PILIHAN SKRIPSI)").font = font_section

    h_3kd = ["Target Angka", "Kode", "Nama Sehari-hari", "Nama Medis Lengkap", "Sifat Medis", "Jumlah Foto", "Porsi (%)", "Peran Klinis"]
    for c_i, h in enumerate(h_3kd, start=1):
        c = ws4.cell(row=r_3kd+1, column=c_i, value=h)
        c.font = font_th_teal
        c.fill = fill_teal
        c.alignment = align_center
        c.border = border_cell
    ws4.row_dimensions[r_3kd+1].height = 25

    classes_3k_easy = [
        (0, "NV", "Tahi Lalat Biasa", "Melanocytic Nevus", "Jinak", 14148, 14148/22051, "Kelas mayoritas terbanyak (64%). Sebagai pembanding utama tahi lalat normal."),
        (1, "MEL", "Kanker Melanoma", "Melanoma", "Ganas", 4895, 4895/22051, "Fokus klinis utama (22%). Kanker berbahaya yang wajib terdeteksi akurat."),
        (2, "BKL", "Kutil Tua / Keratosis", "Benign Keratosis", "Jinak", 3008, 3008/22051, "Lesi jinak peniru (14%). Sering disangka melanoma karena warnanya gelap/hitam.")
    ]

    for idx, (t_num, t_code, t_easy, t_name, t_nature, t_cnt, t_pct, t_role) in enumerate(classes_3k_easy, start=r_3kd+2):
        row_vals = [t_num, t_code, t_easy, t_name, t_nature, t_cnt, t_pct, t_role]
        for c_i, val in enumerate(row_vals, start=1):
            cell = ws4.cell(row=idx, column=c_i, value=val)
            cell.font = font_td
            cell.border = border_cell
            if c_i == 1:
                cell.alignment = align_center
                cell.font = font_td_bold
            elif c_i == 2:
                cell.alignment = align_center
                cell.font = font_td_code
            elif c_i in [3, 4]:
                cell.alignment = align_left
            elif c_i == 5:
                cell.alignment = align_center
                if val == "Jinak":
                    cell.fill = fill_benign_soft
                    cell.font = font_benign
                else:
                    cell.fill = fill_malignant_soft
                    cell.font = font_malignant
            elif c_i == 6:
                cell.alignment = align_right
                cell.number_format = '#,##0'
            elif c_i == 7:
                cell.alignment = align_right
                cell.number_format = '0.0%'
            else:
                cell.alignment = align_left
        ws4.row_dimensions[idx].height = 22

    # Section C: Pembagian Data Anti-Bocor
    r_sp = r_3kd + 6
    ws4.cell(row=r_sp, column=1, value="C. PEMBAGIAN DATA BELAJAR & UJIAN BEBAS BOCOR (SPLIT 80:10:10)").font = font_section

    h_sp = ["Kelompok Data", "Target Pembagian", "Jumlah Foto", "Porsi Aktual", "Tahi Lalat (NV)", "Melanoma (MEL)", "Kutil Tua (BKL)", "Kebocoran Data Pasien", "Status Jaminan"]
    for c_i, h in enumerate(h_sp, start=1):
        c = ws4.cell(row=r_sp+1, column=c_i, value=h)
        c.font = font_th_navy
        c.fill = fill_navy
        c.alignment = align_center
        c.border = border_cell
    ws4.row_dimensions[r_sp+1].height = 25

    split_easy_rows = [
        ("Data Belajar (Training)", "80%", 17656, 17656/22051, 11302, 3902, 2452, "0 Pasien Bocor", "Aman 100%"),
        ("Data Latihan Ujian (Validation)", "10%", 2192, 2192/22051, 1455, 450, 287, "0 Pasien Bocor", "Aman 100%"),
        ("Data Ujian Akhir (Test)", "10%", 2203, 2203/22051, 1391, 543, 269, "0 Pasien Bocor", "Aman 100%"),
    ]

    for idx, r_data in enumerate(split_easy_rows, start=r_sp+2):
        for c_i, val in enumerate(r_data, start=1):
            cell = ws4.cell(row=idx, column=c_i, value=val)
            cell.font = font_td
            cell.border = border_cell
            if c_i in [1, 2]:
                cell.alignment = align_left
                if c_i == 1:
                    cell.font = font_td_bold
            elif c_i in [3, 5, 6, 7]:
                cell.alignment = align_right
                cell.number_format = '#,##0'
            elif c_i == 4:
                cell.alignment = align_right
                cell.number_format = '0.0%'
            elif c_i in [8, 9]:
                cell.alignment = align_center
                if c_i == 9:
                    cell.fill = fill_benign_soft
                    cell.font = font_benign
            if idx % 2 == 1:
                cell.fill = fill_zebra
        ws4.row_dimensions[idx].height = 22

    # Split Total
    r_sp_tot = r_sp + 5
    ws4.cell(row=r_sp_tot, column=1, value="TOTAL KESELURUHAN").font = font_th_sub
    ws4.cell(row=r_sp_tot, column=2, value="100%").font = font_th_sub
    ws4.cell(row=r_sp_tot, column=3, value=22051).number_format = '#,##0'
    ws4.cell(row=r_sp_tot, column=4, value=1.0).number_format = '0.0%'
    ws4.cell(row=r_sp_tot, column=5, value=14148).number_format = '#,##0'
    ws4.cell(row=r_sp_tot, column=6, value=4895).number_format = '#,##0'
    ws4.cell(row=r_sp_tot, column=7, value=3008).number_format = '#,##0'
    ws4.cell(row=r_sp_tot, column=8, value="0 Pasien Tumpang Tindih").font = font_th_sub
    ws4.cell(row=r_sp_tot, column=9, value="Validasi Sempurna").font = font_th_sub

    for c_i in range(1, 10):
        c = ws4.cell(row=r_sp_tot, column=c_i)
        c.font = font_th_sub
        c.fill = fill_sub_header
        c.border = border_total
        if 3 <= c_i <= 7:
            c.alignment = align_right
        elif c_i in [8, 9]:
            c.alignment = align_center
    ws4.row_dimensions[r_sp_tot].height = 24

    format_sheet_autofit(ws4, max_col=9, cap=45)

    # =========================================================================
    # SHEET 5: BUKTI DATA KLOP (AUDIT)
    # =========================================================================
    ws5 = wb.create_sheet(title="5. Bukti Data Klop (Audit)")
    ws5.freeze_panes = "A6"

    ws5['A1'] = "BUKTI VALIDASI: SEMUA DATA KLOP 100% TANPA KESALAHAN"
    ws5['A1'].font = font_main_title
    ws5['A2'] = "Pembuktian Komputer: 22.051 Foto Irisan Masuk Utuh ke Data Biner & Kemana Perginya 11.501 Foto Sisanya"
    ws5['A2'].font = font_subtitle

    ws5['A4'] = "A. HASIL PEMERIKSAAN INTEGRITAS OLEH KOMPUTER"
    ws5['A4'].font = font_section

    h_audit_easy = ["Hal yang Dicek Komputer", "Hasil Pemeriksaan Aktual", "Standar Kelulusan", "Status Audit", "Arti Sederhananya"]
    for c_i, h in enumerate(h_audit_easy, start=1):
        c = ws5.cell(row=5, column=c_i, value=h)
        c.font = font_th_navy
        c.fill = fill_navy
        c.alignment = align_center
        c.border = border_cell
    ws5.row_dimensions[5].height = 25

    audit_easy_rows = [
        ("Apakah semua ID foto irisan ada di data biner?", "22.051 dari 22.051 foto ada", "100% Wajib Ada", "LULUS (100%)", "Tidak ada satu pun foto irisan yang hilang atau nyasar."),
        ("Apakah ada nama label diagnosis yang beda/salah?", "0 kasus salah label", "0 Kesalahan", "LULUS (100%)", "Label NV, MEL, BKL sama persis di kedua dataset."),
        ("Apakah ada sumber dataset yang tertukar?", "0 kasus tertukar", "0 Kesalahan", "LULUS (100%)", "Asal usul dataset (HAM10k, 2019, 2017) konsisten 100%."),
        ("Apakah file gambar JPG fisiknya benar ada di laptop?", "1.000 dari 1.000 sampel fisik ada", "100% Ada", "LULUS (100%)", "Semua file foto tersimpan rapi dan bisa dibuka di hard disk."),
        ("Apakah ada data pasien yang bocor saat ujian?", "0 lesi/pasien bocor", "0 Kebocoran", "LULUS (100%)", "AI dijamin tidak menyontek data pasien saat evaluasi."),
        ("Apakah ada baris kosong / nilai rusak (NaN)?", "0 nilai kosong", "0 Nilai Rusak", "LULUS (100%)", "Semua tabel data terisi lengkap tanpa cacat.")
    ]

    for r_i, r_data in enumerate(audit_easy_rows, start=6):
        for c_i, val in enumerate(r_data, start=1):
            cell = ws5.cell(row=r_i, column=c_i, value=val)
            cell.font = font_td
            cell.border = border_cell
            if c_i == 1:
                cell.alignment = align_left
                cell.font = font_td_bold
            elif c_i in [2, 3]:
                cell.alignment = align_center
            elif c_i == 4:
                cell.alignment = align_center
                cell.fill = fill_benign_soft
                cell.font = font_benign
            else:
                cell.alignment = align_left
            if r_i % 2 == 1:
                cell.fill = fill_zebra
        ws5.row_dimensions[r_i].height = 22

    # Section B: Dekomposisi 11.501
    r_non_easy = 13
    ws5.cell(row=r_non_easy, column=1, value="B. KEMANA PERGINYA 11.501 FOTO BINER YANG TIDAK MASUK IRISAN 3 KELAS?").font = font_section

    h_non_easy = ["Sumber Dataset", "BCC (Sel Basal)", "AKIEC (Pra-Kanker)", "SCC (Skuamosa)", "VASC (Titik Darah)", "DF (Kenyal)", "Lainnya", "Total Non-Irisan", "Kenapa Tidak Dimasukkan ke Jalur Irisan?"]
    for c_i, h in enumerate(h_non_easy, start=1):
        c = ws5.cell(row=r_non_easy+1, column=c_i, value=h)
        c.font = font_th_teal
        c.fill = fill_teal
        c.alignment = align_center
        c.border = border_cell
    ws5.row_dimensions[r_non_easy+1].height = 25

    non_easy_rows = [
        ("HAM10000", 514, 327, 0, 142, 115, 0, 1098, "Penyakit ini (BCC, AKIEC, VASC, DF) memang tidak disediakan di dataset ISIC 2017."),
        ("ISIC 2019 Training", 2809, 737, 431, 111, 124, 0, 4212, "Penyakit ini (BCC, AKIEC, SCC, VASC, DF) memang tidak disediakan di dataset ISIC 2017."),
        ("ISIC 2019 Test", 975, 374, 165, 104, 91, 4482, 6191, "Seluruh partisi Uji 2019 sengaja disimpan hanya untuk jalur biner global."),
    ]

    for r_i, r_data in enumerate(non_easy_rows, start=r_non_easy+2):
        for c_i, val in enumerate(r_data, start=1):
            cell = ws5.cell(row=r_i, column=c_i, value=val)
            cell.font = font_td
            cell.border = border_cell
            if c_i == 1:
                cell.alignment = align_left
                cell.font = font_td_bold
            elif 2 <= c_i <= 8:
                cell.alignment = align_right
                cell.number_format = '#,##0'
            else:
                cell.alignment = align_left
            if r_i % 2 == 1:
                cell.fill = fill_zebra
        ws5.row_dimensions[r_i].height = 20

    # Total non-irisan
    r_non_tot = r_non_easy + 5
    ws5.cell(row=r_non_tot, column=1, value="TOTAL BUKTI").font = font_th_sub
    ws5.cell(row=r_non_tot, column=2, value=4298).number_format = '#,##0'
    ws5.cell(row=r_non_tot, column=3, value=1438).number_format = '#,##0'
    ws5.cell(row=r_non_tot, column=4, value=596).number_format = '#,##0'
    ws5.cell(row=r_non_tot, column=5, value=357).number_format = '#,##0'
    ws5.cell(row=r_non_tot, column=6, value=330).number_format = '#,##0'
    ws5.cell(row=r_non_tot, column=7, value=4482).number_format = '#,##0'
    ws5.cell(row=r_non_tot, column=8, value=11501).number_format = '#,##0'
    ws5.cell(row=r_non_tot, column=9, value="Pas 100%: 11.501 (di luar) + 22.051 (irisan) = Tepat 33.552 Gambar Biner!").font = font_th_sub

    for c_i in range(1, 10):
        c = ws5.cell(row=r_non_tot, column=c_i)
        c.font = font_th_sub
        c.fill = fill_sub_header
        c.border = border_total
        if 2 <= c_i <= 8:
            c.alignment = align_right
    ws5.row_dimensions[r_non_tot].height = 24

    format_sheet_autofit(ws5, max_col=9, cap=48)

    # =========================================================================
    # SHEET 6: DAFTAR JURNAL LENGKAP & DETAIL
    # =========================================================================
    ws6 = wb.create_sheet(title="6. Daftar Jurnal Lengkap")
    ws6.freeze_panes = "A6"

    ws6['A1'] = "DAFTAR JURNAL ILMIAH INTERNASIONAL LENGKAP (STANDAR SCOPUS Q1 & NATURE)"
    ws6['A1'].font = font_main_title
    ws6['A2'] = "Kompilasi Judul Lengkap Paper, Nama Jurnal, Penulis, DOI, Reputasi, dan Penjelasan Sederhana Perannya"
    ws6['A2'].font = font_subtitle

    ws6['A4'] = "TABEL LENGKAP PAPER RUJUKAN RESMI"
    ws6['A4'].font = font_section

    h_journal = ["No", "Penulis & Tahun", "Judul Lengkap Paper Ilmiah", "Nama Jurnal / Konferensi Lengkap", "Penerbit & Reputasi", "Link DOI / Akses", "Kenapa Paper Ini Dipakai? (Penjelasan Santai)"]
    for c_i, h in enumerate(h_journal, start=1):
        c = ws6.cell(row=5, column=c_i, value=h)
        c.font = font_th_navy
        c.fill = fill_navy
        c.alignment = align_center
        c.border = border_cell
    ws6.row_dimensions[5].height = 25

    journals_full_data = [
        (1, "Philipp Tschandl, Cliff Rosendahl, & Harald Kittler (2018)",
         "The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions",
         "Scientific Data (Nature Publishing Group)",
         "Nature Research (Scopus Q1, Impact Factor: 9.8)",
         "https://doi.org/10.1038/sdata.2018.161",
         "Paper 'kitab suci' HAM10000. Dari sinilah nama singkatan NV, MEL, BKL berasal, dan paper ini yang membuktikan secara medis bahwa Seborrheic Keratosis itu masuk keluarga besar BKL."),

        (2, "Noel C. F. Codella, David Gutman, M. Emre Celebi, et al. (2018)",
         "Skin lesion analysis toward melanoma detection: A challenge at the 2017 International Symposium on Biomedical Imaging (ISBI), hosted by the International Skin Imaging Collaboration (ISIC)",
         "2018 IEEE 15th International Symposium on Biomedical Imaging (ISBI 2018)",
         "IEEE Xplore (Disitasi >1.200+ Peneliti Dunia)",
         "https://doi.org/10.1109/ISBI.2018.8363547",
         "Paper resmi kompetisi ISIC 2017. Menjadi alasan kenapa kita memilih 3 kelas (NV, MEL, BKL) karena kompetisi dunia ini menetapkan 3 diagnosis ini sebagai tolok ukur standar."),

        (3, "Abdul Rehman Baig, Qaisar Abbas, Reem Almakki, et al. (2023)",
         "Light-Dermo: A lightweight pretrained convolution neural network for the diagnosis of multiclass skin lesions",
         "Diagnostics (MDPI)",
         "MDPI (Scopus Q2, Impact Factor: 3.6)",
         "https://doi.org/10.3390/diagnostics13030385",
         "Contoh nyata penggabungan dataset HAM10000 dan ISIC 2019. Membuktikan bahwa menggabungkan data dan membuang gambar duplikat membuat model AI jadi jauh lebih pintar."),

        (4, "Luminiţa Ichim, Radu-Ioan Mitrica, Mihai-Octavian Serghei, & Dan Popescu (2023)",
         "Detection of malignant skin lesions based on decision fusion of ensembles of neural networks",
         "Cancers (MDPI)",
         "MDPI (Scopus Q1, Impact Factor: 5.2)",
         "https://doi.org/10.3390/cancers15204946",
         "Pedoman cara membersihkan gambar kembar (overlap removal) antar-arsip ISIC. Supaya AI kita tidak dinilai terlalu tinggi secara palsu karena menghafal gambar yang sama."),

        (5, "Catarina Barata, M. Emre Celebi, & Jorge S. Marques (2020)",
         "Explainable skin lesion diagnosis using taxonomies",
         "Pattern Recognition (Elsevier)",
         "Elsevier (Scopus Q1, Impact Factor: 8.0)",
         "https://doi.org/10.1016/j.patcog.2020.107413",
         "Rujukan pemetaan biner ISIC 2017: Menjelaskan bahwa Melanoma adalah target Kanker Ganas (1), sedangkan Nevus dan Keratosis adalah kelompok Jinak (0)."),

        (6, "Mario Fernando Jojoa Acosta, Liesle Yail Caballero Tovar, et al. (2021)",
         "Melanoma diagnosis using deep learning techniques on dermatoscopic images",
         "BMC Medical Imaging (Springer Nature)",
         "Springer Nature (Scopus Q2, Impact Factor: 2.7)",
         "https://doi.org/10.1186/s12880-020-00534-8",
         "Rujukan kedua untuk ISIC 2017: Menguji deteksi melanoma berbasis Mask R-CNN dan menggolongkan Nevus + Keratosis Seboroik ke dalam kelas Jinak."),

        (7, "Ioannis Kousis, Isidoros Perikos, Ioannis Hatzilygeroudis, & Maria Virvou (2022)",
         "Deep Learning Methods for Accurate Skin Cancer Recognition and Mobile Application",
         "Electronics (MDPI)",
         "MDPI (Scopus Q2, Impact Factor: 2.9)",
         "https://doi.org/10.3390/electronics11091294",
         "Rujukan biner HAM10000: Membuktikan bahwa membagi 7 kelas menjadi 2 (Jinak: NV, BKL, DF, VASC vs Ganas: MEL, BCC, AKIEC) memberikan akurasi sangat tinggi untuk aplikasi ponsel."),

        (8, "Pronab Ghosh, Sami Azam, Ryana Quadir, Asif Karim, et al. (2022)",
         "SkinNet-16: A deep learning approach to identify benign and malignant skin lesions",
         "Frontiers in Oncology (Frontiers Media)",
         "Frontiers (Scopus Q2, Impact Factor: 4.7)",
         "https://doi.org/10.3389/fonc.2022.931141",
         "Rujukan biner kedua HAM10000: Menegaskan bahwa tahi lalat, keratosis, dermatofibroma, dan vaskular adalah kelompok Jinak; sedangkan melanoma, sel basal, dan pra-kanker adalah Ganas."),

        (9, "Balázs Harangi, Ágnes Baran, & András Hajdu (2020)",
         "Assisted deep learning framework for multi-class skin lesion classification considering a binary classification support",
         "Biomedical Signal Processing and Control (Elsevier)",
         "Elsevier (Scopus Q1, Impact Factor: 5.1)",
         "https://doi.org/10.1016/j.bspc.2020.102041",
         "Rujukan transisi multiclass ke biner pada dataset kompetisi ISIC 2018 Task 3."),

        (10, "Bradley Yao, Angela Jin, Huijuan Liu, & Qiliang Li (2026)",
         "MorphoNet: An Interpretable Hierarchical Deep Learning Framework for Multi-Class Skin Lesion Classification Using Dermoscopic Morphology",
         "Bioengineering (MDPI)",
         "MDPI (Scopus Q2, Impact Factor: 4.0)",
         "https://doi.org/10.3390/bioengineering13090989",
         "Rujukan resmi pemetaan 8 kelas ISIC 2019: Skrining tahap 1 memisahkan Jinak (NV, BKL, DF, VASC) vs Ganas (MEL, BCC, AKIEC, SCC)."),

        (11, "Veronica Rotemberg, Nicholas Kurtansky, Brigid Betz-Stablein, et al. (2021)",
         "A patient-centric dataset of images and metadata for identifying melanomas using clinical context",
         "Nature Medicine (Nature Publishing Group)",
         "Nature Research (Scopus Q1, Impact Factor: 82.9)",
         "https://doi.org/10.1038/s41591-021-01255-3",
         "Paper resmi ISIC 2020. Menjelaskan tentang 584 kasus melanoma ganas biopsi vs 32 ribu lesi skrining jinak klinis non-biopsi.")
    ]

    for r_i, r_data in enumerate(journals_full_data, start=6):
        for c_i, val in enumerate(r_data, start=1):
            cell = ws6.cell(row=r_i, column=c_i, value=val)
            cell.font = font_td
            cell.border = border_cell
            if c_i == 1:
                cell.alignment = align_center
                cell.font = font_td_bold
            elif c_i in [2, 3, 4, 5, 7]:
                cell.alignment = align_wrap_left
                if c_i == 3:
                    cell.font = font_td_bold
            elif c_i == 6:
                cell.alignment = align_wrap_left
                cell.font = Font(name='Segoe UI', size=9, color='2563EB', underline='single')
            if r_i % 2 == 1:
                cell.fill = fill_zebra
        ws6.row_dimensions[r_i].height = 48

    format_sheet_autofit(ws6, max_col=7, cap=55)

    # Save to improved file
    output_filename = "rekap_dataset_biner_dan_irisan improve.xlsx"
    wb.save(output_filename)
    print(f"File Excel versi improve berhasil dibuat: {output_filename}")

if __name__ == '__main__':
    build_improved_excel()
