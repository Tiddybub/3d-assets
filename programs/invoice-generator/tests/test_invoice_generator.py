"""Tests for the invoice generator. Run: python3 -m unittest discover -s tests"""

import datetime as dt
import json
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import invoice_generator as ig  # noqa: E402

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def sample_invoice(**overrides):
    config = json.loads((EXAMPLES / "config.json").read_text())
    clients = json.loads((EXAMPLES / "clients.json").read_text())
    items = ig.load_items(EXAMPLES / "items.csv")
    rows = [i for i in items if i["client_id"] == "acme"]
    invoice = ig.build_invoice(config, clients[0], rows, "INV-2026-0001", dt.date(2026, 1, 10))
    for key, value in overrides.items():
        setattr(invoice, key, value)
    return invoice


class MoneyTests(unittest.TestCase):
    def test_parses_messy_input(self):
        self.assertEqual(ig.money("$1,234.50"), Decimal("1234.50"))
        self.assertEqual(ig.money("95"), Decimal("95.00"))
        self.assertEqual(ig.money(""), Decimal("0.00"))

    def test_rounds_half_up_not_bankers(self):
        self.assertEqual(ig.money(Decimal("2.005")), Decimal("2.01"))
        self.assertEqual(ig.money(Decimal("2.015")), Decimal("2.02"))

    def test_formats_with_symbol_and_fallback(self):
        self.assertEqual(ig.fmt_money(Decimal("1234.5"), "USD"), "$1,234.50")
        self.assertEqual(ig.fmt_money(Decimal("-40"), "USD"), "-$40.00")
        self.assertEqual(ig.fmt_money(Decimal("10"), "SEK"), "10.00 SEK")


class LineItemTests(unittest.TestCase):
    def test_discount_and_tax_per_line(self):
        item = ig.LineItem.from_dict(
            {"description": "work", "quantity": 10, "unit_price": "100", "discount_pct": 10, "tax_rate": 20}
        )
        self.assertEqual(item.gross, Decimal("1000.00"))
        self.assertEqual(item.discount_amount, Decimal("100.00"))
        self.assertEqual(item.net, Decimal("900.00"))
        self.assertEqual(item.tax_amount(Decimal("0")), Decimal("180.00"))

    def test_line_tax_rate_overrides_invoice_default(self):
        taxed = ig.LineItem.from_dict({"description": "a", "quantity": 1, "unit_price": 100})
        exempt = ig.LineItem.from_dict({"description": "b", "quantity": 1, "unit_price": 100, "tax_rate": 0})
        self.assertEqual(taxed.tax_amount(Decimal("10")), Decimal("10.00"))
        self.assertEqual(exempt.tax_amount(Decimal("10")), Decimal("0.00"))


class TotalsTests(unittest.TestCase):
    def test_totals_add_up(self):
        invoice = sample_invoice()
        # 32*95 = 3040 ; 12*85 = 1020 less 10% = 918 ; 4*75 = 300 (tax exempt)
        self.assertEqual(invoice.subtotal, Decimal("4258.00"))
        self.assertEqual(invoice.discount_total, Decimal("102.00"))
        self.assertEqual(invoice.tax_total, Decimal("336.43"))  # 8.5% on 3958, not on the 300
        self.assertEqual(invoice.total, Decimal("4594.43"))
        self.assertEqual(invoice.balance_due, invoice.total)

    def test_due_date_follows_payment_terms(self):
        invoice = sample_invoice()
        self.assertEqual(invoice.due_date, dt.date(2026, 1, 24))

    def test_status_transitions(self):
        invoice = sample_invoice()
        self.assertEqual(invoice.status, "unpaid")
        invoice.amount_paid = Decimal("100.00")
        self.assertEqual(invoice.status, "partial")
        invoice.amount_paid = invoice.total
        self.assertEqual(invoice.status, "paid")
        self.assertEqual(invoice.balance_due, Decimal("0.00"))

    def test_overdue_only_when_unpaid(self):
        invoice = sample_invoice()
        as_of = dt.date(2026, 2, 10)
        self.assertTrue(invoice.is_overdue(as_of))
        self.assertEqual(invoice.days_overdue(as_of), 17)
        invoice.amount_paid = invoice.total
        self.assertFalse(invoice.is_overdue(as_of))


