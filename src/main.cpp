#include <iostream>
#include <vector>
#include <algorithm>
#include <iomanip>
#include <set>

using namespace std;

struct Graph {
    int n;
    vector<vector<int>> matrix;

    Graph(int vertices = 0) : n(vertices) {
        matrix.resize(n, vector<int>(n, 0));
    }

    long long totalEdges() const {
        long long count = 0;
        for(const auto& row : matrix) {
            for(int val : row) count += val;
        }
        return count;
    }
};

struct Solution {
    Graph extendedGraph;
    Mappings mappings;
    uint64_t cost;
    bool found;

    Solution() : cost(-1), found(false) {}
};

struct Mappings {
    int n, k;
    std::vector<std::vector<int>> maps;

    Mappings(int copies_count = 0, int vertices = 0) : n(vertices), k(copies_count) {
        maps.resize(copies_count, vector<int>(vertices, 0));
    }
};

int countCost(int u, int v, Graph G1, Graph G2, vector<int> mapping) {
    int costIncrease = 0;
    for (int i = 0; i < mapping.size(); i++) {
            int reqOut = G1.matrix[u][i];
            int reqIn = G1.matrix[i][u];
            int currOut = G2.matrix[v][mapping[i]];
            int currIn = G2.matrix[mapping[i]][v];
            if (currOut < reqOut) {
                int diff = reqOut - currOut;
                costIncrease += diff;
            }
            if (currIn < reqIn) {
                int diff = reqIn - currIn;
                costIncrease += diff;
            }
    }

    return costIncrease;
}

// Usuwamy affected wiezrchołki z mapowania
// Przeiterować się po wszystkich kopiach i dołożyć ile powinno istnieć krawędzi z wierzchołka na które było mapowanie. Sprawdzić o ile zmniejszyły się ilości krawędzi potrzebnych do dołożenia
// Przed chwilą koszt się zminiejszał, teraz będzie sie zwiększał. Wywołujemy ObliczKoszt z odpowiednim mapowaniem. Następnie delta to roznica tego co sie zmniejszylo - to co dostalismyz obliczkoszt
// Jak mam swapa: usuwamy oba jednoczesnie, liczymy dla sasiadów tego i tego to samo. Updatujemy od razu krotności krawędzi. Patrzymy o ile spadło jak obu nie ma. Potem obliczkoszta dla jednego
// dodajemy tego jednego obliczamy koszt dla drugiego i suma z tego to jest to co wzroslo. nastepnie roznica analogicznie.

// Alternatywna opcja: swap od razu. Ustawiam na jakiejs kopii (w cpp nie w kontekscie zadania) grafu wartosci z oryginalnego grafu na sasiadach tego na który było mapowane.
// Potem zwiększam na podstawie k kopii by zmaksować co jest potrzebne. Potem to samo dla drugiego wiezrchołka. TPotem na grafie przed transofmacjami i tej ztransformowanej kopii robie roznice
// kosztow po tych affected krawedziach. 

