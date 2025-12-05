# Szybki start - ładne wykresy na losowych grafach

## Najprostszy sposób (kopiuj-wklej)

### Opcja 1: Scenariusz `scaling` (ZALECANE - ~100+ testów)
```bash
# 1. Wygeneruj testy losowe i uruchom testy
python3.13 performance_tests.py --scenario scaling --runs 1 --timeout 120

# 2. Wygeneruj wszystkie wykresy (ulepszone!)
python3.13 generate_plots.py
python3.13 generate_plots_improved.py

# 3. Wygeneruj raporty
python3.13 compare_algorithms.py
python3.13 generate_report.py
```

### Opcja 2: Scenariusz `comprehensive` (BARDZO DUŻO testów - dla solidnych danych)
```bash
# UWAGA: To może zająć dużo czasu, ale daje najlepsze dane!
python3.13 performance_tests.py --scenario comprehensive --runs 1 --timeout 180

# Potem wykresy i raporty jak wyżej
python3.13 generate_plots.py
python3.13 generate_plots_improved.py
python3.13 compare_algorithms.py
python3.13 generate_report.py
```

## Lub wszystko naraz

```bash
# Scaling (szybsze)
python3.13 run_all_tests.py --scenario scaling --timeout 120

# Comprehensive (wolniejsze, ale więcej danych)
python3.13 run_all_tests.py --scenario comprehensive --timeout 180
```

## Co dostaniesz

### Wykresy (w `performance_results/plots/`):
- **time_vs_n1.png** - czas vs rozmiar G1 (wszystkie punkty + średnie)
- **time_vs_n2.png** - czas vs rozmiar G2 (wszystkie punkty + średnie)
- **time_vs_k.png** - czas vs liczba kopii (wszystkie punkty + średnie)
- **comparison_exact_vs_approx.png** - porównanie czasu i kosztu
- **speedup_ratio.png** - jak często Approx jest szybszy
- **cost_ratio.png** - jakość rozwiązania Approx
- **time_vs_parameters_scatter.png** - wszystkie punkty + box plots
- **heatmap_time_*.png** - heatmapy pokazujące wszystkie kombinacje
- **aggregated_trends.png** - trendy z error bars
- **size_complexity.png** - złożoność względem rozmiaru problemu

### Raporty:
- **comparison_report.txt** - szczegółowe statystyki
- **report.md** - sprawozdanie w Markdown

## Uwagi

- Scenariusz `scaling` daje systematyczne pokrycie parametrów (najlepsze dla wykresów)
- Timeout 120s powinien wystarczyć
- Niektóre losowe testy mogą zwrócić NO_SOL (to normalne)
- Wykresy pokazują wszystkie punkty danych, nie tylko średnie

