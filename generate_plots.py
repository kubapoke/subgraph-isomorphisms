#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WYKRESY WYDAJNOŚCI
==================
Generuje wykresy pokazujące zależności wydajności od parametrów wejściowych.
"""

import json
import os
import argparse
from typing import List, Dict, Tuple
from collections import defaultdict
from dataclasses import dataclass

IMPORT_ERROR = None
try:
    import numpy as np
    import matplotlib.pyplot as plt
    # Konfiguracja matplotlib dla polskich znaków
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['figure.figsize'] = (14, 10)
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 13
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 11
    plt.rcParams['figure.dpi'] = 100
    HAS_PLOTTING = True
except ImportError as e:
    HAS_PLOTTING = False
    np = None
    plt = None
    IMPORT_ERROR = str(e)

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

def filter_valid_results(results: List[TestResult]) -> Tuple[List[TestResult], List[TestResult]]:
    """Dzieli wyniki na exact i approx, filtruje tylko te z rozwiązaniem"""
    exact = [r for r in results if r.algorithm == 'exact' and r.found and r.cost is not None]
    approx = [r for r in results if r.algorithm == 'approx' and r.found and r.cost is not None]
    return exact, approx

def plot_time_vs_n1(results: List[TestResult], output_dir: str):
    """Wykres: czas vs n1 - pokazuje WSZYSTKIE dane, agregowane trendy"""
    exact, approx = filter_valid_results(results)
    
    if not exact and not approx:
        print("Brak danych do wykresu time_vs_n1")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Czas wykonania vs n1 (rozmiar grafu G1) - wszystkie dane', fontsize=16, fontweight='bold')
    
    # Wykres 1: Wszystkie punkty (Exact vs Approx) - agregowane po n1
    ax = axes[0, 0]
    if exact:
        exact_n1_all = [r.n1 for r in exact]
        exact_times_all = [r.time_ms for r in exact]
        ax.scatter(exact_n1_all, exact_times_all, alpha=0.5, s=60, color='#2E86AB', marker='o', 
                  edgecolors='#1B4F72', linewidths=0.3, zorder=1, label='Exact (wszystkie punkty)')
        
        # Agregowane średnie po n1
        n1_groups = {}
        for r in exact:
            if r.n1 not in n1_groups:
                n1_groups[r.n1] = []
            n1_groups[r.n1].append(r.time_ms)
        n1_vals = sorted(n1_groups.keys())
        exact_means = [np.mean(n1_groups[n1]) for n1 in n1_vals]
        exact_stds = [np.std(n1_groups[n1]) for n1 in n1_vals]
        ax.errorbar(n1_vals, exact_means, yerr=exact_stds, fmt='o-', label='Exact (średnia±σ)', 
                   linewidth=3, markersize=10, capsize=5, capthick=2, color='#1B4F72', zorder=3)
        
        # Trend line
        if len(n1_vals) > 2:
            z = np.polyfit(exact_n1_all, exact_times_all, 1)
            p = np.poly1d(z)
            x_trend = np.linspace(min(exact_n1_all), max(exact_n1_all), 100)
            ax.plot(x_trend, p(x_trend), '--', color='#1B4F72', alpha=0.6, linewidth=2, 
                   label=f'Exact trend (slope={z[0]:.2f})', zorder=2)
    
    if approx:
        approx_n1_all = [r.n1 for r in approx]
        approx_times_all = [r.time_ms for r in approx]
        ax.scatter(approx_n1_all, approx_times_all, alpha=0.5, s=60, color='#F77F00', marker='s', 
                  edgecolors='#D62828', linewidths=0.3, zorder=1, label='Approx (wszystkie punkty)')
        
        # Agregowane średnie po n1
        n1_groups = {}
        for r in approx:
            if r.n1 not in n1_groups:
                n1_groups[r.n1] = []
            n1_groups[r.n1].append(r.time_ms)
        n1_vals = sorted(n1_groups.keys())
        approx_means = [np.mean(n1_groups[n1]) for n1 in n1_vals]
        approx_stds = [np.std(n1_groups[n1]) for n1 in n1_vals]
        ax.errorbar(n1_vals, approx_means, yerr=approx_stds, fmt='s-', label='Approx (średnia±σ)', 
                   linewidth=3, markersize=10, capsize=5, capthick=2, color='#D62828', zorder=3)
        
        # Trend line
        if len(n1_vals) > 2:
            z = np.polyfit(approx_n1_all, approx_times_all, 1)
            p = np.poly1d(z)
            x_trend = np.linspace(min(approx_n1_all), max(approx_n1_all), 100)
            ax.plot(x_trend, p(x_trend), '--', color='#D62828', alpha=0.6, linewidth=2, 
                   label=f'Approx trend (slope={z[0]:.2f})', zorder=2)
    
    ax.set_xlabel('n1 (liczba wierzchołków G1)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Czas [ms]', fontsize=12, fontweight='bold')
    ax.set_title('Wszystkie dane - agregowane po n1', fontsize=13, fontweight='bold', pad=10)
    ax.legend(loc='best', framealpha=0.9, fancybox=True, shadow=True, fontsize=9)
    ax.grid(True, alpha=0.4, linestyle='--', linewidth=0.5)
    ax.set_yscale('log')
    ax.set_facecolor('#FAFAFA')
    
    # Wykres 2-4: Dla wybranych (n2, k) - tylko jeśli mają różne n1
    scenarios = set((r.n2, r.k) for r in exact + approx)
    scenarios_with_variety = []
    for n2, k in scenarios:
        n1_vals = set(r.n1 for r in exact + approx if r.n2 == n2 and r.k == k)
        if len(n1_vals) > 1:  # Tylko scenariusze z różnymi n1
            scenarios_with_variety.append((n2, k, len(n1_vals)))
    scenarios_with_variety.sort(key=lambda x: x[2], reverse=True)  # Sortuj po liczbie różnych n1
    
    for idx, (n2, k, _) in enumerate(scenarios_with_variety[:3]):  # Top 3 scenariusze
        ax = axes[(idx + 1) // 2, (idx + 1) % 2]
        
        exact_subset = [r for r in exact if r.n2 == n2 and r.k == k]
        approx_subset = [r for r in approx if r.n2 == n2 and r.k == k]
        
        # Pokaż wszystkie punkty danych + średnie + trend
        if exact_subset:
            # Wszystkie punkty (większe, bardziej widoczne)
            exact_n1_all = [r.n1 for r in exact_subset]
            exact_times_all = [r.time_ms for r in exact_subset]
            ax.scatter(exact_n1_all, exact_times_all, alpha=0.6, s=100, color='#2E86AB', marker='o', 
                      edgecolors='#1B4F72', linewidths=0.5, zorder=1, label='Exact (punkty)')
            
            # Średnie z error bars
            n1_vals = sorted(set(r.n1 for r in exact_subset))
            exact_times = []
            exact_stds = []
            for n1 in n1_vals:
                times = [r.time_ms for r in exact_subset if r.n1 == n1]
                if times:
                    exact_times.append(np.mean(times))
                    exact_stds.append(np.std(times) if len(times) > 1 else 0)
                else:
                    exact_times.append(0)
                    exact_stds.append(0)
            ax.errorbar(n1_vals, exact_times, yerr=exact_stds, fmt='o-', label='Exact (średnia±σ)', 
                       linewidth=3, markersize=10, capsize=5, capthick=2, color='#1B4F72', zorder=3)
            
            # Trend line (regresja)
            if len(n1_vals) > 2:
                z = np.polyfit(exact_n1_all, exact_times_all, 1)
                p = np.poly1d(z)
                x_trend = np.linspace(min(exact_n1_all), max(exact_n1_all), 100)
                ax.plot(x_trend, p(x_trend), '--', color='#1B4F72', alpha=0.5, linewidth=2, 
                       label=f'Exact trend (slope={z[0]:.2f})', zorder=2)
        
        if approx_subset:
            # Wszystkie punkty
            approx_n1_all = [r.n1 for r in approx_subset]
            approx_times_all = [r.time_ms for r in approx_subset]
            ax.scatter(approx_n1_all, approx_times_all, alpha=0.6, s=100, color='#F77F00', marker='s', 
                      edgecolors='#D62828', linewidths=0.5, zorder=1, label='Approx (punkty)')
            
            # Średnie z error bars
            n1_vals = sorted(set(r.n1 for r in approx_subset))
            approx_times = []
            approx_stds = []
            for n1 in n1_vals:
                times = [r.time_ms for r in approx_subset if r.n1 == n1]
                if times:
                    approx_times.append(np.mean(times))
                    approx_stds.append(np.std(times) if len(times) > 1 else 0)
                else:
                    approx_times.append(0)
                    approx_stds.append(0)
            ax.errorbar(n1_vals, approx_times, yerr=approx_stds, fmt='s-', label='Approx (średnia±σ)', 
                       linewidth=3, markersize=10, capsize=5, capthick=2, color='#D62828', zorder=3)
            
            # Trend line
            if len(n1_vals) > 2:
                z = np.polyfit(approx_n1_all, approx_times_all, 1)
                p = np.poly1d(z)
                x_trend = np.linspace(min(approx_n1_all), max(approx_n1_all), 100)
                ax.plot(x_trend, p(x_trend), '--', color='#D62828', alpha=0.5, linewidth=2, 
                       label=f'Approx trend (slope={z[0]:.2f})', zorder=2)
        
        ax.set_xlabel('n1 (liczba wierzchołków G1)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Czas [ms]', fontsize=12, fontweight='bold')
        ax.set_title(f'n2={n2}, k={k}', fontsize=13, fontweight='bold', pad=10)
        ax.legend(loc='best', framealpha=0.9, fancybox=True, shadow=True)
        ax.grid(True, alpha=0.4, linestyle='--', linewidth=0.5)
        ax.set_yscale('log')
        ax.set_facecolor('#FAFAFA')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'time_vs_n1.png'), dpi=300, bbox_inches='tight')
    print(f"Zapisano: time_vs_n1.png")
    plt.close()

def plot_time_vs_n2(results: List[TestResult], output_dir: str):
    """Wykres: czas vs n2 (dla różnych n1, k)"""
    exact, approx = filter_valid_results(results)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Czas wykonania vs n2 (rozmiar grafu G2)', fontsize=16, fontweight='bold')
    
    scenarios = set((r.n1, r.k) for r in exact + approx)
    
    for idx, (n1, k) in enumerate(sorted(scenarios)[:4]):
        ax = axes[idx // 2, idx % 2]
        
        exact_subset = [r for r in exact if r.n1 == n1 and r.k == k]
        approx_subset = [r for r in approx if r.n1 == n1 and r.k == k]
        
        # Pokaż wszystkie punkty danych + średnie + trend
        if exact_subset:
            exact_n2_all = [r.n2 for r in exact_subset]
            exact_times_all = [r.time_ms for r in exact_subset]
            ax.scatter(exact_n2_all, exact_times_all, alpha=0.6, s=100, color='#2E86AB', marker='o', 
                      edgecolors='#1B4F72', linewidths=0.5, zorder=1, label='Exact (punkty)')
            
            n2_vals = sorted(set(r.n2 for r in exact_subset))
            exact_times = []
            exact_stds = []
            for n2 in n2_vals:
                times = [r.time_ms for r in exact_subset if r.n2 == n2]
                if times:
                    exact_times.append(np.mean(times))
                    exact_stds.append(np.std(times) if len(times) > 1 else 0)
                else:
                    exact_times.append(0)
                    exact_stds.append(0)
            ax.errorbar(n2_vals, exact_times, yerr=exact_stds, fmt='o-', label='Exact (średnia±σ)', 
                       linewidth=3, markersize=10, capsize=5, capthick=2, color='#1B4F72', zorder=3)
            
            if len(n2_vals) > 2:
                z = np.polyfit(exact_n2_all, exact_times_all, 1)
                p = np.poly1d(z)
                x_trend = np.linspace(min(exact_n2_all), max(exact_n2_all), 100)
                ax.plot(x_trend, p(x_trend), '--', color='#1B4F72', alpha=0.5, linewidth=2, 
                       label=f'Exact trend (slope={z[0]:.2f})', zorder=2)
        
        if approx_subset:
            approx_n2_all = [r.n2 for r in approx_subset]
            approx_times_all = [r.time_ms for r in approx_subset]
            ax.scatter(approx_n2_all, approx_times_all, alpha=0.6, s=100, color='#F77F00', marker='s', 
                      edgecolors='#D62828', linewidths=0.5, zorder=1, label='Approx (punkty)')
            
            n2_vals = sorted(set(r.n2 for r in approx_subset))
            approx_times = []
            approx_stds = []
            for n2 in n2_vals:
                times = [r.time_ms for r in approx_subset if r.n2 == n2]
                if times:
                    approx_times.append(np.mean(times))
                    approx_stds.append(np.std(times) if len(times) > 1 else 0)
                else:
                    approx_times.append(0)
                    approx_stds.append(0)
            ax.errorbar(n2_vals, approx_times, yerr=approx_stds, fmt='s-', label='Approx (średnia±σ)', 
                       linewidth=3, markersize=10, capsize=5, capthick=2, color='#D62828', zorder=3)
            
            if len(n2_vals) > 2:
                z = np.polyfit(approx_n2_all, approx_times_all, 1)
                p = np.poly1d(z)
                x_trend = np.linspace(min(approx_n2_all), max(approx_n2_all), 100)
                ax.plot(x_trend, p(x_trend), '--', color='#D62828', alpha=0.5, linewidth=2, 
                       label=f'Approx trend (slope={z[0]:.2f})', zorder=2)
        
        ax.set_xlabel('n2 (liczba wierzchołków G2)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Czas [ms]', fontsize=12, fontweight='bold')
        ax.set_title(f'n1={n1}, k={k}', fontsize=13, fontweight='bold', pad=10)
        ax.legend(loc='best', framealpha=0.9, fancybox=True, shadow=True)
        ax.grid(True, alpha=0.4, linestyle='--', linewidth=0.5)
        ax.set_yscale('log')
        ax.set_facecolor('#FAFAFA')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'time_vs_n2.png'), dpi=300, bbox_inches='tight')
    print(f"Zapisano: time_vs_n2.png")
    plt.close()

def plot_time_vs_k(results: List[TestResult], output_dir: str):
    """Wykres: czas vs k (liczba kopii)"""
    exact, approx = filter_valid_results(results)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Czas wykonania vs k (liczba kopii)', fontsize=16, fontweight='bold')
    
    scenarios = set((r.n1, r.n2) for r in exact + approx)
    
    for idx, (n1, n2) in enumerate(sorted(scenarios)[:4]):
        ax = axes[idx // 2, idx % 2]
        
        exact_subset = [r for r in exact if r.n1 == n1 and r.n2 == n2]
        approx_subset = [r for r in approx if r.n1 == n1 and r.n2 == n2]
        
        # Pokaż wszystkie punkty danych + średnie + trend
        if exact_subset:
            exact_k_all = [r.k for r in exact_subset]
            exact_times_all = [r.time_ms for r in exact_subset]
            ax.scatter(exact_k_all, exact_times_all, alpha=0.6, s=100, color='#2E86AB', marker='o', 
                      edgecolors='#1B4F72', linewidths=0.5, zorder=1, label='Exact (punkty)')
            
            k_vals = sorted(set(r.k for r in exact_subset))
            exact_times = []
            exact_stds = []
            for k in k_vals:
                times = [r.time_ms for r in exact_subset if r.k == k]
                if times:
                    exact_times.append(np.mean(times))
                    exact_stds.append(np.std(times) if len(times) > 1 else 0)
                else:
                    exact_times.append(0)
                    exact_stds.append(0)
            ax.errorbar(k_vals, exact_times, yerr=exact_stds, fmt='o-', label='Exact (średnia±σ)', 
                       linewidth=3, markersize=10, capsize=5, capthick=2, color='#1B4F72', zorder=3)
            
            if len(k_vals) > 2:
                z = np.polyfit(exact_k_all, exact_times_all, 1)
                p = np.poly1d(z)
                x_trend = np.linspace(min(exact_k_all), max(exact_k_all), 100)
                ax.plot(x_trend, p(x_trend), '--', color='#1B4F72', alpha=0.5, linewidth=2, 
                       label=f'Exact trend (slope={z[0]:.2f})', zorder=2)
        
        if approx_subset:
            approx_k_all = [r.k for r in approx_subset]
            approx_times_all = [r.time_ms for r in approx_subset]
            ax.scatter(approx_k_all, approx_times_all, alpha=0.6, s=100, color='#F77F00', marker='s', 
                      edgecolors='#D62828', linewidths=0.5, zorder=1, label='Approx (punkty)')
            
            k_vals = sorted(set(r.k for r in approx_subset))
            approx_times = []
            approx_stds = []
            for k in k_vals:
                times = [r.time_ms for r in approx_subset if r.k == k]
                if times:
                    approx_times.append(np.mean(times))
                    approx_stds.append(np.std(times) if len(times) > 1 else 0)
                else:
                    approx_times.append(0)
                    approx_stds.append(0)
            ax.errorbar(k_vals, approx_times, yerr=approx_stds, fmt='s-', label='Approx (średnia±σ)', 
                       linewidth=3, markersize=10, capsize=5, capthick=2, color='#D62828', zorder=3)
            
            if len(k_vals) > 2:
                z = np.polyfit(approx_k_all, approx_times_all, 1)
                p = np.poly1d(z)
                x_trend = np.linspace(min(approx_k_all), max(approx_k_all), 100)
                ax.plot(x_trend, p(x_trend), '--', color='#D62828', alpha=0.5, linewidth=2, 
                       label=f'Approx trend (slope={z[0]:.2f})', zorder=2)
        
        ax.set_xlabel('k (liczba kopii)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Czas [ms]', fontsize=12, fontweight='bold')
        ax.set_title(f'n1={n1}, n2={n2}', fontsize=13, fontweight='bold', pad=10)
        ax.legend(loc='best', framealpha=0.9, fancybox=True, shadow=True)
        ax.grid(True, alpha=0.4, linestyle='--', linewidth=0.5)
        ax.set_yscale('log')
        ax.set_facecolor('#FAFAFA')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'time_vs_k.png'), dpi=300, bbox_inches='tight')
    print(f"Zapisano: time_vs_k.png")
    plt.close()

def plot_comparison_exact_vs_approx(results: List[TestResult], output_dir: str):
    """Wykres porównawczy: exact vs approx (czas i koszt)"""
    exact, approx = filter_valid_results(results)
    
    # Znajdź wspólne testy (te same n1, n2, k)
    exact_dict = {(r.n1, r.n2, r.k): r for r in exact}
    approx_dict = {(r.n1, r.n2, r.k): r for r in approx}
    
    common_keys = set(exact_dict.keys()) & set(approx_dict.keys())
    
    if not common_keys:
        print("Brak wspólnych testów do porównania")
        return
    
    # Porównanie czasu
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    exact_times = [exact_dict[k].time_ms for k in common_keys]
    approx_times = [approx_dict[k].time_ms for k in common_keys]
    
    # Wykres czasu
    ax1.scatter(exact_times, approx_times, alpha=0.7, s=150, color='#2E86AB', 
               edgecolors='#1B4F72', linewidths=1, zorder=2)
    max_time = max(max(exact_times), max(approx_times))
    ax1.plot([0, max_time], [0, max_time], 'r--', label='y=x (równe czasy)', linewidth=3, zorder=1)
    ax1.set_xlabel('Czas Exact [ms]', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Czas Approx [ms]', fontsize=13, fontweight='bold')
    ax1.set_title('Porównanie czasu wykonania', fontsize=15, fontweight='bold', pad=15)
    ax1.legend(loc='best', framealpha=0.9, fancybox=True, shadow=True, fontsize=11)
    ax1.grid(True, alpha=0.4, linestyle='--', linewidth=0.5)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_facecolor('#FAFAFA')
    
    # Porównanie kosztu
    exact_costs = [exact_dict[k].cost for k in common_keys]
    approx_costs = [approx_dict[k].cost for k in common_keys]
    
    ax2.scatter(exact_costs, approx_costs, alpha=0.7, s=150, color='#F77F00', 
               edgecolors='#D62828', linewidths=1, zorder=2)
    max_cost = max(max(exact_costs), max(approx_costs))
    ax2.plot([0, max_cost], [0, max_cost], 'r--', label='y=x (równe koszty)', linewidth=3, zorder=1)
    ax2.set_xlabel('Koszt Exact', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Koszt Approx', fontsize=13, fontweight='bold')
    ax2.set_title('Porównanie kosztu rozszerzenia', fontsize=15, fontweight='bold', pad=15)
    ax2.legend(loc='best', framealpha=0.9, fancybox=True, shadow=True, fontsize=11)
    ax2.grid(True, alpha=0.4, linestyle='--', linewidth=0.5)
    ax2.set_facecolor('#FAFAFA')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'comparison_exact_vs_approx.png'), dpi=300, bbox_inches='tight')
    print(f"Zapisano: comparison_exact_vs_approx.png")
    plt.close()
    
    # Wykres stosunku czasów - ulepszony z box plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Przyspieszenie Approx względem Exact', fontsize=16, fontweight='bold')
    
    speedup_ratios = [exact_times[i] / approx_times[i] if approx_times[i] > 0 and np.isfinite(exact_times[i] / approx_times[i]) else None
                      for i in range(len(exact_times))]
    speedup_ratios = [r for r in speedup_ratios if r is not None]
    
    if speedup_ratios:
        # Box plot
        ax = axes[0]
        bp = ax.boxplot([speedup_ratios], labels=['Speedup'], patch_artist=True, widths=0.5)
        bp['boxes'][0].set_facecolor('lightgreen')
        ax.axhline(y=1, color='r', linestyle='--', linewidth=2, label='y=1 (równe czasy)')
        ax.set_ylabel('Stosunek czasu (Exact / Approx)', fontsize=12, fontweight='bold')
        ax.set_title('Box Plot', fontsize=13, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        # Histogram z lepszymi binami
        ax = axes[1]
        if len(set(speedup_ratios)) > 1:
            bins = np.linspace(min(speedup_ratios), max(speedup_ratios), min(30, len(speedup_ratios)))
            ax.hist(speedup_ratios, bins=bins, edgecolor='black', alpha=0.7, color='lightgreen')
        else:
            unique_val = speedup_ratios[0]
            ax.bar([unique_val], [len(speedup_ratios)], width=0.1, edgecolor='black', alpha=0.7, color='lightgreen')
        ax.axvline(x=1, color='r', linestyle='--', linewidth=2, label='x=1 (równe czasy)')
        ax.set_xlabel('Stosunek czasu (Exact / Approx)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Liczba testów', fontsize=12, fontweight='bold')
        ax.set_title('Histogram', fontsize=13, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        median_ratio = np.median(speedup_ratios)
        mean_ratio = np.mean(speedup_ratios)
        ax.text(0.02, 0.98, f'Mediana: {median_ratio:.3f}\nŚrednia: {mean_ratio:.3f}\nN={len(speedup_ratios)}', 
               transform=ax.transAxes, fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'speedup_ratio.png'), dpi=300, bbox_inches='tight')
    print(f"Zapisano: speedup_ratio.png")
    plt.close()
    
    # Wykres stosunku kosztów - ulepszony z box plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Jakość rozwiązania Approx względem Exact', fontsize=16, fontweight='bold')
    
    cost_ratios = [approx_costs[i] / exact_costs[i] if exact_costs[i] > 0 and np.isfinite(approx_costs[i] / exact_costs[i]) else None
                   for i in range(len(exact_costs))]
    cost_ratios = [r for r in cost_ratios if r is not None]
    
    if cost_ratios:
        # Box plot
        ax = axes[0]
        bp = ax.boxplot([cost_ratios], labels=['Cost Ratio'], patch_artist=True, widths=0.5)
        bp['boxes'][0].set_facecolor('lightcoral')
        ax.axhline(y=1, color='r', linestyle='--', linewidth=2, label='y=1 (równe koszty)')
        ax.set_ylabel('Stosunek kosztu (Approx / Exact)', fontsize=12, fontweight='bold')
        ax.set_title('Box Plot', fontsize=13, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        # Histogram z lepszymi binami
        ax = axes[1]
        if len(set(cost_ratios)) > 1:
            bins = np.linspace(min(cost_ratios), max(cost_ratios), min(30, len(cost_ratios)))
            ax.hist(cost_ratios, bins=bins, edgecolor='black', alpha=0.7, color='lightcoral')
        else:
            unique_val = cost_ratios[0]
            ax.bar([unique_val], [len(cost_ratios)], width=0.1, edgecolor='black', alpha=0.7, color='lightcoral')
        ax.axvline(x=1, color='r', linestyle='--', linewidth=2, label='x=1 (równe koszty)')
        ax.set_xlabel('Stosunek kosztu (Approx / Exact)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Liczba testów', fontsize=12, fontweight='bold')
        ax.set_title('Histogram', fontsize=13, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        median_ratio = np.median(cost_ratios)
        mean_ratio = np.mean(cost_ratios)
        ax.text(0.02, 0.98, f'Mediana: {median_ratio:.3f}\nŚrednia: {mean_ratio:.3f}\nN={len(cost_ratios)}', 
               transform=ax.transAxes, fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'cost_ratio.png'), dpi=300, bbox_inches='tight')
    print(f"Zapisano: cost_ratio.png")
    plt.close()

# Wykresy 3D usunięte - były mało czytelne, używamy heatmap zamiast tego

def main():
    parser = argparse.ArgumentParser(description="Generate Performance Plots")
    parser.add_argument('--input', type=str, default='performance_results/results.json',
                       help="Input JSON file with test results")
    parser.add_argument('--output', type=str, default='performance_results/plots',
                       help="Output directory for plots")
    
    args = parser.parse_args()
    
    if not HAS_PLOTTING:
        print("Błąd: Brak bibliotek matplotlib/numpy!")
        print(f"Szczegóły błędu: {IMPORT_ERROR}")
        print("\nAby zainstalować:")
        print("  python -m pip install matplotlib numpy")
        print("\nLub jeśli używasz innego interpretera:")
        print("  py -3.13 -m pip install matplotlib numpy")
        print("  (jeśli masz Python 3.13)")
        return 1
    
    if not os.path.exists(args.input):
        print(f"Błąd: Plik {args.input} nie istnieje!")
        print("Uruchom najpierw performance_tests.py aby wygenerować dane.")
        return 1
    
    os.makedirs(args.output, exist_ok=True)
    
    print("=" * 80)
    print("GENEROWANIE WYKRESÓW WYDAJNOŚCI")
    print("=" * 80)
    
    results = load_results(args.input)
    print(f"Wczytano {len(results)} wyników testów")
    
    exact, approx = filter_valid_results(results)
    print(f"  - Exact:  {len(exact)} poprawnych wyników")
    print(f"  - Approx: {len(approx)} poprawnych wyników")
    print()
    
    if len(exact) == 0 and len(approx) == 0:
        print("UWAGA: Brak poprawnych wyników do wygenerowania wykresów!")
        print("Wszystkie testy zwróciły NO_SOL. Spróbuj użyć istniejących testów z katalogu tests/")
        return 1
    
    print("Generowanie wykresów...")
    plot_time_vs_n1(results, args.output)
    plot_time_vs_n2(results, args.output)
    plot_time_vs_k(results, args.output)
    plot_comparison_exact_vs_approx(results, args.output)
    
    # Heatmapa (uśredniona po k) - import z generate_plots_improved
    try:
        import sys
        import importlib.util
        spec = importlib.util.spec_from_file_location("generate_plots_improved", "generate_plots_improved.py")
        if spec and spec.loader:
            improved_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(improved_module)
            improved_module.plot_heatmap_time(results, args.output)
    except Exception as e:
        print(f"UWAGA: Nie udało się wygenerować heatmapy: {e}")
        print("      (Użyj generate_plots_improved.py aby wygenerować heatmapy)")
    
    # Wykresy 3D usunięte - używamy heatmap zamiast tego (są bardziej czytelne)
    
    print("\n" + "=" * 80)
    print(f"Wszystkie wykresy zapisane w: {args.output}")
    print("=" * 80)
    return 0

if __name__ == "__main__":
    main()

