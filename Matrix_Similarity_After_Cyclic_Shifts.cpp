// Problem: Matrix Similarity After Cyclic Shifts
// Platform: LeetCode
// Approach:
// - Even rows → left rotate
// - Odd rows → right rotate
// - Compare with original matrix

class Solution {
public:
    bool areSimilar(vector<vector<int>>& mat, int k) {
        
        int r = mat.size();
        int c = mat[0].size();
        
        vector<vector<int>> original = mat;
        
        k = k % c;
        if(k == 0) return true;
        
        for(int i = 0; i < r; i++){
            if(i % 2 == 0){
                rotate(mat[i].begin(), mat[i].begin() + k, mat[i].end());
            }
            else{
                rotate(mat[i].begin(), mat[i].end() - k, mat[i].end());
            }
        }
        
        return mat == original;
    }
};
