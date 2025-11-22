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
    [[nodiscard]] uint32_t degree(const uint32_t v) const {
        uint32_t degree = 0;

        for (const uint32_t u : std::ranges::views::iota(0, n)) {
            degree += matrix[u][v];
            degree += matrix[v][u];
        }

        return degree;
    }

    [[nodiscard]] uint64_t totalEdges() const {
        uint64_t count = 0;
        for(const auto& row : matrix) {
            for(const int val : row) count += val;
        }
        return count;
    }

    // Zwraca wierzchołki w kolejności, w jakiej powinny być rozpatrywane
    // Patrz: "PorządekWierzchołków" w dokumentacji
    [[nodiscard]] std::vector<uint32_t> verticesOrder() const {
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

    explicit Candidate(const uint32_t v, const uint32_t deltaCost, const uint32_t deltaExist): v(v), deltaCost(deltaCost), deltaExist(deltaExist) {}
    Candidate(Candidate&&) = default;
    Candidate& operator=(Candidate&&) = default;
};

typedef std::vector<Candidate> Candidates;

uint32_t computeDeltaExist(const uint32_t u, const uint32_t v, const Graph& g1, const Graph& extended, const std::vector<int>& mapping) {
    uint32_t covered = 0;
    for (const uint32_t x : std::ranges::views::iota(0, g1.n)) {
        const auto mappedX = mapping[x];
        if (mappedX == Mappings::NO_MAPPING) {
            continue;
        }

        int reqOut = g1.matrix[u][x];
        int haveOut = extended.matrix[v][mappedX];
        covered += std::min(reqOut, haveOut);

        int reqIn = g1.matrix[x][u];
        int haveIn = extended.matrix[mappedX][v];
        covered += std::min(reqIn, haveIn);
    }

    return covered;
}

Candidates chooseCandidates(const uint32_t u, const Graph& g1, const Graph &g2, const Graph &extended, const std::vector<int> &mapping) {
    auto candidates = std::vector<Candidate>();

    for (const uint32_t v : std::ranges::views::iota(0, g2.n)) {
        if (mapping[v] == Mappings::NO_MAPPING) {
            continue;
        }
        const auto deltaCost = countCost(u, v, g1, extended, mapping);
        const auto deltaExist = computeDeltaExist(u, v, g1, extended, mapping);

        candidates.emplace_back(v, deltaCost, deltaExist);
    }

    std::ranges::sort(candidates, [&extended](const Candidate &a, const Candidate &b) {
         if (a.deltaExist != b.deltaExist) {
             return a.deltaExist < b.deltaExist;
         }
        if (a.deltaCost != b.deltaCost) {
            return a.deltaCost > b.deltaCost;
        }
        return extended.degree(a.v) < extended.degree(b.v);
    });
    return candidates;
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

// TODO: Zapewnienie odnalezienia rodziny mapowań -> trzeba to zapewnic tutaj, dodajac jakies checki
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
                // Kandydat spelnia wymagania, mozemy pominac kolejnych
                v = candidate.v;
                candCost = candidate.deltaCost;
                break;
            }
            mappings.maps[i][u] = v;
            cost += candCost;
            addMissingEdges(u, v, g1, extended, mappings.maps[i]);
            prefixEqual = prefixEqual && (v == mPrevious[u]);
        }

    }
    return Solution(std::move(extended), std::move(mappings), cost);
}


