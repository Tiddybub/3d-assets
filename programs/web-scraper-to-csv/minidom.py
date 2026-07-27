"""A tiny HTML tree + CSS selector engine built on the standard library.

Exists so the scraper has no third-party dependencies. It covers the selector
syntax real scraping jobs actually use:

    tag  #id  .class  [attr]  [attr=v]  [attr^=v]  [attr$=v]  [attr*=v]  [attr~=v]
    ancestor descendant      parent > child      a, b  (groups)
    :first-child  :last-child  :nth-child(n)  :not(simple)

It is deliberately not a full CSS4 implementation. If a selector gets hairy,
prefer chaining `select()` calls over extending this file.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Iterator

VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}
SKIP_TEXT_TAGS = {"script", "style", "noscript", "template"}


class Node:
    """One element in the document tree. Text lives in `data` on `#text` nodes."""

    __slots__ = ("tag", "attrs", "children", "parent", "data", "order")

    def __init__(self, tag: str, attrs: dict[str, str] | None = None, parent: "Node | None" = None):
        self.tag = tag
        self.attrs: dict[str, str] = attrs or {}
        self.children: list[Node] = []
        self.parent = parent
        self.data = ""
        self.order = 0

    # ---- navigation -------------------------------------------------------
    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        ident = f"#{self.attrs['id']}" if "id" in self.attrs else ""
        cls = "." + ".".join(self.classes) if self.classes else ""
        return f"<{self.tag}{ident}{cls}>"

    @property
    def classes(self) -> list[str]:
        return self.attrs.get("class", "").split()

    @property
    def elements(self) -> list["Node"]:
        return [c for c in self.children if c.tag != "#text"]

    def descendants(self) -> Iterator["Node"]:
        for child in self.children:
            if child.tag != "#text":
                yield child
                yield from child.descendants()

    # ---- content ----------------------------------------------------------
    @property
    def text(self) -> str:
        """Visible text of this node and its descendants, whitespace collapsed."""
        parts: list[str] = []
        self._collect_text(parts)
        return re.sub(r"\s+", " ", "".join(parts)).strip()

    def _collect_text(self, parts: list[str]) -> None:
        if self.tag in SKIP_TEXT_TAGS:
            return
        for child in self.children:
            if child.tag == "#text":
                parts.append(child.data)
            else:
                child._collect_text(parts)

    def get(self, name: str, default: str = "") -> str:
        return self.attrs.get(name.lower(), default)

    # ---- querying ---------------------------------------------------------
    def select(self, selector: str) -> list["Node"]:
        """All descendants matching a (possibly grouped) CSS selector."""
        seen: dict[int, Node] = {}
        for group in split_groups(selector):
            for node in _match_group(self, group):
                seen[node.order] = node
        return [seen[key] for key in sorted(seen)]

    def select_one(self, selector: str) -> "Node | None":
        matches = self.select(selector)
        return matches[0] if matches else None


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------

class _TreeBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("#document")
        self.stack = [self.root]
        self.counter = 0

    def _add(self, node: Node) -> None:
        self.counter += 1
        node.order = self.counter
        node.parent = self.stack[-1]
        self.stack[-1].children.append(node)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(tag.lower(), {k.lower(): (v or "") for k, v in attrs})
        self._add(node)
        if tag.lower() not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._add(Node(tag.lower(), {k.lower(): (v or "") for k, v in attrs}))

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in VOID_TAGS:
            return
        # Real-world HTML leaves tags unclosed; unwind to the nearest match.
        for depth in range(len(self.stack) - 1, 0, -1):
            if self.stack[depth].tag == tag:
                del self.stack[depth:]
                return

    def handle_data(self, data: str) -> None:
        if not data.strip():
            # keep a single space so "<b>a</b> <b>b</b>" does not become "ab"
            if data and self.stack[-1].children:
                node = Node("#text", parent=self.stack[-1])
                node.data = " "
                self.stack[-1].children.append(node)
            return
        node = Node("#text")
        node.data = data
        self._add(node)


def parse_html(html: str) -> Node:
    """Parse a document into a tree. Never raises on malformed markup."""
    builder = _TreeBuilder()
    builder.feed(html)
    builder.close()
    return builder.root


# --------------------------------------------------------------------------
# selector parsing + matching
# --------------------------------------------------------------------------

_SIMPLE_RE = re.compile(
    r"""
    (?P<tag>^[a-zA-Z][\w-]*|\*)
  | \#(?P<id>[\w-]+)
  | \.(?P<cls>[\w-]+)
  | \[(?P<attr>[\w:-]+)(?:(?P<op>[~^$*|]?=)(?P<val>"[^"]*"|'[^']*'|[^\]]*))?\]
  | :(?P<pseudo>[\w-]+)(?:\((?P<arg>[^)]*)\))?
    """,
    re.X,
)


def split_groups(selector: str) -> list[list[tuple[str, str]]]:
    """'a b, c > d' -> [[(' ','a'),(' ','b')], [(' ','c'),('>','d')]]"""
    groups = []
    for part in selector.split(","):
        part = part.strip()
        if not part:
            continue
        tokens = re.split(r"\s*(>)\s*|\s+", part)
        steps: list[tuple[str, str]] = []
        combinator = " "
        for token in tokens:
            if token is None or token == "":
                continue
            if token == ">":
                combinator = ">"
                continue
            steps.append((combinator, token))
            combinator = " "
        if steps:
            groups.append(steps)
    return groups


def matches_simple(node: Node, simple: str) -> bool:
    """Test one compound selector such as `a.btn[href^=/x]:not(.off)`."""
    if node.tag == "#text":
        return False
    position = 0
    matched_any = False
    while position < len(simple):
        match = _SIMPLE_RE.match(simple, position)
        if not match:
            return False
        position = match.end()
        matched_any = True
        groups = match.groupdict()

        if groups["tag"]:
            if groups["tag"] != "*" and node.tag != groups["tag"].lower():
                return False
        elif groups["id"]:
            if node.get("id") != groups["id"]:
                return False
        elif groups["cls"]:
            if groups["cls"] not in node.classes:
                return False
        elif groups["attr"]:
            if not _attr_matches(node, groups["attr"], groups["op"], groups["val"]):
                return False
        elif groups["pseudo"]:
            if not _pseudo_matches(node, groups["pseudo"], groups["arg"]):
                return False
    return matched_any


def _attr_matches(node: Node, name: str, op: str | None, raw: str | None) -> bool:
    name = name.lower()
    if name not in node.attrs:
        return False
    if op is None:
        return True
    value = (raw or "").strip().strip("\"'")
    actual = node.attrs[name]
    if op == "=":
        return actual == value
    if op == "^=":
        return actual.startswith(value)
    if op == "$=":
        return actual.endswith(value)
    if op == "*=":
        return value in actual
    if op == "~=":
        return value in actual.split()
    if op == "|=":
        return actual == value or actual.startswith(value + "-")
    return False


def _pseudo_matches(node: Node, pseudo: str, arg: str | None) -> bool:
    siblings = node.parent.elements if node.parent else [node]
    if pseudo == "first-child":
        return bool(siblings) and siblings[0] is node
    if pseudo == "last-child":
        return bool(siblings) and siblings[-1] is node
    if pseudo == "nth-child":
        try:
            index = int((arg or "").strip())
        except ValueError:
            return False
        return 1 <= index <= len(siblings) and siblings[index - 1] is node
    if pseudo == "only-child":
        return len(siblings) == 1
    if pseudo == "not":
        return not matches_simple(node, (arg or "").strip())
    if pseudo == "empty":
        return not node.elements and not node.text
    return False


def _match_group(root: Node, steps: list[tuple[str, str]]) -> list[Node]:
    current = [root]
    for combinator, simple in steps:
        found: dict[int, Node] = {}
        for node in current:
            pool = node.elements if combinator == ">" else node.descendants()
            for candidate in pool:
                if matches_simple(candidate, simple):
                    found[candidate.order] = candidate
        current = [found[key] for key in sorted(found)]
        if not current:
            return []
    return current
