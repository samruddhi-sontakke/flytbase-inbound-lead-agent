"""Readable console output for the live demo."""
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

_start = time.time()


def _t():
    return f"[{time.time() - _start:5.1f}s]"


def stage(num, title):
    print(f"\n{'=' * 64}\n  STAGE {num}: {title}\n{'=' * 64}", flush=True)


def step(msg):
    print(f"{_t()}  -> {msg}", flush=True)


def ok(msg):
    print(f"{_t()}  OK {msg}", flush=True)


def warn(msg):
    print(f"{_t()}  !! {msg}", flush=True)
