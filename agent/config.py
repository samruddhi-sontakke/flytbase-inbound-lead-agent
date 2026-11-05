"""Settings.

The AI agent is Claude Code itself (see .claude/skills and .claude/agents), so there are no LLM API keys here.
The only secret is the MongoDB connection string, read from an environment variable or from `.env`
(git-ignored), with lines like:
    mongodb=mongodb+srv://...
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "outputs"


def _read_key_files():
    found = {}
    for name in ("keys.txt", ".env"):
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


# Company website the case-study and partner stages crawl.
VENDOR_SITE = "https://flytbase.com"
VENDOR_NAME = "FlytBase"
BDR_NAME = "Samruddhi Sontakke"  # signs the emails

# Reddit archive used for practitioner / community signals (no key needed).
ARCTIC_SHIFT_API = "https://arctic-shift.photon-reddit.com/api"

# A lead claimed by the agent is considered abandoned after this many minutes (lease lock).
LEASE_MINUTES = 45


def check_keys():
    return [] if _get("MONGODB", "MONGODB_URI", "MONGO_URI") else ["MONGODB"]
