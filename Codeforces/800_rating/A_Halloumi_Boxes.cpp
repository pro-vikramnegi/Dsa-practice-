// Problem: <Add Problem Name>
// Platform: Codeforces
// Rating: 800

#include <iostream>
#include <vector>
using namespace std;

int main() {
    int t;
    cin >> t;

    while(t--) {
        int n, k;
        cin >> n >> k;

        vector<int> a(n);
        for(int i = 0; i < n; i++) cin >> a[i];

        if(k >= 2) {
            cout << "YES\n";
        } 
        else {
            for(int i = 1; i < n; i++) {
                if(a[i] < a[i-1]) {
                    cout << "NO\n";
                    return 0;
                }
            }
            cout << "YES\n";
        }
    }

    return 0;
}
