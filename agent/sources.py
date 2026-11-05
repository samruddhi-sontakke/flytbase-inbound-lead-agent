"""Source registry: every fact the system uses must point to one of these.

Each web result gets an ID like S1, S2 ... The LLM may only cite these IDs,
and the verifier checks every claim against the text of the source it cites.
"""


class Sources:
    def __init__(self):
        self.items = {}      # id -> dict
        self._by_url = {}

    def add(self, url, title, content, kind="web", query=None, published=None):
        url = (url or "").strip()
        if not url:
            return None
        if url in self._by_url:
            sid = self._by_url[url]
            # keep the longest text we have for this URL
            if len(content or "") > len(self.items[sid]["content"]):
                self.items[sid]["content"] = content
            return sid
        sid = f"S{len(self.items) + 1}"
        self.items[sid] = {
            "id": sid, "url": url, "title": (title or url)[:200],
            "content": content or "", "kind": kind, "query": query,
            "published": published,
        }
        self._by_url[url] = sid
        return sid

    def get(self, sid):
        return self.items.get(sid)

    def as_prompt(self, ids=None, max_chars=1800):
        """Format sources for an LLM prompt."""
        out = []
        for sid, s in self.items.items():
            if ids is not None and sid not in ids:
                continue
            date = f" | published {s['published']}" if s.get("published") else ""
            out.append(f"[{sid}] {s['title']}{date}\nURL: {s['url']}\n{s['content'][:max_chars]}\n")
        return "\n".join(out)

    def public_list(self):
        return [{k: v for k, v in s.items() if k != "content"} for s in self.items.values()]
