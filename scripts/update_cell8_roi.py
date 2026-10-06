import json

fpath = 'kode/5_segmentasi_unet/sk3_bigdat_ham2019_unetmask_ak85_v2 (1).ipynb'
with open(fpath, encoding='utf-8') as f:
    nb = json.load(f)

new_cell8_code = '''# ==========================================
# TAHAP 3: REKAYASA CITRA (ROI CROP + HAIR REMOVAL + CLAHE)
# PIPELINE: HAIR REMOVAL -> LESION ROI CROP (15% PADDING) -> CLAHE -> PAD & RESIZE 224
# ==========================================
import os
import cv2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

cv2.setNumThreads(1)
TARGET_SIZE = 224
REF_SIZE = 600

def remove_hair(img_rgb):
    """Black-hat (ukuran kernel ikut resolusi) -> threshold -> dilasi -> inpainting."""
    h, w = img_rgb.shape[:2]
    k = max(9, int(round(9 * max(h, w) / REF_SIZE)) | 1)   # selalu ganjil, minimal 9
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (k, k))
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
    _, hair_mask = cv2.threshold(blackhat, 10, 255, cv2.THRESH_BINARY)
    hair_mask = cv2.dilate(
        hair_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=1
    )
    return cv2.inpaint(img_rgb, hair_mask, 3, cv2.INPAINT_TELEA)

def crop_lesion_roi(img_rgb, mask_path, padding_ratio=0.15):
    """
    Menggunakan mask untuk mencari bounding box lesi,
    kemudian crop dengan padding 15% agar tetap ada konteks kulit sehat di sekitarnya.
    """
    h, w = img_rgb.shape[:2]
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        return img_rgb, np.full((h, w), 255, dtype=np.uint8)

    if mask.shape != (h, w):
        mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_LINEAR)

    mask_bin = (mask > 127).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_clean = cv2.morphologyEx(mask_bin, cv2.MORPH_CLOSE, kernel)

    ys, xs = np.where(mask_clean > 0)
    if len(xs) == 0 or len(ys) == 0:
        return img_rgb, mask_clean

    x1, x2 = xs.min(), xs.max()
    y1, y2 = ys.min(), ys.max()

    lesion_w = x2 - x1 + 1
    lesion_h = y2 - y1 + 1

    pad_x = int(lesion_w * padding_ratio)
    pad_y = int(lesion_h * padding_ratio)

    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(w, x2 + pad_x + 1)
    y2 = min(h, y2 + pad_y + 1)

    roi = img_rgb[y1:y2, x1:x2]
    return roi, mask_clean

def apply_enhancement(img_rgb):
    """ CLAHE untuk penajaman tekstur lesi (Tanpa Blur) """
    img = img_rgb.astype('uint8')
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    clahe_img = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
    return clahe_img

def pad_and_resize(img, target_size=224, is_mask=False):
    """ Letterbox padding reflect agar lesi tidak terdistorsi/gepeng """
    h, w = img.shape[:2]
    max_dim = max(h, w)
    top, bottom = (max_dim - h) // 2, (max_dim - h) - ((max_dim - h) // 2)
    left, right = (max_dim - w) // 2, (max_dim - w) - ((max_dim - w) // 2)
    border_mode = cv2.BORDER_CONSTANT if is_mask else cv2.BORDER_REFLECT
    padded = cv2.copyMakeBorder(img, top, bottom, left, right, border_mode)
    interp = cv2.INTER_LINEAR if is_mask else cv2.INTER_AREA
    return cv2.resize(padded, (target_size, target_size), interpolation=interp)

def plot_perbandingan(asli, bersih, mask, roi, final_img, index):
    """ Menampilkan plot 5 tahap preprocessing berdampingan """
    fig, axes = plt.subplots(1, 5, figsize=(18, 4))
    axes[0].imshow(asli)
    axes[0].set_title(f"1. Asli (Img {index})")
    axes[0].axis('off')

    axes[1].imshow(bersih)
    axes[1].set_title("2. Tanpa Rambut")
    axes[1].axis('off')

    axes[2].imshow(mask, cmap='gray')
    axes[2].set_title("3. Mask U-Net / Dokter")
    axes[2].axis('off')

    axes[3].imshow(roi)
    axes[3].set_title("4. ROI Crop (Pad 15%)")
    axes[3].axis('off')

    axes[4].imshow(final_img)
    axes[4].set_title("5. CLAHE + Resize (224x224)")
    axes[4].axis('off')

    plt.tight_layout()
    plt.show()

# ==========================================
# OFFLINE PREPROCESSING (MULTI-THREADED PARALEL)
# ==========================================

output_dir = str(WORK_DIR / "processed_images_roi") + "/"
os.makedirs(output_dir, exist_ok=True)

# 1. Visualisasi 3 Sampel Pertama sebagai Pengecekan Kualitas
print("[INFO] Menampilkan visualisasi 3 sampel citra pertama:")
for index, row in df_final.head(3).iterrows():
    img_bgr = cv2.imread(row['filepath'])
    if img_bgr is not None:
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        clean_img = remove_hair(img_rgb)
        roi_img, mask_full = crop_lesion_roi(clean_img, row['mask_path'], padding_ratio=0.15)
        enhanced_roi = apply_enhancement(roi_img)
        final_img = pad_and_resize(enhanced_roi, target_size=TARGET_SIZE, is_mask=False)
        plot_perbandingan(img_rgb, clean_img, mask_full, roi_img, final_img, index)

# 2. Fungsi Worker untuk Eksekusi Paralel Multi-Core
def process_single_image(args):
    index, img_path, mask_path = args
    filename = f"{index}_{os.path.basename(img_path)}"
    new_img_path = os.path.join(output_dir, filename)

    if os.path.exists(new_img_path):
        return index, new_img_path

    img = cv2.imread(img_path)
    if img is None:
        return index, img_path

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # 1. Hair removal
    clean_img = remove_hair(img)
    # 2. Ambil ROI lesi berdasarkan mask (+15% padding konteks kulit)
    roi_img, _ = crop_lesion_roi(clean_img, mask_path, padding_ratio=0.15)
    # 3. CLAHE pada ROI lesi
    enhanced_roi = apply_enhancement(roi_img)
    # 4. Letterbox pad & resize ke 224x224
    final_img = pad_and_resize(enhanced_roi, target_size=TARGET_SIZE, is_mask=False)

    final_bgr = cv2.cvtColor(final_img, cv2.COLOR_RGB2BGR)
    cv2.imwrite(new_img_path, final_bgr)
    return index, new_img_path

# 3. Jalankan Eksekusi Multi-Threaded dengan Seluruh CPU Cores
tasks = [(idx, row['filepath'], row['mask_path']) for idx, row in df_final.iterrows()]
num_workers = os.cpu_count() or 4   # Colab A100 = 12 vCPU
print(f"[INFO] Memproses {len(tasks):,} gambar secara paralel menggunakan {num_workers} worker CPU...")

with ThreadPoolExecutor(max_workers=num_workers) as executor:
    results = list(tqdm(executor.map(process_single_image, tasks), total=len(tasks)))

# 4. Susun Kembali Path Sesuai Indeks Asli
results.sort(key=lambda x: x[0])
df_final['filepath'] = [r[1] for r in results]
df_final.to_csv(str(WORK_DIR / "processed_metadata_combined.csv"), index=False)

print(f"\\n[INFO] Selesai! Sebanyak {len(results):,} citra ROI tersegmentasi siap digunakan.")
'''

nb['cells'][8]['source'] = new_cell8_code.splitlines(keepends=True)
# Reset cell 8 outputs for fresh run
nb['cells'][8]['outputs'] = []
nb['cells'][8]['execution_count'] = None

with open(fpath, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Cell 8 berhasil diperbarui dengan ROI Crop!")
