
import csv
import io
import random
import statistics
import time
from contextlib import redirect_stdout
from pathlib import Path

from gearshare import GearShare
from items import Equipment
from rentals import Rental

from dsa.search import (
    linear_search_by_name,
    binary_search_by_sku,
)

from dsa.sorting import (
    bubble_sort,
    insertion_sort,
    selection_sort,
)


OUTPUT_FOLDER = Path("docs")
OUTPUT_FOLDER.mkdir(exist_ok=True)

CORE_SIZES = [1000, 5000, 10000, 50000]
SORT_SIZES = [1000, 5000, 10000]

CORE_RUNS = 5
SORT_RUNS = 3


def build_benchmark_app(size):
    """
    Create a fresh GearShare application with synthetic data.

    The original CSV files are loaded normally.
    Synthetic items and historical rentals are added in memory.
    """

    app = GearShare()

    synthetic_items = []

    for i in range(size):
        sku = str(2000000000 + i)

        item = Equipment(
            sku,
            f"Benchmark Item {i:06d}",
            "benchmark",
            "Bench",
            "Bench",
            100 + (i % 500),
            1000,
            1,
        )

        app.items[sku] = item
        synthetic_items.append(item)

    # Add historical returned rentals.
    # These increase the size of the rental list without
    # creating active rentals that interfere with tests.

    for i in range(size):
        item = synthetic_items[i % size]

        rental = Rental(
            f"H{i:06d}",
            "C003",
            item.sku,
            "2026-10-10",
            "2026-10-13",
            "2026-10-13",
        )

        app.rentals.append(rental)

    return app, synthetic_items


def elapsed_time(function):
    """Measure one function execution."""

    start = time.perf_counter()
    function()
    return time.perf_counter() - start


def median_time(values):
    return statistics.median(values)


def benchmark_core_operations():
    """Benchmark GearShare and search operations."""

    results = []

    for size in CORE_SIZES:

        measurements = {
            "catalogue": [],
            "linear_search": [],
            "binary_search": [],
            "rent_item": [],
            "return_item": [],
            "overdue_report": [],
        }

        print(f"\nBenchmarking {size:,} synthetic records...")

        for run in range(CORE_RUNS):

            app, synthetic_items = build_benchmark_app(size)

            target_item = synthetic_items[-1]

            catalogue_items = app.catalogue()

            sorted_items = sorted(
                catalogue_items,
                key=lambda item: item.sku
            )

            # Catalogue listing
            measurements["catalogue"].append(
                elapsed_time(app.catalogue)
            )

            # Linear search: target is at the end
            measurements["linear_search"].append(
                elapsed_time(
                    lambda: linear_search_by_name(
                        catalogue_items,
                        target_item.name
                    )
                )
            )

            # Binary search: list is sorted by SKU
            measurements["binary_search"].append(
                elapsed_time(
                    lambda: binary_search_by_sku(
                        sorted_items,
                        target_item.sku
                    )
                )
            )

            # Overdue report: fully consume the generator
            measurements["overdue_report"].append(
                elapsed_time(
                    lambda: list(app.overdue_rentals())
                )
            )

            # Rent an item
            rental = None

            def rent_operation():
                nonlocal rental
                rental = app.rent_item("C003", target_item.sku)

            measurements["rent_item"].append(
                elapsed_time(rent_operation)
            )

            # Return the item just rented
            measurements["return_item"].append(
                elapsed_time(
                    lambda: app.return_item(rental.rental_id)
                )
            )

        for operation, times in measurements.items():

            median = median_time(times)

            results.append({
                "section": "Core operations",
                "size": size,
                "operation": operation,
                "median_seconds": median,
                "all_runs_seconds": ";".join(
                    f"{value:.8f}" for value in times
                ),
            })

            print(
                f"  {operation:20s}: "
                f"{median:.8f} seconds"
            )

    return results



def create_sorting_items(size):
    """Generate random integer weights for sorting benchmarks."""

    rng = random.Random(42)

    return [
        rng.randint(1, 100000)
        for _ in range(size)
    ]



def run_sort(function, items):
    """
    Run a sorting function while suppressing its pass-by-pass
    output, so benchmark timings are not affected by printing.
    """

    with redirect_stdout(io.StringIO()):
        function(items)



def benchmark_sorting():
    """Compare manual sorting algorithms with Python sorted()."""

    algorithms = {
        "bubble_sort": bubble_sort,
        "insertion_sort": insertion_sort,
        "selection_sort": selection_sort,
        "python_sorted": lambda items: sorted(items),
    }

    results = []

    for size in SORT_SIZES:

        print(f"\nSorting benchmark: {size:,} items")

        original_items = create_sorting_items(size)

        for name, function in algorithms.items():

            times = []

            for run in range(SORT_RUNS):

                items = list(original_items)

                if name == "python_sorted":
                    elapsed = elapsed_time(
                        lambda: function(items)
                    )
                else:
                    elapsed = elapsed_time(
                        lambda: run_sort(function, items)
                    )

                times.append(elapsed)

            median = median_time(times)

            results.append({
                "section": "Sorting comparison",
                "size": size,
                "operation": name,
                "median_seconds": median,
                "all_runs_seconds": ";".join(
                    f"{value:.8f}" for value in times
                ),
            })

            print(
                f"  {name:20s}: "
                f"{median:.8f} seconds"
            )

    return results



def save_results(results):
    """Save all measurements in a CSV file."""

    output_file = OUTPUT_FOLDER / "benchmark_results.csv"

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        fieldnames = [
            "section",
            "size",
            "operation",
            "median_seconds",
            "all_runs_seconds",
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to: {output_file}")


def main():

    print("=" * 55)
    print("GEARSHARE PERFORMANCE BENCHMARK")
    print("=" * 55)

    core_results = benchmark_core_operations()

    sorting_results = benchmark_sorting()

    all_results = core_results + sorting_results

    save_results(all_results)

    print("\nBenchmark completed successfully.")


if __name__ == "__main__":
    main()
