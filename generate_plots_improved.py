#!/usr/bin/env python3.13
# -*- coding: utf-8 -*-
"""
ULEPSZONE WYKRESY WYDAJNOŚCI
============================
Generuje bardziej czytelne i informacyjne wykresy wydajności.
"""

import json
import os
import argparse
from typing import List, Dict, Tuple
from collections import defaultdict
from dataclasses import dataclass

try:
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from mpl_toolkits.mplot3d import Axes3D
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['figure.figsize'] = (14, 10)
    HAS_PLOTTING = True
    IMPORT_ERROR = None
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
        filtered = {k: v for k, v in r.items() 
                   if k in ['n1', 'n2', 'k', 'algorithm', 'time_ms', 'cost', 'found']}
        results.append(TestResult(**filtered))
    return results

def filter_valid_results(results: List[TestResult]) -> Tuple[List[TestResult], List[TestResult]]:
    """Dzieli wyniki na exact i approx, filtruje tylko te z rozwiązaniem"""
    exact = [r for r in results if r.algorithm == 'exact' and r.found and r.cost is not None]
    approx = [r for r in results if r.algorithm == 'approx' and r.found and r.cost is not None]
    return exact, approx

def plot_time_vs_parameter_scatter(results: List[TestResult], output_dir: str):
    """Wykres scatter: czas vs parametry - pokazuje wszystkie punkty danych"""
    exact, approx = filter_valid_results(results)
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Czas wykonania vs parametry wejściowe (wszystkie punkty danych)', 
                 fontsize=16, fontweight='bold')
    
    # n1 vs czas
    ax = axes[0, 0]
    if exact:
        exact_n1 = [r.n1 for r in exact]
        exact_times = [r.time_ms for r in exact]
        ax.scatter(exact_n1, exact_times, alpha=0.6, s=80, label='Exact', color='blue', marker='o')
    if approx:
        approx_n1 = [r.n1 for r in approx]
        approx_times = [r.time_ms for r in approx]
        ax.scatter(approx_n1, approx_times, alpha=0.6, s=80, label='Approx', color='orange', marker='s')
    ax.set_xlabel('n1 (liczba wierzchołków G1)', fontsize=11)
    ax.set_ylabel('Czas [ms]', fontsize=11)
    ax.set_title('Czas vs n1', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    
    # n2 vs czas
    ax = axes[0, 1]
    if exact:
        exact_n2 = [r.n2 for r in exact]
        exact_times = [r.time_ms for r in exact]
        ax.scatter(exact_n2, exact_times, alpha=0.6, s=80, label='Exact', color='blue', marker='o')
    if approx:
        approx_n2 = [r.n2 for r in approx]
        approx_times = [r.time_ms for r in approx]
        ax.scatter(approx_n2, approx_times, alpha=0.6, s=80, label='Approx', color='orange', marker='s')
    ax.set_xlabel('n2 (liczba wierzchołków G2)', fontsize=11)
    ax.set_ylabel('Czas [ms]', fontsize=11)
    ax.set_title('Czas vs n2', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    
    # k vs czas
    ax = axes[0, 2]
    if exact:
        exact_k = [r.k for r in exact]
        exact_times = [r.time_ms for r in exact]
        ax.scatter(exact_k, exact_times, alpha=0.6, s=80, label='Exact', color='blue', marker='o')
    if approx:
        approx_k = [r.k for r in approx]
        approx_times = [r.time_ms for r in approx]
        ax.scatter(approx_k, approx_times, alpha=0.6, s=80, label='Approx', color='orange', marker='s')
    ax.set_xlabel('k (liczba kopii)', fontsize=11)
    ax.set_ylabel('Czas [ms]', fontsize=11)
    ax.set_title('Czas vs k', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    
    # Box plots dla n1
    ax = axes[1, 0]
    if exact or approx:
        data_to_plot = []
        labels = []
        n1_vals = sorted(set(r.n1 for r in exact + approx))
        for n1 in n1_vals:
            exact_times_n1 = [r.time_ms for r in exact if r.n1 == n1]
            approx_times_n1 = [r.time_ms for r in approx if r.n1 == n1]
            if exact_times_n1:
                data_to_plot.append(exact_times_n1)
                labels.append(f'E{n1}')
            if approx_times_n1:
                data_to_plot.append(approx_times_n1)
                labels.append(f'A{n1}')
        if data_to_plot:
            bp = ax.boxplot(data_to_plot, tick_labels=labels, patch_artist=True)
            for patch, color in zip(bp['boxes'], ['lightblue' if 'E' in l else 'lightcoral' for l in labels]):
                patch.set_facecolor(color)
            ax.set_ylabel('Czas [ms]', fontsize=11)
            ax.set_title('Rozkład czasu dla różnych n1', fontsize=12, fontweight='bold')
            ax.set_yscale('log')
            ax.grid(True, alpha=0.3, axis='y')
    
    # Box plots dla n2
    ax = axes[1, 1]
    if exact or approx:
        data_to_plot = []
        labels = []
        n2_vals = sorted(set(r.n2 for r in exact + approx))[:10]  # Max 10 wartości
        for n2 in n2_vals:
            exact_times_n2 = [r.time_ms for r in exact if r.n2 == n2]
            approx_times_n2 = [r.time_ms for r in approx if r.n2 == n2]
            if exact_times_n2:
                data_to_plot.append(exact_times_n2)
                labels.append(f'E{n2}')
            if approx_times_n2:
                data_to_plot.append(approx_times_n2)
                labels.append(f'A{n2}')
        if data_to_plot:
            bp = ax.boxplot(data_to_plot, tick_labels=labels, patch_artist=True)
            for patch, color in zip(bp['boxes'], ['lightblue' if 'E' in l else 'lightcoral' for l in labels]):
                patch.set_facecolor(color)
            ax.set_ylabel('Czas [ms]', fontsize=11)
            ax.set_title('Rozkład czasu dla różnych n2', fontsize=12, fontweight='bold')
            ax.set_yscale('log')
            ax.tick_params(axis='x', rotation=45)
            ax.grid(True, alpha=0.3, axis='y')
    
    # Box plots dla k
    ax = axes[1, 2]
    if exact or approx:
        data_to_plot = []
        labels = []
        k_vals = sorted(set(r.k for r in exact + approx))
        for k in k_vals:
            exact_times_k = [r.time_ms for r in exact if r.k == k]
            approx_times_k = [r.time_ms for r in approx if r.k == k]
            if exact_times_k:
                data_to_plot.append(exact_times_k)
                labels.append(f'E{k}')
            if approx_times_k:
                data_to_plot.append(approx_times_k)
                labels.append(f'A{k}')
        if data_to_plot:
            bp = ax.boxplot(data_to_plot, tick_labels=labels, patch_artist=True)
            for patch, color in zip(bp['boxes'], ['lightblue' if 'E' in l else 'lightcoral' for l in labels]):
                patch.set_facecolor(color)
            ax.set_ylabel('Czas [ms]', fontsize=11)
            ax.set_title('Rozkład czasu dla różnych k', fontsize=12, fontweight='bold')
            ax.set_yscale('log')
            ax.grid(True, alpha=0.3, axis='y')
    
    # Legenda z wyjaśnieniem etykiet
    blue_patch = mpatches.Patch(color='lightblue', label='Exact (E = Exact)')
    red_patch = mpatches.Patch(color='lightcoral', label='Approx (A = Approx)')
    fig.legend(handles=[blue_patch, red_patch], loc='upper right', 
              title='Legenda:\nE3 = Exact dla n1=3\nA3 = Approx dla n1=3\n(itd. dla n2, k)')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'time_vs_parameters_scatter.png'), dpi=300, bbox_inches='tight')
    print(f"Zapisano: time_vs_parameters_scatter.png")
    plt.close()

def plot_heatmap_time(results: List[TestResult], output_dir: str):
    """Heatmapa pokazująca średni czas dla różnych kombinacji n1, n2 - uśrednione po k"""
    exact, approx = filter_valid_results(results)
    
    for alg_name, subset in [('exact', exact), ('approx', approx)]:
        if not subset:
            continue
        
        # Przygotuj dane - uśrednij po k dla każdego (n1, n2)
        n1_vals = sorted(set(r.n1 for r in subset))
        n2_vals = sorted(set(r.n2 for r in subset))
        
        # Zbierz wszystkie czasy dla każdego (n1, n2) - uśrednij po k
        data_dict = {}  # (n1, n2) -> lista czasów
        for r in subset:
            key = (r.n1, r.n2)
            if key not in data_dict:
                data_dict[key] = []
            data_dict[key].append(r.time_ms)
        
        # Utwórz macierz
        heatmap_data = np.zeros((len(n2_vals), len(n1_vals)))
        counts = np.zeros((len(n2_vals), len(n1_vals)))
        
        for (n1, n2), times in data_dict.items():
            if n1 in n1_vals and n2 in n2_vals:
                i = n2_vals.index(n2)
                j = n1_vals.index(n1)
                heatmap_data[i, j] = np.mean(times)  # Średnia po wszystkich k
                counts[i, j] = len(times)
        
        # Oznacz brakujące dane
        heatmap_data[counts == 0] = np.nan
        
        # Sprawdź czy są jakieś dane
        if np.all(np.isnan(heatmap_data)):
            print(f"UWAGA: Brak danych do heatmapy dla {alg_name}")
            continue
        
        # Wykres
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Oblicz min/max (pomijając NaN)
        vmin_val = np.nanmin(heatmap_data)
        vmax_val = np.nanmax(heatmap_data)
        
        # Jeśli wszystkie wartości są takie same, dodaj mały zakres
        if vmin_val == vmax_val:
            vmin_val = max(0, vmin_val - 1)
            vmax_val = vmax_val + 1
        
        # Dla exact użyj logarytmicznej skali kolorów, dla approx liniowej
        if alg_name == 'exact' and vmax_val > vmin_val * 10:
            # Logarytmiczna skala dla exact (jeśli zakres > 10x)
            from matplotlib.colors import LogNorm
            norm = LogNorm(vmin=max(1, vmin_val), vmax=vmax_val)
            im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto', interpolation='nearest', norm=norm)
        else:
            # Liniowa skala dla approx lub małych zakresów
            im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto', interpolation='nearest', 
                          vmin=vmin_val, vmax=vmax_val)
        
        # Etykiety
        ax.set_xticks(range(len(n1_vals)))
        ax.set_xticklabels(n1_vals, fontsize=10)
        ax.set_yticks(range(len(n2_vals)))
        ax.set_yticklabels(n2_vals, fontsize=10)
        
        ax.set_xlabel('n1 (liczba wierzchołków G1)', fontsize=13, fontweight='bold')
        ax.set_ylabel('n2 (liczba wierzchołków G2)', fontsize=13, fontweight='bold')
        scale_note = " (skala logarytmiczna)" if alg_name == 'exact' and vmax_val > vmin_val * 10 else ""
        ax.set_title(f'Średni czas wykonania [ms] - {alg_name.upper()}{scale_note}\n(uśrednione po k, białe = brak danych)', 
                    fontsize=15, fontweight='bold', pad=15)
        
        # Dodaj wartości w komórkach (tylko dla istniejących danych)
        for i in range(len(n2_vals)):
            for j in range(len(n1_vals)):
                if not np.isnan(heatmap_data[i, j]):
                    # Wybierz kolor tekstu w zależności od jasności tła
                    val = heatmap_data[i, j]
                    max_val = np.nanmax(heatmap_data)
                    text_color = 'white' if val > max_val * 0.6 else 'black'
                    text = ax.text(j, i, f'{heatmap_data[i, j]:.0f}',
                                 ha="center", va="center", color=text_color, fontsize=9, fontweight='bold')
        
        # Dodaj informację o liczbie punktów danych
        total_points = len(subset)
        ax.text(0.02, 0.98, f'Łącznie punktów: {total_points}', 
               transform=ax.transAxes, fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.colorbar(im, ax=ax, label='Czas [ms]', shrink=0.8)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'heatmap_time_{alg_name}.png'), dpi=300, bbox_inches='tight')
        print(f"Zapisano: heatmap_time_{alg_name}.png")
        plt.close()

