// LeetCode 206: Reverse Linked List

/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 * };
 */

class Solution {
public:
    ListNode* reverseList(ListNode* head) {

        ListNode* prev = NULL;
        ListNode* curr = head;

        while(curr != NULL) {
            // Store next node
            ListNode* next = curr->next;

            // Reverse link
            curr->next = prev;

            // Move pointers forward
            prev = curr;
            curr = next;
        }

        // New head
        return prev;
    }
};
