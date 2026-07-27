#!/usr/bin/env python3
"""Config-driven web scraper that outputs CSV / JSON / JSONL.

You describe a site in a small JSON file - what an "item" looks like, which
fields to pull out of it, how to page through results - and this runs the crawl
politely: robots.txt is respected, requests are rate limited, failures are
retried with backoff, and pages can be cached so re-runs during development
don't re-hit the site.

Standard library only (uses the bundled minidom.py for CSS selectors).
Run `python3 scraper.py --help` for usage.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from minidom import Node, parse_html

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (compatible; scraper-to-csv/1.0; +https://example.com/bot)"
)
VERBOSITY = 1  # 0 quiet, 1 normal, 2 verbose


def log(message: str, level: int = 1) -> None:
    if VERBOSITY >= level:
        print(message, file=sys.stderr)


# --------------------------------------------------------------------------
# fetching
# --------------------------------------------------------------------------

@dataclass
class FetchPolicy:
    user_agent: str = DEFAULT_USER_AGENT
    delay: float = 1.0            # seconds between requests to the same host
    jitter: float = 0.3           # random extra delay, 0..jitter seconds
    timeout: float = 20.0
    retries: int = 3
    obey_robots: bool = True
    max_bytes: int = 8 * 1024 * 1024
    headers: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FetchPolicy":
        return cls(
            user_agent=data.get("user_agent", DEFAULT_USER_AGENT),
            delay=float(data.get("delay", 1.0)),
            jitter=float(data.get("jitter", 0.3)),
            timeout=float(data.get("timeout", 20.0)),
            retries=int(data.get("retries", 3)),
            obey_robots=bool(data.get("obey_robots", True)),
            max_bytes=int(data.get("max_bytes", 8 * 1024 * 1024)),
            headers=dict(data.get("headers", {})),
        )


class RobotsError(Exception):
    """Raised when robots.txt disallows a URL and obey_robots is on."""


class Fetcher:
    """HTTP getter with rate limiting, retries, robots.txt and an on-disk cache."""

    def __init__(self, policy: FetchPolicy, cache_dir: Path | None = None):
        self.policy = policy
        self.cache_dir = cache_dir
        self._last_request: dict[str, float] = {}
        self._robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        self.stats = {"requests": 0, "cache_hits": 0, "retries": 0, "blocked": 0}
        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)

    # ---- robots -----------------------------------------------------------
    def _robots_for(self, url: str) -> urllib.robotparser.RobotFileParser | None:
        parts = urllib.parse.urlsplit(url)
        host = f"{parts.scheme}://{parts.netloc}"
        if host in self._robots:
            return self._robots[host]
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(urllib.parse.urljoin(host, "/robots.txt"))
        try:
            request = urllib.request.Request(
                parser.url, headers={"User-Agent": self.policy.user_agent}
            )
            with urllib.request.urlopen(request, timeout=self.policy.timeout) as response:
                parser.parse(response.read().decode("utf-8", "replace").splitlines())
        except Exception as exc:  # no robots.txt, or unreachable -> allow
            log(f"  robots.txt unavailable for {host} ({exc}); continuing", 2)
            self._robots[host] = None
            return None
        self._robots[host] = parser
        return parser

    def allowed(self, url: str) -> bool:
        if not self.policy.obey_robots:
            return True
        parser = self._robots_for(url)
        return True if parser is None else parser.can_fetch(self.policy.user_agent, url)

    def crawl_delay(self, url: str) -> float:
        parser = self._robots_for(url) if self.policy.obey_robots else None
        if parser is None:
            return self.policy.delay
        try:
            declared = parser.crawl_delay(self.policy.user_agent)
        except Exception:
            declared = None
        return max(self.policy.delay, float(declared)) if declared else self.policy.delay

    # ---- cache ------------------------------------------------------------
    def _cache_path(self, url: str) -> Path | None:
        if not self.cache_dir:
            return None
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
        return self.cache_dir / f"{digest}.html"

    # ---- fetching ---------------------------------------------------------
    def _wait(self, url: str) -> None:
        host = urllib.parse.urlsplit(url).netloc
        delay = self.crawl_delay(url)
        elapsed = time.monotonic() - self._last_request.get(host, 0.0)
        remaining = delay + random.uniform(0, self.policy.jitter) - elapsed
        if remaining > 0:
            time.sleep(remaining)
        self._last_request[host] = time.monotonic()

    def get(self, url: str) -> str:
        """Fetch a URL as text. Raises RobotsError / urllib errors on failure."""
        cache_path = self._cache_path(url)
        if cache_path and cache_path.exists():
            self.stats["cache_hits"] += 1
            log(f"  cache {url}", 2)
            return cache_path.read_text(encoding="utf-8", errors="replace")

        if not self.allowed(url):
            self.stats["blocked"] += 1
            raise RobotsError(f"robots.txt disallows {url}")

        headers = {
            "User-Agent": self.policy.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip",
            **self.policy.headers,
        }

        last_error: Exception | None = None
        for attempt in range(self.policy.retries + 1):
            if attempt:
                backoff = min(60.0, 2 ** attempt) + random.uniform(0, 0.5)
                self.stats["retries"] += 1
                log(f"  retry {attempt}/{self.policy.retries} in {backoff:.1f}s - {url}", 1)
                time.sleep(backoff)
            self._wait(url)
            try:
                request = urllib.request.Request(url, headers=headers)
                self.stats["requests"] += 1
                with urllib.request.urlopen(request, timeout=self.policy.timeout) as response:
                    raw = response.read(self.policy.max_bytes)
                    if response.headers.get("Content-Encoding") == "gzip":
                        raw = gzip.decompress(raw)
                    charset = response.headers.get_content_charset() or "utf-8"
                    body = raw.decode(charset, "replace")
                if cache_path:
                    cache_path.write_text(body, encoding="utf-8")
                return body
            except urllib.error.HTTPError as exc:
                last_error = exc
                if exc.code in (429, 500, 502, 503, 504):
                    retry_after = exc.headers.get("Retry-After") if exc.headers else None
                    if retry_after and retry_after.isdigit():
                        time.sleep(min(60, int(retry_after)))
                    continue
                raise  # 404/403 etc: not worth retrying
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_error = exc
                continue
        raise last_error if last_error else RuntimeError(f"failed to fetch {url}")


# --------------------------------------------------------------------------
# field extraction
# --------------------------------------------------------------------------

SHORTHAND_RE = re.compile(r"^(?P<sel>.*?)(?:::(?P<what>text|html|attr\((?P<attr>[^)]+)\)))?$")


def normalise_field(spec: Any) -> dict[str, Any]:
    """Accept both `"h3 a::attr(href)"` and the long dict form."""
    if isinstance(spec, str):
        match = SHORTHAND_RE.match(spec.strip())
        assert match  # the regex matches anything
        out: dict[str, Any] = {"selector": match.group("sel").strip()}
        what = match.group("what")
        if what and what.startswith("attr"):
            out["attr"] = match.group("attr")
        elif what == "html":
            out["type"] = "html"
        return out
    return dict(spec)


def node_value(node: Node, spec: dict[str, Any]) -> str:
    if spec.get("attr"):
        return node.get(spec["attr"])
    if spec.get("type") == "html":
        return node.text  # outer HTML is intentionally not exposed; text is safer
    return node.text


def clean_value(value: str, spec: dict[str, Any], base_url: str) -> str:
    value = value.strip() if spec.get("strip", True) else value

    pattern = spec.get("regex")
    if pattern:
        match = re.search(pattern, value, re.S)
        value = "" if not match else (match.group(1) if match.groups() else match.group(0))

    replace = spec.get("replace")
    if replace:
        pairs = replace if isinstance(replace[0], (list, tuple)) else [replace]
        for old, new in pairs:
            value = value.replace(old, new)

    if spec.get("number"):
        match = re.search(r"-?\d[\d,]*(?:\.\d+)?", value)
        value = match.group(0).replace(",", "") if match else ""

    if spec.get("absolute") or spec.get("attr") in ("href", "src"):
        if value and not value.startswith(("http://", "https://", "mailto:", "tel:", "data:")):
            value = urllib.parse.urljoin(base_url, value)

    return value.strip()


def extract_item(scope: Node, fields: dict[str, Any], base_url: str) -> dict[str, str]:
    item: dict[str, str] = {}
    for name, raw_spec in fields.items():
        spec = normalise_field(raw_spec)
        selector = spec.get("selector", "")
        nodes = scope.select(selector) if selector else [scope]

        if spec.get("all"):
            values = [clean_value(node_value(n, spec), spec, base_url) for n in nodes]
            item[name] = spec.get("separator", " | ").join(v for v in values if v)
        else:
            value = clean_value(node_value(nodes[0], spec), spec, base_url) if nodes else ""
            item[name] = value or str(spec.get("default", ""))
    return item


# --------------------------------------------------------------------------
# crawling
# --------------------------------------------------------------------------

def page_urls(config: dict[str, Any]) -> list[str]:
    """Start URLs, expanding a `url_template` page range if one is configured."""
    urls = list(config.get("start_urls", []))
    if config.get("start_url"):
        urls.insert(0, config["start_url"])
    pagination = config.get("pagination", {})
    template = pagination.get("url_template")
    if template:
        start = int(pagination.get("start_page", 1))
        end = int(pagination.get("end_page", start))
        step = int(pagination.get("step", 1))
        urls.extend(template.format(page=page) for page in range(start, end + 1, step))
    return urls


def scrape(
    config: dict[str, Any],
    fetcher: Fetcher,
    max_items: int | None = None,
    max_pages: int | None = None,
) -> Iterator[dict[str, str]]:
    """Yield one dict per scraped item, following pagination as configured."""
    item_selector = config.get("item_selector")
    fields = config.get("fields") or {}
    if not fields:
        raise SystemExit("config error: 'fields' is required")

    pagination = config.get("pagination", {})
    next_selector = pagination.get("next_selector")
    page_cap = max_pages if max_pages is not None else int(pagination.get("max_pages", 50))
    stop_when_empty = bool(pagination.get("stop_when_empty", True))
    include_source = config.get("include_source_url", True)
    dedupe_on = config.get("dedupe_on") or []

    queue = page_urls(config)
    if not queue:
        raise SystemExit("config error: no 'start_urls'")

    visited: set[str] = set()
    seen_keys: set[tuple[str, ...]] = set()
    emitted = 0
    pages = 0

    while queue and pages < page_cap:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            html = fetcher.get(url)
        except RobotsError as exc:
            log(f"blocked: {exc}")
            continue
        except Exception as exc:
            log(f"failed: {url} ({exc})")
            continue

        pages += 1
        document = parse_html(html)
        scopes = document.select(item_selector) if item_selector else [document]
        log(f"[{pages}] {url} -> {len(scopes)} items", 1)

        if not scopes and stop_when_empty and next_selector:
            log("  empty page, stopping pagination", 2)
            break

        for scope in scopes:
            item = extract_item(scope, fields, url)
            if dedupe_on:
                key = tuple(item.get(name, "") for name in dedupe_on)
                if key in seen_keys:
                    continue
                seen_keys.add(key)
            if include_source:
                item["source_url"] = url
            yield item
            emitted += 1
            if max_items is not None and emitted >= max_items:
                log(f"reached item limit ({max_items})", 1)
                return

        if next_selector:
            link = document.select_one(next_selector)
            href = link.get("href") if link else ""
            if href:
                nxt = urllib.parse.urljoin(url, href)
                if nxt not in visited:
                    queue.append(nxt)


# --------------------------------------------------------------------------
# output
# --------------------------------------------------------------------------

def write_output(items: list[dict[str, str]], path: Path | None, fmt: str, columns: list[str]) -> None:
    if fmt == "csv":
        handle = path.open("w", newline="", encoding="utf-8-sig") if path else sys.stdout
        try:
            writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(items)
        finally:
            if path:
                handle.close()
    elif fmt == "json":
        text = json.dumps(items, indent=2, ensure_ascii=False)
        path.write_text(text, encoding="utf-8") if path else print(text)
    elif fmt == "jsonl":
        lines = "\n".join(json.dumps(item, ensure_ascii=False) for item in items)
        path.write_text(lines + "\n", encoding="utf-8") if path else print(lines)
    else:
        raise SystemExit(f"unknown output format: {fmt}")


def columns_for(config: dict[str, Any], items: list[dict[str, str]]) -> list[str]:
    columns = list(config.get("fields", {}).keys())
    for item in items:
        for key in item:
            if key not in columns:
                columns.append(key)
    return columns


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------

STARTER_CONFIG = {
    "name": "example",
    "start_urls": ["https://example.com/products?page=1"],
    "item_selector": "li.product",
    "fields": {
        "title": "h2.title::text",
        "price": {"selector": ".price", "number": True},
        "url": "h2.title a::attr(href)",
        "image": "img::attr(src)",
        "tags": {"selector": ".tag", "all": True, "separator": ", "},
    },
    "pagination": {"next_selector": "a.next", "max_pages": 10},
    "dedupe_on": ["url"],
    "request": {"delay": 1.0, "retries": 3, "obey_robots": True},
    "output": {"format": "csv", "path": "output.csv"},
}


def cmd_run(args: argparse.Namespace) -> int:
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    policy = FetchPolicy.from_dict(config.get("request", {}))
    if args.delay is not None:
        policy.delay = args.delay
    if args.ignore_robots:
        policy.obey_robots = False
    if args.user_agent:
        policy.user_agent = args.user_agent

    fetcher = Fetcher(policy, Path(args.cache) if args.cache else None)
    started = time.time()

    limit = args.limit if not args.dry_run else (args.limit or 5)
    max_pages = 1 if args.dry_run else args.max_pages
    items = list(scrape(config, fetcher, max_items=limit, max_pages=max_pages))

    output = config.get("output", {})
    fmt = args.format or output.get("format", "csv")
    columns = columns_for(config, items)

    if args.dry_run:
        print(json.dumps(items, indent=2, ensure_ascii=False))
    else:
        target = Path(args.out) if args.out else (Path(output["path"]) if output.get("path") else None)
        if target:
            target.parent.mkdir(parents=True, exist_ok=True)
        write_output(items, target, fmt, columns)
        if target:
            log(f"wrote {len(items)} rows -> {target}", 1)

    log(
        f"done in {time.time() - started:.1f}s | items {len(items)} | "
        f"requests {fetcher.stats['requests']} | cache {fetcher.stats['cache_hits']} | "
        f"retries {fetcher.stats['retries']} | blocked {fetcher.stats['blocked']}",
        1,
    )
    return 0 if items else 2


def cmd_probe(args: argparse.Namespace) -> int:
    """Try a selector against a live page - the fastest way to build a config."""
    policy = FetchPolicy(obey_robots=not args.ignore_robots, delay=0.0)
    if args.user_agent:
        policy.user_agent = args.user_agent
    fetcher = Fetcher(policy, Path(args.cache) if args.cache else None)
    document = parse_html(fetcher.get(args.url))
    nodes = document.select(args.selector)
    print(f"{len(nodes)} match(es) for {args.selector!r}")
    for node in nodes[: args.limit]:
        value = node.get(args.attr) if args.attr else node.text
        print(f"  {node!r:<40} {value[:140]}")
    return 0 if nodes else 1


def cmd_init(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if path.exists() and not args.force:
        raise SystemExit(f"{path} exists (use --force to overwrite)")
    config = dict(STARTER_CONFIG, name=path.stem)
    path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(f"wrote starter config -> {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scraper.py",
        description="Config-driven, robots-respecting scraper that exports CSV/JSON/JSONL.",
    )
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="run a scrape from a config file")
    run.add_argument("config")
    run.add_argument("--out", help="output path (overrides config.output.path)")
    run.add_argument("--format", choices=["csv", "json", "jsonl"])
    run.add_argument("--limit", type=int, help="stop after N items")
    run.add_argument("--max-pages", type=int, help="stop after N pages")
    run.add_argument("--delay", type=float, help="seconds between requests")
    run.add_argument("--cache", help="directory to cache fetched pages in")
    run.add_argument("--dry-run", action="store_true", help="first page only, print JSON, write nothing")
    run.add_argument("--ignore-robots", action="store_true",
                     help="only for sites you own or have written permission to crawl")
    run.add_argument("--user-agent")
    run.set_defaults(func=cmd_run)

    probe = sub.add_parser("probe", help="test a selector against one URL")
    probe.add_argument("url")
    probe.add_argument("selector")
    probe.add_argument("--attr", help="print this attribute instead of text")
    probe.add_argument("--limit", type=int, default=10)
    probe.add_argument("--cache")
    probe.add_argument("--ignore-robots", action="store_true")
    probe.add_argument("--user-agent")
    probe.set_defaults(func=cmd_probe)

    init = sub.add_parser("init", help="write a starter config to edit")
    init.add_argument("path", nargs="?", default="scrape-config.json")
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=cmd_init)

    return parser


def main(argv: list[str] | None = None) -> int:
    global VERBOSITY
    args = build_parser().parse_args(argv)
    VERBOSITY = 0 if args.quiet else 2 if args.verbose else 1
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
