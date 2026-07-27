# Web Scraper → CSV

Describe a site in a small JSON file — what an "item" is, which fields to pull
out of it, how to page through results — and this crawls it politely and writes
CSV, JSON or JSONL.

"Scrape this site into a spreadsheet" is the single most common freelance data
job. This is the reusable version of it: nothing site-specific is hard-coded, so
a new client is a new config file, not a new script.

**Zero dependencies** — Python 3.9+ standard library only. `minidom.py` provides
the CSS selector engine so BeautifulSoup isn't needed.

---

## Quick start

```bash
cd programs/web-scraper-to-csv

# 1. find the selectors interactively
python3 scraper.py probe https://example.com/products "li.product h2 a" --attr href

# 2. write a config (or start from one of the examples)
python3 scraper.py init my-site.json

# 3. check the first page before committing to a full crawl
python3 scraper.py run my-site.json --dry-run

# 4. run it
python3 scraper.py run my-site.json --out products.csv
```

`probe` and `--dry-run` are the whole workflow — build the config against one
page, then let it loose.

## Config format

```json
{
  "start_urls": ["https://example.com/products?page=1"],
  "item_selector": "li.product",
  "fields": {
    "title": "h2.title::text",
    "url":   "h2.title a::attr(href)",
    "price": {"selector": ".price", "number": true},
    "stock": {"selector": ".stock", "regex": "(\\d+) left", "default": "0"},
    "tags":  {"selector": ".tag", "all": true, "separator": ", "}
  },
  "pagination": {"next_selector": "a.next", "max_pages": 10},
  "dedupe_on": ["url"],
  "request": {"delay": 1.0, "retries": 3, "obey_robots": true},
  "output": {"format": "csv", "path": "output.csv"}
}
```

**Field options** (a plain string is shorthand for `{"selector": "..."}`):

| Key | Effect |
|---|---|
| `selector` | CSS selector, relative to the item. Omit to use the item itself. |
| `attr` | Take an attribute instead of text. Shorthand: `a::attr(href)`. |
| `regex` | Keep the first capture group (or the whole match if there are no groups). |
| `replace` | `["old","new"]` or a list of such pairs. |
| `number` | Keep the first number found — turns `"$1,299.00"` into `1299.00`. |
| `all` | Join every match rather than taking the first, using `separator`. |
| `default` | Value used when nothing matched. |
| `absolute` | Force URL joining against the page URL (automatic for `href`/`src`). |

**Pagination** — either follow a link (`next_selector`) or generate URLs
(`url_template` with `start_page`/`end_page`/`step`). `max_pages` always caps the
crawl; `stop_when_empty` halts when a page yields no items.

**Output** — `csv` (BOM-prefixed so Excel opens UTF-8 correctly), `json`, or
`jsonl`. Columns follow the order in `fields`, plus `source_url`
(set `"include_source_url": false` to drop it).

## Selector support

`minidom.py` handles what scraping actually needs:

```
tag  #id  .class  *          [attr] [attr=v] [attr^=v] [attr$=v] [attr*=v] [attr~=v]
ancestor descendant          parent > child          a, b  (groups)
:first-child  :last-child  :nth-child(n)  :only-child  :not(simple)  :empty
```

Text is whitespace-collapsed and skips `<script>`/`<style>`. Malformed markup —
unclosed `<p>`, `<li>`, `<article>` — is recovered rather than dropped.

## Being a good citizen

The defaults are deliberately conservative, because getting a client's IP
blocked is how these jobs go wrong:

- `robots.txt` is fetched once per host and honoured, including `Crawl-delay`
  (the larger of the site's value and your configured `delay` wins).
- One request per host at a time, with `delay` + random `jitter` between them.
- Retries with exponential backoff on 429/5xx and network errors; `Retry-After`
  is respected. 403/404 fail fast — retrying them is pointless.
- `--cache DIR` stores fetched pages so building a config doesn't hammer the
  site. Delete the directory to refresh.

`--ignore-robots` exists for sites you own or have written permission to crawl.
It is not the default for a reason. Check the site's terms before running a job,
and don't collect personal data you don't have a lawful basis to hold.

## Tests

```bash
python3 -m unittest discover -s tests -v   # 28 tests, served from localhost
```

No internet needed — the suite spins up a throwaway HTTP server with fixture
pages covering pagination, robots.txt, caching, dedupe and malformed HTML.

---

## For the next agent

**Layout**
```
scraper.py    fetch policy, robots, cache, retries, field extraction, CLI
minidom.py    HTML tree + CSS selector engine (no third-party deps)
examples/     two ready configs against public scraping sandboxes
tests/        unittest suite, all against a local HTTP server
```

**Things to know before changing it**
- `Fetcher.get()` is the only place that touches the network. Rate limiting,
  robots and caching all live there — keep it that way.
- Extraction is pure: `extract_item(node, fields, base_url)` has no I/O, so new
  field options are cheap to test.
- `normalise_field()` converts shorthand (`"h3 a::attr(href)"`) into the dict
  form. Add new options to the dict form and, if useful, teach the shorthand.
- `minidom` is intentionally partial CSS. If a site needs something exotic,
  chain `select()` calls in a field's `selector` rather than growing the engine.
- The example configs point at `toscrape.com` sandboxes, which some networks
  block; the test suite is the ground truth for behaviour.

**Good next steps**
- Detail-page crawling: a `follow` block that visits each item's `url` and
  merges extra fields into the row.
- Incremental runs: hash rows into a small state file and emit only new/changed
  items, so a scheduled job produces a diff.
- Concurrency with a per-host token bucket (keep the one-at-a-time-per-host rule).
- JSON-LD extraction (`script[type="application/ld+json"]`) — many e-commerce
  sites hand you clean structured data for free.
- Session support (cookies via `http.cookiejar`) for sites behind a login the
  client has authorised you to use.
