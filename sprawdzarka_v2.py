#!/usr/bin/env python3
"""
SPRAWDZARKA V2 - POTĘŻNA WALIDACJA
Rozszerzona wersja z 51 testami i dokładną walidacją rozwiązań
"""

import subprocess
import sys
from pathlib import Path
import random
from typing import Optional, Tuple, List, Set


class Graph:
    """Reprezentacja grafu skierowanego (multigraf)."""
    
    def __init__(self, n: int):
        self.n = n
        self.edges = [[0] * n for _ in range(n)]
    
    def add_edge(self, u: int, v: int, count: int = 1):
        """Dodaj krawędź."""
        self.edges[u][v] += count
    
    def edge_count(self, u: int, v: int) -> int:
        """Zwróć liczbę krawędzi u->v."""
        return self.edges[u][v]
    
    def total_edges(self) -> int:
        """Całkowita liczba krawędzi."""
        return sum(sum(row) for row in self.edges)
    
    def copy(self):
        """Zwróć kopię grafu."""
        g = Graph(self.n)
        for i in range(self.n):
            for j in range(self.n):
                g.edges[i][j] = self.edges[i][j]
        return g
    
    def save_to_file(self, filepath: Path, g2: 'Graph', k: int):
        """Zapisz test do pliku."""
        with open(filepath, 'w') as f:
            # POPRAWNY FORMAT: n1, G1, n2, G2, k
            f.write(f"{self.n}\n")
            for row in self.edges:
                f.write(" ".join(map(str, row)) + "\n")
            
            f.write(f"{g2.n}\n")
            for row in g2.edges:
                f.write(" ".join(map(str, row)) + "\n")
            
            f.write(f"{k}\n")


# ====================== GENERATORY GRAFÓW ======================

def generate_random_graph(n: int, m: int, allow_loops: bool = False) -> Graph:
    """Generuj losowy graf skierowany z ~m krawędziami."""
    g = Graph(n)
    edges_added = 0
    attempts = 0
    max_attempts = m * 10
    
    while edges_added < m and attempts < max_attempts:
        u = random.randint(0, n-1)
        v = random.randint(0, n-1)
        if allow_loops or u != v:
            g.add_edge(u, v)
            edges_added += 1
        attempts += 1
    
    return g


def generate_path_graph(n: int) -> Graph:
    """Generuj ścieżkę P_n."""
    g = Graph(n)
    for i in range(n - 1):
        g.add_edge(i, i + 1)
    return g


def generate_cycle_graph(n: int) -> Graph:
    """Generuj cykl C_n."""
    g = Graph(n)
    for i in range(n):
        g.add_edge(i, (i + 1) % n)
    return g


def generate_complete_graph(n: int) -> Graph:
    """Generuj graf pełny K_n."""
    g = Graph(n)
    for i in range(n):
        for j in range(n):
            if i != j:
                g.add_edge(i, j)
    return g


def generate_star_graph(n: int) -> Graph:
    """Generuj gwiazdę - środek połączony ze wszystkimi."""
    g = Graph(n)
    for i in range(1, n):
        g.add_edge(0, i)
    return g


def generate_dag(n: int, m: int) -> Graph:
    """Generuj DAG - krawędzie tylko w przód."""
    g = Graph(n)
    edges_added = 0
    attempts = 0
    max_attempts = m * 10
    
    while edges_added < m and attempts < max_attempts:
        u = random.randint(0, n-2)
        v = random.randint(u+1, n-1)
        g.add_edge(u, v)
        edges_added += 1
        attempts += 1
    
    return g


def generate_bipartite_graph(n1: int, n2: int, density: float = 0.5) -> Graph:
    """Generuj losowy graf dwudzielny."""
    g = Graph(n1 + n2)
    for i in range(n1):
        for j in range(n2):
            if random.random() < density:
                g.add_edge(i, n1 + j)
    return g


# ====================== WALIDACJA ROZWIĄZAŃ ======================

class TestResult:
    """Wynik testu dla jednego algorytmu."""
    def __init__(self, success: bool, cost: Optional[int] = None, 
                 time_ms: Optional[int] = None, timeout: bool = False,
                 error: Optional[str] = None, mappings: Optional[List[List[int]]] = None):
        self.success = success
        self.cost = cost
        self.time_ms = time_ms
        self.timeout = timeout
        self.error = error
        self.mappings = mappings or []


