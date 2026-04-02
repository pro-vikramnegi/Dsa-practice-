// LeetCode 83: Remove Duplicates from Sorted Linked List

/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 * };
 */

class Solution {
public:
    ListNode* deleteDuplicates(ListNode* head) {
        // Edge case: empty list
        if(head == NULL) return head;

        ListNode* curr = head;

        // Traverse till next exists
        while(curr != NULL && curr->next != NULL) {

            // If duplicate found
            if(curr->val == curr->next->val) {
                // Skip the duplicate node
                curr->next = curr->next->next;
            } 
            else {
                // Move forward
                curr = curr->next;
            }
        }

        return head;
    }
};
