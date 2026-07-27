#!/usr/bin/env python3
"""Invoice & quote generator.

Turns a business profile + client list + line items into numbered invoices,
printable HTML documents, a running ledger and an accounts-receivable aging
report. Money is handled with Decimal throughout, never float.

Standard library only. Run `python3 invoice_generator.py --help` for usage.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable

TWOPLACES = Decimal("0.01")
SEQUENCE_FILE = ".sequence.json"
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"

CURRENCY_SYMBOLS = {
    "USD": "$", "EUR": "€", "GBP": "£", "CAD": "CA$", "AUD": "A$",
    "JPY": "¥", "INR": "₹", "BRL": "R$", "MXN": "MX$", "ZAR": "R",
}


# --------------------------------------------------------------------------
# money helpers
# --------------------------------------------------------------------------

def money(value: Any) -> Decimal:
    """Coerce anything numeric-ish to a 2dp Decimal (half-up, like accounting)."""
    if isinstance(value, Decimal):
        d = value
    else:
        text = str(value).strip()
        if not text:
            return Decimal("0.00")
        # tolerate "$1,234.50" and "1 234,50" style inputs
        text = text.replace(",", "") if text.count(",") and "." in text else text
        text = re.sub(r"[^\d.\-]", "", text.replace(",", "."))
        d = Decimal(text or "0")
    return d.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def rate(value: Any) -> Decimal:
    """Percentage as Decimal, e.g. 8.25 -> Decimal('8.25')."""
    if value in (None, ""):
        return Decimal("0")
    return Decimal(str(value))


def fmt_money(amount: Decimal, currency: str) -> str:
    symbol = CURRENCY_SYMBOLS.get(currency.upper(), "")
    sign = "-" if amount < 0 else ""
    body = f"{abs(amount):,.2f}"
    return f"{sign}{symbol}{body}" if symbol else f"{sign}{body} {currency.upper()}"


# --------------------------------------------------------------------------
# data model
# --------------------------------------------------------------------------

@dataclass
class Party:
    """A business or a client - both sides of the invoice look the same."""

    name: str
    id: str = ""
    email: str = ""
    phone: str = ""
    address: list[str] = field(default_factory=list)
    tax_id: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Party":
        address = data.get("address") or []
        if isinstance(address, str):
            address = [line.strip() for line in address.splitlines() if line.strip()]
        return cls(
            name=data.get("name", ""),
            id=str(data.get("id", "")),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            address=list(address),
            tax_id=data.get("tax_id", ""),
        )


@dataclass
class LineItem:
    description: str
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal | None = None      # percent; None -> use invoice default
    discount_pct: Decimal = Decimal("0")  # percent off this line
    unit: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LineItem":
        qty_raw = data.get("quantity", data.get("qty", 1))
        tax_raw = data.get("tax_rate", data.get("tax", None))
        return cls(
            description=str(data.get("description", data.get("item", ""))).strip(),
            quantity=Decimal(str(qty_raw or 0)),
            unit_price=money(data.get("unit_price", data.get("rate", data.get("price", 0)))),
            tax_rate=None if tax_raw in (None, "") else rate(tax_raw),
            discount_pct=rate(data.get("discount_pct", data.get("discount", 0))),
            unit=str(data.get("unit", "") or ""),
        )

    @property
    def gross(self) -> Decimal:
        return money(self.quantity * self.unit_price)

    @property
    def discount_amount(self) -> Decimal:
        return money(self.gross * self.discount_pct / Decimal("100"))

    @property
    def net(self) -> Decimal:
        """Line total after its own discount, before tax."""
        return money(self.gross - self.discount_amount)

    def tax_amount(self, default_rate: Decimal) -> Decimal:
        applied = self.tax_rate if self.tax_rate is not None else default_rate
        return money(self.net * applied / Decimal("100"))


@dataclass
class Invoice:
    number: str
    issue_date: dt.date
    due_date: dt.date
    business: Party
    client: Party
    items: list[LineItem]
    currency: str = "USD"
    tax_rate: Decimal = Decimal("0")          # default rate for lines without one
    tax_label: str = "Tax"
    notes: str = ""
    payment_terms: str = ""
    payment_details: list[str] = field(default_factory=list)
    document_type: str = "Invoice"            # or "Quote"
    amount_paid: Decimal = Decimal("0.00")
    paid_date: str = ""
    payment_method: str = ""
    purchase_order: str = ""

    # ---- totals -----------------------------------------------------------
    @property
    def subtotal(self) -> Decimal:
        return money(sum((item.net for item in self.items), Decimal("0")))

    @property
    def discount_total(self) -> Decimal:
        return money(sum((item.discount_amount for item in self.items), Decimal("0")))

    @property
    def tax_total(self) -> Decimal:
        return money(sum((item.tax_amount(self.tax_rate) for item in self.items), Decimal("0")))

    @property
    def total(self) -> Decimal:
        return money(self.subtotal + self.tax_total)

    @property
    def balance_due(self) -> Decimal:
        return money(self.total - self.amount_paid)

    @property
    def status(self) -> str:
        if self.document_type.lower() == "quote":
            return "quote"
        if self.balance_due <= Decimal("0.00") and self.total > Decimal("0.00"):
            return "paid"
        if self.amount_paid > Decimal("0.00"):
            return "partial"
        return "unpaid"

    def is_overdue(self, as_of: dt.date) -> bool:
        return self.status in ("unpaid", "partial") and self.due_date < as_of

    def days_overdue(self, as_of: dt.date) -> int:
        return max(0, (as_of - self.due_date).days) if self.is_overdue(as_of) else 0

    # ---- (de)serialisation -------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return {
            "number": self.number,
            "document_type": self.document_type,
            "issue_date": self.issue_date.isoformat(),
            "due_date": self.due_date.isoformat(),
            "currency": self.currency,
            "tax_rate": str(self.tax_rate),
            "tax_label": self.tax_label,
            "purchase_order": self.purchase_order,
            "business": asdict(self.business),
            "client": asdict(self.client),
            "items": [
                {
                    "description": i.description,
                    "quantity": str(i.quantity),
                    "unit": i.unit,
                    "unit_price": str(i.unit_price),
                    "discount_pct": str(i.discount_pct),
                    "tax_rate": None if i.tax_rate is None else str(i.tax_rate),
                }
                for i in self.items
            ],
            "notes": self.notes,
            "payment_terms": self.payment_terms,
            "payment_details": self.payment_details,
            "amount_paid": str(self.amount_paid),
            "paid_date": self.paid_date,
            "payment_method": self.payment_method,
            "totals": {
                "subtotal": str(self.subtotal),
                "discount_total": str(self.discount_total),
                "tax_total": str(self.tax_total),
                "total": str(self.total),
                "balance_due": str(self.balance_due),
                "status": self.status,
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Invoice":
        return cls(
            number=data["number"],
            document_type=data.get("document_type", "Invoice"),
            issue_date=dt.date.fromisoformat(data["issue_date"]),
            due_date=dt.date.fromisoformat(data["due_date"]),
            business=Party.from_dict(data.get("business", {})),
            client=Party.from_dict(data.get("client", {})),
            items=[LineItem.from_dict(i) for i in data.get("items", [])],
            currency=data.get("currency", "USD"),
            tax_rate=rate(data.get("tax_rate", 0)),
            tax_label=data.get("tax_label", "Tax"),
            notes=data.get("notes", ""),
            payment_terms=data.get("payment_terms", ""),
            payment_details=list(data.get("payment_details", [])),
            amount_paid=money(data.get("amount_paid", 0)),
            paid_date=data.get("paid_date", ""),
            payment_method=data.get("payment_method", ""),
            purchase_order=data.get("purchase_order", ""),
        )


# --------------------------------------------------------------------------
# tiny template renderer:  {{key}} and {{#items}} ... {{/items}} blocks
# --------------------------------------------------------------------------

def render_template(template: str, context: dict[str, Any]) -> str:
    def render_block(match: re.Match[str]) -> str:
        name, body = match.group(1), match.group(2)
        rows = context.get(name) or []
        return "".join(render_template(body, {**context, **row}) for row in rows)

    out = re.sub(r"\{\{#(\w+)\}\}(.*?)\{\{/\1\}\}", render_block, template, flags=re.S)

    def render_var(match: re.Match[str]) -> str:
        value = context.get(match.group(1), "")
        return "" if value is None else str(value)

    return re.sub(r"\{\{(\w+)\}\}", render_var, out)


def escape(text: Any) -> str:
    return (
        str(text)
        .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def invoice_html(invoice: Invoice, template_path: Path | None = None) -> str:
    path = template_path or (TEMPLATE_DIR / "invoice.html")
    template = path.read_text(encoding="utf-8")
    cur = invoice.currency
    rows = []
    for item in invoice.items:
        qty = f"{item.quantity.normalize():f}"
        rows.append({
            "description": escape(item.description),
            "quantity": f"{qty} {escape(item.unit)}".strip(),
            "unit_price": fmt_money(item.unit_price, cur),
            "discount": f"{item.discount_pct.normalize():f}%" if item.discount_pct else "",
            "line_total": fmt_money(item.net, cur),
        })

    context: dict[str, Any] = {
        "document_type": escape(invoice.document_type.upper()),
        "number": escape(invoice.number),
        "issue_date": invoice.issue_date.isoformat(),
        "due_date": invoice.due_date.isoformat(),
        "purchase_order": escape(invoice.purchase_order),
        "po_row": (
            f"<div><span>PO number</span><strong>{escape(invoice.purchase_order)}</strong></div>"
            if invoice.purchase_order else ""
        ),
        "business_name": escape(invoice.business.name),
        "business_block": "<br>".join(
            escape(line) for line in [
                *invoice.business.address,
                invoice.business.email,
                invoice.business.phone,
                (f"Tax ID: {invoice.business.tax_id}" if invoice.business.tax_id else ""),
            ] if line
        ),
        "client_name": escape(invoice.client.name),
        "client_block": "<br>".join(
            escape(line) for line in [*invoice.client.address, invoice.client.email, invoice.client.phone] if line
        ),
        "items": rows,
        "subtotal": fmt_money(invoice.subtotal, cur),
        "discount_total": fmt_money(invoice.discount_total, cur),
        "discount_row": "" if not invoice.discount_total else (
            f"<tr><th>Discounts</th><td>-{fmt_money(invoice.discount_total, cur)}</td></tr>"
        ),
        "tax_label": escape(invoice.tax_label),
        "tax_total": fmt_money(invoice.tax_total, cur),
        "total": fmt_money(invoice.total, cur),
        "amount_paid": fmt_money(invoice.amount_paid, cur),
        "paid_row": "" if invoice.amount_paid == 0 else (
            f"<tr><th>Paid</th><td>-{fmt_money(invoice.amount_paid, cur)}</td></tr>"
        ),
        "balance_due": fmt_money(invoice.balance_due, cur),
        "status": escape(invoice.status.upper()),
        "notes": escape(invoice.notes).replace("\n", "<br>"),
        "notes_block": "" if not invoice.notes else (
            f"<section class='notes'><h3>Notes</h3><p>{escape(invoice.notes)}</p></section>"
        ),
        "payment_terms": escape(invoice.payment_terms),
        "payment_block": "<br>".join(escape(line) for line in invoice.payment_details),
    }
    return render_template(template, context)


# --------------------------------------------------------------------------
# loading input
# --------------------------------------------------------------------------

def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_items(path: Path) -> list[dict[str, Any]]:
    """Read line items from CSV or JSON. Both keep the same column names."""
    if path.suffix.lower() == ".json":
        data = load_json(path)
        return data["items"] if isinstance(data, dict) else list(data)
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def next_number(out_dir: Path, number_format: str, today: dt.date) -> str:
    """Allocate the next invoice number, persisting the counter in the out dir."""
    state_path = out_dir / SEQUENCE_FILE
    state = load_json(state_path) if state_path.exists() else {}
    key = str(today.year)
    seq = int(state.get(key, 0)) + 1
    state[key] = seq
    out_dir.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return number_format.format(year=today.year, month=f"{today.month:02d}", seq=seq)


def build_invoice(
    config: dict[str, Any],
    client: dict[str, Any],
    items: Iterable[dict[str, Any]],
    number: str,
    issue_date: dt.date,
    due_days: int | None = None,
    document_type: str = "Invoice",
    notes: str = "",
    purchase_order: str = "",
) -> Invoice:
    terms_days = due_days if due_days is not None else int(config.get("payment_terms_days", 14))
    return Invoice(
        number=number,
        document_type=document_type,
        issue_date=issue_date,
        due_date=issue_date + dt.timedelta(days=terms_days),
        business=Party.from_dict(config.get("business", {})),
        client=Party.from_dict(client),
        items=[LineItem.from_dict(i) for i in items],
        currency=config.get("currency", "USD"),
        tax_rate=rate(client.get("tax_rate", config.get("tax_rate", 0))),
        tax_label=config.get("tax_label", "Tax"),
        notes=notes or config.get("notes", ""),
        payment_terms=config.get("payment_terms", f"Net {terms_days}"),
        payment_details=list(config.get("payment_details", [])),
        purchase_order=purchase_order,
    )


def write_invoice(invoice: Invoice, out_dir: Path, template: Path | None = None) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{invoice.number}.json"
    html_path = out_dir / f"{invoice.number}.html"
    json_path.write_text(json.dumps(invoice.to_dict(), indent=2), encoding="utf-8")
    html_path.write_text(invoice_html(invoice, template), encoding="utf-8")
    return json_path, html_path


def load_invoices(out_dir: Path) -> list[Invoice]:
    invoices = []
    for path in sorted(out_dir.glob("*.json")):
        if path.name == SEQUENCE_FILE:
            continue
        try:
            invoices.append(Invoice.from_dict(load_json(path)))
        except (KeyError, ValueError) as exc:  # not one of ours - skip loudly
            print(f"skipping {path.name}: {exc}", file=sys.stderr)
    return invoices


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------

def find_client(clients: list[dict[str, Any]], key: str) -> dict[str, Any]:
    for client in clients:
        if key in (str(client.get("id", "")), client.get("name", "")):
            return client
    raise SystemExit(f"client not found: {key!r} (known: {[c.get('id') for c in clients]})")


def cmd_new(args: argparse.Namespace) -> int:
    config = load_json(Path(args.config))
    clients = load_json(Path(args.clients)) if args.clients else config.get("clients", [])
    client = find_client(clients, args.client)
    items = load_items(Path(args.items))
    if args.client_column:
        items = [i for i in items if str(i.get(args.client_column, "")) == args.client]

    out_dir = Path(args.out)
    issue = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    number = args.number or next_number(out_dir, config.get("number_format", "INV-{year}-{seq:04d}"), issue)
    invoice = build_invoice(
        config, client, items, number, issue,
        due_days=args.due_days, document_type="Quote" if args.quote else "Invoice",
        notes=args.notes or "", purchase_order=args.po or "",
    )
    json_path, html_path = write_invoice(invoice, out_dir, Path(args.template) if args.template else None)
    print(f"{invoice.number}  {invoice.client.name}  {fmt_money(invoice.total, invoice.currency)}")
    print(f"  {json_path}\n  {html_path}")
    return 0


def cmd_batch(args: argparse.Namespace) -> int:
    """One invoice per client, from a single items file with a client column."""
    config = load_json(Path(args.config))
    clients = load_json(Path(args.clients)) if args.clients else config.get("clients", [])
    rows = load_items(Path(args.items))
    out_dir = Path(args.out)
    issue = dt.date.fromisoformat(args.date) if args.date else dt.date.today()

    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        key = str(row.get(args.client_column, "")).strip()
        if not key:
            print(f"row without {args.client_column}: {row}", file=sys.stderr)
            continue
        grouped.setdefault(key, []).append(row)

    if not grouped:
        print("no rows to invoice", file=sys.stderr)
        return 1

    number_format = config.get("number_format", "INV-{year}-{seq:04d}")
    for key, items in grouped.items():
        client = find_client(clients, key)
        number = next_number(out_dir, number_format, issue)
        invoice = build_invoice(config, client, items, number, issue, due_days=args.due_days)
        write_invoice(invoice, out_dir, Path(args.template) if args.template else None)
        print(f"{invoice.number}  {invoice.client.name:<28} {fmt_money(invoice.total, invoice.currency):>12}")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    invoice = Invoice.from_dict(load_json(Path(args.invoice)))
    out = Path(args.out) if args.out else Path(args.invoice).with_suffix(".html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(invoice_html(invoice, Path(args.template) if args.template else None), encoding="utf-8")
    print(out)
    return 0


def cmd_pay(args: argparse.Namespace) -> int:
    path = Path(args.dir) / f"{args.number}.json"
    if not path.exists():
        raise SystemExit(f"no invoice {args.number} in {args.dir}")
    invoice = Invoice.from_dict(load_json(path))
    invoice.amount_paid = money(args.amount) if args.amount is not None else invoice.total
    invoice.paid_date = args.date or dt.date.today().isoformat()
    invoice.payment_method = args.method or ""
    write_invoice(invoice, Path(args.dir))
    print(f"{invoice.number}: {invoice.status}, balance {fmt_money(invoice.balance_due, invoice.currency)}")
    return 0


def cmd_ledger(args: argparse.Namespace) -> int:
    invoices = load_invoices(Path(args.dir))
    fields = [
        "number", "document_type", "issue_date", "due_date", "client", "currency",
        "subtotal", "tax", "total", "paid", "balance", "status",
    ]
    rows = [
        {
            "number": inv.number, "document_type": inv.document_type,
            "issue_date": inv.issue_date.isoformat(), "due_date": inv.due_date.isoformat(),
            "client": inv.client.name, "currency": inv.currency,
            "subtotal": f"{inv.subtotal:.2f}", "tax": f"{inv.tax_total:.2f}",
            "total": f"{inv.total:.2f}", "paid": f"{inv.amount_paid:.2f}",
            "balance": f"{inv.balance_due:.2f}", "status": inv.status,
        }
        for inv in invoices
    ]
    if args.out:
        with Path(args.out).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        print(f"{len(rows)} invoices -> {args.out}")
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    as_of = dt.date.fromisoformat(args.as_of) if args.as_of else dt.date.today()
    invoices = [i for i in load_invoices(Path(args.dir)) if i.document_type.lower() != "quote"]
    buckets = {"current": Decimal("0"), "1-30": Decimal("0"), "31-60": Decimal("0"), "61+": Decimal("0")}
    outstanding = [i for i in invoices if i.balance_due > 0]

    for inv in outstanding:
        days = inv.days_overdue(as_of)
        key = "current" if days == 0 else "1-30" if days <= 30 else "31-60" if days <= 60 else "61+"
        buckets[key] += inv.balance_due

    currency = invoices[0].currency if invoices else "USD"
    billed = money(sum((i.total for i in invoices), Decimal("0")))
    collected = money(sum((i.amount_paid for i in invoices), Decimal("0")))

    print(f"Accounts receivable as of {as_of.isoformat()}")
    print(f"  invoices          {len(invoices)}")
    print(f"  billed            {fmt_money(billed, currency)}")
    print(f"  collected         {fmt_money(collected, currency)}")
    print(f"  outstanding       {fmt_money(money(billed - collected), currency)}")
    print("\nAging")
    for label, amount in buckets.items():
        print(f"  {label:<10} {fmt_money(money(amount), currency):>14}")

    overdue = sorted((i for i in outstanding if i.is_overdue(as_of)), key=lambda i: i.due_date)
    if overdue:
        print("\nOverdue")
        for inv in overdue:
            print(
                f"  {inv.number:<16} {inv.client.name:<26} "
                f"{fmt_money(inv.balance_due, inv.currency):>12}  {inv.days_overdue(as_of)}d late"
            )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="invoice_generator.py",
        description="Generate invoices/quotes, track payments and report on receivables.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    new = sub.add_parser("new", help="create one invoice for one client")
    new.add_argument("--config", required=True, help="business profile JSON")
    new.add_argument("--clients", help="clients JSON (defaults to config.clients)")
    new.add_argument("--client", required=True, help="client id or name")
    new.add_argument("--items", required=True, help="line items CSV or JSON")
    new.add_argument("--client-column", help="filter items by this column matching --client")
    new.add_argument("--out", default="invoices", help="output directory")
    new.add_argument("--number", help="explicit invoice number (default: auto sequence)")
    new.add_argument("--date", help="issue date YYYY-MM-DD (default: today)")
    new.add_argument("--due-days", type=int, help="override payment terms in days")
    new.add_argument("--quote", action="store_true", help="produce a quote instead of an invoice")
    new.add_argument("--po", help="client purchase order number")
    new.add_argument("--notes", help="notes printed on the document")
    new.add_argument("--template", help="custom HTML template")
    new.set_defaults(func=cmd_new)

    batch = sub.add_parser("batch", help="one invoice per client from a single items file")
    batch.add_argument("--config", required=True)
    batch.add_argument("--clients")
    batch.add_argument("--items", required=True)
    batch.add_argument("--client-column", default="client_id")
    batch.add_argument("--out", default="invoices")
    batch.add_argument("--date")
    batch.add_argument("--due-days", type=int)
    batch.add_argument("--template")
    batch.set_defaults(func=cmd_batch)

    render = sub.add_parser("render", help="re-render an invoice JSON to HTML")
    render.add_argument("invoice")
    render.add_argument("--out")
    render.add_argument("--template")
    render.set_defaults(func=cmd_render)

    pay = sub.add_parser("pay", help="record a payment against an invoice")
    pay.add_argument("number")
    pay.add_argument("--dir", default="invoices")
    pay.add_argument("--amount", help="amount paid (default: pay in full)")
    pay.add_argument("--date", help="payment date YYYY-MM-DD")
    pay.add_argument("--method", help="e.g. bank transfer, stripe")
    pay.set_defaults(func=cmd_pay)

    ledger = sub.add_parser("ledger", help="export every invoice as one CSV")
    ledger.add_argument("--dir", default="invoices")
    ledger.add_argument("--out", help="CSV path (default: stdout)")
    ledger.set_defaults(func=cmd_ledger)

    report = sub.add_parser("report", help="accounts-receivable aging report")
    report.add_argument("--dir", default="invoices")
    report.add_argument("--as-of", help="date YYYY-MM-DD (default: today)")
    report.set_defaults(func=cmd_report)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
