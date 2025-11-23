import subprocess
import os
import re
import time
import math
import random
from typing import List, Tuple, Dict, Optional, Set

# ============================================================================
# KLASY I WALIDACJA (Z giga_sprawdzarka.py)
# ============================================================================

class Graph:
    def __init__(self, n: int, matrix: List[List[int]] = None):
        self.n = n
        self.matrix = matrix if matrix else [[0]*n for _ in range(n)]
        
    def edge_count(self, u: int, v: int) -> int:
        return self.matrix[u][v]

class Mapping:
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

def verify_isomorphic_embedding(g1: Graph, g2: Graph, mapping: Mapping) -> Tuple[bool, str]:
    if not mapping.is_complete(): return False, "Mapowanie niepełne"
    if not mapping.is_injection(): return False, "Mapowanie nie jest iniekcją"
    for u in range(g1.n):
        for v in range(g1.n):
            if g1.edge_count(u, v) > g2.edge_count(mapping.get(u), mapping.get(v)):
                return False, f"E1({u},{v}) > E2"
    return True, "OK"

def verify_k_copies(g1: Graph, g2: Graph, mappings: List[Mapping], k: int) -> Tuple[bool, str]:
    if len(mappings) != k: return False, f"Liczba mapowań {len(mappings)} != k"
    for i, m in enumerate(mappings):
        ok, msg = verify_isomorphic_embedding(g1, g2, m)
        if not ok: return False, f"M{i}: {msg}"
    
    # Sprawdzenie unikalności obrazów (Definicja 5)
    images = [tuple(sorted(list(m.image()))) for m in mappings]
    if len(set(images)) != k:
        return False, "Obrazy mapowań nie są unikalne!"
    return True, "OK"

def compute_extension_cost(g2_orig: Graph, g2_ext: Graph) -> int:
    cost = 0
    for u in range(g2_orig.n):
        for v in range(g2_orig.n):
            diff = g2_ext.edge_count(u, v) - g2_orig.edge_count(u, v)
            if diff < 0: raise ValueError(f"E'2 < E2 w ({u},{v})")
            cost += diff
    return cost

# ============================================================================
# GENEROWANIE I PARSOWANIE
# ============================================================================

def generate_random_test_file(filename, n1, n2, k, density=0.3):
    with open(filename, 'w') as f:
        f.write(f"{n1}\n")
        for _ in range(n1):
            row = [random.randint(1, 10) if random.random() < density else 0 for _ in range(n1)]
            f.write(" ".join(map(str, row)) + "\n")
        
        f.write(f"{n2}\n")
        for _ in range(n2):
            row = [random.randint(1, 10) if random.random() < density else 0 for _ in range(n2)]
            f.write(" ".join(map(str, row)) + "\n")
            
        f.write(f"{k}\n")

def parse_output(output: str, n1: int, n2: int, k: int):
    lines = output.split('\n')
    cost = None
    for line in lines:
        if 'Koszt rozszerzenia:' in line:
            match = re.search(r':\s*(\d+)', line)
            if match: cost = int(match.group(1))
            
    if cost is None: return None

    mappings = [Mapping(n1) for _ in range(k)]
    g2_ext = None
    
    # Parsowanie mapowań
    in_mappings = False
    for line in lines:
        if 'Mapowania:' in line: in_mappings = True; continue
        if in_mappings and 'Rozszerzony graf' in line: break
        if in_mappings:
            m = re.match(r'\s*Kopia\s+(\d+):\s*(.+)', line)
            if m:
                idx = int(m.group(1)) - 1
                pairs = re.findall(r'(\d+)->(\d+)', m.group(2))
                for u, v in pairs:
                    if idx < k: mappings[idx].set(int(u), int(v))

    # Parsowanie macierzy
    matrix_lines = []
    in_matrix = False
    for line in lines:
        if 'Rozszerzony graf' in line: in_matrix = True; continue
        if in_matrix:
            nums = re.findall(r'\d+', line)
            if len(nums) == n2: matrix_lines.append(list(map(int, nums)))
    
    if len(matrix_lines) == n2:
        g2_ext = Graph(n2, matrix_lines)
        
    return g2_ext, mappings, cost

# ============================================================================
# MAIN
# ============================================================================

def main():
    exe = r".\build\subgraph-isomorphism.exe"
    test_file = "temp_scale_test.txt"
    
    scenarios = [
        (10, 20, 2),
        (15, 30, 3),
        (20, 50, 5),
        (30, 100, 5),
        (40, 150, 5),
        (50, 200, 10) # To już jest spore
    ]
    
    print("="*80)
    print("TEST SKALOWALNOŚCI ALGORYTMU APPROX")
    print("="*80)
    print(f"{'SCENARIUSZ':<25} | {'CZAS':<10} | {'KOSZT':<10} | {'WYNIK'}")
    print("-" * 80)
    
    for n1, n2, k in scenarios:
        generate_random_test_file(test_file, n1, n2, k, density=0.2)
        
        # Wczytaj oryginalny G2 do weryfikacji kosztu
        with open(test_file, 'r') as f:
            lines = f.readlines()
            # Pomijamy n1 i macierz G1
            idx = 1 + n1
            # n2
            idx += 1
            # Macierz G2
            g2_matrix = []
            for i in range(n2):
                g2_matrix.append(list(map(int, lines[idx+i].split())))
            g2_orig = Graph(n2, g2_matrix)
            
            # G1 do weryfikacji izomorfizmu
            g1_matrix = []
            for i in range(n1):
                g1_matrix.append(list(map(int, lines[1+i].split())))
            g1 = Graph(n1, g1_matrix)

        start = time.time()
        try:
            result = subprocess.run(
                [exe, test_file, "approx"],
                capture_output=True, text=True, timeout=60
            )
            elapsed = time.time() - start
            
            parsed = parse_output(result.stdout, n1, n2, k)
            
            if parsed:
                g2_ext, mappings, reported_cost = parsed
                
                # WERYFIKACJA
                errors = []
                
                # 1. Definicja 5 (k kopii, unikalne obrazy, izomorfizm)
                ok_k, msg_k = verify_k_copies(g1, g2_ext, mappings, k)
                if not ok_k: errors.append(msg_k)
                
                # 2. Definicja 7 (Koszt)
                try:
                    real_cost = compute_extension_cost(g2_orig, g2_ext)
                    if real_cost != reported_cost:
                        errors.append(f"Koszt {reported_cost} != {real_cost}")
                except ValueError as e:
                    errors.append(str(e))
                
                status = "✅ OK" if not errors else f"❌ {errors[0]}"
                print(f"n1={n1}, n2={n2}, k={k:<4} | {elapsed*1000:.0f}ms     | {reported_cost:<10} | {status}")
                
            else:
                if "Nie znaleziono rozwiązania" in result.stdout:
                     print(f"n1={n1}, n2={n2}, k={k:<4} | {elapsed*1000:.0f}ms     | {'-':<10} | ❓ NO_SOLUTION (Możliwe)")
                else:
                     print(f"n1={n1}, n2={n2}, k={k:<4} | {elapsed*1000:.0f}ms     | {'?':<10} | ❌ PARSE ERROR")
                
        except subprocess.TimeoutExpired:
            print(f"n1={n1}, n2={n2}, k={k:<4} | >60000ms   | {'-':<10} | ⏱️ TIMEOUT")
            
    if os.path.exists(test_file):
        os.remove(test_file)

if __name__ == "__main__":
    main()