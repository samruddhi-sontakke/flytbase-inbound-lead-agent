"""Deterministic 'hands' the agent calls through the leaddesk MCP server:
page reading (requests + BeautifulSoup), sitemap crawling and Reddit search (Arctic Shift).
Web *search* is done by Claude's own WebSearch tool; every page it uses is read here so the raw text is stored."""
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup

from . import config, log

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) LeadResearchAgent/1.0"}
LANG_PREFIX = re.compile(r"^https?://[^/]+/(es|de|fr|ja|ko|zh|pt|ru|it|ar|nl|tr)/")

_page_cache = {}


# ---------- page reading ----------

def fetch_text(url, max_chars=12000):
    """Download a page and return its readable text (menus, scripts removed)."""
    if url in _page_cache:
        return _page_cache[url][:max_chars]
    try:
        r = requests.get(url, headers=HEADERS, timeout=25)
        r.raise_for_status()
    except Exception as e:
        log.warn(f"could not open {url}: {str(e)[:80]}")
        _page_cache[url] = ""
        return ""
    ctype = r.headers.get("content-type", "").lower()
    if "officedocument.wordprocessingml" in ctype or url.lower().split("?")[0].endswith(".docx"):
        text = _docx_text(r.content)
        _page_cache[url] = text
        _page_cache[url + "#title"] = url.rsplit("/", 1)[-1] or url
        return text[:max_chars]
    if "pdf" in ctype or r.content[:5] == b"%PDF-":
        text = _pdf_text(r.content)
        _page_cache[url] = text
        _page_cache[url + "#title"] = url.rsplit("/", 1)[-1] or url
        return text[:max_chars]
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "noscript", "svg", "form"]):
        tag.decompose()
    main = soup.find("main") or soup.body or soup
    text = re.sub(r"\s+", " ", main.get_text(" ", strip=True))
    title = soup.title.get_text(strip=True) if soup.title else url
    _page_cache[url] = text
    _page_cache[url + "#title"] = title
    return text[:max_chars]


def _pdf_text(data, max_pages=60):
    """Text of an annual report / 20-F / investor letter PDF (first max_pages pages)."""
    import io
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        pages = [(p.extract_text() or "") for p in reader.pages[:max_pages]]
    except Exception as e:
        log.warn(f"could not read PDF: {str(e)[:80]}")
        return ""
    return re.sub(r"\s+", " ", " ".join(pages)).strip()


def _docx_text(data):
    """Text of a Word .docx (press releases are often published as attachments). A .docx is a zip of XML:
    read word/document.xml and keep the text runs, one paragraph per line."""
    import io
    import zipfile
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            xml = z.read("word/document.xml").decode("utf-8", "ignore")
    except Exception as e:
        log.warn(f"could not read DOCX: {str(e)[:80]}")
        return ""
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<w:tab/>", " ", xml)
    text = re.sub(r"<[^>]+>", "", xml)
    import html
    return re.sub(r"[ \t]+", " ", html.unescape(text)).strip()


def page_title(url):
    return _page_cache.get(url + "#title", url)


def fetch_many(urls, max_chars=12000, workers=8):
    with ThreadPoolExecutor(max_workers=workers) as ex:
        texts = list(ex.map(lambda u: fetch_text(u, max_chars), urls))
    return dict(zip(urls, texts))


def sitemap_urls(site, section_filter=None):
    """Read a site's sitemap.xml (and nested sitemaps). English pages only."""
    def locs(url):
        try:
            r = requests.get(url, headers=HEADERS, timeout=25)
            r.raise_for_status()
            root = ET.fromstring(r.content)
        except Exception:
            return [], []
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        sub = [e.text.strip() for e in root.findall("s:sitemap/s:loc", ns)]
        pages = [e.text.strip() for e in root.findall("s:url/s:loc", ns)]
        return sub, pages

    sub, pages = locs(site.rstrip("/") + "/sitemap.xml")
    if section_filter:
        sub = [s for s in sub if any(f in s for f in section_filter)] or sub
    for s in sub:
        _, p = locs(s)
        pages.extend(p)
    return [p for p in dict.fromkeys(pages) if not LANG_PREFIX.match(p)]


# ---------- Reddit (Arctic Shift archive) ----------

def reddit_search(query, subreddit, kind="posts", limit=10):
    """Search one subreddit through the Arctic Shift archive. Returns a list of
    {title, url, content, published, subreddit}. Arctic Shift needs a subreddit for text search."""
    import datetime
    import time
    field = "query" if kind == "posts" else "body"
    params = {"subreddit": subreddit.removeprefix("r/").strip("/"), field: query, "limit": max(1, min(int(limit), 25))}
    last = None
    for attempt in range(3):
        try:
            r = requests.get(f"{config.ARCTIC_SHIFT_API}/{kind}/search", params=params, headers=HEADERS, timeout=40)
            data = r.json()
        except Exception as e:
            last = str(e)
            time.sleep(3 * (attempt + 1))
            continue
        if data.get("error"):
            last = data["error"]
            if "imeout" in last:
                time.sleep(3 * (attempt + 1))
                continue
            break
        out = []
        for p in data.get("data") or []:
            when = p.get("created_utc")
            published = datetime.datetime.fromtimestamp(when, datetime.timezone.utc).date().isoformat() if when else None
            text = (p.get("title", "") + "\n" + (p.get("selftext") or "")) if kind == "posts" else (p.get("body") or "")
            out.append({"title": (p.get("title") or text[:90]).strip() or "Reddit comment",
                        "url": "https://www.reddit.com" + (p.get("permalink") or ""),
                        "content": text.strip(), "published": published, "subreddit": p.get("subreddit")})
        return out, None
    return [], last or "no results"
