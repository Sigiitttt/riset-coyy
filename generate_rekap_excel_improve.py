"""
Generator: rekap_dataset_biner_dan_irisan improve.xlsx
-----------------------------------------------------
Versi improve dari file asli rekap_dataset_biner_dan_irisan.xlsx.
Perubahan utama:
  - Bahasa natural, enak dibaca, tanpa analogi kekanak-kanakan.
  - Tampilan lebih bersih: warna modern, spacing rapi, border halus.
  - Jurnal lengkap: judul paper, nama jurnal, DOI/link.
"""

import openpyxl
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side, numbers
)
from openpyxl.utils import get_column_letter
from copy import copy

# ===========================================================================
# DESIGN SYSTEM
# ===========================================================================
FONT_BODY = Font(name="Segoe UI", size=10, color="2D3436")
FONT_HEADER = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
FONT_TITLE = Font(name="Segoe UI", size=13, bold=True, color="2D3436")
FONT_SUBTITLE = Font(name="Segoe UI", size=10, italic=True, color="636E72")
FONT_SECTION = Font(name="Segoe UI", size=11, bold=True, color="2D3436")
FONT_NOTE = Font(name="Segoe UI", size=9, italic=True, color="636E72")
FONT_TOTAL = Font(name="Segoe UI", size=10, bold=True, color="2D3436")
FONT_BOLD = Font(name="Segoe UI", size=10, bold=True, color="2D3436")
FONT_JINAK = Font(name="Segoe UI", size=10, bold=True, color="27AE60")
FONT_GANAS = Font(name="Segoe UI", size=10, bold=True, color="E74C3C")
FONT_LINK = Font(name="Segoe UI", size=10, color="2980B9", underline="single")

# Fills
FILL_HEADER = PatternFill("solid", fgColor="2C3E50")  # dark navy
FILL_ROW_ODD = PatternFill("solid", fgColor="FFFFFF")
FILL_ROW_EVEN = PatternFill("solid", fgColor="F8F9FA")
FILL_TOTAL = PatternFill("solid", fgColor="E8EDF2")
FILL_JINAK = PatternFill("solid", fgColor="E8F8F5")   # soft mint
FILL_GANAS = PatternFill("solid", fgColor="FDEDEC")   # soft rose
FILL_SECTION = PatternFill("solid", fgColor="EBF0F5")
FILL_NOTE_BG = PatternFill("solid", fgColor="FFF9E6")  # warm cream for notes
FILL_LOLOS = PatternFill("solid", fgColor="D5F5E3")   # green pass

# Borders
THIN_BORDER = Border(
    left=Side(style="thin", color="D5D8DC"),
    right=Side(style="thin", color="D5D8DC"),
    top=Side(style="thin", color="D5D8DC"),
    bottom=Side(style="thin", color="D5D8DC"),
)
NO_BORDER = Border()

# Alignment
ALIGN_CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
ALIGN_LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)
ALIGN_LEFT_TOP = Alignment(horizontal="left", vertical="top", wrap_text=True)
ALIGN_RIGHT = Alignment(horizontal="right", vertical="center", wrap_text=True)

PERCENT_FMT = '0.00%'


# ===========================================================================
# HELPER FUNCTIONS
# ===========================================================================

def set_col_widths(ws, widths):
    """Set column widths from a dict {col_letter_or_num: width}."""
    for col, w in widths.items():
        if isinstance(col, int):
            col = get_column_letter(col)
        ws.column_dimensions[col].width = w


def write_title(ws, row, col, text, subtitle=None, merge_end=5):
    """Write a sheet title + optional subtitle."""
    c = ws.cell(row=row, column=col, value=text)
    c.font = FONT_TITLE
    c.alignment = ALIGN_LEFT
    ws.merge_cells(
        start_row=row, start_column=col,
        end_row=row, end_column=merge_end
    )
    if subtitle:
        r2 = row + 1
        c2 = ws.cell(row=r2, column=col, value=subtitle)
        c2.font = FONT_SUBTITLE
        c2.alignment = ALIGN_LEFT
        ws.merge_cells(
            start_row=r2, start_column=col,
            end_row=r2, end_column=merge_end
        )


def write_section(ws, row, col, text, merge_end=5):
    """Write a section heading row."""
    c = ws.cell(row=row, column=col, value=text)
    c.font = FONT_SECTION
    c.alignment = ALIGN_LEFT
    c.fill = FILL_SECTION
    for cc in range(col, merge_end + 1):
        ws.cell(row=row, column=cc).fill = FILL_SECTION
        ws.cell(row=row, column=cc).border = THIN_BORDER
    ws.merge_cells(
        start_row=row, start_column=col,
        end_row=row, end_column=merge_end
    )


def write_header_row(ws, row, headers, start_col=1):
    """Write a styled header row."""
    for i, h in enumerate(headers):
        c = ws.cell(row=row, column=start_col + i, value=h)
        c.font = FONT_HEADER
        c.fill = FILL_HEADER
        c.alignment = ALIGN_CENTER
        c.border = THIN_BORDER


