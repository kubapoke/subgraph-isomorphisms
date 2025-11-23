#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generator POPRAWNYCH testów edge case
======================================
Generuje testy które spełniają: k * n1 <= n2
Wszystkie muszą być rozwiązywalne przez algorytm exact!
"""

import random
import os

def create_test_directory():
    """Tworzy katalog dla nowych testów"""
    dir_path = "tests_valid_edge_cases"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path

def write_test(filepath, n1, matrix_g1, n2, matrix_g2, k):
    """Zapisuje test do pliku"""
    with open(filepath, 'w') as f:
        # G1
        f.write(f"{n1}\n")
        for row in matrix_g1:
            f.write(" ".join(map(str, row)) + "\n")
        
        # G2
        f.write(f"{n2}\n")
        for row in matrix_g2:
            f.write(" ".join(map(str, row)) + "\n")
        
        # k
        f.write(f"{k}\n")

def generate_isolated_vertices():
    """Test 1: Grafy z izolowanymi wierzchołkami"""
    dir_path = create_test_directory()
    
    # G1: 3 wierzchołki, 1 krawędź, 2 izolowane
    n1 = 3
    g1 = [[0, 1, 0],
          [0, 0, 0],
          [0, 0, 0]]
    
    # G2: 8 wierzchołków, wystarczająco dla k=2
    n2 = 8
    g2 = [[0]*n2 for _ in range(n2)]
    g2[0][1] = 1
    g2[2][3] = 1
    
    k = 2
    write_test(f"{dir_path}/isolated_vertices_01.txt", n1, g1, n2, g2, k)
    print(f"✓ isolated_vertices_01: n1={n1}, n2={n2}, k={k} (k*n1={k*n1})")

def generate_bipartite():
    """Test 2: Graf dwudzielny"""
    dir_path = create_test_directory()
    
    # G1: K_{2,2} - pełny graf dwudzielny
    n1 = 4
    g1 = [[0, 0, 1, 1],
          [0, 0, 1, 1],
          [1, 1, 0, 0],
          [1, 1, 0, 0]]
    
    # G2: większy graf dwudzielny (wystarczy dla k=2)
    n2 = 10
    g2 = [[0]*n2 for _ in range(n2)]
    # Krawędzie między grupami (0-4) i (5-9)
    for i in range(5):
        for j in range(5, 10):
            g2[i][j] = 1
            g2[j][i] = 1
    
    k = 2
    write_test(f"{dir_path}/bipartite_01.txt", n1, g1, n2, g2, k)
    print(f"✓ bipartite_01: n1={n1}, n2={n2}, k={k} (k*n1={k*n1})")

def generate_tree_binary():
    """Test 3: Drzewo binarne"""
    dir_path = create_test_directory()
    
    # G1: małe drzewo binarne (3 poziomy)
    n1 = 7
    g1 = [[0]*n1 for _ in range(n1)]
    # Korzeń 0 -> dzieci 1,2
    g1[0][1] = 1
    g1[0][2] = 1
    # 1 -> dzieci 3,4
    g1[1][3] = 1
    g1[1][4] = 1
    # 2 -> dzieci 5,6
    g1[2][5] = 1
    g1[2][6] = 1
    
    # G2: większe drzewo (wystarczy dla k=2)
    n2 = 15
    g2 = [[0]*n2 for _ in range(n2)]
    g2[0][1] = g2[0][2] = 1
    g2[1][3] = g2[1][4] = 1
    g2[2][5] = g2[2][6] = 1
    g2[3][7] = g2[3][8] = 1
    g2[4][9] = g2[4][10] = 1
    g2[5][11] = g2[5][12] = 1
    g2[6][13] = g2[6][14] = 1
    
    k = 2
    write_test(f"{dir_path}/tree_binary_01.txt", n1, g1, n2, g2, k)
    print(f"✓ tree_binary_01: n1={n1}, n2={n2}, k={k} (k*n1={k*n1})")

def generate_high_multiplicity():
    """Test 4: Bardzo wysokie krotności"""
    dir_path = create_test_directory()
    
    # G1: 2 wierzchołki, krotność 15
    n1 = 2
    g1 = [[0, 15],
          [0, 0]]
    
    # G2: 6 wierzchołków (wystarczy dla k=3)
    n2 = 6
    g2 = [[0]*n2 for _ in range(n2)]
    g2[0][1] = 15
    g2[2][3] = 10
    g2[4][5] = 5
    
    k = 3
    write_test(f"{dir_path}/high_multiplicity_01.txt", n1, g1, n2, g2, k)
    print(f"✓ high_multiplicity_01: n1={n1}, n2={n2}, k={k} (k*n1={k*n1})")

def generate_selfloops_only():
    """Test 5: Graf tylko z pętlami"""
    dir_path = create_test_directory()
    
    # G1: 3 wierzchołki, tylko pętle
    n1 = 3
    g1 = [[5, 0, 0],
          [0, 3, 0],
          [0, 0, 7]]
    
    # G2: 9 wierzchołków (wystarczy dla k=3)
    n2 = 9
    g2 = [[0]*n2 for _ in range(n2)]
    for i in range(n2):
        g2[i][i] = random.randint(3, 10)
    
    k = 3
    write_test(f"{dir_path}/selfloops_only_01.txt", n1, g1, n2, g2, k)
    print(f"✓ selfloops_only_01: n1={n1}, n2={n2}, k={k} (k*n1={k*n1})")

def generate_regular_graph():
    """Test 6: Graf regularny (wszystkie wierzchołki ten sam stopień)"""
    dir_path = create_test_directory()
    
    # G1: cykl C5 (graf 2-regularny)
    n1 = 5
    g1 = [[0, 1, 0, 0, 1],
          [1, 0, 1, 0, 0],
          [0, 1, 0, 1, 0],
          [0, 0, 1, 0, 1],
          [1, 0, 0, 1, 0]]
    
    # G2: większy cykl (wystarczy dla k=2)
    n2 = 12
    g2 = [[0]*n2 for _ in range(n2)]
    for i in range(n2):
        g2[i][(i+1) % n2] = 1
        g2[i][(i-1) % n2] = 1
    
    k = 2
    write_test(f"{dir_path}/regular_graph_01.txt", n1, g1, n2, g2, k)
    print(f"✓ regular_graph_01: n1={n1}, n2={n2}, k={k} (k*n1={k*n1})")

def generate_dense_graph():
    """Test 7: Bardzo gęsty graf (gęstość ~80%)"""
    dir_path = create_test_directory()
    
    # G1: gęsty graf (5 wierzchołków)
    n1 = 5
    g1 = [[0]*n1 for _ in range(n1)]
    for i in range(n1):
        for j in range(n1):
            if i != j and random.random() < 0.8:
                g1[i][j] = random.randint(1, 3)
    
    # G2: większy gęsty graf (wystarczy dla k=2)
    n2 = 12
    g2 = [[0]*n2 for _ in range(n2)]
    for i in range(n2):
        for j in range(n2):
            if i != j and random.random() < 0.6:
                g2[i][j] = random.randint(1, 2)
    
    k = 2
    write_test(f"{dir_path}/dense_graph_01.txt", n1, g1, n2, g2, k)
    print(f"✓ dense_graph_01: n1={n1}, n2={n2}, k={k} (k*n1={k*n1})")

def generate_sparse_graph():
    """Test 8: Bardzo rzadki graf (gęstość ~10%)"""
    dir_path = create_test_directory()
    
    # G1: rzadki graf (6 wierzchołków)
    n1 = 6
    g1 = [[0]*n1 for _ in range(n1)]
    for i in range(n1):
        for j in range(n1):
            if i != j and random.random() < 0.1:
                g1[i][j] = 1
    
    # G2: większy rzadki graf (wystarczy dla k=2)
    n2 = 15
    g2 = [[0]*n2 for _ in range(n2)]
    for i in range(n2):
        for j in range(n2):
            if i != j and random.random() < 0.08:
                g2[i][j] = 1
    
    k = 2
    write_test(f"{dir_path}/sparse_graph_01.txt", n1, g1, n2, g2, k)
    print(f"✓ sparse_graph_01: n1={n1}, n2={n2}, k={k} (k*n1={k*n1})")

def generate_boundary_k_min():
    """Test 9: k=1 (minimum)"""
    dir_path = create_test_directory()
    
    # G1: prosty graf
    n1 = 4
    g1 = [[0, 1, 0, 1],
          [0, 0, 1, 0],
          [0, 0, 0, 1],
          [0, 0, 0, 0]]
    
    # G2: większy graf
    n2 = 6
    g2 = [[0]*n2 for _ in range(n2)]
    g2[0][1] = g2[1][2] = g2[2][3] = g2[0][3] = 1
    
    k = 1  # minimum
    write_test(f"{dir_path}/boundary_k_min_01.txt", n1, g1, n2, g2, k)
    print(f"✓ boundary_k_min_01: n1={n1}, n2={n2}, k={k} (k*n1={k*n1})")

def generate_boundary_k_equals_n1():
    """Test 10: k * n1 = n2 (graniczny przypadek)"""
    dir_path = create_test_directory()
    
    # G1: bardzo mały graf
    n1 = 2
    g1 = [[0, 1],
          [0, 0]]
    
    # G2: dokładnie k*n1 wierzchołków
    n2 = 10  # k=5, więc 5*2=10
    g2 = [[0]*n2 for _ in range(n2)]
    for i in range(0, n2-1, 2):
        g2[i][i+1] = 1
    
    k = 5  # graniczny: k*n1 = 10 = n2
    write_test(f"{dir_path}/boundary_k_max_01.txt", n1, g1, n2, g2, k)
    print(f"✓ boundary_k_max_01: n1={n1}, n2={n2}, k={k} (k*n1={k*n1}=n2)")

def generate_asymmetric_directed():
    """Test 11: Silnie asymetryczny graf skierowany"""
    dir_path = create_test_directory()
    
    # G1: silnie skierowany w jedną stronę (łańcuch)
    n1 = 4
    g1 = [[0, 3, 0, 0],  # Wysokie krotności w jednym kierunku
          [0, 0, 2, 0],
          [0, 0, 0, 4],
          [0, 0, 0, 0]]
    
    # G2: większy graf z różnymi kierunkami
    n2 = 10
    g2 = [[0]*n2 for _ in range(n2)]
    for i in range(n2-1):
        g2[i][i+1] = random.randint(1, 5)  # Skierowany łańcuch
    
    k = 2
    write_test(f"{dir_path}/asymmetric_directed_01.txt", n1, g1, n2, g2, k)
    print(f"✓ asymmetric_directed_01: n1={n1}, n2={n2}, k={k} (k*n1={k*n1})")

def generate_mixed_loops_and_edges():
    """Test 12: Mieszanka pętli i krawędzi"""
    dir_path = create_test_directory()
    
    # G1: graf z pętlami i normalnymi krawędziami
    n1 = 4
    g1 = [[2, 1, 0, 0],  # pętla na 0, krawędź 0->1
          [0, 3, 1, 0],  # pętla na 1, krawędź 1->2
          [0, 0, 1, 1],  # pętla na 2, krawędź 2->3
          [1, 0, 0, 4]]  # pętla na 3, krawędź 3->0
    
    # G2: większy z pętlami
    n2 = 10
    g2 = [[0]*n2 for _ in range(n2)]
    for i in range(n2):
        g2[i][i] = random.randint(1, 5)  # Pętle
        if i < n2-1:
            g2[i][i+1] = random.randint(0, 3)  # Krawędzie
    
    k = 2
    write_test(f"{dir_path}/mixed_loops_edges_01.txt", n1, g1, n2, g2, k)
    print(f"✓ mixed_loops_edges_01: n1={n1}, n2={n2}, k={k} (k*n1={k*n1})")

def generate_large_k():
    """Test 13: Duże k (k=10)"""
    dir_path = create_test_directory()
    
    # G1: bardzo mały graf (łatwy do znajdowania kopii)
    n1 = 2
    g1 = [[0, 1],
          [0, 0]]
    
    # G2: dużo wierzchołków dla k=10
    n2 = 25  # 10*2 = 20 < 25, więc OK
    g2 = [[0]*n2 for _ in range(n2)]
    for i in range(n2-1):
        g2[i][i+1] = 1
    
    k = 10  # duże k
    write_test(f"{dir_path}/large_k_01.txt", n1, g1, n2, g2, k)
    print(f"✓ large_k_01: n1={n1}, n2={n2}, k={k} (k*n1={k*n1})")

def generate_star_graph():
    """Test 14: Graf gwiaździsty"""
    dir_path = create_test_directory()
    
    # G1: gwiazda S_4 (środek + 4 liście)
    n1 = 5
    g1 = [[0]*n1 for _ in range(n1)]
    for i in range(1, n1):
        g1[0][i] = 1  # Krawędzie ze środka do liści
    
    # G2: większa gwiazda
    n2 = 12
    g2 = [[0]*n2 for _ in range(n2)]
    for i in range(1, n2):
        g2[0][i] = 1
    
    k = 2
    write_test(f"{dir_path}/star_graph_01.txt", n1, g1, n2, g2, k)
    print(f"✓ star_graph_01: n1={n1}, n2={n2}, k={k} (k*n1={k*n1})")

def generate_clique():
    """Test 15: Klika (graf pełny)"""
    dir_path = create_test_directory()
    
    # G1: K_4 (klika 4-wierzchołkowa)
    n1 = 4
    g1 = [[0]*n1 for _ in range(n1)]
    for i in range(n1):
        for j in range(n1):
            if i != j:
                g1[i][j] = 1
    
    # G2: K_10 (większa klika)
    n2 = 10
    g2 = [[0]*n2 for _ in range(n2)]
    for i in range(n2):
        for j in range(n2):
            if i != j:
                g2[i][j] = 1
    
    k = 2
    write_test(f"{dir_path}/clique_01.txt", n1, g1, n2, g2, k)
    print(f"✓ clique_01: n1={n1}, n2={n2}, k={k} (k*n1={k*n1})")

def main():
    print("="*60)
    print("GENERATOR POPRAWNYCH TESTÓW EDGE CASE")
    print("="*60)
    print("\nGenerowanie testów które spełniają: k * n1 <= n2")
    print("(Zgodnie z Definicją 5 - różne obrazy mapowań)\n")
    
    tests = [
        ("Izolowane wierzchołki", generate_isolated_vertices),
        ("Graf dwudzielny", generate_bipartite),
        ("Drzewo binarne", generate_tree_binary),
        ("Wysoka krotność", generate_high_multiplicity),
        ("Tylko pętle", generate_selfloops_only),
        ("Graf regularny", generate_regular_graph),
        ("Gęsty graf", generate_dense_graph),
        ("Rzadki graf", generate_sparse_graph),
        ("k=1 (minimum)", generate_boundary_k_min),
        ("k*n1=n2 (graniczny)", generate_boundary_k_equals_n1),
        ("Asymetryczny skierowany", generate_asymmetric_directed),
        ("Mieszanka pętli i krawędzi", generate_mixed_loops_and_edges),
        ("Duże k (k=10)", generate_large_k),
        ("Graf gwiaździsty", generate_star_graph),
        ("Klika (graf pełny)", generate_clique),
    ]
    
    for name, func in tests:
        print(f"\nGenerowanie: {name}...")
        try:
            func()
        except Exception as e:
            print(f"  ✗ BŁĄD: {e}")
    
    print("\n" + "="*60)
    print(f"Wygenerowano {len(tests)} nowych testów!")
    print("Katalog: tests_valid_edge_cases/")
    print("="*60)

if __name__ == "__main__":
    main()
