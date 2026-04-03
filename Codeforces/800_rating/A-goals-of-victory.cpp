#include <bits/stdc++.h>
using namespace std;

/*
Problem: A. Goals of Victory (Codeforces)

Key Idea:
Total efficiency of all teams = 0
=> Missing team = -(sum of given efficiencies)
*/

int main() {
    int t;
    cin >> t; // number of test cases

    while(t--) {
        int n;
        cin >> n; // number of teams

        int sum = 0;

        // read n-1 efficiencies
        for(int i = 0; i < n - 1; i++){
            int x;
            cin >> x;
            sum += x; // accumulate sum
        }

        // missing efficiency = negative of sum
        cout << -sum << "\n";
    }

    return 0;
}
