

\# GearShare Performance and Complexity Report



\## 1. Objective



The purpose of this benchmark is to evaluate the performance of GearShare operations and compare manual sorting algorithms with Python's built-in sorting function.



\## 2. Benchmark Methodology



\- Dataset sizes: 1,000, 5,000, 10,000 and 50,000 synthetic records.

\- Core operations: 5 runs per dataset size.

\- Sorting operations: 3 runs per dataset size.

\- Measurement tool: Python `time.perf\_counter()`.

\- Reported measurement: Median execution time.

\- Sorting output was suppressed during measurement to avoid including console printing time.

\- Synthetic records were added in memory. Original CSV files were not modified.



\## 3. Core Operations: Measured Results



| Operation | 1,000 records | 5,000 records | 10,000 records | 50,000 records |

|---|---:|---:|---:|---:|

| Catalogue listing | 0.00000670 | 0.00005420 | 0.00007600 | 0.00104650 |

| Linear search | 0.00008690 | 0.00047870 | 0.00078350 | 0.00380170 |

| Binary search | 0.00000530 | 0.00000540 | 0.00000570 | 0.00000810 |

| Rent item | 0.00020970 | 0.00086910 | 0.00148530 | 0.00845200 |

| Return item | 0.00003420 | 0.00010360 | 0.00022270 | 0.00114930 |

| Overdue report | 0.00004790 | 0.00020940 | 0.00036470 | 0.00171100 |



Times are in seconds.



\## 4. Predicted Time and Space Complexity



| Operation | Predicted Time Complexity | Auxiliary Space |

|---|---|---|

| Catalogue listing | O(n) | O(n) for returned list |

| Linear search | O(n) | O(1) |

| Binary search | O(log n) | O(1) |

| Rent item | O(n) | O(n) for temporary active-rental collections |

| Return item | O(n) | O(n) for temporary collections |

| Overdue report | O(n) | O(1) for generator, excluding consumed results |



\### Analysis



1\. Catalogue listing takes O(n) because it creates a list containing all catalogue items.

2\. Linear search checks items one by one. Its time increases as the dataset grows.

3\. Binary search repeatedly halves the search range. Its execution time remains very low even for 50,000 records.

4\. Rent and return operations involve scanning rental records to check active rentals, availability, fines or locate a rental.

5\. Overdue reporting checks each rental, resulting in O(n) time complexity.



\## 5. Sorting Algorithm Comparison



| Algorithm | 1,000 items | 5,000 items | 10,000 items | Predicted Time |

|---|---:|---:|---:|---|

| Bubble sort | 0.06604900 | 1.62127260 | 6.53906830 | O(n²) |

| Insertion sort | 0.04603510 | 1.09525120 | 4.46481060 | O(n²) |

| Selection sort | 0.04604570 | 1.12376510 | 4.39325830 | O(n²) |

| Python sorted() | 0.00006300 | 0.00042690 | 0.00092170 | O(n log n) |



Times are in seconds.



\### Sorting Analysis



\- Bubble sort repeatedly compares adjacent elements and swaps them when necessary.

\- Insertion sort builds a sorted portion by inserting each element into its correct position.

\- Selection sort repeatedly selects the smallest remaining element.

\- All three manual algorithms have O(n²) average and worst-case time complexity.

\- Python's built-in sorted() uses Timsort, which has O(n log n) worst-case time complexity.



Python's built-in sorting function performed significantly better than the manual algorithms, especially for larger datasets.



\## 6. Conclusion



The benchmark demonstrates why choosing the correct data structure and algorithm matters.



Binary search is significantly more efficient than linear search when the input is sorted. Manual quadratic sorting algorithms become expensive as input size increases, while Python's built-in sorting function handles larger datasets much more efficiently.



The results support the predicted complexity analysis and demonstrate the importance of algorithm selection in GearShare.



