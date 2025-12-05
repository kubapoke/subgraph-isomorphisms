# Teoria algorytmów i obliczeń - implementacja algortymów

Projekt implementuje algorytmy (dokładny i aproksymacyjny) dla problemu znalezienia minimalnego rozszerzenia grafu G2, 
które zawiera k różnych kopii zadanego grafu G1.

## Założenia

Założenia działania programu pozostają zgodne z dokumentacją, w szczególności:
- Zakładamy, że |G1| <= |G2|.
- Nasze rozszerzenie dodaje do grafu G2 jedynie krawędzie.

## Kompilacja

Program został przygotowany w ramach pojedynczego pliku `.cpp`, wobec czego do jego kompilacji wystarczy wywołanie:

```bash
g++ ./main.cpp -o subgraph-isomorphism.exe
```

w folderze zawierającym plik `main.cpp`. Poprawność kompilacji była testowana na komputerach laboratoryjnych.
Wykorzystana wersja `g++` musi wspierać wersję języka `C++14`.

## Uruchamianie

```bash
./subgraph-isomorphism.exe [plik_z_danymi] [-a] [-r]
```

Po wywołaniu program domyślnie uruchamia algorytm dokładny.
Aby uruchomić algorytm aproksymacyjny, należy wywołać program z flagą `-a`.

Program akceptuje następujące flagi:
-   `-a, --approx`: algorytm aproksymacyjny
-   `-r, --raw`: surowe, niesformatowane wyjście do łatwego przetwarzania

## Format pliku wejściowego

Zadany plik wejściowy z instancją problemu powinien przyjmować następujący format:

```text
n1                  <-- Liczba wierzchołków G1
0 1 ...             <-- Macierz sąsiedztwa G1 (n1 x n1)
...
n2                  <-- Liczba wierzchołków G2
0 2 ...             <-- Macierz sąsiedztwa G2 (n2 x n2)
...
k                   <-- Liczba kopii do znalezienia
```

## Przykładowe wyjście

Program wypisuje wynik działania algorytmu na konsolę.
Przykładowe wyjście działania programu wygląda następująco:

```text
=== Input ===
G1 (n=3, m=6):
0 1 1
1 0 1
1 1 0

G2 (n=3, m=1):
0 1 0
0 0 0
0 0 0

Number of copies k: 1
Max possible distinct embeddings: C(3,3)=1

Running exact algorithm...

=== Results from exact algorithm ===
Extension cost: 5

Mappings:
  Copy 1: 0->0, 1->1, 2->2

Extended graph G'2:
G'2 (n=3, m=6):
0 1 1
1 0 1
1 1 0

Execution time: 1 ms
```

Program opisuje najpierw instancję wejściową, po czym wypisuje osiągnięte przez wybrany algorytm wyniki, gdzie:
- Extension cost -- koszt rozszerzenia zgodnie z definicją w dokumentacji.
- Mappings -- opisuje mapowania wierzchołków kolejnych kopii grafu G1 na wierzchołki grafu G2.
- Extended graph G'2 -- macierz sąsiedztwa rozszerzonego grafu G'2 zawierającego k kopii grafu G1.

Wyniki działania programu (część "Results") są zapisywane również do pliku `out.txt` w bieżącym katalogu.
