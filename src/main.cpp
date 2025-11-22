#include <vector>
#include <algorithm>
#include <set>
#include <cstdint>
#include <ranges>

using namespace std;

struct Graph {
    int n;
    std::vector<std::vector<int>> matrix;

    explicit Graph(const int vertices = 0) : n(vertices) {
        matrix.resize(n, std::vector(n, 0));
    }
    Graph(const Graph&) = default;
    Graph& operator=(const Graph&) = default;
    Graph(Graph&&) = default;

    // Liczba krawedzi wchodzacych i wychodzacych z v.
    uint32_t degree(const uint32_t v) const {
        uint32_t degree = 0;

        for (const uint32_t u : std::ranges::views::iota(0, n)) {
            degree += matrix[u][v];
            degree += matrix[v][u];
        }

        return degree;
    }

    uint64_t totalEdges() const {
        uint64_t count = 0;
        for(const auto& row : matrix) {
            for(const int val : row) count += val;
        }
        return count;
    }

    // Zwraca wierzchołki w kolejności, w jakiej powinny być rozpatrywane
    // Patrz: "PorządekWierzchołków" w dokumentacji
    std::vector<uint32_t> verticesOrder() const {
        std::vector<uint32_t> order(n, 0);

        // edgesToAlreadyAssigned[i] = j oznaczna, że i-ty wierzchołek ma j krawędzi do już uporządkowanych wierzchołków
        std::vector<uint32_t> edgesToAlreadyAssigned(n, 0);

        std::vector<bool> assigned(n, false);
        for (const uint32_t i : std::ranges::views::iota(0, n)) {
            auto best = UINT32_MAX;

            // Znajdujemy wierzcholek, ktory:
            // - ma najwiecej krawedzi do juz przypisanych wierzcholkow
            // - w przypadku remisu ma najwiekszy stopien
            for (const uint32_t v : std::ranges::views::iota(0, n)) {
                if (assigned[v]) {
                    continue;
                }
                if (edgesToAlreadyAssigned[v] > edgesToAlreadyAssigned[best]) {
                    best = v;
                    continue;
                }
                if (edgesToAlreadyAssigned[v] == edgesToAlreadyAssigned[best]) {
                    if (degree(v) > degree(best)) {
                        best = v;
                    }
                }
            }

            order[i] = best;
            assigned[i] = true;

            // Poprawiamy informacje o liczbie krawedzi do juz przypisanych wierzcholkow
            // dla kazdego sasiada wierzcholka, ktorego przypisalismy w tej iteracji.
            for (const uint32_t u : std::ranges::views::iota(0, n)) {
                if (matrix[best][u] > 0 || matrix[u][best] > 0) {
                    const auto total = matrix[best][u] + matrix[u][best];
                    edgesToAlreadyAssigned[u] += total;
                }
            }
        }

        return order;
    }
};

struct Mappings {
    int n, k;
    std::vector<std::vector<int>> maps;

    static constexpr int NO_MAPPING = -1;

    explicit Mappings(const int copies_count = 0, const int vertices = 0) : n(vertices), k(copies_count) {
        maps.resize(copies_count, std::vector<int>(vertices, NO_MAPPING));
    }
    Mappings(Mappings&&) = default;
};

struct Solution {
    Graph extendedGraph;
    Mappings mappings;
    uint64_t cost;
    bool found;

    Solution() : cost(-1), found(false) {}
    Solution(Graph&& extendedGraph, Mappings&& mappings, const uint64_t cost) : extendedGraph(std::move(extendedGraph)), mappings(std::move(mappings)), cost(cost), found(false) {}
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

struct Candidate {
    uint32_t v;
    uint32_t deltaCost;
    uint32_t deltaExist;
};

typedef std::vector<Candidate> Candidates;

Candidates chooseCandidates(const uint32_t u, const Graph& g1, const Graph &g2, const Graph &extended, const std::vector<int> &mapping) {
    // TODO:
    return std::vector<Candidate>();
}

// Aktualizuje graf `extended` dodając brakujące krawędzie po przypisaniu mapowania u -> v.
void addMissingEdges(const uint32_t u, const uint32_t v, const Graph& g1, Graph &extended, const std::vector<int> &mapping) {
    for (const uint32_t i : std::ranges::views::iota(0, g1.n)) {
        const auto mapped = mapping[i];
        // Pomijamy dla niezmappowanych wierzchołków
        if (mapped == Mappings::NO_MAPPING) {
            continue;
        }

        const auto reqOut = g1.matrix[u][i];
        const auto reqIn = g1.matrix[i][u];

        int& currOut = extended.matrix[v][mapped];
        int& currIn = extended.matrix[mapped][v];

        if (currOut < reqOut) {
            currOut = reqOut;
        }
        if (currIn < reqIn) {
            currIn = reqIn;
        }
    }
}

Solution initializeApproximateExpansion(const Graph &g1, const Graph &g2, const int copiesCount) {
    auto extended = g2;
    auto mappings = Mappings(copiesCount, extended.n);
    const auto order = g1.verticesOrder();
    auto cost = 0;
    for (const uint32_t i : std::ranges::views::iota(0, copiesCount)) {
        bool prefixEqual = true;
        auto v = UINT32_MAX;
        auto candCost = 0;
        std::vector<int32_t> mPrevious;
        if (i == 0) {
            mPrevious = std::vector<int32_t>(g1.n, UINT32_MAX);
        } else {
            mPrevious = mappings.maps[i - 1];
        }
        for (const uint32_t j : std::ranges::views::iota(0, g1.n)) {
            const auto u = order[j];
            const auto candidates = chooseCandidates(u, g1, g2, extended, mappings.maps[i]);
            for (const auto &candidate : candidates) {
                if (prefixEqual) {
                    if (j < g1.n && candidate.v < mPrevious[u]) {
                        continue;
                    }
                    if (j == g1.n && candidate.v <= mPrevious[u]) {
                        continue;
                    }
                }
                else {
                    // Kandydat spelnia wymagania, mozemy pominac kolejnych
                    v = candidate.v;
                    candCost = candidate.deltaCost;
                    break;
                }
            }
            mappings.maps[i][u] = v;
            cost += candCost;
            addMissingEdges(u, v, g1, extended, mappings.maps[i]);
            prefixEqual = prefixEqual && (v == mPrevious[u]);
        }

    }
    return Solution(std::move(extended), std::move(mappings), cost);
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