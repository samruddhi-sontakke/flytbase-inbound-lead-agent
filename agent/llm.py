"""One small wrapper around Gemini.

Every call is logged to trace.jsonl in the run folder, so anyone can inspect
exactly what each stage asked the model and what came back.
"""
import json
import re
import time

from . import config, log

_client = None
TRACE_FILE = None  # set by run.py
_last_call = 0.0
MIN_GAP_SECONDS = 5  # free tier allows only a few requests per minute
_dead_models = set()  # models that hit their limit this run are skipped next time


def _get_client():
    global _client
    if _client is None:
        from google import genai
        _client = genai.Client(api_key=config.GEMINI_KEY)
    return _client


def _parse_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start:end + 1])
        raise


def _trace(entry):
    if TRACE_FILE:
        with open(TRACE_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def ask(prompt, system=None, json_mode=True, temperature=0.3, label="llm"):
    """Send a prompt to Gemini. Returns a dict (json_mode) or a string."""
    from google.genai import types

    last_error = None
    global _last_call
    for model in config.MODELS:
        if model in _dead_models:
            continue
        for attempt in range(3):
            gap = time.time() - _last_call
            if gap < MIN_GAP_SECONDS:
                time.sleep(MIN_GAP_SECONDS - gap)
            _last_call = time.time()
            try:
                cfg = types.GenerateContentConfig(
                    system_instruction=system,
                    temperature=temperature,
                    response_mime_type="application/json" if json_mode else "text/plain",
                )
                t0 = time.time()
                resp = _get_client().models.generate_content(
                    model=model, contents=prompt, config=cfg
                )
                text = resp.text or ""
                result = _parse_json(text) if json_mode else text
                _trace({
                    "stage": label, "model": model, "seconds": round(time.time() - t0, 1),
                    "system": system, "prompt": prompt, "response": text,
                })
                return result
            except json.JSONDecodeError as e:
                last_error = e
                log.warn(f"{label}: model returned invalid JSON, retrying")
                continue
            except Exception as e:  # network / quota / model errors
                last_error = e
                msg = str(e)
                if any(s in msg for s in ("429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE", "500", "overloaded")):
                    daily = "PerDay" in msg or "per day" in msg.lower()
                    if attempt == 2 or daily:
                        log.warn(f"{label}: {model} limit reached, switching to the next model")
                        _dead_models.add(model)
                        break
                    wait = 15 * (attempt + 1)
                    log.warn(f"{label}: Gemini busy or free-tier limit on {model}, waiting {wait}s")
                    log.warn(f"      detail: {msg[:160]}")
                    time.sleep(wait)
                    continue
                if any(s in msg for s in ("404", "NOT_FOUND", "not found", "not supported")):
                    log.warn(f"{label}: model {model} unavailable, trying next model")
                    _dead_models.add(model)
                    break
                if any(s in msg for s in ("API key", "API_KEY", "PERMISSION_DENIED", "401", "403")):
                    raise RuntimeError(
                        "Gemini rejected the API key. Check the GEMINI= line in keys.txt."
                    ) from e
                raise
    raise RuntimeError(f"Gemini call failed for {label}: {last_error}")
