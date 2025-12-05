# Sprawozdanie z testów wydajnościowych

**Data wygenerowania:** 2025-11-30 20:19:51

---

## 1. Podsumowanie

- **Łączna liczba testów:** 470
- **Exact - poprawne wyniki:** 214
- **Approx - poprawne wyniki:** 218
- **Wspólne testy (do porównania):** 96

### 1.1. Algorytm Exact - Statystyki czasu

| Metryka | Wartość [ms] |
|---------|--------------|
| Średnia | 140.97 |
| Mediana | 47.43 |
| Minimum | 31.24 |
| Maksimum | 5445.73 |

### 1.2. Algorytm Approximate - Statystyki czasu

| Metryka | Wartość [ms] |
|---------|--------------|
| Średnia | 51.21 |
| Mediana | 41.17 |
| Minimum | 29.08 |
| Maksimum | 124.72 |

## 2. Porównanie algorytmów

### 2.1. Porównanie czasu wykonania

| Metryka | Exact [ms] | Approx [ms] | Stosunek (Exact/Approx) |
|---------|------------|-------------|--------------------------|
| Średnia | 219.26 | 47.83 | 4.43x |
| Mediana | 43.73 | 38.65 | 1.07x |

### 2.2. Porównanie kosztu rozszerzenia

| Metryka | Exact | Approx | Stosunek (Approx/Exact) |
|---------|-------|--------|-------------------------|
| Średnia | 26.88 | 36.81 | 1.04x |
| Mediana | 2.00 | 3.00 | 1.00x |

**Rozwiązania optymalne (Approx = Exact):** 32/96 (33.3%)

## 3. Analiza skalowalności

### 3.1. Wpływ n1 (rozmiar grafu G1)

| n1 | Exact - średni czas [ms] | Approx - średni czas [ms] |
|----|--------------------------|---------------------------|
| 1 | 43.22 | 40.23 |
| 2 | 50.97 | 50.78 |
| 3 | 46.75 | 45.75 |
| 4 | 156.11 | 54.20 |
| 5 | 265.34 | 52.48 |
| 6 | 191.62 | 64.47 |
| 7 | 116.92 | 52.74 |
| 8 | 1437.54 | 54.13 |

### 3.2. Wpływ n2 (rozmiar grafu G2)

| n2 | Exact - średni czas [ms] | Approx - średni czas [ms] |
|----|--------------------------|---------------------------|
| 1 | 38.38 | 36.25 |
| 2 | 56.34 | 54.16 |
| 3 | 45.23 | 45.78 |
| 4 | 50.85 | 47.40 |
| 5 | 61.48 | 50.23 |
| 6 | 51.64 | 48.15 |
| 7 | 72.26 | 43.92 |
| 8 | 232.92 | 55.23 |
| 9 | 290.60 | 49.39 |
| 10 | 67.50 | 57.31 |
| 11 | 46.45 | 48.60 |
| 12 | 655.05 | 68.26 |
| 13 | 147.44 | 110.75 |
| 15 | 733.05 | 57.51 |
| 25 | 0.00 | 78.63 |

### 3.3. Wpływ k (liczba kopii)

| k | Exact - średni czas [ms] | Approx - średni czas [ms] |
|----|--------------------------|---------------------------|
| 1 | 56.35 | 48.17 |
| 2 | 156.31 | 50.72 |
| 3 | 223.52 | 56.37 |
| 4 | 477.82 | 50.70 |
| 5 | 83.64 | 65.44 |
| 6 | 47.46 | 64.41 |
| 7 | 60.95 | 65.62 |
| 10 | 50.16 | 55.09 |
| 15 | 59.81 | 61.69 |

## 4. Wnioski

- Algorytm Approximate jest średnio **4.43x szybszy** niż Exact
- Algorytm Approximate znajduje rozwiązania **bardzo bliskie optymalnym** (średnio 1.04x kosztu Exact)
- Approximate znajduje rozwiązanie optymalne w **33.3%** przypadków

---

*Sprawozdanie wygenerowane automatycznie przez generate_report.py*