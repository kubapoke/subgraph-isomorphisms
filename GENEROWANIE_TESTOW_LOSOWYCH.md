# Generowanie testów losowych i wykresów

## Szybki start - ładne wykresy na losowych grafach

### Krok 1: Wygeneruj testy losowe i uruchom testy

```bash
# Scenariusz "scaling" - różne rozmiary (ZALECANE dla wykresów)
python3.13 performance_tests.py --scenario scaling --runs 1 --timeout 120

# Lub mniejszy scenariusz dla szybszych testów
python3.13 performance_tests.py --scenario medium --runs 1 --timeout 120

# Lub większy scenariusz dla więcej danych
python3.13 performance_tests.py --scenario large --runs 1 --timeout 180
```

### Krok 2: Wygeneruj wykresy

```bash
# Oryginalne wykresy (ulepszone - pokazują wszystkie punkty)
python3.13 generate_plots.py

# Ulepszone wykresy (bardziej informacyjne)
python3.13 generate_plots_improved.py
```

### Krok 3: Porównanie i sprawozdanie

```bash
# Szczegółowe porównanie
python3.13 compare_algorithms.py

# Sprawozdanie Markdown
python3.13 generate_report.py
```

## Wszystko naraz

```bash
# Pełna suita (generuje testy losowe + wykresy + raporty)
python3.13 run_all_tests.py --scenario scaling --timeout 120
```

## Dostępne scenariusze

### `small` - Małe testy (szybkie)
- n1: 3-5, n2: 5-8, k: 1-2
- ~12 testów
- Czas: ~1-2 minuty

### `medium` - Średnie testy (ZALECANE)
- n1: 5-7, n2: 10-15, k: 1-3
- ~15 testów
- Czas: ~5-10 minut

### `large` - Duże testy
- n1: 8-12, n2: 20-30, k: 1-3
- ~15 testów
- Czas: ~15-30 minut (może być dłużej)

### `scaling` - Testy skalowalności (NAJLEPSZE dla wykresów)
- Różne n1: 3, 5, 7, 10
- Różne n2: 10, 15, 20, 25, 30
- Różne k: 1, 2, 3, 4, 5
- ~22 testów
- Czas: ~10-20 minut
- **Zalecane dla wykresów** - daje systematyczne pokrycie parametrów

## Parametry

### `--runs` - Liczba powtórzeń
```bash
# 1 powtórzenie (szybciej)
python3.13 performance_tests.py --scenario scaling --runs 1

# 3 powtórzenia (lepsze średnie, dłużej)
python3.13 performance_tests.py --scenario scaling --runs 3
```

### `--timeout` - Timeout w sekundach
```bash
# 60 sekund (domyślnie)
python3.13 performance_tests.py --scenario scaling --timeout 60

# 120 sekund (dla większych testów)
python3.13 performance_tests.py --scenario scaling --timeout 120

# 300 sekund (5 minut - dla bardzo dużych)
python3.13 performance_tests.py --scenario scaling --timeout 300
```

## Rekomendacja dla ładnych wykresów

```bash
# 1. Wygeneruj testy losowe (scaling daje najlepsze pokrycie)
python3.13 performance_tests.py --scenario scaling --runs 1 --timeout 120

# 2. Wygeneruj wszystkie wykresy
python3.13 generate_plots.py
python3.13 generate_plots_improved.py

# 3. Wygeneruj raporty
python3.13 compare_algorithms.py
python3.13 generate_report.py
```

## Co dostaniesz

### Wykresy w `performance_results/plots/`:
- `time_vs_n1.png` - czas vs n1 (z wszystkimi punktami)
- `time_vs_n2.png` - czas vs n2 (z wszystkimi punktami)
- `time_vs_k.png` - czas vs k (z wszystkimi punktami)
- `comparison_exact_vs_approx.png` - porównanie czasu i kosztu
- `speedup_ratio.png` - rozkład przyspieszenia
- `cost_ratio.png` - rozkład jakości
- `time_vs_parameters_scatter.png` - wszystkie punkty + box plots
- `heatmap_time_*.png` - heatmapy dla n1×n2
- `aggregated_trends.png` - trendy z error bars
- `size_complexity.png` - złożoność vs rozmiar problemu
- `3d_surface_*.png` - wykresy 3D

### Raporty:
- `comparison_report.txt` - szczegółowe porównanie
- `report.md` - sprawozdanie Markdown

## Uwagi

- Losowe testy mogą zwracać NO_SOL (to normalne - nie wszystkie losowe grafy mają rozwiązanie)
- Scenariusz `scaling` daje najlepsze pokrycie parametrów dla wykresów
- Więcej powtórzeń (`--runs 3`) daje lepsze średnie, ale trwa dłużej
- Timeout 120s powinien wystarczyć dla większości testów

