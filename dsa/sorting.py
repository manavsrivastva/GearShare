
def bubble_sort(arr):
    """
    Sort elements in ascending order using Bubble Sort.

    Prints the list after every pass.

    Time Complexity:
        Best: O(n) with early stopping
        Average: O(n^2)
        Worst: O(n^2)

    Space Complexity: O(1)
    """

    arr = arr.copy()
    n = len(arr)

    for i in range(n - 1):

        swapped = False

        for j in range(n - i - 1):

            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True

        print(f"Pass {i + 1}: {arr}")

        if not swapped:
            break

    return arr


def insertion_sort(arr):
    """
    Sort elements using Insertion Sort.

    Time Complexity:
        Best: O(n)
        Average: O(n^2)
        Worst: O(n^2)

    Space Complexity: O(1)
    """

    arr = arr.copy()

    for i in range(1, len(arr)):

        key = arr[i]
        j = i - 1

        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = key

        print(f"Pass {i}: {arr}")

    return arr


def selection_sort(arr):
    """
    Sort elements using Selection Sort.

    Time Complexity:
        Best: O(n^2)
        Average: O(n^2)
        Worst: O(n^2)

    Space Complexity: O(1)
    """

    arr = arr.copy()
    n = len(arr)

    for i in range(n - 1):

        min_index = i

        for j in range(i + 1, n):

            if arr[j] < arr[min_index]:
                min_index = j

        arr[i], arr[min_index] = arr[min_index], arr[i]

        print(f"Pass {i + 1}: {arr}")

    return arr


def sort_catalogue(items):
    """
    Sort catalogue by:
    1. Top-level category ascending
    2. Weight descending
    3. Name ascending

    Python sorting is stable.
    """

    return sorted(
        items,
        key=lambda item: (
            item.parent_category or item.category,
            -item.weight_g,
            item.name.lower()
        )
    )
