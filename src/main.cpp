#include <vector>
#include <algorithm>
#include <set>
#include <cstdint>

struct Graph {
    int n;
    std::vector<std::vector<int>> matrix;

    explicit Graph(const int vertices = 0) : n(vertices) {
        matrix.resize(n, std::vector<int>(n, 0));
    }

    long long totalEdges() const {
        long long count = 0;
        for(const auto& row : matrix) {
            for(const int val : row) count += val;
        }
        return count;
    }
};

struct Mappings {
    int n, k;
    std::vector<std::vector<int>> maps;

    explicit Mappings(const int copies_count = 0, const int vertices = 0) : n(vertices), k(copies_count) {
        maps.resize(copies_count, std::vector<int>(vertices, 0));
    }
};

struct Solution {
    Graph extendedGraph;
    Mappings mappings;
    uint64_t cost;
    bool found;

    Solution() : cost(-1), found(false) {}
};

int countCost(const int u, const int v, const Graph &G1, const Graph &G2, const std::vector<int> &mapping) {
    int costIncrease = 0;
    for (int i = 0; i < mapping.size(); i++) {
        const int reqOut = G1.matrix[u][i];
        const int reqIn = G1.matrix[i][u];
        const int currOut = G2.matrix[v][mapping[i]];
        const int currIn = G2.matrix[mapping[i]][v];
        if (currOut < reqOut) {
            const int diff = reqOut - currOut;
            costIncrease += diff;
        }
        if (currIn < reqIn) {
            const int diff = reqIn - currIn;
            costIncrease += diff;
        }
    }

    return costIncrease;
}


void ImproveApproximateExpansion(Solution s, const Graph &g1 /* smaller graph */, const Graph &g2 /* bigger graph */) {
    std::vector<std::set<int>> images;
    bool improved = true;
    int bestDelta;
    while (improved) {
        improved = false;
        bestDelta = 0;
        for (int i = 0; i < s.mappings.k; i++) {
            
            for (int u = 0; u < g1.n; u++) {
                for (int v = 0; v < g2.n; v++) {
                    bool ifSwapped = false;
                    int mappedVertex;
                    // Usuwamy affected wiezrchołki z mapowania
                    // Przeiterować się po wszystkich kopiach i dołożyć ile powinno istnieć krawędzi z wierzchołka na które było mapowanie. Sprawdzić o ile zmniejszyły się ilości krawędzi potrzebnych do dołożenia
                    // Przed chwilą koszt się zminiejszał, teraz będzie sie zwiększał. Wywołujemy ObliczKoszt z odpowiednim mapowaniem. Następnie delta to roznica tego co sie zmniejszylo - to co dostalismyz obliczkoszt
                    // Jak mam swapa: usuwamy oba jednoczesnie, liczymy dla sasiadów tego i tego to samo. Updatujemy od razu krotności krawędzi. Patrzymy o ile spadło jak obu nie ma. Potem obliczkoszta dla jednego
                    // dodajemy tego jednego obliczamy koszt dla drugiego i suma z tego to jest to co wzroslo. nastepnie roznica analogicznie.

                    // Alternatywna opcja: swap od razu. Ustawiam na jakiejs kopii (w cpp nie w kontekscie zadania) grafu wartosci z oryginalnego grafu na sasiadach tego na który było mapowane.
                    // Potem zwiększam na podstawie k kopii by zmaksować co jest potrzebne. Potem to samo dla drugiego wiezrchołka. TPotem na grafie przed transofmacjami i tej ztransformowanej kopii robie roznice
                    // kosztow po tych affected krawedziach. 
                    auto it = std::find(s.mappings.maps[i].begin(), s.mappings.maps[i].end(), v);
                    if (it != s.mappings.maps[i].end()) {
                        mappedVertex = distance(s.mappings.maps[i].begin(), it);
                        std::swap(s.mappings.maps[i][mappedVertex], s.mappings.maps[i][u]);
                    }
                    else {
                        s.mappings.maps[i][u] = v;
                    }
                    for (int k = 0; k < s.extendedGraph.n; k++) {
                        s.extendedGraph.matrix[u][k] = g2.matrix[u][k];
                        s.extendedGraph.matrix[k][u] = g2.matrix[k][u];
                        if (ifSwapped) {
                            s.extendedGraph.matrix[mappedVertex][k] = g2.matrix[mappedVertex][k];
                            s.extendedGraph.matrix[k][mappedVertex] = g2.matrix[k][mappedVertex];
                        }
                    }

                }
            }
        }
    }
}

int main() {

}