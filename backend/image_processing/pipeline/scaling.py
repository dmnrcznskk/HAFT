from PIL import Image

def scale_to_stitches(img: Image.Image, width_cm: float, aida_count: int) -> Image.Image:
    stitches_per_cm = aida_count / 2.54
    target_width = int(width_cm * stitches_per_cm)
    target_height = int(target_width * img.height / img.width)
    return img.resize((target_width, target_height), Image.Resampling.LANCZOS)
