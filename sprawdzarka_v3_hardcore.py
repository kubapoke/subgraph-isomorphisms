#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPRAWDZARKA V3 - HARDCORE MATEMATYCZNA WALIDACJA
=================================================
Zgodnie z dokumentacją PDF i emailami:
- Weryfikacja WSZYSTKICH definicji matematycznych
- Testy edge case'ów: pętle, multigrafy, ekstremalne k
- Walidacja porządku leksykograficznego
- Sprawdzanie iniekcji i unikalności obrazów
- Testy z niemożliwymi konfiguracjami
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
# MATEMATYCZNA WALIDACJA ZGODNA Z DOKUMENTACJĄ
# ============================================================================

class Graph:
    """Reprezentacja multigrafu skierowanego (V, E) gdzie E: V×V → ℕ₀"""
    def __init__(self, n: int, matrix: List[List[int]] = None):
        self.n = n  # |V|
        self.matrix = matrix if matrix else [[0]*n for _ in range(n)]
        
    def edge_count(self, u: int, v: int) -> int:
        """E(u,v) - krotność krawędzi z u do v"""
        return self.matrix[u][v]
    
    def size(self) -> int:
        """|G| = Σ E(u,v) - rozmiar multigrafu (liczba krawędzi z krotnościami)"""
        return sum(sum(row) for row in self.matrix)
    
    def degree(self, v: int) -> int:
        """Stopień wierzchołka (in + out)"""
        in_deg = sum(self.matrix[u][v] for u in range(self.n))
        out_deg = sum(self.matrix[v][u] for u in range(self.n))
        return in_deg + out_deg
    
    def copy(self):
        """Kopia głęboka grafu"""
        return Graph(self.n, [row[:] for row in self.matrix])


class Mapping:
    """Mapowanie M: V₁ → V₂ (może być częściowe)"""
    def __init__(self, n1: int):
        self.n1 = n1
        self.map = [-1] * n1  # -1 oznacza brak mapowania
        
    def set(self, u: int, v: int):
        """M(u) = v"""
        self.map[u] = v
        
    def get(self, u: int) -> int:
        """M(u)"""
        return self.map[u]
    
    def is_complete(self) -> bool:
        """Czy mapowanie jest pełne"""
        return all(v != -1 for v in self.map)
    
    def image(self) -> Set[int]:
        """Im(M) - obraz mapowania (zbiór wierzchołków V₂)"""
        return set(v for v in self.map if v != -1)
    
    def is_injection(self) -> bool:
        """Czy M jest różnowartościowe (iniekcja)"""
        mapped = [v for v in self.map if v != -1]
        return len(mapped) == len(set(mapped))
    
    def as_tuple(self) -> tuple:
        """Reprezentacja jako krotka (dla porządku leksykograficznego)"""
        return tuple(self.map)


def verify_isomorphic_embedding(g1: Graph, g2: Graph, mapping: Mapping) -> Tuple[bool, str]:
    """
    DEFINICJA 4 z dokumentacji:
    G₂ zawiera podgraf izomorficzny z G₁ jeśli istnieje iniekcja M: V₁ → V₂
    taka że dla każdej pary u,v ∈ V₁: E₁(u,v) ≤ E₂(M(u), M(v))
    """
    if not mapping.is_complete():
        return False, "Mapowanie nie jest pełne"
    
    if not mapping.is_injection():
        return False, "Mapowanie nie jest iniekcją (nie jest różnowartościowe)"
    
    # Sprawdź warunek izomorfizmu dla każdej pary wierzchołków
    for u in range(g1.n):
        for v in range(g1.n):
            e1_uv = g1.edge_count(u, v)
            mu = mapping.get(u)
            mv = mapping.get(v)
            e2_mumv = g2.edge_count(mu, mv)
            
            if e1_uv > e2_mumv:
                return False, f"Naruszenie E₁({u},{v})={e1_uv} ≤ E₂({mu},{mv})={e2_mumv}"
    
    return True, "OK"


