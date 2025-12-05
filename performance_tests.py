#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PERFORMANCE TESTING SUITE
==========================
Przeprowadza systematyczne testy wydajnościowe dla algorytmów exact i approximate.
Zbiera dane o czasie wykonania, koszcie, i parametrach wejściowych (n1, n2, k).
"""

import subprocess
import os
import re
import time
import json
import random
import argparse
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class TestResult:
    """Wynik pojedynczego testu"""
    n1: int
    n2: int
    k: int
    algorithm: str  # 'exact' or 'approx'
    time_ms: float
    cost: Optional[int]
    found: bool
    test_file: str
    error: Optional[str] = None

def parse_execution_time(output: str) -> Optional[float]:
    """Parsuje czas wykonania z outputu programu (TIME_MS: 123.45)"""
    match = re.search(r'TIME_MS:\s*([\d\.]+)', output)
    if match:
        return float(match.group(1))
    return None

def parse_output(output: str, n1: int, n2: int, k: int) -> Tuple[Optional[int], bool]:
    """
    Parsuje output programu C++ i zwraca (koszt, czy znaleziono rozwiązanie)
    """
    lines = output.split('\n')
    
    # Sprawdź czy znaleziono rozwiązanie
    if "ERROR: No solution found" in output or "Nie znaleziono rozwiązania" in output:
        return None, False
    
    # Sprawdź czy to verbose mode
    is_verbose = any('===' in line or 'Extension cost:' in line for line in lines)
    
    if is_verbose:
        # Parsuj koszt z verbose mode
        for line in lines:
            if 'Extension cost:' in line or 'Koszt rozszerzenia:' in line:
                match = re.search(r':\s*(\d+)', line)
                if match:
                    return int(match.group(1)), True
    else:
        # Simple mode: n, macierz, koszt
        clean_lines = [line.strip() for line in lines if line.strip() and not line.startswith('ERROR')]
        if len(clean_lines) >= 3:
            try:
                n = int(clean_lines[0])
                if n == n2:
                    cost_line = clean_lines[n + 1]
                    return int(cost_line), True
            except (ValueError, IndexError):
                pass
    
    return None, False

def run_single_test(test_file: str, algorithm: str, exe_path: str, timeout: int = 60, kill_on_timeout: bool = True) -> TestResult:
    """
    Uruchamia pojedynczy test i zwraca wynik.
    
    Args:
        test_file: Ścieżka do pliku testowego
        algorithm: 'exact' lub 'approx'
        exe_path: Ścieżka do programu wykonywalnego
        timeout: Timeout w sekundach (domyślnie 60)
        kill_on_timeout: Czy zabić proces przy timeout (domyślnie True)
    """
    # Wczytaj parametry z pliku
    with open(test_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    try:
        n1 = int(lines[0])
        n2 = int(lines[n1 + 1])
        k = int(lines[n1 + n2 + 2]) if len(lines) > n1 + n2 + 2 else 1
    except (ValueError, IndexError):
        return TestResult(0, 0, 0, algorithm, 0.0, None, False, test_file, "Błąd parsowania pliku")
    
    # Przygotuj komendę
    cmd = [exe_path, test_file]
    if algorithm == 'approx':
        cmd.append('-a')
    cmd.append('-r')  # Raw output dla szybszego parsowania
    
    start_time = time.time()
    process = None
    try:
        # Uruchom proces
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Czekaj na zakończenie z timeoutem
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            elapsed_ms = (time.time() - start_time) * 1000
            returncode = process.returncode
            
            # Debug: sprawdź output jeśli nie znaleziono rozwiązania
            combined_output = stdout + "\n" + stderr
            
            # Sprawdź czy program zwrócił błąd walidacji (to jest OK - niektóre testy są niemożliwe)
            if "ERROR: Impossible" in combined_output or "k > C(n2,n1)" in combined_output:
                return TestResult(n1, n2, k, algorithm, elapsed_ms, None, False, test_file, "Mathematically impossible")
            
            cost, found = parse_output(combined_output, n1, n2, k)
            
            # Spróbuj pobrać dokładny czas wewnętrzny
            internal_time = parse_execution_time(combined_output)
            if internal_time is not None:
                elapsed_ms = internal_time
            
            # Jeśli nie znaleziono, sprawdź czy to błąd czy rzeczywiście brak rozwiązania
            if not found and returncode == 0:
                # Program zakończył się sukcesem, ale nie znalazł rozwiązania (możliwe)
                return TestResult(n1, n2, k, algorithm, elapsed_ms, cost, False, test_file, None)
            elif not found and returncode != 0:
                # Program zwrócił błąd
                error_msg = (stderr[:200] if stderr else stdout[:200]) or "Unknown error"
                return TestResult(n1, n2, k, algorithm, elapsed_ms, cost, False, test_file, error_msg)
            
            return TestResult(n1, n2, k, algorithm, elapsed_ms, cost, found, test_file, None)
            
        except subprocess.TimeoutExpired:
            # Timeout - zabij proces jeśli wymagane
            elapsed_ms = (time.time() - start_time) * 1000
            if kill_on_timeout and process:
                try:
                    process.kill()
                    process.wait(timeout=5)  # Czekaj na zakończenie
                except:
                    pass  # Ignoruj błędy przy zabijaniu
            return TestResult(n1, n2, k, algorithm, elapsed_ms, None, False, test_file, "Timeout")
        
    except Exception as e:
        # Zabij proces jeśli jeszcze działa
        if process:
            try:
                process.kill()
                process.wait(timeout=2)
            except:
                pass
        return TestResult(n1, n2, k, algorithm, 0.0, None, False, test_file, str(e))

def generate_test_case(output_file: str, n1: int, n2: int, k: int, density: float = 0.3, seed: Optional[int] = None, easy: bool = False):
    """
    Generuje losowy test case i zapisuje do pliku.
    
    Args:
        easy: Jeśli True, G1 jest zawsze podgrafem G2 (łatwe testy, zawsze rozwiązanie).
              Jeśli False, G1 i G2 są generowane niezależnie (trudniejsze, może nie być rozwiązania).
    """
    if seed is not None:
        random.seed(seed)
    
    with open(output_file, 'w') as f:
        f.write(f"{n1}\n")
        # Macierz G1 - losowy graf
        g1_matrix = []
        for i in range(n1):
            row = [random.randint(1, 3) if random.random() < density else 0 for _ in range(n1)]
            g1_matrix.append(row)
            f.write(" ".join(map(str, row)) + "\n")
        
        f.write(f"{n2}\n")
        # Macierz G2
        g2_matrix = []
        
        if easy:
            # ŁATWE: G1 jest zawsze podgrafem G2 (w losowych miejscach, nie zawsze pierwsze n1)
            # Wybierz losowe pozycje dla G1 w G2
            g1_positions = sorted(random.sample(range(n2), n1))
            
            for i in range(n2):
                row = []
                for j in range(n2):
                    # Sprawdź czy (i, j) odpowiada jakiejś krawędzi w G1
                    if i in g1_positions and j in g1_positions:
                        idx_i = g1_positions.index(i)
                        idx_j = g1_positions.index(j)
                        base = g1_matrix[idx_i][idx_j]
                        # Dodaj losowe krawędzie z większym prawdopodobieństwem
                        extra = random.randint(0, 2) if random.random() < 0.3 else 0
                        row.append(base + extra)
                    else:
                        # Reszta grafu - losowe krawędzie
                        val = random.randint(1, 3) if random.random() < density else 0
                        row.append(val)
                g2_matrix.append(row)
        else:
            # TRUDNE: G1 i G2 są niezależne - może nie być rozwiązania!
            # Generuj G2 losowo
            for i in range(n2):
                row = [random.randint(1, 3) if random.random() < density else 0 for _ in range(n2)]
                g2_matrix.append(row)
            
            # Z małym prawdopodobieństwem dodaj G1 jako podgraf (żeby nie wszystkie były NO_SOL)
            if random.random() < 0.3:  # 30% szansy że G1 jest podgrafem
                g1_positions = sorted(random.sample(range(n2), n1))
                for idx_i, pos_i in enumerate(g1_positions):
                    for idx_j, pos_j in enumerate(g1_positions):
                        if g1_matrix[idx_i][idx_j] > 0:
                            # Upewnij się że krawędź w G2 ma co najmniej taką samą wagę
                            g2_matrix[pos_i][pos_j] = max(g2_matrix[pos_i][pos_j], g1_matrix[idx_i][idx_j])
        
        for row in g2_matrix:
            f.write(" ".join(map(str, row)) + "\n")
        
        f.write(f"{k}\n")

def find_all_test_dirs() -> List[str]:
    """
    Automatycznie znajduje wszystkie katalogi z testami (zaczynające się od 'tests').
    """
    test_dirs = []
    for item in os.listdir('.'):
        if os.path.isdir(item) and item.startswith('tests'):
            test_dirs.append(item)
    return sorted(test_dirs)

def collect_existing_tests(test_dirs: List[str]) -> List[Tuple[str, int, int, int]]:
    """
    Zbiera istniejące testy z katalogów i parsuje ich parametry.
    Zwraca listę (ścieżka_pliku, n1, n2, k)
    """
    tests = []
    for test_dir in test_dirs:
        if not os.path.exists(test_dir):
            continue
        for filename in sorted(os.listdir(test_dir)):
            if not filename.endswith('.txt'):
                continue
            filepath = os.path.join(test_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    lines = [line.strip() for line in f if line.strip()]
                if len(lines) < 2:
                    continue
                n1 = int(lines[0])
                n2 = int(lines[n1 + 1])
                k = int(lines[n1 + n2 + 2]) if len(lines) > n1 + n2 + 2 else 1
                tests.append((filepath, n1, n2, k))
            except (ValueError, IndexError):
                continue
    return tests

def run_performance_suite(
    test_scenarios: List[Tuple[int, int, int]] = None,
    exe_path: str = None,
    output_dir: str = "performance_results",
    num_runs: int = 1,
    timeout: int = 60,
    use_existing_tests: bool = False,
    test_dirs: List[str] = None,
    skip_timeout: bool = False,
    easy_tests: bool = False,
    hard_tests: bool = False
) -> List[TestResult]:
    """
    Przeprowadza pełną serię testów wydajnościowych
    """
    os.makedirs(output_dir, exist_ok=True)
    results = []
    
    print("=" * 80)
    print("PERFORMANCE TEST SUITE")
    print("=" * 80)
    
    if use_existing_tests:
        # Użyj istniejących testów
        if not test_dirs:
            test_dirs = find_all_test_dirs()
            print(f"Auto-wykryto katalogi testowe: {', '.join(test_dirs)}")
        existing_tests = collect_existing_tests(test_dirs)
        print(f"Znaleziono {len(existing_tests)} istniejących testów z {len(test_dirs)} katalogów")
        print(f"Algorytmy: exact, approx")
        print("=" * 80)
        
        total_tests = len(existing_tests) * 2  # 2 algorytmy
        current_test = 0
        
        for test_file, n1, n2, k in existing_tests:
            # Test exact
            current_test += 1
            print(f"[{current_test}/{total_tests}] EXACT  {os.path.basename(test_file)} (n1={n1}, n2={n2}, k={k})", end=" ... ", flush=True)
            try:
                result_exact = run_single_test(test_file, 'exact', exe_path, timeout)
                results.append(result_exact)
                status = "OK" if result_exact.found else ("TIMEOUT" if result_exact.error == "Timeout" else "NO_SOL")
                print(f"{status:8s} {result_exact.time_ms:8.1f}ms")
            except KeyboardInterrupt:
                print("PRZERWANO przez użytkownika")
                break
            except Exception as e:
                print(f"BŁĄD: {str(e)[:50]}")
                results.append(TestResult(n1, n2, k, 'exact', 0.0, None, False, test_file, str(e)))
            
            # Test approx
            current_test += 1
            print(f"[{current_test}/{total_tests}] APPROX {os.path.basename(test_file)} (n1={n1}, n2={n2}, k={k})", end=" ... ", flush=True)
            try:
                result_approx = run_single_test(test_file, 'approx', exe_path, timeout)
                results.append(result_approx)
                status = "OK" if result_approx.found else ("TIMEOUT" if result_approx.error == "Timeout" else "NO_SOL")
                print(f"{status:8s} {result_approx.time_ms:8.1f}ms")
            except KeyboardInterrupt:
                print("PRZERWANO przez użytkownika")
                break
            except Exception as e:
                print(f"BŁĄD: {str(e)[:50]}")
                results.append(TestResult(n1, n2, k, 'approx', 0.0, None, False, test_file, str(e)))
    else:
        # Generuj losowe testy
        print(f"Scenariuszy: {len(test_scenarios)}, Powtórzeń: {num_runs}")
        print(f"Algorytmy: exact, approx")
        print("=" * 80)
        
        temp_dir = os.path.join(output_dir, "temp_tests")
        os.makedirs(temp_dir, exist_ok=True)
        
        total_tests = len(test_scenarios) * 2 * num_runs  # 2 algorytmy
        current_test = 0
        
        for scenario_idx, (n1, n2, k) in enumerate(test_scenarios):
            for run in range(num_runs):
                # Generuj test case
                test_file = os.path.join(temp_dir, f"test_{scenario_idx}_{run}.txt")
                seed = scenario_idx * 1000 + run
                # Określ trudność testów
                if easy_tests:
                    easy_mode = True
                elif hard_tests:
                    easy_mode = False
                else:
                    # Domyślnie: łatwe dla małych, trudne dla dużych
                    easy_mode = n1 < 7 and n2 < 20
                generate_test_case(test_file, n1, n2, k, density=0.2, seed=seed, easy=easy_mode)
                
                # Test exact
                current_test += 1
                print(f"[{current_test}/{total_tests}] EXACT  n1={n1:3d}, n2={n2:3d}, k={k:2d} (run {run+1}/{num_runs})", end=" ... ")
                result_exact = run_single_test(test_file, 'exact', exe_path, timeout)
                results.append(result_exact)
                status = "OK" if result_exact.found else ("TIMEOUT" if result_exact.error == "Timeout" else "NO_SOL")
                print(f"{status:8s} {result_exact.time_ms:8.1f}ms")
                
                # Test approx
                current_test += 1
                print(f"[{current_test}/{total_tests}] APPROX n1={n1:3d}, n2={n2:3d}, k={k:2d} (run {run+1}/{num_runs})", end=" ... ")
                result_approx = run_single_test(test_file, 'approx', exe_path, timeout)
                results.append(result_approx)
                status = "OK" if result_approx.found else ("TIMEOUT" if result_approx.error == "Timeout" else "NO_SOL")
                print(f"{status:8s} {result_approx.time_ms:8.1f}ms")
        
        # Usuń pliki tymczasowe
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    # Zapisz wyniki do JSON
    results_file = os.path.join(output_dir, "results.json")
    with open(results_file, 'w') as f:
        json.dump([asdict(r) for r in results], f, indent=2)
    
    print("\n" + "=" * 80)
    print(f"Wyniki zapisane do: {results_file}")
    print("=" * 80)
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Performance Testing Suite")
    parser.add_argument('--exe', type=str, default=r".\build\subgraph-isomorphism.exe",
                       help="Path to executable")
    parser.add_argument('--output', type=str, default="performance_results",
                       help="Output directory for results")
    parser.add_argument('--runs', type=int, default=1,
                       help="Number of runs per scenario (for averaging)")
    parser.add_argument('--timeout', type=int, default=60,
                       help="Timeout per test in seconds (default: 60)")
    parser.add_argument('--skip-timeout', action='store_true',
                       help="Skip tests that timeout (continue with next test)")
    parser.add_argument('--scenario', type=str, choices=['small', 'medium', 'large', 'scaling', 'comprehensive', 'custom', 'existing'],
                       default='scaling', help="Test scenario set (comprehensive = bardzo dużo testów)")
    parser.add_argument('--use-existing', action='store_true',
                       help="Use existing test files instead of generating random tests")
    parser.add_argument('--test-dirs', type=str, nargs='+',
                       default=None,
                       help="Directories with existing test files (default: auto-detect all 'tests*' folders)")
    parser.add_argument('--auto-detect', action='store_true', default=True,
                       help="Auto-detect all test directories (default: True)")
    parser.add_argument('--easy-tests', action='store_true', default=False,
                       help="Generate easy tests (G1 always subgraph of G2) - faster but less realistic")
    parser.add_argument('--hard-tests', action='store_true', default=False,
                       help="Generate hard tests (G1 and G2 independent) - more realistic but may have NO_SOL")
    
    args = parser.parse_args()
    
    # Użyj istniejących testów jeśli wybrano
    if args.use_existing or args.scenario == 'existing':
        if args.test_dirs:
            test_dirs = args.test_dirs
        elif args.auto_detect:
            test_dirs = find_all_test_dirs()
            print(f"Auto-wykryto katalogi testowe: {', '.join(test_dirs)}")
        else:
            test_dirs = ['tests', 'tests_auto', 'tests_stress']
        results = run_performance_suite(
            exe_path=args.exe,
            output_dir=args.output,
            num_runs=1,
            timeout=args.timeout,
            use_existing_tests=True,
            test_dirs=test_dirs,
            skip_timeout=args.skip_timeout
        )
    else:
        # Definiuj scenariusze testowe
        if args.scenario == 'small':
            scenarios = [
                (3, 5, 1), (3, 5, 2),
                (4, 6, 1), (4, 6, 2),
                (5, 8, 1), (5, 8, 2),
            ]
        elif args.scenario == 'medium':
            scenarios = [
                (5, 10, 1), (5, 10, 2), (5, 10, 3),
                (6, 12, 1), (6, 12, 2),
                (7, 15, 1), (7, 15, 2),
            ]
        elif args.scenario == 'large':
            scenarios = [
                (8, 20, 1), (8, 20, 2), (8, 20, 3),
                (10, 25, 1), (10, 25, 2),
                (12, 30, 1),
            ]
        elif args.scenario == 'scaling':
            # Testy skalowalności - PEŁNE SYSTEMATYCZNE pokrycie WSZYSTKICH kombinacji
            scenarios = []
            # Dla każdego n1, testuj WSZYSTKIE sensowne n2 (każde, nie co 2!)
            for n1 in range(3, 11):  # n1: 3-10
                for n2 in range(n1 + 2, 31):  # n2: od n1+2 do 30, KAŻDE (bez przerw!)
                    for k in range(1, 6):  # k: 1-5
                        scenarios.append((n1, n2, k))
            # Usuń duplikaty i posortuj
            scenarios = list(set(scenarios))
            scenarios.sort()
        elif args.scenario == 'comprehensive':
            # Bardzo duży zestaw testów - dla solidnych danych
            scenarios = []
            # Systematyczne pokrycie przestrzeni parametrów
            for n1 in range(3, 11):  # n1: 3-10
                for n2 in range(max(n1+2, 8), 32, 2):  # n2: co 2, od max(n1+2, 8) do 30
                    for k in range(1, 6):  # k: 1-5
                        if n2 > n1:  # n2 musi być większe niż n1
                            scenarios.append((n1, n2, k))
            # Usuń duplikaty i posortuj
            scenarios = list(set(scenarios))
            scenarios.sort()
        else:  # custom - można rozszerzyć
            scenarios = [
                (5, 15, 2),
            ]
        
        results = run_performance_suite(
            scenarios,
            args.exe,
            args.output,
            args.runs,
            args.timeout,
            use_existing_tests=False,
            skip_timeout=args.skip_timeout,
            easy_tests=args.easy_tests,
            hard_tests=args.hard_tests
        )
    
    # Podsumowanie
    exact_results = [r for r in results if r.algorithm == 'exact' and r.found]
    approx_results = [r for r in results if r.algorithm == 'approx' and r.found]
    exact_timeouts = [r for r in results if r.algorithm == 'exact' and r.error == "Timeout"]
    approx_timeouts = [r for r in results if r.algorithm == 'approx' and r.error == "Timeout"]
    
    print("\n" + "=" * 80)
    print("PODSUMOWANIE")
    print("=" * 80)
    exact_total = len([r for r in results if r.algorithm == 'exact'])
    print(f"EXACT:  {len(exact_results)}/{exact_total} testów zakończonych sukcesem")
    if exact_timeouts:
        print(f"        {len(exact_timeouts)} testów przekroczyło timeout")
    if exact_results:
        avg_time = sum(r.time_ms for r in exact_results) / len(exact_results)
        print(f"        Średni czas: {avg_time:.2f}ms")
    
    approx_total = len([r for r in results if r.algorithm == 'approx'])
    print(f"APPROX: {len(approx_results)}/{approx_total} testów zakończonych sukcesem")
    if approx_timeouts:
        print(f"        {len(approx_timeouts)} testów przekroczyło timeout")
    if approx_results:
        avg_time = sum(r.time_ms for r in approx_results) / len(approx_results)
        print(f"        Średni czas: {avg_time:.2f}ms")
    print("=" * 80)

if __name__ == "__main__":
    main()

