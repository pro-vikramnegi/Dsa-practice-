#include <bits/stdc++.h>
using namespace std;

int robotSim(vector<int>& commands, vector<vector<int>>& obstacles) {

    /*
    🧠 Approach:

    1. Robot initially (0,0) pe hai aur north direction me face kar raha hai.

    2. Directions ko manage karne ke liye:
       - North, East, South, West (0,1,2,3)
       - dx, dy arrays use karenge

    3. Obstacles ko fast check karne ke liye:
       → set / unordered_set me store karenge (x,y as string or pair)

    4. Har command ke liye:
       - -1 → right turn (dir++)
       - -2 → left turn (dir--)

       - Agar positive command hai (steps):
         → ek-ek step move karenge
         → har step pe check:
            - next cell obstacle hai kya?
            - agar hai → stop moving
            - warna move continue

    5. Har movement ke baad:
       → distance = x^2 + y^2
       → maximum distance track karo

    6. Final answer = maximum distance squared

    ⏱️ Time: O(N + M)
    */

    // directions: N, E, S, W
    vector<int> dx = {0, 1, 0, -1};
    vector<int> dy = {1, 0, -1, 0};

    int dir = 0; // north
    int x = 0, y = 0;
    int maxDist = 0;

    // store obstacles
    set<pair<int,int>> st;
    for(auto &o : obstacles) {
        st.insert({o[0], o[1]});
    }

    for(int cmd : commands) {
        if(cmd == -1) {
            dir = (dir + 1) % 4; // right turn
        }
        else if(cmd == -2) {
            dir = (dir + 3) % 4; // left turn
        }
        else {
            for(int i = 0; i < cmd; i++) {
                int nx = x + dx[dir];
                int ny = y + dy[dir];

                // check obstacle
                if(st.count({nx, ny})) break;

                x = nx;
                y = ny;

                maxDist = max(maxDist, x*x + y*y);
            }
        }
    }

    return maxDist;
}