Solution ImproveApproximateExpansion(Solution s, Graph g1 /* smaller graph */, Graph g2 /* bigger graph */) {
    bool improved = true; // czy znaleziono lepsze rozwiązanie
    int bestDelta;  // o ile lepsze rozwiązanie znalezion (zakres (-inf, 0))
    int copyToModify; // kopia, w która należy dokonać zmian przy najlepszym znalezionym rozwiązaniu
    vector<int> newBestMapping; // najoptymalniejsze znalezione mapowanie
    vector<vector<int>> matrixForNewBestMapping; // Macierz sąsiedztwa grafu G2' po zastosowaniu mapowania newBestMapping
    while (improved) {
        improved = false; 
        bestDelta = 0;
        copyToModify = -1;
        for (int i = 0; i < s.mappings.k; i++) { // wybór kopii, w której szukamy lepszego mapowania

            for (int u = 0; u < g1.n; u++) { // wierzchołek który dostaje mapowanie nowe mapowanie
                for (int v = 0; v < g2.n; v++) { // v - nowe mapowanie wierzchołka u
                    vector<vector<int>> modifiedMatrix = s.extendedGraph.matrix; // kopia macierzy sąsiedztwa grafu G2 - do modyfikacji
                    vector<int> currentMapping = s.mappings.maps[i]; // aktualne mapowanie dla kopii i(zapisane, by na końcu móc cofnąć zmiany)
                    auto it = std::find(s.mappings.maps[i].begin(), s.mappings.maps[i].end(), v);
                    int oldUMapping;
                    int delta;
                    if (it != s.mappings.maps[i].end()) { // jeżeli jakis wierzchołek z G1 juz jest mapowany n v
                        int vertexMappedToV = distance(s.mappings.maps[i].begin(), it); // wierzchołek G1, który aktualnie jest mapowany na v
                        oldUMapping = s.mappings.maps[i][u]; // stare mapowanie u
                        swap(s.mappings.maps[i][vertexMappedToV], s.mappings.maps[i][u]);
                    }
                    else { // jeżeli żaden wierzchołek z G1 nie jest mapowany na v
                        oldUMapping = s.mappings.maps[i][u]; 
                        s.mappings.maps[i][u] = v;
                    }
                    for (int k = 0; k < s.extendedGraph.n; k++) { // usuwanie dodanych wcześniej krawędzi do G2 wchodzących/wychodzących do v i oldUMapping
                        delta -= (modifiedMatrix[oldUMapping][k] - g2.matrix[oldUMapping][k]);
                        modifiedMatrix[oldUMapping][k] = g2.matrix[oldUMapping][k];
                        delta -= (modifiedMatrix[v][k] - g2.matrix[v][k]);
                        modifiedMatrix[v][k] = g2.matrix[v][k];
                        delta -= (modifiedMatrix[k][oldUMapping] - g2.matrix[k][oldUMapping]);
                        modifiedMatrix[k][oldUMapping] = g2.matrix[k][oldUMapping];
                        delta -= (modifiedMatrix[k][v] - g2.matrix[k][v]);
                        modifiedMatrix[k][v] = g2.matrix[k][v];
                    }
                    // zwiększamy krawędzie ze względu na mapowanie na v
                    for (int copynr = 0; copynr < s.mappings.k; copynr++) { 
                        auto vIterator = std::find(s.mappings.maps[copynr].begin(), s.mappings.maps[copynr].end(), v); // sprawdź czy v jest czyimś mapowaniem w kopii copynr
                        if (it != s.mappings.maps[copynr].end()) {
                            int vertexMappedOnV = distance(s.mappings.maps[i].begin(), it); // wierzchołek mapowany na v w kopii copynr
                            for (int n = 0; n < g1.n; n++) { // dla kazdego wierzchołka z mniejszego grafu
                                int mappingOfN = s.mappings.maps[copynr][n]; // mapowanie wierzchołka n z g1 dla kopii copynr na wierzcholek g2
                                int reqIn = g1.matrix[n][vertexMappedOnV]; // sprawdzenie ile wychodzi krawdzi z n do wierzchołka który jest mapowany na v w kopii copynr
                                int currIn = modifiedMatrix[mappingOfN][v]; // ilosc krawedzi pomiedzy zmapowanymi wierzcholkami w grafie
                                if (reqIn > currIn) {
                                    modifiedMatrix[mappingOfN][v] = reqIn;
                                    delta += (reqIn - currIn);
                                }
                                int reqOut = g1.matrix[vertexMappedOnV][n]; // sprawdzenie ile wychodzi krawedzi z wierzchołka mapowanego na v do n
                                int currOut = modifiedMatrix[v][mappingOfN]; // ilosc krawedzi pomiedzy zmapowanymi wierzcholkami w grafie
                                if (reqOut > currOut) {
                                    modifiedMatrix[v][s.mappings.maps[copynr][n]] = reqOut;
                                    delta += (reqOut - currOut);
                                }
                            }
                        }
                    }

                    // zwiększamy krawędzie ze względu na to że mapowania na oldUMapping
                    for (int copynr = 0; copynr < s.mappings.k; copynr++) {
                        auto oldUMappingIterator = std::find(s.mappings.maps[copynr].begin(), s.mappings.maps[copynr].end(), oldUMapping); // sprawdź czy stare mapowanie u jest czyimś mapowaniem w kopii copynr
                        if (oldUMappingIterator != s.mappings.maps[copynr].end()) {
                            int vertexMappedToOldUMapping = distance(s.mappings.maps[i].begin(), it); // wierzchołek mapowany na stare mapowanie u w kopii copynr
                            for (int n = 0; n < g1.n; n++) {
                                int mappingOfN = s.mappings.maps[copynr][n]; // mapowanie wierzchołka n z g1 dla kopii copynr na wierzcholek g2
                                int reqIn = g1.matrix[n][vertexMappedToOldUMapping]; // sprawdzenie ile wychodzi krawdzi z n do wierzchołka który jest mapowany na stare mapowanie u w kopii copynr
                                int currIn = modifiedMatrix[mappingOfN][oldUMapping]; // ilosc krawedzi pomiedzy zmapowanymi wierzcholkami w grafie
                                if (reqIn > currIn) {
                                    modifiedMatrix[mappingOfN][oldUMapping] = reqIn;
                                    delta += (reqIn - currIn);
                                }
                                int reqOut = g1.matrix[vertexMappedToOldUMapping][n]; // sprawdzenie ile wychodiz krawedzi z wierzchołka mapowanego na stare mapowanie u do n
                                int currOut = modifiedMatrix[oldUMapping][mappingOfN]; // ilosc krawedzi pomiedzy zmapowanymi wierzcholkami w grafie
                                if (reqOut > currOut) {
                                    modifiedMatrix[oldUMapping][s.mappings.maps[copynr][n]] = reqOut;
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