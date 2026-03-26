/*
Approach:
1. Traverse the list
2. If current == next → skip next
3. Else move forward

Time: O(n)
Space: O(1)
*/

class Solution {
public:
    ListNode* deleteDuplicates(ListNode* head) {
        ListNode* temp = head;

        while(temp && temp->next){
            if(temp->val == temp->next->val){
                temp->next = temp->next->next;
            } else {
                temp = temp->next;
            }
        }

        return head;
    }
};
