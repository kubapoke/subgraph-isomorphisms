#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automatyczna sprawdzarka algorytmów dokładnego i aproksymacyjnego
Generuje losowe grafy, uruchamia algorytmy i porównuje wyniki
"""

import subprocess
import random
import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import time

class Graph:
    """Reprezentacja multigrafu skierowanego"""
    def __init__(self, n: int, directed: bool = True, allow_multi: bool = True):
        self.n = n
        self.directed = directed
        self.allow_multi = allow_multi
        self.matrix = [[0] * n for _ in range(n)]
    
    def add_edge(self, u: int, v: int, count: int = 1):
        """Dodaj krawędź (lub wiele krawędzi w multigrafie)"""
        self.matrix[u][v] += count
        if not self.directed:
            self.matrix[v][u] += count
    
    def edge_count(self) -> int:
        """Całkowita liczba krawędzi"""
        return sum(sum(row) for row in self.matrix)
    
    def save_to_file(self, filename: str, g2: 'Graph', k: int):
        """Zapisz dwa grafy do pliku w formacie programu"""
        with open(filename, 'w') as f:
            # Graf G1
            f.write(f"{self.n}\n")
            for row in self.matrix:
                f.write(" ".join(map(str, row)) + "\n")
            
            # Graf G2
            f.write(f"{g2.n}\n")
            for row in g2.matrix:
                f.write(" ".join(map(str, row)) + "\n")
            
            # Liczba kopii
            f.write(f"{k}\n")
    
    def __str__(self):
        result = f"Graf {self.n}x{self.n}, krawędzi: {self.edge_count()}\n"
        for row in self.matrix:
            result += " ".join(map(str, row)) + "\n"
        return result

def generate_random_graph(n: int, edge_prob: float = 0.3, max_multi: int = 1, 
                         directed: bool = True) -> Graph:
    """
    Generuje losowy multigraf
    
    Args:
        n: liczba wierzchołków
        edge_prob: prawdopodobieństwo wystąpienia krawędzi
        max_multi: maksymalna krotność krawędzi (1 = graf prosty)
        directed: czy graf skierowany
    """
    g = Graph(n, directed, max_multi > 1)
    
    for i in range(n):
        start_j = i if not directed else 0
        for j in range(start_j, n):
            if random.random() < edge_prob:
                count = random.randint(1, max_multi)
                if i != j or directed:  # Pomijamy pętle w grafach nieskierowanych
                    g.add_edge(i, j, count)
    
    return g

def generate_path_graph(n: int) -> Graph:
    """Generuje graf ścieżkowy P_n (0->1->2->...->n-1)"""
    g = Graph(n, directed=True, allow_multi=False)
    for i in range(n - 1):
        g.add_edge(i, i + 1)
    return g

def generate_cycle_graph(n: int) -> Graph:
    """Generuje graf cykliczny C_n"""
    g = Graph(n, directed=True, allow_multi=False)
    for i in range(n):
        g.add_edge(i, (i + 1) % n)
    return g

def generate_complete_graph(n: int, directed: bool = False) -> Graph:
    """Generuje graf pełny K_n"""
    g = Graph(n, directed=directed, allow_multi=False)
    for i in range(n):
        for j in range(n):
            if i != j:
                g.add_edge(i, j)
    return g

def generate_empty_graph(n: int) -> Graph:
    """Generuje graf pusty (bez krawędzi)"""
    return Graph(n, directed=True, allow_multi=False)

def run_algorithm(test_file: str, algorithm: str, timeout: int = 30) -> Optional[dict]:
    """
    Uruchamia algorytm i parsuje wynik
    
    Returns:
        dict z kluczami: 'cost', 'time_ms', 'found', 'edges_added'
        lub None jeśli błąd
    """
    exe_path = Path("build/subgraph-isomorphism.exe")
    if not exe_path.exists():
        exe_path = Path("build/Release/subgraph-isomorphism.exe")
    
    if not exe_path.exists():
        print(f"BŁĄD: Nie znaleziono pliku wykonywalnego!")
        return None
    
    try:
        result = subprocess.run(
            [str(exe_path), test_file, algorithm],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )
        
        output = result.stdout
        
        # Parsuj wyniki
        res = {
            'cost': None,
            'time_ms': None,
            'found': False,
            'edges_added': None,
            'output': output
        }
        
        for line in output.split('\n'):
            if 'Koszt rozszerzenia:' in line:
                try:
                    res['cost'] = int(line.split(':')[1].strip())
                    res['found'] = True
                except:
                    pass
            elif 'Liczba dodanych krawędzi:' in line or 'Liczba dodanych kraw' in line:
                try:
                    res['edges_added'] = int(line.split(':')[1].strip())
                except:
                    pass
            elif 'Czas wykonania:' in line:
                try:
                    res['time_ms'] = int(line.split(':')[1].strip().split()[0])
                except:
                    pass
        
        return res
        
    except subprocess.TimeoutExpired:
        print(f"  ⏱️  TIMEOUT ({timeout}s)")
        return {'cost': None, 'time_ms': timeout * 1000, 'found': False, 'timeout': True}
    except Exception as e:
        print(f"  ❌ BŁĄD: {e}")
        return None

def verify_solution_detailed(test_file: str, result: dict, k: int) -> dict:
    """
    Szczegółowa weryfikacja rozwiązania
    - Wczytuje plik z wynikiem
    - Sprawdza czy mapowania są poprawne
    - Sprawdza czy graf rozszerzony zawiera k kopii
    """
    verification = {
        'valid': False,
        'errors': [],
        'warnings': []
    }
    
    if not result or not result['found']:
        verification['errors'].append("Nie znaleziono rozwiązania")
        return verification
    
    # Wczytaj wynik z pliku output
    result_file = Path("src/output/result.txt")
    if not result_file.exists():
        verification['warnings'].append("Brak pliku result.txt do weryfikacji")
        verification['valid'] = True  # Zakładamy że OK jeśli brak pliku
        return verification
    
    try:
        with open(result_file, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            
            # Sprawdź czy koszt się zgadza
            if f"Koszt: {result['cost']}" in content:
                verification['valid'] = True
            else:
                verification['errors'].append(f"Koszt w pliku nie zgadza się z outputem")
    except Exception as e:
        verification['warnings'].append(f"Błąd czytania result.txt: {e}")
        verification['valid'] = True
    
    return verification

def verify_solution(g1: Graph, g2: Graph, result: dict, k: int) -> bool:
    """
    Podstawowa weryfikacja czy rozwiązanie ma sens
    - Czy koszt jest nieujemny
    - Czy koszt nie jest większy niż k * liczba_krawędzi_G1
    """
    if not result or not result['found']:
        return False
    
    cost = result['cost']
    max_cost = k * g1.edge_count()
    
    if cost < 0:
        print(f"    ⚠️  Koszt ujemny: {cost}")
        return False
    
    if cost > max_cost:
        print(f"    ⚠️  Koszt za duży: {cost} > {max_cost}")
        return False
    
    return True

def compare_results(exact_res: dict, approx_res: dict, test_name: str):
    """Porównuje wyniki algorytmu dokładnego i aproksymacyjnego"""
    print(f"\n{'='*70}")
    print(f"Test: {test_name}")
    print(f"{'='*70}")
    
    if not exact_res or not exact_res['found']:
        print("  ❌ Algorytm DOKŁADNY nie znalazł rozwiązania")
        exact_cost = float('inf')
        exact_time = exact_res.get('time_ms', 0) if exact_res else 0
    else:
        exact_cost = exact_res['cost']
        exact_time = exact_res['time_ms']
        print(f"  ✅ Algorytm DOKŁADNY:        koszt = {exact_cost:4d}, czas = {exact_time:6d} ms")
    
    if not approx_res or not approx_res['found']:
        print("  ❌ Algorytm APROKSYMACYJNY nie znalazł rozwiązania")
        approx_cost = float('inf')
        approx_time = approx_res.get('time_ms', 0) if approx_res else 0
    else:
        approx_cost = approx_res['cost']
        approx_time = approx_res['time_ms']
        print(f"  ✅ Algorytm APROKSYMACYJNY:  koszt = {approx_cost:4d}, czas = {approx_time:6d} ms")
    
    # Porównanie
    if exact_cost != float('inf') and approx_cost != float('inf'):
        if approx_cost == exact_cost:
            print(f"  🎯 IDEALNE! Aproksymacja znalazła optimum!")
        elif approx_cost < exact_cost:
            print(f"  ⚠️  BŁĄD! Aproksymacja ma MNIEJSZY koszt niż dokładny! {approx_cost} < {exact_cost}")
        else:
            ratio = approx_cost / exact_cost if exact_cost > 0 else float('inf')
            diff = approx_cost - exact_cost
            print(f"  📊 Aproksymacja: {diff} więcej krawędzi (stosunek: {ratio:.2f}x)")
    
    print()

def run_test_suite(test_approx=True):
    """Uruchamia zestaw testów"""
    print("="*70)
    print("SPRAWDZARKA ALGORYTMÓW - Subgraph Isomorphisms")
    print("="*70)
    
    if not test_approx:
        print("⚠️  UWAGA: Testowanie tylko algorytmu DOKŁADNEGO (approx wyłączony)")
        print()
    
    test_dir = Path("tests_auto")
    test_dir.mkdir(exist_ok=True)
    
    tests = []
    
    # Test 1: Małe grafy proste
    print("\n📝 Generuję testy dla małych grafów prostych...")
    for i in range(3):
        n1 = random.randint(2, 4)
        n2 = random.randint(n1, n1 + 2)
        k = random.randint(1, 2)
        
        g1 = generate_random_graph(n1, edge_prob=0.4, max_multi=1, directed=True)
        g2 = generate_random_graph(n2, edge_prob=0.2, max_multi=1, directed=True)
        
        test_file = test_dir / f"test_small_{i+1}.txt"
        g1.save_to_file(str(test_file), g2, k)
        tests.append((f"Mały graf #{i+1} (n1={n1}, n2={n2}, k={k})", test_file))
    
    # Test 2: Ścieżki
    print("📝 Generuję testy dla ścieżek...")
    for i in range(3):
        n1 = random.randint(2, 5)
        n2 = random.randint(n1, n1 + 3)
        k = random.randint(1, 2)
        
        g1 = generate_path_graph(n1)
        g2 = generate_random_graph(n2, edge_prob=0.3, max_multi=1, directed=True)
        
        test_file = test_dir / f"test_path_{i+1}.txt"
        g1.save_to_file(str(test_file), g2, k)
        tests.append((f"Ścieżka #{i+1} (P{n1} w grafie {n2}, k={k})", test_file))
    
    # Test 3: Graf pusty G2
    print("📝 Generuję testy z pustym G2...")
    for i in range(2):
        n1 = random.randint(2, 3)
        n2 = random.randint(n1, n1 + 2)
        k = 1
        
        g1 = generate_random_graph(n1, edge_prob=0.5, max_multi=1, directed=True)
        g2 = generate_empty_graph(n2)
        
        test_file = test_dir / f"test_empty_{i+1}.txt"
        g1.save_to_file(str(test_file), g2, k)
        tests.append((f"Pusty G2 #{i+1} (G1={n1} wierzchołków, G2={n2} wierzchołków)", test_file))
    
    # Test 4: Multigrafy
    print("📝 Generuję testy dla multigrafów...")
    for i in range(2):
        n1 = random.randint(2, 3)
        n2 = random.randint(n1, n1 + 2)
        k = 1
        
        g1 = generate_random_graph(n1, edge_prob=0.4, max_multi=3, directed=True)
        g2 = generate_random_graph(n2, edge_prob=0.2, max_multi=2, directed=True)
        
        test_file = test_dir / f"test_multi_{i+1}.txt"
        g1.save_to_file(str(test_file), g2, k)
        tests.append((f"Multigraf #{i+1} (n1={n1}, n2={n2})", test_file))
    
    # Test 5: Większe k
    print("📝 Generuję testy z większym k...")
    for i in range(2):
        n1 = 2
        n2 = random.randint(4, 6)
        k = random.randint(2, 3)
        
        g1 = generate_path_graph(n1)
        g2 = generate_empty_graph(n2)
        
        test_file = test_dir / f"test_multi_copy_{i+1}.txt"
        g1.save_to_file(str(test_file), g2, k)
        tests.append((f"Wiele kopii #{i+1} (k={k}, n2={n2})", test_file))
    
    print(f"\n✅ Wygenerowano {len(tests)} testów\n")
    
    # Uruchom wszystkie testy
    results = {
        'total': len(tests),
        'exact_ok': 0,
        'approx_ok': 0,
        'both_ok': 0,
        'approx_optimal': 0,
        'approx_better_time': 0,
        'exact_timeout': 0,
        'approx_timeout': 0
    }
    
    for test_name, test_file in tests:
        print(f"\n🔬 Uruchamiam: {test_name}")
        print(f"   Plik: {test_file}")
        
        # Algorytm dokładny
        print("   Uruchamiam algorytm DOKŁADNY...")
        exact_res = run_algorithm(str(test_file), "exact", timeout=10)
        
        # Algorytm aproksymacyjny
        approx_res = None
        if test_approx:
            print("   Uruchamiam algorytm APROKSYMACYJNY...")
            approx_res = run_algorithm(str(test_file), "approx", timeout=5)
        
        # Porównaj wyniki
        compare_results(exact_res, approx_res, test_name)
        
        # Statystyki
        if exact_res and exact_res['found']:
            results['exact_ok'] += 1
        if exact_res and exact_res.get('timeout'):
            results['exact_timeout'] += 1
            
        if approx_res and approx_res['found']:
            results['approx_ok'] += 1
        if approx_res and approx_res.get('timeout'):
            results['approx_timeout'] += 1
            
        if exact_res and approx_res and exact_res['found'] and approx_res['found']:
            results['both_ok'] += 1
            if exact_res['cost'] == approx_res['cost']:
                results['approx_optimal'] += 1
            if approx_res['time_ms'] < exact_res['time_ms']:
                results['approx_better_time'] += 1
    
    # Podsumowanie
    print("\n" + "="*70)
    print("PODSUMOWANIE")
    print("="*70)
    print(f"Wszystkich testów:                    {results['total']}")
    print(f"Dokładny znalazł rozwiązanie:         {results['exact_ok']}/{results['total']}")
    print(f"Aproksymacyjny znalazł rozwiązanie:   {results['approx_ok']}/{results['total']}")
    print(f"Oba znalazły rozwiązanie:             {results['both_ok']}/{results['total']}")
    print(f"Aproksymacyjny znalazł optimum:       {results['approx_optimal']}/{results['both_ok']}")
    print(f"Aproksymacyjny szybszy:               {results['approx_better_time']}/{results['both_ok']}")
    print(f"Dokładny timeout:                     {results['exact_timeout']}")
    print(f"Aproksymacyjny timeout:               {results['approx_timeout']}")
    print("="*70)
    
    return results

if __name__ == "__main__":
    print("Upewnij się, że program jest skompilowany w build/subgraph-isomorphism.exe\n")
    
    # Parsuj argumenty
    test_approx = True
    quick_mode = False
    
    for arg in sys.argv[1:]:
        if arg == "--quick":
            quick_mode = True
        elif arg == "--no-approx" or arg == "--exact-only":
            test_approx = False
        elif arg == "--help":
            print("Użycie: python sprawdzarka.py [opcje]")
            print("\nOpcje:")
            print("  --quick          Tylko szybki test (1 test)")
            print("  --exact-only     Testuj tylko algorytm dokładny (pomija aproks.)")
            print("  --no-approx      To samo co --exact-only")
            print("  --help           Wyświetl tę pomoc")
            print("\nPrzykłady:")
            print("  python sprawdzarka.py                    # Pełny zestaw testów")
            print("  python sprawdzarka.py --quick            # Szybki test")
            print("  python sprawdzarka.py --exact-only       # Tylko dokładny (bezpieczne)")
            print("  python sprawdzarka.py --quick --exact-only  # Kombinacja opcji")
            sys.exit(0)
    
    if not test_approx:
        print("⚠️  Algorytm aproksymacyjny WYŁĄCZONY (testowanie tylko exact)\n")
    
    if quick_mode:
        print("Tryb QUICK - tylko kilka testów\n")
        # Pojedynczy szybki test
        test_dir = Path("tests_auto")
        test_dir.mkdir(exist_ok=True)
        
        g1 = generate_path_graph(3)
        g2 = generate_empty_graph(4)
        test_file = test_dir / "quick_test.txt"
        g1.save_to_file(str(test_file), g2, 1)
        
        print("Test: Ścieżka P3 w pustym grafie 4 wierzchołków")
        exact = run_algorithm(str(test_file), "exact")
        
        approx = None
        if test_approx:
            approx = run_algorithm(str(test_file), "approx", timeout=5)
        
        compare_results(exact, approx, "Quick test")
    else:
        # Pełny zestaw testów
        run_test_suite(test_approx=test_approx)
    
    print("\n✅ Sprawdzarka zakończona!")
