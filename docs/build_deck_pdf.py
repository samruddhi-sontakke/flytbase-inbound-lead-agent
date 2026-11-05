"""Build docs/Inbound-Lead-Desk-Walkthrough.pdf from the deck source in docs/deck/.

    py docs/build_deck_pdf.py

docs/deck/deck.json gives the slide order; docs/deck/slides/<id>.html holds one 1920x1080 <section> per slide
(the same files as the interactive deck). Images point at project/ds/shots/<name>.png, which maps to the
screenshots in docs/screens/slides/. Speaker notes (<aside>) are left out of the PDF; they are the narration in
docs/VIDEO_SCRIPT.md. Headless Chrome prints one page per slide.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

DOCS = Path(__file__).resolve().parent
DECK = DOCS / "deck"
OUT = DOCS / "Inbound-Lead-Desk-Walkthrough.pdf"
CHROME = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
          r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "google-chrome", "chromium"]

CSS = """
@page { size: 1920px 1080px; margin: 0; }
html, body { margin: 0; padding: 0; background: #ffffff; }
* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
section { width: 1920px; height: 1080px; position: relative; overflow: hidden; page-break-after: always; break-after: page; }
section:last-of-type { page-break-after: auto; break-after: auto; }
h1, h2, h3, p, ul, ol, table { margin: 0; }
aside { display: none; }
a { text-decoration: underline; }
table { width: 100%; border-collapse: collapse; }
th { font-weight: 600; padding: 0 16px 16px 0; border-bottom: 2px solid #141414; }
td { padding: 18px 16px 18px 0; border-bottom: 1px solid #E4E6E9; vertical-align: top; line-height: 1.35; }
"""


def chrome():
    for c in CHROME:
        if Path(c).exists() or shutil.which(c):
            return c
    raise SystemExit("Chrome or Edge not found")


def main():
    deck = json.loads((DECK / "deck.json").read_text(encoding="utf-8"))
    fonts = "".join(f'<link rel="stylesheet" href="{f["href"]}">' for f in deck.get("faces", {}).values() if f.get("href"))
    shots = (DOCS / "screens" / "slides").as_uri()
    slides = []
    for sid in deck["order"]:
        html = (DECK / "slides" / f"{sid}.html").read_text(encoding="utf-8")
        html = re.sub(r'src="project/ds/shots/', f'src="{shots}/', html)
        slides.append(html)
    page = (f'<!doctype html><html><head><meta charset="utf-8"><title>{deck["title"]}</title>{fonts}'
            f"<style>{CSS}</style></head><body>{''.join(slides)}</body></html>")
    tmp = DOCS / "_deck_print.html"
    tmp.write_text(page, encoding="utf-8")
    try:
        subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--virtual-time-budget=15000", f"--print-to-pdf={OUT}", tmp.as_uri()],
                       check=True, capture_output=True)
    finally:
        tmp.unlink(missing_ok=True)
    print(f"wrote {OUT} ({len(slides)} slides)")


if __name__ == "__main__":
    main()