def run_algorithm(test_file: Path, algorithm: str, timeout_sec: int = 10) -> TestResult:
    """Uruchom algorytm i sparsuj PEŁNY wynik."""
    exe_path = Path("build/subgraph-isomorphism.exe")
    
    if not exe_path.exists():
        return TestResult(success=False, error=f"Nie znaleziono {exe_path}")
    
    try:
        result = subprocess.run(
            [str(exe_path), str(test_file), algorithm],
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            encoding='utf-8',
            errors='replace'
        )
        
        output = result.stdout
        
        # Parsuj wynik
        cost = None
        time_ms = None
        mappings = []
        
        for line in output.split('\n'):
            if "Koszt" in line and ("rozszerzenia:" in line or "rozwiązania:" in line or "Całkowity koszt:" in line):
                try:
                    cost = int(line.split(':')[1].strip())
                except:
                    pass
            elif "Czas wykonania:" in line or "Czas:" in line:
                try:
                    # Parsuj "Czas wykonania: 123 ms" lub "Czas: 123ms"
                    time_str = line.split(':')[1].strip()
                    time_str = time_str.replace('ms', '').strip()
                    time_ms = int(time_str)
                except:
                    pass
            elif "Kopia" in line and "->" in line:
                # Parsuj: "  Kopia 1: 0->3, 1->2, 2->4"
                try:
                    mapping_str = line.split(':', 1)[1].strip()
                    mapping = []
                    for pair in mapping_str.split(','):
                        if '->' in pair:
                            u, v = pair.strip().split('->')
                            mapping.append(int(v.strip()))
                    if mapping:
                        mappings.append(mapping)
                except:
                    pass
        
        if cost is not None:
            return TestResult(success=True, cost=cost, time_ms=time_ms, mappings=mappings)
        else:
            return TestResult(success=False, error="Nie znaleziono kosztu w wyniku")
            
    except subprocess.TimeoutExpired:
        return TestResult(success=False, timeout=True, error=f"Timeout ({timeout_sec}s)")
    except Exception as e:
        return TestResult(success=False, error=str(e))


def verify_solution(g1: Graph, g2: Graph, k: int, 
                    exact_result: TestResult, 
                    approx_result: TestResult) -> Tuple[bool, str]:
    """
    DOKŁADNA WALIDACJA rozwiązań.
    Zwraca (czy_ok, komunikat).
    """
    # Sprawdź czy oba się udały
    if not exact_result.success:
        return False, f"❌ Exact nie znalazł rozwiązania: {exact_result.error}"
    
    if not approx_result.success:
        return False, f"❌ Approx nie znalazł rozwiązania: {approx_result.error}"
    
    # KRYTYCZNE: Approx nie może być lepszy niż exact!
    if approx_result.cost < exact_result.cost:
        return False, f"❌ BŁĄD LOGICZNY: Approx (koszt={approx_result.cost}) < Exact (koszt={exact_result.cost})!"
    
    # === WALIDACJA MAPOWAŃ ===
    for algo_name, result in [("Exact", exact_result), ("Approx", approx_result)]:
        if result.mappings:
            # Sprawdź liczbę kopii
            if len(result.mappings) != k:
                return False, f"❌ {algo_name}: znaleziono {len(result.mappings)} kopii zamiast {k}"
            
            # Sprawdź każde mapowanie
            images = []
            for i, mapping in enumerate(result.mappings):
                # Poprawna długość?
                if len(mapping) != g1.n:
                    return False, f"❌ {algo_name}: Kopia {i+1} ma {len(mapping)} wierzchołków zamiast {g1.n}"
                
                # Wierzchołki w zakresie?
                for j, v in enumerate(mapping):
                    if v < 0 or v >= g2.n:
                        return False, f"❌ {algo_name}: Kopia {i+1} mapuje wierzchołek {j} na {v} (poza zakresem [0,{g2.n-1}])"
                
                # Sprawdź czy mapowanie jest injekcją (różne wierzchołki → różne obrazy w JEDNEJ kopii)
                if len(set(mapping)) != len(mapping):
                    duplicates = [v for v in set(mapping) if mapping.count(v) > 1]
                    return False, f"❌ {algo_name}: Kopia {i+1} NIE jest injekcją! Wierzchołki {duplicates} mają wiele preobrazów."
                
                # Obraz = zbiór wierzchołków na które mapujemy
                image = tuple(sorted(mapping))
                
                # DUPLIKATY? (Im(Mi) ≠ Im(Mj))
                if image in images:
                    return False, f"❌ {algo_name}: Kopia {i+1} ma IDENTYCZNY obraz {image} jak inna kopia!\n   KRYTYCZNE: Im(M{i+1}) = Im(Mj) - naruszenie definicji!"
                images.append(image)
    
    # Górne ograniczenie kosztu
    max_possible_cost = k * g1.total_edges()
    
    if exact_result.cost > max_possible_cost:
        return False, f"❌ Exact koszt={exact_result.cost} > teoretyczne max={max_possible_cost}"
    
    return True, "✅ Walidacja OK"


