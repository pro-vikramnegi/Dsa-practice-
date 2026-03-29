#include <bits/stdc++.h>
using namespace std;

/*
🧩 LeetCode 2839 - Check if Strings Can be Made Equal With Operations I

🧠 Approach (Direct Comparison):
- Hum sirf (i, i+2) indices swap kar sakte hain
- Iska matlab:
    Even indices (0,2) ek group
    Odd indices (1,3) ek group

👉 Har group me sirf 2 possibilities hoti hain:
    1. Same order
    2. Swapped order

⚙️ Steps:
1. Even indices (0,2) check karo:
   - ya to same match ho
   - ya swapped match ho

2. Odd indices (1,3) check karo:
   - ya to same match ho
   - ya swapped match ho

3. Agar dono groups match kare → return true

⏱️ Complexity:
- Time: O(1)
- Space: O(1)

🏷️ Tags:
- Strings
- Greedy
- Implementation
*/

class Solution {
public:
    bool canBeEqual(string s1, string s2) {

        // Check even indices (0,2)
        if(!((s1[0] == s2[0] && s1[2] == s2[2]) ||
             (s1[0] == s2[2] && s1[2] == s2[0]))) {
            return false;
        }

        // Check odd indices (1,3)
        if(!((s1[1] == s2[1] && s1[3] == s2[3]) ||
             (s1[1] == s2[3] && s1[3] == s2[1]))) {
            return false;
        }

        return true;
    }
};
