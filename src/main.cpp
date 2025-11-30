#include <vector>
#include <algorithm>
#include <set>
#include <cstdint>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <chrono>

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

    // Zwraca wierzcholki w kolejnosci, w jakiej powinny byc rozpatrywane
    // Patrz: "PorzadekWierzcholkow" w dokumentacji
    [[nodiscard]] std::vector<uint32_t> verticesOrder() const {
        std::vector<uint32_t> order(n, 0);

        // edgesToAlreadyAssigned[i] = j oznaczna, ze i-ty wierzcholek ma j krawedzi do juz uporzadkowanych wierzcholkow
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
// Zgodnie z sekcja 3.5 dokumentacji: ObliczKoszt
int countCost(const int u, const int v, const Graph &G1, const Graph &G2Extended, const std::vector<int> &mapping) {
    int costIncrease = 0;
    for (size_t i = 0; i < mapping.size(); i++) {
        if (mapping[i] == Mappings::NO_MAPPING) {
            continue;  // Pomijamy niezmapowane wierzcholki
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
    
    // Dodaj koszt petli (self-loop)
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

    // Dodaj pokrycie petli (self-loop)
    int reqSelfLoop = g1.matrix[u][u];
    int haveSelfLoop = extended.matrix[v][v];
    covered += std::min(reqSelfLoop, haveSelfLoop);

    return covered;
}

Candidates chooseCandidates(const uint32_t u, const Graph& g1, const Graph &g2, const Graph &extended, const std::vector<int> &mapping) {
    auto candidates = std::vector<Candidate>();

    // Znajdz wierzcholki juz uzyte w biezacym mapowaniu
    std::set<int> usedVertices;
    for (int mappedVertex : mapping) {
        if (mappedVertex != Mappings::NO_MAPPING) {
            usedVertices.insert(mappedVertex);
        }
    }

    for (int v = 0; v < g2.n; ++v) {
        // Pomin wierzcholki juz uzyte w biezacej kopii
        if (usedVertices.count(v)) {
            continue;
        }
        
        const auto deltaCost = countCost(u, v, g1, extended, mapping);
        const auto deltaExist = computeDeltaExist(u, v, g1, extended, mapping);

        candidates.emplace_back(v, deltaCost, deltaExist);
    }

    // Sortowanie zgodnie z sekcja 3.3 dokumentacji:
    // 1. Maksymalizacja zgodnosci (deltaExist - wiecej lepiej, wiec malejaco)
    // 2. Minimalizacja przyrostu kosztu (deltaCost - mniej lepiej, wiec rosnaco)
    // 3. Maksymalny stopien wierzcholka (wiecej lepiej, wiec malejaco)
    std::sort(candidates.begin(), candidates.end(), [&extended](const Candidate &a, const Candidate &b) {
        if (a.deltaExist != b.deltaExist) {
            return a.deltaExist > b.deltaExist;
        }
        if (a.deltaCost != b.deltaCost) {
            return a.deltaCost < b.deltaCost;
        }
        return extended.degree(a.v) > extended.degree(b.v);
    });
    return candidates;
}

// Aktualizuje graf `extended` dodajac brakujace krawedzie po przypisaniu mapowania u -> v.
void addMissingEdges(const uint32_t u, const uint32_t v, const Graph& g1, Graph &extended, const std::vector<int> &mapping) {
    for (int i = 0; i < g1.n; ++i) {
        const auto mapped = mapping[i];
        // Pomijamy dla niezmappowanych wierzcholkow
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
    
    // Dodaj obsluge petli (self-loop)
    const int reqSelfLoop = g1.matrix[u][u];
    int& currSelfLoop = extended.matrix[v][v];
    if (currSelfLoop < reqSelfLoop) {
        currSelfLoop = reqSelfLoop;
    }
}

// Forward declaration dla exactAlgorithm (potrzebne dla initializeApproximateExpansion)
Solution exactAlgorithm(const Graph& g1, const Graph& g2, int k, bool oneBranch);

// Inicjalizacja rozszerzenia aproksymacyjnego
Solution initializeApproximateExpansion(const Graph &g1, const Graph &g2, const uint32_t copiesCount) {
    if (copiesCount == 0) {
        Solution noSolution;
        noSolution.found = false;
        noSolution.cost = UINT64_MAX;
        return noSolution;
    }
    
    // Użyj algorytmu dokładnego dla k=1 aby znaleźć pierwszą kopię
    Solution firstCopy = exactAlgorithm(g1, g2, 1, true);
    
    if (!firstCopy.found || firstCopy.cost == UINT64_MAX) {
        // Nie udało się znaleźć nawet jednej kopii
        Solution noSolution;
        noSolution.found = false;
        noSolution.cost = UINT64_MAX;
        return noSolution;
    }
    
    // Jeśli potrzebujemy tylko jednej kopii, zwracamy
    if (copiesCount == 1) {
        return firstCopy;
    }
    
    // Dla kolejnych kopii (i >= 1) modyfikujemy mapowanie
    auto extended = firstCopy.extendedGraph;
    auto mappings = Mappings(copiesCount, g1.n);
    
    // Przepisz pierwszą kopię
    mappings.maps[0] = firstCopy.mappings.maps[0];
    uint64_t cost = firstCopy.cost;
    
    const auto order = g1.verticesOrder();
    
    // Helper: sprawdza czy obraz i-tej kopii różni się od wszystkich poprzednich
    auto isImageUnique = [&](uint32_t currentCopy) -> bool {
        std::vector<int> currentImage;
        for (int u = 0; u < g1.n; ++u) {
            if (mappings.maps[currentCopy][u] != Mappings::NO_MAPPING) {
                currentImage.push_back(mappings.maps[currentCopy][u]);
            }
        }
        std::sort(currentImage.begin(), currentImage.end());
        
        for (uint32_t prevCopy = 0; prevCopy < currentCopy; ++prevCopy) {
            std::vector<int> prevImage;
            for (int u = 0; u < g1.n; ++u) {
                if (mappings.maps[prevCopy][u] != Mappings::NO_MAPPING) {
                    prevImage.push_back(mappings.maps[prevCopy][u]);
                }
            }
            std::sort(prevImage.begin(), prevImage.end());
            
            if (currentImage == prevImage) {
                return false;
            }
        }
        return true;
    };
    
    // Dla każdej kolejnej kopii (i = 1, 2, ..., copiesCount-1)
    for (uint32_t copyIdx = 1; copyIdx < copiesCount; ++copyIdx) {
        // Skopiuj poprzednią kopię jako punkt startowy
        mappings.maps[copyIdx] = mappings.maps[copyIdx - 1];
        
        bool foundUnique = false;
        
        // Próbujemy modyfikować wierzchołki od końca do początku
        for (int vertexIdx = static_cast<int>(g1.n) - 1; vertexIdx >= 0 && !foundUnique; --vertexIdx) {
            const auto u = order[vertexIdx];
            
            // Zbierz wszystkie możliwe kandydaty dla tego wierzchołka
            // (które nie są już użyte w bieżącym mapowaniu)
            std::set<int> usedVertices;
            for (int j = 0; j < g1.n; ++j) {
                if (j != static_cast<int>(u) && mappings.maps[copyIdx][j] != Mappings::NO_MAPPING) {
                    usedVertices.insert(mappings.maps[copyIdx][j]);
                }
            }
            
            // Próbuj każdego możliwego v z G2
            for (int v = 0; v < g2.n; ++v) {
                // Pomiń wierzchołki już użyte w tym mapowaniu
                if (usedVertices.count(v)) {
                    continue;
                }
                
                // Zapisz stare mapowanie
                int oldV = mappings.maps[copyIdx][u];
                
                // Ustaw nowe mapowanie
                mappings.maps[copyIdx][u] = v;
                
                // Sprawdź czy to mapowanie jest izomorficzne z G1
                // oraz oblicz dodatkowy koszt dla tego mapowania
                bool isValidMapping = true;
                uint64_t additionalCost = 0;
                
                for (int x = 0; x < g1.n; ++x) {
                    int mappedX = mappings.maps[copyIdx][x];
                    if (mappedX == Mappings::NO_MAPPING) continue;
                    
                    for (int y = 0; y < g1.n; ++y) {
                        int mappedY = mappings.maps[copyIdx][y];
                        if (mappedY == Mappings::NO_MAPPING) continue;
                        
                        int reqEdges = g1.matrix[x][y];
                        int haveEdges = extended.matrix[mappedX][mappedY];
                        
                        if (reqEdges > haveEdges) {
                            additionalCost += (reqEdges - haveEdges);
                        }
                    }
                }
                
                // Sprawdź czy obraz jest unikalny
                if (isValidMapping && isImageUnique(copyIdx)) {
                    // Znaleźliśmy unikalne mapowanie!
                    // Dodaj brakujące krawędzie do extended
                    for (int x = 0; x < g1.n; ++x) {
                        int mappedX = mappings.maps[copyIdx][x];
                        if (mappedX == Mappings::NO_MAPPING) continue;
                        
                        for (int y = 0; y < g1.n; ++y) {
                            int mappedY = mappings.maps[copyIdx][y];
                            if (mappedY == Mappings::NO_MAPPING) continue;
                            
                            int reqEdges = g1.matrix[x][y];
                            int& haveEdges = extended.matrix[mappedX][mappedY];
                            
                            if (reqEdges > haveEdges) {
                                haveEdges = reqEdges;
                            }
                        }
                    }
                    
                    cost += additionalCost;
                    foundUnique = true;
                    break;
                }
                
                // Przywróć stare mapowanie jeśli nie znaleziono
                mappings.maps[copyIdx][u] = oldV;
            }
        }
        
        // Jeśli nie znaleziono unikalnego mapowania dla tej kopii, zwróć błąd
        if (!foundUnique) {
            Solution noSolution;
            noSolution.found = false;
            noSolution.cost = UINT64_MAX;
            return noSolution;
        }
    }
    
    auto solution = Solution(std::move(extended), std::move(mappings), cost);
    solution.found = true;
    return solution;
}

// Funkcja usuwa krawędzie, które zostały dodane do wierzchołków v1 i v2 w rozszerzonym grafie. Zwraca koszt tej operacji.
int deleteEdgesAddedToVertices(vector<vector<int>>& modifiedExtendedGraph, int v1, int v2, Graph& g2) {
    int delta = 0;
    for (int k = 0; k < modifiedExtendedGraph.size(); k++) {
        delta -= (modifiedExtendedGraph[v2][k] - g2.matrix[v2][k]);
        modifiedExtendedGraph[v2][k] = g2.matrix[v2][k];
        delta -= (modifiedExtendedGraph[v1][k] - g2.matrix[v1][k]);
        modifiedExtendedGraph[v1][k] = g2.matrix[v1][k];
        delta -= (modifiedExtendedGraph[k][v2] - g2.matrix[k][v2]);
        modifiedExtendedGraph[k][v2] = g2.matrix[k][v2];
        delta -= (modifiedExtendedGraph[k][v1] - g2.matrix[k][v1]);
        modifiedExtendedGraph[k][v1] = g2.matrix[k][v1];
    }
    return delta;
}

// Funkcja dodaje krawędzie do rozszerzonego grafu, tak by wszystkie mapowania na wierzchołek v były poprawne, Zwraca koszt operacji
int addEdgesForGivenVertex(Mappings& mappings, Graph& g1, vector<vector<int>>& modifiedExtendedGraph, int v) {
    int delta = 0;
    for (int copynr = 0; copynr < mappings.k; copynr++) {

        // sprawdz czy v jest czyims mapowaniem w kopii copynr
        auto vIterator = std::find(mappings.maps[copynr].begin(), mappings.maps[copynr].end(), v); 
        if (vIterator != mappings.maps[copynr].end()) { 
            int vertexMappedOnV = distance(mappings.maps[copynr].begin(), vIterator);

            // dla każdego potencjalnego sąsiada v
            for (int n = 0; n < g1.n; n++) { 

                // sprawdzenie czy z mapowania n wychodzi odpowiednia ilosc wierzchołkow do v i ewentualne dodanie brakujacych krawedzi
                int mappingOfN = mappings.maps[copynr][n]; 
                int reqIn = g1.matrix[n][vertexMappedOnV]; 
                int currIn = modifiedExtendedGraph[mappingOfN][v]; 
                if (reqIn > currIn) {
                    modifiedExtendedGraph[mappingOfN][v] = reqIn;
                    delta += (reqIn - currIn);
                }

                // sprawdzenie czy z v wychodzi odpowiednia ilosc wierzchołkow do mapowania n i ewentualne dodanie brakujacych krawedzi
                int reqOut = g1.matrix[vertexMappedOnV][n]; 
                int currOut = modifiedExtendedGraph[v][mappingOfN]; 
                if (reqOut > currOut) {
                    modifiedExtendedGraph[v][mappings.maps[copynr][n]] = reqOut;
                    delta += (reqOut - currOut);
                }
            }
        }
    }

    return delta;
}

struct BetterSolution {
    bool ifFound;
    int copyId;
    vector<int> newMapping;
    vector<vector<int>> newAdjacencyMatrix;
};

Solution ImproveApproximateExpansion(Solution s, Graph g1 , Graph g2) {

    // Jesli wejsciowe rozwiazanie nie zostalo znalezione, zwroc je bez zmian
    if (!s.found) {
        return s;
    }
    
    bool improved = true; 
    int bestDelta;  
    BetterSolution betterSolution;
    while (improved) {
        improved = false; 
        bestDelta = 0;
        betterSolution.ifFound = false;

        // wybor kopii, w ktorej szukamy lepszego mapowania
        for (int i = 0; i < s.mappings.k; i++) {
            // wybor wierzcholka ktory dostanie nowe mapowanie
            for (int u = 0; u < g1.n; u++) { 
                // wybor nowego mapowania dla wierzchołka u
                for (int v = 0; v < g2.n; v++) { 

                    // Kopia rozszerzonego grafu, na której będą przeporowadzane modyfikacje
                    vector<vector<int>> modifiedExtendedGraph = s.extendedGraph.matrix;

                    vector<int> oldMapping = s.mappings.maps[i];
                    int oldUMapping;
                    int delta;

                    // Szukamy czy jakis wierzcholek w aktualnej kopii jest juz zmapowany na v
                    auto it = std::find(s.mappings.maps[i].begin(), s.mappings.maps[i].end(), v);

                    // Jezeli jakis wierzcholek w jest juz zmapowany na v to zmieniamy mapowanie
                    // tak, ze u jest mapowany na v a w jest mapowany na stare mapowanie u
                    if (it != s.mappings.maps[i].end()) { // jezeli jakis wierzcholek z G1 juz jest mapowany n v
                        int vertexMappedToV = distance(s.mappings.maps[i].begin(), it); 
                        oldUMapping = s.mappings.maps[i][u]; 
                        swap(s.mappings.maps[i][vertexMappedToV], s.mappings.maps[i][u]);
                    }
                    // Jezeli zaden wierzcholek nie jest mapowany na v to ustawiamy mapowanie u na v
                    else {
                        oldUMapping = s.mappings.maps[i][u]; 
                        s.mappings.maps[i][u] = v;
                    }

                    // Ustawiamy liczności wszystkich krawędzie, wchodzących i wychodzących do v i starego mapowania u
                    // na wartości z niezmodyfikowanego G2, poniewaz, przez zmiane mapowania, tylko one mogly zmienic
                    // swoja licznosc 
                    delta = deleteEdgesAddedToVertices(modifiedExtendedGraph, v, oldUMapping, g2);

                    // Dodajemy krawedzie tak, by wszystkie mapowania we wszystkich kopiach na wierzchołek v działały
                    delta += addEdgesForGivenVertex(s.mappings, g1, modifiedExtendedGraph, v);

                    // Dodajemy krawedzie tak, by wszystkie mapowania we wszystkich kopiach na stare mapowanie u działały
                    delta += addEdgesForGivenVertex(s.mappings, g1, modifiedExtendedGraph, oldUMapping);

                    vector<int> newMapping = s.mappings.maps[i];

                    // Potencjalne nowe mapowanie zamienione na set
                    set<int> vset(s.mappings.maps[i].begin(), s.mappings.maps[i].end());
                    s.mappings.maps[i] = oldMapping;

                    if (delta < bestDelta) {
                        // Sprawdz czy to byl swap (czy v bylo juz w mapowaniu)
                        bool isSwap = false;
                        for (int val : oldMapping) {
                            if (val == v) {
                                isSwap = true;
                                break;
                            }
                        }
                        // sprawdzenie czy zadne inne mapowanie nie zawiera dokladnie tych samych wierzcholkow
                        bool isMappingValid = true;

                        // Jesli to nie byl swap (czyli zmienil sie zbior wartosci), to sprawdzamy unikalnosc.
                        if (!isSwap) {
                            for (const auto& mp : s.mappings.maps) {
                                std::set<int> mpSet(mp.begin(), mp.end());
                                if (mpSet == vset) {
                                    isMappingValid = false;
                                    break;
                                }
                            }
                        }

                        // Jeżeli aktualna zmiana jest korzystniejsza niż najlepsza znaleziona i mapowanie jest prawidłowe
                        // To ustawiamy nowe najlepsze znalezione mapowanie
                        if (isMappingValid) {
                            bestDelta = delta;
                            betterSolution.ifFound = true;
                            betterSolution.copyId = i;
                            betterSolution.newAdjacencyMatrix = modifiedExtendedGraph;
                            betterSolution.newMapping = newMapping;
                        }
                    }
                }
            }
        }

        // Jeżeli znaleziono lepsze mapowanie to podmieniamy je w rozwiązaniu i kontynuujemy algorytm
        if (betterSolution.ifFound) {
            s.mappings.maps[betterSolution.copyId] = betterSolution.newMapping;
            s.extendedGraph.matrix = betterSolution.newAdjacencyMatrix;
            s.cost += bestDelta;
            improved = true;
        }

    }

    return s;
}

// Funkcja pomocnicza: sprawdza czy obraz mapowania jest rozny od wszystkich poprzednich kopii
bool isImageUnique(const Mappings& mappings, int currentCopy, int n) {
    if (currentCopy == 0) return true; // Pierwsza kopia zawsze unikalna
    
    // Zbierz obraz biezacej kopii (posortowany)
    std::vector<int> currentImage;
    for (int i = 0; i < n; ++i) {
        if (mappings.maps[currentCopy][i] != Mappings::NO_MAPPING) {
            currentImage.push_back(mappings.maps[currentCopy][i]);
        }
    }
    std::sort(currentImage.begin(), currentImage.end());
    
    // Porownaj z obrazami wszystkich poprzednich kopii
    for (int prevCopy = 0; prevCopy < currentCopy; ++prevCopy) {
        std::vector<int> prevImage;
        for (int i = 0; i < n; ++i) {
            if (mappings.maps[prevCopy][i] != Mappings::NO_MAPPING) {
                prevImage.push_back(mappings.maps[prevCopy][i]);
            }
        }
        std::sort(prevImage.begin(), prevImage.end());
        
        // Jesli obrazy identyczne - BlaD!
        if (currentImage == prevImage) {
            return false;
        }
    }
    
    return true;
}

// Funkcja pomocnicza: oblicza C(n, k) = n! / (k! * (n-k)!)
// Uzywana do sprawdzenia czy jest wystarczajaco duzo roznych n1-elementowych podzbiorow
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

// Algorytm dokladny - funkcja rekurencyjna
// Zgodnie z sekcja 3.7 dokumentacji: RozgalezienieRekurencyjne
void recursiveBranching(
    int copyIndex,           // i - numer biezacej kopii (0..k-1)
    int vertexIndex,         // j - indeks wierzcholka w porzadku P (0..n1-1)
    const std::vector<uint32_t>& order,  // P - porzadek wierzcholkow G1
    const Graph& g1,         // Mniejszy graf
    const Graph& g2,         // Wiekszy graf (oryginalny)
    Graph& gExtended,        // G'_2 - aktualnie rozszerzony graf
    Mappings& mappings,      // Aktualne mapowania dla wszystkich kopii
    uint64_t currentCost,    // n - biezacy koszt
    bool prefixEqual,        // czy wczesniejsze przypisania w M_i sa takie same jak w M_{i-1}
    Solution& bestSolution,  // Globalne najlepsze rozwiazanie (in/out)
    const int k,              // Liczba kopii
    bool oneBranch
) {
    // Jesli zmapowalismy juz wszystkie wierzcholki biezacej kopii
    if (vertexIndex >= g1.n) {
        // WALIDACJA: Sprawdz czy obraz jest unikalny!
        if (!isImageUnique(mappings, copyIndex, g1.n)) {
            return; // Duplikat obrazu - odrzuc to rozwiazanie
        }
        
        if (copyIndex == k - 1) {
            // Znalezlismy kompletne mapowanie wszystkich k kopii
            if (currentCost < bestSolution.cost) {
                bestSolution.cost = currentCost;
                bestSolution.extendedGraph = gExtended;
                bestSolution.mappings = mappings;
                bestSolution.found = true;
            }
        } else {
            // Przechodzimy do kolejnej kopii
            recursiveBranching(copyIndex + 1, 0, order, g1, g2, gExtended, 
                             mappings, currentCost, true, bestSolution, k, oneBranch);
        }
        return;
    }

    // Przycinanie galezi
    if (bestSolution.found && currentCost >= bestSolution.cost) {
        return;
    }

    const uint32_t u = order[vertexIndex];  // Biezacy wierzcholek G1 do zmapowania
    
    // Wybierz kandydatow zgodnie z heurystyka z sekcji 3.3
    const auto candidates = chooseCandidates(u, g1, g2, gExtended, mappings.maps[copyIndex]);

    for (const auto& candidate : candidates) {
        const uint32_t v = candidate.v;
        const uint32_t deltaCost = candidate.deltaCost;

        // Sprawdzenie porzadku leksykograficznego (sekcja 3.4)
        if (copyIndex > 0 && prefixEqual) {
            const int prevMapping = mappings.maps[copyIndex - 1][u];
            // Jesli prefix jest rowny, obecny wierzcholek MUSI byc >= poprzedniego
            if (static_cast<int>(v) < prevMapping) {
                continue;
            }
            // Jesli to ostatni wierzcholek i wszystkie poprzednie byly rowne,
            // to ten MUSI byc > (zeby cale mapowanie bylo rozne)
            if (vertexIndex == g1.n - 1 && static_cast<int>(v) <= prevMapping) {
                continue;
            }
        }
        
        // POPRAWKA: Wczesniejsze sprawdzenie czy tworzymy duplikat obrazu
        // Budujemy tymczasowy obraz biezacego mapowania z nowym v
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
            
            // Sprawdz czy ten obraz juz istnieje w poprzednich kopiach
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
                continue; // Pomin ten kandydat - tworzy duplikat
            }
        }

        // Sprawdz, czy v nie jest juz uzyty w biezacej kopii
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

        // Przycinanie - mozemy przerwac bo kandydaci sa posortowani rosnaco wg kosztu
        if (newCost >= bestSolution.cost) {
            mappings.maps[copyIndex][u] = Mappings::NO_MAPPING;
            break;
        }

        // Zapisz stan grafu przed modyfikacja (do cofniecia)
        std::vector<std::pair<std::pair<int,int>, int>> edgeChanges;
        
        // Aktualizuj G'_2 o brakujace krawedzie
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
        
        // Dodaj obsluge petli (self-loop) dla wierzcholka u
        const int reqSelfLoop = g1.matrix[u][u];
        int& currSelfLoop = gExtended.matrix[v][v];
        if (currSelfLoop < reqSelfLoop) {
            edgeChanges.push_back({{v, v}, currSelfLoop});
            currSelfLoop = reqSelfLoop;
        }

        // Sprawdz czy prefix jest rowny
        const bool newPrefixEqual = copyIndex > 0 && prefixEqual && 
                                   (static_cast<int>(v) == mappings.maps[copyIndex - 1][u]);

        // Wywolanie rekurencyjne
        recursiveBranching(copyIndex, vertexIndex + 1, order, g1, g2, gExtended,
                         mappings, newCost, newPrefixEqual, bestSolution, k, oneBranch);

        if (oneBranch && bestSolution.found)
            return;

        // Cofnij zmiany w G'_2
        for (const auto& change : edgeChanges) {
            gExtended.matrix[change.first.first][change.first.second] = change.second;
        }

        // Cofnij mapowanie
        mappings.maps[copyIndex][u] = Mappings::NO_MAPPING;
    }
}

// Algorytm dokladny - glowna funkcja
// Zgodnie z sekcja 3.7 dokumentacji: AlgorytmDokladny
Solution exactAlgorithm(const Graph& g1, const Graph& g2, const int k, const bool oneBranch) {
    // Wyznacz porzadek wierzcholkow P
    const auto order = g1.verticesOrder();

    // Inicjalizacja
    Graph gExtended = g2;
    Mappings mappings(k, g1.n);
    Solution bestSolution;
    bestSolution.cost = UINT64_MAX;
    bestSolution.found = false;

    // Wywolaj rekurencje
    recursiveBranching(0, 0, order, g1, g2, gExtended, mappings, 
                      0, false, bestSolution, k, oneBranch);

    return bestSolution;
}

// Wczytywanie grafow z pliku z bulletproof walidacją
bool loadGraphsFromFile(const std::string& filename, Graph& g1, Graph& g2, int& k) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "ERROR: Cannot open file: " << filename << std::endl;
        return false;
    }

    // Wczytaj n1
    int n1;
    if (!(file >> n1)) {
        std::cerr << "ERROR: Cannot read n1 (number of vertices in G1)" << std::endl;
        return false;
    }
    if (n1 <= 0) {
        std::cerr << "ERROR: Invalid n1=" << n1 << " (must be positive)" << std::endl;
        return false;
    }

    g1 = Graph(n1);
    // Wczytaj macierz sasiedztwa G1
    for (int i = 0; i < n1; ++i) {
        for (int j = 0; j < n1; ++j) {
            if (!(file >> g1.matrix[i][j])) {
                std::cerr << "ERROR: Cannot read G1 adjacency matrix at position (" << i << "," << j << ")" << std::endl;
                return false;
            }
            if (g1.matrix[i][j] < 0) {
                std::cerr << "ERROR: Negative edge count in G1[" << i << "][" << j << "]=" << g1.matrix[i][j] << std::endl;
                return false;
            }
        }
    }

    // Wczytaj n2
    int n2;
    if (!(file >> n2)) {
        std::cerr << "ERROR: Cannot read n2 (number of vertices in G2)" << std::endl;
        return false;
    }
    if (n2 <= 0) {
        std::cerr << "ERROR: Invalid n2=" << n2 << " (must be positive)" << std::endl;
        return false;
    }
    if (n2 < n1) {
        std::cerr << "ERROR: n2=" << n2 << " < n1=" << n1 << " (G2 must have at least as many vertices as G1)" << std::endl;
        return false;
    }

    g2 = Graph(n2);
    // Wczytaj macierz sasiedztwa G2
    for (int i = 0; i < n2; ++i) {
        for (int j = 0; j < n2; ++j) {
            if (!(file >> g2.matrix[i][j])) {
                std::cerr << "ERROR: Cannot read G2 adjacency matrix at position (" << i << "," << j << ")" << std::endl;
                return false;
            }
            if (g2.matrix[i][j] < 0) {
                std::cerr << "ERROR: Negative edge count in G2[" << i << "][" << j << "]=" << g2.matrix[i][j] << std::endl;
                return false;
            }
        }
    }

    // Wczytaj k (opcjonalnie, domyslnie 1)
    k = 1;
    if (file >> k) {
        if (k <= 0) {
            std::cerr << "ERROR: Invalid k=" << k << " (must be positive)" << std::endl;
            return false;
        }
    }

    file.close();
    return true;
}