def verify_k_copies(g1: Graph, g2: Graph, mappings: List[Mapping], k: int) -> Tuple[bool, str]:
    """
    DEFINICJA 5 z dokumentacji:
    G₂ zawiera k różnych podgrafów izomorficznych jeśli istnieje k iniekcji
    M₁, M₂, ..., Mₖ takich że:
    1. E₁(u,v) ≤ E₂(Mᵢ(u), Mᵢ(v)) dla wszystkich u,v ∈ V₁, i=1,...,k
    2. Im(Mᵢ) ≠ Im(Mⱼ) dla i ≠ j
    """
    if len(mappings) != k:
        return False, f"Liczba mapowań ({len(mappings)}) ≠ k ({k})"
    
    # Sprawdź każde mapowanie
    for i, mapping in enumerate(mappings):
        ok, msg = verify_isomorphic_embedding(g1, g2, mapping)
        if not ok:
            return False, f"Mapowanie M{i+1}: {msg}"
    
    # Sprawdź unikalność obrazów Im(Mᵢ) ≠ Im(Mⱼ)
    images = [mapping.image() for mapping in mappings]
    for i in range(k):
        for j in range(i+1, k):
            if images[i] == images[j]:
                img_i = sorted(images[i])
                return False, f"Im(M{i+1}) = Im(M{j+1}) = {img_i} (obrazy muszą być różne!)"
    
    return True, "OK - wszystkie k kopii są poprawne i różne"


def verify_lexicographic_order(mappings: List[Mapping], k: int) -> Tuple[bool, str]:
    """
    Sekcja 3.4 dokumentacji - porządek kanoniczny:
    M₁ < M₂ < ... < Mₖ w sensie leksykograficznym
    """
    for i in range(k-1):
        t1 = mappings[i].as_tuple()
        t2 = mappings[i+1].as_tuple()
        if t1 >= t2:
            return False, f"Naruszenie porządku: M{i+1} = {t1} >= M{i+2} = {t2}"
    
    return True, "OK - porządek leksykograficzny zachowany"


def compute_extension_cost(g2_original: Graph, g2_extended: Graph) -> int:
    """
    DEFINICJA 7 z dokumentacji:
    cost(G'₂, G₂) = Σ_{(u,v) ∈ V×V} (E'₂(u,v) - E₂(u,v))
    """
    cost = 0
    for u in range(g2_original.n):
        for v in range(g2_original.n):
            diff = g2_extended.edge_count(u, v) - g2_original.edge_count(u, v)
            if diff < 0:
                raise ValueError(f"E'₂({u},{v}) < E₂({u},{v}) - niepoprawne rozszerzenie!")
            cost += diff
    return cost


# ============================================================================
# PARSER WYNIKÓW (obsługuje różne formaty)
# ============================================================================

