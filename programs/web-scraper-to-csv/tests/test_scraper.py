"""Tests for the scraper and its selector engine.

Everything runs against a throwaway HTTP server on localhost - no internet
access is required. Run: python3 -m unittest discover -s tests
"""

import csv
import json
import shutil
import sys
import tempfile
import threading
import unittest
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scraper  # noqa: E402
from minidom import parse_html  # noqa: E402

scraper.VERBOSITY = 0

PAGE_1 = """
<!doctype html><html><head><title>Catalog</title>
<style>.price { color: red }</style></head>
<body>
  <div id="grid" class="grid wide">
    <article class="product" data-sku="A-1">
      <h3><a href="/item/anvil" title="Anvil">Anvil</a></h3>
      <p class="price">$19.99</p>
      <span class="stock">In stock (7 available)</span>
      <span class="tag">metal</span><span class="tag">heavy</span>
    </article>
    <article class="product featured" data-sku="A-2">
      <h3><a href="/item/rope" title="Rope">Rope</a></h3>
      <p class="price">$4.50</p>
      <span class="stock">In stock (23 available)</span>
      <span class="tag">fibre</span>
    </article>
    <article class="product" data-sku="A-3">
      <h3><a href="/item/lantern" title="Lantern">Lantern</a>
      <p class="price">$12.00</p>
      <span class="stock">Out of stock</span>
  </div>
  <ul class="pager"><li><a class="next" href="page2.html">Next</a></li></ul>
  <script>var noise = "should not appear in text";</script>
</body></html>
"""

PAGE_2 = """
<!doctype html><html><body>
  <div id="grid">
    <article class="product" data-sku="B-1">
      <h3><a href="/item/anvil" title="Anvil">Anvil</a></h3>
      <p class="price">$19.99</p><span class="stock">In stock (2 available)</span>
    </article>
    <article class="product" data-sku="B-2">
      <h3><a href="/item/chain" title="Chain">Chain</a></h3>
      <p class="price">$8.25</p><span class="stock">In stock (5 available)</span>
    </article>
  </div>
  <ul class="pager"><li><span class="next-disabled">Next</span></li></ul>
</body></html>
"""


class _QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):  # keep test output clean
        pass


class ServerCase(unittest.TestCase):
    """Base class that serves ./fixtures over HTTP for the duration of a test."""

    @classmethod
    def setUpClass(cls):
        # Never route localhost through an ambient HTTP proxy.
        urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))
        cls.root = Path(tempfile.mkdtemp(prefix="scraper-fixtures-"))
        (cls.root / "page1.html").write_text(PAGE_1, encoding="utf-8")
        (cls.root / "page2.html").write_text(PAGE_2, encoding="utf-8")
        handler = partial(_QuietHandler, directory=str(cls.root))
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.base = f"http://127.0.0.1:{cls.server.server_port}/"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)
        shutil.rmtree(cls.root, ignore_errors=True)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.workdir = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        # main() sets the global verbosity; put it back so tests stay quiet.
        self.addCleanup(setattr, scraper, "VERBOSITY", 0)
        robots = self.root / "robots.txt"
        if robots.exists():
            robots.unlink()

    def config(self, **overrides):
        config = {
            "name": "test",
            "start_urls": [self.base + "page1.html"],
            "item_selector": "article.product",
            "fields": {
                "title": "h3 a::attr(title)",
                "price": {"selector": ".price", "number": True},
                "url": "h3 a::attr(href)",
                "stock": {"selector": ".stock", "regex": r"(\d+) available", "default": "0"},
            },
            "pagination": {"next_selector": "a.next", "max_pages": 5},
            "request": {"delay": 0, "jitter": 0, "retries": 1, "obey_robots": False},
        }
        config.update(overrides)
        return config

    def fetcher(self, **policy_overrides):
        policy = scraper.FetchPolicy(delay=0, jitter=0, retries=1, obey_robots=False)
        for key, value in policy_overrides.items():
            setattr(policy, key, value)
        return scraper.Fetcher(policy)


# --------------------------------------------------------------------------
# selector engine
# --------------------------------------------------------------------------

