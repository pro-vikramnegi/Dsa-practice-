#include <iostream>
#include <vector>
using namespace std;

/*
🧠 Approach (Brute Force)

1. Temp matrix bana lo
2. Original matrix traverse karo
3. Jaha 0 mile:
   → temp ki row & column 0 karo
4. End me temp copy back
*/

void setZeroes(vector<vector<int>>& matrix) {
    int n = matrix.size();
    int m = matrix[0].size();

    vector<vector<int>> temp = matrix;

    for(int i = 0; i < n; i++) {
        for(int j = 0; j < m; j++) {

            if(matrix[i][j] == 0) {

                // row zero
                for(int k = 0; k < m; k++) {
                    temp[i][k] = 0;
                }

                // column zero
                for(int k = 0; k < n; k++) {
                    temp[k][j] = 0;
                }
            }
        }
    }

    matrix = temp;
}

int main() {
    int n, m;
    cin >> n >> m;

    vector<vector<int>> matrix(n, vector<int>(m));

    // Input
    for(int i = 0; i < n; i++) {
        for(int j = 0; j < m; j++) {
            cin >> matrix[i][j];
        }
    }

    // Function call
    setZeroes(matrix);

    // Output
    for(int i = 0; i < n; i++) {
        for(int j = 0; j < m; j++) {
            cout << matrix[i][j] << " ";
        }
        cout << endl;
    }

    return 0;
}