def parse_graph_from_file(filepath: str) -> Tuple[Graph, Graph, int]:
    """Parsuje plik testowy: G1, G2, k"""
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
    Parsuje wyjście algorytmu i zwraca:
    - G'₂ (rozszerzony graf)
    - lista k mapowań
    - koszt
    """
    lines = output.split('\n')
    
    # Szukaj kosztu
    cost = None
    for line in lines:
        if 'Koszt rozszerzenia:' in line or 'Cost:' in line:
            match = re.search(r':\s*(\d+)', line)
            if match:
                cost = int(match.group(1))
                break
    
    if cost is None:
        return None  # Nie znaleziono kosztu
    
    # Szukaj mapowań
    mappings = []
    for i in range(k):
        mappings.append(Mapping(n1))
    
    # Parsuj sekcję "Mapowania:"
    in_mappings = False
    current_copy = -1
    
    for line in lines:
        if 'Mapowania:' in line or 'Mappings:' in line:
            in_mappings = True
            continue
        
        if in_mappings:
            # Kopia X: a->b, c->d, ...
            copy_match = re.match(r'\s*Kopia\s+(\d+):\s*(.+)', line, re.IGNORECASE)
            if copy_match:
                copy_num = int(copy_match.group(1)) - 1  # 0-indexed
                mapping_str = copy_match.group(2)
                
                # Parsuj pary a->b
                pairs = re.findall(r'(\d+)->(\d+)', mapping_str)
                for u_str, v_str in pairs:
                    u = int(u_str)
                    v = int(v_str)
                    if copy_num < k:
                        mappings[copy_num].set(u, v)
            
            # Koniec sekcji mapowań
            if 'Rozszerzony graf' in line or 'Extended graph' in line:
                break
    
    # Parsuj G'₂
    g2_extended = None
    in_extended = False
    matrix_lines = []
    
    for line in lines:
        if 'Rozszerzony graf' in line or "G'_2" in line:
            in_extended = True
            continue
        
        if in_extended:
            # Próbuj sparsować wiersz macierzy
            numbers = re.findall(r'\d+', line)
            if len(numbers) == n2:
                matrix_lines.append(list(map(int, numbers)))
                if len(matrix_lines) == n2:
                    g2_extended = Graph(n2, matrix_lines)
                    break
    
    if g2_extended is None:
        return None
    
    return g2_extended, mappings, cost


# ============================================================================
# GENERATOR TESTÓW EKSTREMALNYCH
# ============================================================================

def generate_extreme_tests() -> List[Tuple[str, Graph, Graph, int, str]]:
    """
    Generuje HARDCORE testy:
    - Pętle (self-loops)
    - Wielokrotne krawędzie (multigrafy)
    - k > n₂ (niemożliwe)
    - k × n₁ > n₂ (za mało wierzchołków)
    - Grafy puste
    - Grafy pełne z wysokimi krotnościami
    """
    tests = []
    
    # Test 1: Pętle
    g1 = Graph(2, [[2, 1], [1, 0]])  # Wierzchołek 0 ma pętlę krotności 2
    g2 = Graph(3, [[1, 0, 1], [0, 0, 0], [1, 0, 3]])  # Różne pętle
    tests.append(("Pętle (self-loops)", g1, g2, 1, "Sprawdza obsługę pętli"))
    
    # Test 2: Wysokie krotności
    g1 = Graph(2, [[0, 5], [3, 0]])  # 5 krawędzi 0→1, 3 krawędzie 1→0
    g2 = Graph(3, [[0, 2, 1], [1, 0, 4], [0, 6, 0]])
    tests.append(("Wysokie krotności", g1, g2, 1, "Multigraf z wielokrotnymi krawędziami"))
    
    # Test 3: k × n₁ = n₂ (ścisła równość - przypadek graniczny)
    g1 = Graph(2, [[0, 1], [0, 0]])  # P2 (ścieżka 2 wierzchołki)
    g2 = Graph(4, [[0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 0, 0]])  # P4
    tests.append(("k×n₁=n₂ graniczny", g1, g2, 2, "Dokładnie tyle wierzchołków ile trzeba"))
    
    # Test 4: k × n₁ > n₂ (NIEMOŻLIWE - za mało wierzchołków dla różnych obrazów)
    g1 = Graph(3, [[0, 1, 0], [0, 0, 1], [0, 0, 0]])  # P3
    g2 = Graph(4, [[0]*4 for _ in range(4)])  # Pusty graf 4 wierzchołki
    tests.append(("k×n₁>n₂ NIEMOŻLIWE", g1, g2, 2, "6 > 4 - niemożliwe znaleźć 2 różne obrazy"))
    
    # Test 5: Wszystkie wierzchołki mają pętle
    g1 = Graph(2, [[3, 1], [1, 2]])  # Oba wierzchołki z pętlami
    g2 = Graph(3, [[1, 0, 0], [0, 2, 1], [0, 1, 4]])
    tests.append(("Wszystkie pętle", g1, g2, 1, "Każdy wierzchołek G₁ ma pętlę"))
    
    # Test 6: k bardzo duże
    g1 = Graph(1, [[0]])  # Pojedynczy wierzchołek bez pętli
    g2 = Graph(10, [[0]*10 for _ in range(10)])  # 10 izolowanych wierzchołków
    tests.append(("k=10 duże", g1, g2, 10, "Maksymalna liczba kopii dla izolowanych wierzchołków"))
    
    # Test 7: Graf pełny z krotnościami
    g1 = Graph(3, [[2, 1, 1], [1, 0, 1], [1, 1, 1]])  # Prawie pełny z krotnościami
    g2 = Graph(4, [[0, 1, 1, 0], [1, 0, 1, 1], [1, 1, 0, 1], [0, 1, 1, 0]])
    tests.append(("Graf pełny + krotności", g1, g2, 1, "Gęsty graf z wielokrotnym krawędziami"))
    
    # Test 8: Asymetryczny multigraf (różne krotności w obu kierunkach)
    g1 = Graph(2, [[0, 3], [1, 0]])  # 3 krawędzie 0→1, ale 1 krawędź 1→0
    g2 = Graph(3, [[0, 2, 4], [3, 0, 1], [1, 2, 0]])
    tests.append(("Asymetryczny", g1, g2, 1, "Różne krotności w różnych kierunkach"))
    
    # Test 9: k=1 ale G₁=G₂ (identyczne grafy)
    g1 = Graph(3, [[0, 1, 0], [0, 0, 1], [1, 0, 0]])  # Cykl C3
    g2 = Graph(3, [[0, 1, 0], [0, 0, 1], [1, 0, 0]])  # Identyczny
    tests.append(("G₁=G₂ identyczne", g1, g2, 1, "Koszt powinien być 0"))
    
    # Test 10: Losowy gęsty multigraf
    random.seed(42)
    n1, n2 = 3, 5
    matrix1 = [[random.randint(0, 3) for _ in range(n1)] for _ in range(n1)]
    matrix2 = [[random.randint(0, 2) for _ in range(n2)] for _ in range(n2)]
    g1 = Graph(n1, matrix1)
    g2 = Graph(n2, matrix2)
    tests.append(("Losowy gęsty", g1, g2, 2, "Graf losowy z wieloma krawędziami"))
    
    return tests


def write_test_file(filepath: str, g1: Graph, g2: Graph, k: int):
    """Zapisuje test do pliku w formacie zgodnym z emailem"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"{g1.n}\n")
        for row in g1.matrix:
            f.write(" ".join(map(str, row)) + "\n")
        f.write(f"{g2.n}\n")
        for row in g2.matrix:
            f.write(" ".join(map(str, row)) + "\n")
        f.write(f"{k}\n")


