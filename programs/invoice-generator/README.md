# Invoice & Quote Generator

A CLI that turns a business profile, a client list and a line-items file into
numbered invoices (or quotes), printable HTML documents, a payment ledger and an
accounts-receivable aging report.

This is one of the most repeatedly requested freelance builds: small businesses
want their own invoicing instead of a per-seat SaaS subscription.

**Zero dependencies** — Python 3.9+ standard library only.

---

## Quick start

```bash
cd programs/invoice-generator

# one invoice per client, from a single CSV
python3 invoice_generator.py batch \
  --config examples/config.json \
  --clients examples/clients.json \
  --items examples/items.csv \
  --out invoices

# record a partial payment
python3 invoice_generator.py pay INV-2026-0002 --dir invoices --amount 2000

# who owes what, and how late
python3 invoice_generator.py report --dir invoices

# everything as one spreadsheet
python3 invoice_generator.py ledger --dir invoices --out ledger.csv
```

Open any `invoices/INV-*.html` in a browser and print to PDF — the stylesheet has
a `@media print` block, so the output is clean without a PDF library.

## Commands

| Command | What it does |
|---|---|
| `new` | One invoice for one client. `--quote` makes it a quote, `--po` adds a PO number. |
| `batch` | Groups an items file by `--client-column` and issues one invoice per client. |
| `render` | Re-renders an existing invoice JSON to HTML (use after editing JSON or the template). |
| `pay` | Records a payment. No `--amount` means paid in full. |
| `ledger` | Every invoice as one CSV — hand this to an accountant. |
| `report` | Receivables summary with 1–30 / 31–60 / 61+ day aging buckets and an overdue list. |

## Input files

**`config.json`** — your business, currency, default tax rate, payment terms,
invoice number format (`INV-{year}-{seq:04d}`), bank details, footer notes.

**`clients.json`** — a list of clients with `id`, `name`, `address`, `email`. A
client may carry its own `tax_rate` (e.g. `0` for an export-exempt client), which
overrides the config default.

**`items.csv`** (or `.json`) — one row per line item:

```csv
client_id,description,quantity,unit,unit_price,discount_pct,tax_rate
acme,Environment art pass,32,hrs,95.00,0,
acme,Asset optimisation,12,hrs,85.00,10,
acme,Project management,4,hrs,75.00,0,0
```

An empty `tax_rate` inherits the invoice rate; `0` is an explicit exemption.
Column aliases are accepted: `qty`/`quantity`, `rate`/`price`/`unit_price`,
`item`/`description`, `discount`/`discount_pct`.

## How the numbers work

- All money is `Decimal`, rounded half-up to 2dp at every step. No floats, so
  totals never drift by a cent.
- Per line: `gross = qty × unit_price`, `discount = gross × discount_pct`,
  `net = gross − discount`, `tax = net × (line rate or invoice rate)`.
- Invoice: `subtotal = Σ net`, `total = subtotal + Σ tax`,
  `balance_due = total − amount_paid`.
- Status is derived, never stored by hand: `unpaid` → `partial` → `paid`, plus
  `quote` for non-billable documents (excluded from the receivables report).

## Customising the document

`templates/invoice.html` is a plain HTML file with `{{placeholder}}` slots and one
`{{#items}}…{{/items}}` repeating block. Edit the CSS freely, or pass your own
file with `--template mine.html`. All interpolated values are HTML-escaped.

## Tests

```bash
python3 -m unittest discover -s tests -v   # 18 tests, no network, no deps
```

---

## For the next agent

**Layout**
```
invoice_generator.py   single-module CLI; data model + totals + render + commands
templates/invoice.html print-ready template ({{var}} and {{#items}} blocks)
examples/              config.json, clients.json, items.csv - used by the tests
tests/                 unittest suite covering money math, status, CLI
```

**Design decisions worth keeping**
- Decimal-only money via `money()` / `fmt_money()`. If you add a feature, do not
  introduce `float` anywhere in the totals path.
- Invoice status and totals are **computed properties**, not stored fields — the
  JSON `totals` block is a read-only snapshot for downstream tools.
- Invoice numbers come from `next_number()`, which persists a per-year counter in
  `<out-dir>/.sequence.json`. Numbers are never reused.
- Line `tax_rate` of `None` means "inherit"; `0` means "exempt". Preserve that
  distinction — it is how zero-rated/export clients are handled.

**Good next steps**
- `--pdf` flag shelling out to headless Chrome or `wkhtmltopdf` when present,
  falling back to HTML with a clear message.
- Recurring/retainer invoices: a `schedule.json` plus a `run-due` command.
- Emailing via `smtplib` with the HTML as the body and the ledger row updated.
- Multi-currency reporting (the report currently reports in the first invoice's
  currency; group by currency before summing).
- Credit notes / partial refunds as negative-quantity line items.