def write_data_row(ws, row, values, start_col=1, is_total=False, fonts=None, fills=None):
    """Write a data row with alternating colors."""
    is_even = (row % 2 == 0)
    default_fill = FILL_TOTAL if is_total else (FILL_ROW_EVEN if is_even else FILL_ROW_ODD)
    default_font = FONT_TOTAL if is_total else FONT_BODY
    for i, v in enumerate(values):
        c = ws.cell(row=row, column=start_col + i, value=v)
        c.font = fonts[i] if (fonts and i < len(fonts) and fonts[i]) else default_font
        c.fill = fills[i] if (fills and i < len(fills) and fills[i]) else default_fill
        c.border = THIN_BORDER
        # Number formatting
        if isinstance(v, float) and 0 <= v <= 1:
            c.number_format = PERCENT_FMT
            c.alignment = ALIGN_CENTER
        elif isinstance(v, (int, float)):
            c.number_format = '#,##0'
            c.alignment = ALIGN_CENTER
        else:
            c.alignment = ALIGN_LEFT


def write_note(ws, row, col, text, merge_end=5):
    """Write a note/remark cell."""
    c = ws.cell(row=row, column=col, value=text)
    c.font = FONT_NOTE
    c.alignment = ALIGN_LEFT_TOP
    c.fill = FILL_NOTE_BG
    c.border = THIN_BORDER
    ws.merge_cells(
        start_row=row, start_column=col,
        end_row=row, end_column=merge_end
    )


# ===========================================================================
# SHEET 1: Ringkasan Komparatif
# ===========================================================================
def build_sheet_1(wb):
    ws = wb.active
    ws.title = "1. Ringkasan Komparatif"
    ws.sheet_properties.tabColor = "2C3E50"

    set_col_widths(ws, {1: 28, 2: 40, 3: 40, 4: 42})

    write_title(ws, 1, 1,
                "Ringkasan Komparatif: Jalur Biner vs Jalur Irisan 3 Kelas",
                "Perbandingan dua jalur klasifikasi yang dipakai dalam riset ini",
                merge_end=4)

    # -- Table --
    r = 4
    write_header_row(ws, r, ["Aspek Perbandingan", "Jalur Biner", "Jalur Irisan 3 Kelas", "Catatan"], 1)

    data = [
        ["Tujuan utama",
         "Membedakan lesi kulit jinak (benign) vs ganas (malignant)",
         "Mengenali 3 jenis diagnosis spesifik: NV, MEL, BKL",
         "Biner = skrining awal, Irisan = diagnosis lebih detail"],
        ["Dataset yang dipakai",
         "HAM10000 + ISIC 2019 + ISIC 2017 (semua partisi)",
         "HAM10000 + ISIC 2019 Train + ISIC 2017 (Train/Val/Test)",
         "Keduanya pakai 3 sumber dataset yang sama"],
        ["Jumlah citra bersih",
         "33.552 gambar (setelah deduplikasi + buang UNK)",
         "22.051 gambar (hanya kelas NV, MEL, BKL yang ada di ketiga dataset)",
         "Irisan lebih kecil karena hanya ambil kelas yang sama-sama ada"],
        ["Jumlah kelas",
         "2 kelas: Benign (0) dan Malignant (1)",
         "3 kelas: NV (0), MEL (1), BKL (2)",
         "Biner pakai semua 8 jenis penyakit, irisan cuma 3"],
        ["Sebaran kelas (proporsi)",
         "Benign: 20.998 (62,58%) | Malignant: 12.554 (37,42%)",
         "NV: 14.148 (64,17%) | MEL: 4.895 (22,20%) | BKL: 3.008 (13,64%)",
         "Keduanya punya ketimpangan kelas, diatasi pakai Focal Loss / Class-Balanced Loss"],
        ["Acuan paper utama",
         "Konsensus voting 8 paper internasional (Elsevier, MDPI, Springer, Frontiers)",
         "Tschandl et al. (Nature 2018), Codella et al. (IEEE ISBI 2018), Baig (2023), Ichim (2023)",
         "Semua pemetaan didasarkan rujukan jurnal bereputasi (Scopus Q1 / Nature)"],
    ]
    for i, d in enumerate(data):
        write_data_row(ws, r + 1 + i, d, 1)

    # -- Notes for supervisor --
    r2 = r + 1 + len(data) + 1
    write_section(ws, r2, 1, "Catatan Penting untuk Dosen Pembimbing", merge_end=4)

    notes = [
        "1. Konsistensi data: Seluruh 22.051 citra irisan berada di dalam dataset biner (33.552). Tidak ada satu pun gambar yang bentrok labelnya.",
        "2. Validitas label BKL: Penggabungan 'Seborrheic Keratosis' (ISIC 2017) ke 'BKL' sudah sesuai standar Nature Scientific Data (Tschandl et al., 2018, hal. 7).",
        "3. Data siap modeling: Dataset irisan 3 kelas sudah dipartisi Train (17.656) / Val (2.192) / Test (2.203) dengan jaminan 0% kebocoran lesi pasien.",
        "4. Pipeline lengkap: Seluruh kode Data Understanding, Data Preparation, sampai skrip training PyTorch (ResNet-50 & EfficientNet-B0) sudah terstruktur dan terverifikasi.",
    ]
    for i, n in enumerate(notes):
        write_note(ws, r2 + 1 + i, 1, n, merge_end=4)


