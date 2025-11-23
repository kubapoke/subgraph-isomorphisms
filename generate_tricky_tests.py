import os
import random

def write_test(filename, g1_matrix, g2_matrix, k, description):
    os.makedirs("tests_tricky", exist_ok=True)
    filepath = os.path.join("tests_tricky", filename)
    n1 = len(g1_matrix)
    n2 = len(g2_matrix)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"{n1}\n")
        for row in g1_matrix:
            f.write(" ".join(map(str, row)) + "\n")
        f.write(f"{n2}\n")
        for row in g2_matrix:
            f.write(" ".join(map(str, row)) + "\n")
        f.write(f"{k}\n")
    print(f"Generated {filename}: {description}")

def gen_matrix(n, val=0):
    return [[val]*n for _ in range(n)]

def main():
    print("Generating TRICKY tests...")

    # 1. Pułapka Kierunkowa (Directionality Trap)
    # G1: 0->1, G2: 1->0. Cost should be 1.
    g1 = gen_matrix(2)
    g1[0][1] = 1
    g2 = gen_matrix(2)
    g2[1][0] = 1
    write_test("tricky_01_direction.txt", g1, g2, 1, "Directionality check: 0->1 vs 1->0")

    # 2. Maksymalne Upakowanie (Tetrahedron)
    # Find 4 triangles (K3) in K4.
    # C(4,3) = 4. Max possible. Cost should be 0.
    g1 = gen_matrix(3, 1) # K3 (with self loops? no, let's zero diagonal)
    for i in range(3): g1[i][i] = 0
    
    g2 = gen_matrix(4, 1) # K4
    for i in range(4): g2[i][i] = 0
    
    write_test("tricky_02_tetrahedron.txt", g1, g2, 4, "Find 4 K3 in K4 (Max packing)")

    # 3. Grafy Rozłączne (Disconnected Components)
    # G1: 0-1  2-3 (two edges, disjoint)
    g1 = gen_matrix(4)
    g1[0][1] = g1[1][0] = 1
    g1[2][3] = g1[3][2] = 1
    
    # G2: Path 0-1-2-3-4
    g2 = gen_matrix(5)
    for i in range(4):
        g2[i][i+1] = g2[i+1][i] = 1
        
    write_test("tricky_03_disconnected.txt", g1, g2, 1, "Disconnected G1 in connected G2")

    # 4. Wysokie Krotności (High Weights)
    # G1: 0->1 weight 100
    # G2: 0->1 weight 99
    # Cost: 1
    g1 = gen_matrix(2)
    g1[0][1] = 100
    g2 = gen_matrix(2)
    g2[0][1] = 99
    write_test("tricky_04_high_weights.txt", g1, g2, 1, "Weight difference 100 vs 99")

    # 5. Symetria (Symmetry/Automorphisms)
    # Find 4 paths of length 2 (P3) in C4.
    # C4: 0-1-2-3-0. P3: 0-1-2.
    # There are 4 such paths.
    g1 = gen_matrix(3)
    g1[0][1] = g1[1][0] = 1
    g1[1][2] = g1[2][1] = 1
    
    g2 = gen_matrix(4)
    edges = [(0,1), (1,2), (2,3), (3,0)]
    for u,v in edges:
        g2[u][v] = g2[v][u] = 1
        
    write_test("tricky_05_symmetry_C4.txt", g1, g2, 4, "4 paths P3 in Cycle C4")

    # 6. Izolowane wierzchołki (Isolated Vertices)
    # G1: 3 isolated vertices
    # G2: K3
    # Cost: 0 (subgraph relation allows fewer edges)
    g1 = gen_matrix(3)
    g2 = gen_matrix(3, 1)
    for i in range(3): g2[i][i] = 0
    write_test("tricky_06_isolated_in_K3.txt", g1, g2, 1, "Empty graph in K3 (Cost 0)")

    # 7. Odwrotność: K3 w pustym
    # G1: K3
    # G2: 3 isolated vertices
    # Cost: 6 (3 edges * 2 directions if directed, or just 3 edges? Matrix is symmetric for undirected usually, but here we treat as directed multigraphs. K3 usually means 0-1, 1-0 etc. Let's assume simple directed K3: 0->1, 1->2, 2->0 cycle? Or full? Let's do full.)
    g1 = gen_matrix(3, 1)
    for i in range(3): g1[i][i] = 0
    g2 = gen_matrix(3)
    write_test("tricky_07_K3_in_empty.txt", g1, g2, 1, "K3 in empty graph (High cost)")

    # 8. Self-loop trap
    # G1: Node with self loop
    # G2: Node without self loop
    g1 = gen_matrix(1)
    g1[0][0] = 1
    g2 = gen_matrix(1)
    write_test("tricky_08_self_loop.txt", g1, g2, 1, "Self loop requirement")

    # 9. "Niemożliwe" upakowanie (Pigeonhole)
    # G1: K3
    # G2: K4
    # k=5 (Max is 4)
    # Should fail / NO_SOLUTION
    g1 = gen_matrix(3, 1)
    for i in range(3): g1[i][i] = 0
    g2 = gen_matrix(4, 1)
    for i in range(4): g2[i][i] = 0
    write_test("tricky_09_pigeonhole.txt", g1, g2, 5, "5 K3 in K4 (Impossible)")

    # 10. Duży graf rzadki (Sparse)
    # G1: Path 5
    # G2: Path 10
    # k=2
    g1 = gen_matrix(5)
    for i in range(4): g1[i][i+1] = 1
    g2 = gen_matrix(10)
    for i in range(9): g2[i][i+1] = 1
    write_test("tricky_10_sparse_paths.txt", g1, g2, 2, "2 Paths P5 in Path P10")

if __name__ == "__main__":
    main()
