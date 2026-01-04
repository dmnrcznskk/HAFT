import sys
import numpy as np
import cv2
from PIL import Image
from collections import Counter
from typing import Tuple, List, Type, Optional, Callable, Union

# Importy Scikit-learn
import sklearn.utils
from sklearn.cluster import KMeans, MeanShift, MiniBatchKMeans

# Importy Scipy
import scipy.cluster

# Importy PyClustering
from pyclustering.cluster import (
    bsas, mbsas, dbscan, optics, syncnet, syncsom, ttsas, xmeans,
    center_initializer, elbow, kmeans, kmedians
)
from pyclustering.utils import type_metric, distance_metric

# --- KONFIGURACJA ---
INPUT_IMAGE = "monke.jpg"  # Nazwa pliku wejściowego
OUTPUT_PREFIX = "test"
WIDTH_CM = 12.0
AIDA_COUNT = 14
NUM_COLORS = 20

# UWAGA: W Twoim kodzie było to 0.02 (2%). Dla haftu to za dużo!
# Małe detale (oczy, pysk) znikną. Zmieniam na 0 (wyłączone) lub bardzo mało.
THRESHOLD_PERCENTAGE = 0.0001 

# --- NARZĘDZIA (Twoje funkcje + skalowanie) ---

def scale_to_stitches(img: Image.Image, width_cm: float, aida_count: int) -> Image.Image:
    stitches_per_cm = aida_count / 2.54
    target_width = int(width_cm * stitches_per_cm)
    aspect_ratio = img.height / img.width
    target_height = int(target_width * aspect_ratio)
    return img.resize((target_width, target_height), Image.Resampling.LANCZOS)

def get_img_data(img_input: Image.Image, conversion_method: int = cv2.COLOR_RGB2BGR) -> Tuple[np.ndarray, int, np.ndarray]:
    img_array = np.array(img_input)
    if img_array.shape[2] == 4:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
    img = cv2.cvtColor(img_array, conversion_method)
    nb_pixels = img.size // 3
    flat_img = img.reshape((-1, 3)).astype(np.float32)
    return img, nb_pixels, flat_img

def process_result(center: np.ndarray, label: np.ndarray, shape: Tuple[int, int, int], conversion_method: int = cv2.COLOR_BGR2RGB) -> Image.Image:
    center = np.uint8(center)
    quantized_img = center[label].reshape(shape)
    quantized_img = cv2.cvtColor(quantized_img, conversion_method)
    return Image.fromarray(quantized_img)

def process_pycluster_result(flat_img: np.ndarray, clusters: List[List[int]], representatives: List[List[float]], shape: Tuple[int, int, int], conversion_method: int = cv2.COLOR_BGR2RGB) -> Image.Image:
    output_flat = np.copy(flat_img)
    representatives = np.uint8(representatives)
    for index_cluster, cluster in enumerate(clusters):
        for pixel_idx in cluster:
            output_flat[pixel_idx] = representatives[index_cluster]
    quantized_img = np.uint8(output_flat.reshape(shape))
    quantized_img = cv2.cvtColor(quantized_img, conversion_method)
    return Image.fromarray(quantized_img)

