import json
import numpy as np
import io
import os  # <--- WAŻNE
from PIL import Image

from pipeline.scaling import scale_to_stitches
from pipeline.quantization import quantize_opencv_lab
from pipeline.dmc import load_dmc_palette
from pipeline.mapping import map_image_to_dmc 
from pipeline.grid import build_grid_payload
from pipeline.symbols import assign_symbols, generate_symbol_chart

def process_image(
    image_file, 
    num_colors: int,
    width_cm: float,
    aida_count: int
):

    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    dmc_csv_path = os.path.join(base_dir, "data", "dmc_dict.csv")

    if not os.path.exists(dmc_csv_path):
        raise FileNotFoundError(f"BŁĄD KRYTYCZNY: Nie znaleziono bazy DMC pod adresem: {dmc_csv_path}")


    img = Image.open(image_file).convert("RGB")
    

    base_img = scale_to_stitches(img, width_cm, aida_count)


    quantized_img = quantize_opencv_lab(base_img, num_colors)


    dmc_colors, dmc_matrix = load_dmc_palette(dmc_csv_path)
    
    final_img, _, raw_global_grid = map_image_to_dmc(
        quantized_img,
        dmc_colors,
        dmc_matrix
    )


    unique_globals = np.unique(raw_global_grid)
    sorted_globals = sorted(unique_globals.tolist())
    
    global_to_local = { gid: lid for lid, gid in enumerate(sorted_globals) }
    
    mapper = np.vectorize(lambda x: global_to_local[x])
    local_grid_numpy = mapper(raw_global_grid)
    final_local_grid = local_grid_numpy.tolist()

    local_indices = list(range(len(sorted_globals)))
    symbol_map = assign_symbols(local_indices)

    final_palette = []
    for global_idx in sorted_globals:
        local_id = global_to_local[global_idx]
        dmc_data = dmc_colors[int(global_idx)]
        
        entry = {
            "id": local_id,
            "dmc": dmc_data["id"],
            "name": dmc_data["name"],
            "rgb": list(dmc_data["rgb"]),
            "symbol": symbol_map.get(local_id, "?")
        }
        final_palette.append(entry)


    if len(final_palette) > 0:
        max_id_in_grid = np.max(local_grid_numpy)
        max_id_in_palette = len(final_palette) - 1
        if max_id_in_grid > max_id_in_palette:
            raise ValueError("FATAL ERROR: Błąd spójności ID!")

    payload = build_grid_payload(
        final_local_grid=final_local_grid,
        final_palette=final_palette,
        aida_count=aida_count
    )

    chart_img = generate_symbol_chart(
        grid_matrix=payload['grid'], 
        palette=payload['palette'], 
        symbol_map=symbol_map
    )

    preview_buffer = io.BytesIO()
    final_img.save(preview_buffer, format="PNG")
    preview_buffer.seek(0)

    chart_buffer = io.BytesIO()
    chart_img.save(chart_buffer, format="PNG")
    chart_buffer.seek(0)

    return {
        "pattern_data": payload,
        "preview_png": preview_buffer,
        "chart_png": chart_buffer
    }