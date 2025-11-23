#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENERATOR MAŁYCH TESTÓW - weryfikowalne ręcznie na kartce
===========================================================
Generuje proste testy gdzie można policzyć koszt ręcznie i sprawdzić poprawność
"""

import os

def create_test_file(filename, n1, matrix1, n2, matrix2, k, description):
    """Tworzy plik testowy z opisem"""
    os.makedirs('tests_manual_verify', exist_ok=True)
    filepath = os.path.join('tests_manual_verify', filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"{n1}\n")
        for row in matrix1:
            f.write(" ".join(map(str, row)) + "\n")
        f.write(f"{n2}\n")
        for row in matrix2:
            f.write(" ".join(map(str, row)) + "\n")
        f.write(f"{k}\n")
    
    # Zapisz opis obok
    desc_file = filepath.replace('.txt', '_OPIS.txt')
    with open(desc_file, 'w', encoding='utf-8') as f:
        f.write(description)
    
    print(f"Created: {filename}")
    print(f"  {description.split(chr(10))[0]}")


def main():
    print("=" * 80)
    print("GENERATOR TESTÓW DO RĘCZNEJ WERYFIKACJI")
    print("=" * 80)
    print()
    
    # TEST 1: Pojedyncza krawędź w pustym grafie
    create_test_file(
        'manual_01_single_edge.txt',
        n1=2,
        matrix1=[
            [0, 1],
            [0, 0]
        ],
        n2=2,
        matrix2=[
            [0, 0],
            [0, 0]
        ],
        k=1,
        description="""TEST 1: Pojedyncza krawędź w pustym grafie
G1: 0→1 (jedna krawędź)
G2: pusty (2 wierzchołki, 0 krawędzi)
k=1

RĘCZNE OBLICZENIE:
- Mapowanie: M(0)=0, M(1)=1 (lub M(0)=1, M(1)=0)
- G1 wymaga krawędzi 0→1
- G2 nie ma tej krawędzi
- Trzeba dodać: 1 krawędź

OCZEKIWANY KOSZT: 1
OCZEKIWANE MAPOWANIE: {0→0, 1→1} lub {0→1, 1→0}
"""
    )
    
    # TEST 2: Trójkąt w grafie z 3 wierzchołkami
    create_test_file(
        'manual_02_triangle.txt',
        n1=3,
        matrix1=[
            [0, 1, 1],
            [1, 0, 1],
            [1, 1, 0]
        ],
        n2=3,
        matrix2=[
            [0, 1, 0],
            [0, 0, 0],
            [0, 0, 0]
        ],
        k=1,
        description="""TEST 2: Trójkąt (K3) w grafie z jedną krawędzią
G1: Trójkąt (pełny graf K3)
    0↔1, 0↔2, 1↔2 (6 krawędzi nieskierowanych = 6 w macierzy)
G2: Jedna krawędź 0→1
k=1

RĘCZNE OBLICZENIE:
- Najlepsze mapowanie: M(0)=0, M(1)=1, M(2)=2
- G1 wymaga:
  * 0→1 ✓ (jest w G2)
  * 1→0 (trzeba dodać)
  * 0→2 (trzeba dodać)
  * 2→0 (trzeba dodać)
  * 1→2 (trzeba dodać)
  * 2→1 (trzeba dodać)

OCZEKIWANY KOSZT: 5
"""
    )
    
    # TEST 3: Ścieżka P3 w ścieżce P4
    create_test_file(
        'manual_03_path_in_path.txt',
        n1=3,
        matrix1=[
            [0, 1, 0],
            [0, 0, 1],
            [0, 0, 0]
        ],
        n2=4,
        matrix2=[
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [0, 0, 0, 0]
        ],
        k=1,
        description="""TEST 3: Ścieżka P3 w ścieżce P4
G1: 0→1→2 (ścieżka długości 2)
G2: 0→1→2→3 (ścieżka długości 3)
k=1