def plot_aggregated_trends(results: List[TestResult], output_dir: str):
    """Wykresy pokazujące trendy z uśrednieniem po wszystkich dostępnych danych - używa mediany i IQR zamiast mean/std"""
    exact, approx = filter_valid_results(results)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Trendy wydajności (mediana i IQR - bardziej odporna na outliery)', 
                 fontsize=16, fontweight='bold')
    
    def compute_median_iqr(data_list):
        """Oblicza medianę i IQR (interquartile range)"""
        if not data_list:
            return None, None, None, None
        q25, median, q75 = np.percentile(data_list, [25, 50, 75])
        iqr = q75 - q25
        return median, q25, q75, iqr
    
    # Trend n1
    ax = axes[0, 0]
    if exact:
        n1_groups = defaultdict(list)
        for r in exact:
            n1_groups[r.n1].append(r.time_ms)
        n1_vals = sorted(n1_groups.keys())
        exact_medians = []
        exact_lowers = []
        exact_uppers = []
        for n1 in n1_vals:
            median, q25, q75, _ = compute_median_iqr(n1_groups[n1])
            exact_medians.append(median)
            exact_lowers.append(median - q25)  # Odległość od mediany do q25
            exact_uppers.append(q75 - median)  # Odległość od mediany do q75
        ax.errorbar(n1_vals, exact_medians, yerr=[exact_lowers, exact_uppers], 
                   fmt='o-', label='Exact (mediana±IQR)', 
                   linewidth=2, markersize=8, capsize=5, capthick=2, color='#2E86AB')
    
    if approx:
        n1_groups = defaultdict(list)
        for r in approx:
            n1_groups[r.n1].append(r.time_ms)
        n1_vals = sorted(n1_groups.keys())
        approx_medians = []
        approx_lowers = []
        approx_uppers = []
        for n1 in n1_vals:
            median, q25, q75, _ = compute_median_iqr(n1_groups[n1])
            approx_medians.append(median)
            approx_lowers.append(median - q25)
            approx_uppers.append(q75 - median)
        ax.errorbar(n1_vals, approx_medians, yerr=[approx_lowers, approx_uppers], 
                   fmt='s-', label='Approx (mediana±IQR)', 
                   linewidth=2, markersize=8, capsize=5, capthick=2, color='#F77F00')
    
    ax.set_xlabel('n1', fontsize=12)
    ax.set_ylabel('Czas [ms]', fontsize=12)
    ax.set_title('Mediana czasu vs n1 (z IQR)', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    
    # Trend n2
    ax = axes[0, 1]
    if exact:
        n2_groups = defaultdict(list)
        for r in exact:
            n2_groups[r.n2].append(r.time_ms)
        n2_vals = sorted(n2_groups.keys())
        exact_medians = []
        exact_lowers = []
        exact_uppers = []
        for n2 in n2_vals:
            median, q25, q75, _ = compute_median_iqr(n2_groups[n2])
            exact_medians.append(median)
            exact_lowers.append(median - q25)
            exact_uppers.append(q75 - median)
        ax.errorbar(n2_vals, exact_medians, yerr=[exact_lowers, exact_uppers], 
                   fmt='o-', label='Exact (mediana±IQR)', 
                   linewidth=2, markersize=8, capsize=5, capthick=2, color='#2E86AB')
    
    if approx:
        n2_groups = defaultdict(list)
        for r in approx:
            n2_groups[r.n2].append(r.time_ms)
        n2_vals = sorted(n2_groups.keys())
        approx_medians = []
        approx_lowers = []
        approx_uppers = []
        for n2 in n2_vals:
            median, q25, q75, _ = compute_median_iqr(n2_groups[n2])
            approx_medians.append(median)
            approx_lowers.append(median - q25)
            approx_uppers.append(q75 - median)
        ax.errorbar(n2_vals, approx_medians, yerr=[approx_lowers, approx_uppers], 
                   fmt='s-', label='Approx (mediana±IQR)', 
                   linewidth=2, markersize=8, capsize=5, capthick=2, color='#F77F00')
    
    ax.set_xlabel('n2', fontsize=12)
    ax.set_ylabel('Czas [ms]', fontsize=12)
    ax.set_title('Mediana czasu vs n2 (z IQR)', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    
    # Trend k
    ax = axes[1, 0]
    if exact:
        k_groups = defaultdict(list)
        for r in exact:
            k_groups[r.k].append(r.time_ms)
        k_vals = sorted(k_groups.keys())
        exact_medians = []
        exact_lowers = []
        exact_uppers = []
        for k in k_vals:
            median, q25, q75, _ = compute_median_iqr(k_groups[k])
            exact_medians.append(median)
            exact_lowers.append(median - q25)
            exact_uppers.append(q75 - median)
        ax.errorbar(k_vals, exact_medians, yerr=[exact_lowers, exact_uppers], 
                   fmt='o-', label='Exact (mediana±IQR)', 
                   linewidth=2, markersize=8, capsize=5, capthick=2, color='#2E86AB')
    
    if approx:
        k_groups = defaultdict(list)
        for r in approx:
            k_groups[r.k].append(r.time_ms)
        k_vals = sorted(k_groups.keys())
        approx_medians = []
        approx_lowers = []
        approx_uppers = []
        for k in k_vals:
            median, q25, q75, _ = compute_median_iqr(k_groups[k])
            approx_medians.append(median)
            approx_lowers.append(median - q25)
            approx_uppers.append(q75 - median)
        ax.errorbar(k_vals, approx_medians, yerr=[approx_lowers, approx_uppers], 
                   fmt='s-', label='Approx (mediana±IQR)', 
                   linewidth=2, markersize=8, capsize=5, capthick=2, color='#F77F00')
    
    ax.set_xlabel('k', fontsize=12)
    ax.set_ylabel('Czas [ms]', fontsize=12)
    ax.set_title('Mediana czasu vs k (z IQR)', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    
    # Porównanie kosztu
    ax = axes[1, 1]
    exact_dict = {(r.n1, r.n2, r.k): r for r in exact}
    approx_dict = {(r.n1, r.n2, r.k): r for r in approx}
    common_keys = set(exact_dict.keys()) & set(approx_dict.keys())
    
    if common_keys:
        exact_costs = [exact_dict[k].cost for k in common_keys]
        approx_costs = [approx_dict[k].cost for k in common_keys]
        ax.scatter(exact_costs, approx_costs, alpha=0.7, s=100, edgecolors='black', linewidths=0.5)
        max_cost = max(max(exact_costs), max(approx_costs))
        ax.plot([0, max_cost], [0, max_cost], 'r--', label='y=x (równe koszty)', linewidth=2)
        ax.set_xlabel('Koszt Exact', fontsize=12)
        ax.set_ylabel('Koszt Approx', fontsize=12)
        ax.set_title('Porównanie kosztu rozszerzenia', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'aggregated_trends.png'), dpi=300, bbox_inches='tight')
    print(f"Zapisano: aggregated_trends.png")
    plt.close()

def plot_size_complexity(results: List[TestResult], output_dir: str):
    """Wykres pokazujący złożoność względem rozmiaru problemu - używa log-log regression"""
    exact, approx = filter_valid_results(results)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Złożoność względem rozmiaru problemu (log-log skala)', fontsize=16, fontweight='bold')
    
    # Oblicz "rozmiar problemu" jako n1 * n2 * k
    for alg_name, subset, ax in [('Exact', exact, axes[0]), ('Approx', approx, axes[1])]:
        if not subset:
            continue
        
        problem_sizes = np.array([r.n1 * r.n2 * r.k for r in subset])
        times = np.array([r.time_ms for r in subset])
        
        # Scatter plot
        ax.scatter(problem_sizes, times, alpha=0.6, s=80, color='#2E86AB' if alg_name == 'Exact' else '#F77F00')
        
        # Log-log regression (lepsze dla wykładniczych algorytmów)
        if len(subset) > 3:
            # Filtruj zera (nie można logarytmować)
            valid = (problem_sizes > 0) & (times > 0)
            if np.sum(valid) > 3:
                log_sizes = np.log(problem_sizes[valid])
                log_times = np.log(times[valid])
                # Regresja liniowa w przestrzeni log-log
                z = np.polyfit(log_sizes, log_times, 1)
                p = np.poly1d(z)
                # Generuj punkty dla trendu w przestrzeni log-log
                x_trend_log = np.linspace(log_sizes.min(), log_sizes.max(), 100)
                y_trend_log = p(x_trend_log)
                # Konwertuj z powrotem do normalnej skali
                x_trend = np.exp(x_trend_log)
                y_trend = np.exp(y_trend_log)
                ax.plot(x_trend, y_trend, "r--", alpha=0.8, linewidth=2, 
                       label=f'Trend log-log (wykładnik={z[0]:.2f})')
        
        ax.set_xlabel('Rozmiar problemu (n1 × n2 × k)', fontsize=12)
        ax.set_ylabel('Czas [ms]', fontsize=12)
        ax.set_title(f'{alg_name}', fontsize=14, fontweight='bold')
        ax.set_yscale('log')
        ax.set_xscale('log')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'size_complexity.png'), dpi=300, bbox_inches='tight')
    print(f"Zapisano: size_complexity.png")
    plt.close()

