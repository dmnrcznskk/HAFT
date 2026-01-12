import sys
import csv
import numpy as np
import cv2
from PIL import Image
from collections import Counter
from scipy.spatial.distance import cdist
import warnings

# --- PATCH ---
if not hasattr(np, "warnings"):
    np.warnings = warnings

# --- USTAWIENIA ---
INPUT_IMAGE = "grzib.jpg"
OUTPUT_IMAGE = "final_wzor.png"
CSV_PATH = "dmc_dict.csv"

WIDTH_CM = 30.0
AIDA_COUNT = 14
NUM_COLORS = 20
THRESHOLD_PERCENTAGE = 0.0001

# --- DMC ---
def load_dmc_palette(csv_path):
    dmc_colors = []
    dmc_matrix = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 5:
                continue
            try:
                r, g, b = int(row[1]), int(row[2]), int(row[3])
                dmc_colors.append({
                    "id": row[0],
                    "rgb": (r, g, b),
                    "name": row[4]
                })
                dmc_matrix.append([r, g, b])
            except ValueError:
                continue

    return dmc_colors, np.array(dmc_matrix)

# --- SKALOWANIE ---
def scale_to_stitches(img, width_cm, aida_count):
    stitches_per_cm = aida_count / 2.54
    target_width = int(width_cm * stitches_per_cm)
    target_height = int(target_width * img.height / img.width)
    return img.resize((target_width, target_height), Image.Resampling.LANCZOS)

# --- NARZĘDZIA ---
def get_img_data(img_input, conversion_method):
    img_array = np.array(img_input)
    img = cv2.cvtColor(img_array, conversion_method)
    flat = img.reshape((-1, 3)).astype(np.float32)
    return img, img.shape[0] * img.shape[1], flat

def process_result(center, label, shape, conversion_method):
    center = np.uint8(center)
    img = center[label].reshape(shape)
    img = cv2.cvtColor(img, conversion_method)
    return Image.fromarray(img)

def update_nb_colours(label, nb_pixels, threshold, nb_colours):
    counts = Counter(label.flatten())
    removed = sum(1 for c in counts.values() if c / nb_pixels < threshold)
    if removed > 0:
        nb_colours += removed // 2 + removed % 2
    return nb_colours, removed

# --- KMEANS OPENCV (LAB) ---
def quantize_opencv_lab(img_input):
    img, nb_pixels, flat = get_img_data(img_input, cv2.COLOR_RGB2Lab)

    current_colors = NUM_COLORS
    under_threshold = current_colors
    iteration = 0

    while under_threshold > 0 and iteration < 5:
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(
            flat,
            current_colors,
            None,
            criteria,
            10,
            cv2.KMEANS_PP_CENTERS
        )
        current_colors, under_threshold = update_nb_colours(
            labels, nb_pixels, THRESHOLD_PERCENTAGE, current_colors
        )
        iteration += 1

    return process_result(centers, labels.flatten(), img.shape, cv2.COLOR_Lab2RGB)

# --- MAPOWANIE NA DMC ---
def map_to_dmc(image, dmc_colors, dmc_matrix):
    arr = np.array(image)
    h, w, _ = arr.shape
    pixels = arr.reshape((-1, 3))

    unique_colors = np.unique(pixels, axis=0)
    distances = cdist(unique_colors, dmc_matrix)
    closest = np.argmin(distances, axis=1)

    color_map = {}
    used_threads = set()

    print("\n--- LISTA ZAKUPÓW (DMC) ---")
    for i, idx in enumerate(closest):
        orig = tuple(unique_colors[i])
        dmc = dmc_colors[idx]
        color_map[orig] = dmc["rgb"]

        if dmc["id"] not in used_threads:
            print(f"DMC {dmc['id']} - {dmc['name']}")
            used_threads.add(dmc["id"])

    final_pixels = np.array([color_map[tuple(p)] for p in pixels], dtype=np.uint8)
    return Image.fromarray(final_pixels.reshape((h, w, 3)))

# --- MAIN ---
if __name__ == "__main__":
    try:
        img = Image.open(INPUT_IMAGE).convert("RGB")
    except FileNotFoundError:
        print("Nie znaleziono pliku wejściowego")
        sys.exit(1)

    print("Ładowanie DMC...")
    dmc_list, dmc_matrix = load_dmc_palette(CSV_PATH)

    print("Skalowanie...")
    base = scale_to_stitches(img, WIDTH_CM, AIDA_COUNT)
    print(f"Rozmiar haftu: {base.width} x {base.height}")

    print("Kwantyzacja (OpenCV LAB)...")
    quantized = quantize_opencv_lab(base)

    print("Mapowanie na DMC...")
    final_img = map_to_dmc(quantized, dmc_list, dmc_matrix)

    final_img.save(OUTPUT_IMAGE)
    print(f"\nGotowe. Zapisano: {OUTPUT_IMAGE}")
