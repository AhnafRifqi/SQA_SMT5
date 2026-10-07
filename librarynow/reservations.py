# librarynow/reservations.py
"""LibraryNow reservation rules (Lab 8 challenge).

Rules:
- a student may reserve books;
- at most three active reservations per student;
- a reservation expires after 24 hours if not collected;
- a borrowed book cannot be reserved.
"""

from datetime import timedelta

MAX_ACTIVE_RESERVATIONS = 3
RESERVATION_TTL = timedelta(hours=24)


class Result:
    """Outcome of a may_reserve() check."""

    def __init__(self, accepted, reason):
        self.accepted = accepted
        self.reason = reason


class Reservation:
    """A single reservation placed on a book by a student."""

    def __init__(self, student, book, reserved_at):
        self.student = student
        self.book = book
        self.reserved_at = reserved_at
        self.collected = False


class Student:
    """A library student. Each student keeps their own list of reservations."""

    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name
        self.reservations = []


class Book:
    """A library book."""

    def __init__(self, book_id, title, borrowed=False):
        self.book_id = book_id
        self.title = title
        self.borrowed = borrowed


def active_count(student, now):
    """Number of reservations that are still active at `now`."""
    active = 0
    for reservation in student.reservations:
        if reservation.collected:
            continue
        if now - reservation.reserved_at >= RESERVATION_TTL:
            continue
        active += 1
    return active


def may_reserve(student, book, now):
    """Return a Result deciding whether `student` may reserve `book` now."""
    if book.borrowed:
        return Result(accepted=False, reason="book is already borrowed")
    if active_count(student, now) >= MAX_ACTIVE_RESERVATIONS:
        return Result(accepted=False, reason="three active reservation limit reached")
    return Result(accepted=True, reason="reservation allowed")