# ===========================================================================
# SHEET 2: Harmonisasi Label & Konsensus
# ===========================================================================
def build_sheet_2(wb):
    ws = wb.create_sheet("2. Harmonisasi & Konsensus")
    ws.sheet_properties.tabColor = "2980B9"

    set_col_widths(ws, {1: 14, 2: 42, 3: 18, 4: 16, 5: 22, 6: 20, 7: 16,
                        8: 12, 9: 12, 10: 12, 11: 12, 12: 12})

    write_title(ws, 1, 1,
                "Harmonisasi Label & Konsensus Pemetaan Biner",
                "Standarisasi kode diagnosis antar-dataset dan matriks voting 8 jurnal internasional",
                merge_end=7)

    # -- A. Harmonization Table --
    r = 4
    write_section(ws, r, 1, "A. Kode Harmonisasi 8 Kelas Diagnosis Kulit", merge_end=7)
    r += 1
    write_header_row(ws, r, [
        "Kode", "Nama Diagnosis", "Label HAM10000",
        "Label ISIC 2019", "Label ISIC 2017", "Sifat Klinis", "Pemetaan Biner"
    ], 1)

    harm_data = [
        ["NV", "Melanocytic Nevus (tahi lalat jinak)", "nv", "NV", "nevus", "Jinak", "Benign (0)"],
        ["MEL", "Melanoma (kanker kulit ganas)", "mel", "MEL", "melanoma", "Ganas", "Malignant (1)"],
        ["BKL", "Benign Keratosis (keratosis seboroik)", "bkl", "BKL", "seborrheic_keratosis", "Jinak", "Benign (0)"],
        ["BCC", "Basal Cell Carcinoma (karsinoma sel basal)", "bcc", "BCC", "-", "Ganas", "Malignant (1)"],
        ["AKIEC", "Actinic Keratosis (pre-kanker)", "akiec", "AK", "-", "Pre-kanker/Ganas", "Malignant (1)"],
        ["SCC", "Squamous Cell Carcinoma (karsinoma sel skuamosa)", "-", "SCC", "-", "Ganas", "Malignant (1)"],
        ["VASC", "Vascular Lesion (lesi pembuluh darah)", "vasc", "VASC", "-", "Jinak", "Benign (0)"],
        ["DF", "Dermatofibroma (nodul jinak di kulit)", "df", "DF", "-", "Jinak", "Benign (0)"],
    ]
    for i, d in enumerate(harm_data):
        sifat = d[5]
        sifat_font = FONT_JINAK if "Jinak" in sifat else FONT_GANAS
        biner_font = FONT_JINAK if "Benign" in d[6] else FONT_GANAS
        biner_fill = FILL_JINAK if "Benign" in d[6] else FILL_GANAS
        fonts = [FONT_BOLD, None, None, None, None, sifat_font, biner_font]
        fills = [None, None, None, None, None, None, biner_fill]
        write_data_row(ws, r + 1 + i, d, 1, fonts=fonts, fills=fills)

    # -- B. BKL Explanation --
    r2 = r + 1 + len(harm_data) + 1
    write_section(ws, r2, 1, "B. Kenapa 'Seborrheic Keratosis' (ISIC 2017) Digabung ke 'BKL'", merge_end=7)
    r2 += 1
    explanation = (
        'Tschandl, Rosendahl, & Kittler (2018) di Nature Scientific Data, hal. 7, menjelaskan:\n'
        '"Benign keratosis is a generic class that includes seborrheic keratoses (senile wart), '
        'solar lentigo, and lichen-planus like keratoses (LPLK)... we grouped them together because '
        'they are similar biologically and often reported under the same generic term histopathologically."\n\n'
        'Jadi penggabungan ini bukan keputusan kita sendiri -- ini standar resmi dari konsorsium ISIC sejak 2018.'
    )
    c = ws.cell(row=r2, column=1, value=explanation)
    c.font = FONT_BODY
    c.alignment = ALIGN_LEFT_TOP
    c.fill = FILL_NOTE_BG
    c.border = THIN_BORDER
    ws.merge_cells(start_row=r2, start_column=1, end_row=r2 + 3, end_column=7)

    # -- C. Voting Matrix (with paper titles) --
    r3 = r2 + 5
    write_section(ws, r3, 1, "C. Matriks Voting 8 Paper Internasional (Pemetaan Biner)", merge_end=12)
    r3 += 1
    write_header_row(ws, r3, [
        "Penulis", "Judul Paper", "Jurnal & Tahun", "Dataset",
        "NV", "BKL", "DF", "VASC", "MEL", "BCC", "AKIEC", "SCC"
    ], 1)
    # Adjust column widths for voting table area
    ws.column_dimensions['B'].width = 52  # Judul Paper needs more space
    ws.column_dimensions['C'].width = 44

    voting_data = [
        ["Kousis et al.",
         "Deep Learning Methods for Accurate Skin Cancer Recognition and Mobile Application",
         "Electronics (MDPI), 2022", "HAM10000",
         "Jinak", "Jinak", "Jinak", "Jinak", "Ganas", "Ganas", "Ganas", "-"],
        ["Ghosh et al.",
         "SkinNet-16: A deep learning approach to identify benign and malignant skin lesions",
         "Frontiers in Oncology, 2022", "HAM10000",
         "Jinak", "Jinak", "Jinak", "Jinak", "Ganas", "Ganas", "Ganas", "-"],
        ["Harangi et al.",
         "Assisted deep learning framework for multi-class skin lesion classification considering a binary classification support",
         "Biomedical Signal Proc. & Control (Elsevier), 2020", "HAM10000 / 2018",
         "Jinak", "Jinak", "Jinak", "Ganas*", "Ganas", "Ganas", "Ganas", "-"],
        ["Ameri",
         "A deep learning approach to skin cancer detection in dermoscopy images",
         "J. Biomed. Physics & Eng. (JBPE), 2020", "HAM10000",
         "Jinak", "Jinak", "Jinak", "Exclude", "Ganas", "Ganas", "Ganas", "-"],
        ["Barata et al.",
         "Explainable skin lesion diagnosis using taxonomies",
         "Pattern Recognition (Elsevier), 2020", "ISIC 2017",
         "Jinak", "Jinak", "-", "-", "Ganas", "-", "-", "-"],
        ["Jojoa Acosta et al.",
         "Melanoma diagnosis using deep learning techniques on dermatoscopic images",
         "BMC Medical Imaging (Springer), 2021", "ISIC 2017",
         "Jinak", "Jinak", "-", "-", "Ganas", "-", "-", "-"],
        ["Yao et al.",
         "MorphoNet: An Interpretable Hierarchical Deep Learning Framework for Multi-Class Skin Lesion Classification",
         "Bioengineering (MDPI), 2026", "HAM10k & 2019",
         "Jinak", "Jinak", "Jinak", "Jinak", "Ganas", "Ganas", "Ganas", "Ganas"],
        ["Venugopal et al.",
         "Multiclass skin cancer classification using ensemble of fine-tuned deep learning models",
         "Data Analysis Journal (Elsevier), 2023", "ISIC 2019",
         "Jinak", "Jinak", "Jinak", "Jinak", "Ganas", "Ganas", "Ganas", "Ganas"],
    ]
    for i, d in enumerate(voting_data):
        fonts = [None, None, None, None]  # Penulis, Judul, Jurnal, Dataset
        fills = [None, None, None, None]
        for j in range(4, 12):
            val = d[j]
            if val == "Jinak":
                fonts.append(FONT_JINAK)
                fills.append(FILL_JINAK)
            elif val in ("Ganas", "Ganas*"):
                fonts.append(FONT_GANAS)
                fills.append(FILL_GANAS)
            else:
                fonts.append(None)
                fills.append(None)
        write_data_row(ws, r3 + 1 + i, d, 1, fonts=fonts, fills=fills)
        ws.row_dimensions[r3 + 1 + i].height = 36  # taller rows for title readability

    # Consensus row
    r_cons = r3 + 1 + len(voting_data)
    consensus = [
        "KONSENSUS (VOTING)", "", "Mayoritas Literatur", "Semua Sumber",
        "JINAK (100%)", "JINAK (100%)", "JINAK (100%)", "JINAK (80%)",
        "GANAS (100%)", "GANAS (100%)", "GANAS (100%)", "GANAS (100%)"
    ]
    fonts_cons = [FONT_TOTAL, FONT_TOTAL, FONT_TOTAL, FONT_TOTAL]
    fills_cons = [FILL_TOTAL, FILL_TOTAL, FILL_TOTAL, FILL_TOTAL]
    for j in range(4, 12):
        if "JINAK" in consensus[j]:
            fonts_cons.append(FONT_JINAK)
            fills_cons.append(FILL_JINAK)
        else:
            fonts_cons.append(FONT_GANAS)
            fills_cons.append(FILL_GANAS)
    write_data_row(ws, r_cons, consensus, 1, is_total=True, fonts=fonts_cons, fills=fills_cons)


