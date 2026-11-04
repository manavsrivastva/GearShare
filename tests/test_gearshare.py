import pytest
from datetime import date

from gearshare import GearShare
from errors import (
    DisplayItemRentalError,
    InvalidSKUError,
    CustomerNotFoundError,
    UnpaidFineError,
)


@pytest.fixture
def app():
    return GearShare()


def test_catalogue_loads_seven_items(app):
    items = app.catalogue()
    assert len(items) == 7


def test_display_item_cannot_be_rented(app):
    with pytest.raises(DisplayItemRentalError):
        app.rent_item("C001", "1000000006")


def test_invalid_sku_is_rejected(app):
    with pytest.raises(InvalidSKUError):
        app.rent_item("C001", "9999999999")


def test_unknown_customer_is_rejected(app):
    with pytest.raises(CustomerNotFoundError):
        app.rent_item("C999", "1000000007")


def test_customer_with_unpaid_fines_over_500_is_blocked(app):
    with pytest.raises(UnpaidFineError):
        app.rent_item("C004", "1000000007")


def test_accessory_rental_is_two_days(app):
    rental = app.rent_item("C001", "1000000007")
    assert (rental.due_date - rental.issue_date).days == 2


def test_overdue_rentals_are_detected(app):
    overdue_ids = {r.rental_id for r in app.overdue_rentals()}
    assert "RN001" in overdue_ids
    assert "RN002" in overdue_ids


def test_due_date_itself_is_not_late():
    from rentals import Rental

    rental = Rental(
        "RNTEST", "C001", "1000000001",
        "2026-10-31", "2026-11-03"
    )
    assert rental.days_late(date(2026, 11, 3)) == 0

def test_equipment_can_be_extended_twice(app):
    first = app.extend_rental("RN003")
    second = app.extend_rental("RN003")

    assert first == date(2026, 11, 13)
    assert second == date(2026, 11, 20)


def test_equipment_cannot_be_extended_third_time(app):
    app.extend_rental("RN003")
    app.extend_rental("RN003")

    from errors import ExtensionNotAllowedError

    with pytest.raises(ExtensionNotAllowedError):
        app.extend_rental("RN003")


def test_accessory_cannot_be_extended(app):
    from errors import ExtensionNotAllowedError

    rental = app.rent_item("C001", "1000000007")

    with pytest.raises(ExtensionNotAllowedError):
        app.extend_rental(rental.rental_id)

def test_late_fee_is_calculated_correctly(app):
    result = app.return_item("RN002")

    # Basic customer: 3 late days × Rs.50
    assert result["late_fee"] == 150


def test_late_fee_is_capped_at_item_price(app):
    app.today = date(2030, 1, 1)

    result = app.return_item("RN001")

    # Fee cannot exceed the replacement price.
    assert result["late_fee"] == app.items["1000000003"].price


def test_customer_cannot_rent_same_item_twice(app):
    app.rent_item("C001", "1000000007")

    from errors import DuplicateRentalError

    with pytest.raises(DuplicateRentalError):
        app.rent_item("C001", "1000000007")


def test_waiting_list_uses_fifo_order(app):
    from errors import ItemUnavailableError

    # C001 takes the only available lens.
    rental = app.rent_item("C001", "1000000002")

    # C005 joins first.
    with pytest.raises(ItemUnavailableError):
        app.rent_item("C005", "1000000002")

    # C003 joins second.
    with pytest.raises(ItemUnavailableError):
        app.rent_item("C003", "1000000002")

    assert list(app.waiting_lists["1000000002"]) == ["C005", "C003"]

    # Return the lens.
    app.return_item(rental.rental_id)

    # C005 gets priority.
    app.rent_item("C005", "1000000002")

    assert list(app.waiting_lists["1000000002"]) == ["C003"]


def test_sku_must_contain_exactly_ten_digits(app):
    with pytest.raises(InvalidSKUError):
        app.rent_item("C001", "12345")

# --------------------------------------------------
# ADDITIONAL EDGE-CASE TESTS
# --------------------------------------------------

def test_customer_cannot_exceed_tier_item_limit(app):
    from errors import TierLimitError

    app.rent_item("C001", "1000000001")
    app.rent_item("C001", "1000000007")

    with pytest.raises(TierLimitError):
        app.rent_item("C001", "1000000004")


def test_customer_with_exactly_500_unpaid_fines_is_not_blocked(app):
    for fine in app.fines:
        fine["paid"] = True

    app.fines.append({
        "rental_id": "RN002",
        "amount": 500,
        "paid": False
    })

    rental = app.rent_item("C004", "1000000007")

    assert rental is not None


def test_returning_on_due_date_has_no_late_fee(app):
    app.today = date(2026, 10, 31)

    result = app.return_item("RN002")

    assert result["late_fee"] == 0


def test_extension_is_blocked_when_waiting_list_exists(app):
    from errors import ExtensionNotAllowedError

    app.waiting_lists["1000000004"].append("C005")

    with pytest.raises(ExtensionNotAllowedError):
        app.extend_rental("RN003")
