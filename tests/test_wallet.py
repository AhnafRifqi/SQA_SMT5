"""Lab 6 — a test double (Mock) for the payment provider."""

from unittest.mock import Mock

from campusgo.orders import Wallet


def test_failed_payment_leaves_balance_unchanged():
    provider = Mock()
    provider.charge.return_value = {"status": "REJECTED"}
    wallet = Wallet(balance=24000, provider=provider)

    result = wallet.pay(25000)

    assert result.success is False
    assert wallet.balance == 24000
    provider.charge.assert_called_once_with(25000)


def test_accepted_payment_deducts_balance_when_sufficient():
    provider = Mock()
    provider.charge.return_value = {"status": "ACCEPTED"}
    wallet = Wallet(balance=25000, provider=provider)

    result = wallet.pay(25000)

    assert result.success is True
    assert wallet.balance == 0
    provider.charge.assert_called_once_with(25000)


def test_accepted_payment_rejected_when_balance_insufficient():
    provider = Mock()
    provider.charge.return_value = {"status": "ACCEPTED"}
    wallet = Wallet(balance=1000, provider=provider)

    result = wallet.pay(25000)

    assert result.success is False
    assert wallet.balance == 1000
    provider.charge.assert_called_once_with(25000)