RĘCZNE OBLICZENIE:
- G1 jest podgrafem G2!
- Mapowanie: M(0)=0, M(1)=1, M(2)=2
- Wszystkie krawędzie G1 już są w G2
- Nie trzeba nic dodawać

OCZEKIWANY KOSZT: 0
"""
    )
    
    # TEST 4: Pętla (self-loop)
    create_test_file(
        'manual_04_selfloop.txt',
        n1=2,
        matrix1=[
            [1, 0],
            [0, 1]
        ],
        n2=2,
        matrix2=[
            [0, 0],
            [0, 0]
        ],
        k=1,
        description="""TEST 4: Dwie pętle (self-loops)
G1: Dwa wierzchołki, każdy z pętlą
    0: pętla (0→0)
    1: pętla (1→1)
G2: Pusty (2 wierzchołki, 0 krawędzi)
k=1

RĘCZNE OBLICZENIE:
- Mapowanie: M(0)=0, M(1)=1
- G1 wymaga:
  * pętla na 0 (trzeba dodać)
  * pętla na 1 (trzeba dodać)

OCZEKIWANY KOSZT: 2
"""
    )
    
    # TEST 5: Krotność krawędzi
    create_test_file(
        'manual_05_multiplicity.txt',
        n1=2,
        matrix1=[
            [0, 3],
            [0, 0]
        ],
        n2=2,
        matrix2=[
            [0, 1],
            [0, 0]
        ],
        k=1,
        description="""TEST 5: Krotność krawędzi (multigraf)
G1: 0→1 z krotnością 3 (3 krawędzie)
G2: 0→1 z krotnością 1 (1 krawędź)
k=1

RĘCZNE OBLICZENIE:
- Mapowanie: M(0)=0, M(1)=1
- G1 wymaga 3 krawędzi 0→1
- G2 ma tylko 1 krawędź 0→1
- Trzeba dodać: 3 - 1 = 2 krawędzie

OCZEKIWANY KOSZT: 2
"""
    )
    
    # TEST 6: Dwie kopie - prosty przypadek
    create_test_file(
        'manual_06_two_copies.txt',
        n1=2,
        matrix1=[
            [0, 1],
            [0, 0]
        ],
        n2=4,
        matrix2=[
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ],
        k=2,
        description="""TEST 6: Dwie kopie krawędzi w pustym grafie
G1: 0→1 (jedna krawędź)
G2: Pusty (4 wierzchołki, 0 krawędzi)
k=2

RĘCZNE OBLICZENIE:
- Kopia 1: M1(0)=0, M1(1)=1 → dodaj krawędź 0→1
- Kopia 2: M2(0)=2, M2(1)=3 → dodaj krawędź 2→3
- Obrazy są różne: Im(M1)={0,1}, Im(M2)={2,3} ✓

OCZEKIWANY KOSZT: 2 (po jednej krawędzi dla każdej kopii)
"""
    )
    
    # TEST 7: Przypadek niemożliwy (k*n1 > n2)
    create_test_file(
        'manual_07_impossible.txt',
        n1=3,
        matrix1=[
            [0, 1, 0],
            [0, 0, 1],
            [0, 0, 0]
        ],
        n2=3,
        matrix2=[
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ],
        k=2,
        description="""TEST 7: Przypadek NIEMOŻLIWY (k*n1 > n2)
G1: Ścieżka 0→1→2 (3 wierzchołki)
G2: Pusty (3 wierzchołki)
k=2

RĘCZNE OBLICZENIE:
- k*n1 = 2*3 = 6 > 3 = n2
- Potrzeba 2 różne 3-elementowe podzbiory z 3-elementowego zbioru
- Istnieje tylko 1 taki podzbiór: {0,1,2}
- MATEMATYCZNIE NIEMOŻLIWE!

OCZEKIWANY WYNIK: NO_SOLUTION (exact), lub naruszenie Def5 (approx)
"""
    )
    
    # TEST 8: Cykl C3 z dodatkową krawędzią
    create_test_file(
        'manual_08_cycle_plus.txt',
        n1=3,
        matrix1=[
            [0, 1, 0],
            [0, 0, 1],
            [1, 0, 0]
        ],
        n2=3,
        matrix2=[
            [0, 1, 1],
            [0, 0, 1],
            [1, 0, 0]
        ],
        k=1,
        description="""TEST 8: Cykl C3 w grafie z cyklem i dodatkową krawędzią
