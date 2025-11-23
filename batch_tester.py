#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BATCH TESTER - Testowanie dowolnego exe na folderze testów
===========================================================
Użycie:
  python batch_tester.py <exe_path> <tests_folder> [algorithm]
  
Przykłady:
  python batch_tester.py .\\build\\subgraph-isomorphism.exe tests_v2 exact
  python batch_tester.py other_team\\solver.exe tests_manual_verify exact
  python batch_tester.py competitor.exe tests_stress approx
"""

import subprocess
import os
import sys
import re
import time
from typing import List, Tuple, Optional
import json


def run_single_test(exe_path: str, test_file: str, algorithm: str = "exact", timeout: int = 30) -> dict:
    """
    Uruchamia pojedynczy test i zwraca wyniki
    
    Returns:
        dict: {
            'success': bool,
            'cost': int or None,
            'time_ms': float,
            'error': str or None,
            'stdout': str,
            'stderr': str
        }
    """
    start = time.time()
    
    try:
        result = subprocess.run(
            [exe_path, test_file, algorithm],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )
        elapsed_ms = (time.time() - start) * 1000
        
        # Parse koszt
        cost = None
        for line in result.stdout.split('\n'):
            # Obsługa różnych formatów outputu
            if 'Koszt rozszerzenia:' in line or 'Cost:' in line or 'koszt:' in line.lower():
                match = re.search(r':\s*(\d+)', line)
                if match:
                    cost = int(match.group(1))
                    break
        
        # Sprawdź czy znaleziono rozwiązanie
        no_solution = ('Nie znaleziono' in result.stdout or 
                       'No solution' in result.stdout or
                       'BRAK' in result.stdout.upper())
        
        if no_solution:
            return {
                'success': False,
                'cost': None,
                'time_ms': elapsed_ms,
                'error': 'NO_SOLUTION',
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        
        if cost is None:
            return {
                'success': False,
                'cost': None,
                'time_ms': elapsed_ms,
                'error': 'PARSE_ERROR (nie znaleziono kosztu w output)',
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        
        return {
            'success': True,
            'cost': cost,
            'time_ms': elapsed_ms,
            'error': None,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'cost': None,
            'time_ms': timeout * 1000,
            'error': 'TIMEOUT',
            'stdout': '',
            'stderr': ''
        }
    except FileNotFoundError:
        return {
            'success': False,
            'cost': None,
            'time_ms': 0,
            'error': f'EXE_NOT_FOUND: {exe_path}',
            'stdout': '',
            'stderr': ''
        }
    except Exception as e:
        return {
            'success': False,
            'cost': None,
            'time_ms': 0,
            'error': f'EXCEPTION: {str(e)}',
            'stdout': '',
            'stderr': ''
        }


def collect_tests(folder: str) -> List[str]:
    """Zbiera wszystkie pliki .txt z folderu"""
    if not os.path.exists(folder):
        print(f"BŁĄD: Folder {folder} nie istnieje!")
        return []
    
    tests = []
    for filename in sorted(os.listdir(folder)):
        if filename.endswith('.txt') and not filename.endswith('_OPIS.txt'):
            tests.append(os.path.join(folder, filename))
    
    return tests


def print_result(test_name: str, result: dict, index: int, total: int):
    """Wyświetla wynik testu"""
    status = "OK" if result['success'] else result['error']
    time_str = f"{result['time_ms']:.0f}ms" if result['time_ms'] < 1000 else f"{result['time_ms']/1000:.1f}s"
    
    if result['success']:
        print(f"[{index}/{total}] {test_name:50s} [{status:12s}] koszt={result['cost']:4d} ({time_str})")
    else:
        print(f"[{index}/{total}] {test_name:50s} [{status:12s}] ({time_str})")


def save_results(results: List[dict], output_file: str):
    """Zapisuje wyniki do pliku JSON"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nWyniki zapisane do: {output_file}")


