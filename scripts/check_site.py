"""Check generated routes, links, contact targets and SEO metadata before publishing."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote, parse_qs
import json
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SITE = json.loads((ROOT / "data/site.json").read_text(encoding="utf-8"))
ORIGIN = SITE["domain"].rstrip("/")
errors = []


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.references = []
        self.meta = {}
        self.canonicals = []
        self.h1s = 0
        self.title = ""
        self.in_title = False
        self.json_ld = []
        self.script = None
        self.label_targets = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.append(a["id"])
        if tag in ("a", "link") and a.get("href"):
            if a.get("rel") == "canonical":
                self.canonicals.append(a["href"])
            else:
                self.references.append(a["href"])
        if tag in ("script", "img") and a.get("src"):
            self.references.append(a["src"])
        if tag == "img" and not a.get("alt"):
            errors.append("Image without alternative text")
        if tag == "meta":
            self.meta[a.get("name", a.get("property", ""))] = a.get("content", "")
        if tag == "h1":
            self.h1s += 1
        if tag == "title":
            self.in_title = True
        if tag == "script" and a.get("type") == "application/ld+json":
            self.script = ""
        if tag == "label" and a.get("for"):
            self.label_targets.append(a["for"])

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.script is not None:
            self.script += data

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "script" and self.script is not None:
            try:
                self.json_ld.append(json.loads(self.script))
            except json.JSONDecodeError:
                errors.append("Invalid JSON-LD")
            self.script = None


def local_path(url):
    path = unquote(urlsplit(url).path).lstrip("/")
    return DIST / (path + "index.html" if not path or path.endswith("/") else path)


pages = {}
for file in DIST.rglob("*.html"):
    parsed = Page(file.read_text(encoding="utf-8"))
    pages[file] = parsed
    rel = file.relative_to(DIST).as_posix()
    if parsed.h1s != 1 or not parsed.title or not parsed.meta.get("description"):
        errors.append(f"Missing page heading or metadata: {rel}")
    if len(set(parsed.ids)) != len(parsed.ids):
        errors.append(f"Duplicate HTML id: {rel}")
    if set(parsed.label_targets) - set(parsed.ids):
        errors.append(f"Unbound form label: {rel}")
    if rel == "404.html":
        if "noindex" not in parsed.meta.get("robots", ""):
            errors.append("404 page must be noindex")
        continue
    expected = ORIGIN + "/" + rel.removesuffix("index.html")
    if parsed.canonicals != [expected]:
        errors.append(f"Unexpected canonical: {rel}")
    if SITE.get("indexable") and parsed.meta.get("robots") != "index, follow":
        errors.append(f"Page unexpectedly excluded from indexing: {rel}")
    if not parsed.json_ld:
        errors.append(f"Missing structured data: {rel}")

checked_links = 0
for file, parsed in pages.items():
    rel = file.relative_to(DIST).as_posix()
    page_url = ORIGIN + "/" + rel.removesuffix("index.html")
    for reference in parsed.references:
        target = urlsplit(urljoin(page_url, reference))
        if target.scheme == "tel":
            if target.path != "+905433719972":
                errors.append(f"Unexpected phone number in {rel}")
            continue
        if target.hostname == "wa.me":
            if target.path != "/905433719972":
                errors.append(f"Unexpected WhatsApp number in {rel}")
            if "Sayfa: " + page_url not in parse_qs(target.query).get("text", [""])[0] and rel != "404.html":
                errors.append(f"Missing WhatsApp source context in {rel}")
            continue
        if target.scheme not in ("http", "https") or target.hostname != urlsplit(ORIGIN).hostname:
            continue
        checked_links += 1
        destination = local_path(target.geturl())
        if not destination.is_file():
            errors.append(f"Broken link in {rel}: {reference}")
        elif target.fragment and destination in pages and unquote(target.fragment) not in pages[destination].ids:
            errors.append(f"Missing anchor in {rel}: {reference}")

sitemap = ET.parse(DIST / "sitemap.xml")
urls = [e.text for e in sitemap.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
if len(urls) != len(set(urls)):
    errors.append("Duplicate sitemap URL")
expected_urls = {ORIGIN + "/" + file.relative_to(DIST).as_posix().removesuffix("index.html") for file in pages if file.name == "index.html"}
if SITE.get("indexable") and set(urls) != expected_urls:
    errors.append("Sitemap does not match generated index pages")
for title, count in Counter(p.title for p in pages.values()).items():
    if count > 1:
        errors.append(f"Duplicate page title: {title}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"PASS: {len(pages)} HTML documents, {len(urls)} sitemap URLs, {checked_links} internal references; contact targets, anchors, form labels and metadata valid.")
