# 🧵 Cross-Stitch Generator (Backend)

Moduł do przetwarzania obrazów na wzory haftu w pamięci RAM.

## Funkcja główna

`process_image(image_file, num_colors, width_cm, aida_count)`

### Argumenty wejściowe

| Nazwa | Typ | Opis |
| :--- | :--- | :--- |
| `image_file` | `BinaryIO` / `bytes` | Otwarty plik (tryb `rb`) lub strumień bajtów obrazu. |
| `num_colors` | `int` | Maksymalna liczba kolorów w palecie docelowej. |
| `width_cm` | `float` | Fizyczna szerokość haftu w centymetrach. |
| `aida_count` | `int` | Gęstość kanwy (np. 14, 16, 18). |

### Zwracana wartość

Funkcja zwraca słownik (`dict`) zawierający trzy klucze:

* **`"pattern_data"`** (`dict`): Gotowy obiekt z danymi wzoru (opis struktury poniżej).
* **`"preview_png"`** (`io.BytesIO`): Obraz podglądu (Pixel Art) w formacie PNG (w pamięci RAM).
* **`"chart_png"`** (`io.BytesIO`): Obraz schematu technicznego z symbolami w formacie PNG (w pamięci RAM).

---

## Struktura JSON (`pattern_data`)

Obiekt zwracany w kluczu `pattern_data` składa się z następujących sekcji:

### 1. `meta` (Metadane)
Informacje ogólne o wymiarach.
* `width` (int): Szerokość w krzyżykach.
* `height` (int): Wysokość w krzyżykach.
* `aida` (int): Gęstość kanwy.
* `colors` (int): Liczba użytych unikalnych kolorów.

### 2. `palette` (Legenda)
Lista obiektów definiujących kolory.
* `id` (int): Lokalne ID używane w macierzy `grid`.
* `dmc` (str): Kod nici DMC (np. "310").
* `name` (str): Nazwa koloru (np. "Black").
* `rgb` (list): Tablica `[R, G, B]` dla koloru.
* `symbol` (str): Znak (Unicode/ASCII) reprezentujący kolor na schemacie.

### 3. `grid` (Siatka)
Macierz 2D (lista list) reprezentująca obraz piksel po pikselu.
* Wartości w macierzy to liczby całkowite (`int`) odpowiadające polu `id` z sekcji `palette`.

### 4. `stats` (Statystyki)
Słownik zużycia nici.
* **Klucz**: Kod DMC (np. "310").
* **Wartość**: Całkowita liczba krzyżyków tego koloru we wzorze.

### 5. `grid_lines` (Linie siatki)
Gotowe współrzędne linii pomocniczych (dla renderingu).
* Podzielone na `vertical` (pionowe) i `horizontal` (poziome).
* Każda linia ma atrybut `type`: `"major"` (gruba, co 10 kratek) lub `"minor"` (cienka).
