"""Crop the raw web-app screenshots in docs/screens/ into slide-sized images (docs/screens/slides/).

    py docs/crop_screens.py

Each crop keeps the part of the page a slide talks about. Boxes are (left, top, right, bottom) in pixels of
the 1600-px-wide captures made with headless Chrome against http://127.0.0.1:8000.
"""
from pathlib import Path

from PIL import Image

SRC = Path(__file__).parent / "screens"
OUT = SRC / "slides"

CROPS = {
    "leads": (248, 0, 1600, 520),
    "inbox": (248, 0, 1600, 780),
    "system": (248, 0, 1600, 1000),
    "sqm_qualification": (270, 60, 1250, 1060),
    "sqm_research": (270, 60, 1250, 1060),
    "sqm_emails": (270, 830, 1250, 1500),
    "sqm_case_study": (270, 60, 1250, 1060),
    "sqm_partner": (270, 60, 1250, 1060),
    "sqm_handoff": (270, 60, 1250, 1060),
    "sqm_sources": (270, 60, 1250, 1060),
    "sqm_trace": (270, 60, 1250, 1000),
    "eon_handoff": (270, 60, 1250, 1060),
    "eon_qualification": (270, 60, 1250, 1060),
    "sqm_report": (0, 0, 1600, 1000),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, box in CROPS.items():
        src = SRC / f"{name}.png"
        if not src.exists():
            print(f"skip {name} (no capture yet)")
            continue
        img = Image.open(src)
        l, t, r, b = box
        img.crop((l, t, min(r, img.width), min(b, img.height))).save(OUT / f"{name}.png", optimize=True)
        print(f"{name}: {min(r, img.width) - l}x{min(b, img.height) - t}")


if __name__ == "__main__":
    main()
