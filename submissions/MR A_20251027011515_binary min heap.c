#include <stdio.h>
#include <stdlib.h>

// Binary Min Heap structure
struct MinHeap {
    int* array;
    int capacity;
    int size;
};

// Function to create a new Min Heap
struct MinHeap* createMinHeap(int capacity) {
    struct MinHeap* minHeap = (struct MinHeap*)malloc(sizeof(struct MinHeap));
    minHeap->capacity = capacity;
    minHeap->size = 0;
    minHeap->array = (int*)malloc(capacity * sizeof(int));
    return minHeap;
}

// Function to swap two elements in the Min Heap
void swap(int* a, int* b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

// Function to maintain the Min Heap property after inserting an element
void heapifyUp(struct MinHeap* minHeap, int index) {
    int parent = (index - 1) / 2;

    while (index > 0 && minHeap->array[index] < minHeap->array[parent]) {
        swap(&minHeap->array[index], &minHeap->array[parent]);
        index = parent;
        parent = (index - 1) / 2;
    }
}

// Function to insert a new element into the Min Heap
void insert(struct MinHeap* minHeap, int value) {
    if (minHeap->size == minHeap->capacity) {
        printf("Heap is full. Cannot insert more elements.\n");
        return;
    }

    minHeap->array[minHeap->size] = value;
    heapifyUp(minHeap, minHeap->size);
    minHeap->size++;
}

// Function to maintain the Min Heap property after extracting the minimum element
void heapifyDown(struct MinHeap* minHeap, int index) {
    int leftChild = 2 * index + 1;
    int rightChild = 2 * index + 2;
    int smallest = index;

    if (leftChild < minHeap->size && minHeap->array[leftChild] < minHeap->array[smallest]) {
        smallest = leftChild;
    }

    if (rightChild < minHeap->size && minHeap->array[rightChild] < minHeap->array[smallest]) {
        smallest = rightChild;
    }

    if (smallest != index) {
        swap(&minHeap->array[index], &minHeap->array[smallest]);
        heapifyDown(minHeap, smallest);
    }
}

// Function to extract the minimum element from the Min Heap
int extractMin(struct MinHeap* minHeap) {
    if (minHeap->size <= 0) {
        printf("Heap is empty. Cannot extract minimum element.\n");
        return -1;
    }

    int minElement = minHeap->array[0];
    minHeap->array[0] = minHeap->array[minHeap->size - 1];
    minHeap->size--;

    heapifyDown(minHeap, 0);

    return minElement;
}

// Function to print the elements of the Min Heap
void printHeap(struct MinHeap* minHeap) {
    printf("Min Heap: ");
    for (int i = 0; i < minHeap->size; i++) {
        printf("%d ", minHeap->array[i]);
    }
    printf("\n");
}

int main() {
    struct MinHeap* minHeap = createMinHeap(10);

    insert(minHeap, 4);
    insert(minHeap, 2);
    insert(minHeap, 8);
    insert(minHeap, 1);
    insert(minHeap, 6);

    printHeap(minHeap);

    int minElement = extractMin(minHeap);
    if (minElement != -1) {
        printf("Minimum Element Extracted: %d\n", minElement);
        printHeap(minHeap);
    }

    return 0;
}
