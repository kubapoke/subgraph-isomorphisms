# Problem z generowaniem testów - NAPRAWIONE

## Problem

Wcześniejsza wersja `generate_test_case` **zawsze** umieszczała G1 jako podgraf w **pierwszych n1 wierzchołkach** G2. To powodowało:

1. **Trywialne rozwiązanie** - algorytm zawsze znajdował rozwiązanie w pierwszych n1 wierzchołkach
2. **Podobne czasy** (~30-60ms) - nawet dla dużych n1, n2, bo rozwiązanie było oczywiste
3. **100% sukces** - wszystkie testy kończyły się sukcesem
4. **Nierealistyczne testy** - nie testowały prawdziwej złożoności algorytmu

## Co zostało naprawione

### Nowa funkcja `generate_test_case`:

**Parametr `easy`**:
- `easy=True`: G1 jest podgrafem G2 (w losowych miejscach, nie zawsze pierwsze n1)
- `easy=False`: G1 i G2 są niezależne - może nie być rozwiązania (NO_SOL)

**Domyślne zachowanie**:
- Małe testy (n1<7 i n2<20): łatwe (zawsze rozwiązanie)
- Duże testy (n1>=7 lub n2>=20): trudne (może nie być rozwiązania)

### Nowe opcje wiersza poleceń:

```bash
# Łatwe testy (G1 zawsze podgraf G2) - szybkie, zawsze rozwiązanie
python3.13 performance_tests.py --scenario scaling --easy-tests

# Trudne testy (G1 i G2 niezależne) - realistyczne, może być NO_SOL
python3.13 performance_tests.py --scenario scaling --hard-tests

# Domyślnie: automatycznie (łatwe dla małych, trudne dla dużych)
python3.13 performance_tests.py --scenario scaling
```

## Co się zmieniło w kodzie

### Przed:
```python
# Zawsze pierwsze n1 wierzchołków = G1
if i < n1 and j < n1:
    base = g1_matrix[i][j]  # Trywialne!
```

### Teraz:
```python
if easy:
    # G1 w losowych miejscach G2
    g1_positions = sorted(random.sample(range(n2), n1))
    # Mapowanie G1 -> G2 w losowych pozycjach
else:
    # G1 i G2 niezależne - może nie być rozwiązania!
    # Tylko 30% szansy że G1 jest podgrafem
```

## Rezultat

- ✅ **Realistyczne testy** - większe testy są trudniejsze
- ✅ **Różnorodne czasy** - zależne od trudności problemu
- ✅ **NO_SOL możliwe** - dla trudnych testów
- ✅ **Lepsze testy wydajnościowe** - pokazują prawdziwą złożoność

## Uwaga

Po zmianie możesz zobaczyć:
- Więcej NO_SOL dla dużych testów (to normalne!)
- Większe różnice w czasach (zależnie od trudności)
- Dłuższe czasy dla trudnych testów (to pokazuje prawdziwą złożoność)