class MiniDomTests(unittest.TestCase):
    def setUp(self):
        self.doc = parse_html(PAGE_1)

    def test_class_and_tag_selectors(self):
        self.assertEqual(len(self.doc.select("article.product")), 3)
        self.assertEqual(len(self.doc.select(".featured")), 1)
        self.assertEqual(len(self.doc.select("h3")), 3)

    def test_id_and_descendant(self):
        self.assertEqual(len(self.doc.select("#grid .price")), 3)
        self.assertIsNotNone(self.doc.select_one("#grid"))

    def test_child_combinator_is_stricter_than_descendant(self):
        self.assertEqual(len(self.doc.select("#grid > article")), 3)
        self.assertEqual(len(self.doc.select("#grid > a")), 0)
        self.assertEqual(len(self.doc.select("#grid a")), 3)

    def test_attribute_operators(self):
        self.assertEqual(len(self.doc.select("[data-sku]")), 3)
        self.assertEqual(len(self.doc.select('[data-sku="A-2"]')), 1)
        self.assertEqual(len(self.doc.select('a[href^="/item/"]')), 3)
        self.assertEqual(len(self.doc.select('a[href$="rope"]')), 1)
        self.assertEqual(len(self.doc.select('[class*="feature"]')), 1)

    def test_groups_and_pseudo_classes(self):
        self.assertEqual(len(self.doc.select(".price, .stock")), 6)
        self.assertEqual(self.doc.select("article:first-child")[0].get("data-sku"), "A-1")
        self.assertEqual(len(self.doc.select("article:not(.featured)")), 2)
        self.assertEqual(self.doc.select("article:nth-child(2)")[0].get("data-sku"), "A-2")

    def test_text_is_collapsed_and_skips_script_and_style(self):
        first = self.doc.select_one("article.product")
        self.assertIn("Anvil", first.text)
        self.assertNotIn("\n", first.text)
        body = self.doc.select_one("body").text
        self.assertNotIn("should not appear", body)
        self.assertNotIn("color: red", body)

    def test_unclosed_tags_do_not_lose_content(self):
        # the third article never closes <h3>, <p> or </article> in PAGE_1
        third = self.doc.select("article.product")[2]
        self.assertEqual(third.get("data-sku"), "A-3")
        self.assertIn("Lantern", third.text)
        self.assertEqual(third.select_one(".price").text, "$12.00")

    def test_missing_selector_returns_empty_not_error(self):
        self.assertEqual(self.doc.select(".nope"), [])
        self.assertIsNone(self.doc.select_one(".nope"))

    def test_adjacent_elements_keep_a_word_boundary(self):
        doc = parse_html("<p><b>one</b> <b>two</b></p>")
        self.assertEqual(doc.select_one("p").text, "one two")


# --------------------------------------------------------------------------
# field extraction
# --------------------------------------------------------------------------

class ExtractionTests(unittest.TestCase):
    def setUp(self):
        self.doc = parse_html(PAGE_1)
        self.scope = self.doc.select_one("article.product")

    def test_shorthand_forms(self):
        self.assertEqual(scraper.normalise_field("h3 a::text"), {"selector": "h3 a"})
        self.assertEqual(
            scraper.normalise_field("h3 a::attr(href)"), {"selector": "h3 a", "attr": "href"}
        )

    def test_number_regex_and_default(self):
        fields = {
            "price": {"selector": ".price", "number": True},
            "qty": {"selector": ".stock", "regex": r"(\d+) available", "default": "0"},
            "missing": {"selector": ".nope", "default": "n/a"},
        }
        item = scraper.extract_item(self.scope, fields, "http://x/")
        self.assertEqual(item, {"price": "19.99", "qty": "7", "missing": "n/a"})

    def test_relative_links_become_absolute(self):
        item = scraper.extract_item(self.scope, {"url": "h3 a::attr(href)"}, "http://x/shop/page1.html")
        self.assertEqual(item["url"], "http://x/item/anvil")

    def test_all_joins_repeated_nodes(self):
        fields = {"tags": {"selector": ".tag", "all": True, "separator": ", "}}
        self.assertEqual(scraper.extract_item(self.scope, fields, "http://x/")["tags"], "metal, heavy")

    def test_replace_pairs(self):
        fields = {"price": {"selector": ".price", "replace": [["$", ""], [".", ","]]}}
        self.assertEqual(scraper.extract_item(self.scope, fields, "http://x/")["price"], "19,99")


# --------------------------------------------------------------------------
# end to end
# --------------------------------------------------------------------------

