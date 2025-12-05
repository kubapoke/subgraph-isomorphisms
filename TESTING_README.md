# Instrukcja testowania i generowania wykresów

Ten dokument opisuje jak przeprowadzić testy wydajnościowe i wygenerować wykresy oraz sprawozdania.

## Wymagania

1. **Python 3.7+** z następującymi bibliotekami:
   ```bash
   pip install matplotlib numpy
   ```

2. **Skompilowany program C++** (domyślnie: `.\build\subgraph-isomorphism.exe`)

## Struktura plików

- `performance_tests.py` - przeprowadza testy wydajnościowe
- `generate_plots.py` - generuje wykresy wydajności
- `compare_algorithms.py` - porównuje algorytmy exact vs approximate
- `generate_report.py` - generuje sprawozdanie w formacie Markdown
- `run_all_tests.py` - uruchamia wszystkie testy i generuje wszystkie raporty

## Szybki start

### 1. Uruchomienie wszystkich testów i generowanie raportów

```bash
python run_all_tests.py
```

To uruchomi:
- Testy wydajnościowe dla obu algorytmów
- Generowanie wykresów
- Porównanie algorytmów
- Generowanie sprawozdania

### 2. Tylko testy wydajnościowe

```bash
python performance_tests.py --scenario scaling
```

Opcje:
- `--scenario`: `small`, `medium`, `large`, `scaling` (domyślnie: `scaling`)
- `--runs`: liczba powtórzeń każdego testu (domyślnie: 1)
- `--timeout`: timeout w sekundach (domyślnie: 300)
- `--exe`: ścieżka do pliku wykonywalnego

### 3. Tylko generowanie wykresów

```bash
python generate_plots.py
```

Wymaga wcześniej wygenerowanego pliku `performance_results/results.json`.

### 4. Tylko porównanie algorytmów

```bash
python compare_algorithms.py
```

Generuje szczegółowe porównanie czasów i kosztów.

### 5. Tylko sprawozdanie

```bash
python generate_report.py
```

Generuje sprawozdanie w formacie Markdown.

## Scenariusze testowe

### `small`
Małe testy (n1=3-5, n2=5-8, k=1-2)

### `medium`
Średnie testy (n1=5-7, n2=10-15, k=1-3)

### `large`
Duże testy (n1=8-12, n2=20-30, k=1-3)

### `scaling` (domyślnie)
Kompleksowy zestaw testów skalowalności:
- Różne wartości n1 (3, 5, 7, 10)
- Różne wartości n2 (10, 15, 20, 25, 30)
- Różne wartości k (1, 2, 3, 4, 5)

## Generowane wykresy

W katalogu `performance_results/plots/` znajdziesz:

1. **time_vs_n1.png** - Czas wykonania vs rozmiar grafu G1 (n1)
2. **time_vs_n2.png** - Czas wykonania vs rozmiar grafu G2 (n2)
3. **time_vs_k.png** - Czas wykonania vs liczba kopii (k)
4. **comparison_exact_vs_approx.png** - Porównanie czasu i kosztu (exact vs approx)
5. **speedup_ratio.png** - Rozkład przyspieszenia Approx względem Exact
6. **cost_ratio.png** - Rozkład jakości rozwiązania Approx względem Exact
7. **3d_surface_*.png** - Wykresy 3D pokazujące zależność czasu od n1 i n2

## Generowane raporty

1. **performance_results/results.json** - Surowe dane testowe (JSON)
2. **performance_results/comparison_report.txt** - Szczegółowe porównanie algorytmów
3. **performance_results/report.md** - Sprawozdanie w formacie Markdown

## Przykładowe użycie

### Pełna suita testowa (małe testy, 3 powtórzenia)

```bash
python run_all_tests.py --scenario small --runs 3
```

### Tylko generowanie wykresów (jeśli już masz wyniki)

```bash
python run_all_tests.py --skip-tests
```

### Testy z własnym plikiem wykonywalnym

```bash
python performance_tests.py --exe ".\build\subgraph-isomorphism.exe" --scenario medium
```

## Interpretacja wyników

### Wykresy czasowe
- **Skala logarytmiczna** na osi Y (czas) - pozwala zobaczyć różnice rzędu wielkości
- **Linie ciągłe** - średnie wartości dla danego parametru
- **Różne kolory** - exact (niebieski) vs approximate (pomarańczowy)

### Porównanie exact vs approximate
- **Wykres rozrzutu** - punkty powyżej linii y=x oznaczają, że Approx jest szybszy/lepszy
- **Histogramy stosunków** - pokazują rozkład przyspieszenia/jakości

### Sprawozdanie
- **Tabele statystyk** - średnie, mediany, min/max dla czasu i kosztu
- **Analiza skalowalności** - jak parametry wpływają na wydajność
- **Wnioski** - automatyczna analiza wyników

## Rozwiązywanie problemów

### Błąd: "matplotlib not found"
```bash
pip install matplotlib numpy
```

### Błąd: "Cannot find executable"
Sprawdź ścieżkę do pliku wykonywalnego:
```bash
python performance_tests.py --exe ".\twoja_sciezka\subgraph-isomorphism.exe"
```

### Timeout w testach
Zwiększ timeout:
```bash
python performance_tests.py --timeout 600  # 10 minut
```

### Brak wyników w wykresach
Upewnij się, że najpierw uruchomiłeś `performance_tests.py` i wygenerowałeś `results.json`.

## Zaawansowane użycie

### Własne scenariusze testowe

Edytuj `performance_tests.py` i dodaj własne scenariusze w funkcji `main()`:

```python
scenarios = [
    (n1, n2, k),  # Twoje parametry
    ...
]
```

### Modyfikacja wykresów

Edytuj `generate_plots.py` aby dostosować style, kolory, rozmiary wykresów.

### Dodatkowe metryki

Rozszerz `compare_algorithms.py` aby dodać własne metryki porównawcze.

