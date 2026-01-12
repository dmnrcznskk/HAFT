import os
import sys
import json

# Fix importów
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from process_image import process_image 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DMC_CSV_PATH już nie jest potrzebne tutaj, bo jest zaszyte w process_image.py
INPUT_FILE = os.path.join(BASE_DIR, "ludzie.jpg") 
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs_test")

def run_test():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"--- TEST ---")
    
    if not os.path.exists(INPUT_FILE):
        print(f"Brak pliku wejściowego: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "rb") as f:
        # Wywołanie funkcji BEZ argumentu dmc_csv_path
        result = process_image(
            image_file=f,
            num_colors=30,
            width_cm=30.0,
            aida_count=14
        )

    # Zapis wyników
    json_path = os.path.join(OUTPUT_DIR, "result.json")
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(result["pattern_data"], jf, indent=2, ensure_ascii=False)
    
    with open(os.path.join(OUTPUT_DIR, "preview.png"), "wb") as pf:
        pf.write(result["preview_png"].getvalue())
        
    with open(os.path.join(OUTPUT_DIR, "chart.png"), "wb") as cf:
        cf.write(result["chart_png"].getvalue())

    print(f"Gotowe. Wyniki w {OUTPUT_DIR}")

if __name__ == "__main__":
    run_test()