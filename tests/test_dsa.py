
import pytest

from gearshare import GearShare
from dsa.search import linear_search_by_name, binary_search_by_sku


@pytest.fixture
def app():
    return GearShare()


def test_linear_search_finds_item(app):
    items = app.catalogue()

    result = linear_search_by_name(
        items,
        "Canon EOS 200D"
    )

    assert result is not None
    assert result.sku == "1000000001"


def test_linear_search_is_case_insensitive(app):
    result = linear_search_by_name(
        app.catalogue(),
        "canon eos 200d"
    )

    assert result is not None


def test_linear_search_returns_none_when_missing(app):
    result = linear_search_by_name(
        app.catalogue(),
        "Unknown Camera"
    )

    assert result is None


def test_binary_search_finds_first_item(app):
    items = sorted(app.catalogue(), key=lambda item: item.sku)

    result = binary_search_by_sku(items, "1000000001")

    assert result is not None
    assert result.name == "Canon EOS 200D"


def test_binary_search_finds_last_item(app):
    items = sorted(app.catalogue(), key=lambda item: item.sku)

    result = binary_search_by_sku(items, "1000000007")

    assert result is not None
    assert result.name == "SD Card 128GB"


def test_binary_search_returns_none_when_missing(app):
    items = sorted(app.catalogue(), key=lambda item: item.sku)

    result = binary_search_by_sku(items, "9999999999")

    assert result is None


def test_binary_search_handles_empty_list():
    assert binary_search_by_sku([], "1000000001") is None


from dsa.sorting import (
    bubble_sort,
    insertion_sort,
    selection_sort,
    sort_catalogue
)


def test_bubble_sort():
    assert bubble_sort([6, 3, 5, 2]) == [2, 3, 5, 6]


def test_insertion_sort():
    assert insertion_sort([6, 3, 5, 2]) == [2, 3, 5, 6]


def test_selection_sort():
    assert selection_sort([6, 3, 5, 2]) == [2, 3, 5, 6]


def test_sorting_empty_list():
    assert bubble_sort([]) == []
    assert insertion_sort([]) == []
    assert selection_sort([]) == []


def test_sorting_single_element():
    assert bubble_sort([10]) == [10]
    assert insertion_sort([10]) == [10]
    assert selection_sort([10]) == [10]


def test_sort_catalogue_returns_all_items(app):
    result = sort_catalogue(app.catalogue())

    assert len(result) == 7


def test_sorting_does_not_modify_original_list():
    original = [6, 3, 5, 2]
    bubble_sort(original)

    assert original == [6, 3, 5, 2]

from dsa.hashing import (
    find_duplicate_skus,
    group_by_tag,
    most_rented,
    packing_challenge
)


def test_group_by_tag():
    from gearshare import GearShare

    app = GearShare()
    grouped = group_by_tag(app.catalogue())

    assert "photo" in grouped
    assert "Canon EOS 200D" in grouped["photo"]
    assert "Sony 50mm Lens" in grouped["photo"]


def test_most_rented_items():
    from gearshare import GearShare

    app = GearShare()
    result = most_rented(app.rentals, app.catalogue(), 3)

    assert result == [
        ("Canon EOS 200D", 3),
        ("DJI Mini Drone", 2),
        ("Rode Wireless Mic", 2)
    ]


def test_packing_challenge_730():
    from gearshare import GearShare

    app = GearShare()
    result = packing_challenge(app.catalogue(), 730)

    assert result is not None
    assert result[0].weight_g + result[1].weight_g == 730


def test_packing_challenge_1320():
    from gearshare import GearShare

    app = GearShare()
    result = packing_challenge(app.catalogue(), 1320)

    assert result is not None
    assert result[0].weight_g + result[1].weight_g == 1320


def test_packing_challenge_no_pair():
    from gearshare import GearShare

    app = GearShare()
    assert packing_challenge(app.catalogue(), 1000) is None


def test_duplicate_sku_detection(tmp_path):
    csv_file = tmp_path / "gear_test.csv"

    csv_file.write_text(
        "sku,name\n"
        "1000000001,Camera\n"
        "1000000002,Lens\n"
        "1000000001,Duplicate Camera\n",
        encoding="utf-8"
    )

    result = find_duplicate_skus(csv_file)

    assert result == [("1000000001", 4)]


