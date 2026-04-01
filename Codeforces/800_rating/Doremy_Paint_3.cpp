#include <iostream>
#include <map>
#include <cmath>
using namespace std;

/*
🧠 Approach:
- Array "good" tab hoga jab adjacent sums equal ho
- Iska matlab:
    a1 = a3 = a5 ...
    a2 = a4 = a6 ...

👉 So only 2 distinct elements allowed

Cases:
1. 1 unique element → YES
2. 2 unique elements → freq difference ≤ 1 → YES
3. >2 elements → NO
*/

void solve() {
    int n;
    cin >> n;

    map<int, int> freq;

    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        freq[x]++;
    }

    // Case 1: All same
    if (freq.size() == 1) {
        cout << "YES\n";
    }
    // Case 2: Exactly 2 elements
    else if (freq.size() == 2) {
        auto it = freq.begin();
        int c1 = it->second;
        it++;
        int c2 = it->second;

        if (abs(c1 - c2) <= 1) {
            cout << "YES\n";
        } else {
            cout << "NO\n";
        }
    }
    // Case 3: More than 2 elements
    else {
        cout << "NO\n";
    }
}

int main() {
    int t;
    cin >> t;
    while (t--) {
        solve();
    }
    return 0;
}
