// Codeforces Problem (800 Rating)
// Idea: Check minimum operations to make string s a substring of x
// Operation: In one step, we can double the string x (x = x + x)

#include <iostream>
#include <string>

using namespace std;

int main() {
    // Fast I/O (important in Codeforces)
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int t;
    cin >> t;   // number of test cases

    while (t--) {
        int n, m;
        cin >> n >> m;   // lengths (given but not strictly needed)

        string x, s;
        cin >> x >> s;

        int operations = -1;  // default if not found

        // Since constraints small (n * m <= 25),
        // max ~6 doublings enough to cover all cases
        for (int i = 0; i <= 6; i++) {

            // Check if s is substring of x
            if (x.find(s) != string::npos) {
                operations = i;
                break;
            }

            // Double the string x
            x += x;
        }

        // Output minimum operations or -1
        cout << operations << endl;
    }

    return 0;
}
