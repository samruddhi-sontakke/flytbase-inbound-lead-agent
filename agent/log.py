"""Readable console output for the live demo.

Every message is also sent to any registered listener, so the web app can show
live progress without changing the stages.
"""
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

_start = time.time()
listeners = []  # callables: fn(kind, message, seconds)
OUT = sys.stdout  # the MCP server sets this to sys.stderr (stdout carries the MCP protocol)


def reset_clock():
    global _start
    _start = time.time()


def _emit(kind, msg):
    for fn in list(listeners):
        try:
            fn(kind, msg, round(time.time() - _start, 1))
        except Exception:
            pass


def _t():
    return f"[{time.time() - _start:5.1f}s]"


def stage(num, title):
    print(f"\n{'=' * 64}\n  STAGE {num}: {title}\n{'=' * 64}", file=OUT, flush=True)
    _emit("stage", f"{num}|{title}")


def step(msg):
    print(f"{_t()}  -> {msg}", file=OUT, flush=True)
    _emit("step", msg)


def ok(msg):
    print(f"{_t()}  OK {msg}", file=OUT, flush=True)
    _emit("ok", msg)


def warn(msg):
    print(f"{_t()}  !! {msg}", file=OUT, flush=True)
    _emit("warn", msg)
