"""Settings and API keys.

Keys are read (in this order) from:
  1. environment variables GEMINI_API_KEY / TAVILY_API_KEY
  2. a file called keys.txt or .env in the project folder, with lines like:
        GEMINI=your-key
        TAVILY=your-key
keys.txt and .env are listed in .gitignore, so they never get uploaded to GitHub.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "outputs"


def _read_key_files():
    found = {}
    for name in ("keys.txt", "keys.txt.txt", ".env"):
        f = ROOT / name
        if not f.exists():
            continue
        for line in f.read_text(encoding="utf-8-sig").splitlines():
            if "=" not in line or line.strip().startswith("#"):
                continue
            k, v = line.split("=", 1)
            found[k.strip().upper()] = v.strip().strip('"').strip("'")
    return found


_file_keys = _read_key_files()


def _get(*names):
    for n in names:
        if os.environ.get(n):
            return os.environ[n].strip()
        if _file_keys.get(n):
            return _file_keys[n]
    return ""


GEMINI_KEY = _get("GEMINI_API_KEY", "GEMINI", "GOOGLE_API_KEY")
TAVILY_KEY = _get("TAVILY_API_KEY", "TAVILY")

# Models are tried in order; if one is unavailable on the free tier, the next is used.
_override = _get("GEMINI_MODEL")
MODELS = ([_override] if _override else []) + [
    "gemini-flash-lite-latest",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-flash-latest",
    "gemini-2.5-flash",
]
MODELS = list(dict.fromkeys(MODELS))  # remove duplicates, keep order

# Company website the case-study and partner stages crawl.
VENDOR_SITE = "https://flytbase.com"
VENDOR_NAME = "FlytBase"
BDR_NAME = "Samruddhi Sontakke"  # signs the emails

# How much research to do (each Tavily search = 1-2 free credits).
RESEARCH_RESULTS_PER_QUERY = 5
MAX_RESEARCH_QUERIES = 12


def check_keys():
    missing = []
    if not GEMINI_KEY:
        missing.append("GEMINI")
    if not TAVILY_KEY:
        missing.append("TAVILY")
    return missing