// Wypisz graf
void printGraph(ostream& o, const Graph& g, const std::string& name) {
    o << name << " (n=" << g.n << ", m=" << g.totalEdges() << "):" << std::endl;
    for (int i = 0; i < g.n; ++i) {
        for (int j = 0; j < g.n; ++j) {
            o << g.matrix[i][j];
            if (j < g.n - 1) o << " ";
        }
        o << std::endl;
    }
    o << std::endl;
}

// Wypisz tylko macierz (bez ozdobników)
void printMatrixOnly(ostream& o, const Graph& g) {
    for (int i = 0; i < g.n; ++i) {
        for (int j = 0; j < g.n; ++j) {
            o << g.matrix[i][j];
            if (j < g.n - 1) o << " ";
        }
        o << std::endl;
    }
}

// Wypisz rozwiazanie - verbose mode
void printSolutionVerbose(ostream& o, const Solution& sol, const Graph& g1, const Graph& g2, const std::string& algName, int n1, int n2, int k) {
    o << "=== Results from " << algName << " algorithm ===" << std::endl;
    if (!sol.found || sol.cost == UINT64_MAX) {
        std::cerr << "ERROR: Solution not found." << std::endl;
        const uint64_t maxMappings = binomialCoefficient(n2, n1);
        if (static_cast<uint64_t>(k) > maxMappings) {
            std::cerr << "REASON: k > C(n2,n1) - mathematically impossible." << std::endl;
            std::cerr << "  Requested k=" << k << " different " << n1 << "-element subsets" << std::endl;
            std::cerr << "  from " << n2 << "-element set, but C(" << n2 << "," << n1 << ")=" << maxMappings << std::endl;
        } else {
            std::cerr << "REASON: Graph structure does not allow k distinct isomorphic embeddings." << std::endl;
        }
        return;
    }

    o << "Extension cost: " << sol.cost << std::endl;

    o << "\nMappings:" << std::endl;
    for (int i = 0; i < sol.mappings.k; ++i) {
        o << "  Copy " << (i+1) << ": ";
        for (int j = 0; j < sol.mappings.n; ++j) {
            if (j > 0) o << ", ";
            o << j << "->" << sol.mappings.maps[i][j];
        }
        o << std::endl;
    }

    o << "\nExtended graph G'2:" << std::endl;
    printGraph(o, sol.extendedGraph, "G'2");
}

