/*
Approach:
1. Use two pointers (fast & slow)
2. Move fast n steps ahead
3. Move both until fast reaches end
4. Delete slow->next

Time: O(n)
Space: O(1)
*/

class Solution {
public:
    ListNode* removeNthFromEnd(ListNode* head, int n) {
        ListNode* dummy = new ListNode(0);
        dummy->next = head;

        ListNode* fast = dummy;
        ListNode* slow = dummy;

        for(int i = 0; i < n; i++){
            fast = fast->next;
        }

        while(fast->next){
            fast = fast->next;
            slow = slow->next;
        }

        slow->next = slow->next->next;

        return dummy->next;
    }
};
