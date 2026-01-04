import PIL
from PIL import Image
import sys

def scale_for_embroidery(
    img,
    width_cm,
    height_cm=None,
    aida_count=14,
    keep_ratio=True
):
    stitches_per_cm = aida_count / 2.54
    target_width = int(width_cm * stitches_per_cm)

    if keep_ratio:
        aspect_ratio = img.size[1] / img.size[0]
        target_height = int(target_width * aspect_ratio)
    else:
        if height_cm is None:
            raise ValueError("height_cm required when keep_ratio=False")
        target_height = int(height_cm * stitches_per_cm)

    img = img.resize(
        (target_width, target_height),
        Image.Resampling.NEAREST
    )

    return img, target_width, target_height

def load_dmc_palette(csv_path):
    colors = []
    meta = []

    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            floss_id = row[0]
            r, g, b = map(int, row[1:4])
            name = row[4]

            colors.append((r, g, b))
            meta.append((floss_id, name))

    return colors, meta

def build_palette_image(colors):
    palette_img = Image.new("P", (1, 1))

    flat_palette = []
    for r, g, b in colors:
        flat_palette.extend([r, g, b])

    flat_palette += [0] * (256 * 3 - len(flat_palette))
    palette_img.putpalette(flat_palette)

    return palette_img


def main(path):
    img = Image.open(path).convert("RGB")
    img = img.quantize(colors=20, method=0, kmeans=1, dither=Image.Dither.NONE)
    img, w, h = scale_for_embroidery(img, 12)
    img = img.save("result_main.png")
    print(f'wymiary haftu: {w} x {h} krzyzykow')

if __name__=="__main__":
    path = str(sys.argv[1])
    main(path)
