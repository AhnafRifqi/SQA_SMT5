"""LibraryNow challenge tests — Lab 8 (assessed)."""

from datetime import datetime, timedelta

import pytest

from librarynow.reservations import (
    MAX_ACTIVE_RESERVATIONS,
    Book,
    Reservation,
    Student,
    active_count,
    may_reserve,
)

NOW = datetime(2026, 10, 7, 10, 0, 0)


def _student_with_reservations(count):
    """Helper: a student holding `count` active reservations made at NOW."""
    student = Student("S-01", "Student A")
    for index in range(count):
        book = Book(f"B-{index:02d}", f"Book {index + 1}")
        student.reservations.append(Reservation(student, book, NOW))
    return student


# --- Positive: a reservation succeeds -------------------------------------

def test_reserves_available_book_with_zero_active_reservations():
    student = Student("S-01", "Student A")
    book = Book("B-10", "Clean Architecture")

    result = may_reserve(student, book, NOW)

    assert result.accepted is True
    assert result.reason == "reservation allowed"


# --- Negative: three-reservation limit ------------------------------------

def test_refuses_at_three_reservation_limit():
    student = _student_with_reservations(MAX_ACTIVE_RESERVATIONS)

    result = may_reserve(student, Book("B-10", "Clean Architecture"), NOW)

    assert result.accepted is False
    assert "three active reservation limit" in result.reason


@pytest.fixture
def student_with_three_active_reservations():
    """Fixture: a student holding three active reservations (+ cleanup)."""
    student = Student("S-01", "Student A")
    for index in range(MAX_ACTIVE_RESERVATIONS):
        book = Book(f"B-{index:02d}", f"Book {index + 1}")
        student.reservations.append(Reservation(student, book, NOW))
    yield student
    # Cleanup: reset state so it cannot leak into the next test.
    student.reservations.clear()


def test_fixture_student_cannot_reserve_more(student_with_three_active_reservations):
    result = may_reserve(
        student_with_three_active_reservations, Book("B-99", "New Book"), NOW
    )
    assert result.accepted is False
    assert "three active reservation limit" in result.reason


# --- Negative: a borrowed book cannot be reserved --------------------------

def test_refuses_borrowed_book():
    student = Student("S-01", "Student A")
    borrowed = Book("B-10", "Clean Architecture", borrowed=True)

    result = may_reserve(student, borrowed, NOW)

    assert result.accepted is False
    assert "borrowed" in result.reason


# --- Parameterised: reservation counts 0 / 2 / 3 / 4 -----------------------

@pytest.mark.parametrize(
    ("active", "expected"),
    [
        (0, True),   # no reservations -> allowed
        (2, True),   # below the limit -> allowed
        (3, False),  # at the boundary -> refused
        (4, False),  # above the boundary -> refused
    ],
    ids=["count-0", "count-2", "count-3-at-limit", "count-4-over-limit"],
)
def test_may_reserve_at_boundary_counts(active, expected):
    result = may_reserve(_student_with_reservations(active), Book("B-99", "New Book"), NOW)
    assert result.accepted is expected


# --- 24-hour expiry, driven by an injected `now` ---------------------------

def test_reservation_older_than_24_hours_does_not_count():
    student = Student("S-01", "Student A")
    student.reservations.append(
        Reservation(student, Book("B-01", "Old Book"), NOW - timedelta(hours=25))
    )
    student.reservations.append(
        Reservation(student, Book("B-02", "Fresh Book"), NOW - timedelta(hours=5))
    )

    result = may_reserve(student, Book("B-99", "New Book"), NOW)

    assert active_count(student, NOW) == 1
    assert result.accepted is True


def test_reservation_at_exactly_24_hours_is_expired():
    student = Student("S-01", "Student A")
    student.reservations.append(
        Reservation(student, Book("B-01", "Old Book"), NOW - timedelta(hours=24))
    )

    result = may_reserve(student, Book("B-99", "New Book"), NOW)

    assert active_count(student, NOW) == 0
    assert result.accepted is True


def test_collected_reservation_does_not_count_as_active():
    student = Student("S-01", "Student A")
    collected = Reservation(student, Book("B-01", "Collected Book"), NOW)
    collected.collected = True
    student.reservations.append(collected)

    result = may_reserve(student, Book("B-99", "New Book"), NOW)

    assert result.accepted is True