class ScrapeTests(ServerCase):
    def test_follows_pagination_and_extracts_every_item(self):
        items = list(scraper.scrape(self.config(), self.fetcher()))
        self.assertEqual(len(items), 5)  # 3 on page 1 + 2 on page 2
        self.assertEqual(items[0]["title"], "Anvil")
        self.assertEqual(items[0]["price"], "19.99")
        self.assertEqual(items[0]["stock"], "7")
        self.assertEqual(items[2]["stock"], "0")  # "Out of stock" -> default
        self.assertTrue(items[0]["url"].endswith("/item/anvil"))
        self.assertTrue(all(i["source_url"].startswith(self.base) for i in items))

    def test_pagination_stops_when_next_link_is_absent(self):
        items = list(scraper.scrape(self.config(), self.fetcher()))
        self.assertEqual({i["source_url"] for i in items},
                         {self.base + "page1.html", self.base + "page2.html"})

    def test_max_pages_and_limit_are_honoured(self):
        self.assertEqual(len(list(scraper.scrape(self.config(), self.fetcher(), max_pages=1))), 3)
        self.assertEqual(len(list(scraper.scrape(self.config(), self.fetcher(), max_items=2))), 2)

    def test_dedupe_on_drops_repeats_across_pages(self):
        config = self.config(dedupe_on=["url"])
        items = list(scraper.scrape(config, self.fetcher()))
        self.assertEqual(len(items), 4)  # the Anvil appears on both pages
        self.assertEqual(len({i["url"] for i in items}), 4)

    def test_url_template_pagination(self):
        config = self.config(
            start_urls=[],
            pagination={"url_template": self.base + "page{page}.html", "start_page": 1, "end_page": 2},
        )
        self.assertEqual(len(list(scraper.scrape(config, self.fetcher()))), 5)

    def test_cache_avoids_a_second_request(self):
        cache = self.workdir / "cache"
        fetcher = scraper.Fetcher(scraper.FetchPolicy(delay=0, jitter=0, obey_robots=False), cache)
        url = self.base + "page1.html"
        fetcher.get(url)
        fetcher.get(url)
        self.assertEqual(fetcher.stats["requests"], 1)
        self.assertEqual(fetcher.stats["cache_hits"], 1)


class RobotsTests(ServerCase):
    def write_robots(self, body):
        (self.root / "robots.txt").write_text(body, encoding="utf-8")

    def test_disallowed_url_is_refused(self):
        self.write_robots("User-agent: *\nDisallow: /page1.html\n")
        fetcher = self.fetcher(obey_robots=True)
        self.assertFalse(fetcher.allowed(self.base + "page1.html"))
        with self.assertRaises(scraper.RobotsError):
            fetcher.get(self.base + "page1.html")

    def test_allowed_url_passes(self):
        self.write_robots("User-agent: *\nDisallow: /admin/\n")
        fetcher = self.fetcher(obey_robots=True)
        self.assertTrue(fetcher.allowed(self.base + "page1.html"))
        self.assertIn("Anvil", fetcher.get(self.base + "page1.html"))

    def test_missing_robots_txt_allows_crawling(self):
        self.assertTrue(self.fetcher(obey_robots=True).allowed(self.base + "page1.html"))

    def test_crawl_delay_from_robots_wins_over_config(self):
        self.write_robots("User-agent: *\nCrawl-delay: 3\n")
        fetcher = self.fetcher(obey_robots=True)
        self.assertEqual(fetcher.crawl_delay(self.base + "page1.html"), 3.0)


class CliTests(ServerCase):
    def write_config(self, **overrides):
        path = self.workdir / "config.json"
        path.write_text(json.dumps(self.config(**overrides)), encoding="utf-8")
        return path

    def test_run_writes_csv_with_configured_columns(self):
        config = self.write_config()
        out = self.workdir / "out.csv"
        self.assertEqual(scraper.main(["-q", "run", str(config), "--out", str(out)]), 0)
        with out.open(encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 5)
        self.assertEqual(list(rows[0].keys()), ["title", "price", "url", "stock", "source_url"])
        self.assertEqual(rows[1]["title"], "Rope")

    def test_run_writes_jsonl(self):
        config = self.write_config()
        out = self.workdir / "out.jsonl"
        scraper.main(["-q", "run", str(config), "--out", str(out), "--format", "jsonl"])
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines), 5)
        self.assertEqual(json.loads(lines[0])["title"], "Anvil")

    def test_limit_flag_caps_rows(self):
        config = self.write_config()
        out = self.workdir / "out.json"
        scraper.main(["-q", "run", str(config), "--out", str(out), "--format", "json", "--limit", "2"])
        self.assertEqual(len(json.loads(out.read_text())), 2)

    def test_init_writes_a_usable_starter_config(self):
        path = self.workdir / "starter.json"
        scraper.main(["-q", "init", str(path)])
        config = json.loads(path.read_text())
        self.assertIn("fields", config)
        self.assertEqual(config["name"], "starter")


if __name__ == "__main__":
    unittest.main()