Solution ImproveApproximateExpansion(Solution s, Graph g1 /* smaller graph */, Graph g2 /* bigger graph */) {
    bool improved = true;
    int bestDelta;
    int copyToModify;
    vector<int> newBestMapping;
    vector<vector<int>> matrixForNewBestMapping;
    while (improved) {
        improved = false;
        bestDelta = 0;
        copyToModify = -1;
        for (int i = 0; i < s.mappings.k; i++) { // wybór kopii, w której zmieniamy mapowanie
            
            for (int u = 0; u < g1.n; u++) { // wierzchołek który dostaje mapowanie
                for (int v = 0; v < g2.n; v++) { // v - nowe mapowanie wierzchołka u
                    vector<vector<int>> modifiedMatrix = s.extendedGraph.matrix; // kopia macierzy grafu
                    vector<int> currentMapping = s.mappings.maps[i];
                    auto it = std::find(s.mappings.maps[i].begin(), s.mappings.maps[i].end(), v);
                    int oldUMapping;
                    int delta;
                    if (it != s.mappings.maps[i].end()) {
                        int vertexMappedToV = distance(s.mappings.maps[i].begin(), it); // wierzchołek który przedtem był mapowany na v
                        oldUMapping = s.mappings.maps[i][u]; // stare mapowanie u
                        swap(s.mappings.maps[i][vertexMappedToV], s.mappings.maps[i][u]);
                    }
                    else {
                        oldUMapping = s.mappings.maps[i][u]; // stare mapowanie u
                        s.mappings.maps[i][u] = v;
                    }
                    for (int k = 0; k < s.extendedGraph.n; k++) { // resetowanie grafu do stanu neutralnego ze wsględnu na zmianę mapowań
                        delta -= (modifiedMatrix[oldUMapping][k] - g2.matrix[oldUMapping][k]);
                        modifiedMatrix[oldUMapping][k] = g2.matrix[oldUMapping][k];
                        delta -= (modifiedMatrix[v][k] - g2.matrix[v][k]);
                        modifiedMatrix[v][k] = g2.matrix[v][k];
                        delta -= (modifiedMatrix[k][oldUMapping] - g2.matrix[k][oldUMapping]);
                        modifiedMatrix[k][oldUMapping] = g2.matrix[k][oldUMapping];
                        delta -= (modifiedMatrix[k][v] - g2.matrix[k][v]);
                        modifiedMatrix[k][v] = g2.matrix[k][v];
                    }
                    // zwiększamy krawędzie ze względu na mapowania na v
                    for (int copynr = 0; copynr < s.mappings.k; copynr++) { // dla kazdej kopii
                        auto vIterator = std::find(s.mappings.maps[copynr].begin(), s.mappings.maps[copynr].end(), v); // sprawdź czy v jest czyimś mapowaniem w kopii copynr
                        int vertexMappedOnV = distance(s.mappings.maps[i].begin(), it); // wierzchołek mapowany na v w kopii copynr
                        if (it != s.mappings.maps[copynr].end()) {
                            for (int n = 0; n < g1.n; n++) { // dla kazdego wierzchołka z mniejszego grafu
                                int mappingOfN = s.mappings.maps[copynr][n]; // mapowanie wierzchołka n z g1 dla kopii copynr na wierzcholek g2
                                int reqIn = g1.matrix[n][vertexMappedOnV]; // sprawdzenie ile wychodzi krawdzi z n do wierzchołka który jest mapowany na v w kopii copynr
                                int currIn = modifiedMatrix[mappingOfN][v]; // ilosc krawedzi pomiedzy zmapowanymi wierzcholkami w grafie
                                if (reqIn > currIn) {
                                    modifiedMatrix[mappingOfN][v] = reqIn;
                                    delta += (reqIn - currIn);
                                }
                                int reqOut = g1.matrix[vertexMappedOnV][n]; // sprawdzenie ile wychodiz krawedzi z wierzchołka mapowanego na v do n
                                int currOut = modifiedMatrix[v][mappingOfN]; // ilosc krawedzi pomiedzy zmapowanymi wierzcholkami w grafie
                                if (reqOut > currOut) {
                                    modifiedMatrix[v][s.mappings.maps[copynr][n]] = reqOut;
                                    delta += (reqOut - currOut);
                                }
                            }
                        }
                    }

                    // zwiększamy krawędzie ze względu na to że mapowania na oldUMapping
                    for (int copynr = 0; copynr < s.mappings.k; copynr++) { // dla kazdej kopii
                        auto oldUMappingIterator = std::find(s.mappings.maps[copynr].begin(), s.mappings.maps[copynr].end(), oldUMapping); // sprawdź czy v jest czyimś mapowaniem w kopii copynr
                        int vertexMappedOnOldUMapping = distance(s.mappings.maps[i].begin(), it); // wierzchołek mapowany na stare mapowanie u w kopii copynr
                        if (oldUMappingIterator != s.mappings.maps[copynr].end()) {
                            for (int n = 0; n < g1.n; n++) { // dla kazdego wierzchołka z mniejszego grafu
                                int mappingOfN = s.mappings.maps[copynr][n]; // mapowanie wierzchołka n z g1 dla kopii copynr na wierzcholek g2
                                int reqIn = g1.matrix[n][vertexMappedOnOldUMapping]; // sprawdzenie ile wychodzi krawdzi z n do wierzchołka który jest mapowany na stare mapowanie u w kopii copynr
                                int currIn = modifiedMatrix[mappingOfN][v]; // ilosc krawedzi pomiedzy zmapowanymi wierzcholkami w grafie
                                if (reqIn > currIn) {
                                    modifiedMatrix[mappingOfN][v] = reqIn;
                                    delta += (reqIn - currIn);
                                }
                                int reqOut = g1.matrix[vertexMappedOnOldUMapping][n]; // sprawdzenie ile wychodiz krawedzi z wierzchołka mapowanego na stare mapowanie u do n
                                int currOut = modifiedMatrix[v][mappingOfN]; // ilosc krawedzi pomiedzy zmapowanymi wierzcholkami w grafie
                                if (reqOut > currOut) {
                                    modifiedMatrix[v][s.mappings.maps[copynr][n]] = reqOut;
                                    delta += (reqOut - currOut);
                                }
                            }
                        }
                    }

                    vector<int> newMapping = s.mappings.maps[i];
                    set<int> vset(s.mappings.maps[i].begin(), s.mappings.maps[i].end());
                    s.mappings.maps[i] = currentMapping;
                    bool isMappingValid = std::find(s.mappings.maps.begin(), s.mappings.maps.end(), vset) != s.mappings.maps.end();
                  
                    if (isMappingValid && delta < bestDelta) {
                        bestDelta = delta;
                        copyToModify = i;
                        newBestMapping = newMapping;
                        matrixForNewBestMapping = modifiedMatrix;
                    }


                }
            }
        }
        if (copyToModify != -1) {
            s.mappings.maps[copyToModify] = newBestMapping;
            s.extendedGraph.matrix = matrixForNewBestMapping;
            s.cost += bestDelta;
            improved = true;
        }

    }

    return s;
}

int main() {

}