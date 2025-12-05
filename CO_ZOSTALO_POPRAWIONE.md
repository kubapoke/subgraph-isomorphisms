# Co zostało poprawione

## 1. Więcej testów

### Scenariusz `scaling` (ZALECANE)
- **Przed**: ~30 testów
- **Teraz**: ~100+ testów
- Więcej kombinacji n1, n2, k
- Lepsze pokrycie przestrzeni parametrów

### Nowy scenariusz `comprehensive`
- **~300+ testów** - systematyczne pokrycie całej przestrzeni parametrów
- n1: 3-10
- n2: 8-30 (co 2)
- k: 1-5
- Dla solidnych, statystycznie istotnych danych

## 2. Ulepszone wykresy

### Wizualne ulepszenia:
- ✅ **Większe punkty** (s=100 zamiast 40) - lepiej widoczne
- ✅ **Lepsze kolory** - profesjonalna paleta (#2E86AB, #F77F00, etc.)
- ✅ **Error bars** - pokazują odchylenie standardowe (σ)
- ✅ **Trend lines** - regresja liniowa pokazująca kierunek trendu
- ✅ **Lepsze etykiety** - większe, pogrubione, czytelniejsze
- ✅ **Tło wykresów** - jasnoszare (#FAFAFA) dla lepszego kontrastu
- ✅ **Legenda** - z cieniem i przezroczystością
- ✅ **Siatka** - bardziej subtelna, ale widoczna

### Nowe informacje na wykresach:
- Średnia ± odchylenie standardowe (error bars)
- Trend line z nachyleniem (slope)
- Wszystkie punkty danych (nie tylko średnie)
- Lepsze kolory dla Exact (niebieski) i Approx (pomarańczowy)

## 3. Jak używać

### Szybki start (scaling - ~100 testów):
```bash
python3.13 performance_tests.py --scenario scaling --runs 1 --timeout 120
python3.13 generate_plots.py
```

### Pełny zestaw (comprehensive - ~300 testów):
```bash
python3.13 performance_tests.py --scenario comprehensive --runs 1 --timeout 180
python3.13 generate_plots.py
```

## 4. Co się zmieniło w wykresach

### Przed:
- Małe punkty (s=40)
- Słaba widoczność (alpha=0.4)
- Tylko średnie (bez error bars)
- Brak trend lines
- Podstawowe kolory

### Teraz:
- Duże, wyraźne punkty (s=100)
- Lepsza widoczność (alpha=0.6)
- Średnie + error bars (odchylenie standardowe)
- Trend lines z regresją
- Profesjonalna paleta kolorów
- Lepsze etykiety i legenda
- Czytelniejsza siatka i tło

## 5. Rekomendacje

- **Dla szybkich testów**: `scaling` (~100 testów, ~10-20 min)
- **Dla solidnych danych**: `comprehensive` (~300 testów, ~30-60 min)
- **Dla wykresów**: zawsze użyj `generate_plots.py` - teraz pokazuje więcej informacji!

