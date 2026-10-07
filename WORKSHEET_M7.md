# Meeting 7 — Worksheet (isi Jawaban) & Laporan Output

|                       |                                                                  |
|-----------------------|------------------------------------------------------------------|
| **Course**            | Software Quality Assurance (SIB216101)                           |
| **Meeting**           | 7 — Implementing an Automatic Unit Testing Tool                  |
| **Case studies**      | CampusGo (main) and LibraryNow (challenge)                       |
| **Name / Student ID** | _(isi nama & NIM)_                                               |
| **Class / Group**     | _(isi kelas & kelompok)_                                         |

> Lingkungan yang dipakai: Python 3.14.3, pytest 9.1.1, pytest-cov 7.1.0.
> Semua perintah dijalankan dari root proyek (`python -m pytest ...`).

---

## Lab 1 — Your First Running Test (TC-CAL-005)

| **Question**                              | **Answer** |
|-------------------------------------------|------------|
| The test function name you used           | `test_ten_percent_discount_at_subtotal_50000` |
| Output when green (copy one line)         | `tests/test_orders.py::test_ten_percent_discount_at_subtotal_50000 PASSED` |
| Failure message after changing the number | `E assert 45000 == 45001` diikuti `tests\test_orders.py:23: AssertionError` |
| What does the red message tell you?       | Menampilkan baris assertion lengkap dengan nilai **aktual (45000)** vs **ekspektasi (45001)**, sehingga perbedaan langsung terlihat — diskon 10% memang menghasilkan 45000, bukan 45001. |

Potongan output merah yang direkam:

```text
>       assert total == 45001
E       assert 45000 == 45001
tests\test_orders.py:23: AssertionError
```

**Checkpoint Lab 1:** pesan merah yang baik menunjukkan nilai harapan dan nilai aktual — itulah
sebabnya assertion harus spesifik, bukan sekadar "sesuatu gagal".

---

## Lab 2 — Choosing the Right Assertion

| **Expected result**                        | **Assertion used**                                        |
|--------------------------------------------|-----------------------------------------------------------|
| The order total becomes Rp67,500           | `assert total == 67500`                                   |
| The error message contains the word “qty”  | `assert "qty" in str(err.value)`                          |
| The order produces no notifications at all | `assert len(order.tenant_notifications) == 0`             |
| The order status remains PROCESSING        | `assert order.status == "PROCESSING"`                     |
| A floating-point value is close to 0.3     | `assert value == pytest.approx(0.3)`                      |

Test yang ditulis untuk tiga baris pertama (semuanya hijau):

```python
def test_total_becomes_67500():
    assert order_total(25000, 3, True) == 67500

def test_error_message_contains_qty():
    with pytest.raises(ValueError) as err:
        order_total(25000, 0)
    assert "qty" in str(err.value)

def test_order_produces_no_notifications():
    order = Order(id="ORD-T002", owner="U-01", total=25000)
    assert len(order.tenant_notifications) == 0
```

**Mengapa `assert total` tanpa pembanding tidak baik:** assertion itu hanya mengecek *truthiness*;
nilai 1, 99, dan 45.000 semuanya lolos dan hanya 0 yang gagal. Ini padanan kode dari expected
result Chapter 4 yang berbunyi "the system works fine".
---

## Lab 3 — Testing the Negative Path

| **Question**                                    | **Answer** |
|-------------------------------------------------|------------|
| Does the test still pass without the last line? | Ya. Dengan hanya `pytest.raises(ValueError)`, tes tetap **PASSED** meskipun pesan error produksi diubah total menjadi `"something went wrong entirely"`. |
| Why is that dangerous?                          | Tanpa cek pesan, tes juga akan lolos jika program menaikkan `ValueError` untuk alasan yang sama sekali berbeda (contoh: typo variabel, gagal konversi). Bug sesungguhnya tidak terdeteksi. |
| The name of your second negative test           | `test_negative_qty_is_rejected` |
| Negative test passing vs positive test failing  | Negative test *passing* berarti sistem bertindak benar dengan menolak aksi tidak sah; positive test *failing* berarti sistem bertindak salah. Keduanya melibatkan penolakan tetapi maknanya berlawanan. |

Eksperimen yang benar-benar dijalankan: setelah baris `assert "qty" ...` dihapus dan pesan error
diubah, `test_zero_qty_is_rejected PASSED` sedangkan `test_negative_qty_is_rejected` (yang masih
mengecek pesan) gagal dengan:

```text
>       assert "qty" in str(err.value)
E       AssertionError: assert 'qty' in 'something went wrong entirely'
```

---

## Lab 4 — Fixtures as Preconditions (TC-ORD-003)

