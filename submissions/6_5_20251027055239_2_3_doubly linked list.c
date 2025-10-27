#include <stdio.h>
#include <stdlib.h>

// Node structure
struct Node {
    int data;
    struct Node* prev;
    struct Node* next;
};

// Doubly linked list structure
struct DoublyLinkedList {
    struct Node* head;
};

// Function to create a new node
struct Node* createNode(int data) {
    struct Node* newNode = (struct Node*)malloc(sizeof(struct Node));
    newNode->data = data;
    newNode->prev = NULL;
    newNode->next = NULL;
    return newNode;
}

// Function to insert a node at the beginning of the list
void insertAtBeginning(struct DoublyLinkedList* list, int data) {
    struct Node* newNode = createNode(data);

    if (list->head == NULL) {
        list->head = newNode;
    } else {
        newNode->next = list->head;
        list->head->prev = newNode;
        list->head = newNode;
    }

    printf("Node inserted at the beginning successfully.\n");
}

// Function to insert a node at the end of the list
void insertAtEnd(struct DoublyLinkedList* list, int data) {
    struct Node* newNode = createNode(data);

    if (list->head == NULL) {
        list->head = newNode;
    } else {
        struct Node* temp = list->head;
        while (temp->next != NULL) {
            temp = temp->next;
        }

        temp->next = newNode;
        newNode->prev = temp;
    }

    printf("Node inserted at the end successfully.\n");
}

// Function to delete a node with a specific value
void deleteByValue(struct DoublyLinkedList* list, int value) {
    if (list->head == NULL) {
        printf("List is empty. Deletion failed.\n");
        return;
    }

    struct Node* temp = list->head;

    while (temp != NULL && temp->data != value) {
        temp = temp->next;
    }

    if (temp == NULL) {
        printf("Element with value %d not found. Deletion failed.\n", value);
        return;
    }

    if (temp->prev != NULL) {
        temp->prev->next = temp->next;
    } else {
        list->head = temp->next;
    }

    if (temp->next != NULL) {
        temp->next->prev = temp->prev;
    }

    free(temp);
    printf("Node with value %d deleted successfully.\n", value);
}

// Function to display the doubly linked list
void displayList(struct DoublyLinkedList* list) {
    if (list->head == NULL) {
        printf("List is empty.\n");
    } else {
        struct Node* temp = list->head;
        while (temp != NULL) {
            printf("%d ", temp->data);
            temp = temp->next;
        }
        printf("\n");
    }
}

int main() {
    struct DoublyLinkedList doublyLinkedList;
    doublyLinkedList.head = NULL;

    int choice, data;

    while (1) {
        printf("Menu:\n");
        printf("1. Insert at the beginning\n");
        printf("2. Insert at the end\n");
        printf("3. Delete by value\n");
        printf("4. Display the list\n");
        printf("5. Exit\n");
        printf("Enter your choice: ");

        scanf("%d", &choice);

        switch (choice) {
            case 1:
                printf("Enter data to insert at the beginning: ");
                scanf("%d", &data);
                insertAtBeginning(&doublyLinkedList, data);
                break;
            case 2:
                printf("Enter data to insert at the end: ");
                scanf("%d", &data);
                insertAtEnd(&doublyLinkedList, data);
                break;
            case 3:
                printf("Enter value to delete: ");
                scanf("%d", &data);
                deleteByValue(&doublyLinkedList, data);
                break;
            case 4:
                displayList(&doublyLinkedList);
                break;
            case 5:
                printf("Exiting program. Goodbye!\n");
                exit(0);
            default:
                printf("Invalid choice. Please enter a valid option.\n");
        }
    }

    return 0;
}

