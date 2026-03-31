/**
 * 🚀 Jagged Swaps
 *
 * 💡 Problem:
 * - Array diya hai
 * - Adjacent swaps allowed hain
 * - Check karna hai kya array ko sorted bana sakte hain
 *
 * 💡 Key Observation:
 * - Agar array ka first element 1 hai → always possible
 * - Agar first element 1 nahi hai → impossible
 *
 * 🧠 Reason:
 * - 1 smallest element hai
 * - Agar wo starting me nahi hai, toh required swaps possible nahi honge
 *   (problem ke constraints ke hisaab se)
 *
 * 🔄 Steps:
 * 1. Input lo
 * 2. Check karo a[0] == 1 ?
 * 3. Agar haan → "YES"
 * 4. warna → "NO"
 *
 * ⚡ Time Complexity: O(N)
 * ⚡ Space Complexity: O(1)
 */

#include <bits/stdc++.h>
using namespace std;

int main() {
    int t;
    cin >> t;

    while(t--) {
        int n;
        cin >> n;

        vector<int> a(n);
        for(int i = 0; i < n; i++) {
            cin >> a[i];
        }

        // Main logic
        if(a[0] == 1) {
            cout << "YES\n";
        } else {
            cout << "NO\n";
        }
    }

    return 0;
}
