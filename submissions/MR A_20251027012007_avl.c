#include <stdio.h>
#include <stdlib.h>

// AVL Node structure
struct Node {
    int data;
    struct Node* left;
    struct Node* right;
    int height;
};

// Function to print spaces for indentation
void printSpaces(int n) {
    for (int i = 0; i < n; ++i) {
        printf(" ");
    }
}

// Function to display an AVL tree with balance factors
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

    // Print the value and balance factor of the current node
    printf("%d", root->data);
    printf(" (%d)\n", balanceFactor(root));

    // Recursively display the left subtree
    displayTree(root->left, level + 1);
}

// Function to get the height of a node
int height(struct Node* node) {
    if (node == NULL) {
        return 0;
    }
    return node->height;
}

// Function to calculate the balance factor of a node
int balanceFactor(struct Node* node) {
    if (node == NULL) {
        return 0;
    }
    return height(node->left) - height(node->right);
}

// Function to rotate right at the given node (to fix imbalance)
struct Node* rightRotate(struct Node* y) {
    struct Node* x = y->left;
    struct Node* T2 = x->right;

    // Perform rotation
    x->right = y;
    y->left = T2;

    // Update heights
    y->height = 1 + (height(y->left) > height(y->right) ? height(y->left) : height(y->right));
    x->height = 1 + (height(x->left) > height(x->right) ? height(x->left) : height(x->right));

    return x;
}

// Function to rotate left at the given node (to fix imbalance)
struct Node* leftRotate(struct Node* x) {
    struct Node* y = x->right;
    struct Node* T2 = y->left;

    // Perform rotation
    y->left = x;
    x->right = T2;

    // Update heights
    x->height = 1 + (height(x->left) > height(x->right) ? height(x->left) : height(x->right));
    y->height = 1 + (height(y->left) > height(y->right) ? height(y->left) : height(y->right));

    return y;
}

// Function to create a new AVL node
struct Node* createNode(int data) {
    struct Node* newNode = (struct Node*)malloc(sizeof(struct Node));
    newNode->data = data;
    newNode->left = NULL;
    newNode->right = NULL;
    newNode->height = 1;
    return newNode;
}

// Function to insert a node into the AVL tree
struct Node* insert(struct Node* root, int data) {
    // Perform standard BST insertion
    if (root == NULL) {
        return createNode(data);
    }

    if (data < root->data) {
        root->left = insert(root->left, data);
    } else if (data > root->data) {
        root->right = insert(root->right, data);
    } else {
        // Duplicate data is not allowed in AVL tree
        return root;
    }

    // Update height of the current node
    root->height = 1 + (height(root->left) > height(root->right) ? height(root->left) : height(root->right));

    // Get the balance factor to check whether this node became unbalanced
    int balance = balanceFactor(root);

    // Perform rotations if needed to restore balance
    // Left Heavy (Left-Left case)
    if (balance > 1 && data < root->left->data) {
        return rightRotate(root);
    }
    // Right Heavy (Right-Right case)
    if (balance < -1 && data > root->right->data) {
        return leftRotate(root);
    }
    // Left Right Heavy (Left-Right case)
    if (balance > 1 && data > root->left->data) {
        root->left = leftRotate(root->left);
        return rightRotate(root);
    }
    // Right Left Heavy (Right-Left case)
    if (balance < -1 && data < root->right->data) {
        root->right = rightRotate(root->right);
        return leftRotate(root);
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

// Function to delete a node from the AVL tree
struct Node* deleteNode(struct Node* root, int data) {
    // Perform standard BST deletion
    if (root == NULL) {
        return root;
    }

    if (data < root->data) {
        root->left = deleteNode(root->left, data);
    } else if (data > root->data) {
        root->right = deleteNode(root->right, data);
    } else {
        // Node with only one child or no child
        if (root->left == NULL || root->right == NULL) {
            struct Node* temp = (root->left != NULL) ? root->left : root->right;

            // No child case
            if (temp == NULL) {
                temp = root;
                root = NULL;
            } else {
                // One child case
                *root = *temp; // Copy the contents of the non-empty child
            }

            free(temp);
        } else {
            // Node with two children: Get the inorder successor (smallest in the right subtree)
            struct Node* temp = minValueNode(root->right);

            // Copy the inorder successor's data to this node
            root->data = temp->data;

            // Delete the inorder successor
            root->right = deleteNode(root->right, temp->data);
        }
    }

    // If the tree had only one node then return
    if (root == NULL) {
        return root;
    }

    // Update height of the current node
    root->height = 1 + (height(root->left) > height(root->right) ? height(root->left) : height(root->right));

    // Get the balance factor to check whether this node became unbalanced
    int balance = balanceFactor(root);

    // Perform rotations if needed to restore balance
    // Left Heavy (Left-Left case)
    if (balance > 1 && balanceFactor(root->left) >= 0) {
        return rightRotate(root);
    }
    // Right Heavy (Right-Right case)
    if (balance < -1 && balanceFactor(root->right) <= 0) {
        return leftRotate(root);
    }
    // Left Right Heavy (Left-Right case)
    if (balance > 1 && balanceFactor(root->left) < 0) {
        root->left = leftRotate(root->left);
        return rightRotate(root);
    }
    // Right Left Heavy (Right-Left case)
    if (balance < -1 && balanceFactor(root->right) > 0) {
        root->right = rightRotate(root->right);
        return leftRotate(root);
    }

    return root;
}

// Function to perform in-order traversal
void inorderTraversal(struct Node* root) {
    if (root != NULL) {
        inorderTraversal(root->left);
        printf("%d ", root->data);
        inorderTraversal(root->right);
    }
}

// Function to free the memory allocated for the AVL tree nodes
void freeTree(struct Node* root) {
    if (root != NULL) {
        freeTree(root->left);
        freeTree(root->right);
        free(root);
    }
}

int main() {
    struct Node* root = NULL;
    int choice, value;

    do {
        printf("\nAVL Tree Menu:\n");
        printf("1. Insert\n");
        printf("2. Delete\n");
        printf("3. Display\n");
        printf("4. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);

        switch (choice) {
            case 1:
                printf("Enter the value to insert: ");
                scanf("%d", &value);
                root = insert(root, value);
                break;

            case 2:
                printf("Enter the value to delete: ");
                scanf("%d", &value);
                root = deleteNode(root, value);
                break;

            case 3:
                printf("AVL Tree Structure:\n");
                displayTree(root, 0);
                break;

            case 4:
                printf("Exiting the program.\n");
                break;

            default:
                printf("Invalid choice. Please enter a valid option.\n");
        }

    } while (choice != 4);

    // Free the allocated memory before exiting
    freeTree(root);

    return 0;
}