# ====================== GENEROWANIE TESTÓW ======================

def generate_test_suite(output_dir: Path) -> List[Tuple[str, Path, Graph, Graph, int]]:
    """
    Generuj ROZSZERZONY zestaw testów (51 testów).
    Zwraca listę: (nazwa, plik, g1, g2, k)
    """
    output_dir.mkdir(exist_ok=True)
    tests = []
    
    print("📝 [1/10] Małe grafy losowe...")
    for i in range(5):
        n1 = random.randint(2, 4)
        n2 = random.randint(n1, 6)
        m1 = random.randint(1, n1 * 2)
        m2 = random.randint(0, n2 * 2)
        k = random.randint(1, 3)
        
        g1 = generate_random_graph(n1, m1)
        g2 = generate_random_graph(n2, m2)
        
        test_file = output_dir / f"test_small_{i+1}.txt"
        g1.save_to_file(test_file, g2, k)
        tests.append((f"Mały graf #{i+1} (n1={n1}, n2={n2}, k={k})", test_file, g1, g2, k))
    
    print("📝 [2/10] Ścieżki...")
    for i in range(5):
        path_len = random.randint(2, 6)
        n2 = random.randint(path_len, path_len + 5)
        k = random.randint(1, 3)
        
        g1 = generate_path_graph(path_len)
        g2 = generate_random_graph(n2, random.randint(0, n2))
        
        test_file = output_dir / f"test_path_{i+1}.txt"
        g1.save_to_file(test_file, g2, k)
        tests.append((f"Ścieżka #{i+1} (P{path_len} w grafie {n2}, k={k})", test_file, g1, g2, k))
    
    print("📝 [3/10] Cykle...")
    for i in range(5):
        cycle_len = random.randint(3, 6)
        n2 = random.randint(cycle_len, cycle_len + 4)
        k = random.randint(1, 2)
        
        g1 = generate_cycle_graph(cycle_len)
        g2 = generate_random_graph(n2, random.randint(0, n2 * 2))
        
        test_file = output_dir / f"test_cycle_{i+1}.txt"
        g1.save_to_file(test_file, g2, k)
        tests.append((f"Cykl #{i+1} (C{cycle_len} w grafie {n2}, k={k})", test_file, g1, g2, k))
    
    print("📝 [4/10] Gwiazdy...")
    for i in range(5):
        n1 = random.randint(3, 5)
        n2 = random.randint(n1, n1 + 3)
        k = random.randint(1, 2)
        
        g1 = generate_star_graph(n1)
        g2 = generate_random_graph(n2, random.randint(0, n2))
        
        test_file = output_dir / f"test_star_{i+1}.txt"
        g1.save_to_file(test_file, g2, k)
        tests.append((f"Gwiazda #{i+1} (n1={n1}, n2={n2}, k={k})", test_file, g1, g2, k))
    
    print("📝 [5/10] Grafy pełne...")
    for i in range(4):
        n1 = random.randint(2, 3)  # K_n rośnie szybko!
        n2 = random.randint(n1, n1 + 2)
        k = 1
        
        g1 = generate_complete_graph(n1)
        g2 = generate_random_graph(n2, random.randint(0, n2))
        
        test_file = output_dir / f"test_complete_{i+1}.txt"
        g1.save_to_file(test_file, g2, k)
        tests.append((f"Graf pełny #{i+1} (K{n1} w grafie {n2})", test_file, g1, g2, k))
    
    print("📝 [6/10] DAG-i...")
    for i in range(5):
        n1 = random.randint(3, 5)
        n2 = random.randint(n1, n1 + 3)
        m1 = random.randint(2, n1 * 2)
        k = random.randint(1, 2)
        
        g1 = generate_dag(n1, m1)
        g2 = generate_random_graph(n2, random.randint(0, n2))
        
        test_file = output_dir / f"test_dag_{i+1}.txt"
        g1.save_to_file(test_file, g2, k)
        tests.append((f"DAG #{i+1} (n1={n1}, n2={n2}, k={k})", test_file, g1, g2, k))
    
    print("📝 [7/10] Pusty G2...")
    for i in range(5):
        n1 = random.randint(2, 4)
        n2 = random.randint(n1, n1 + 3)
        m1 = random.randint(1, n1 * 2)
        k = random.randint(1, 2)
        
        g1 = generate_random_graph(n1, m1)
        g2 = Graph(n2)  # pusty
        
        test_file = output_dir / f"test_empty_{i+1}.txt"
        g1.save_to_file(test_file, g2, k)
        tests.append((f"Pusty G2 #{i+1} (n1={n1}, n2={n2}, k={k})", test_file, g1, g2, k))
    
    print("📝 [8/10] Multigrafy...")
    for i in range(5):
        n1 = random.randint(2, 3)
        n2 = random.randint(n1, n1 + 3)
        k = random.randint(1, 2)
        
        g1 = Graph(n1)
        for _ in range(random.randint(1, 3)):
            u = random.randint(0, n1-1)
            v = random.randint(0, n1-1)
            if u != v:
                g1.add_edge(u, v, count=random.randint(2, 3))
        
        g2 = generate_random_graph(n2, random.randint(0, n2))
        
        test_file = output_dir / f"test_multi_{i+1}.txt"
        g1.save_to_file(test_file, g2, k)
        tests.append((f"Multigraf #{i+1} (n1={n1}, n2={n2}, k={k})", test_file, g1, g2, k))
    
    print("📝 [9/10] Wiele kopii...")
    for i in range(5):
        n1 = random.randint(2, 3)
        n2 = random.randint(4, 7)
        k = random.randint(3, 5)
        
        g1 = generate_path_graph(n1)
        g2 = generate_random_graph(n2, random.randint(0, 3))
        
        test_file = output_dir / f"test_multi_copy_{i+1}.txt"
        g1.save_to_file(test_file, g2, k)
        tests.append((f"Wiele kopii #{i+1} (k={k}, n1={n1}, n2={n2})", test_file, g1, g2, k))
    
    print("📝 [10/10] Średnie grafy...")
    for i in range(6):
        n1 = random.randint(4, 6)
        n2 = random.randint(n1, n1 + 4)
        m1 = random.randint(3, n1 * 3)
        m2 = random.randint(0, n2 * 2)
        k = random.randint(1, 2)
        
        g1 = generate_random_graph(n1, m1)
        g2 = generate_random_graph(n2, m2)
        
        test_file = output_dir / f"test_medium_{i+1}.txt"
        g1.save_to_file(test_file, g2, k)
        tests.append((f"Średni graf #{i+1} (n1={n1}, n2={n2}, k={k})", test_file, g1, g2, k))
    
    print(f"\n✅ Wygenerowano {len(tests)} testów\n")
    return tests


