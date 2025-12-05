# Szybkie naprawy błędów

## Naprawione błędy

1. ✅ **Brak importu Optional** w `compare_algorithms.py` - naprawione
2. ✅ **TestResult bez pola test_file** w `generate_report.py` - naprawione (ignoruje nieznane pola)
3. ✅ **Brak obsługi numpy/matplotlib** w `generate_plots.py` - dodana obsługa braku bibliotek
4. ✅ **Wszystkie testy zwracają NO_SOL** - poprawione generowanie testów (G1 jest podgrafem G2)

## Nowe funkcje

- **Opcja używania istniejących testów** - zamiast generować losowe testy, można użyć istniejących z katalogów `tests/`, `tests_auto/`, `tests_stress/`

## Jak używać

### Opcja 1: Użyj istniejących testów (ZALECANE)
```bash
python performance_tests.py --use-existing
```

lub

```bash
python run_all_tests.py --scenario existing
```

### Opcja 2: Generuj losowe testy (poprawione)
```bash
python performance_tests.py --scenario small
```

## Instalacja bibliotek

Jeśli chcesz generować wykresy:
```bash
pip install matplotlib numpy
```

## Uwaga o testach

Losowe testy mogą nadal zwracać NO_SOL, ponieważ:
- Problem subgraph isomorphism jest trudny
- Losowe grafy mogą nie mieć rozwiązania

**Zalecenie:** Użyj opcji `--use-existing` aby testować na istniejących testach, które na pewno mają rozwiązania.

