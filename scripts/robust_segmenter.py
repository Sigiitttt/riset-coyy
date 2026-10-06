import cv2
import numpy as np

def segment_dermoscopy_robust(img_rgb):
    """
    Segmentasi adaptif multi-komponen untuk citra dermatoskopi:
    1. Eliminasi sudut hitam vignette via FloodFill dari 4 sudut
    2. Deteksi kontras lesi via kanal L* (Lightness) ruang warna Lab
    3. Penggabungan klaster lesi multikomponen (tidak memotong lesi besar menjadi bintik kecil)
    4. Safe Fallback: Jika kontras terlalu rendah/halus, tidak memaksakan crop bintik kecil.
    """
    h, w = 224, 224
    if img_rgb.shape[:2] != (h, w):
        img = cv2.resize(img_rgb, (w, h), interpolation=cv2.INTER_AREA)
    else:
        img = img_rgb.copy()
        
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # 1. Deteksi sudut hitam vignette dengan floodFill dari 4 sudut gambar
    ff_mask = np.zeros((h + 2, w + 2), np.uint8)
    for pt in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        if gray[pt[1], pt[0]] < 40:
            cv2.floodFill(gray.copy(), ff_mask, pt, 255, 15, 15, cv2.FLOODFILL_MASK_ONLY | (255 << 8))

    corner_vignette = (ff_mask[1:-1, 1:-1] == 255)
    skin_fov = ~corner_vignette
    
    # 2. Kanal L* dari Lab space (standar pengolahan citra dermatologi)
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l_channel = lab[:, :, 0]
    
    # Gaussian blur untuk menyatukan tekstur mikroskopis lesi
    blurred = cv2.GaussianBlur(l_channel, (15, 15), 0)
    
    valid_l = blurred[skin_fov]
    if len(valid_l) < 500:
        return np.ones((h, w), dtype=np.uint8) * 255, False
    
    otsu_val, _ = cv2.threshold(valid_l.reshape(-1, 1), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Lesi adalah area dalam skin_fov yang lebih gelap dari threshold kulit
    lesion_mask = np.zeros((h, w), dtype=np.uint8)
    lesion_mask[(blurred < otsu_val) & skin_fov] = 255
    
    # Morfologi closing besar untuk menyatukan pulau-pulau lesi yang tersebar
    k_merge = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    lesion_mask = cv2.morphologyEx(lesion_mask, cv2.MORPH_CLOSE, k_merge)
    
    cnts, _ = cv2.findContours(lesion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    final_mask = np.zeros((h, w), dtype=np.uint8)
    
    if cnts:
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
        max_area = cv2.contourArea(cnts[0])
        
        # Ambil kontur terbesar DAN kontur signifikan lainnya (multikomponen)
        chosen = [c for c in cnts if cv2.contourArea(c) >= max_area * 0.15 and cv2.contourArea(c) > 80]
        for c in chosen:
            cv2.drawContours(final_mask, [c], -1, 255, -1)
            
        # Safe Fallback: Jika luas lesi yang terdeteksi < 3.5% dari luas gambar,
        # ini adalah lesi difus/kontras sangat rendah (seperti seborrheic keratosis pucat).
        # Jangan potong jadi bintik kecil, gunakan seluruh area kulit FOV agar fitur lesi tidak hilang!
        mask_area = np.count_nonzero(final_mask)
        if mask_area < (h * w * 0.035):
            final_mask = (skin_fov * 255).astype(np.uint8)
            return final_mask, False
        else:
            return final_mask, True
    else:
        final_mask = (skin_fov * 255).astype(np.uint8)
        return final_mask, False
