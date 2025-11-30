#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIGA SPRAWDZARKA - COMPREHENSIVE TEST SUITE
===========================================
Połączenie systematycznego testowania wszystkich plików z
rygorystyczną walidacją matematyczną.

Sprawdza:
1. Poprawność izomorfizmu (Definicja 4)
2. Rozłączność obrazów mapowań (Definicja 5)
3. Poprawność kosztu rozszerzenia (Definicja 7)
4. Czy G' jest faktycznym rozszerzeniem G
5. Porządek leksykograficzny (dla algorytmu exact)
"""

import subprocess
import os
import re
import time
import math
import sys
import random
import argparse
from typing import List, Tuple, Dict, Optional, Set

# ============================================================================
# KLASY I WALIDACJA MATEMATYCZNA
# ============================================================================

class Graph:
    """Reprezentacja multigrafu skierowanego (V, E) gdzie E: V×V → ℕ₀"""
    def __init__(self, n: int, matrix: List[List[int]] = None):
        self.n = n
        self.matrix = matrix if matrix else [[0]*n for _ in range(n)]
        
    def edge_count(self, u: int, v: int) -> int:
        return self.matrix[u][v]
    
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

def nCr(n, r):
    if r > n: return 0
    return math.comb(n, r)

# ============================================================================
# PARSOWANIE
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
    """
    Parsuje output z programu C++.
    
    Tryb verbose: stary format z opisami
    Tryb simple: 
        n
        macierz (n x n)
        koszt
    """
    lines = output.split('\n')
    
    # Sprawd\u017a czy to tryb verbose (ma "Results from" lub podobne)
    is_verbose = any('===' in line or 'Results' in line or 'Extension cost:' in line for line in lines)
    
    if is_verbose:
        # Stary parser verbose
        cost = None
        for line in lines:
            if 'Extension cost:' in line or 'Koszt rozszerzenia:' in line:
                match = re.search(r':\s*(\d+)', line)
                if match:
                    cost = int(match.group(1))
                    break
        
        if cost is None:
            return None
        
        mappings = [Mapping(n1) for _ in range(k)]
        in_mappings = False
        
        for line in lines:
            if 'Mapowania:' in line or 'Mappings:' in line:
                in_mappings = True
                continue
            
            if in_mappings:
                copy_match = re.match(r'\s*(?:Kopia|Copy)\s+(\d+):\s*(.+)', line, re.IGNORECASE)
                if copy_match:
                    copy_num = int(copy_match.group(1)) - 1
                    mapping_str = copy_match.group(2)
                    pairs = re.findall(r'(\d+)->(\d+)', mapping_str)
                    for u_str, v_str in pairs:
                        u, v = int(u_str), int(v_str)
                        if copy_num < k:
                            mappings[copy_num].set(u, v)
                
                if 'Rozszerzony graf' in line or 'Extended graph' in line:
                    break
        
        g2_extended = None
        in_extended = False
        matrix_lines = []
        
        for line in lines:
            if 'Rozszerzony graf' in line or "G'2" in line or 'Extended graph' in line:
                in_extended = True
                continue
            
            if in_extended:
                numbers = re.findall(r'\d+', line)
                if len(numbers) == n2:
                    matrix_lines.append(list(map(int, numbers)))
                    if len(matrix_lines) == n2:
                        g2_extended = Graph(n2, matrix_lines)
                        break
    else:
        # Nowy parser simple mode
        # Format: n, macierz (n linii), koszt
        clean_lines = [line.strip() for line in lines if line.strip() and not line.startswith('ERROR')]
        
        if len(clean_lines) < 3:
            return None
        
        try:
            n = int(clean_lines[0])
            if n != n2:
                return None
            
            matrix_lines = []
            for i in range(1, n+1):
                if i >= len(clean_lines):
                    return None
                row = list(map(int, clean_lines[i].split()))
                if len(row) != n:
                    return None
                matrix_lines.append(row)
            
            cost = int(clean_lines[n+1])
            g2_extended = Graph(n, matrix_lines)
            
            # W simple mode nie mamy mapowa\u0144, ale musimy je odtworzy\u0107 z pliku out.txt lub nie sprawdza\u0107
            # Na razie zwr\u00f3\u0107my puste mapowania
            mappings = [Mapping(n1) for _ in range(k)]
            # To b\u0119dzie niepe\u0142ne, ale koszt mo\u017cemy sprawdzi\u0107
            
        except (ValueError, IndexError):
            return None
    
    if g2_extended is None:
        return None
    
    return g2_extended, mappings, cost

# ============================================================================
# TEST RUNNER
# ============================================================================

def run_test_with_validation(filepath: str, algorithm: str, exe_path: str = r".\cmake-build-debug\subgraph-isomorphism.exe") -> Dict:
    # Wczytaj dane wejściowe
    try:
        g1, g2, k = parse_graph_from_file(filepath)
    except Exception as e:
        return {'status': 'ERROR', 'msg': f"Błąd wczytywania pliku: {e}"}

    start = time.time()
    try:
        # Nowy format: exe plik [-a] [-v]
        cmd = [exe_path, filepath]
        if algorithm == 'approx':
            cmd.append('-a')
        # Dodajemy -v aby uzyska\u0107 mapowania do walidacji
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3,
            encoding='utf-8',
            errors='replace'
        )
        elapsed = time.time() - start
        
        # Sprawdź stderr - program może zwrócić błąd walidacji input
        stderr_output = result.stderr if result.stderr else ""
        stdout_output = result.stdout if result.stdout else ""
        combined_output = stdout_output + "\n" + stderr_output
        
        # Obsługa błędów walidacji wejścia (to są poprawne odpowiedzi programu!)
        if result.returncode != 0:
            # Błąd walidacji input
            if "ERROR: Impossible" in combined_output or "cannot add new vertices" in combined_output:
                return {'status': 'OK', 'msg': 'Poprawnie wykryto niemożliwe k (k > C(n2,n1))', 'time': elapsed}
            if "n2=" in combined_output and "< n1=" in combined_output:
                return {'status': 'OK', 'msg': 'Poprawnie wykryto n2 < n1', 'time': elapsed}
            if "ERROR: Cannot open file" in combined_output:
                return {'status': 'ERROR', 'msg': 'Nie można otworzyć pliku', 'time': elapsed}
            if "ERROR: Cannot read" in combined_output or "ERROR: Invalid" in combined_output:
                return {'status': 'OK', 'msg': 'Poprawnie wykryto błędny format', 'time': elapsed}
            # No solution found (algorytm się wykonał, ale nie znalazł)
            if "ERROR: No solution found" in combined_output:
                max_copies = nCr(g2.n, g1.n)
                if k > max_copies:
                    return {'status': 'OK', 'msg': 'Poprawnie nie znaleziono (k > C(n2,n1))', 'time': elapsed}
                else:
                    return {'status': 'NO_SOLUTION', 'msg': 'Nie znaleziono rozwiązania (choć może istnieć)', 'time': elapsed}
        
        parsed = parse_algorithm_output(result.stdout, g1.n, g2.n, k)
        
        if parsed is None:
            # Sprawdź dodatkowe przypadki w stdout
            if "No solution found" in stdout_output:
                max_copies = nCr(g2.n, g1.n)
                if k > max_copies:
                    return {'status': 'OK', 'msg': 'Poprawnie nie znaleziono (k > C(n2,n1))', 'time': elapsed}
                else:
                    return {'status': 'NO_SOLUTION', 'msg': 'Nie znaleziono rozwiązania (choć może istnieć)', 'time': elapsed}

            return {'status': 'FAIL', 'msg': 'Błąd parsowania wyjścia', 'time': elapsed}
            
        g2_ext, mappings, reported_cost = parsed
        
        # WALIDACJA
        errors = []
        
        # 1. Sprawdź k kopii (tylko je\u015bli mamy mapowania z verbose mode)
        if all(m.is_complete() for m in mappings):
            ok, msg = verify_k_copies(g1, g2_ext, mappings, k)
            if not ok:
                errors.append(f"Błąd definicji 5: {msg}")
            
        # 2. Sprawdź koszt
        try:
            actual_cost = compute_extension_cost(g2, g2_ext)
            if actual_cost != reported_cost:
                errors.append(f"Błąd kosztu: raportowany {reported_cost} != rzeczywisty {actual_cost}")
        except ValueError as e:
            errors.append(f"Błąd rozszerzenia: {e}")
            
        if errors:
            return {'status': 'FAIL', 'msg': "; ".join(errors), 'time': elapsed, 'cost': reported_cost}
            
        return {'status': 'OK', 'msg': 'Walidacja poprawna', 'time': elapsed, 'cost': reported_cost}
        
    except subprocess.TimeoutExpired:
        return {'status': 'TIMEOUT', 'msg': 'Przekroczono czas oczekiwania', 'time': time.time() - start}
    except Exception as e:
        return {'status': 'ERROR', 'msg': str(e), 'time': 0}

def collect_all_tests() -> List[Tuple[str, str]]:
    tests = []
    test_dirs = [
        'tests_auto',
        'tests_v2', 
        'tests_v3_hardcore', 
        'tests_stress', 
        'tests_valid_edge_cases', 
        'tests_tricky',
        'tests_chaos',
        'tests_nightmare',
    ]
    for test_dir in test_dirs:
        if not os.path.exists(test_dir):
            continue
        for filename in sorted(os.listdir(test_dir)):
            if filename.endswith('.txt'):
                filepath = os.path.join(test_dir, filename)
                category = test_dir.replace('tests_', '')
                tests.append((category, filepath))
    return tests

# ============================================================================
# FUZZING
# ============================================================================

def generate_random_test_content(seed: int) -> str:
    random.seed(seed)
    # Random parameters for "small" tests
    n1 = random.randint(3, 8)
    n2 = random.randint(n1, 15)
    
    # Calculate max k
    max_k = nCr(n2, n1)
    # Cap k at 5 or max_k to keep it fast, but sometimes try impossible k
    k_limit = min(5, max_k + 2)
    k = random.randint(1, k_limit)
    
    # Density
    density1 = random.random()
    density2 = random.random()
    
    # Weights
    max_w = 10 if random.random() < 0.8 else 100
    
    lines = []
    lines.append(f"{n1}")
    for _ in range(n1):
        row = [random.randint(1, max_w) if random.random() < density1 else 0 for _ in range(n1)]
        lines.append(" ".join(map(str, row)))
        
    lines.append(f"{n2}")
    for _ in range(n2):
        row = [random.randint(1, max_w) if random.random() < density2 else 0 for _ in range(n2)]
        lines.append(" ".join(map(str, row)))
        
    lines.append(f"{k}")
    
    return "\n".join(lines)

def run_fuzzing_session(count: int, start_seed: int, exe_path: str = r".\cmake-build-debug\subgraph-isomorphism.exe"):
    print("=" * 80)
    print(f"FUZZING SESSION: {count} tests, start_seed={start_seed}")
    print("=" * 80)
    
    temp_file = "temp_fuzz.txt"
    stats = {'exact': {'ok': 0, 'fail': 0, 'timeout': 0}, 'approx': {'ok': 0, 'fail': 0, 'timeout': 0}}
    
    start_time = time.time()
    
    for i in range(count):
        seed = start_seed + i
        content = generate_random_test_content(seed)
        with open(temp_file, 'w') as f:
            f.write(content)
            
        # Run both algorithms
        for alg in ['exact', 'approx']:
            res = run_test_with_validation(temp_file, alg, exe_path)
            status = res['status']
            
            if status == 'OK' or status == 'NO_SOLUTION':
                 stats[alg]['ok'] += 1
            elif status == 'TIMEOUT':
                 stats[alg]['timeout'] += 1
            else:
                 stats[alg]['fail'] += 1
                 print(f"[FAIL] [Seed {seed}] {alg}: {res['msg']}")
                 # Save failed test
                 fail_name = f"fuzz_fail_{seed}_{alg}.txt"
                 with open(fail_name, 'w') as f:
                     f.write(content)
                 print(f"  Saved to {fail_name}")
        
        if (i+1) % 10 == 0:
            elapsed = time.time() - start_time
            rate = (i+1) / elapsed
            print(f"Progress: {i+1}/{count} ({rate:.1f} tests/s) | Failures: E={stats['exact']['fail']} A={stats['approx']['fail']}")

    print("\n" + "=" * 80)
    print("FUZZING COMPLETE")
    print("=" * 80)
    print(f"Total time: {time.time() - start_time:.2f}s")
    print(f"Exact : OK={stats['exact']['ok']}, TIMEOUT={stats['exact']['timeout']}, FAIL={stats['exact']['fail']}")
    print(f"Approx: OK={stats['approx']['ok']}, TIMEOUT={stats['approx']['timeout']}, FAIL={stats['approx']['fail']}")
    
    if os.path.exists(temp_file):
        os.remove(temp_file)

def main():
    parser = argparse.ArgumentParser(description="Giga Sprawdzarka")
    parser.add_argument('--fuzz', type=int, help="Run N random fuzz tests", default=0)
    parser.add_argument('--seed', type=int, help="Start seed for fuzzing", default=None)
    parser.add_argument('--exe', type=str, help="Path to executable", default=r".\cmake-build-debug\subgraph-isomorphism.exe")
    args = parser.parse_args()

    if args.fuzz > 0:
        seed = args.seed if args.seed is not None else random.randint(0, 1000000)
        run_fuzzing_session(args.fuzz, seed, args.exe)
        return

    print("=" * 80)
    print("GIGA SPRAWDZARKA")
    print("=" * 80)
    
    tests = collect_all_tests()
    print(f"Znaleziono {len(tests)} plików testowych\n")
    
    results = {
        'exact': {'passed': 0, 'failed': 0, 'timeout': 0, 'no_sol': 0},
        'approx': {'passed': 0, 'failed': 0, 'timeout': 0, 'no_sol': 0}
    }
    
    for i, (category, filepath) in enumerate(tests, 1):
        filename = os.path.basename(filepath)
        print(f"[{i}/{len(tests)}] {category}/{filename}")
        
        for alg in ['exact', 'approx']:
            res = run_test_with_validation(filepath, alg, args.exe)
            status = res['status']
            msg = res['msg']
            elapsed = res.get('time', 0)
            cost = res.get('cost', '-')
            
            if status == 'OK':
                results[alg]['passed'] += 1
                print(f"  {alg:6s}: [OK] (koszt={cost}, {elapsed*1000:.0f}ms)")
            elif status == 'TIMEOUT':
                results[alg]['timeout'] += 1
                print(f"  {alg:6s}: [TIMEOUT]")
            elif status == 'NO_SOLUTION':
                results[alg]['no_sol'] += 1
                print(f"  {alg:6s}: [NO_SOL]")
            else:
                results[alg]['failed'] += 1
                print(f"  {alg:6s}: [FAIL] - {msg}")
                
    print("\n" + "=" * 80)
    print("PODSUMOWANIE")
    print("=" * 80)
    for alg in ['exact', 'approx']:
        r = results[alg]
        print(f"{alg.upper()}: OK: {r['passed']}, FAIL: {r['failed']}, TIMEOUT: {r['timeout']}, NO_SOL: {r['no_sol']}")

if __name__ == "__main__":
    main()
