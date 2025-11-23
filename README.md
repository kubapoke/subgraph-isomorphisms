# Subgraph Isomorphisms

Projekt implementuje algorytmy (dokładny i aproksymacyjny) dla problemu znalezienia minimalnego rozszerzenia grafu $G_2$ (oznaczanego jako $G'_2$), które zawiera $k$ rozłącznych kopii zadanego grafu $G_1$.

## Budowanie

Wymagany CMake oraz kompilator C++ (np. MinGW, MSVC).

```bash
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

## Uruchamianie

```bash
./build/subgraph-isomorphism.exe [plik_z_danymi] [algorytm]
```

-   `algorytm`: `exact` (domyślny) lub `approx`

## Format pliku wejściowego

```text
n1                  <-- Liczba wierzchołków G1
0 1 ...             <-- Macierz sąsiedztwa G1 (wiersz 1)
...
n2                  <-- Liczba wierzchołków G2
0 2 ...             <-- Macierz sąsiedztwa G2 (wiersz 1)
...
k                   <-- Liczba kopii do znalezienia
```

## Testowanie

Do weryfikacji poprawności służy skrypt `giga_sprawdzarka.py`, który sprawdza zgodność wyników z definicjami matematycznymi.

**Uruchomienie wszystkich testów (160+ plików):**

```bash
python giga_sprawdzarka.py
```

**Uruchomienie Fuzzingu (losowe testy):**

```bash
python giga_sprawdzarka.py --fuzz 100
```