G1: Cykl 0→1→2→0
G2: Cykl 0→1→2→0 + krawędź 0→2
k=1

RĘCZNE OBLICZENIE:
- G1 jest podgrafem G2!
- Mapowanie: M(0)=0, M(1)=1, M(2)=2
- G1 wymaga: 0→1, 1→2, 2→0
- G2 ma: 0→1, 1→2, 2→0, 0→2
- Wszystkie wymagane krawędzie już są!

OCZEKIWANY KOSZT: 0
"""
    )
    
    # TEST 9: Gwiazda S3
    create_test_file(
        'manual_09_star.txt',
        n1=4,
        matrix1=[
            [0, 1, 1, 1],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ],
        n2=4,
        matrix2=[
            [0, 1, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ],
        k=1,
        description="""TEST 9: Gwiazda S3 (hub z 3 krawędziami)
G1: Wierzchołek 0 połączony z 1,2,3 (gwiazda)
    Krawędzie: 0→1, 0→2, 0→3
G2: Tylko jedna krawędź 0→1
k=1

RĘCZNE OBLICZENIE:
- Mapowanie: M(0)=0, M(1)=1, M(2)=2, M(3)=3
- G1 wymaga:
  * 0→1 ✓ (jest w G2)
  * 0→2 (trzeba dodać)
  * 0→3 (trzeba dodać)

OCZEKIWANY KOSZT: 2
"""
    )
    
    # TEST 10: Graniczny przypadek k*n1 = n2
    create_test_file(
        'manual_10_boundary.txt',
        n1=2,
        matrix1=[
            [0, 1],
            [0, 0]
        ],
        n2=4,
        matrix2=[
            [0, 1, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 0, 0]
        ],
        k=2,
        description="""TEST 10: Graniczny przypadek k*n1 = n2
G1: 0→1 (jedna krawędź)
G2: Dwie krawędzie: 0→1 i 2→3 (4 wierzchołki)
k=2

RĘCZNE OBLICZENIE:
- k*n1 = 2*2 = 4 = n2 (graniczny przypadek!)
- Kopia 1: M1(0)=0, M1(1)=1 → krawędź 0→1 już jest ✓
- Kopia 2: M2(0)=2, M2(1)=3 → krawędź 2→3 już jest ✓
- Im(M1)={0,1}, Im(M2)={2,3} - różne ✓
- Nic nie trzeba dodawać!

OCZEKIWANY KOSZT: 0
"""
    )
    
    print()
    print("=" * 80)
    print("PODSUMOWANIE")
    print("=" * 80)
    print(f"\nWygenerowano 10 testów do ręcznej weryfikacji w katalogu: tests_manual_verify/")
    print()
    print("Każdy test ma:")
    print("  - Plik .txt z danymi (format jak wszystkie inne testy)")
    print("  - Plik _OPIS.txt ze szczegółowym obliczeniem na kartce")
    print()
    print("Testy pokrywają:")
    print("  [OK] Pojedyncza krawędź")
    print("  [OK] Trójkąt (K3)")
    print("  [OK] Ścieżki")
    print("  [OK] Pętle (self-loops)")
    print("  [OK] Krotność krawędzi")
    print("  [OK] Wiele kopii (k>1)")
    print("  [OK] Przypadek niemożliwy (k*n1 > n2)")
    print("  [OK] Cykle")
    print("  [OK] Gwiazdy")
    print("  [OK] Przypadek graniczny (k*n1 = n2)")
    print()
    print("UŻYCIE:")
    print("  .\\build\\subgraph-isomorphism.exe tests_manual_verify\\manual_01_single_edge.txt exact")
    print("  Porównaj wynik z plikiem manual_01_single_edge_OPIS.txt")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
