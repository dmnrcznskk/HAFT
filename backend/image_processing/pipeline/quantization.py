import cv2
import numpy as np
from collections import Counter
from PIL import Image
from .config import THRESHOLD_PERCENTAGE

def update_nb_colours(label: np.ndarray, nb_pixels: int, threshold: float, nb_colours: int):
    """
    Usuwa rzadkie kolory (threshold) i ewentualnie zwiększa liczbę klastrów
    """
    nb_colours_under_threshold = 0
    label = label.flatten()
    colour_count = Counter(label)
    for count in colour_count.values():
        if count / nb_pixels < threshold:
            nb_colours_under_threshold += 1

    # kompensacja kolorów, które usunęliśmy
    if nb_colours_under_threshold > 0:
        nb_colours += -(-nb_colours_under_threshold // 2)  # ceiling divide

    return nb_colours, nb_colours_under_threshold

def quantize_opencv_lab(img_input: Image.Image, num_colors: int, use_lab: bool = True) -> Image.Image:
    import cv2
    import numpy as np

    # Konwersja
    img = np.array(img_input)
    if use_lab:
        conversion_to = cv2.COLOR_RGB2Lab
        conversion_from = cv2.COLOR_Lab2RGB
    else:
        conversion_to = cv2.COLOR_RGB2BGR  # RGB OpenCV
        conversion_from = cv2.COLOR_BGR2RGB

    img_cv = cv2.cvtColor(img, conversion_to)

    # Flatten
    flat_img = img_cv.reshape((-1, 3)).astype(np.float32)
    nb_pixels = flat_img.shape[0]

    # KMeans OpenCV
    current_colors = num_colors
    threshold = 0.0001
    iteration = 0
    label, center = None, None

    while iteration < 5:
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        ret, label, center = cv2.kmeans(flat_img, current_colors, None, criteria, 10, cv2.KMEANS_PP_CENTERS)

        # Usuwanie rzadkich kolorów
        from pipeline.config import THRESHOLD_PERCENTAGE
        from pipeline.utils import update_nb_colours  # jeśli masz funkcję do threshold
        current_colors, under_threshold = update_nb_colours(label, nb_pixels, threshold, current_colors)
        if under_threshold == 0:
            break
        iteration += 1

    # Rekonstrukcja obrazu
    quantized_img = np.uint8(center[label.flatten()]).reshape(img_cv.shape)
    quantized_img = cv2.cvtColor(quantized_img, conversion_from)
    from PIL import Image
    return Image.fromarray(quantized_img)