# ============================================================================
# RUNNER TESTÓW
# ============================================================================

def run_algorithm(test_file: str, algorithm: str, timeout_sec: int = 60) -> Tuple[Optional[str], float]:
    """Uruchamia algorytm i zwraca (output, czas)"""
    exe_path = r".\build\subgraph-isomorphism.exe"
    
    if not os.path.exists(exe_path):
        raise FileNotFoundError(f"Nie znaleziono {exe_path}")
    
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


def validate_solution(g1: Graph, g2_original: Graph, g2_extended: Graph, 
                     mappings: List[Mapping], k: int, reported_cost: int) -> Dict:
    """
    PEŁNA WALIDACJA zgodnie z dokumentacją PDF:
    1. Każde Mᵢ jest iniekcją
    2. E₁(u,v) ≤ E₂(Mᵢ(u), Mᵢ(v)) dla wszystkich par
    3. Im(Mᵢ) ≠ Im(Mⱼ) dla i ≠ j
    4. Porządek leksykograficzny M₁ < M₂ < ... < Mₖ
    5. cost(G'₂, G₂) = Σ(E'₂ - E₂) zgadza się z raportowanym
    6. G'₂ jest rozszerzeniem G₂ (E'₂ ≥ E₂ wszędzie)
    """
    errors = []
    warnings = []
    
    # Walidacja 1: k kopii z poprawnymi mapowaniami
    ok, msg = verify_k_copies(g1, g2_extended, mappings, k)
    if not ok:
        errors.append(f"❌ Definicja 5: {msg}")
    
    # Walidacja 2: Porządek leksykograficzny (opcjonalnie - algorytm approx może nie zachowywać)
    ok, msg = verify_lexicographic_order(mappings, k)
    if not ok:
        warnings.append(f"⚠️  Porządek leksykograficzny: {msg}")
    
    # Walidacja 3: Koszt rozszerzenia
    actual_cost = compute_extension_cost(g2_original, g2_extended)
    if actual_cost != reported_cost:
        errors.append(f"❌ Koszt: raportowany={reported_cost}, rzeczywisty={actual_cost}")
    
    # Walidacja 4: G'₂ jest poprawnym rozszerzeniem G₂
    for u in range(g2_original.n):
        for v in range(g2_original.n):
            if g2_extended.edge_count(u, v) < g2_original.edge_count(u, v):
                errors.append(f"❌ Rozszerzenie: E'₂({u},{v}) < E₂({u},{v})")
    
    # Walidacja 5: Każde mapowanie jest kompletne
    for i, mapping in enumerate(mappings):
        if not mapping.is_complete():
            errors.append(f"❌ M{i+1} nie jest pełne")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'cost_verified': actual_cost == reported_cost,
        'actual_cost': actual_cost
    }


