// LeetCode Daily Question
// Date: 25-03-2026
// Problem: Can Partition Grid
// Approach:
// 1. Calculate total sum of grid
// 2. Store row-wise and column-wise sums
// 3. Check if we can split grid horizontally or vertically such that both parts have equal sum

class Solution {
public:
    bool canPartitionGrid(vector<vector<int>>& grid) {
        int n = grid.size();
        int m = grid[0].size();

        vector<long long> rowSum(n, 0);
        vector<long long> colSum(m, 0);

        long long totalSum = 0;

        // Calculate total sum, row sums and column sums
        for(int i = 0; i < n; i++){
            for(int j = 0; j < m; j++){
                totalSum += grid[i][j];
                rowSum[i] += grid[i][j];
                colSum[j] += grid[i][j];
            }  
        }

        // If total sum is odd, partition is not possible
        if(totalSum % 2 != 0){
            return false;
        }

        // Check horizontal partition
        long long upperSum = 0;
        for(int i = 0; i < n - 1; i++){
            upperSum += rowSum[i];
            if(upperSum == totalSum - upperSum){
                return true;
            }
        }

        // Check vertical partition
        long long leftSum = 0;
        for(int j = 0; j < m - 1; j++){
            leftSum += colSum[j];
            if(leftSum == totalSum - leftSum){
                return true;
            }
        }

        return false;
    }
};