// Wypisz rozwiazanie - simple mode (tylko wynik)
void printSolutionSimple(ostream& o, const Solution& sol) {
    if (!sol.found || sol.cost == UINT64_MAX) {
        std::cerr << "ERROR: No solution found" << std::endl;
        return;
    }
    
    // Format: n, macierz, koszt
    o << sol.extendedGraph.n << std::endl;
    printMatrixOnly(o, sol.extendedGraph);
    o << sol.cost << std::endl;
}

void printUsage(const char* programName) {
    std::cout << "Usage: " << programName << " <input_file> [options]" << std::endl;
    std::cout << "\nOptions:" << std::endl;
    std::cout << "  -a, --approx     Use approximate algorithm (default: exact)" << std::endl;
    std::cout << "  -r, --raw    Show simple output without details" << std::endl;
    std::cout << "\nInput file format:" << std::endl;
    std::cout << "  n1" << std::endl;
    std::cout << "  adjacency_matrix_G1 (n1 x n1)" << std::endl;
    std::cout << "  n2" << std::endl;
    std::cout << "  adjacency_matrix_G2 (n2 x n2)" << std::endl;
    std::cout << "  k (optional, number of copies, default: 1)" << std::endl;
    std::cout << "\nOutput format (simple mode):" << std::endl;
    std::cout << "  n" << std::endl;
    std::cout << "  extended_adjacency_matrix (n x n)" << std::endl;
    std::cout << "  extension_cost" << std::endl;
    std::cout << "\nOutput file: out.txt (created next to executable)" << std::endl;
}

