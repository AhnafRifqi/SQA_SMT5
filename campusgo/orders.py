# campusgo/orders.py
"""CampusGo order business rules used in Labs 1-7."""


def order_total(unit_price, qty, has_promo=False):
    """BR-07: apply a 10% discount once the subtotal reaches Rp50,000."""
    if qty <= 0:
        raise ValueError("qty must be greater than 0")
    subtotal = unit_price * qty
    if has_promo and subtotal >= 50000:
        return int(subtotal * 0.9)
    return subtotal


class Result:
    """Result of an order operation (rejected flag + human-readable message)."""

    def __init__(self, rejected, message):
        self.rejected = rejected
        self.message = message


class Order:
    """A CampusGo order (Lab 4: TC-ORD-003 cancellation rules)."""

    def __init__(self, id, owner, total):
        self.id, self.owner, self.total = id, owner, total
        self.status = "UNPAID"
        self.tenant_notifications = []

    def cancel(self, by):
        if self.status == "PROCESSING":
            return Result(rejected=True, message="Order is being processed")
        self.status = "CANCELLED"
        self.tenant_notifications.append("cancelled")
        return Result(rejected=False, message="Cancelled")


class PaymentResult:
    """Outcome of a Wallet.pay() call."""

    def __init__(self, success, message):
        self.success = success
        self.message = message


class Wallet:
    """A wallet whose payments go through an external provider (Lab 6)."""

    def __init__(self, balance, provider):
        self.balance = balance
        self.provider = provider

    def pay(self, amount):
        response = self.provider.charge(amount)
        if response["status"] == "ACCEPTED" and self.balance >= amount:
            self.balance -= amount
            return PaymentResult(success=True, message="Payment accepted")
        return PaymentResult(success=False, message="Payment rejected")