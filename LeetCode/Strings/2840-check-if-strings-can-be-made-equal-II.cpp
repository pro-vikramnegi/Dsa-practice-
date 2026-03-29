// LeetCode 2840 - Check if Strings Can be Made Equal With Operations II
// Difficulty: Medium | Date: 29 Mar
//
// KEY INSIGHT: (same as 2839, but now string length is variable)
// Swapping s[i] <-> s[i+2] means:
//   → All even-indexed chars form one "free pool" (can arrange in any order)
//   → All odd-indexed chars form another "free pool"
// So s1 can become s2 iff:
//   → multiset of even-pos chars is same in both strings
//   → multiset of odd-pos chars is same in both strings
//
// Time:  O(n) — single pass through both strings
// Space: O(1) — only 2 frequency arrays of size 26

class Solution {
public:
    bool checkStrings(string s1, string s2) {
        int n = s1.size();

        // freq[0] tracks even-position char balance (s1 vs s2)
        // freq[1] tracks odd-position char balance (s1 vs s2)
        int freq[2][26] = {};

        for (int i = 0; i < n; i++) {
            freq[i % 2][s1[i] - 'a']++;  // s1 char at position i
            freq[i % 2][s2[i] - 'a']--;  // cancel with s2 char
        }

        // All frequencies must cancel to 0
        // i.e., even-pos chars match AND odd-pos chars match
        for (int j = 0; j < 26; j++) {
            if (freq[0][j] != 0 || freq[1][j] != 0) return false;
        }

        return true;
    }
};
