# Podsumowanie systemu testowania

## Co zostało stworzone

### 1. **performance_tests.py** - System testów wydajnościowych
   - Przeprowadza systematyczne testy dla algorytmów exact i approximate
   - Generuje losowe testy z różnymi parametrami (n1, n2, k)
   - Mierzy czas wykonania i koszt rozszerzenia
   - Zapisuje wyniki do pliku JSON
   - Obsługuje różne scenariusze: small, medium, large, scaling

### 2. **generate_plots.py** - Generator wykresów wydajności
   - **Wykresy 2D:**
     - Czas vs n1 (rozmiar grafu G1)
     - Czas vs n2 (rozmiar grafu G2)
     - Czas vs k (liczba kopii)
   - **Wykresy porównawcze:**
     - Porównanie czasu exact vs approximate
     - Porównanie kosztu exact vs approximate
     - Rozkład przyspieszenia (speedup ratio)
     - Rozkład jakości rozwiązania (cost ratio)
   - **Wykresy 3D:**
     - Powierzchnia pokazująca zależność czasu od n1 i n2

### 3. **compare_algorithms.py** - Szczegółowe porównanie algorytmów
   - Statystyki czasu wykonania (średnia, mediana, min, max)
   - Statystyki kosztu rozszerzenia
   - Analiza jakości (ile razy Approx znalazł rozwiązanie optymalne)
   - Generuje raport tekstowy z wnioskami

### 4. **generate_report.py** - Generator sprawozdania
   - Tworzy sprawozdanie w formacie Markdown
   - Zawiera:
     - Podsumowanie testów
     - Statystyki dla każdego algorytmu
     - Porównanie algorytmów
     - Analizę skalowalności (wpływ n1, n2, k)
     - Wnioski

### 5. **run_all_tests.py** - Główny skrypt
   - Uruchamia wszystkie testy i generuje wszystkie raporty
   - Automatyzuje cały proces testowania

## Jakie wykresy pokazują zależności?

### Problem z wieloma parametrami (n1, n2, k)

Mamy trzy parametry wejściowe, więc potrzebujemy różnych podejść:

1. **Wykresy 2D z podziałem na scenariusze**
   - Dla każdego wykresu (czas vs n1, n2, k) tworzymy 4 podwykresy
   - Każdy podwykres pokazuje zależność dla różnych wartości pozostałych parametrów
   - Przykład: wykres "czas vs n1" ma 4 wersje dla różnych par (n2, k)

2. **Wykresy porównawcze**
   - Wykresy rozrzutu pokazują bezpośrednie porównanie exact vs approximate
   - Histogramy pokazują rozkład stosunków (przyspieszenie, jakość)

3. **Wykresy 3D**
   - Pokazują zależność czasu od dwóch parametrów jednocześnie (n1 i n2)
   - Dla stałej wartości k

## Proponowane wykresy

### 1. Czas vs n1 (z podziałem na n2, k)
   - **Cel:** Pokazać jak rozmiar grafu G1 wpływa na czas
   - **Format:** 4 podwykresy dla różnych kombinacji (n2, k)
   - **Skala:** Logarytmiczna na osi Y (czas)

### 2. Czas vs n2 (z podziałem na n1, k)
   - **Cel:** Pokazać jak rozmiar grafu G2 wpływa na czas
   - **Format:** 4 podwykresy dla różnych kombinacji (n1, k)
   - **Skala:** Logarytmiczna na osi Y (czas)

### 3. Czas vs k (z podziałem na n1, n2)
   - **Cel:** Pokazać jak liczba kopii wpływa na czas
   - **Format:** 4 podwykresy dla różnych kombinacji (n1, n2)
   - **Skala:** Logarytmiczna na osi Y (czas)

### 4. Porównanie exact vs approximate
   - **Czas:** Wykres rozrzutu (exact vs approx)
   - **Koszt:** Wykres rozrzutu (exact vs approx)
   - **Przyspieszenie:** Histogram stosunku czasów
   - **Jakość:** Histogram stosunku kosztów

### 5. Powierzchnia 3D
   - **Cel:** Wizualizacja zależności czasu od n1 i n2 jednocześnie
   - **Format:** Wykres 3D dla stałego k

## Jak używać

### Szybki start:
```bash
python run_all_tests.py
```

### Szczegółowe instrukcje:
Zobacz `TESTING_README.md`

## Struktura wyników

Po uruchomieniu testów, w katalogu `performance_results/` znajdziesz:

```
performance_results/
├── results.json              # Surowe dane testowe
├── plots/                    # Wykresy
│   ├── time_vs_n1.png
│   ├── time_vs_n2.png
│   ├── time_vs_k.png
│   ├── comparison_exact_vs_approx.png
│   ├── speedup_ratio.png
│   ├── cost_ratio.png
│   └── 3d_surface_*.png
├── comparison_report.txt     # Szczegółowe porównanie
└── report.md                 # Sprawozdanie Markdown
```

## Co jeszcze można dodać?

1. **Wykresy zależności od gęstości grafu**
   - Można dodać parametr density i pokazać jak wpływa na czas

2. **Wykresy zależności od typu grafu**
   - Testy dla różnych typów grafów (path, cycle, complete, etc.)

3. **Wykresy pamięci**
   - Jeśli dodać pomiar zużycia pamięci

4. **Wykresy zależności od stosunku n2/n1**
   - Pokazać jak stosunek rozmiarów grafów wpływa na wydajność

5. **Heatmapy**
   - Macierze ciepła pokazujące czas dla różnych kombinacji parametrów

## Uwagi

- Wykresy używają skali logarytmicznej dla czasu (ze względu na duże różnice)
- Wszystkie wykresy są zapisywane w wysokiej rozdzielczości (300 DPI)
- Sprawozdania są generowane automatycznie z analizą wyników

