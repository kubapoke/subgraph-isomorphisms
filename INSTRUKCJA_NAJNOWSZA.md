# Instrukcja - Najnowsze ulepszenia

## 🎯 Szybki start - ładne wykresy na losowych grafach

### Opcja 1: Scenariusz `scaling` (ZALECANE - ~100+ testów)
```bash
# 1. Wygeneruj testy losowe
python3.13 performance_tests.py --scenario scaling --runs 1 --timeout 120

# 2. Wygeneruj ulepszone wykresy
python3.13 generate_plots.py
python3.13 generate_plots_improved.py

# 3. Porównanie i raporty
python3.13 compare_algorithms.py
python3.13 generate_report.py
```

### Opcja 2: Scenariusz `comprehensive` (BARDZO DUŻO testów)
```bash
# UWAGA: To może zająć 30-60 minut, ale daje najlepsze dane!
python3.13 performance_tests.py --scenario comprehensive --runs 1 --timeout 180

# Potem wykresy jak wyżej
python3.13 generate_plots.py
python3.13 generate_plots_improved.py
python3.13 compare_algorithms.py
python3.13 generate_report.py
```

### Opcja 3: Wszystko naraz
```bash
# Scaling (szybsze, ~100 testów)
python3.13 run_all_tests.py --scenario scaling --timeout 120

# Comprehensive (wolniejsze, ~300 testów)
python3.13 run_all_tests.py --scenario comprehensive --timeout 180
```

## 📊 Co się zmieniło w wykresach?

### Ulepszenia wizualne:
- ✅ **Większe punkty** - lepiej widoczne (s=100)
- ✅ **Lepsze kolory** - profesjonalna paleta
- ✅ **Error bars** - pokazują odchylenie standardowe
- ✅ **Trend lines** - regresja liniowa z nachyleniem
- ✅ **Lepsze etykiety** - większe, pogrubione
- ✅ **Czytelniejsza siatka** - subtelna, ale widoczna
- ✅ **Tło wykresów** - jasnoszare dla lepszego kontrastu

### Nowe informacje:
- Średnia ± odchylenie standardowe (σ)
- Trend line z wartością nachylenia (slope)
- Wszystkie punkty danych (nie tylko średnie)

## 📈 Dostępne scenariusze

| Scenariusz | Liczba testów | Czas | Opis |
|------------|---------------|------|------|
| `small` | ~12 | ~2 min | Małe testy (szybkie) |
| `medium` | ~15 | ~5-10 min | Średnie testy |
| `large` | ~15 | ~15-30 min | Duże testy |
| `scaling` | **~100+** | **~10-20 min** | **ZALECANE dla wykresów** |
| `comprehensive` | **~300+** | **~30-60 min** | **Najlepsze dane** |
| `existing` | zależy | zależy | Istniejące testy z folderów |

## 💡 Rekomendacje

1. **Dla szybkich testów i wykresów**: użyj `scaling` (~100 testów)
2. **Dla solidnych, statystycznie istotnych danych**: użyj `comprehensive` (~300 testów)
3. **Dla wykresów**: zawsze użyj `generate_plots.py` - teraz pokazuje więcej informacji!

## 🔍 Przykładowe polecenia

```bash
# Najszybsze - scaling
python3.13 performance_tests.py --scenario scaling --runs 1 --timeout 120
python3.13 generate_plots.py

# Najlepsze dane - comprehensive
python3.13 performance_tests.py --scenario comprehensive --runs 1 --timeout 180
python3.13 generate_plots.py

# Z większą liczbą powtórzeń (lepsze średnie)
python3.13 performance_tests.py --scenario scaling --runs 3 --timeout 120
python3.13 generate_plots.py
```

## 📁 Gdzie są wyniki?

- **Wykresy**: `performance_results/plots/`
- **Dane JSON**: `performance_results/results.json`
- **Raporty**: `performance_results/comparison_report.txt`, `performance_results/report.md`

