import sys
import csv
import numpy as np
from PIL import Image, ImageEnhance
from scipy.spatial.distance import cdist

# --- USTAWIENIA ---
INPUT_IMAGE = "dick.jpg"      # Tu wpisz nazwę swojego zdjęcia
OUTPUT_IMAGE = "final_wzor.png"
CSV_PATH = "dmc_dict.csv"      # Twój plik z kolorami
WIDTH_CM = 30.0
AIDA_COUNT = 14
NUM_COLORS = 30

# --- 1. Ładowanie DMC ---
def load_dmc_palette(csv_path):
    dmc_colors = []
    dmc_rgb_matrix = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or len(row) < 5: continue
                try:
                    # Zakładamy strukturę: id, r, g, b, nazwa
                    r, g, b = int(row[1]), int(row[2]), int(row[3])
                    dmc_colors.append({'id': row[0], 'rgb': (r, g, b), 'name': row[4]})
                    dmc_rgb_matrix.append([r, g, b])
                except ValueError: continue
        return dmc_colors, np.array(dmc_rgb_matrix)
    except Exception as e:
        print(f"Błąd CSV: {e}")
        sys.exit(1)

# --- 2. Skalowanie ---
def scale_to_stitches(img, width_cm, aida_count):
    stitches_per_cm = aida_count / 2.54
    target_width = int(width_cm * stitches_per_cm)
    aspect_ratio = img.height / img.width
    target_height = int(target_width * aspect_ratio)
    # LANCZOS jest najlepszy do zachowania jakości przy zmniejszaniu
    return img.resize((target_width, target_height), Image.Resampling.LANCZOS)

# --- 3. Główna Magia: Max Coverage -> DMC ---
def process_max_coverage_to_dmc(image, dmc_colors, dmc_matrix, num_colors):
    # Krok A: Używamy Pillow Max Coverage (method=1) żeby znaleźć te 20 kluczowych kolorów
    # To jest ten moment, gdzie pysk małpy zostaje "uratowany"
    print(f"1. Wybieranie {num_colors} kolorów metodą Max Coverage...")
    quantized_temp = image.quantize(colors=num_colors, method=1, kmeans=0).convert("RGB")
    
    # Pobieramy piksele jako tablicę numpy
    img_array = np.array(quantized_temp)
    h, w, d = img_array.shape
    pixels = img_array.reshape((h * w, d))
    
    # Znajdujemy unikalne kolory, które wybrał algorytm (powinno być ich max 20)
    unique_colors = np.unique(pixels, axis=0)
    print(f"   Znaleziono {len(unique_colors)} unikalnych kolorów we wstępnym wzorze.")

    # Krok B: Mapujemy te unikalne kolory na nici DMC
    print("2. Tłumaczenie kolorów na nici DMC...")
    distances = cdist(unique_colors, dmc_matrix, 'euclidean')
    closest_indices = np.argmin(distances, axis=1)
    
    # Tworzymy słownik: {stary_kolor_rgb: nowy_kolor_dmc_rgb}
    color_map = {}
    used_threads = set()
    
    print("\n--- LISTA ZAKUPÓW (Nici DMC) ---")
    for i, idx in enumerate(closest_indices):
        original_rgb = tuple(unique_colors[i])
        dmc_match = dmc_colors[idx]
        dmc_rgb = tuple(dmc_match['rgb'])
        
        color_map[original_rgb] = dmc_rgb
        
        # Wypisz nić tylko jeśli jeszcze jej nie było na liście
        if dmc_match['id'] not in used_threads:
            print(f"DMC {dmc_match['id']} - {dmc_match['name']}")
            used_threads.add(dmc_match['id'])

    # Krok C: Podmieniamy piksele na obrazku
    final_pixels = np.zeros_like(pixels)
    for i in range(len(pixels)):
        final_pixels[i] = color_map[tuple(pixels[i])]
        
    final_image = Image.fromarray(final_pixels.reshape((h, w, d)).astype(np.uint8))
    return final_image

# --- MAIN ---
if __name__ == "__main__":
    print(f"Wczytuję {INPUT_IMAGE}...")
    try:
        img = Image.open(INPUT_IMAGE).convert("RGB")
    except FileNotFoundError:
        print("Nie znaleziono pliku!")
        sys.exit()

    print("Ładowanie bazy DMC...")
    dmc_list, dmc_matrix = load_dmc_palette(CSV_PATH)

    print("Skalowanie...")
    base_img = scale_to_stitches(img, WIDTH_CM, AIDA_COUNT)
    print(f"Wymiary haftu: {base_img.width} x {base_img.height} krzyżyków")

    # Opcjonalnie: Lekkie podbicie kolorów przed algorytmem
    # base_img = ImageEnhance.Color(base_img).enhance(1.2)

    final_img = process_max_coverage_to_dmc(base_img, dmc_list, dmc_matrix, NUM_COLORS)
    
    final_img.save(OUTPUT_IMAGE)
    print(f"\nGotowe! Zapisano jako: {OUTPUT_IMAGE}")
    print("Porada: Otwórz ten plik i przybliż, żeby zobaczyć pojedyncze krzyżyki.")