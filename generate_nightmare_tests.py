import random
import os
import shutil
import math

def generate_matrix(n, fill_val=0):
    return [[fill_val] * n for _ in range(n)]

def save_test(filename, k, n1, matrix1, n2, matrix2):
    with open(filename, 'w') as f:
        f.write(f"{n1}\n")
        for row in matrix1:
            f.write(" ".join(map(str, row)) + "\n")
        f.write(f"{n2}\n")
        for row in matrix2:
            f.write(" ".join(map(str, row)) + "\n")
        f.write(f"{k}\n")

output_dir = "tests_nightmare"
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir, exist_ok=True)

print(f"Generowanie testów w {output_dir}...")

# 1. SYMETRYCZNE PIEKŁO (Symmetry Hell)
# G1 = K_3 (trójkąt), G2 = K_6 (pełny).
# Liczba kopii k bardzo duża.
# To testuje czy algorytm radzi sobie z ogromną liczbą permutacji.
for i in range(1, 4):
    n1 = 3
    n2 = 5 + i
    k = 5 * i # Dużo kopii
    
    # G1 = K3 (wszystkie wagi 1)
    m1 = generate_matrix(n1, 1)
    
    # G2 = Kn2 (wszystkie wagi 1)
    m2 = generate_matrix(n2, 1)
    
    save_test(os.path.join(output_dir, f"nightmare_symmetry_clique_{i}.txt"), k, n1, m1, n2, m2)

# 2. BACKTRACKING HELL (Prawie pasuje)
# G1 ma krawędzie o wadze 10.
# G2 ma mnóstwo krawędzi o wadze 9, i tylko kilka o wadze 10.
# Algorytm zachłanny (approx) może się nabrać na 9, exact musi szukać 10.
for i in range(1, 4):
    n1 = 5
    n2 = 12
    k = 2
    
    m1 = generate_matrix(n1, 0)
    # Ścieżka w G1 o wadze 10
    for j in range(n1-1):
        m1[j][j+1] = 10
        
    m2 = generate_matrix(n2, 0)
    # Wypełnij G2 krawędziami o wadze 9 (szum)
    for r in range(n2):
        for c in range(n2):
            if r != c and random.random() < 0.6:
                m2[r][c] = 9
    
    # Ukryj jedną ścieżkę o wadze 10 w G2
    path = list(range(n2))
    random.shuffle(path)
    for j in range(n1-1):
        u, v = path[j], path[j+1]
        m2[u][v] = 10
        
    save_test(os.path.join(output_dir, f"nightmare_backtrack_weights_{i}.txt"), k, n1, m1, n2, m2)

# 3. MAXIMAL K (Test wydajności struktur danych)
# G1 = pojedyncza krawędź. G2 = rzadki graf.
# k = maksymalna możliwa liczba krawędzi w G2.
for i in range(1, 3):
    n1 = 2
    n2 = 10
    
    m1 = generate_matrix(n1, 0)
    m1[0][1] = 1 # Jedna krawędź
    
    m2 = generate_matrix(n2, 0)
    edge_count = 0
    for r in range(n2):
        for c in range(n2):
            if r != c and random.random() < 0.3:
                m2[r][c] = 1
                edge_count += 1
    
    k = max(1, edge_count // 3)
    
    save_test(os.path.join(output_dir, f"nightmare_max_k_{i}.txt"), k, n1, m1, n2, m2)

# 4. DUŻE GRAFY (Scale)
# n1=7, n2=15. Dla Exact to może być timeout.
for i in range(1, 4):
    n1 = 7
    n2 = 15
    k = 2
    
    m1 = [[random.randint(0, 1) for _ in range(n1)] for _ in range(n1)]
    m2 = [[random.randint(0, 1) for _ in range(n2)] for _ in range(n2)]
    
    save_test(os.path.join(output_dir, f"nightmare_scale_{i}.txt"), k, n1, m1, n2, m2)

# 5. PĘTLE I IZOLOWANE (Self-loops & Isolated)
# G1 ma pętle własne. G2 nie ma pętli. Koszt powinien być wysoki.
for i in range(1, 3):
    n1 = 4
    n2 = 8
    k = 3
    
    m1 = generate_matrix(n1, 0)
    for j in range(n1): m1[j][j] = 5 # Pętle
    
    m2 = generate_matrix(n2, 0) # Pusty (brak pętli)
    
    save_test(os.path.join(output_dir, f"nightmare_loops_{i}.txt"), k, n1, m1, n2, m2)

print("Wygenerowano testy Nightmare.")