class SerialisationTests(unittest.TestCase):
    def test_round_trip_preserves_totals(self):
        original = sample_invoice()
        restored = ig.Invoice.from_dict(json.loads(json.dumps(original.to_dict())))
        self.assertEqual(restored.total, original.total)
        self.assertEqual(restored.number, original.number)
        self.assertEqual(len(restored.items), len(original.items))
        self.assertEqual(restored.client.name, "Acme Interactive")


class TemplateTests(unittest.TestCase):
    def test_repeating_block_and_escaping(self):
        out = ig.render_template("<p>{{title}}</p>{{#rows}}<li>{{name}}</li>{{/rows}}",
                                 {"title": "T", "rows": [{"name": "a"}, {"name": "b"}]})
        self.assertEqual(out, "<p>T</p><li>a</li><li>b</li>")

    def test_missing_keys_render_empty(self):
        self.assertEqual(ig.render_template("[{{nope}}]", {}), "[]")

    def test_html_contains_totals_and_escapes_client(self):
        invoice = sample_invoice()
        invoice.client.name = "A & B <Ltd>"
        html = ig.invoice_html(invoice)
        self.assertIn("$4,594.43", html)
        self.assertIn("A &amp; B &lt;Ltd&gt;", html)
        self.assertNotIn("<Ltd>", html)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name) / "invoices"

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args):
        return ig.main([str(a) for a in args])

    def test_batch_creates_one_invoice_per_client(self):
        code = self.run_cli(
            "batch", "--config", EXAMPLES / "config.json", "--clients", EXAMPLES / "clients.json",
            "--items", EXAMPLES / "items.csv", "--out", self.out, "--date", "2026-01-10",
        )
        self.assertEqual(code, 0)
        invoices = ig.load_invoices(self.out)
        self.assertEqual(len(invoices), 3)
        self.assertEqual({i.number for i in invoices},
                         {"INV-2026-0001", "INV-2026-0002", "INV-2026-0003"})
        for invoice in invoices:
            self.assertTrue((self.out / f"{invoice.number}.html").exists())

    def test_sequence_does_not_reuse_numbers(self):
        for _ in range(2):
            self.run_cli("new", "--config", EXAMPLES / "config.json", "--clients", EXAMPLES / "clients.json",
                         "--client", "acme", "--items", EXAMPLES / "items.csv",
                         "--client-column", "client_id", "--out", self.out, "--date", "2026-01-10")
        numbers = [i.number for i in ig.load_invoices(self.out)]
        self.assertEqual(sorted(numbers), ["INV-2026-0001", "INV-2026-0002"])

    def test_pay_marks_invoice_paid(self):
        self.run_cli("new", "--config", EXAMPLES / "config.json", "--clients", EXAMPLES / "clients.json",
                     "--client", "vireo", "--items", EXAMPLES / "items.csv",
                     "--client-column", "client_id", "--out", self.out, "--date", "2026-01-10")
        self.run_cli("pay", "INV-2026-0001", "--dir", self.out, "--date", "2026-01-20")
        invoice = ig.load_invoices(self.out)[0]
        self.assertEqual(invoice.status, "paid")
        self.assertEqual(invoice.paid_date, "2026-01-20")

    def test_ledger_csv_has_a_row_per_invoice(self):
        self.run_cli("batch", "--config", EXAMPLES / "config.json", "--clients", EXAMPLES / "clients.json",
                     "--items", EXAMPLES / "items.csv", "--out", self.out, "--date", "2026-01-10")
        ledger = Path(self.tmp.name) / "ledger.csv"
        self.run_cli("ledger", "--dir", self.out, "--out", ledger)
        lines = ledger.read_text().strip().splitlines()
        self.assertEqual(len(lines), 4)  # header + 3
        self.assertTrue(lines[0].startswith("number,document_type"))

    def test_quote_is_not_counted_as_receivable(self):
        self.run_cli("new", "--config", EXAMPLES / "config.json", "--clients", EXAMPLES / "clients.json",
                     "--client", "harbor", "--items", EXAMPLES / "items.csv",
                     "--client-column", "client_id", "--out", self.out, "--quote", "--date", "2026-01-10")
        invoice = ig.load_invoices(self.out)[0]
        self.assertEqual(invoice.document_type, "Quote")
        self.assertEqual(invoice.status, "quote")


if __name__ == "__main__":
    unittest.main()
