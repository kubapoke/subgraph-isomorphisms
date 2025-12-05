#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENERATOR SPRAWOZDANIA Z TESTÓW
================================
Generuje kompleksowe sprawozdanie z testów w formacie Markdown.
"""

import json
import os
import argparse
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime
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

def generate_markdown_report(results: List[TestResult], output_file: str):
    """Generuje sprawozdanie w formacie Markdown"""
    
    exact = [r for r in results if r.algorithm == 'exact' and r.found and r.cost is not None]
    approx = [r for r in results if r.algorithm == 'approx' and r.found and r.cost is not None]
    
    # Znajdź wspólne testy
    exact_dict = {(r.n1, r.n2, r.k): r for r in exact}
    approx_dict = {(r.n1, r.n2, r.k): r for r in approx}
    common_keys = set(exact_dict.keys()) & set(approx_dict.keys())
    
    lines = []
    
    # Nagłówek
    lines.append("# Sprawozdanie z testów wydajnościowych")
    lines.append("")
    lines.append(f"**Data wygenerowania:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Podsumowanie
    lines.append("## 1. Podsumowanie")
    lines.append("")
    lines.append(f"- **Łączna liczba testów:** {len(results)}")
    lines.append(f"- **Exact - poprawne wyniki:** {len(exact)}")
    lines.append(f"- **Approx - poprawne wyniki:** {len(approx)}")
    lines.append(f"- **Wspólne testy (do porównania):** {len(common_keys)}")
    lines.append("")
    
    # Statystyki czasu
    if exact:
        exact_times = [r.time_ms for r in exact]
        lines.append("### 1.1. Algorytm Exact - Statystyki czasu")
        lines.append("")
        lines.append("| Metryka | Wartość [ms] |")
        lines.append("|---------|--------------|")
        lines.append(f"| Średnia | {statistics.mean(exact_times):.2f} |")
        lines.append(f"| Mediana | {statistics.median(exact_times):.2f} |")
        lines.append(f"| Minimum | {min(exact_times):.2f} |")
        lines.append(f"| Maksimum | {max(exact_times):.2f} |")
        lines.append("")
    
    if approx:
        approx_times = [r.time_ms for r in approx]
        lines.append("### 1.2. Algorytm Approximate - Statystyki czasu")
        lines.append("")
        lines.append("| Metryka | Wartość [ms] |")
        lines.append("|---------|--------------|")
        lines.append(f"| Średnia | {statistics.mean(approx_times):.2f} |")
        lines.append(f"| Mediana | {statistics.median(approx_times):.2f} |")
        lines.append(f"| Minimum | {min(approx_times):.2f} |")
        lines.append(f"| Maksimum | {max(approx_times):.2f} |")
        lines.append("")
    
    # Porównanie
    if common_keys:
        lines.append("## 2. Porównanie algorytmów")
        lines.append("")
        
        exact_times = [exact_dict[k].time_ms for k in common_keys]
        approx_times = [approx_dict[k].time_ms for k in common_keys]
        time_ratios = [exact_times[i] / approx_times[i] if approx_times[i] > 0 else 0 
                      for i in range(len(exact_times))]
        
        exact_costs = [exact_dict[k].cost for k in common_keys]
        approx_costs = [approx_dict[k].cost for k in common_keys]
        cost_ratios = [approx_costs[i] / exact_costs[i] if exact_costs[i] > 0 else 0 
                      for i in range(len(exact_costs))]
        
        lines.append("### 2.1. Porównanie czasu wykonania")
        lines.append("")
        lines.append("| Metryka | Exact [ms] | Approx [ms] | Stosunek (Exact/Approx) |")
        lines.append("|---------|------------|-------------|--------------------------|")
        lines.append(f"| Średnia | {statistics.mean(exact_times):.2f} | {statistics.mean(approx_times):.2f} | {statistics.mean(time_ratios):.2f}x |")
        lines.append(f"| Mediana | {statistics.median(exact_times):.2f} | {statistics.median(approx_times):.2f} | {statistics.median(time_ratios):.2f}x |")
        lines.append("")
        
        lines.append("### 2.2. Porównanie kosztu rozszerzenia")
        lines.append("")
        lines.append("| Metryka | Exact | Approx | Stosunek (Approx/Exact) |")
        lines.append("|---------|-------|--------|-------------------------|")
        lines.append(f"| Średnia | {statistics.mean(exact_costs):.2f} | {statistics.mean(approx_costs):.2f} | {statistics.mean(cost_ratios):.2f}x |")
        lines.append(f"| Mediana | {statistics.median(exact_costs):.2f} | {statistics.median(approx_costs):.2f} | {statistics.median(cost_ratios):.2f}x |")
        lines.append("")
        
        optimal_count = sum(1 for r in cost_ratios if r == 1.0)
        lines.append(f"**Rozwiązania optymalne (Approx = Exact):** {optimal_count}/{len(common_keys)} ({100*optimal_count/len(common_keys):.1f}%)")
        lines.append("")
    
    # Analiza skalowalności
    lines.append("## 3. Analiza skalowalności")
    lines.append("")
    
    # Skalowanie względem n1
    lines.append("### 3.1. Wpływ n1 (rozmiar grafu G1)")
    lines.append("")
    lines.append("| n1 | Exact - średni czas [ms] | Approx - średni czas [ms] |")
    lines.append("|----|--------------------------|---------------------------|")
    
    n1_groups = defaultdict(list)
    for r in exact + approx:
        n1_groups[r.n1].append(r)
    
    for n1 in sorted(n1_groups.keys()):
        exact_n1 = [r for r in exact if r.n1 == n1]
        approx_n1 = [r for r in approx if r.n1 == n1]
        exact_avg = statistics.mean([r.time_ms for r in exact_n1]) if exact_n1 else 0
        approx_avg = statistics.mean([r.time_ms for r in approx_n1]) if approx_n1 else 0
        lines.append(f"| {n1} | {exact_avg:.2f} | {approx_avg:.2f} |")
    lines.append("")
    
    # Skalowanie względem n2
    lines.append("### 3.2. Wpływ n2 (rozmiar grafu G2)")
    lines.append("")
    lines.append("| n2 | Exact - średni czas [ms] | Approx - średni czas [ms] |")
    lines.append("|----|--------------------------|---------------------------|")
    
    n2_groups = defaultdict(list)
    for r in exact + approx:
        n2_groups[r.n2].append(r)
    
    for n2 in sorted(n2_groups.keys()):
        exact_n2 = [r for r in exact if r.n2 == n2]
        approx_n2 = [r for r in approx if r.n2 == n2]
        exact_avg = statistics.mean([r.time_ms for r in exact_n2]) if exact_n2 else 0
        approx_avg = statistics.mean([r.time_ms for r in approx_n2]) if approx_n2 else 0
        lines.append(f"| {n2} | {exact_avg:.2f} | {approx_avg:.2f} |")
    lines.append("")
    
    # Skalowanie względem k
    lines.append("### 3.3. Wpływ k (liczba kopii)")
    lines.append("")
    lines.append("| k | Exact - średni czas [ms] | Approx - średni czas [ms] |")
    lines.append("|----|--------------------------|---------------------------|")
    
    k_groups = defaultdict(list)
    for r in exact + approx:
        k_groups[r.k].append(r)
    
    for k in sorted(k_groups.keys()):
        exact_k = [r for r in exact if r.k == k]
        approx_k = [r for r in approx if r.k == k]
        exact_avg = statistics.mean([r.time_ms for r in exact_k]) if exact_k else 0
        approx_avg = statistics.mean([r.time_ms for r in approx_k]) if approx_k else 0
        lines.append(f"| {k} | {exact_avg:.2f} | {approx_avg:.2f} |")
    lines.append("")
    
    # Wnioski
    lines.append("## 4. Wnioski")
    lines.append("")
    
    if common_keys and time_ratios:
        avg_speedup = statistics.mean(time_ratios)
        if avg_speedup > 1.0:
            lines.append(f"- Algorytm Approximate jest średnio **{avg_speedup:.2f}x szybszy** niż Exact")
        else:
            lines.append(f"- Algorytm Approximate jest średnio **{1/avg_speedup:.2f}x wolniejszy** niż Exact")
    
    if common_keys and cost_ratios:
        avg_cost_ratio = statistics.mean(cost_ratios)
        if avg_cost_ratio <= 1.1:
            lines.append(f"- Algorytm Approximate znajduje rozwiązania **bardzo bliskie optymalnym** (średnio {avg_cost_ratio:.2f}x kosztu Exact)")
        elif avg_cost_ratio <= 1.5:
            lines.append(f"- Algorytm Approximate znajduje rozwiązania **akceptowalne** (średnio {avg_cost_ratio:.2f}x kosztu Exact)")
        else:
            lines.append(f"- Algorytm Approximate znajduje rozwiązania **znacznie gorsze** (średnio {avg_cost_ratio:.2f}x kosztu Exact)")
    
    if common_keys:
        optimal_count = sum(1 for r in cost_ratios if r == 1.0)
        lines.append(f"- Approximate znajduje rozwiązanie optymalne w **{100*optimal_count/len(common_keys):.1f}%** przypadków")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Sprawozdanie wygenerowane automatycznie przez generate_report.py*")
    
    # Zapisz do pliku
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    
    print(f"Sprawozdanie zapisane do: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate Test Report")
    parser.add_argument('--input', type=str, default='performance_results/results.json',
                       help="Input JSON file with test results")
    parser.add_argument('--output', type=str, default='performance_results/report.md',
                       help="Output Markdown file for report")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Błąd: Plik {args.input} nie istnieje!")
        print("Uruchom najpierw performance_tests.py aby wygenerować dane.")
        return
    
    results = load_results(args.input)
    print(f"Wczytano {len(results)} wyników testów")
    
    generate_markdown_report(results, args.output)

if __name__ == "__main__":
    from collections import defaultdict
    main()

