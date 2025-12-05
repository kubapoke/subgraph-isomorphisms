# Instrukcja instalacji i użycia

## Problem z Pythonem

Masz dwa Pythony:
- **Python 3.12** (msys64) - używany domyślnie przez `python`, ale nie ma pip
- **Python 3.13** (Windows Store) - ma pip i zainstalowane biblioteki

## Rozwiązanie

### Opcja 1: Użyj Python 3.13 bezpośrednio (ZALECANE)

Wszystkie skrypty uruchamiaj przez `python3.13`:

```bash
# Testy wydajnościowe
python3.13 performance_tests.py --use-existing

# Generowanie wykresów
python3.13 generate_plots.py

# Porównanie algorytmów
python3.13 compare_algorithms.py

# Sprawozdanie
python3.13 generate_report.py

# Wszystko naraz
python3.13 run_all_tests.py
```

### Opcja 2: Zmień domyślny Python (zaawansowane)

Możesz zmienić PATH w systemie, żeby `python` wskazywał na Python 3.13, ale to może zepsuć inne rzeczy.

### Opcja 3: Użyj skryptów batch (łatwe)

Utworzyłem skrypty `.bat`, które automatycznie używają Python 3.13.

## Sprawdzenie czy działa

```bash
# Sprawdź czy Python 3.13 ma biblioteki
python3.13 -c "import matplotlib; import numpy; print('OK!')"

# Jeśli widzisz "OK!", wszystko działa!
```

## Instalacja bibliotek (jeśli potrzebne)

```bash
# Zainstaluj w Python 3.13
pip install matplotlib numpy

# Lub przez python3.13
python3.13 -m pip install matplotlib numpy
```