# ===========================================================================
# SHEET 3: Statistik Jalur Biner
# ===========================================================================
def build_sheet_3(wb):
    ws = wb.create_sheet("3. Statistik Jalur Biner")
    ws.sheet_properties.tabColor = "8E44AD"

    set_col_widths(ws, {1: 16, 2: 20, 3: 18, 4: 16, 5: 18, 6: 14, 7: 44,
                        8: 16, 9: 14, 10: 14, 11: 18})

    write_title(ws, 1, 1,
                "Statistik Dataset Jalur Biner (33.552 Citra Bersih)",
                "Deduplikasi, sebaran 8 kelas, dan distribusi target akhir Benign vs Malignant",
                merge_end=7)

    # -- A. Dedup Table --
    r = 4
    write_section(ws, r, 1, "A. Proses Deduplikasi Antar-Dataset", merge_end=7)
    r += 1
    write_header_row(ws, r, [
        "Sumber Dataset", "Partisi", "Citra Mentah", "Duplikat Dibuang",
        "Citra Bersih", "% Proporsi", "Keterangan"
    ], 1)

    dedup = [
        ["HAM10000", "Part 1 & 2", 10015, 0, 10015, 0.2985, "Dipertahankan 100% utuh, tidak ada yang dibuang"],
        ["ISIC 2019", "Training Input", 25331, 10015, 15316, 0.4565, "10.015 duplikat identik dengan HAM10000 dibuang"],
        ["ISIC 2019", "Test Input", 8238, 2047, 6191, 0.1845, "2.047 citra UNK (out-of-distribution) dibuang"],
        ["ISIC 2017", "Training Data", 2000, 717, 1283, 0.0382, "717 duplikat dengan HAM10k/2019 dibuang"],
        ["ISIC 2017", "Test Data", 600, 1, 599, 0.0179, "1 duplikat dibuang"],
        ["ISIC 2017", "Validation Data", 150, 2, 148, 0.0044, "2 duplikat dibuang"],
    ]
    for i, d in enumerate(dedup):
        write_data_row(ws, r + 1 + i, d, 1)

    total_dedup = ["TOTAL", "6 Partisi", 46334, 12782, 33552, 1.0, "33.552 citra berlabel bersih, 100% unik"]
    write_data_row(ws, r + 1 + len(dedup), total_dedup, 1, is_total=True)

    # -- B. 8-Class Distribution --
    r2 = r + 1 + len(dedup) + 2
    write_section(ws, r2, 1, "B. Sebaran 8 Kelas Diagnosis per Sumber Dataset", merge_end=11)
    r2 += 1
    write_header_row(ws, r2, [
        "Kode", "Nama Diagnosis", "HAM10k", "ISIC 2019 Train",
        "ISIC 2019 Test", "ISIC 2017 Train", "ISIC 2017 Test",
        "ISIC 2017 Val", "Total", "% Proporsi", "Sifat Klinis"
    ], 1)

    kelas8 = [
        ["NV", "Melanocytic Nevus", 6705, 6170, 2495, 804, 393, 76, 16643, 0.4960, "Jinak"],
        ["MEL", "Melanoma", 1113, 3409, 1327, 227, 116, 30, 6222, 0.1854, "Ganas"],
        ["BCC", "Basal Cell Carcinoma", 514, 2809, 975, 0, 0, 0, 4298, 0.1281, "Ganas"],
        ["BKL", "Benign Keratosis", 1099, 1525, 660, 252, 90, 42, 3668, 0.1093, "Jinak"],
        ["AKIEC", "Actinic Keratosis", 327, 737, 374, 0, 0, 0, 1438, 0.0429, "Pre-kanker/Ganas"],
        ["SCC", "Squamous Cell Carcinoma", 0, 431, 165, 0, 0, 0, 596, 0.0178, "Ganas"],
        ["VASC", "Vascular Lesion", 142, 111, 104, 0, 0, 0, 357, 0.0106, "Jinak"],
        ["DF", "Dermatofibroma", 115, 124, 91, 0, 0, 0, 330, 0.0098, "Jinak"],
    ]
    for i, d in enumerate(kelas8):
        sifat = d[10]
        sifat_font = FONT_JINAK if "Jinak" in sifat else FONT_GANAS
        fonts = [FONT_BOLD] + [None]*9 + [sifat_font]
        write_data_row(ws, r2 + 1 + i, d, 1, fonts=fonts)

    total_8 = ["TOTAL", "8 Kelas", 10015, 15316, 6191, 1283, 599, 148, 33552, 1.0, ""]
    write_data_row(ws, r2 + 1 + len(kelas8), total_8, 1, is_total=True)

    # -- C. Binary Target --
    r3 = r2 + 1 + len(kelas8) + 2
    write_section(ws, r3, 1, "C. Distribusi Target Akhir (Benign vs Malignant)", merge_end=6)
    r3 += 1
    write_header_row(ws, r3, [
        "Target", "Label", "Kelas Pembentuk", "Jumlah Citra", "% Proporsi", "Rasio"
    ], 1)

    biner_data = [
        [0, "Benign (Jinak)", "NV (16.643) + BKL (3.668) + VASC (357) + DF (330)", 20998, 0.6258, "1,67 : 1 (mayoritas)"],
        [1, "Malignant (Ganas)", "MEL (6.222) + BCC (4.298) + AKIEC (1.438) + SCC (596)", 12554, 0.3742, "1 : 1,67 (minoritas)"],
    ]
    for i, d in enumerate(biner_data):
        label_font = FONT_JINAK if d[0] == 0 else FONT_GANAS
        label_fill = FILL_JINAK if d[0] == 0 else FILL_GANAS
        fonts = [None, label_font, None, None, None, None]
        fills = [None, label_fill, None, None, None, None]
        write_data_row(ws, r3 + 1 + i, d, 1, fonts=fonts, fills=fills)

    total_biner = ["-", "TOTAL", "8 Kelas Gabungan", 33552, 1.0, "Siap Modeling"]
    write_data_row(ws, r3 + 1 + len(biner_data), total_biner, 1, is_total=True)


