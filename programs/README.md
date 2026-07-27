# Programs

Self-contained command-line programs, each one a build that clients request
over and over on freelance marketplaces. They are independent of the asset
library in this repo — nothing here reads or writes the asset folders — so each
can be lifted out, renamed and delivered on its own.

| # | Program | What it does | Dependencies |
|---|---|---|---|
| 1 | [`invoice-generator/`](invoice-generator/) | Invoices & quotes → printable HTML, payment ledger, receivables aging report | none (stdlib) |
| 2 | [`web-scraper-to-csv/`](web-scraper-to-csv/) | Config-driven, robots-respecting scraper → CSV/JSON/JSONL | none (stdlib) |
| 3 | [`bulk-image-processor/`](bulk-image-processor/) | Batch resize / convert / watermark / optimise with a CSV manifest | Pillow |

## Run everything

```bash
cd programs/invoice-generator     && python3 -m unittest discover -s tests   # 18 tests
cd ../web-scraper-to-csv          && python3 -m unittest discover -s tests   # 28 tests
cd ../bulk-image-processor        && pip install -r requirements.txt \
                                  && python3 -m unittest discover -s tests   # 29 tests
```

75 tests total. No network access required — the scraper suite serves its
fixtures from a throwaway localhost HTTP server.

## Shared conventions

Every program follows the same shape, so a change in one is a change you already
know how to make in the others:

- **Python 3.9+**, standard library first. A dependency has to earn its place;
  only the image processor has one (Pillow, for image decoding).
- **`python3 <program>.py --help`** is the real documentation for flags;
  each README covers the workflow and the decisions behind it.
- **Subcommand CLIs** built on `argparse`, returning an exit code from `main()`
  so they compose in shell scripts and cron.
- **Non-destructive by default.** Nothing overwrites its input. Every program
  has a `--dry-run` (or equivalent) that shows the plan and writes nothing.
- **Tests are `unittest`, no fixtures committed** — data is generated at run
  time into temp directories, so `python3 -m unittest discover -s tests` works
  from a clean checkout with nothing to set up.
- **CSV output is the deliverable**, because the client's next step is almost
  always a spreadsheet.

---

## For the next agent

Start with the target program's own README — each ends with a "For the next
agent" section covering its layout, the design decisions that should be
preserved, and a concrete list of good next features.

**If you are adding a fourth program**, mirror the existing structure:

```
programs/<name>/
  README.md          what it does, quick start, options, "For the next agent"
  <name>.py          single-module CLI with subcommands and a main() -> int
  requirements.txt   only if a dependency is genuinely required
  examples/          sample inputs the README commands actually run against
  tests/test_<name>.py
```

Then add a row to the table above and to the root `README.md`.

**Ideas that come up as often as these three, and aren't built yet:**
PDF toolkit (merge/split/watermark/form-fill), CSV & Excel data cleaner
(dedupe, normalise, validate), file organiser with duplicate detection, an
email/report scheduler, a booking-and-availability CLI, and a receipt/expense
extractor.

**Don't** wire these into the 3D asset pipeline unless asked — they are
standalone deliverables, and keeping them free of repo-specific assumptions is
what makes them reusable for the next client.
