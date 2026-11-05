"""The system's two 'hands': web search (Tavily) and page reading (requests + BeautifulSoup)."""
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup

from . import config, log

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) LeadResearchAgent/1.0"}
LANG_PREFIX = re.compile(r"^https?://[^/]+/(es|de|fr|ja|ko|zh|pt|ru|it|ar|nl|tr)/")

_tavily = None
_page_cache = {}


# ---------- web search ----------

def search(query, max_results=5, include_domains=None, depth="advanced", topic="general"):
    """Search the web. Returns a list of {title, url, content, published}."""
    global _tavily
    if _tavily is None:
        from tavily import TavilyClient
        _tavily = TavilyClient(api_key=config.TAVILY_KEY)
    kwargs = dict(query=query, max_results=max_results, search_depth=depth, topic=topic)
    if include_domains:
        kwargs["include_domains"] = include_domains
    try:
        res = _tavily.search(**kwargs)
    except Exception as e:
        msg = str(e)
        if "401" in msg or "Unauthorized" in msg or "invalid" in msg.lower() and "key" in msg.lower():
            raise RuntimeError("Tavily rejected the API key. Check the TAVILY= line in keys.txt.") from e
        log.warn(f"search failed for '{query}': {msg[:120]}")
        return []
    return [
        {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": r.get("content", ""),
            "published": r.get("published_date"),
        }
        for r in res.get("results", [])
    ]


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
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "noscript", "svg", "form"]):
        tag.decompose()
    main = soup.find("main") or soup.body or soup
    text = re.sub(r"\s+", " ", main.get_text(" ", strip=True))
    title = soup.title.get_text(strip=True) if soup.title else url
    _page_cache[url] = text
    _page_cache[url + "#title"] = title
    return text[:max_chars]


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