# ===========================================================================
# SHEET 4: Statistik Jalur Irisan 3 Kelas
# ===========================================================================
def build_sheet_4(wb):
    ws = wb.create_sheet("4. Statistik Jalur Irisan 3K")
    ws.sheet_properties.tabColor = "27AE60"

    set_col_widths(ws, {1: 16, 2: 28, 3: 14, 4: 14, 5: 14, 6: 16, 7: 20,
                        8: 20, 9: 22})

    write_title(ws, 1, 1,
                "Statistik Dataset Jalur Irisan 3 Kelas (22.051 Citra Bersih)",
                "Hanya 3 jenis diagnosis yang ada di ketiga dataset sekaligus: NV, MEL, BKL",
                merge_end=7)

    # -- A. Per-source distribution --
    r = 4
    write_section(ws, r, 1, "A. Sebaran 3 Kelas per Sumber Dataset", merge_end=7)
    r += 1
    write_header_row(ws, r, [
        "Sumber Dataset", "Partisi", "NV", "MEL", "BKL", "Total", "% Kontribusi"
    ], 1)

    source_data = [
        ["HAM10000", "Part 1 & 2 (100% utuh)", 6705, 1113, 1099, 8917, 0.4044],
        ["ISIC 2019", "Training (non-HAM)", 6170, 3409, 1525, 11104, 0.5036],
        ["ISIC 2017", "Training Data", 804, 227, 252, 1283, 0.0582],
        ["ISIC 2017", "Test Data", 393, 116, 90, 599, 0.0272],
        ["ISIC 2017", "Validation Data", 76, 30, 42, 148, 0.0067],
    ]
    for i, d in enumerate(source_data):
        write_data_row(ws, r + 1 + i, d, 1)

    total_src = ["TOTAL", "3 Dataset", 14148, 4895, 3008, 22051, 1.0]
    write_data_row(ws, r + 1 + len(source_data), total_src, 1, is_total=True)

    # -- B. Class characteristics --
    r2 = r + 1 + len(source_data) + 2
    write_section(ws, r2, 1, "B. Ringkasan 3 Kelas Harmonisasi", merge_end=7)
    r2 += 1
    write_header_row(ws, r2, [
        "Target", "Kode", "Nama Diagnosis Lengkap", "Sifat Klinis",
        "Jumlah Citra", "% Proporsi", "Bobot Loss (Inverse)"
    ], 1)

    class_data = [
        [0, "NV", "Melanocytic Nevus (tahi lalat jinak)", "Jinak", 14148, 0.6416, "0.52 (kelas mayoritas)"],
        [1, "MEL", "Melanoma (kanker kulit ganas)", "Ganas", 4895, 0.2220, "1.50 (perhatian klinis utama)"],
        [2, "BKL", "Benign Keratosis (keratosis seboroik)", "Jinak", 3008, 0.1364, "2.44 (kelas minoritas)"],
    ]
    for i, d in enumerate(class_data):
        sifat = d[3]
        sf = FONT_JINAK if "Jinak" in sifat else FONT_GANAS
        fonts = [None, FONT_BOLD, None, sf, None, None, None]
        write_data_row(ws, r2 + 1 + i, d, 1, fonts=fonts)

    # -- C. Lesion-aware split --
    r3 = r2 + 1 + len(class_data) + 1
    write_section(ws, r3, 1, "C. Partisi Data (Lesion-Aware Split 80:10:10)", merge_end=9)
    r3 += 1
    write_header_row(ws, r3, [
        "Subset", "Rasio Target", "Jumlah Citra", "% Aktual",
        "NV", "MEL", "BKL", "Overlap Lesi", "Status"
    ], 1)

    split_data = [
        ["Training", "80%", 17656, 0.8007, 11302, 3902, 2452, "0 overlap", "Bebas Kebocoran"],
        ["Validation", "10%", 2192, 0.0994, 1455, 450, 287, "0 overlap", "Bebas Kebocoran"],
        ["Test", "10%", 2203, 0.0999, 1391, 543, 269, "0 overlap", "Bebas Kebocoran"],
    ]
    for i, d in enumerate(split_data):
        status_font = Font(name="Segoe UI", size=10, bold=True, color="27AE60")
        fonts = [None]*8 + [status_font]
        fills = [None]*8 + [FILL_LOLOS]
        write_data_row(ws, r3 + 1 + i, d, 1, fonts=fonts, fills=fills)

    total_split = ["TOTAL", "100%", 22051, 1.0, 14148, 4895, 3008, "0 overlap", "Lolos Semua"]
    write_data_row(ws, r3 + 1 + len(split_data), total_split, 1, is_total=True)


