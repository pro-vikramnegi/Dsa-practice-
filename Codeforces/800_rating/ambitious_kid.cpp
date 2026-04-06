#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;

    /*
    🧠 Approach:

    1. Hume product = 0 banana hai.
       → Product tabhi 0 hoga jab array me at least ek element 0 ho.

    2. Ek operation me kisi element ko +1 ya -1 kar sakte hain.

    3. To goal: kisi ek element ko 0 banana with minimum operations.

    4. Kisi bhi element Ai ko 0 banane ka cost = abs(Ai)
       - Ai > 0 → Ai baar decrease
       - Ai < 0 → |Ai| baar increase
       - Ai = 0 → 0 operations

    5. Final answer = minimum(abs(Ai)) over all elements.
    */

    int ans = INT_MAX;

    for (int i = 0; i < n; i++) {
        int x;
        cin >> x;
        ans = min(ans, abs(x)); // minimum cost to convert any element to 0
    }

    cout << ans << endl;

    return 0;
}
