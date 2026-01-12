from collections import Counter
import numpy as np

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