# ===========================================================================
# SHEET 5: Audit & Validasi Silang
# ===========================================================================
def build_sheet_5(wb):
    ws = wb.create_sheet("5. Audit & Validasi Silang")
    ws.sheet_properties.tabColor = "E67E22"

    set_col_widths(ws, {1: 38, 2: 28, 3: 18, 4: 18, 5: 52,
                        6: 14, 7: 12, 8: 12, 9: 12, 10: 12, 11: 36})

    write_title(ws, 1, 1,
                "Audit Validasi Silang: Jalur Biner vs Jalur Irisan",
                "Pembuktian bahwa kedua dataset 100% konsisten satu sama lain",
                merge_end=5)

    # -- A. Audit checklist --
    r = 4
    write_section(ws, r, 1, "A. Hasil Audit Komputasional", merge_end=5)
    r += 1
    write_header_row(ws, r, [
        "Yang Diuji", "Hasil", "Standar", "Status", "Keterangan"
    ], 1)

    audit_data = [
        ["Kesesuaian ID citra (irisan ada di biner)",
         "22.051 dari 22.051 (100%)", "100% harus ada", "LOLOS",
         "Semua gambar irisan ada di dalam dataset biner"],
        ["Ketidakcocokan label (label mismatch)",
         "0 kasus (0%)", "0 mismatch", "LOLOS",
         "Label NV, MEL, BKL di kedua dataset sama persis"],
        ["Ketidakcocokan sumber (source mismatch)",
         "0 kasus (0%)", "0 mismatch", "LOLOS",
         "Asal dataset (HAM10k, 2019, 2017) 100% konsisten"],
        ["File fisik citra di disk",
         "1.000 / 1.000 sampel valid", "100% ada", "LOLOS",
         "File JPG terverifikasi ada secara fisik di hard disk"],
        ["Kebocoran lesi antar-subset",
         "0 lesi tumpang tindih", "0 overlap", "LOLOS",
         "StratifiedGroupKFold menjamin tidak ada pasien bocor antar Train/Val/Test"],
        ["Missing value / data kosong",
         "0 missing values", "0 NaN", "LOLOS",
         "Tidak ada baris atau kolom yang kosong"],
    ]
    for i, d in enumerate(audit_data):
        status = d[3]
        status_font = Font(name="Segoe UI", size=10, bold=True, color="27AE60")
        fonts = [None, None, None, status_font, None]
        fills = [None, None, None, FILL_LOLOS, None]
        write_data_row(ws, r + 1 + i, d, 1, fonts=fonts, fills=fills)

    # -- B. Non-intersection breakdown --
    r2 = r + 1 + len(audit_data) + 1
    write_section(ws, r2, 1, "B. Rincian 11.501 Citra yang Tidak Masuk Irisan (Kenapa?)", merge_end=11)
    r2 += 1
    write_header_row(ws, r2, [
        "Sumber Dataset", "AKIEC", "BCC", "BKL", "DF", "MEL", "NV", "SCC", "VASC",
        "Total", "Alasan Tidak Masuk Irisan"
    ], 1)

    non_irisan = [
        ["HAM10000", 327, 514, 0, 115, 0, 0, 0, 142, 1098,
         "Kelas ini (BCC, AKIEC, DF, VASC) tidak ada di ISIC 2017"],
        ["ISIC 2019 Training", 737, 2809, 0, 124, 0, 0, 431, 111, 4212,
         "Kelas ini (BCC, AKIEC, SCC, DF, VASC) tidak ada di ISIC 2017"],
        ["ISIC 2019 Test", 374, 975, 660, 91, 1327, 2495, 165, 104, 6191,
         "Partisi Test ISIC 2019 memang tidak diikutkan dalam protokol irisan"],
    ]
    for i, d in enumerate(non_irisan):
        write_data_row(ws, r2 + 1 + i, d, 1)

    total_non = ["TOTAL", 1438, 4298, 660, 330, 1327, 2495, 596, 357, 11501,
                 "11.501 + 22.051 = 33.552 (pas 100%)"]
    write_data_row(ws, r2 + 1 + len(non_irisan), total_non, 1, is_total=True)


