# SQA Meeting 7 — Automatic Unit Testing with pytest

Praktikum *Software Quality Assurance (SIB216101)* — Meeting 7: implementing
automatic unit testing with **pytest** for two case studies.

## Project structure

| File / command                          | Purpose                                          |
|-----------------------------------------|--------------------------------------------------|
| `campusgo/orders.py`                    | Production code under test (BR-07, Order, Wallet)|
| `campusgo/__init__.py`                  | Marks the folder as a Python package             |
| `librarynow/reservations.py`            | LibraryNow reservation rules (Lab 8)             |
| `tests/test_orders.py`                  | Tests for Labs 1, 2, 3, 4, 5, 7                  |
| `tests/test_wallet.py`                  | Test double for payments (Lab 6)                 |
| `tests/test_reservations.py`            | LibraryNow challenge (Lab 8, assessed)           |
| `pyproject.toml`                        | pytest configuration (`pythonpath`, `testpaths`) |

## Basic commands

```powershell
pip install pytest pytest-cov        # install tooling (Python 3.11+)
python -m pytest -v                  # run every test with names
python -m pytest -k discount         # only tests whose name contains "discount"
python -m pytest --cov=campusgo --cov-report=term-missing        # CampusGo coverage
python -m pytest tests/test_reservations.py --cov=librarynow --cov-report=term-missing
```

## Labs covered

1. First running test (TC-CAL-005)
2. Choosing the right assertion
3. Testing the negative path
4. Fixtures as preconditions (TC-ORD-003)
5. Parameterisation from the test-data sheet
6. A test double (Mock) for payments
7. Coverage and what you forgot
8. LibraryNow challenge (assessed)