def update_nb_colours(label: np.ndarray, nb_pixels: int, threshold: float, nb_colours: int) -> Tuple[int, int]:
    # To jest ta funkcja, która usuwała Ci małpę w oryginale!
    nb_colours_under_threshold = 0
    label = label.flatten()
    colour_count = Counter(label)
    for (pixel, count) in colour_count.items():
        if count / nb_pixels < threshold:
            nb_colours_under_threshold += 1
    
    # Logika zwiększania kolorów, żeby zkompensować te usunięte
    if nb_colours_under_threshold > 0:
        nb_colours -= -(-nb_colours_under_threshold // 2)
    
    return nb_colours, nb_colours_under_threshold

# --- IMPLEMENTACJE ALGORYTMÓW (Przywrócone z Twojego kodu) ---

def test_pillow(img_input: Image.Image, method: int) -> Image.Image:
    # Pillow nie obsługuje pętli threshold tak łatwo bez konwersji, zostawiamy standard
    return img_input.quantize(colors=NUM_COLORS, method=method, kmeans=0).convert('RGB')

def test_opencv(img_input: Image.Image, method1: int, method2: int) -> Image.Image:
    img, nb_pixels, flat_img = get_img_data(img_input, method1)
    current_colors = NUM_COLORS
    under_threshold = current_colors
    center, label = None, None
    
    # Pętla z Twojego kodu (zabezpieczona max 5 iteracji żeby nie wpadła w infinite loop)
    iteration = 0
    while under_threshold > 0 and iteration < 5:
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        ret, label, center = cv2.kmeans(flat_img, current_colors, None, criteria, 10, cv2.KMEANS_PP_CENTERS)
        current_colors, under_threshold = update_nb_colours(label, nb_pixels, THRESHOLD_PERCENTAGE, current_colors)
        iteration += 1
        
    return process_result(center, label.flatten(), img.shape, method2)

def test_scipy(img_input: Image.Image) -> Image.Image:
    img, nb_pixels, flat_img = get_img_data(img_input)
    current_colors = NUM_COLORS
    under_threshold = current_colors
    centroids, qnt = None, None
    iteration = 0
    while under_threshold > 0 and iteration < 5:
        centroids, _ = scipy.cluster.vq.kmeans(flat_img, current_colors)
        if len(centroids) == 0: break 
        qnt, _ = scipy.cluster.vq.vq(flat_img, centroids)
        current_colors, under_threshold = update_nb_colours(qnt, nb_pixels, THRESHOLD_PERCENTAGE, current_colors)
        iteration += 1
    
    centers_idx = np.reshape(qnt, (img.shape[0], img.shape[1]))
    return process_result(centroids, centers_idx.flatten(), img.shape)

def test_sklearn_kmeans(img_input: Image.Image) -> Image.Image:
    img, nb_pixels, flat_img = get_img_data(img_input)
    current_colors = NUM_COLORS
    under_threshold = current_colors
    center, label = None, None
    iteration = 0
    while under_threshold > 0 and iteration < 5:
        kmeans = KMeans(n_clusters=current_colors, random_state=0, n_init=10).fit(flat_img)
        label = kmeans.labels_
        center = kmeans.cluster_centers_
        current_colors, under_threshold = update_nb_colours(label, nb_pixels, THRESHOLD_PERCENTAGE, current_colors)
        iteration += 1
    return process_result(center, label, img.shape)

# --- PYCLUSTERING (Tu jest najwięcej różnic w API) ---

def test_pycluster_bsas(img_input: Image.Image) -> Image.Image:
    img, nb_pixels, flat_img = get_img_data(img_input)
    # BSAS używa threshold odległości, a nie ilości klastrów wprost
    clusterer = bsas.bsas(flat_img, NUM_COLORS, threshold=15.0, metric=distance_metric(type_metric.CHI_SQUARE))
    clusterer.process()
    return process_pycluster_result(flat_img, clusterer.get_clusters(), clusterer.get_representatives(), img.shape)

def test_pycluster_mbsas(img_input: Image.Image) -> Image.Image:
    img, nb_pixels, flat_img = get_img_data(img_input)
    clusterer = mbsas.mbsas(flat_img, NUM_COLORS, threshold=15.0, metric=distance_metric(type_metric.CHI_SQUARE))
    clusterer.process()
    return process_pycluster_result(flat_img, clusterer.get_clusters(), clusterer.get_representatives(), img.shape)

def test_pycluster_kmeans(img_input: Image.Image) -> Image.Image:
    img, nb_pixels, flat_img = get_img_data(img_input)
    initial_centers = center_initializer.kmeans_plusplus_initializer(flat_img, NUM_COLORS).initialize()
    clusterer = kmeans.kmeans(flat_img, initial_centers)
    clusterer.process()
    return process_pycluster_result(flat_img, clusterer.get_clusters(), clusterer.get_centers(), img.shape)

def test_pycluster_kmedians(img_input: Image.Image) -> Image.Image:
    img, nb_pixels, flat_img = get_img_data(img_input)
    initial_centers = center_initializer.kmeans_plusplus_initializer(flat_img, NUM_COLORS).initialize()
    clusterer = kmedians.kmedians(flat_img, initial_centers)
    clusterer.process()
    return process_pycluster_result(flat_img, clusterer.get_clusters(), clusterer.get_medians(), img.shape)

def test_pycluster_xmeans(img_input: Image.Image) -> Image.Image:
    img, nb_pixels, flat_img = get_img_data(img_input)
    initial_centers = center_initializer.kmeans_plusplus_initializer(flat_img, 2).initialize()
    # X-Means sam decyduje o liczbie klastrów do max_clusters
    clusterer = xmeans.xmeans(flat_img, initial_centers, kmax=NUM_COLORS)
    clusterer.process()
    return process_pycluster_result(flat_img, clusterer.get_clusters(), clusterer.get_centers(), img.shape)

# --- MAIN LOOP ---

def run_tests():
    print(f"--- START (Threshold: {THRESHOLD_PERCENTAGE}) ---")
    try:
        original_img = Image.open(INPUT_IMAGE).convert("RGB")
    except FileNotFoundError:
        print("Brak pliku!")
        return

    base_img = scale_to_stitches(original_img, WIDTH_CM, AIDA_COUNT)
    base_img.save(f"{OUTPUT_PREFIX}_BASE.png")
    print(f"Rozmiar: {base_img.size}")

    algorithms = [
        ("pillow_median_cut", lambda i: test_pillow(i, 0)),
        ("pillow_max_coverage", lambda i: test_pillow(i, 1)),
        ("opencv_rgb", lambda i: test_opencv(i, cv2.COLOR_RGB2BGR, cv2.COLOR_BGR2RGB)),
        ("opencv_lab", lambda i: test_opencv(i, cv2.COLOR_RGB2Lab, cv2.COLOR_Lab2RGB)),
        ("scipy_kmeans", test_scipy),
        ("sklearn_kmeans", test_sklearn_kmeans),
        ("pycluster_kmeans", test_pycluster_kmeans),
        ("pycluster_xmeans", test_pycluster_xmeans),
        ("pycluster_bsas", test_pycluster_bsas),
        # Możesz odkomentować inne, ale uwaga na czas obliczeń
    ]

    for name, func in algorithms:
        print(f"Testowanie: {name}...")
        try:
            res = func(base_img.copy())
            res.save(f"{OUTPUT_PREFIX}_{name}.png")
        except Exception as e:
            print(f"Błąd {name}: {e}")

if __name__ == "__main__":
    run_tests()