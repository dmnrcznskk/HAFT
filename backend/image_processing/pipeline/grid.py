from collections import Counter

def generate_grid_lines(width, height, major_every=10):
    vertical = []
    horizontal = []
    for x in range(width):
        vertical.append({"x": x, "type": "major" if x % major_every == 0 else "minor"})
    for y in range(height):
        horizontal.append({"y": y, "type": "major" if y % major_every == 0 else "minor"})
    return { "vertical": vertical, "horizontal": horizontal }

def compute_stats(grid, palette):
    flat = [cell for row in grid for cell in row]
    counts = Counter(flat)
    stats = {}
    for item in palette:
        stats[item["dmc"]] = counts.get(item["id"], 0) 
    return stats

# PRZYWRÓCONA NAZWA (ale nowa, bezpieczna logika w środku)
def build_grid_payload(
    final_local_grid,  
    final_palette,     
    aida_count,
    major_grid_every=10
):
    h = len(final_local_grid)
    w = len(final_local_grid[0]) if h > 0 else 0

    stats = compute_stats(final_local_grid, final_palette)

    return {
        "meta": {
            "width": w,
            "height": h,
            "aida": aida_count,
            "colors": len(final_palette)
        },
        "palette": final_palette,
        "grid": final_local_grid,
        "grid_lines": generate_grid_lines(w, h, major_grid_every),
        "stats": stats
    }