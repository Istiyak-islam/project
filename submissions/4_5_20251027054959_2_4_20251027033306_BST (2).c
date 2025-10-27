#include <stdio.h>
#include <stdlib.h>

// BST Node structure
struct Node {
    int data;
    struct Node* left;
    struct Node* right;
};

// Function to print spaces for indentation
void printSpaces(int n) {
    for (int i = 0; i < n; ++i) {
        printf(" ");
    }
}

// Function to display a Binary Search Tree
void displayTree(struct Node* root, int level) {
    if (root == NULL) {
        return;
    }

    // Adjust the space for better visualization
    int spaces = 4;

    // Recursively display the right subtree
    displayTree(root->right, level + 1);

    // Print spaces for indentation based on the level
    printSpaces(level * spaces);

    // Print the value of the current node
    printf("%d\n", root->data);

    // Recursively display the left subtree
    displayTree(root->left, level + 1);
}

// Function to create a new BST node
struct Node* createNode(int data) {
    struct Node* newNode = (struct Node*)malloc(sizeof(struct Node));
    newNode->data = data;
    newNode->left = NULL;
    newNode->right = NULL;
    return newNode;
}

// Function to insert a node into the BST
struct Node* insert(struct Node* root, int data) {
    if (root == NULL) {
        return createNode(data);
    }

    if (data < root->data) {
        root->left = insert(root->left, data);
    } else if (data > root->data) {
        root->right = insert(root->right, data);
    }

    return root;
}

// Function to find the node with the minimum value in a tree
struct Node* minValueNode(struct Node* node) {
    struct Node* current = node;
    while (current->left != NULL) {
        current = current->left;
    }
    return current;
}

// Function to delete a node from the BST
struct Node* deleteNode(struct Node* root, int data) {
    if (root == NULL) {
        return root;
    }

    if (data < root->data) {
        root->left = deleteNode(root->left, data);
    } else if (data > root->data) {
        root->right = deleteNode(root->right, data);
    } else {
        // Node with only one child or no child
        if (root->left == NULL) {
            struct Node* temp = root->right;
            free(root);
            return temp;
        } else if (root->right == NULL) {
            struct Node* temp = root->left;
            free(root);
            return temp;
        }

        // Node with two children: Get the inorder successor (smallest in the right subtree)
        struct Node* temp = minValueNode(root->right);

        // Copy the inorder successor's data to this node
        root->data = temp->data;

        // Delete the inorder successor
        root->right = deleteNode(root->right, temp->data);
    }

    return root;
}

int main() {
    struct Node* root = NULL;

    // Insert nodes into the BST
    root = insert(root, 9);
    root = insert(root, 5);
    root = insert(root, 10);
    root = insert(root, 0);
    root = insert(root, 6);
    root = insert(root, 11);
    root = insert(root, -1);
    root = insert(root, 1);
    root = insert(root, 2);

    // Display the BST before deletion
    printf("BST Structure before Deletion:\n");
    displayTree(root, 0);
    printf("\n");

    // Delete nodes from the BST
    root = deleteNode(root, 10);
    root = deleteNode(root, 2);
    root = deleteNode(root, 5);

    // Display the BST after deletion
    printf("BST Structure after Deletion:\n");
    displayTree(root, 0);

    return 0;
}
