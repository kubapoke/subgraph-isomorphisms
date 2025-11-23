import random
import os
import shutil

def generate_graph_matrix(n, density, max_weight=10, allow_self_loops=True):
    matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if not allow_self_loops and i == j:
                continue
            # Random chance for an edge
            if random.random() < density:
                matrix[i][j] = random.randint(1, max_weight)
    return matrix

def save_test(filename, k, n1, matrix1, n2, matrix2):
    with open(filename, 'w') as f:
        # G1
        f.write(f"{n1}\n")
        for row in matrix1:
            f.write(" ".join(map(str, row)) + "\n")
        
        # G2
        f.write(f"{n2}\n")
        for row in matrix2:
            f.write(" ".join(map(str, row)) + "\n")
            
        # k
        f.write(f"{k}\n")

output_dir = "tests_chaos"
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir, exist_ok=True)

print(f"Generowanie testów w {output_dir} (FORMAT MACIERZOWY)...")

# 1. Małe, gęste grafy (duża szansa na kolizje)
for i in range(1, 11):
    n1 = random.randint(3, 6)
    n2 = random.randint(n1, 10)
    k = random.randint(1, 3)
    matrix1 = generate_graph_matrix(n1, 0.8) # Gęsty G1
    matrix2 = generate_graph_matrix(n2, 0.8) # Gęsty G2
    save_test(os.path.join(output_dir, f"chaos_dense_{i:02d}.txt"), k, n1, matrix1, n2, matrix2)

# 2. Rzadkie grafy (dużo izolowanych wierzchołków)
for i in range(1, 11):
    n1 = random.randint(4, 8)
    n2 = random.randint(n1, 12)
    k = random.randint(1, 4)
    matrix1 = generate_graph_matrix(n1, 0.2)
    matrix2 = generate_graph_matrix(n2, 0.2)
    save_test(os.path.join(output_dir, f"chaos_sparse_{i:02d}.txt"), k, n1, matrix1, n2, matrix2)

# 3. Losowe wagi (duży rozrzut)
for i in range(1, 11):
    n1 = random.randint(3, 7)
    n2 = random.randint(n1, 10)
    k = random.randint(1, 3)
    matrix1 = generate_graph_matrix(n1, 0.5, max_weight=100)
    matrix2 = generate_graph_matrix(n2, 0.5, max_weight=100)
    save_test(os.path.join(output_dir, f"chaos_weights_{i:02d}.txt"), k, n1, matrix1, n2, matrix2)

# 4. "Niemożliwe" (k * n1 > n2 lub blisko granicy)
for i in range(1, 11):
    n1 = random.randint(4, 6)
    n2 = random.randint(n1, 12)
    # Próbujemy wymusić k tak, żeby było ciasno lub niemożliwe
    max_k = n2 // n1
    k = random.randint(max_k, max_k + 2) 
    matrix1 = generate_graph_matrix(n1, 0.4)
    matrix2 = generate_graph_matrix(n2, 0.4)
    save_test(os.path.join(output_dir, f"chaos_impossible_{i:02d}.txt"), k, n1, matrix1, n2, matrix2)

# 5. Totalny random (różne n1, n2, k)
for i in range(1, 11):
    n1 = random.randint(2, 8)
    n2 = random.randint(n1, 15)
    k = random.randint(1, 3)
    d1 = random.random()
    d2 = random.random()
    matrix1 = generate_graph_matrix(n1, d1)
    matrix2 = generate_graph_matrix(n2, d2)
    save_test(os.path.join(output_dir, f"chaos_random_{i:02d}.txt"), k, n1, matrix1, n2, matrix2)

print("Wygenerowano 50 testów chaosu w poprawnym formacie.")
