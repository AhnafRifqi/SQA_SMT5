"""CampusGo unit tests — Labs 1 to 5, and 7 (coverage).

Run from the project root with:
    python -m pytest -v
    python -m pytest --cov=campusgo --cov-report=term-missing
"""

import pytest

from campusgo.orders import Order, order_total


# ---------------------------------------------------------------------------
# Lab 1 — your first running test (TC-CAL-005, BR-07 discount @ Rp50,000)
# ---------------------------------------------------------------------------

def test_ten_percent_discount_at_subtotal_50000():
    # Arrange
    price, qty = 25000, 2
    # Act
    total = order_total(price, qty, has_promo=True)
    # Assert
    assert total == 45000


# ---------------------------------------------------------------------------
# Lab 2 — choosing the right assertion
# ---------------------------------------------------------------------------

def test_total_becomes_67500():
    # A value-based expected result maps to an equality assertion.
    assert order_total(25000, 3, True) == 67500


def test_error_message_contains_qty():
    # A message-based expected result maps to a substring check.
    with pytest.raises(ValueError) as err:
        order_total(25000, 0)
    assert "qty" in str(err.value)


def test_order_produces_no_notifications():
    # A "no side effect" expected result maps to an empty-collection check.
    order = Order(id="ORD-T002", owner="U-01", total=25000)
    assert len(order.tenant_notifications) == 0


def test_float_value_is_close_to_0_3():
    # Table 4, row 5: a floating-point result is compared with pytest.approx.
    value = 0.1 + 0.2
    assert value == pytest.approx(0.3)


# ---------------------------------------------------------------------------
# Lab 3 — testing the negative path
# ---------------------------------------------------------------------------

def test_zero_qty_is_rejected():
    with pytest.raises(ValueError) as err:
        order_total(25000, 0)
    assert "qty" in str(err.value)


def test_negative_qty_is_rejected():
    with pytest.raises(ValueError) as err:
        order_total(25000, -1)
    assert "qty" in str(err.value)


# ---------------------------------------------------------------------------
# Lab 4 — fixtures as preconditions (TC-ORD-003)
# ---------------------------------------------------------------------------

@pytest.fixture
def processing_order():
    """Precondition for TC-ORD-003: ORD-T003, owner U-01, PROCESSING status."""
    order = Order(id="ORD-T003", owner="U-01", total=25000)
    order.status = "PROCESSING"
    yield order
    # Cleanup: reset state so it cannot leak into the next test.
    order.tenant_notifications.clear()


def test_processing_order_cannot_be_cancelled(processing_order):
    # Screen layer: the refusal is shown to the caller.
    result = processing_order.cancel(by="U-01")
    assert result.rejected is True

    # Data layer: the status must remain PROCESSING.
    assert processing_order.status == "PROCESSING"

    # Side-effect layer: the tenant must receive no notification.
    assert processing_order.tenant_notifications == []


# ---------------------------------------------------------------------------
# Lab 5 — parameterisation from the test-data sheet
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("price", "qty", "promo", "expected"),
    [
        (25000, 1, True, 25000),   # below the threshold -> no discount
        (25000, 2, True, 45000),   # exactly at the boundary -> discount
        (25000, 3, True, 67500),   # above the threshold -> discount
        (25000, 2, False, 50000),  # no promo -> discount never applies
    ],
    ids=["below-threshold", "at-boundary", "above-threshold", "no-promo"],
)
def test_order_total_discount_boundaries(price, qty, promo, expected):
    assert order_total(price, qty, promo) == expected


# ---------------------------------------------------------------------------
# Lab 7 — coverage: tests that touch previously-missed lines
# ---------------------------------------------------------------------------

def test_unpaid_order_cancel_succeeds_and_notifies_tenant():
    """Extra Lab 7 test: covers the non-PROCESSING branch of Order.cancel."""
    order = Order(id="ORD-T004", owner="U-01", total=25000)
    result = order.cancel(by="U-01")
    assert result.rejected is False
    assert order.status == "CANCELLED"
    assert order.tenant_notifications == ["cancelled"]


def test_calls_function_without_assertion():
    """
    Lab 7 demonstration: executes a branch (raises coverage) but asserts
    nothing. Coverage rises, testing quality does not.
    """
    order_total(25000, 2, True)