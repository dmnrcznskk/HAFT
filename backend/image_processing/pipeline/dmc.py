import csv
import numpy as np

def load_dmc_palette(csv_path: str):
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
