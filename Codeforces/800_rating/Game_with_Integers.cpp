/*
    Problem: Game with Integers
    Platform: Codeforces

    Approach:
    - Agar n % 3 == 0 → First player lose (Second wins)
    - Otherwise → First player wins

    Logic:
    - Game pattern observe karne par pata chalta hai ki
      multiples of 3 losing positions hote hain.
*/

#include <iostream>
using namespace std;

int main() {
    int t;
    cin >> t;

    while (t--) {
        int n;
        cin >> n;

        if (n % 3 == 0) {
            cout << "Second" << endl;  // losing position
        } else {
            cout << "First" << endl;   // winning position
        }
    }

    return 0;
}