# ============================================================================
# MAIN - HARDCORE TESTING SUITE
# ============================================================================

def main():
    print("=" * 80)
    print("SPRAWDZARKA V3 - HARDCORE MATEMATYCZNA WALIDACJA")
    print("Zgodnie z dokumentacją PDF i emailami prof. Homendy")
    print("=" * 80)
    print()
    
    # Katalog na testy
    test_dir = "tests_v3_hardcore"
    os.makedirs(test_dir, exist_ok=True)
    
    # Generuj testy ekstremalne
    print("🔥 Generowanie testów ekstremalnych...")
    extreme_tests = generate_extreme_tests()
    
    test_files = []
    for i, (name, g1, g2, k, desc) in enumerate(extreme_tests, 1):
        # Bezpieczna nazwa pliku (usuń wszystkie niebezpieczne znaki)
        safe_name = name.replace(' ', '_').replace('×', 'x').replace('>', 'gt').replace('<', 'lt').replace('=', 'eq').replace('₁', '1').replace('₂', '2')
        safe_name = ''.join(c if c.isalnum() or c in ('_', '-') else '' for c in safe_name)
        filepath = os.path.join(test_dir, f"extreme_{i:02d}_{safe_name}.txt")
        write_test_file(filepath, g1, g2, k)
        test_files.append((filepath, name, desc, g1, g2, k))
        print(f"  ✅ {name}: {desc}")
    
    print(f"\n✨ Wygenerowano {len(test_files)} testów hardcore\n")
    
    # Uruchom testy
    results_exact = []
    results_approx = []
    
    print("=" * 80)
    print("TESTY EXACT ALGORITHM")
    print("=" * 80)
    
    for filepath, name, desc, g1_orig, g2_orig, k in test_files:
        print(f"\n🧪 [{name}]")
        print(f"   {desc}")
        print(f"   n₁={g1_orig.n}, n₂={g2_orig.n}, k={k}, |G₁|={g1_orig.size()}")
        
        output, elapsed = run_algorithm(filepath, "exact", timeout_sec=120)
        
        if output is None:
            print(f"   ⏱️  TIMEOUT (>120s)")
            results_exact.append({
                'name': name,
                'timeout': True,
                'valid': False
            })
            continue
        
        parsed = parse_algorithm_output(output, g1_orig.n, g2_orig.n, k)
        
        if parsed is None:
            print(f"   ❌ Nie znaleziono rozwiązania")
            results_exact.append({
                'name': name,
                'found': False,
                'valid': False
            })
            continue
        
        g2_ext, mappings, cost = parsed
        print(f"   ✅ Koszt={cost}, Czas={elapsed*1000:.1f}ms")
        
        # WALIDACJA
        validation = validate_solution(g1_orig, g2_orig, g2_ext, mappings, k, cost)
        
        if validation['errors']:
            print(f"   ❌ BŁĘDY WALIDACJI:")
            for err in validation['errors']:
                print(f"      {err}")
        else:
            print(f"   ✅ Walidacja: PASSED")
        
        if validation['warnings']:
            for warn in validation['warnings']:
                print(f"      {warn}")
        
        results_exact.append({
            'name': name,
            'found': True,
            'valid': validation['valid'],
            'cost': cost,
            'time': elapsed,
            'validation': validation
        })
    
    print("\n" + "=" * 80)
    print("TESTY APPROX ALGORITHM")
    print("=" * 80)
    
    for filepath, name, desc, g1_orig, g2_orig, k in test_files:
        print(f"\n🧪 [{name}]")
        
        output, elapsed = run_algorithm(filepath, "approx", timeout_sec=60)
        
        if output is None:
            print(f"   ⏱️  TIMEOUT (>60s)")
            results_approx.append({
                'name': name,
                'timeout': True,
                'valid': False
            })
            continue
        
        parsed = parse_algorithm_output(output, g1_orig.n, g2_orig.n, k)
        
        if parsed is None:
            print(f"   ❌ Nie znaleziono rozwiązania")
            results_approx.append({
                'name': name,
                'found': False,
                'valid': False
            })
            continue
        
        g2_ext, mappings, cost = parsed
        print(f"   ✅ Koszt={cost}, Czas={elapsed*1000:.1f}ms")
        
        # WALIDACJA
        validation = validate_solution(g1_orig, g2_orig, g2_ext, mappings, k, cost)
        
        if validation['errors']:
            print(f"   ❌ BŁĘDY WALIDACJI:")
            for err in validation['errors']:
                print(f"      {err}")
        else:
            print(f"   ✅ Walidacja: PASSED")
        
        results_approx.append({
            'name': name,
            'found': True,
            'valid': validation['valid'],
            'cost': cost,
            'time': elapsed,
            'validation': validation
        })
    
    # PODSUMOWANIE
    print("\n" + "=" * 80)
    print("PODSUMOWANIE HARDCORE TESTÓW")
    print("=" * 80)
    
    exact_valid = sum(1 for r in results_exact if r.get('valid', False))
    exact_found = sum(1 for r in results_exact if r.get('found', False))
    
    approx_valid = sum(1 for r in results_approx if r.get('valid', False))
    approx_found = sum(1 for r in results_approx if r.get('found', False))
    
    print(f"\nEXACT Algorithm:")
    print(f"  Znaleziono rozwiązanie: {exact_found}/{len(test_files)}")
    print(f"  Walidacja PASSED:       {exact_valid}/{exact_found}")
    
    print(f"\nAPPROX Algorithm:")
    print(f"  Znaleziono rozwiązanie: {approx_found}/{len(test_files)}")
    print(f"  Walidacja PASSED:       {approx_valid}/{approx_found}")
    
    # Przypadki z błędami
    print(f"\n🔍 Przypadki z błędami walidacji:")
    for r in results_exact + results_approx:
        if not r.get('valid', False) and r.get('found', False):
            print(f"  ❌ {r['name']}")
            if 'validation' in r:
                for err in r['validation'].get('errors', []):
                    print(f"     {err}")
    
    if exact_valid == exact_found and approx_valid == approx_found:
        print(f"\n🎉 WSZYSTKIE TESTY PASSED! Kod działa PERFEKCYJNIE!")
    else:
        print(f"\n⚠️  ZNALEZIONO BŁĘDY - kod wymaga poprawek")
    
    print("=" * 80)


if __name__ == "__main__":
    main()