def plot_comparison_improved(results: List[TestResult], output_dir: str):
    """Ulepszone porównanie exact vs approx - lepsze wizualizacje"""
    exact, approx = filter_valid_results(results)
    
    # Znajdź wspólne testy (te same n1, n2, k)
    exact_dict = {(r.n1, r.n2, r.k): r for r in exact}
    approx_dict = {(r.n1, r.n2, r.k): r for r in approx}
    common_keys = set(exact_dict.keys()) & set(approx_dict.keys())
    
    if not common_keys:
        print("Brak wspólnych testów do porównania")
        return
    
    exact_times = [exact_dict[k].time_ms for k in common_keys]
    approx_times = [approx_dict[k].time_ms for k in common_keys]
    exact_costs = [exact_dict[k].cost for k in common_keys]
    approx_costs = [approx_dict[k].cost for k in common_keys]
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Porównanie algorytmów Exact vs Approx', fontsize=16, fontweight='bold')
    
    # 1. Scatter plot czasu z linią y=x
    ax = axes[0, 0]
    ax.scatter(exact_times, approx_times, alpha=0.6, s=100, color='#2E86AB', edgecolors='black', linewidths=0.5)
    max_time = max(max(exact_times), max(approx_times))
    ax.plot([0, max_time], [0, max_time], 'r--', label='y=x (równe czasy)', linewidth=2, zorder=1)
    ax.set_xlabel('Czas Exact [ms]', fontsize=12, fontweight='bold')
    ax.set_ylabel('Czas Approx [ms]', fontsize=12, fontweight='bold')
    ax.set_title('Porównanie czasu wykonania', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log')
    ax.set_yscale('log')
    
    # 2. Scatter plot kosztu z linią y=x
    ax = axes[0, 1]
    ax.scatter(exact_costs, approx_costs, alpha=0.6, s=100, color='#F77F00', edgecolors='black', linewidths=0.5)
    max_cost = max(max(exact_costs), max(approx_costs)) if exact_costs and approx_costs else 1
    if max_cost > 0:
        ax.plot([0, max_cost], [0, max_cost], 'r--', label='y=x (równe koszty)', linewidth=2, zorder=1)
    ax.set_xlabel('Koszt Exact', fontsize=12, fontweight='bold')
    ax.set_ylabel('Koszt Approx', fontsize=12, fontweight='bold')
    ax.set_title('Porównanie kosztu rozszerzenia', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 3. Box plot porównujący czasy
    ax = axes[1, 0]
    data_to_plot = [exact_times, approx_times]
    bp = ax.boxplot(data_to_plot, labels=['Exact', 'Approx'], patch_artist=True)
    bp['boxes'][0].set_facecolor('lightblue')
    bp['boxes'][1].set_facecolor('lightcoral')
    ax.set_ylabel('Czas [ms]', fontsize=12, fontweight='bold')
    ax.set_title('Rozkład czasu wykonania', fontsize=13, fontweight='bold')
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3, axis='y')
    
    # 4. Box plot porównujący koszty
    ax = axes[1, 1]
    data_to_plot = [exact_costs, approx_costs]
    bp = ax.boxplot(data_to_plot, labels=['Exact', 'Approx'], patch_artist=True)
    bp['boxes'][0].set_facecolor('lightblue')
    bp['boxes'][1].set_facecolor('lightcoral')
    ax.set_ylabel('Koszt', fontsize=12, fontweight='bold')
    ax.set_title('Rozkład kosztu rozszerzenia', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'comparison_exact_vs_approx_improved.png'), dpi=300, bbox_inches='tight')
    print(f"Zapisano: comparison_exact_vs_approx_improved.png")
    plt.close()

