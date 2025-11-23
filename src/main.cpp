#include <vector>
#include <algorithm>
#include <set>
#include <cstdint>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <chrono>
#include <iomanip>

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

        for (int u = 0; u < n; ++u) {
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
        for (int i = 0; i < n; ++i) {
            int best = -1;

            // Znajdujemy wierzcholek, ktory:
            // - ma najwiecej krawedzi do juz przypisanych wierzcholkow
            // - w przypadku remisu ma najwiekszy stopien
            for (uint32_t v = 0; v < static_cast<uint32_t>(n); ++v) {
                if (assigned[v]) {
                    continue;
                }
                if (best == -1) {
                    best = v;
                    continue;
                }
                if (edgesToAlreadyAssigned[v] > edgesToAlreadyAssigned[best]) {
                    best = v;
                    continue;
                }
                if (edgesToAlreadyAssigned[v] == edgesToAlreadyAssigned[best]) {
                    if (degree(v) > degree(static_cast<uint32_t>(best))) {
                        best = v;
                    }
                }
            }

            order[i] = best;
            assigned[best] = true;

            // Poprawiamy informacje o liczbie krawedzi do juz przypisanych wierzcholkow
            // dla kazdego sasiada wierzcholka, ktorego przypisalismy w tej iteracji.
            for (uint32_t u = 0; u < static_cast<uint32_t>(n); ++u) {
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
    Mappings(const Mappings&) = default;
    Mappings& operator=(const Mappings&) = default;
};

struct Solution {
    Graph extendedGraph;
    Mappings mappings;
    uint64_t cost;
    bool found;

    Solution() : cost(-1), found(false) {}
    Solution(Graph&& extendedGraph, Mappings&& mappings, const uint64_t cost) : extendedGraph(std::move(extendedGraph)), mappings(std::move(mappings)), cost(cost), found(false) {}
};

// Oblicza koszt przypisania u -> v
// Zgodnie z sekcją 3.5 dokumentacji: ObliczKoszt
int countCost(const int u, const int v, const Graph &G1, const Graph &G2Extended, const std::vector<int> &mapping) {
    int costIncrease = 0;
    for (size_t i = 0; i < mapping.size(); i++) {
        if (mapping[i] == Mappings::NO_MAPPING) {
            continue;  // Pomijamy niezmapowane wierzchołki
        }
        const int reqOut = G1.matrix[u][i];
        const int reqIn = G1.matrix[i][u];
        const int currOut = G2Extended.matrix[v][mapping[i]];
        const int currIn = G2Extended.matrix[mapping[i]][v];
        if (currOut < reqOut) {
            const int diff = reqOut - currOut;
            costIncrease += diff;
        }
        if (currIn < reqIn) {
            const int diff = reqIn - currIn;
            costIncrease += diff;
        }
    }
    
    // POPRAWKA: Dodaj koszt pętli (self-loop)
    const int reqSelfLoop = G1.matrix[u][u];
    const int currSelfLoop = G2Extended.matrix[v][v];
    if (currSelfLoop < reqSelfLoop) {
        costIncrease += (reqSelfLoop - currSelfLoop);
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
    for (int x = 0; x < g1.n; ++x) {
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
    
    // POPRAWKA: Dodaj pokrycie pętli (self-loop)
    int reqSelfLoop = g1.matrix[u][u];
    int haveSelfLoop = extended.matrix[v][v];
    covered += std::min(reqSelfLoop, haveSelfLoop);

    return covered;
}

Candidates chooseCandidates(const uint32_t u, const Graph& g1, const Graph &g2, const Graph &extended, const std::vector<int> &mapping) {
    auto candidates = std::vector<Candidate>();

    // Znajdź wierzchołki już użyte w bieżącym mapowaniu
    std::set<int> usedVertices;
    for (int mappedVertex : mapping) {
        if (mappedVertex != Mappings::NO_MAPPING) {
            usedVertices.insert(mappedVertex);
        }
    }

    for (int v = 0; v < g2.n; ++v) {
        // Pomiń wierzchołki już użyte w bieżącej kopii
        if (usedVertices.count(v)) {
            continue;
        }
        
        const auto deltaCost = countCost(u, v, g1, extended, mapping);
        const auto deltaExist = computeDeltaExist(u, v, g1, extended, mapping);

        candidates.emplace_back(v, deltaCost, deltaExist);
    }

    // Sortowanie zgodnie z sekcją 3.3 dokumentacji:
    // 1. Maksymalizacja zgodności (deltaExist - więcej lepiej, więc malejąco)
    // 2. Minimalizacja przyrostu kosztu (deltaCost - mniej lepiej, więc rosnąco)
    // 3. Maksymalny stopień wierzchołka (więcej lepiej, więc malejąco)
    std::sort(candidates.begin(), candidates.end(), [&extended](const Candidate &a, const Candidate &b) {
         if (a.deltaExist != b.deltaExist) {
             return a.deltaExist > b.deltaExist;  // POPRAWKA: malejąco (więcej pokrytych krawędzi to lepiej)
         }
        if (a.deltaCost != b.deltaCost) {
            return a.deltaCost < b.deltaCost;  // POPRAWKA: rosnąco (mniejszy koszt to lepiej)
        }
        return extended.degree(a.v) > extended.degree(b.v);  // POPRAWKA: malejąco (większy stopień to lepiej)
    });
    return candidates;
}

// Aktualizuje graf `extended` dodając brakujące krawędzie po przypisaniu mapowania u -> v.
void addMissingEdges(const uint32_t u, const uint32_t v, const Graph& g1, Graph &extended, const std::vector<int> &mapping) {
    for (int i = 0; i < g1.n; ++i) {
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
    
    // POPRAWKA: Dodaj obsługę pętli (self-loop)
    const int reqSelfLoop = g1.matrix[u][u];
    int& currSelfLoop = extended.matrix[v][v];
    if (currSelfLoop < reqSelfLoop) {
        currSelfLoop = reqSelfLoop;
    }
}

// TODO: Zapewnienie odnalezienia rodziny mapowań -> trzeba to zapewnic tutaj, dodajac jakies checki
Solution initializeApproximateExpansion(const Graph &g1, const Graph &g2, const uint32_t copiesCount) {
    auto extended = g2;
    auto mappings = Mappings(copiesCount, extended.n);
    const auto order = g1.verticesOrder();
    auto cost = 0;
    
    // Helper: sprawdź czy obraz bieżącej kopii jest unikalny
    auto isImageUniqueApprox = [&](uint32_t currentCopy) -> bool {
        if (currentCopy == 0) return true;
        
        std::vector<int> currentImage;
        for (uint32_t i = 0; i < static_cast<uint32_t>(g1.n); ++i) {
            if (mappings.maps[currentCopy][i] != Mappings::NO_MAPPING) {
                currentImage.push_back(mappings.maps[currentCopy][i]);
            }
        }
        std::sort(currentImage.begin(), currentImage.end());
        
        for (uint32_t prevCopy = 0; prevCopy < currentCopy; ++prevCopy) {
            std::vector<int> prevImage;
            for (uint32_t i = 0; i < static_cast<uint32_t>(g1.n); ++i) {
                if (mappings.maps[prevCopy][i] != Mappings::NO_MAPPING) {
                    prevImage.push_back(mappings.maps[prevCopy][i]);
                }
            }
            std::sort(prevImage.begin(), prevImage.end());
            if (currentImage == prevImage) {
                return false;
            }
        }
        return true;
    };
    
    for (uint32_t i = 0; i < copiesCount; ++i) {
        bool prefixEqual = true;
        std::vector<int32_t> mPrevious;
        if (i == 0) {
            mPrevious = std::vector<int32_t>(g1.n, -1);  // POPRAWKA: -1 zamiast UINT32_MAX dla porównań
        } else {
            mPrevious = mappings.maps[i - 1];
        }
        for (uint32_t j = 0; j < static_cast<uint32_t>(g1.n); ++j) {
            const auto u = order[j];
            const auto candidates = chooseCandidates(u, g1, g2, extended, mappings.maps[i]);
            
            uint32_t v = UINT32_MAX;
            uint32_t candCost = 0;
            
            for (const auto &candidate : candidates) {
                if (prefixEqual) {
                    // POPRAWKA: Warunki porządku leksykograficznego
                    // Dla i-tej kopii wymagamy M_i > M_{i-1} leksykograficznie
                    // W szczególności: jeśli wszystkie poprzednie wierzchołki są takie same,
                    // to obecny MUSI być >= poprzedniego
                    if (static_cast<int>(candidate.v) < mPrevious[u]) {
                        continue;
                    }
                    // DODATKOWY WARUNEK: jeśli to ostatni wierzchołek i wszystkie wcześniejsze
                    // były równe, to ten MUSI być > (żeby cały tuple był większy)
                    if (j == static_cast<uint32_t>(g1.n - 1)) {
                        bool allPreviousEqual = true;
                        for (uint32_t prev_j = 0; prev_j < j; ++prev_j) {
                            const auto prev_u = order[prev_j];
                            if (mappings.maps[i][prev_u] != mPrevious[prev_u]) {
                                allPreviousEqual = false;
                                break;
                            }
                        }
                        if (allPreviousEqual && static_cast<int>(candidate.v) <= mPrevious[u]) {
                            continue;
                        }
                    }
                }
                // Kandydat spelnia wymagania, mozemy pominac kolejnych
                v = candidate.v;
                candCost = candidate.deltaCost;
                break;
            }
            
            // POPRAWKA: Sprawdź czy znaleziono kandydata
            if (v == UINT32_MAX) {
                // Nie znaleziono poprawnego kandydata - coś poszło nie tak
                // To może się zdarzyć gdy brak wystarczającej liczby wierzchołków
                // Wróć do pierwszego dostępnego
                if (!candidates.empty()) {
                    v = candidates[0].v;
                    candCost = candidates[0].deltaCost;
                }
            }
            
            mappings.maps[i][u] = v;
            cost += candCost;
            addMissingEdges(u, v, g1, extended, mappings.maps[i]);
            prefixEqual = prefixEqual && (static_cast<int>(v) == mPrevious[u]);
        }
        
        // POPRAWKA: Sprawdź unikalność obrazu po zakończeniu mapowania kopii
        // Jeśli obraz nie jest unikalny, trzeba znaleźć inne mapowanie
        if (!isImageUniqueApprox(i)) {
            // Spróbuj znaleźć alternatywne mapowanie zmieniając kolejne wierzchołki od końca
            bool foundUnique = false;
            for (int attemptVertex = static_cast<int>(g1.n) - 1; attemptVertex >= 0 && !foundUnique; --attemptVertex) {
                const auto u = order[attemptVertex];
                const int oldV = mappings.maps[i][u];
                
                // Cofnij mapowanie tego wierzchołka
                mappings.maps[i][u] = Mappings::NO_MAPPING;
                
                const auto candidates = chooseCandidates(u, g1, g2, extended, mappings.maps[i]);
                
                for (const auto &candidate : candidates) {
                    if (static_cast<int>(candidate.v) == oldV) continue; // Pomiń poprzedni wybór
                    
                    mappings.maps[i][u] = candidate.v;
                    addMissingEdges(u, candidate.v, g1, extended, mappings.maps[i]);
                    
                    if (isImageUniqueApprox(i)) {
                        // Znaleziono unikalny obraz!
                        foundUnique = true;
                        cost += candidate.deltaCost;
                        break;
                    }
                }
                
                if (!foundUnique) {
                    // Przywróć poprzednie mapowanie
                    mappings.maps[i][u] = oldV;
                    addMissingEdges(u, oldV, g1, extended, mappings.maps[i]);
                }
            }
            
            // Jeśli nadal nie znaleziono unikalnego obrazu, zwróć NO_SOLUTION
            if (!foundUnique) {
                Solution noSolution;
                noSolution.found = false;
                noSolution.cost = UINT64_MAX;
                return noSolution;
            }
        }

    }
    auto solution = Solution(std::move(extended), std::move(mappings), cost);
    solution.found = true; // Udało się znaleźć mapowania
    return solution;
}


Solution ImproveApproximateExpansion(Solution s, Graph g1 /* smaller graph */, Graph g2 /* bigger graph */) {
    // POPRAWKA: Jeśli wejściowe rozwiązanie nie zostało znalezione, zwróć je bez zmian
    if (!s.found) {
        return s;
    }
    
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
                    int delta = 0;  // POPRAWKA: inicjalizacja na 0!
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
                        if (vIterator != s.mappings.maps[copynr].end()) {  // POPRAWKA: vIterator zamiast it!
                            int vertexMappedOnV = distance(s.mappings.maps[copynr].begin(), vIterator); // POPRAWKA: copynr i vIterator!
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
                            int vertexMappedToOldUMapping = distance(s.mappings.maps[copynr].begin(), oldUMappingIterator); // POPRAWKA: copynr i oldUMappingIterator!
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
                    // POPRAWKA: Odfiltruj NO_MAPPING przed utworzeniem zbioru!
                    set<int> vset;
                    for (int val : s.mappings.maps[i]) {
                        if (val != Mappings::NO_MAPPING) {
                            vset.insert(val);
                        }
                    }
                    s.mappings.maps[i] = currentMapping;

                    if (delta < bestDelta) {

                        // sprawdzenie czy żadne inne mapowanie nie zawiera dokladnie tych samych wiezrchołków
                        bool isMappingValid = true;
                        for (const auto& mp : s.mappings.maps) {
                            std::set<int> mpSet;
                            for (int val : mp) {
                                if (val != Mappings::NO_MAPPING) {
                                    mpSet.insert(val);
                                }
                            }
                            if (mpSet == vset) {
                                isMappingValid = false;
                                break;
                            }
                        }

                        if (isMappingValid) {
                            bestDelta = delta;
                            copyToModify = i;
                            newBestMapping = newMapping;
                            matrixForNewBestMapping = modifiedMatrix;
                        }
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

    // POPRAWKA: Przelicz koszt od zera na samym końcu, aby uniknąć błędów akumulacji (drift)
    // w skomplikowanej logice delta.
    uint64_t trueCost = 0;
    for(int i=0; i<s.extendedGraph.n; ++i) {
        for(int j=0; j<s.extendedGraph.n; ++j) {
            if (s.extendedGraph.matrix[i][j] > g2.matrix[i][j]) {
                trueCost += (s.extendedGraph.matrix[i][j] - g2.matrix[i][j]);
            }
        }
    }
    s.cost = trueCost;

    return s;
}

// Funkcja pomocnicza: sprawdza czy obraz mapowania jest różny od wszystkich poprzednich kopii
// KLUCZOWE: Im(Mi) ≠ Im(Mj) dla i ≠ j
bool isImageUnique(const Mappings& mappings, int currentCopy, int n) {
    if (currentCopy == 0) return true; // Pierwsza kopia zawsze unikalna
    
    // Zbierz obraz bieżącej kopii (posortowany)
    std::vector<int> currentImage;
    for (int i = 0; i < n; ++i) {
        if (mappings.maps[currentCopy][i] != Mappings::NO_MAPPING) {
            currentImage.push_back(mappings.maps[currentCopy][i]);
        }
    }
    std::sort(currentImage.begin(), currentImage.end());
    
    // Porównaj z obrazami wszystkich poprzednich kopii
    for (int prevCopy = 0; prevCopy < currentCopy; ++prevCopy) {
        std::vector<int> prevImage;
        for (int i = 0; i < n; ++i) {
            if (mappings.maps[prevCopy][i] != Mappings::NO_MAPPING) {
                prevImage.push_back(mappings.maps[prevCopy][i]);
            }
        }
        std::sort(prevImage.begin(), prevImage.end());
        
        // Jeśli obrazy identyczne - BŁĄD!
        if (currentImage == prevImage) {
            return false;
        }
    }
    
    return true;
}

// Funkcja pomocnicza: oblicza C(n, k) = n! / (k! * (n-k)!)
// Używana do sprawdzenia czy jest wystarczająco dużo różnych n1-elementowych podzbiorów
uint64_t binomialCoefficient(int n, int k) {
    if (k > n) return 0;
    if (k == 0 || k == n) return 1;
    if (k > n - k) k = n - k; // C(n,k) = C(n,n-k)
    
    uint64_t result = 1;
    for (int i = 0; i < k; ++i) {
        result *= (n - i);
        result /= (i + 1);
    }
    return result;
}

Solution approximateExpansion(const Graph& g1, const Graph& g2, const uint32_t copies_count) {
    const auto initialExpansion = initializeApproximateExpansion(g1, g2, copies_count);
    auto result = initialExpansion;
    result.found = true;
    return ImproveApproximateExpansion(result, g1, g2);
}

// Algorytm dokładny - funkcja rekurencyjna
// Zgodnie z sekcją 3.7 dokumentacji: RozgałęzienieRekurencyjne
void recursiveBranching(
    int copyIndex,           // i - numer bieżącej kopii (0..k-1)
    int vertexIndex,         // j - indeks wierzchołka w porządku P (0..n1-1)
    const std::vector<uint32_t>& order,  // P - porządek wierzchołków G1
    const Graph& g1,         // Mniejszy graf
    const Graph& g2,         // Większy graf (oryginalny)
    Graph& gExtended,        // G'_2 - aktualnie rozszerzony graf
    Mappings& mappings,      // Aktualne mapowania dla wszystkich kopii
    uint64_t currentCost,    // n - bieżący koszt
    bool prefixEqual,        // czy wcześniejsze przypisania w M_i są takie same jak w M_{i-1}
    Solution& bestSolution,  // Globalne najlepsze rozwiązanie (in/out)
    const int k              // Liczba kopii
) {
    // Jeśli zmapowaliśmy już wszystkie wierzchołki bieżącej kopii
    if (vertexIndex >= g1.n) {
        // WALIDACJA: Sprawdź czy obraz jest unikalny!
        if (!isImageUnique(mappings, copyIndex, g1.n)) {
            return; // Duplikat obrazu - odrzuć to rozwiązanie
        }
        
        if (copyIndex == k - 1) {
            // Znaleźliśmy kompletne mapowanie wszystkich k kopii
            if (currentCost < bestSolution.cost) {
                bestSolution.cost = currentCost;
                bestSolution.extendedGraph = gExtended;
                bestSolution.mappings = mappings;
                bestSolution.found = true;
            }
        } else {
            // Przechodzimy do kolejnej kopii
            recursiveBranching(copyIndex + 1, 0, order, g1, g2, gExtended, 
                             mappings, currentCost, true, bestSolution, k);
        }
        return;
    }

    // Przycinanie gałęzi - ale tylko jeśli już znaleźliśmy jakieś rozwiązanie
    // POPRAWKA: Nie przycinaj jeśli jeszcze nie mamy rozwiązania!
    if (bestSolution.found && currentCost >= bestSolution.cost) {
        return;
    }

    const uint32_t u = order[vertexIndex];  // Bieżący wierzchołek G1 do zmapowania
    
    // Wybierz kandydatów zgodnie z heurystyką z sekcji 3.3
    const auto candidates = chooseCandidates(u, g1, g2, gExtended, mappings.maps[copyIndex]);

    for (const auto& candidate : candidates) {
        const uint32_t v = candidate.v;
        const uint32_t deltaCost = candidate.deltaCost;

        // Sprawdzenie porządku leksykograficznego (sekcja 3.4)
        if (copyIndex > 0 && prefixEqual) {
            const int prevMapping = mappings.maps[copyIndex - 1][u];
            // Jeśli prefix jest równy, obecny wierzchołek MUSI być >= poprzedniego
            if (static_cast<int>(v) < prevMapping) {
                continue;
            }
            // Jeśli to ostatni wierzchołek i wszystkie poprzednie były równe,
            // to ten MUSI być > (żeby całe mapowanie było różne)
            if (vertexIndex == g1.n - 1 && static_cast<int>(v) <= prevMapping) {
                continue;
            }
        }
        
        // POPRAWKA: Wcześniejsze sprawdzenie czy tworzymy duplikat obrazu
        // Budujemy tymczasowy obraz bieżącego mapowania z nowym v
        if (copyIndex > 0 && vertexIndex == g1.n - 1) {
            std::vector<int> currentImage;
            for (int idx = 0; idx < g1.n; ++idx) {
                if (idx == static_cast<int>(u)) {
                    currentImage.push_back(v);
                } else if (mappings.maps[copyIndex][idx] != Mappings::NO_MAPPING) {
                    currentImage.push_back(mappings.maps[copyIndex][idx]);
                }
            }
            std::sort(currentImage.begin(), currentImage.end());
            
            // Sprawdź czy ten obraz już istnieje w poprzednich kopiach
            bool isDuplicate = false;
            for (int prevCopy = 0; prevCopy < copyIndex; ++prevCopy) {
                std::vector<int> prevImage;
                for (int idx = 0; idx < g1.n; ++idx) {
                    if (mappings.maps[prevCopy][idx] != Mappings::NO_MAPPING) {
                        prevImage.push_back(mappings.maps[prevCopy][idx]);
                    }
                }
                std::sort(prevImage.begin(), prevImage.end());
                if (currentImage == prevImage) {
                    isDuplicate = true;
                    break;
                }
            }
            if (isDuplicate) {
                continue; // Pomiń ten kandydat - tworzy duplikat
            }
        }

        // Sprawdź, czy v nie jest już użyty w bieżącej kopii
        bool vAlreadyUsed = false;
        for (int idx = 0; idx < g1.n; ++idx) {
            if (mappings.maps[copyIndex][idx] == static_cast<int>(v)) {
                vAlreadyUsed = true;
                break;
            }
        }
        if (vAlreadyUsed) {
            continue;
        }

        // Przypisanie
        mappings.maps[copyIndex][u] = v;
        const uint64_t newCost = currentCost + deltaCost;

        // Przycinanie - możemy przerwać bo kandydaci są posortowani rosnąco wg kosztu
        if (newCost >= bestSolution.cost) {
            mappings.maps[copyIndex][u] = Mappings::NO_MAPPING;
            break;
        }

        // Zapisz stan grafu przed modyfikacją (do cofnięcia)
        std::vector<std::pair<std::pair<int,int>, int>> edgeChanges;
        
        // Aktualizuj G'_2 o brakujące krawędzie
        for (uint32_t i = 0; i < g1.n; ++i) {
            const int mappedI = mappings.maps[copyIndex][i];
            if (mappedI == Mappings::NO_MAPPING) {
                continue;
            }

            const int reqOut = g1.matrix[u][i];
            const int reqIn = g1.matrix[i][u];
            
            int& currOut = gExtended.matrix[v][mappedI];
            int& currIn = gExtended.matrix[mappedI][v];

            if (currOut < reqOut) {
                edgeChanges.push_back({{v, mappedI}, currOut});
                currOut = reqOut;
            }
            if (currIn < reqIn) {
                edgeChanges.push_back({{mappedI, v}, currIn});
                currIn = reqIn;
            }
        }
        
        // POPRAWKA: Dodaj obsługę pętli (self-loop) dla wierzchołka u
        const int reqSelfLoop = g1.matrix[u][u];
        int& currSelfLoop = gExtended.matrix[v][v];
        if (currSelfLoop < reqSelfLoop) {
            edgeChanges.push_back({{v, v}, currSelfLoop});
            currSelfLoop = reqSelfLoop;
        }

        // Sprawdź czy prefix jest równy
        const bool newPrefixEqual = copyIndex > 0 && prefixEqual && 
                                   (static_cast<int>(v) == mappings.maps[copyIndex - 1][u]);

        // Wywołanie rekurencyjne
        recursiveBranching(copyIndex, vertexIndex + 1, order, g1, g2, gExtended,
                         mappings, newCost, newPrefixEqual, bestSolution, k);

        // Cofnij zmiany w G'_2
        for (const auto& change : edgeChanges) {
            gExtended.matrix[change.first.first][change.first.second] = change.second;
        }

        // Cofnij mapowanie
        mappings.maps[copyIndex][u] = Mappings::NO_MAPPING;
    }
}

// Algorytm dokładny - główna funkcja
// Zgodnie z sekcją 3.7 dokumentacji: AlgorytmDokładny
Solution exactAlgorithm(const Graph& g1, const Graph& g2, const int k) {
    // Wyznacz porządek wierzchołków P
    const auto order = g1.verticesOrder();

    // Inicjalizacja
    Graph gExtended = g2;
    Mappings mappings(k, g1.n);
    Solution bestSolution;
    bestSolution.cost = UINT64_MAX;
    bestSolution.found = false;

    // Wywołaj rekurencję
    recursiveBranching(0, 0, order, g1, g2, gExtended, mappings, 
                      0, false, bestSolution, k);

    return bestSolution;
}

// Walidacja wejścia - wyświetla informacje pomocnicze
bool validateInput(int n1, int n2, int k, bool verbose = true) {
    const uint64_t maxDifferentMappings = binomialCoefficient(n2, n1);
    
    if (verbose) {
        std::cout << "Walidacja: k=" << k << ", n1=" << n1 << ", n2=" << n2 << std::endl;
        std::cout << "  C(n2,n1) = C(" << n2 << "," << n1 << ") = " << maxDifferentMappings << std::endl;
    }

    if (static_cast<uint64_t>(k) > maxDifferentMappings) {
        if (verbose) {
            std::cout << "  BŁĄD: k > C(n2,n1) - matematycznie niemożliwe!" << std::endl;
        }
        return false;
    }
    
    return true;
}

// Wczytywanie grafów z pliku
// Format zgodnie z emailem: n1, macierz G1, n2, macierz G2, [k]
bool loadGraphsFromFile(const std::string& filename, Graph& g1, Graph& g2, int& k) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Nie można otworzyć pliku: " << filename << std::endl;
        return false;
    }

    // Wczytaj n1
    int n1;
    file >> n1;
    if (n1 <= 0) {
        std::cerr << "Nieprawidłowa liczba wierzchołków G1: " << n1 << std::endl;
        return false;
    }

    g1 = Graph(n1);
    // Wczytaj macierz sąsiedztwa G1
    for (int i = 0; i < n1; ++i) {
        for (int j = 0; j < n1; ++j) {
            file >> g1.matrix[i][j];
        }
    }

    // Wczytaj n2
    int n2;
    file >> n2;
    if (n2 <= 0) {
        std::cerr << "Nieprawidłowa liczba wierzchołków G2: " << n2 << std::endl;
        return false;
    }

    g2 = Graph(n2);
    // Wczytaj macierz sąsiedztwa G2
    for (int i = 0; i < n2; ++i) {
        for (int j = 0; j < n2; ++j) {
            file >> g2.matrix[i][j];
        }
    }

    // Wczytaj k (opcjonalnie, domyślnie 1)
    if (file >> k) {
        if (k <= 0) {
            std::cerr << "Nieprawidłowa liczba kopii k: " << k << std::endl;
            return false;
        }
    } else {
        k = 1;
    }

    file.close();
    return true;
}

// Wypisz graf
void printGraph(const Graph& g, const std::string& name) {
    std::cout << name << " (n=" << g.n << ", m=" << g.totalEdges() << "):" << std::endl;
    for (int i = 0; i < g.n; ++i) {
        for (int j = 0; j < g.n; ++j) {
            std::cout << g.matrix[i][j];
            if (j < g.n - 1) std::cout << " ";
        }
        std::cout << std::endl;
    }
    std::cout << std::endl;
}

// Wypisz rozwiązanie
void printSolution(const Solution& sol, const Graph& g2, const std::string& algName, int n1, int n2, int k) {
    std::cout << "\n=== Wyniki algorytmu " << algName << " ===" << std::endl;
    if (!sol.found || sol.cost == UINT64_MAX) {
        std::cout << "Nie znaleziono rozwiązania." << std::endl;
        std::cout << "\nMożliwe przyczyny:" << std::endl;
        const uint64_t maxMappings = binomialCoefficient(n2, n1);
        std::cout << "1. k > C(n2,n1): " << k << " > C(" << n2 << "," << n1 << ")=" << maxMappings;
        if (static_cast<uint64_t>(k) > maxMappings) {
            std::cout << " ← PROBLEM!" << std::endl;
            std::cout << "   Matematycznie niemożliwe: potrzeba " << k << " różnych " 
                      << n1 << "-elementowych PODZBIORÓW" << std::endl;
            std::cout << "   z " << n2 << "-elementowego zbioru, a jest maksymalnie " << maxMappings << std::endl;
        } else {
            std::cout << " (OK)" << std::endl;
        }
        
        if (k * n1 > n2) {
            std::cout << "2. k*n1 > n2: " << k << "*" << n1 << "=" << k*n1 << " > " << n2 << std::endl;
            std::cout << "   Niewystarczająca liczba wierzchołków dla rozłącznych obrazów" << std::endl;
        }
        
        std::cout << "3. Struktura grafów uniemożliwia istnienie k różnych izomorfizmów" << std::endl;
        std::cout << "4. Zbyt restrykcyjne warunki krotności krawędzi" << std::endl;
        return;
    }

    std::cout << "Koszt rozszerzenia: " << sol.cost << std::endl;
    std::cout << "Liczba dodanych krawędzi: " << (sol.extendedGraph.totalEdges() - g2.totalEdges()) << std::endl;
    
    std::cout << "\nMapowania:" << std::endl;
    for (int i = 0; i < sol.mappings.k; ++i) {
        std::cout << "  Kopia " << (i+1) << ": ";
        int count = 0;
        for (int j = 0; j < sol.mappings.n; ++j) {
            if (sol.mappings.maps[i][j] != -1) {
                if (count > 0) std::cout << ", ";
                std::cout << j << "->" << sol.mappings.maps[i][j];
                count++;
            }
        }
        std::cout << std::endl;
    }

    std::cout << "\nRozszerzony graf G'_2:" << std::endl;
    printGraph(sol.extendedGraph, "G'_2");
}

void printUsage(const char* programName) {
    std::cout << "Użycie: " << programName << " [plik_z_danymi] [algorytm]" << std::endl;
    std::cout << "  plik_z_danymi - ścieżka do pliku z grafami (opcjonalne, domyślnie wczytuje z stdin)" << std::endl;
    std::cout << "  algorytm      - 'exact' lub 'approx' (opcjonalne, domyślnie 'exact')" << std::endl;
    std::cout << "\nFormat pliku:" << std::endl;
    std::cout << "  n1" << std::endl;
    std::cout << "  macierz_sąsiedztwa_G1 (n1 x n1)" << std::endl;
    std::cout << "  n2" << std::endl;
    std::cout << "  macierz_sąsiedztwa_G2 (n2 x n2)" << std::endl;
    std::cout << "  k (opcjonalne, liczba kopii, domyślnie 1)" << std::endl;
}

int main(int argc, char* argv[]) {
    std::string filename;
    std::string algorithm = "exact";

    // Parsowanie argumentów
    if (argc > 1) {
        filename = argv[1];
        if (filename == "--help" || filename == "-h") {
            printUsage(argv[0]);
            return 0;
        }
    }
    if (argc > 2) {
        algorithm = argv[2];
        if (algorithm != "exact" && algorithm != "approx") {
            std::cerr << "Nieprawidłowy algorytm: " << algorithm << std::endl;
            std::cerr << "Użyj 'exact' lub 'approx'" << std::endl;
            return 1;
        }
    }

    Graph g1, g2;
    int k = 1;

    // Wczytaj dane
    if (!filename.empty()) {
        if (!loadGraphsFromFile(filename, g1, g2, k)) {
            return 1;
        }
    } else {
        std::cout << "Wczytywanie z stdin..." << std::endl;
        std::cout << "Podaj n1: ";
        std::cin >> g1.n;
        g1 = Graph(g1.n);
        std::cout << "Podaj macierz sąsiedztwa G1 (" << g1.n << "x" << g1.n << "):" << std::endl;
        for (int i = 0; i < g1.n; ++i) {
            for (int j = 0; j < g1.n; ++j) {
                std::cin >> g1.matrix[i][j];
            }
        }
        
        std::cout << "Podaj n2: ";
        std::cin >> g2.n;
        g2 = Graph(g2.n);
        std::cout << "Podaj macierz sąsiedztwa G2 (" << g2.n << "x" << g2.n << "):" << std::endl;
        for (int i = 0; i < g2.n; ++i) {
            for (int j = 0; j < g2.n; ++j) {
                std::cin >> g2.matrix[i][j];
            }
        }
        
        std::cout << "Podaj k (liczba kopii): ";
        std::cin >> k;
    }

    // Wypisz dane wejściowe
    std::cout << "\n=== Dane wejściowe ===" << std::endl;
    printGraph(g1, "G1");
    printGraph(g2, "G2");
    std::cout << "Liczba kopii k: " << k << std::endl;
    
    // WALIDACJA WEJŚCIA
    std::cout << "\n=== Walidacja wejścia ===" << std::endl;
    bool inputValid = validateInput(g1.n, g2.n, k, true);
    if (!inputValid) {
        std::cout << "BŁĄD KRYTYCZNY: Parametry wejściowe są niepoprawne (k > C(n2,n1))." << std::endl;
        std::cout << "Prerywanie działania programu." << std::endl;
        return 1;
    } else {
        std::cout << "Parametry wejściowe wyglądają OK." << std::endl;
        const uint64_t maxMappings = binomialCoefficient(g2.n, g1.n);
        std::cout << "k = " << k << " <= C(n2,n1) = C(" << g2.n << "," << g1.n << ") = " << maxMappings << " ✓" << std::endl;
    }

    // Uruchom algorytm
    Solution solution;
    auto startTime = std::chrono::high_resolution_clock::now();
    
    if (algorithm == "exact") {
        std::cout << "\nUruchamianie algorytmu dokładnego..." << std::endl;
        solution = exactAlgorithm(g1, g2, k);
    } else {
        std::cout << "\nUruchamianie algorytmu aproksymacyjnego..." << std::endl;
        solution = approximateExpansion(g1, g2, k);
        // POPRAWKA: Approx może nie znaleźć rozwiązania (gdy k*n1 > n2)
        // solution.found jest już ustawione przez approximateExpansion
    }
    
    auto endTime = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime);

    // Wypisz wyniki
    printSolution(solution, g2, algorithm, g1.n, g2.n, k);
    std::cout << "\nCzas wykonania: " << duration.count() << " ms" << std::endl;

    // Zapisz wynik do pliku output
    std::ofstream outFile("src/output/result.txt");
    if (outFile.is_open()) {
        outFile << "Algorytm: " << algorithm << std::endl;
        outFile << "Koszt: " << solution.cost << std::endl;
        outFile << "Czas: " << duration.count() << " ms" << std::endl;
        outFile << "\nRozszerzony graf G'_2:" << std::endl;
        for (int i = 0; i < solution.extendedGraph.n; ++i) {
            for (int j = 0; j < solution.extendedGraph.n; ++j) {
                outFile << solution.extendedGraph.matrix[i][j];
                if (j < solution.extendedGraph.n - 1) outFile << " ";
            }
            outFile << std::endl;
        }
        outFile.close();
        std::cout << "\nWynik zapisano do src/output/result.txt" << std::endl;
    }

    return 0;
}