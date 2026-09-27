#!/usr/bin/env python3
"""Tiny translation pipeline for the tutorial.

    python3 docs/tools/i18n.py extract            # -> docs/tools/i18n/en.txt (reference list of segments)
    python3 docs/tools/i18n.py apply --lang fr    # docs/tools/i18n/fr.txt -> docs/fr/index.html

Segments are the inner HTML of "leaf" elements (paragraphs, list items, headings, table cells,
SVG <text>, buttons ...) plus alt / title / aria-label attributes, taken from the *raw* source so
that the generated page keeps byte-identical markup everywhere else (inline SVG diagrams included).
A translation file lists `@id hash` headers followed by the translated segment; segments that are
missing keep the English text and are reported.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

DOCS = Path(__file__).resolve().parents[1]
I18N = DOCS / "tools" / "i18n"
EN_HTML = DOCS / "index.html"

SEG_TAGS = {"title", "h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "figcaption", "dt", "dd", "td", "th",
            "button", "text", "summary", "label", "caption", "a", "span", "small", "strong", "em", "div",
            "nav", "footer", "header", "section", "blockquote", "cite", "option", "legend", "desc"}
INLINE = {"a", "strong", "em", "b", "i", "kbd", "code", "span", "button", "br", "sup", "sub", "small", "abbr",
          "tspan", "wbr", "mark", "time"}
VOID = {"img", "br", "meta", "link", "input", "hr", "source", "wbr", "area", "base", "col", "embed", "param", "track"}
ATTRS = ("alt", "title", "aria-label", "placeholder", "content", "data-label")

LANG = {
    "fr": {
        "dir": DOCS / "fr",
        "pdf": "photographier-comme-un-pro-avec-votre-telephone.pdf",
        "switch": '<a class="btn btn-ghost btn-sm lang-switch" href="../" lang="en" hreflang="en" title="Read this guide in English">EN · English</a>',
    }
}


class Seg:
    __slots__ = ("id", "kind", "tag", "start", "end", "text")

    def __init__(self, kind, tag, start, end, text):
        self.kind, self.tag, self.start, self.end, self.text = kind, tag, start, end, text
        self.id = 0

    @property
    def hash(self):
        return hashlib.sha1(re.sub(r"\s+", " ", self.text.strip()).encode()).hexdigest()[:6]


class Extractor(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=False)
        self.raw = raw
        self.line_starts = [0]
        for m in re.finditer("\n", raw):
            self.line_starts.append(m.end())
        self.stack = []      # [tag, inner_start, descendant_tags(set)]
        self.cands = []
        self.attr_segs = []

    def abs(self):
        line, col = self.getpos()
        return self.line_starts[line - 1] + col

    def handle_starttag(self, tag, attrs):
        pos = self.abs()
        st = self.get_starttag_text()
        inner_start = pos + len(st)
        for parent in self.stack:
            parent[2].add(tag)
        # translatable attributes
        d = dict(attrs)
        for m in re.finditer(r'\s(alt|title|aria-label|placeholder|content|data-label)="([^"]*)"', st):
            name, val = m.group(1), m.group(2)
            if not val.strip() or not re.search(r"[A-Za-z]", val):
                continue
            if name == "content" and not (tag == "meta" and re.search(r"description|title", d.get("name", "") + d.get("property", ""))):
                continue
            s = pos + m.start(2)
            self.attr_segs.append(Seg("attr", f"{tag}@{name}", s, s + len(val), val))
        if tag in VOID or st.endswith("/>"):
            return
        self.stack.append([tag, inner_start, set()])

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if not (tag in VOID) and not self.get_starttag_text().endswith("/>"):
            self.stack.pop()

    def handle_endtag(self, tag):
        end = self.abs()
        # pop to the matching tag (tolerates unclosed inline tags)
        idx = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                idx = i
                break
        if idx is None:
            return
        t, inner_start, desc = self.stack[idx]
        del self.stack[idx:]
        if t in SEG_TAGS and desc <= INLINE:
            text = self.raw[inner_start:end]
            plain = re.sub(r"<[^>]+>", "", text)
            if re.search(r"[A-Za-z]", plain):
                self.cands.append(Seg("html", t, inner_start, end, text))


def extract(raw: str) -> list[Seg]:
    p = Extractor(raw)
    p.feed(raw)
    p.close()
    # outermost wins
    cands = sorted(p.cands, key=lambda s: (s.start, -s.end))
    segs, last_end = [], -1
    for s in cands:
        if s.start < last_end:
            continue
        segs.append(s)
        last_end = s.end
    # attributes that sit inside a translated html segment are covered by that segment
    segs += [a for a in p.attr_segs if not any(h.start <= a.start < h.end for h in segs)]
    segs.sort(key=lambda s: s.start)
    for i, s in enumerate(segs, 1):
        s.id = i
    return segs


def dump(segs: list[Seg], path: Path) -> None:
    out = []
    for s in segs:
        out.append(f"@{s.id:04d} [{s.tag}] {s.hash}\n{s.text.strip()}\n")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out), encoding="utf-8")


def load_translation(path: Path) -> dict[int, tuple[str, str]]:
    """Returns {id: (hash_or_empty, text)}."""
    result = {}
    cur = None
    buf: list[str] = []
    hdr = re.compile(r"^@(\d{1,5})(?:\s+\[[^\]]*\])?(?:\s+([0-9a-f]{6}))?\s*$")

    def flush():
        if cur is not None:
            text = "\n".join(buf).strip()
            if text:
                result[cur[0]] = (cur[1], text)

    for line in path.read_text(encoding="utf-8").splitlines():
        m = hdr.match(line)
        if m:
            flush()
            cur = (int(m.group(1)), m.group(2) or "")
            buf = []
        elif cur is not None:
            buf.append(line)
    flush()
    return result


def french_typography(text: str) -> str:
    """Non-breaking spaces before high punctuation and inside guillemets (only outside tags)."""
    parts = re.split(r"(<[^>]+>)", text)
    for i, part in enumerate(parts):
        if part.startswith("<"):
            continue
        part = re.sub(r"(?<=\S) ([;:?!»])", "\u00a0\\1", part)
        part = re.sub(r"« (?=\S)", "«\u00a0", part)
        parts[i] = part
    return "".join(parts)


def apply(lang: str) -> None:
    cfg = LANG[lang]
    raw = EN_HTML.read_text(encoding="utf-8")
    segs = extract(raw)
    tr = load_translation(I18N / f"{lang}.txt")
    missing, mismatched = [], []
    out = raw
    for s in reversed(segs):            # splice from the end so offsets stay valid
        if s.id not in tr:
            missing.append(s)
            continue
        h, text = tr[s.id]
        if h and h != s.hash:
            mismatched.append((s, h))
        if lang == "fr":
            text = french_typography(text)
        if s.kind == "attr":
            text = text.replace('"', "&quot;").replace("\n", " ")
        out = out[:s.start] + text + out[s.end:]

    # language / paths / cross-links
    out = out.replace('<html lang="en">', f'<html lang="{lang}">', 1)
    out = re.sub(r'(href|src|content)="(css|js|images)/', rf'\1="../\2/', out)
    out = out.replace('href="shoot-like-a-pro-with-your-phone.pdf"', f'href="{cfg["pdf"]}"')
    out = re.sub(r'<a class="btn btn-ghost btn-sm lang-switch"[^>]*>.*?</a>', cfg["switch"], out, count=1, flags=re.S)
    out = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="https://gide26.github.io/Gide26/{lang}/">', out)

    dest = cfg["dir"] / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding="utf-8")
    print(f"wrote {dest.relative_to(DOCS.parent)}  ({len(segs) - len(missing)}/{len(segs)} segments translated)")
    if mismatched:
        print(f"WARNING: {len(mismatched)} segments changed in English since they were translated:")
        for s, h in mismatched[:20]:
            print(f"   @{s.id:04d} [{s.tag}] now {s.hash}, file says {h}: {s.text.strip()[:70]!r}")
    if missing:
        print(f"untranslated ({len(missing)}):")
        for s in missing[:40]:
            print(f"   @{s.id:04d} [{s.tag}] {s.hash}: {s.text.strip()[:70]!r}")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract")
    e.add_argument("--out", default=str(I18N / "en.txt"))
    a = sub.add_parser("apply")
    a.add_argument("--lang", required=True, choices=sorted(LANG))
    args = ap.parse_args()
    if args.cmd == "extract":
        segs = extract(EN_HTML.read_text(encoding="utf-8"))
        dump(segs, Path(args.out))
        kinds = {}
        for s in segs:
            kinds[s.tag] = kinds.get(s.tag, 0) + 1
        words = sum(len(re.sub(r"<[^>]+>", " ", s.text).split()) for s in segs)
        print(f"{len(segs)} segments, ~{words} words -> {args.out}")
        print(", ".join(f"{k}:{v}" for k, v in sorted(kinds.items(), key=lambda kv: -kv[1])))
    else:
        apply(args.lang)


if __name__ == "__main__":
    main()
