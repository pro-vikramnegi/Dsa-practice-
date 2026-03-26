/*
Approach:
1. Find middle using slow & fast pointer
2. Reverse second half
3. Compare both halves
4. If same → palindrome

Time: O(n)
Space: O(1)
*/

class Solution {
public:
    ListNode* reverse(ListNode* head){
        ListNode* prev = NULL;
        while(head){
            ListNode* next = head->next;
            head->next = prev;
            prev = head;
            head = next;
        }
        return prev;
    }

    bool isPalindrome(ListNode* head) {
        if(!head || !head->next) return true;

        ListNode* slow = head;
        ListNode* fast = head;

        while(fast->next && fast->next->next){
            slow = slow->next;
            fast = fast->next->next;
        }

        ListNode* second = reverse(slow->next);
        ListNode* first = head;

        while(second){
            if(first->val != second->val) return false;
            first = first->next;
            second = second->next;
        }

        return true;
    }
};
