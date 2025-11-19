#include <iostream>
#include <vector>
#include <algorithm>
#include <iomanip>

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
    long long cost;
    bool found;

    Solution() : cost(-1), found(false) {}
};

int main() {

}