int main(int argc, char* argv[]) {
    std::string filename;
    bool useApprox = false;
    bool verbose = true;

    // Parsowanie argumentow
    if (argc < 2) {
        std::cerr << "ERROR: No input file specified" << std::endl;
        printUsage(argv[0]);
        return 1;
    }

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "-a" || arg == "--approx") {
            useApprox = true;
        } else if (arg == "-r" || arg == "--raw") {
            verbose = false;
        } else if (arg[0] == '-') {
            std::cerr << "ERROR: Unknown option: " << arg << std::endl;
            printUsage(argv[0]);
            return 1;
        } else if (filename.empty()) {
            filename = arg;
        } else {
            std::cerr << "ERROR: Multiple input files specified" << std::endl;
            return 1;
        }
    }

    if (filename.empty()) {
        std::cerr << "ERROR: No input file specified" << std::endl;
        printUsage(argv[0]);
        return 1;
    }

    Graph g1, g2;
    int k = 1;

    // Wczytaj dane
    if (!loadGraphsFromFile(filename, g1, g2, k)) {
        return 1;
    }

    // WALIDACJA WEJSCIA
    const uint64_t maxMappings = binomialCoefficient(g2.n, g1.n);
    if (static_cast<uint64_t>(k) > maxMappings) {
        std::cerr << "ERROR: Impossible to find " << k << " distinct embeddings." << std::endl;
        std::cerr << "REASON: k=" << k << " > C(n2,n1)=C(" << g2.n << "," << g1.n << ")=" << maxMappings << std::endl;
        std::cerr << "Need " << k << " different " << g1.n << "-vertex subgraphs from " << g2.n << " vertices." << std::endl;
        std::cerr << "The algorithm cannot add new vertices to G2." << std::endl;
        return 1;
    }

    // Wypisz dane wejsciowe (tylko w verbose mode)
    if (verbose) {
        std::cout << "\n=== Input ===" << std::endl;
        printGraph(std::cout, g1, "G1");
        printGraph(std::cout, g2, "G2");
        std::cout << "Number of copies k: " << k << std::endl;
        std::cout << "Max possible distinct embeddings: C(" << g2.n << "," << g1.n << ")=" << maxMappings << std::endl;
    }

    // Uruchom algorytm
    Solution solution;
    auto startTime = std::chrono::high_resolution_clock::now();
    
    std::string algName = useApprox ? "approximate" : "exact";
    if (verbose) {
        std::cout << "\nRunning " << algName << " algorithm...\n" << std::endl;
    }
    
    if (useApprox) {
        solution = approximateExpansion(g1, g2, k);
    } else {
        solution = exactAlgorithm(g1, g2, k, false);
    }
    
    auto endTime = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime);

    // Sprawdź czy znaleziono rozwiązanie
    if (!solution.found || solution.cost == UINT64_MAX) {
        std::cerr << "ERROR: No solution found" << std::endl;
        if (verbose) {
            std::cerr << "Graph structure does not allow " << k << " distinct isomorphic embeddings." << std::endl;
            std::cerr << "The algorithm cannot add new vertices to G2." << std::endl;
        }
        return 1;
    }

    // Wypisz wyniki
    if (verbose) {
        printSolutionVerbose(std::cout, solution, g1, g2, algName, g1.n, g2.n, k);
        std::cout << "Execution time: " << duration.count() << " ms" << std::endl;
    } else {
        printSolutionSimple(std::cout, solution);
    }

    // Zapisz wynik do pliku output (obok exe)
    std::ofstream outFile("out.txt");
    if (outFile.is_open()) {
        // Format: n, macierz, koszt
        if (verbose) {
            printSolutionVerbose(outFile, solution, g1, g2, algName, g1.n, g2.n, k);
            std::cout << "\nResult saved to out.txt" << std::endl;
        } else {
            printSolutionSimple(outFile, solution);
        }


    } else {
        if (verbose) {
            std::cerr << "Warning: Could not create out.txt" << std::endl;
        }
    }

    return 0;
}