| **Part**                            | **Answer / code fragment** |
|-------------------------------------|----------------------------|
| Fixture body (before yield)         | `order = Order(id="ORD-T003", owner="U-01", total=25000)` lalu `order.status = "PROCESSING"` |
| Cleanup (after yield)               | `order.tenant_notifications.clear()` |
| Screen-layer assertion              | `assert result.rejected is True` |
| Data-layer assertion                | `assert order.status == "PROCESSING"` |
| Side-effect assertion               | `assert order.tenant_notifications == []` |
| Consequence of removing the cleanup | Sisa state dari satu tes bisa terbawa ke tes berikutnya → urutan eksekusi ikut menentukan hasil (flaky tests, seperti di Chapter 5). |

```python
@pytest.fixture
def processing_order():
    order = Order(id="ORD-T003", owner="U-01", total=25000)
    order.status = "PROCESSING"
    yield order
    order.tenant_notifications.clear()   # cleanup

def test_processing_order_cannot_be_cancelled(processing_order):
    result = processing_order.cancel(by="U-01")
    assert result.rejected is True                # screen
    assert processing_order.status == "PROCESSING"  # data
    assert processing_order.tenant_notifications == []  # side effects
```
---

## Lab 5 — Parameterisation from the Test Data Sheet

| **Price** | **Qty** | **Promo** | **Expected total** | **Why this data was chosen** |
|-----------|---------|-----------|--------------------|------------------------------|
| 25000     | 1       | True      | 25000 | Subtotal Rp25.000 — **di bawah** threshold, diskon tidak berlaku |
| 25000     | 2       | True      | 45000 | Subtotal Rp50.000 — **tepat di boundary**, diskon berlaku |
| 25000     | 3       | True      | 67500 | Subtotal Rp75.000 — **di atas** threshold, diskon berlaku |
| 25000     | 2       | False     | 50000 | Tanpa promo — membuktikan kondisi `has_promo` benar-benar dicek |

**Jumlah hasil yang dilaporkan runner: 4** — bukan 1. `pytest -v` memperluas satu test
berparameter menjadi satu hasil per baris data, jadi kegagalan satu baris tidak menyembunyikan
baris lainnya (keunggulan parameterisasi dibanding empat `assert` di dalam satu test).

Eksperimen baris sengaja dipecah (expected 67500 → 60000):

```text
test_orders.py::test_order_total_discount_boundaries[below-threshold] PASSED
test_orders.py::test_order_total_discount_boundaries[at-boundary] PASSED
test_orders.py::test_order_total_discount_boundaries[above-threshold] FAILED   <- hanya baris ini
test_orders.py::test_order_total_discount_boundaries[no-promo] PASSED
============================ 1 failed, 3 passed ============================
```

**Baris data yang tidak menambah nilai:** qty 4 atau 5 — perilakunya identik dengan qty 3
(jalur "di atas threshold" yang sudah terwakili), sehingga hanya duplikat tanpa informasi baru.

---

## Lab 6 — A Test Double for Payments

| **Question**                             | **Answer** |
|------------------------------------------|------------|
| What does assert_called_once_with check? | Memastikan `charge` dipanggil **tepat satu kali** dan dengan argumen **tepat 25000** — memverifikasi *bagaimana* komponen eksternal dipanggil, bukan hanya hasil akhirnya. |
| Why can a stub not do this?              | Stub hanya mengembalikan jawaban siap pakai dan tidak menyimpan catatan panggilan, sehingga tidak bisa memeriksa jumlah panggilan maupun nilai argumen. |
| The name of your second test             | `test_accepted_payment_deducts_balance_when_sufficient` |
| One risk of over-mocking                 | Test menjadi terikat pada struktur internal program; setiap refactor (walau perilaku sama) memecahkan banyak test, sehingga tim enggan memperbaiki kode. |

```python
def test_failed_payment_leaves_balance_unchanged():
    provider = Mock()
    provider.charge.return_value = {"status": "REJECTED"}
    wallet = Wallet(balance=24000, provider=provider)
    result = wallet.pay(25000)
    assert result.success is False
    assert wallet.balance == 24000
    provider.charge.assert_called_once_with(25000)
```

Test ketiga yang ditulis: `test_accepted_payment_rejected_when_balance_insufficient` — membuktikan
saldo hanya berkurang "if the balance is sufficient" (status ACCEPTED tetapi saldo 1000 < 25000 →
gagal, saldo tetap).
---

## Lab 7 — Coverage and What You Forgot

Perintah: `python -m pytest --cov=campusgo --cov-report=term-missing`

