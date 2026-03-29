// LeetCode 2839 - Check if Strings Can be Made Equal With Operations I
// Difficulty: Easy | Date: 29 Mar
// 
// KEY INSIGHT:
// You can swap s1[i] with s1[i+2] any number of times.
// This means even-indexed chars {s[0], s[2]} can freely rearrange among themselves.
// Same for odd-indexed chars {s[1], s[3]}.
// So just check: freq of even-pos chars same in s1 & s2?
//                freq of odd-pos chars same in s1 & s2?
//
// Time:  O(1) — string length is always 4
// Space: O(1) — fixed-size frequency array

class Solution {
public:
    bool checkStrings(string s1, string s2) {
        // freq[0] = even-index char frequencies
        // freq[1] = odd-index char frequencies
        int freq[2][26] = {};

        for (int i = 0; i < 4; i++) {
            freq[i % 2][s1[i] - 'a']++;  // count chars in s1
            freq[i % 2][s2[i] - 'a']--;  // cancel out with s2
        }

        // If all cancel to 0, both strings have same chars at even & odd positions
        for (int j = 0; j < 26; j++) {
            if (freq[0][j] != 0 || freq[1][j] != 0) return false;
        }

        return true;
    }
};