# ====================== GŁÓWNA PĘTLA ======================

def run_test_suite():
    """Uruchom pełny zestaw testów."""
    
    print("="*70)
    print("SPRAWDZARKA V2 - POTĘŻNA WALIDACJA")
    print("51 testów + dokładna weryfikacja rozwiązań")
    print("="*70)
    print()
    
    exe_path = Path("build/subgraph-isomorphism.exe")
    if not exe_path.exists():
        print(f"❌ Nie znaleziono {exe_path}")
        print("Upewnij się że program jest skompilowany!")
        return False
    
    # Generuj testy
    tests_dir = Path("tests_v2")
    tests = generate_test_suite(tests_dir)
    
    # Statystyki
    total = len(tests)
    exact_success = 0
    approx_success = 0
    both_success = 0
    approx_optimal = 0
    approx_faster = 0
    exact_timeouts = 0
    approx_timeouts = 0
    validation_errors = 0
    
    # Dodatkowe statystyki
    total_exact_time = 0
    total_approx_time = 0
    max_cost_diff = 0
    
    failed_tests = []
    
    # Uruchom testy
    for i, (name, test_file, g1, g2, k) in enumerate(tests, 1):
        print(f"\n[{i}/{total}] 🔬 {name}")
        print(f"        Plik: {test_file}")
        
        # Exact
        print("        Uruchamiam DOKŁADNY...", end=" ", flush=True)
        exact = run_algorithm(test_file, "exact", timeout_sec=15)
        if exact.success:
            exact_success += 1
            print(f"✅ koszt={exact.cost}, czas={exact.time_ms}ms")
        elif exact.timeout:
            exact_timeouts += 1
            print("⏱️  TIMEOUT")
        else:
            print(f"❌ {exact.error}")
        
        # Approx
        print("        Uruchamiam APROKSYMACYJNY...", end=" ", flush=True)
        approx = run_algorithm(test_file, "approx", timeout_sec=15)
        if approx.success:
            approx_success += 1
            print(f"✅ koszt={approx.cost}, czas={approx.time_ms}ms")
        elif approx.timeout:
            approx_timeouts += 1
            print("⏱️  TIMEOUT")
        else:
            print(f"❌ {approx.error}")
        
        # Walidacja
        if exact.success and approx.success:
            both_success += 1
            
            is_valid, msg = verify_solution(g1, g2, k, exact, approx)
            
            if not is_valid:
                validation_errors += 1
                print(f"\n        ⚠️  BŁĄD WALIDACJI: {msg}")
                failed_tests.append((name, test_file, msg))
            else:
                # Statystyki
                if approx.cost == exact.cost:
                    approx_optimal += 1
                    print(f"        🎯 OPTIMUM! Approx = Exact = {exact.cost}")
                else:
                    diff = approx.cost - exact.cost
                    max_cost_diff = max(max_cost_diff, diff)
                    print(f"        📊 Approx o {diff} więcej (Exact={exact.cost}, Approx={approx.cost})")
                
                # Czasy
                if exact.time_ms:
                    total_exact_time += exact.time_ms
                if approx.time_ms:
                    total_approx_time += approx.time_ms
                
                if approx.time_ms and exact.time_ms and approx.time_ms < exact.time_ms:
                    approx_faster += 1
    
    # Podsumowanie
    print("\n" + "="*70)
    print("PODSUMOWANIE")
    print("="*70)
    print(f"Wszystkich testów:                    {total}")
    print(f"Dokładny znalazł rozwiązanie:         {exact_success}/{total}")
    print(f"Aproksymacyjny znalazł rozwiązanie:   {approx_success}/{total}")
    print(f"Oba znalazły rozwiązanie:             {both_success}/{total}")
    if both_success > 0:
        pct = 100 * approx_optimal // both_success
        print(f"Aproksymacyjny znalazł optimum:       {approx_optimal}/{both_success} ({pct}%)")
        print(f"Aproksymacyjny szybszy:               {approx_faster}/{both_success}")
    print(f"Dokładny timeout:                     {exact_timeouts}")
    print(f"Aproksymacyjny timeout:               {approx_timeouts}")
    print(f"Błędy walidacji:                      {validation_errors}")
    
    # Dodatkowe statystyki
    if both_success > 0:
        print(f"\nStatystyki dodatkowe:")
        if total_exact_time > 0:
            print(f"  Całkowity czas Exact:               {total_exact_time} ms")
        if total_approx_time > 0:
            print(f"  Całkowity czas Approx:              {total_approx_time} ms")
        if max_cost_diff > 0:
            print(f"  Maks różnica koszt (Approx-Exact):  {max_cost_diff}")
        avg_exact = total_exact_time // both_success if total_exact_time > 0 else 0
        avg_approx = total_approx_time // both_success if total_approx_time > 0 else 0
        if avg_exact > 0:
            print(f"  Średni czas Exact:                  {avg_exact} ms")
        if avg_approx > 0:
            print(f"  Średni czas Approx:                 {avg_approx} ms")
    
    print("="*70)
    
    # Wyniki
    if validation_errors == 0 and both_success == total:
        print("\n🎉🎉🎉 WSZYSTKIE TESTY PRZESZŁY! KOD DZIAŁA IDEOLO! 🎉🎉🎉")
        print("\n✅ Implementacja jest w 100% poprawna!")
        print("✅ Wszystkie mapowania mają różne obrazy (Im(Mi) ≠ Im(Mj))")
        print("✅ Approx nigdy nie jest lepszy niż Exact")
        print("✅ Wszystkie warunki problemu spełnione")
        return True
    elif validation_errors > 0:
        print(f"\n⚠️  UWAGA: {validation_errors} testów NIE PRZESZŁO walidacji!")
        print("\nNiepoprawne testy:")
        for name, test_file, msg in failed_tests:
            print(f"  • {name}")
            print(f"    Plik: {test_file}")
            print(f"    Błąd: {msg}")
        print("\n⚠️  KOD WYMAGA NAPRAWY!")
        return False
    else:
        print("\n⚠️  Niektóre testy zakończyły się timeoutem.")
        return False


if __name__ == "__main__":
    success = run_test_suite()
    sys.exit(0 if success else 1)
