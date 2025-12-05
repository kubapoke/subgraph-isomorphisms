# Instrukcja testowania - odpowiedzi na pytania

## 1. Czy działa na generowanych testach czy tylko na istniejących?

**Odpowiedź: Działa na OBOJGU!**

### Opcja A: Istniejące testy (domyślnie)
```bash
python3.13 performance_tests.py --use-existing
# LUB
python3.13 performance_tests.py --scenario existing
```

**Co robi:**
- Automatycznie znajduje WSZYSTKIE katalogi zaczynające się od `tests*`
- Zbiera wszystkie pliki `.txt` z tych katalogów
- Uruchamia testy na tych plikach

**Znalezione katalogi:**
- `tests/`
- `tests_auto/`
- `tests_stress/`
- `tests_chaos/`
- `tests_nightmare/`
- `tests_tricky/`
- `tests_v2/`
- `tests_v3_hardcore/`
- `tests_valid_edge_cases/`

### Opcja B: Generowane testy losowe
```bash
python3.13 performance_tests.py --scenario small
python3.13 performance_tests.py --scenario medium
python3.13 performance_tests.py --scenario large
python3.13 performance_tests.py --scenario scaling
```

**Co robi:**
- Generuje losowe testy zgodnie z wybranym scenariuszem
- G1 jest podgrafem G2 (zwiększa szansę na rozwiązanie)
- Uruchamia testy na wygenerowanych plikach

## 2. Jakie foldery są sprawdzane?

### Automatyczne wykrywanie (domyślnie)
System automatycznie znajduje **wszystkie** katalogi zaczynające się od `tests`:
- `tests`
- `tests_auto`
- `tests_stress`
- `tests_chaos`
- `tests_nightmare`
- `tests_tricky`
- `tests_v2`
- `tests_v3_hardcore`
- `tests_valid_edge_cases`

### Ręczne określenie folderów
```bash
python3.13 performance_tests.py --use-existing --test-dirs tests tests_chaos tests_nightmare
```

## Przykłady użycia

### Wszystkie istniejące testy (auto-wykrywanie)
```bash
python3.13 performance_tests.py --use-existing
```

### Tylko wybrane foldery
```bash
python3.13 performance_tests.py --use-existing --test-dirs tests_chaos tests_nightmare
```

### Generowane testy (scaling)
```bash
python3.13 performance_tests.py --scenario scaling
```

### Generowane testy (małe, szybkie)
```bash
python3.13 performance_tests.py --scenario small --runs 3
```

## Sprawdzenie które foldery zostaną użyte

```bash
python3.13 -c "from performance_tests import find_all_test_dirs; print('Znalezione:', find_all_test_dirs())"
```