def plot_cost_ratio_improved(results: List[TestResult], output_dir: str):
    """Ulepszony wykres cost ratio - używa box plot/violin plot zamiast histogramu"""
    exact, approx = filter_valid_results(results)
    
    exact_dict = {(r.n1, r.n2, r.k): r for r in exact}
    approx_dict = {(r.n1, r.n2, r.k): r for r in approx}
    common_keys = set(exact_dict.keys()) & set(approx_dict.keys())
    
    if not common_keys:
        print("Brak wspólnych testów do cost ratio")
        return
    
    exact_costs = [exact_dict[k].cost for k in common_keys]
    approx_costs = [approx_dict[k].cost for k in common_keys]
    
    # Oblicz ratio (Approx / Exact), filtruj zera i nieskończoności
    cost_ratios = []
    for i in range(len(exact_costs)):
        if exact_costs[i] > 0:
            ratio = approx_costs[i] / exact_costs[i]
            if np.isfinite(ratio):
                cost_ratios.append(ratio)
    
    if not cost_ratios:
        print("Brak poprawnych cost ratios (wszystkie exact_costs = 0)")
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Jakość rozwiązania Approx względem Exact (Approx/Exact)', fontsize=16, fontweight='bold')
    
    # Box plot
    ax = axes[0]
    bp = ax.boxplot([cost_ratios], labels=['Cost Ratio'], patch_artist=True, widths=0.5)
    bp['boxes'][0].set_facecolor('lightcoral')
    ax.axhline(y=1, color='r', linestyle='--', linewidth=2, label='y=1 (równe koszty)')
    ax.set_ylabel('Stosunek kosztu (Approx / Exact)', fontsize=12, fontweight='bold')
    ax.set_title('Rozkład stosunku kosztów (Box Plot)', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # Histogram z lepszymi binami (tylko jeśli są różne wartości)
    ax = axes[1]
    if len(set(cost_ratios)) > 1:
        # Użyj inteligentnych binów
        bins = np.linspace(min(cost_ratios), max(cost_ratios), min(30, len(cost_ratios)))
        ax.hist(cost_ratios, bins=bins, edgecolor='black', alpha=0.7, color='lightcoral')
    else:
        # Jeśli wszystkie wartości są takie same, pokaż jako pojedynczy słupek
        unique_val = cost_ratios[0]
        ax.bar([unique_val], [len(cost_ratios)], width=0.1, edgecolor='black', alpha=0.7, color='lightcoral')
        ax.set_xlim(unique_val - 0.2, unique_val + 0.2)
    ax.axvline(x=1, color='r', linestyle='--', linewidth=2, label='x=1 (równe koszty)')
    ax.set_xlabel('Stosunek kosztu (Approx / Exact)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Liczba testów', fontsize=12, fontweight='bold')
    ax.set_title('Rozkład stosunku kosztów (Histogram)', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # Dodaj statystyki
    median_ratio = np.median(cost_ratios)
    mean_ratio = np.mean(cost_ratios)
    ax.text(0.02, 0.98, f'Mediana: {median_ratio:.3f}\nŚrednia: {mean_ratio:.3f}\nN={len(cost_ratios)}', 
           transform=ax.transAxes, fontsize=10, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'cost_ratio_improved.png'), dpi=300, bbox_inches='tight')
    print(f"Zapisano: cost_ratio_improved.png")
    plt.close()

def plot_speedup_ratio_improved(results: List[TestResult], output_dir: str):
    """Ulepszony wykres speedup ratio - używa box plot zamiast histogramu"""
    exact, approx = filter_valid_results(results)
    
    exact_dict = {(r.n1, r.n2, r.k): r for r in exact}
    approx_dict = {(r.n1, r.n2, r.k): r for r in approx}
    common_keys = set(exact_dict.keys()) & set(approx_dict.keys())
    
    if not common_keys:
        print("Brak wspólnych testów do speedup ratio")
        return
    
    exact_times = [exact_dict[k].time_ms for k in common_keys]
    approx_times = [approx_dict[k].time_ms for k in common_keys]
    
    # Oblicz speedup (Exact / Approx)
    speedup_ratios = []
    for i in range(len(exact_times)):
        if approx_times[i] > 0:
            ratio = exact_times[i] / approx_times[i]
            if np.isfinite(ratio):
                speedup_ratios.append(ratio)
    
    if not speedup_ratios:
        print("Brak poprawnych speedup ratios")
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Przyspieszenie Approx względem Exact (Exact/Approx)', fontsize=16, fontweight='bold')
    
    # Box plot
    ax = axes[0]
    bp = ax.boxplot([speedup_ratios], labels=['Speedup'], patch_artist=True, widths=0.5)
    bp['boxes'][0].set_facecolor('lightgreen')
    ax.axhline(y=1, color='r', linestyle='--', linewidth=2, label='y=1 (równe czasy)')
    ax.set_ylabel('Stosunek czasu (Exact / Approx)', fontsize=12, fontweight='bold')
    ax.set_title('Rozkład przyspieszenia (Box Plot)', fontsize=13, fontweight='bold')
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
        ax.set_xlim(unique_val - 0.2, unique_val + 0.2)
    ax.axvline(x=1, color='r', linestyle='--', linewidth=2, label='x=1 (równe czasy)')
    ax.set_xlabel('Stosunek czasu (Exact / Approx)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Liczba testów', fontsize=12, fontweight='bold')
    ax.set_title('Rozkład przyspieszenia (Histogram)', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # Dodaj statystyki
    median_ratio = np.median(speedup_ratios)
    mean_ratio = np.mean(speedup_ratios)
    ax.text(0.02, 0.98, f'Mediana: {median_ratio:.3f}\nŚrednia: {mean_ratio:.3f}\nN={len(speedup_ratios)}', 
           transform=ax.transAxes, fontsize=10, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'speedup_ratio_improved.png'), dpi=300, bbox_inches='tight')
    print(f"Zapisano: speedup_ratio_improved.png")
    plt.close()

def plot_overhead_analysis(results: List[TestResult], output_dir: str):
    """Analiza overheadu - pokazuje minimalny czas wykonania (baseline ~30ms)"""
    exact, approx = filter_valid_results(results)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Analiza overheadu wykonania (minimalny czas ~30ms)', fontsize=16, fontweight='bold')
    
    for alg_name, subset, ax in [('Exact', exact, axes[0]), ('Approx', approx, axes[1])]:
        if not subset:
            continue
        
        times = [r.time_ms for r in subset]
        min_time = min(times)
        median_time = np.median(times)
        mean_time = np.mean(times)
        
        # Histogram z zaznaczonym minimum
        ax.hist(times, bins=30, edgecolor='black', alpha=0.7, 
               color='#2E86AB' if alg_name == 'Exact' else '#F77F00')
        ax.axvline(x=min_time, color='r', linestyle='--', linewidth=2, label=f'Minimum: {min_time:.1f}ms')
        ax.axvline(x=median_time, color='g', linestyle='--', linewidth=2, label=f'Mediana: {median_time:.1f}ms')
        ax.axvline(x=mean_time, color='b', linestyle='--', linewidth=2, label=f'Średnia: {mean_time:.1f}ms')
        
        ax.set_xlabel('Czas wykonania [ms]', fontsize=12, fontweight='bold')
        ax.set_ylabel('Liczba testów', fontsize=12, fontweight='bold')
        ax.set_title(f'{alg_name} - Rozkład czasu', fontsize=13, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        # Dodaj informację o overheadzie
        overhead_estimate = min_time
        ax.text(0.02, 0.98, f'Minimalny czas (overhead): {overhead_estimate:.1f}ms\n'
                           f'Mediana: {median_time:.1f}ms\n'
                           f'Średnia: {mean_time:.1f}ms\n'
                           f'N={len(times)}', 
               transform=ax.transAxes, fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'overhead_analysis.png'), dpi=300, bbox_inches='tight')
    print(f"Zapisano: overhead_analysis.png")
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="Generate Improved Performance Plots")
    parser.add_argument('--input', type=str, default='performance_results/results.json',
                       help="Input JSON file with test results")
    parser.add_argument('--output', type=str, default='performance_results/plots',
                       help="Output directory for plots")
    
    args = parser.parse_args()
    
    if not HAS_PLOTTING:
        print("Błąd: Brak bibliotek matplotlib/numpy!")
        print(f"Szczegóły: {IMPORT_ERROR}")
        return 1
    
    if not os.path.exists(args.input):
        print(f"Błąd: Plik {args.input} nie istnieje!")
        return 1
    
    os.makedirs(args.output, exist_ok=True)
    
    print("=" * 80)
    print("GENEROWANIE ULEPSZONYCH WYKRESÓW")
    print("=" * 80)
    
    try:
        results = load_results(args.input)
        exact, approx = filter_valid_results(results)
        
        print(f"Wczytano {len(results)} wyników")
        print(f"Exact: {len(exact)} wyników, Approx: {len(approx)} wyników")
        print()
        
        if len(exact) == 0 and len(approx) == 0:
            print("UWAGA: Brak poprawnych wyników!")
            return 1
        
        print("Generowanie ulepszonych wykresów...")
        plot_time_vs_parameter_scatter(results, args.output)
        plot_heatmap_time(results, args.output)
        plot_aggregated_trends(results, args.output)
        plot_size_complexity(results, args.output)
        plot_comparison_improved(results, args.output)
        plot_cost_ratio_improved(results, args.output)
        plot_speedup_ratio_improved(results, args.output)
        plot_overhead_analysis(results, args.output)
        
        print("\n" + "=" * 80)
        print(f"Wszystkie wykresy zapisane w: {args.output}")
        print("=" * 80)
        return 0
    except Exception as e:
        print(f"BŁĄD: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    main()

