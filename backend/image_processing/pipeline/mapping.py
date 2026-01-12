import numpy as np
from PIL import Image

def map_image_to_dmc(img: Image.Image, dmc_colors, dmc_matrix):
    # 1. Przygotuj dane
    arr = np.array(img)
    h, w, _ = arr.shape
    pixels = arr.reshape((-1, 3)).astype(np.float32)
    
    palette = np.array(dmc_matrix, dtype=np.float32)

    # 2. Obliczenia Redmean (Ważone RGB) - Twoja sprawdzona matematyka
    diff = pixels[:, np.newaxis, :] - palette[np.newaxis, :, :]
    rmean = (pixels[:, np.newaxis, 0] + palette[np.newaxis, :, 0]) / 2.0
    
    weight_r = 2.0 + rmean / 256.0
    weight_g = 4.0
    weight_b = 2.0 + (255.0 - rmean) / 256.0

    r = diff[:, :, 0]
    g = diff[:, :, 1]
    b = diff[:, :, 2]

    dist_sq = (weight_r * (r ** 2)) + (weight_g * (g ** 2)) + (weight_b * (b ** 2))

    # 3. Znajdź indeksy (Globalne ID z pliku CSV)
    closest_indices = np.argmin(dist_sq, axis=1)

    # 4. Rekonstrukcja obrazu (dla podglądu PNG)
    new_pixels = np.array([dmc_colors[idx]["rgb"] for idx in closest_indices], dtype=np.uint8)
    new_img = Image.fromarray(new_pixels.reshape((h, w, 3)))

    # 5. Budowa siatki indeksów (To jest ten trzeci element, którego brakowało!)
    indices_grid = closest_indices.reshape((h, w)).astype(int)
    
    # ZWRACAMY 3 WARTOŚCI:
    # 1. Obrazek (do PNG)
    # 2. None (żeby zachować kompatybilność pozycyjną, dawniej used_indices)
    # 3. indices_grid (do budowania JSON-a)
    return new_img, None, indices_grid