#include <bits/stdc++.h>
using namespace std;

/*
🧩 Codeforces A - Cover in Water

🧠 Approach:
- String ko traverse karte hain
- Check karte hain ki 3 continuous dots ("...") present hain ya nahi
- Agar mil gaye → answer = 2
- Agar nahi mile → total '.' count kar lete hain

⚙️ Steps:
1. Input lo (t test cases)
2. Har test case ke liye:
   - n aur string s lo
3. Loop chalao string par
4. Check karo:
   s[i] == '.' && s[i+1] == '.' && s[i+2] == '.'
5. Agar mil jaye:
   - print 2
   - break
6. Otherwise:
   - '.' count karo
7. End me:
   - agar "..." nahi mila → count print karo

⏱️ Complexity:
- Time: O(n)
- Space: O(1)

🏷️ Tags:
- Greedy
- Strings
- Implementation
*/

int main() {
    int t;
    cin >> t;

    while(t--) {
        int n;
        cin >> n;

        string s;
        cin >> s;

        int count = 0;
        bool found = false;

        for(int i = 0; i < n; i++) {

            // Check for "..."
            if(i + 2 < n && s[i] == '.' && s[i+1] == '.' && s[i+2] == '.') {
                cout << 2 << endl;
                found = true;
                break;
            }

            // Count dots
            if(s[i] == '.') {
                count++;
            }
        }

        // If no "..." found, print total dots
        if(!found) {
            cout << count << endl;
        }
    }

    return 0;
}