| **Observation**                        | **Result** |
|----------------------------------------|------------|
| Coverage before the extra test         | 92% (`campusgo/orders.py`, 36 stmts, 3 miss) |
| Missed line numbers                    | **34–36** — cabang `Order.cancel` untuk status selain PROCESSING tidak pernah dieksekusi |
| Coverage after the extra test          | **100%** — test baru `test_unpaid_order_cancel_succeeds_and_notifies_tenant` mengeksekusi baris 34–36 |
| Coverage after the assertion-free test | **100%** (tetap) — `test_calls_function_without_assertion` menjalankan `order_total(25000, 2, True)` tanpa satu `assert` pun |
| Two-sentence conclusion                | Coverage hanya mengukur baris yang *dieksekusi*, bukan perilaku yang *diverifikasi*: test tanpa assertion tetap hijau dan ikut menaikkan angka coverage tanpa menambah kualitas apa pun. Karena itu angka coverage saja tidak pernah bisa mengukur kualitas test — ia hanya alat untuk menemukan kode yang terlupa diuji. |

```text
Name                   Stmts   Miss  Cover   Missing
campusgo\orders.py        36      0   100%
TOTAL                     36      0   100%
```

---

## Lab 8 — The LibraryNow Challenge (assessed)

| **Part**                           | **Test function name** | **Notes / assertion fragment** |
|------------------------------------|------------------------|--------------------------------|
| Positive — reservation succeeds    | `test_reserves_available_book_with_zero_active_reservations` | `assert result.accepted is True` dan `assert result.reason == "reservation allowed"` |
| Negative — three-reservation limit | `test_refuses_at_three_reservation_limit` | `assert result.accepted is False` dan `assert "three active reservation limit" in result.reason` |
| Negative — book already borrowed   | `test_refuses_borrowed_book` | `assert result.accepted is False` dan `assert "borrowed" in result.reason` |
| Fixture for three reservations     | `student_with_three_active_reservations` (dipakai `test_fixture_student_cannot_reserve_more`) | membuat 3 reservasi aktif, `yield`, lalu cleanup `student.reservations.clear()` |
| Parameterised test 0/2/3/4         | `test_may_reserve_at_boundary_counts` | counts 0 & 2 → `accepted is True`; counts 3 & 4 → `accepted is False` (3 adalah boundary) |
| 24-hour expiry + weakness          | `test_reservation_older_than_24_hours_does_not_count` | `NOW - timedelta(hours=25)` tidak dihitung aktif → `active_count == 1`, `accepted is True`. **Weakness:** injeksi `now` hanya menguji perhitungan selisih waktu, bukan scheduler/job sungguhan yang mengekspirasi reservasi di produksi. |
| Final coverage                     | — | `python -m pytest tests/test_reservations.py --cov=librarynow --cov-report=term-missing` → **100%** (38 stmts, 0 missed) |

```text
Name                         Stmts   Miss  Cover   Missing
librarynow\reservations.py      38      0   100%
TOTAL                           38      0   100%
```

Bonus/boundary tambahan: `test_reservation_at_exactly_24_hours_is_expired` (tepat 24 jam ⇒ sudah
kadaluarsa) dan `test_collected_reservation_does_not_count_as_active`.

---

## Checklist Sebelum Submit

- [x] Setiap test di Lab 1–7 berjalan hijau di laptop (28 passed).
- [x] Setiap test punya minimal satu assertion yang spesifik.
- [x] Negative test memeriksa pesan error, bukan hanya jenis errornya.
- [x] Fixture Lab 4 punya cleanup setelah `yield`.
- [x] Test parameterisasi Lab 5 dilaporkan sebagai beberapa hasil terpisah (4 hasil).
- [x] Nama fungsi test menyatakan perilaku dan hasil yang diharapkan.
- [x] Tidak ada test yang menyentuh database asli atau jaringan.
- [x] Worksheet Lab 8 lengkap + hasil coverage terlampir (100%).

## Refleksi (tiga kalimat)

1. Salah satu test case Chapter 4 saya yang perlu diperbaiki saat otomatisasi adalah TC-ORD-003:
   expected result "cancel ditolak" harus dipecah menjadi tiga assertion eksplisit (screen, data,
   dan side effect) karena satu assertion longgar tidak akan menangkap regresi status.
2. Bagian tersulit lab ini adalah Lab 6 — memahami perbedaan stub vs mock dan mengapa
   `assert_called_once_with` (memeriksa *bagaimana* komponen dipanggil) tidak bisa digantikan stub.
3. Kebiasaan baru yang akan saya bawa ke mid-term Meeting 8: menjalankan `pytest -v` dan laporan
   coverage setiap selesai menulis/mengubah test, serta menamai test dengan "perilaku + hasil
   yang diharapkan" agar kegagalan langsung bisa dibaca.