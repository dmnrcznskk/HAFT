import sys
from PIL import Image, ImageDraw, ImageFont

# --- KONFIGURACJA ---
INPUT_IMAGE = "final_wzor.png"  # Twój plik z poprzedniego kroku
OUTPUT_PATTERN = "wzor_z_siatka.png"

BLOCK_SIZE = 25       # Jak duży (w pikselach) ma być jeden krzyżyk na ekranie
GRID_COLOR = (180, 180, 180) # Kolor cienkiej siatki (szary)
MAJOR_GRID_COLOR = (60, 60, 60) # Kolor grubych linii co 10 (ciemnoszary)
TEXT_COLOR = (0, 0, 0) # Kolor numerków
BACKGROUND_COLOR = (255, 255, 255) # Białe tło pod numerki

def create_grid_pattern(input_path, output_path):
    try:
        # 1. Wczytanie obrazu
        img = Image.open(input_path).convert("RGB")
        w_stitches, h_stitches = img.size
        print(f"Wymiary wzoru: {w_stitches}x{h_stitches} krzyżyków.")

        # 2. Obliczenie nowego rozmiaru (z marginesami na numerki)
        margin_left = 60
        margin_top = 40
        
        # Szerokość nowego obrazu = margines + (liczba_krzyzyków * rozmiar_kratki) + mały zapas
        new_w = margin_left + (w_stitches * BLOCK_SIZE) + 1
        new_h = margin_top + (h_stitches * BLOCK_SIZE) + 1

        # Tworzymy puste, białe płótno
        pattern_img = Image.new("RGB", (new_w, new_h), BACKGROUND_COLOR)
        draw = ImageDraw.Draw(pattern_img)

        # 3. Wklejenie powiększonych pikseli
        # Skalujemy oryginalny obrazek metodą Nearest Neighbor (zachowuje ostre krawędzie pikseli)
        resized_img = img.resize((w_stitches * BLOCK_SIZE, h_stitches * BLOCK_SIZE), Image.Resampling.NEAREST)
        
        # Wklejamy go na nasze płótno, przesuwając o margines
        pattern_img.paste(resized_img, (margin_left, margin_top))

        # Spróbujmy załadować domyślny font (może być mały, ale zadziała wszędzie)
        try:
            # Jeśli masz jakiś font ttf w systemie, możesz tu podać ścieżkę, np. "arial.ttf"
            font = ImageFont.load_default()
        except:
            font = None

        # 4. Rysowanie Siatki PIONOWEJ (kolumny)
        for x in range(w_stitches + 1):
            # Pozycja X na obrazku
            pos_x = margin_left + (x * BLOCK_SIZE)
            
            is_major = (x % 10 == 0) # Co 10 linia jest gruba
            
            line_color = MAJOR_GRID_COLOR if is_major else GRID_COLOR
            line_width = 3 if is_major else 1
            
            # Rysuj linię od góry do dołu
            draw.line([(pos_x, margin_top), (pos_x, new_h)], fill=line_color, width=line_width)

            # Dodaj numerek na górze (tylko przy głównych liniach i nie na ostatniej)
            if is_major and x < w_stitches and x > 0:
                text = str(x)
                # Centrowanie tekstu (z grubsza)
                draw.text((pos_x - 5, margin_top - 15), text, fill=TEXT_COLOR, font=font)

        # 5. Rysowanie Siatki POZIOMEJ (wiersze)
        for y in range(h_stitches + 1):
            # Pozycja Y na obrazku
            pos_y = margin_top + (y * BLOCK_SIZE)
            
            is_major = (y % 10 == 0)
            
            line_color = MAJOR_GRID_COLOR if is_major else GRID_COLOR
            line_width = 3 if is_major else 1
            
            # Rysuj linię od lewej do prawej
            draw.line([(margin_left, pos_y), (new_w, pos_y)], fill=line_color, width=line_width)

            # Dodaj numerek z lewej
            if is_major and y < h_stitches and y > 0:
                text = str(y)
                draw.text((margin_left - 25, pos_y - 6), text, fill=TEXT_COLOR, font=font)

        # 6. Zapis
        pattern_img.save(output_path)
        print(f"Gotowe! Zapisano siatkę jako: {output_path}")

    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {input_path}")

if __name__ == "__main__":
    # Możesz podać pliki jako argumenty: python make_grid.py input.png output.png
    if len(sys.argv) >= 3:
        create_grid_pattern(sys.argv[1], sys.argv[2])
    else:
        create_grid_pattern(INPUT_IMAGE, OUTPUT_PATTERN)