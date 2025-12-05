#!/usr/bin/env python3.13
# -*- coding: utf-8 -*-
"""
GŁÓWNY SKRYPT DO PRZEPROWADZANIA WSZYSTKICH TESTÓW
==================================================
Uruchamia pełną serię testów, generuje wykresy i sprawozdania.
"""

import subprocess
import sys
import os
import argparse
import shutil

def get_python_cmd():
    """Zwraca komendę python - preferuje python3.13 jeśli dostępny"""
    # Sprawdź czy python3.13 jest dostępny
    try:
        result = subprocess.run(['python3.13', '--version'], 
                              capture_output=True, timeout=2)
        if result.returncode == 0:
            return 'python3.13'
    except:
        pass
    return sys.executable

def main():
    parser = argparse.ArgumentParser(description="Run Complete Test Suite")
    parser.add_argument('--exe', type=str, default=r".\build\subgraph-isomorphism.exe",
                       help="Path to executable")
    parser.add_argument('--scenario', type=str, choices=['small', 'medium', 'large', 'scaling', 'comprehensive', 'existing'],
                       default='scaling', help="Test scenario set (default: scaling - recommended for plots)")
    parser.add_argument('--runs', type=int, default=1,
                       help="Number of runs per scenario")
    parser.add_argument('--timeout', type=int, default=300,
                       help="Timeout per test in seconds")
    parser.add_argument('--skip-tests', action='store_true',
                       help="Skip test execution, only generate plots/reports")
    parser.add_argument('--use-existing', action='store_true', default=True,
                       help="Use existing test files (default: True)")
    parser.add_argument('--test-dirs', type=str, nargs='+',
                       default=None,
                       help="Specific test directories (default: auto-detect all)")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("KOMPLEKSOWA SUITA TESTOWA")
    print("=" * 80)
    print()
    
    # Krok 1: Uruchom testy wydajnościowe
    if not args.skip_tests:
        print("KROK 1: Przeprowadzanie testów wydajnościowych...")
        print("-" * 80)
        python_cmd = get_python_cmd()
        cmd = [
            python_cmd, 'performance_tests.py',
            '--exe', args.exe,
            '--scenario', args.scenario,
            '--runs', str(args.runs),
            '--timeout', str(args.timeout)
        ]
        if args.use_existing or args.scenario == 'existing':
            cmd.append('--use-existing')
        if args.test_dirs:
            cmd.append('--test-dirs')
            cmd.extend(args.test_dirs)
        result = subprocess.run(cmd)
        
        if result.returncode != 0:
            print("BŁĄD: Testy wydajnościowe zakończone niepowodzeniem!")
            return 1
        print()
    else:
        print("KROK 1: Pominięto (--skip-tests)")
        print()
    
    # Krok 2: Generuj wykresy
    print("KROK 2: Generowanie wykresów wydajności...")
    print("-" * 80)
    python_cmd = get_python_cmd()
    result = subprocess.run([
        python_cmd, 'generate_plots.py'
    ])
    
    if result.returncode != 0:
        print("OSTRZEŻENIE: Generowanie wykresów zakończone z błędami (możliwe że brakuje matplotlib)")
        print("Zainstaluj: pip install matplotlib numpy")
    print()
    
    # Krok 3: Porównaj algorytmy
    print("KROK 3: Porównywanie algorytmów...")
    print("-" * 80)
    python_cmd = get_python_cmd()
    result = subprocess.run([
        python_cmd, 'compare_algorithms.py'
    ])
    
    if result.returncode != 0:
        print("OSTRZEŻENIE: Porównywanie algorytmów zakończone z błędami")
    print()
    
    # Krok 4: Generuj sprawozdanie
    print("KROK 4: Generowanie sprawozdania...")
    print("-" * 80)
    python_cmd = get_python_cmd()
    result = subprocess.run([
        python_cmd, 'generate_report.py'
    ])
    
    if result.returncode != 0:
        print("OSTRZEŻENIE: Generowanie sprawozdania zakończone z błędami")
    print()
    
    print("=" * 80)
    print("ZAKOŃCZONO")
    print("=" * 80)
    print()
    print("Wyniki znajdują się w katalogu: performance_results/")
    print("  - results.json - surowe dane testowe")
    print("  - plots/ - wykresy wydajności")
    print("  - comparison_report.txt - szczegółowe porównanie")
    print("  - report.md - sprawozdanie w formacie Markdown")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

