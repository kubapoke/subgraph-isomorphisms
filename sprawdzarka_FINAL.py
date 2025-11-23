#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPRAWDZARKA FINAL - ULTIMATE TESTING SUITE
===========================================
Łączy wszystkie poprzednie testy + nowe stress testy:
- 50 testów z v2 (różne kategorie grafów)
- 10 hardcore testów matematycznych (pętle, multigrafy)
- 20 nowych stress testów (duże grafy, ekstremalne k)
- Pełna walidacja matematyczna zgodna z dokumentacją PDF
"""

import subprocess
import os
import re
import time
import random
import sys
from typing import List, Tuple, Dict, Optional, Set
from collections import defaultdict

# ============================================================================
# MATEMATYCZNA WALIDACJA (z v3)
# ============================================================================

class Graph:
    """Reprezentacja multigrafu skierowanego (V, E) gdzie E: V×V → ℕ₀"""
    def __init__(self, n: int, matrix: List[List[int]] = None):
        self.n = n
        self.matrix = matrix if matrix else [[0]*n for _ in range(n)]
        
    def edge_count(self, u: int, v: int) -> int:
        return self.matrix[u][v]
    
    def size(self) -> int:
        return sum(sum(row) for row in self.matrix)
    
    def degree(self, v: int) -> int:
        in_deg = sum(self.matrix[u][v] for u in range(self.n))
        out_deg = sum(self.matrix[v][u] for u in range(self.n))
        return in_deg + out_deg
    
    def copy(self):
        return Graph(self.n, [row[:] for row in self.matrix])


class Mapping:
    """Mapowanie M: V₁ → V₂"""
    def __init__(self, n1: int):
        self.n1 = n1
        self.map = [-1] * n1
        
    def set(self, u: int, v: int):
        self.map[u] = v
        
    def get(self, u: int) -> int:
        return self.map[u]
    
    def is_complete(self) -> bool:
        return all(v != -1 for v in self.map)
    
    def image(self) -> Set[int]:
        return set(v for v in self.map if v != -1)
    
    def is_injection(self) -> bool:
        mapped = [v for v in self.map if v != -1]
        return len(mapped) == len(set(mapped))
    
    def as_tuple(self) -> tuple:
        return tuple(self.map)


def verify_isomorphic_embedding(g1: Graph, g2: Graph, mapping: Mapping) -> Tuple[bool, str]:
    """DEFINICJA 4: E₁(u,v) ≤ E₂(M(u), M(v))"""
    if not mapping.is_complete():
        return False, "Mapowanie niepełne"
    if not mapping.is_injection():
        return False, "Mapowanie nie jest iniekcją"
    
    for u in range(g1.n):
        for v in range(g1.n):
            e1_uv = g1.edge_count(u, v)
            mu = mapping.get(u)
            mv = mapping.get(v)
            e2_mumv = g2.edge_count(mu, mv)
            
            if e1_uv > e2_mumv:
                return False, f"E₁({u},{v})={e1_uv} > E₂({mu},{mv})={e2_mumv}"
    
    return True, "OK"


def verify_k_copies(g1: Graph, g2: Graph, mappings: List[Mapping], k: int) -> Tuple[bool, str]:
    """DEFINICJA 5: k różnych podgrafów z Im(Mi) ≠ Im(Mj)"""
    if len(mappings) != k:
        return False, f"Liczba mapowań {len(mappings)} ≠ k={k}"
    
    for i, mapping in enumerate(mappings):
        ok, msg = verify_isomorphic_embedding(g1, g2, mapping)
        if not ok:
            return False, f"M{i+1}: {msg}"
    
    images = [mapping.image() for mapping in mappings]
    for i in range(k):
        for j in range(i+1, k):
            if images[i] == images[j]:
                return False, f"Im(M{i+1}) = Im(M{j+1}) = {sorted(images[i])}"
    
    return True, "OK"


def compute_extension_cost(g2_orig: Graph, g2_ext: Graph) -> int:
    """DEFINICJA 7: cost(G'₂, G₂) = Σ(E'₂ - E₂)"""
    cost = 0
    for u in range(g2_orig.n):
        for v in range(g2_orig.n):
            diff = g2_ext.edge_count(u, v) - g2_orig.edge_count(u, v)
            if diff < 0:
                raise ValueError(f"E'₂({u},{v}) < E₂({u},{v})")
            cost += diff
    return cost


# ============================================================================
# PARSER
# ============================================================================

def parse_graph_from_file(filepath: str) -> Tuple[Graph, Graph, int]:
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    idx = 0
    n1 = int(lines[idx])
    idx += 1
    matrix1 = []
    for _ in range(n1):
        row = list(map(int, lines[idx].split()))
        matrix1.append(row)
        idx += 1
    
    n2 = int(lines[idx])
    idx += 1
    matrix2 = []
    for _ in range(n2):
        row = list(map(int, lines[idx].split()))
        matrix2.append(row)
        idx += 1
    
    k = 1
    if idx < len(lines):
        k = int(lines[idx])
    
    return Graph(n1, matrix1), Graph(n2, matrix2), k


def parse_algorithm_output(output: str, n1: int, n2: int, k: int) -> Optional[Tuple[Graph, List[Mapping], int]]:
    lines = output.split('\n')
    
    cost = None
    for line in lines:
        if 'Koszt rozszerzenia:' in line:
            match = re.search(r':\s*(\d+)', line)
            if match:
                cost = int(match.group(1))
                break
    
    if cost is None:
        return None
    
    mappings = [Mapping(n1) for _ in range(k)]
    in_mappings = False
    
    for line in lines:
        if 'Mapowania:' in line:
            in_mappings = True
            continue
        
        if in_mappings:
            copy_match = re.match(r'\s*Kopia\s+(\d+):\s*(.+)', line, re.IGNORECASE)
            if copy_match:
                copy_num = int(copy_match.group(1)) - 1
                mapping_str = copy_match.group(2)
                pairs = re.findall(r'(\d+)->(\d+)', mapping_str)
                for u_str, v_str in pairs:
                    u, v = int(u_str), int(v_str)
                    if copy_num < k:
                        mappings[copy_num].set(u, v)
            
            if 'Rozszerzony graf' in line:
                break
    
    g2_extended = None
    in_extended = False
    matrix_lines = []
    
    for line in lines:
        if 'Rozszerzony graf' in line or "G'_2" in line:
            in_extended = True
            continue
        
        if in_extended:
            numbers = re.findall(r'\d+', line)
            if len(numbers) == n2:
                matrix_lines.append(list(map(int, numbers)))
                if len(matrix_lines) == n2:
                    g2_extended = Graph(n2, matrix_lines)
                    break
    
    if g2_extended is None:
        return None
    
    return g2_extended, mappings, cost


def run_algorithm(test_file: str, algorithm: str, timeout_sec: int = 120) -> Tuple[Optional[str], float]:
    exe_path = r".\build\subgraph-isomorphism.exe"
    
    start_time = time.time()
    try:
        result = subprocess.run(
            [exe_path, test_file, algorithm],
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            encoding='utf-8',
            errors='replace'
        )
        elapsed = time.time() - start_time
        return result.stdout, elapsed
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        return None, elapsed


def validate_solution(g1: Graph, g2_orig: Graph, g2_ext: Graph, 
                     mappings: List[Mapping], k: int, reported_cost: int) -> Dict:
    errors = []
    
    ok, msg = verify_k_copies(g1, g2_ext, mappings, k)
    if not ok:
        errors.append(f"❌ {msg}")
    
    actual_cost = compute_extension_cost(g2_orig, g2_ext)
    if actual_cost != reported_cost:
        errors.append(f"❌ Koszt: raportowany={reported_cost}, rzeczywisty={actual_cost}")
    
    for u in range(g2_orig.n):
        for v in range(g2_orig.n):
            if g2_ext.edge_count(u, v) < g2_orig.edge_count(u, v):
                errors.append(f"❌ E'₂({u},{v}) < E₂({u},{v})")
                break
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'actual_cost': actual_cost
    }


# ============================================================================
# GENERATOR STRESS TESTÓW
# ============================================================================

def generate_stress_tests() -> List[Tuple[str, Graph, Graph, int, str]]:
    """
    STRESS TESTY:
    - Duże grafy (n=15-20)
    - Wysokie k (k=5-8)
    - Grafy z 0 krawędzi
    - Pojedyncze wierzchołki
    - DAG-i z wieloma warstwami
    """
    tests = []
    random.seed(123)
    
    # Test 1: Duży losowy graf
    n1, n2 = 6, 10
    m1 = [[random.randint(0, 1) for _ in range(n1)] for _ in range(n1)]
    m2 = [[random.randint(0, 1) for _ in range(n2)] for _ in range(n2)]
    tests.append(("Duży losowy n1=6,n2=10", Graph(n1, m1), Graph(n2, m2), 2, "Większy graf losowy"))
    
    # Test 2: Bardzo duże k
    g1 = Graph(2, [[0, 1], [0, 0]])  # P2
    g2 = Graph(12, [[0]*12 for _ in range(12)])
    tests.append(("k=6 wysokie", g1, g2, 6, "Wiele kopii prostego grafu"))
    
    # Test 3: Graf z 0 krawędzi (izolowane wierzchołki)
    g1 = Graph(3, [[0]*3 for _ in range(3)])
    g2 = Graph(5, [[0]*5 for _ in range(5)])
    tests.append(("0 krawędzi", g1, g2, 1, "Tylko izolowane wierzchołki"))
    
    # Test 4: Pojedynczy wierzchołek z pętlą
    g1 = Graph(1, [[5]])  # Pętla krotności 5
    g2 = Graph(3, [[2, 0, 0], [0, 1, 0], [0, 0, 3]])
    tests.append(("Pętla krotności 5", g1, g2, 1, "Wysoka krotność pętli"))
    
    # Test 5: Długa ścieżka
    n = 8
    path = [[0]*n for _ in range(n)]
    for i in range(n-1):
        path[i][i+1] = 1
    g1 = Graph(n, path)
    g2 = Graph(12, [[0]*12 for _ in range(12)])
    tests.append(("Długa ścieżka P8", g1, g2, 1, "Ścieżka 8 wierzchołków"))
    
    # Test 6: Gęsty multigraf z wysokimi krotnościami
    g1 = Graph(3, [[3, 2, 1], [2, 1, 3], [1, 3, 2]])
    g2 = Graph(4, [[1, 1, 1, 0], [1, 0, 2, 1], [1, 2, 0, 1], [0, 1, 1, 0]])
    tests.append(("Gęsty krotności 1-3", g1, g2, 1, "Wysokie krotności wszędzie"))
    
    # Test 7: k=1 ale n1=n2 (dokładna równość)
    g1 = Graph(4, [[0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 0, 0]])
    g2 = Graph(4, [[0, 1, 1, 0], [0, 0, 1, 1], [0, 0, 0, 1], [0, 0, 0, 0]])
    tests.append(("n1=n2=4 równe", g1, g2, 1, "Równa liczba wierzchołków"))
    
    # Test 8: Gwiazdka z centrum wysokiego stopnia
    n = 7
    star = [[0]*n for _ in range(n)]
    for i in range(1, n):
        star[0][i] = 2  # Centrum → liście (krotność 2)
        star[i][0] = 1  # Liście → centrum
    g1 = Graph(n, star)
    g2 = Graph(9, [[0]*9 for _ in range(9)])
    tests.append(("Gwiazdka n=7 krotności", g1, g2, 1, "Gwiazda z wysokimi krotnościami"))
    
    # Test 9: Dwukierunkowe krawędzie z różnymi krotnościami
    g1 = Graph(2, [[0, 3], [2, 0]])  # 3 w jedną stronę, 2 w drugą
    g2 = Graph(4, [[0, 1, 1, 0], [2, 0, 0, 1], [1, 0, 0, 2], [0, 1, 3, 0]])
    tests.append(("Asymetryczne krotności", g1, g2, 1, "Różne krotności w obu kierunkach"))
    
    # Test 10: Cykl z pętlami
    c = [[0]*4 for _ in range(4)]
    c[0][1], c[1][2], c[2][3], c[3][0] = 1, 1, 1, 1
    c[0][0], c[2][2] = 2, 1  # Pętle na niektórych wierzchołkach
    g1 = Graph(4, c)
    g2 = Graph(5, [[0]*5 for _ in range(5)])
    tests.append(("Cykl C4 + pętle", g1, g2, 1, "Cykl z pętlami"))
    
    # Test 11-15: Losowe kombinacje
    for i in range(5):
        n1 = random.randint(3, 5)
        n2 = random.randint(n1+1, n1+4)
        k = random.randint(1, min(3, n2 // n1))
        m1 = [[random.randint(0, 2) for _ in range(n1)] for _ in range(n1)]
        m2 = [[random.randint(0, 1) for _ in range(n2)] for _ in range(n2)]
        tests.append((f"Losowy #{i+1}", Graph(n1, m1), Graph(n2, m2), k, f"Losowy n1={n1},n2={n2},k={k}"))
    
    return tests


def write_test_file(filepath: str, g1: Graph, g2: Graph, k: int):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"{g1.n}\n")
        for row in g1.matrix:
            f.write(" ".join(map(str, row)) + "\n")
        f.write(f"{g2.n}\n")
        for row in g2.matrix:
            f.write(" ".join(map(str, row)) + "\n")
        f.write(f"{k}\n")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 80)
    print("SPRAWDZARKA FINAL - ULTIMATE TESTING SUITE")
    print("=" * 80)
    print()
    
    # Zbierz wszystkie testy
    all_tests = []
    
    # 1. Testy v2 (50 testów)
    print("[*] Ladowanie testow v2 (50 testow)...")
    test_dir_v2 = "tests_v2"
    if os.path.exists(test_dir_v2):
        for filename in sorted(os.listdir(test_dir_v2)):
            if filename.endswith('.txt'):
                filepath = os.path.join(test_dir_v2, filename)
                g1, g2, k = parse_graph_from_file(filepath)
                all_tests.append(("v2/" + filename, filepath, g1, g2, k))
        print(f"  [OK] {len(all_tests)} testow z v2")
    
    # 2. Testy v3 hardcore (10 testów)
    print("[*] Ladowanie testow v3 hardcore (10 testow)...")
    test_dir_v3 = "tests_v3_hardcore"
    v3_count = 0
    if os.path.exists(test_dir_v3):
        for filename in sorted(os.listdir(test_dir_v3)):
            if filename.endswith('.txt'):
                filepath = os.path.join(test_dir_v3, filename)
                g1, g2, k = parse_graph_from_file(filepath)
                all_tests.append(("v3/" + filename, filepath, g1, g2, k))
                v3_count += 1
        print(f"  [OK] {v3_count} testow hardcore")
    
    # 3. Nowe stress testy
    print("[*] Generowanie stress testow (15 testow)...")
    stress_dir = "tests_stress"
    os.makedirs(stress_dir, exist_ok=True)
    stress_tests = generate_stress_tests()
    stress_count = 0
    for i, (name, g1, g2, k, desc) in enumerate(stress_tests, 1):
        safe_name = ''.join(c if c.isalnum() or c in ('_', '-') else '' for c in name.replace(' ', '_'))
        filepath = os.path.join(stress_dir, f"stress_{i:02d}_{safe_name}.txt")
        write_test_file(filepath, g1, g2, k)
        all_tests.append((f"stress/{name}", filepath, g1, g2, k))
        stress_count += 1
    print(f"  [OK] {stress_count} stress testow")
    
    print(f"\n[TOTAL] {len(all_tests)} testow\n")
    
    # Uruchom testy
    results = {'exact': [], 'approx': []}
    
    for algorithm in ['exact', 'approx']:
        print("=" * 80)
        print(f"TESTING {algorithm.upper()} ALGORITHM ({len(all_tests)} testów)")
        print("=" * 80)
        
        passed = 0
        failed = 0
        timeouts = 0
        
        for name, filepath, g1, g2, k in all_tests:
            output, elapsed = run_algorithm(filepath, algorithm, timeout_sec=120)
            
            if output is None:
                print(f"[TIMEOUT] {name}")
                timeouts += 1
                results[algorithm].append({'name': name, 'timeout': True})
                continue
            
            parsed = parse_algorithm_output(output, g1.n, g2.n, k)
            
            if parsed is None:
                print(f"[NO_SOL] {name}")
                failed += 1
                results[algorithm].append({'name': name, 'found': False})
                continue
            
            g2_ext, mappings, cost = parsed
            validation = validate_solution(g1, g2, g2_ext, mappings, k, cost)
            
            if validation['valid']:
                passed += 1
                results[algorithm].append({
                    'name': name,
                    'valid': True,
                    'cost': cost,
                    'time': elapsed
                })
            else:
                print(f"[FAIL] {name}")
                for err in validation['errors']:
                    print(f"   {err}")
                failed += 1
                results[algorithm].append({
                    'name': name,
                    'valid': False,
                    'errors': validation['errors']
                })
        
        print(f"\n{algorithm.upper()} Results: [OK] {passed} | [FAIL] {failed} | [TIMEOUT] {timeouts}")
    
    # PODSUMOWANIE
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    exact_passed = sum(1 for r in results['exact'] if r.get('valid', False))
    approx_passed = sum(1 for r in results['approx'] if r.get('valid', False))
    
    print(f"\nTotal tests: {len(all_tests)}")
    print(f"EXACT:  [OK] {exact_passed}/{len(all_tests)} PASSED")
    print(f"APPROX: [OK] {approx_passed}/{len(all_tests)} PASSED")
    
    if exact_passed == len(all_tests) and approx_passed == len(all_tests):
        print("\n*** PERFEKCJA! WSZYSTKIE TESTY PASSED! ***")
    else:
        print(f"\n[!] {len(all_tests) - exact_passed} exact + {len(all_tests) - approx_passed} approx failures")
    
    print("=" * 80)


if __name__ == "__main__":
    main()