from dsa.history import (
    UndoManager,
    WaitingQueue,
    RentalHistory,
    benchmark_queues
)


def test_waiting_queue_fifo():
    queue = WaitingQueue()

    queue.add_customer("C001")
    queue.add_customer("C002")
    queue.add_customer("C003")

    assert queue.serve_next() == "C001"
    assert queue.serve_next() == "C002"
    assert queue.serve_next() == "C003"
    assert queue.serve_next() is None


def test_waiting_queue_does_not_add_duplicate():
    queue = WaitingQueue()

    queue.add_customer("C001")
    queue.add_customer("C001")

    assert queue.serve_next() == "C001"
    assert queue.is_empty()


def test_rental_history_newest_first():
    from rentals import Rental

    history = RentalHistory()

    rental1 = Rental("RN101", "C001", "1000000001",
                     "2026-10-28", "2026-10-31")
    rental2 = Rental("RN102", "C002", "1000000002",
                     "2026-10-29", "2026-11-01")

    history.add_rental(rental1)
    history.add_rental(rental2)

    result = history.get_history()

    assert result == [rental2, rental1]


def test_rental_history_empty():
    history = RentalHistory()

    assert history.is_empty()
    assert history.get_history() == []


def test_undo_rent():
    from gearshare import GearShare

    app = GearShare()
    rental = app.rent_item("C003", "1000000002")

    undo = UndoManager()
    undo.record_rent(rental)

    assert rental in app.rentals

    result = undo.undo(app)

    assert result == f"Undid rent: {rental.rental_id}"
    assert rental not in app.rentals


def test_undo_empty_stack():
    from gearshare import GearShare

    app = GearShare()
    undo = UndoManager()

    assert undo.undo(app) == "Nothing to undo."


def test_queue_benchmark_returns_results():
    result = benchmark_queues(1000)

    assert result["list_pop_0_seconds"] >= 0
    assert result["deque_popleft_seconds"] >= 0

from dsa.categories import (
    factorial,
    fibonacci,
    sum_of_digits,
    build_category_tree,
    print_category_tree,
    count_category_items,
    find_category_path,
    count_category_items_iterative
)


def test_factorial():
    assert factorial(6) == 720
    assert factorial(0) == 1


def test_factorial_negative():
    with pytest.raises(ValueError):
        factorial(-1)


def test_fibonacci():
    assert fibonacci(8) == 21
    assert fibonacci(0) == 0


def test_fibonacci_negative():
    with pytest.raises(ValueError):
        fibonacci(-1)


def test_sum_of_digits():
    assert sum_of_digits(5078) == 20
    assert sum_of_digits(0) == 0
    assert sum_of_digits(-123) == 6


def test_build_category_tree(app):
    tree = build_category_tree(app.catalogue())

    assert "Photography" in tree
    assert "Cameras" in tree["Photography"]
    assert "Canon EOS 200D" in tree["Photography"]["Cameras"]


def test_count_category_items(app):
    tree = build_category_tree(app.catalogue())

    assert count_category_items(tree) == 7


def test_iterative_and_recursive_count_match(app):
    tree = build_category_tree(app.catalogue())

    assert count_category_items(tree) == count_category_items_iterative(tree)


def test_find_category_path(app):
    tree = build_category_tree(app.catalogue())

    path = find_category_path(tree, "Canon EOS 200D")

    assert path == ["Photography", "Cameras", "Canon EOS 200D"]


def test_find_missing_category(app):
    tree = build_category_tree(app.catalogue())

    assert find_category_path(tree, "Nonexistent") is None

def test_actual_rent_can_be_undone(app):
    rental = app.rent_item("C003", "1000000002")

    result = app.undo_last_action()

    assert result == f"Undid rent: {rental.rental_id}"
    assert rental not in app.rentals


def test_actual_return_can_be_undone(app):
    rental = app.rent_item("C003", "1000000002")

    app.return_item(rental.rental_id)

    assert rental.return_date is not None

    result = app.undo_last_action()

    assert result == f"Undid return: {rental.rental_id}"
    assert rental.return_date is None
    assert rental in app.rentals