# ===========================================================================
# SHEET 6: Daftar Rujukan Jurnal
# ===========================================================================
def build_sheet_6(wb):
    ws = wb.create_sheet("6. Daftar Rujukan Jurnal")
    ws.sheet_properties.tabColor = "C0392B"

    set_col_widths(ws, {1: 5, 2: 36, 3: 8, 4: 70, 5: 44, 6: 30, 7: 60})

    write_title(ws, 1, 1,
                "Daftar Rujukan Jurnal Internasional",
                "Paper-paper yang menjadi dasar pemetaan label, harmonisasi, dan konsensus biner dalam riset ini",
                merge_end=7)

    r = 4
    write_section(ws, r, 1, "Daftar Lengkap Paper yang Dipakai", merge_end=7)
    r += 1
    write_header_row(ws, r, [
        "No", "Penulis", "Tahun", "Judul Paper (Lengkap)",
        "Nama Jurnal / Konferensi", "Penerbit & Reputasi", "Peran dalam Riset Kita"
    ], 1)

    papers = [
        [1,
         "Tschandl, P., Rosendahl, C., & Kittler, H.",
         2018,
         "The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions",
         "Scientific Data, Vol. 5, Art. 180161",
         "Nature Research (Scopus Q1, IF: 9.8)",
         "Sumber utama dataset HAM10000 (10.015 citra) dan dasar resmi penggabungan Seborrheic Keratosis ke BKL."],
        [2,
         "Codella, N. C. F., Gutman, D., Celebi, M. E., et al.",
         2018,
         "Skin lesion analysis toward melanoma detection: A challenge at the 2017 International Symposium on Biomedical Imaging (ISBI), hosted by the ISIC",
         "2018 IEEE 15th International Symposium on Biomedical Imaging (ISBI), hal. 168-172",
         "IEEE (Sitasi 1.200+)",
         "Benchmark resmi perumusan 3 kelas standar dunia (Melanoma, Nevus, Seborrheic Keratosis) di ISIC 2017 Challenge."],
        [3,
         "Baig, A. R., Abbas, Q., Almakki, R., et al.",
         2023,
         "Light-Dermo: A lightweight pretrained convolution neural network for the diagnosis of multiclass skin lesions",
         "Diagnostics, Vol. 13, No. 3, Art. 385",
         "MDPI (Scopus Q2, IF: 3.6)",
         "Rujukan penggabungan multi-dataset HAM10000 & ISIC 2019 serta eliminasi duplikasi citra lesi."],
        [4,
         "Ichim, L., Mitrica, R. I., Serghei, M. O., & Popescu, D.",
         2023,
         "Detection of malignant skin lesions based on decision fusion of ensembles of neural networks",
         "Cancers, Vol. 15, No. 20, Art. 4946",
         "MDPI (Scopus Q1, IF: 5.2)",
         "Protokol pembersihan overlap citra lesi ganda antar-arsip ISIC untuk mencegah data leakage."],
        [5,
         "Barata, C., Celebi, M. E., & Marques, J. S.",
         2020,
         "Explainable skin lesion diagnosis using taxonomies",
         "Pattern Recognition, Vol. 110, Art. 107413",
         "Elsevier (Scopus Q1, IF: 8.0)",
         "Rujukan pemetaan biner ISIC 2017: Melanoma = Ganas, Nevus & Keratosis = Jinak."],
        [6,
         "Jojoa Acosta, M. F., Caballero Tovar, L. Y., et al.",
         2021,
         "Melanoma diagnosis using deep learning techniques on dermatoscopic images",
         "BMC Medical Imaging, Vol. 21, Art. 6",
         "Springer Nature (Scopus Q2, IF: 2.7)",
         "Rujukan pemetaan biner ISIC 2017 untuk deteksi melanoma menggunakan Mask R-CNN."],
        [7,
         "Kousis, I., Perikos, I., Hatzilygeroudis, I., & Virvou, M.",
         2022,
         "Deep Learning Methods for Accurate Skin Cancer Recognition and Mobile Application",
         "Electronics, Vol. 11, No. 9, Art. 1294",
         "MDPI (Scopus Q2, IF: 2.9)",
         "Konsensus biner HAM10000: NV, BKL, VASC, DF = Jinak; MEL, BCC, AKIEC = Ganas."],
        [8,
         "Ghosh, P., Azam, S., Quadir, R., Karim, A., et al.",
         2022,
         "SkinNet-16: A deep learning approach to identify benign and malignant skin lesions",
         "Frontiers in Oncology, Vol. 12, Art. 931141",
         "Frontiers Media (Scopus Q2, IF: 4.7)",
         "Konsensus biner HAM10000: 4 kelas Jinak dan 3 kelas Ganas."],
        [9,
         "Harangi, B., Baran, A., & Hajdu, A.",
         2020,
         "Assisted deep learning framework for multi-class skin lesion classification considering a binary classification support",
         "Biomedical Signal Processing and Control, Vol. 62, Art. 102041",
         "Elsevier (Scopus Q1, IF: 5.1)",
         "Analisis transisi multiclass ke binary classification pada dataset ISIC 2018 / HAM10000."],
        [10,
         "Yao, B., Jin, A., Liu, H., & Li, Q.",
         2026,
         "MorphoNet: An Interpretable Hierarchical Deep Learning Framework for Multi-Class Skin Lesion Classification Using Dermoscopic Images",
         "Bioengineering, Vol. 13, No. 9, Art. 989",
         "MDPI (Scopus Q2, IF: 4.0)",
         "Pemetaan biner 8 kelas ISIC 2019: NV, BKL, DF, VASC = Benign; MEL, BCC, AK, SCC = Malignant."],
    ]

    for i, d in enumerate(papers):
        write_data_row(ws, r + 1 + i, d, 1)
        # Set row height for readability
        ws.row_dimensions[r + 1 + i].height = 45


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    wb = openpyxl.Workbook()

    print("Membangun Sheet 1: Ringkasan Komparatif...")
    build_sheet_1(wb)

    print("Membangun Sheet 2: Harmonisasi & Konsensus...")
    build_sheet_2(wb)

    print("Membangun Sheet 3: Statistik Jalur Biner...")
    build_sheet_3(wb)

    print("Membangun Sheet 4: Statistik Jalur Irisan 3K...")
    build_sheet_4(wb)

    print("Membangun Sheet 5: Audit & Validasi Silang...")
    build_sheet_5(wb)

    print("Membangun Sheet 6: Daftar Rujukan Jurnal...")
    build_sheet_6(wb)

    # Freeze panes for all sheets (freeze row 1-2 title area)
    for ws in wb.worksheets:
        ws.sheet_view.showGridLines = False

    outfile = "rekap_dataset_biner_dan_irisan improve.xlsx"
    try:
        wb.save(outfile)
        print(f"\nBerhasil dibuat: {outfile}")
    except PermissionError:
        outfile2 = "rekap_dataset_biner_dan_irisan improve_v2.xlsx"
        wb.save(outfile2)
        print(f"\nFile utama sedang terbuka. Disimpan sebagai: {outfile2}")
        print(f"Tutup file lama di Excel, lalu rename '{outfile2}' -> '{outfile}'.")


if __name__ == "__main__":
    main()
