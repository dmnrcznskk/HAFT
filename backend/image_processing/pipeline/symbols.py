from PIL import Image, ImageDraw, ImageFont

# Lista symboli (zwykłe znaki + Unicode, jeśli masz font)
AVAILABLE_SYMBOLS = list(
    "1234567890"
    "ABCDEFGHJKLMNPRSTUVWXYZ" 
    "abcdefghjkmnpqrstuvwxyz"
    "?!@#$%&+=^~<>"
    "■□▲△▼▽●○♦◊★☆♠♣♥♦"
    "←↑→↓↔↕"
)

def assign_symbols(dmc_used_indices):
    """
    Przypisuje unikalny symbol do każdego lokalnego indeksu palety.
    Zwraca słownik: { local_id (int): symbol (str) }
    """
    symbol_map = {}
    total_symbols = len(AVAILABLE_SYMBOLS)
    
    # dmc_used_indices to lista użytych ID nici. 
    # Ich pozycja w liście to nasz local_id (0, 1, 2...)
    for local_id, _ in enumerate(dmc_used_indices):
        sym = AVAILABLE_SYMBOLS[local_id % total_symbols]
        symbol_map[local_id] = sym
        
    return symbol_map

def generate_symbol_chart(grid_matrix, palette, symbol_map, cell_size=20):
    """
    Generuje obraz z siatką symboli.
    """
    height = len(grid_matrix)
    width = len(grid_matrix[0])
    
    img_w = width * cell_size
    img_h = height * cell_size
    
    chart_img = Image.new("RGB", (img_w, img_h), (255, 255, 255))
    draw = ImageDraw.Draw(chart_img)
    
    # Próba załadowania fontu wspierającego Unicode
    font = None
    try:
        # Windows/macOS standard
        font = ImageFont.truetype("arial.ttf", int(cell_size * 0.6))
    except IOError:
        try:
            # Linux fallback
            font = ImageFont.truetype("DejaVuSans.ttf", int(cell_size * 0.6))
        except IOError:
            font = ImageFont.load_default()

    # 1. Rysowanie symboli
    for y in range(height):
        for x in range(width):
            local_id = grid_matrix[y][x]
            symbol = symbol_map.get(local_id, "?")
            
            # Środek kratki
            center_x = x * cell_size + cell_size / 2
            center_y = y * cell_size + cell_size / 2
            
            # Rysowanie
            # (Uproszczone centrowanie dla kompatybilności ze starszym Pillow)
            try:
                draw.text((center_x, center_y), symbol, fill=(0, 0, 0), font=font, anchor="mm")
            except ValueError:
                # Bardzo stary Pillow
                draw.text((center_x - 5, center_y - 5), symbol, fill=(0, 0, 0), font=font)

    # 2. Linie siatki
    for x in range(width + 1):
        line_x = x * cell_size
        width_line = 3 if x % 10 == 0 else 1
        fill_col = (0,0,0) if x % 10 == 0 else (180,180,180)
        draw.line([(line_x, 0), (line_x, img_h)], fill=fill_col, width=width_line)
        
    for y in range(height + 1):
        line_y = y * cell_size
        width_line = 3 if y % 10 == 0 else 1
        fill_col = (0,0,0) if y % 10 == 0 else (180,180,180)
        draw.line([(0, line_y), (img_w, line_y)], fill=fill_col, width=width_line)

    return chart_img