#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PORÓWNANIE ALGORYTMÓW
=====================
Szczegółowe porównanie wyników algorytmów exact i approximate.
Generuje statystyki, tabele i analizę różnic.
"""

import json
import os
import argparse
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import statistics

@dataclass
class TestResult:
    n1: int
    n2: int
    k: int
    algorithm: str
    time_ms: float
    cost: int
    found: bool

def load_results(json_file: str) -> List[TestResult]:
    """Wczytuje wyniki z pliku JSON"""
    with open(json_file, 'r') as f:
        data = json.load(f)
    results = []
    for r in data:
        # Ignoruj nieznane pola (test_file, error)
        filtered = {k: v for k, v in r.items() 
                   if k in ['n1', 'n2', 'k', 'algorithm', 'time_ms', 'cost', 'found']}
        results.append(TestResult(**filtered))
    return results

def compare_algorithms(results: List[TestResult]) -> Dict:
    """
    Porównuje algorytmy exact i approximate.
    Zwraca słownik ze statystykami.
    """
    exact = [r for r in results if r.algorithm == 'exact' and r.found and r.cost is not None]
    approx = [r for r in results if r.algorithm == 'approx' and r.found and r.cost is not None]
    
    # Znajdź wspólne testy (te same n1, n2, k)
    exact_dict = {(r.n1, r.n2, r.k): r for r in exact}
    approx_dict = {(r.n1, r.n2, r.k): r for r in approx}
    
    common_keys = set(exact_dict.keys()) & set(approx_dict.keys())
    
    if not common_keys:
        return {
            'error': 'Brak wspólnych testów do porównania',
            'exact_count': len(exact),
            'approx_count': len(approx)
        }
    
    # Porównanie czasu
    exact_times = [exact_dict[k].time_ms for k in common_keys]
    approx_times = [approx_dict[k].time_ms for k in common_keys]
    
    time_ratios = [exact_times[i] / approx_times[i] if approx_times[i] > 0 else 0 
                   for i in range(len(exact_times))]
    
    # Porównanie kosztu
    exact_costs = [exact_dict[k].cost for k in common_keys]
    approx_costs = [approx_dict[k].cost for k in common_keys]
    
    cost_ratios = [approx_costs[i] / exact_costs[i] if exact_costs[i] > 0 else 0 
                   for i in range(len(exact_costs))]
    
    # Statystyki
    stats = {
        'total_tests': len(common_keys),
        'exact_only': len(exact_dict) - len(common_keys),
        'approx_only': len(approx_dict) - len(common_keys),
        
        'time': {
            'exact_mean': statistics.mean(exact_times) if exact_times else 0,
            'exact_median': statistics.median(exact_times) if exact_times else 0,
            'exact_max': max(exact_times) if exact_times else 0,
            'exact_min': min(exact_times) if exact_times else 0,
            'approx_mean': statistics.mean(approx_times) if approx_times else 0,
            'approx_median': statistics.median(approx_times) if approx_times else 0,
            'approx_max': max(approx_times) if approx_times else 0,
            'approx_min': min(approx_times) if approx_times else 0,
            'speedup_mean': statistics.mean(time_ratios) if time_ratios else 0,
            'speedup_median': statistics.median(time_ratios) if time_ratios else 0,
            'speedup_max': max(time_ratios) if time_ratios else 0,
            'speedup_min': min(time_ratios) if time_ratios else 0,
        },
        
        'cost': {
            'exact_mean': statistics.mean(exact_costs) if exact_costs else 0,
            'exact_median': statistics.median(exact_costs) if exact_costs else 0,
            'exact_max': max(exact_costs) if exact_costs else 0,
            'exact_min': min(exact_costs) if exact_costs else 0,
            'approx_mean': statistics.mean(approx_costs) if approx_costs else 0,
            'approx_median': statistics.median(approx_costs) if approx_costs else 0,
            'approx_max': max(approx_costs) if approx_costs else 0,
            'approx_min': min(approx_costs) if approx_costs else 0,
            'ratio_mean': statistics.mean(cost_ratios) if cost_ratios else 0,
            'ratio_median': statistics.median(cost_ratios) if cost_ratios else 0,
            'ratio_max': max(cost_ratios) if cost_ratios else 0,
            'ratio_min': min(cost_ratios) if cost_ratios else 0,
        },
        
        'optimal_solutions': sum(1 for i in range(len(cost_ratios)) if cost_ratios[i] == 1.0),
        'approx_better_time': sum(1 for r in time_ratios if r > 1.0),
        'approx_worse_cost': sum(1 for r in cost_ratios if r > 1.0),
    }
    
    return stats

def print_comparison_report(stats: Dict, output_file: Optional[str] = None):
    """Wypisuje raport porównawczy"""
    lines = []
    
    lines.append("=" * 80)
    lines.append("PORÓWNANIE ALGORYTMÓW EXACT vs APPROXIMATE")
    lines.append("=" * 80)
    lines.append("")
    
    if 'error' in stats:
        lines.append(f"BŁĄD: {stats['error']}")
        lines.append(f"Exact: {stats['exact_count']} wyników")
        lines.append(f"Approx: {stats['approx_count']} wyników")
        output = "\n".join(lines)
        print(output)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
        return
    
    lines.append(f"Liczba porównywanych testów: {stats['total_tests']}")
    lines.append(f"Testy tylko w Exact: {stats['exact_only']}")
    lines.append(f"Testy tylko w Approx: {stats['approx_only']}")
    lines.append("")
    
    # Statystyki czasu
    lines.append("-" * 80)
    lines.append("STATYSTYKI CZASU WYKONANIA")
    lines.append("-" * 80)
    lines.append(f"{'Metryka':<30} | {'Exact [ms]':<15} | {'Approx [ms]':<15} | {'Stosunek':<15}")
    lines.append("-" * 80)
    lines.append(f"{'Średnia':<30} | {stats['time']['exact_mean']:<15.2f} | {stats['time']['approx_mean']:<15.2f} | {stats['time']['speedup_mean']:<15.2f}x")
    lines.append(f"{'Mediana':<30} | {stats['time']['exact_median']:<15.2f} | {stats['time']['approx_median']:<15.2f} | {stats['time']['speedup_median']:<15.2f}x")
    lines.append(f"{'Maksimum':<30} | {stats['time']['exact_max']:<15.2f} | {stats['time']['approx_max']:<15.2f} | {stats['time']['speedup_max']:<15.2f}x")
    lines.append(f"{'Minimum':<30} | {stats['time']['exact_min']:<15.2f} | {stats['time']['approx_min']:<15.2f} | {stats['time']['speedup_min']:<15.2f}x")
    lines.append("")
    
    # Statystyki kosztu
    lines.append("-" * 80)
    lines.append("STATYSTYKI KOSZTU ROZSZERZENIA")
    lines.append("-" * 80)
    lines.append(f"{'Metryka':<30} | {'Exact':<15} | {'Approx':<15} | {'Stosunek':<15}")
    lines.append("-" * 80)
    lines.append(f"{'Średnia':<30} | {stats['cost']['exact_mean']:<15.2f} | {stats['cost']['approx_mean']:<15.2f} | {stats['cost']['ratio_mean']:<15.2f}x")
    lines.append(f"{'Mediana':<30} | {stats['cost']['exact_median']:<15.2f} | {stats['cost']['approx_median']:<15.2f} | {stats['cost']['ratio_median']:<15.2f}x")
    lines.append(f"{'Maksimum':<30} | {stats['cost']['exact_max']:<15} | {stats['cost']['approx_max']:<15} | {stats['cost']['ratio_max']:<15.2f}x")
    lines.append(f"{'Minimum':<30} | {stats['cost']['exact_min']:<15} | {stats['cost']['approx_min']:<15} | {stats['cost']['ratio_min']:<15.2f}x")
    lines.append("")
    
    # Analiza jakości
    lines.append("-" * 80)
    lines.append("ANALIZA JAKOŚCI")
    lines.append("-" * 80)
    lines.append(f"Rozwiązania optymalne (Approx = Exact): {stats['optimal_solutions']}/{stats['total_tests']} ({100*stats['optimal_solutions']/stats['total_tests']:.1f}%)")
    lines.append(f"Approx szybszy niż Exact: {stats['approx_better_time']}/{stats['total_tests']} ({100*stats['approx_better_time']/stats['total_tests']:.1f}%)")
    lines.append(f"Approx gorszy koszt niż Exact: {stats['approx_worse_cost']}/{stats['total_tests']} ({100*stats['approx_worse_cost']/stats['total_tests']:.1f}%)")
    lines.append("")
    
    # Wnioski
    lines.append("-" * 80)
    lines.append("WNIOSKI")
    lines.append("-" * 80)
    
    if stats['time']['speedup_mean'] > 1.0:
        lines.append(f"✓ Approx jest średnio {stats['time']['speedup_mean']:.2f}x szybszy niż Exact")
    else:
        lines.append(f"✗ Approx jest średnio {1/stats['time']['speedup_mean']:.2f}x wolniejszy niż Exact")
    
    if stats['cost']['ratio_mean'] <= 1.1:
        lines.append(f"✓ Approx znajduje rozwiązania bardzo bliskie optymalnym (średnio {stats['cost']['ratio_mean']:.2f}x kosztu Exact)")
    elif stats['cost']['ratio_mean'] <= 1.5:
        lines.append(f"⚠ Approx znajduje rozwiązania akceptowalne (średnio {stats['cost']['ratio_mean']:.2f}x kosztu Exact)")
    else:
        lines.append(f"✗ Approx znajduje rozwiązania znacznie gorsze (średnio {stats['cost']['ratio_mean']:.2f}x kosztu Exact)")
    
    if stats['optimal_solutions'] / stats['total_tests'] > 0.5:
        lines.append(f"✓ Approx znajduje rozwiązanie optymalne w {100*stats['optimal_solutions']/stats['total_tests']:.1f}% przypadków")
    
    lines.append("")
    lines.append("=" * 80)
    
    output = "\n".join(lines)
    print(output)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"\nRaport zapisany do: {output_file}")

def main():
    from typing import Optional
    
    parser = argparse.ArgumentParser(description="Compare Exact vs Approximate Algorithms")
    parser.add_argument('--input', type=str, default='performance_results/results.json',
                       help="Input JSON file with test results")
    parser.add_argument('--output', type=str, default='performance_results/comparison_report.txt',
                       help="Output file for comparison report")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Błąd: Plik {args.input} nie istnieje!")
        print("Uruchom najpierw performance_tests.py aby wygenerować dane.")
        return
    
    results = load_results(args.input)
    print(f"Wczytano {len(results)} wyników testów")
    
    stats = compare_algorithms(results)
    print_comparison_report(stats, args.output)

if __name__ == "__main__":
    main()

