/*
    Problem: Add Two Numbers
    Platform: LeetCode
    Topic: Linked List

    Approach:
    - Traverse both linked lists
    - Add corresponding digits + carry
    - Create new node for each digit
*/

#include <bits/stdc++.h>
using namespace std;

/**
 * Definition for singly-linked list.
 */
struct ListNode {
    int val;
    ListNode *next;
    ListNode(int x) : val(x), next(NULL) {}
};

class Solution {
public:
    ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) {
        ListNode* dummy = new ListNode(0);
        ListNode* temp = dummy;

        int carry = 0;

        while(l1 != NULL || l2 != NULL || carry) {
            int sum = carry;

            if(l1 != NULL) {
                sum += l1->val;
                l1 = l1->next;
            }

            if(l2 != NULL) {
                sum += l2->val;
                l2 = l2->next;
            }

            carry = sum / 10;

            temp->next = new ListNode(sum % 10);
            temp = temp->next;
        }

        return dummy->next;
    }
};
