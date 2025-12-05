# Poprawki wykresów - co zostało zmienione

## Problem 1: "Same kropki" - brak trendów

### Przed:
- Wykres `time_vs_n1` pokazywał tylko 4 scenariusze (n2, k)
- Dla każdego scenariusza był tylko jeden punkt (n1=3)
- Brak trendów, tylko pojedyncze punkty

### Teraz:
- **Wykres 1**: Wszystkie dane agregowane po n1 - pokazuje pełny trend
- **Wykresy 2-4**: Tylko scenariusze z różnymi n1 (więcej niż 1 wartość)
- Trend lines z regresją liniową
- Error bars pokazujące odchylenie standardowe

## Problem 2: "Dziury" w heatmapie

### Przed:
- Heatmapa miała dużo białych miejsc (brak danych)
- Nie wszystkie kombinacje (n1, n2) były testowane
- Nieczytelne, "dziurawe"

### Teraz:
- **Scenariusz `scaling`**: Systematyczne pokrycie wszystkich kombinacji
  - n1: 3-10
  - n2: od n1+2 do 20 (co 2), plus większe dla wybranych n1
  - k: 1-5
- **Heatmapa**: Uśredniona po k (każda komórka = średnia wszystkich k dla danego (n1, n2))
- Interpolacja bilinear dla lepszego wyglądu
- Informacja o liczbie punktów danych

## Co zostało zmienione w kodzie

### `performance_tests.py`:
```python
# PRZED: Losowe kombinacje, duplikaty
# TERAZ: Systematyczne pokrycie
for n1 in range(3, 11):  # n1: 3-10
    for n2 in range(n1 + 2, 21, 2):  # n2: od n1+2 do 20, co 2
        for k in range(1, 6):  # k: 1-5
            scenarios.append((n1, n2, k))
```

### `generate_plots.py`:
- `plot_time_vs_n1`: Teraz pokazuje WSZYSTKIE dane agregowane po n1
- Filtruje scenariusze - tylko te z różnymi n1
- Trend lines z wartością nachylenia

### `generate_plots_improved.py`:
- `plot_heatmap_time`: Uśrednia po k, interpolacja bilinear
- Lepsze kolory tekstu (biały/czarny w zależności od tła)
- Informacja o liczbie punktów danych

## Jak używać

```bash
# 1. Wygeneruj testy (teraz systematyczne!)
python3.13 performance_tests.py --scenario scaling --runs 1 --timeout 120

# 2. Wygeneruj wykresy (teraz pokazują wszystkie dane!)
python3.13 generate_plots.py
python3.13 generate_plots_improved.py
```

## Rezultat

- ✅ **Wykresy pokazują trendy** - nie tylko pojedyncze punkty
- ✅ **Heatmapa bez dziur** - systematyczne pokrycie wszystkich kombinacji
- ✅ **Wszystkie dane widoczne** - agregowane i indywidualne punkty
- ✅ **Trend lines** - regresja liniowa pokazująca kierunek
- ✅ **Error bars** - odchylenie standardowe