def print_summary(results: List[dict], exe_name: str, folder: str, algorithm: str):
    """Wyświetla podsumowanie wyników"""
    total = len(results)
    passed = sum(1 for r in results if r['results']['success'])
    failed = sum(1 for r in results if not r['results']['success'] and r['results']['error'] != 'NO_SOLUTION')
    no_solution = sum(1 for r in results if r['results']['error'] == 'NO_SOLUTION')
    timeout = sum(1 for r in results if r['results']['error'] == 'TIMEOUT')
    
    avg_time = sum(r['results']['time_ms'] for r in results if r['results']['success']) / max(passed, 1)
    total_time = sum(r['results']['time_ms'] for r in results)
    
    print("\n" + "=" * 80)
    print("PODSUMOWANIE")
    print("=" * 80)
    print(f"\nProgram:     {exe_name}")
    print(f"Folder:      {folder}")
    print(f"Algorytm:    {algorithm}")
    print(f"Testy:       {total}")
    print()
    print(f"PASSED:      {passed}/{total} ({passed*100//total if total > 0 else 0}%)")
    print(f"NO_SOLUTION: {no_solution}/{total}")
    print(f"TIMEOUT:     {timeout}/{total}")
    print(f"FAILED:      {failed}/{total}")
    print()
    print(f"Średni czas (PASSED): {avg_time:.0f}ms")
    print(f"Całkowity czas:       {total_time/1000:.1f}s")
    
    # Lista błędów
    errors = [r for r in results if not r['results']['success'] and r['results']['error'] not in ['NO_SOLUTION', 'TIMEOUT']]
    if errors:
        print("\n" + "=" * 80)
        print("BŁĘDY")
        print("=" * 80)
        for item in errors[:10]:  # Pokaż max 10 błędów
            print(f"  {item['test']}: {item['results']['error']}")
        if len(errors) > 10:
            print(f"  ... i {len(errors)-10} więcej")
    
    print("=" * 80)


def main():
    if len(sys.argv) < 3:
        print("UŻYCIE: python batch_tester.py <exe_path> <tests_folder> [algorithm] [timeout]")
        print()
        print("PRZYKŁADY:")
        print("  python batch_tester.py .\\build\\subgraph-isomorphism.exe tests_v2 exact")
        print("  python batch_tester.py other_team\\solver.exe tests_manual_verify exact")
        print("  python batch_tester.py competitor.exe tests_stress approx 60")
        print()
        print("PARAMETRY:")
        print("  exe_path      - ścieżka do pliku .exe")
        print("  tests_folder  - folder z testami (.txt)")
        print("  algorithm     - 'exact' lub 'approx' (domyślnie: exact)")
        print("  timeout       - timeout w sekundach (domyślnie: 30)")
        sys.exit(1)
    
    exe_path = sys.argv[1]
    tests_folder = sys.argv[2]
    algorithm = sys.argv[3] if len(sys.argv) > 3 else "exact"
    timeout = int(sys.argv[4]) if len(sys.argv) > 4 else 30
    
    # Walidacja
    if not os.path.exists(exe_path):
        print(f"BŁĄD: Plik {exe_path} nie istnieje!")
        sys.exit(1)
    
    if algorithm not in ['exact', 'approx']:
        print(f"BŁĄD: Algorytm musi być 'exact' lub 'approx', nie '{algorithm}'")
        sys.exit(1)
    
    # Zbierz testy
    tests = collect_tests(tests_folder)
    if not tests:
        print(f"BŁĄD: Nie znaleziono testów w {tests_folder}")
        sys.exit(1)
    
    print("=" * 80)
    print("BATCH TESTER")
    print("=" * 80)
    print(f"\nProgram:   {exe_path}")
    print(f"Folder:    {tests_folder}")
    print(f"Algorytm:  {algorithm}")
    print(f"Timeout:   {timeout}s")
    print(f"Testy:     {len(tests)}")
    print()
    
    # Uruchom testy
    results = []
    for i, test_file in enumerate(tests, 1):
        test_name = os.path.basename(test_file)
        result = run_single_test(exe_path, test_file, algorithm, timeout)
        
        results.append({
            'test': test_name,
            'path': test_file,
            'results': result
        })
        
        print_result(test_name, result, i, len(tests))
    
    # Podsumowanie
    print_summary(results, os.path.basename(exe_path), tests_folder, algorithm)
    
    # Zapisz wyniki
    output_file = f"batch_results_{os.path.basename(exe_path).replace('.exe', '')}_{os.path.basename(tests_folder)}_{algorithm}.json"
    save_results(results, output_file)


if __name__ == "__main__":
    main()
