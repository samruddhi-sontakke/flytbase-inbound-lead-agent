"""leaddesk: the local MCP server that gives Claude Code (the backend agent) its deterministic tools.

    py -m leaddesk_mcp.server        # stdio; registered for Claude Code in .mcp.json

Claude does the reading, judging and writing (skills in .claude/skills, one subagent per stage in .claude/agents).
Everything that must be exact lives here, in plain Python: the inbox log, the lead queue and its lock, the source
registry ([S#] IDs with the raw page text), crawling flytbase.com, Reddit search, the scoring, the fact-check
removal, the partner verification, the PDF checklist per stage, storage in MongoDB and the run-folder reports.
"""
import asyncio
import functools
import json
import sys

from mcp.server.mcpserver import MCPServer

from agent import log, store, tools
from agent.stages import s1_qualify, s4_case_study, s5_partner

log.OUT = sys.stderr  # stdout carries the MCP protocol

mcp = MCPServer(
    name="leaddesk",
    instructions=(
        "Tools for the FlytBase Inbound Lead Desk agent. Workflow: inbox_filter -> inbox_check -> inbox_verdict for "
        "unread Gmail; queue_claim; then per stage save_stage (Stage 2 goes save_draft('research') -> research_claims -> "
        "submit_fact_check); finish_lead. Every fact used in research must come from a source registered with "
        "read_page or register_source and be cited by its S# ID."
    ),
)


def tool(fn):
    """Register a blocking function as an async MCP tool. Errors come back as {'error': ...} so the agent can fix and retry."""
    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        try:
            return await asyncio.to_thread(fn, *args, **kwargs)
        except store.StageError as e:
            return {"error": str(e)}
        except Exception as e:  # never kill the server on one bad call
            return {"error": f"{type(e).__name__}: {str(e)[:500]}"}
    return mcp.tool()(wrapper)


# ---------------------------------------------------------------- heartbeat and rubric

@tool
def agent_heartbeat(kind: str = "tick", note: str = "") -> dict:
    """Record that the agent ran. kind: 'tick' (start of a cron tick) or 'inbox_sweep' (after reading Gmail)."""
    return store.record_tick(kind, note)


@tool
def get_rubric() -> dict:
    """Stage 1 rubric: the MEDDPICC elements and ICP fit factors (with weights) the qualification must rate.
    Python computes the scores from these ratings in save_stage."""
    return s1_qualify.rubric()


# ---------------------------------------------------------------- inbox intake

@tool
def inbox_filter(message_ids: list[str]) -> dict:
    """Split Gmail message IDs into ones the agent has already processed and new ones."""
    return store.inbox_known(message_ids)


@tool
def inbox_check(message_id: str, thread_id: str, sender: str, subject: str, body: str, received_at: str = "") -> dict:
    """Deterministic first pass over one unread email: contact-form markers (flytbase.com/contact, From/Title/
    Company/Subject/Context fields), buying-intent words, business domain, bulk-mail signs. Logged in inbox_log."""
    return store.inbox_check(message_id, thread_id, sender, subject, body, received_at)


@tool
def inbox_check_batch(messages: list[dict]) -> list:
    """Triage many unread emails in one call from their subject + snippet. Each item: {message_id, thread_id,
    sender, subject, body (snippet), received_at}. Returns the marker score and hint per message; then open the
    full body (get_thread) only for possible/likely leads and run inbox_check on it."""
    return store.inbox_check_batch(messages)


@tool
def inbox_verdicts(items: list[dict]) -> list:
    """Record many verdicts at once: [{message_id, is_lead, reason}]. Leads are created and queued."""
    return store.inbox_verdicts(items)


@tool
def inbox_verdict(message_id: str, is_lead: bool, reason: str) -> dict:
    """Record the agent's lead / not-a-lead decision with a reason. A lead is created and queued (deduplicated)."""
    return store.inbox_verdict(message_id, is_lead, reason)


# ---------------------------------------------------------------- queue

@tool
def queue_status() -> list:
    """Leads waiting (queued) or in progress (running), from Gmail, the web app or the command line."""
    return store.queue_status()


@tool
def queue_claim() -> dict:
    """Claim the oldest queued lead (one at a time, with a lease lock). Returns lead_id and the raw email."""
    return store.claim_next()


@tool
def get_lead(lead_id: str, stages: list[str] | None = None) -> dict:
    """Read saved stage outputs for a lead. stages: any of lead, qualification, research, emails, case_study, partner, handoff."""
    return store.get_lead(lead_id, stages)


@tool
def progress(lead_id: str, message: str, kind: str = "step", stage: int | None = None) -> dict:
    """Write a line to the lead's live log in the web app. kind: stage (pass stage=1..6), step, ok or warn."""
    return store.progress(lead_id, message, kind, stage)


# ---------------------------------------------------------------- sources

@tool
def read_page(lead_id: str, url: str, kind: str = "web", query: str = "", max_chars: int = 8000) -> dict:
    """Download a web page, store its full readable text as a source for this lead and return its S# ID plus
    the text. Use this for every page you want to cite (found with WebSearch, LinkedIn, etc.)."""
    text = tools.fetch_text(url, max_chars=60000)
    if not text:
        return {"error": f"Could not read {url} (blocked, empty or not HTML). Try another page, or register_source with text you read in the browser."}
    sid = store.add_source(lead_id, url, tools.page_title(url), text, kind=kind, query=query or None)
    return {"source_id": sid, "title": tools.page_title(url), "chars": len(text), "text": text[:max(500, min(max_chars, 20000))]}


@tool
def register_source(lead_id: str, url: str, title: str, content: str, kind: str = "web", query: str = "",
                    published: str = "") -> dict:
    """Store a source whose text you obtained another way (WebSearch result text, a LinkedIn page read in Chrome,
    a PDF). content must be text copied from the source itself, never your summary. Returns its S# ID."""
    return {"source_id": store.add_source(lead_id, url, title, content, kind=kind, query=query or None,
                                          published=published or None)}


@tool
def get_sources(lead_id: str, ids: list[str] | None = None, max_chars: int = 2500) -> list:
    """Stored sources for this lead (all, or the given S# IDs), with up to max_chars of each one's text."""
    docs = store.list_sources(lead_id, with_content=True)
    if ids:
        docs = [d for d in docs if d["id"] in ids]
    for d in docs:
        d["content"] = (d.get("content") or "")[:max_chars]
    return docs


@tool
def reddit_search(lead_id: str, query: str, subreddits: list[str], kind: str = "posts", limit: int = 8) -> dict:
    """Search Reddit (Arctic Shift archive) in the given subreddits for practitioner and community signals.
    kind: posts or comments. Every result that mentions the query is stored as a source and gets an S# ID."""
    found, errors = [], {}
    words = [w.lower() for w in query.split() if len(w) > 2]
    for sub in subreddits[:6]:
        res, err = tools.reddit_search(query, sub, kind=kind, limit=limit)
        if err:
            errors[sub] = err
        for r in res:
            if words and not any(w in r["content"].lower() for w in words):
                continue
            sid = store.add_source(lead_id, r["url"], f"Reddit r/{r['subreddit']}: {r['title']}", r["content"],
                                   kind="reddit", query=f"{query} (r/{sub})", published=r["published"])
            found.append({"source_id": sid, "subreddit": r["subreddit"], "published": r["published"],
                          "url": r["url"], "text": r["content"][:600]})
    return {"results": found, "errors": errors}


# ---------------------------------------------------------------- FlytBase site crawls

@tool
def case_study_candidates(lead_id: str, extra_urls: list[str] | None = None) -> dict:
    """Stage 4 crawl: list every case study in the flytbase.com sitemap (plus extra_urls you found with
    WebSearch site:flytbase.com), read them all, pre-score each against the Stage 1 lead (keyword overlap,
    mentions_referrer, mentions_lead_company) and store the shortlist as sources. Needs Stage 1 saved."""
    lead = store.get_lead(lead_id, ["lead"]).get("lead")
    if not lead:
        return {"error": "Save Stage 1 first: the pre-score uses the extracted lead (referrer, company, keywords)."}
    urls, from_sitemap = s4_case_study.discover(extra_urls)
    texts = tools.fetch_many(urls, max_chars=15000)
    # cut the "related stories" footer so one case study's links don't count as a mention in another
    texts = {u: t.split("Related customer stories")[0] for u, t in texts.items() if t}
    scored, shortlist, inputs = s4_case_study.prescore(lead, texts)
    for s in shortlist:
        s["source_id"] = store.add_source(lead_id, s["url"], s["title"], texts[s["url"]], kind="case_study")
    store.save_work(lead_id, "case_study", {"scored": scored, "scanned": len(urls), "from_sitemap": from_sitemap,
                                            "urls": urls, "inputs": inputs})
    store.progress(lead_id, f"Crawled {len(urls)} case studies ({from_sitemap} from the sitemap); shortlist of {len(shortlist)}", "ok")
    return {"case_studies_scanned": len(urls), "prescore_inputs": inputs,
            "shortlist": [{**s, "text": texts[s["url"]][:4000]} for s in shortlist],
            "others": [{"url": s["url"], "title": s["title"], "pre_score": s["pre_score"]} for s in scored if s not in shortlist][:25]}


@tool
def partner_directory(lead_id: str) -> dict:
    """Stage 5 crawl: read FlytBase's partner pages from its sitemap and store them as sources."""
    pages = s5_partner.partner_pages()
    texts = tools.fetch_many(pages, max_chars=20000)
    out = []
    for u, t in texts.items():
        if t:
            sid = store.add_source(lead_id, u, tools.page_title(u), t, kind="partner_directory")
            out.append({"source_id": sid, "url": u, "title": tools.page_title(u), "text": t[:12000]})
    store.progress(lead_id, f"Read {len(out)} FlytBase partner page(s)", "ok")
    return {"pages": out}


# ---------------------------------------------------------------- stage outputs

@tool
def save_draft(lead_id: str, key: str, data: dict) -> dict:
    """Save an intermediate output (e.g. key='research' for the brief before fact-checking)."""
    return store.save_draft(lead_id, key, data)


@tool
def research_claims(lead_id: str) -> list:
    """For the fact-checker: every claim in the research draft, numbered, with the stored text of the sources it cites."""
    return store.research_claims(lead_id)


@tool
def submit_fact_check(lead_id: str, verdicts: list[dict], seconds: float | None = None) -> dict:
    """Apply the fact-checker's verdicts [{n, verdict: supported|partial|unsupported, note}] to the research draft.
    Python removes unsupported claims (and any claim citing no stored source), runs the PDF checklist and saves Stage 2."""
    return store.submit_fact_check(lead_id, verdicts, seconds=seconds)


@tool
def save_stage(lead_id: str, stage: str, data: dict, agent: str = "", inputs: str = "", seconds: float | None = None) -> dict:
    """Validate and save one stage's output. stage: qualification (Stage 1, includes the extracted 'lead'),
    emails (3), case_study (4), partner (5), handoff (6). Python computes scores / verifications and the PDF
    checklist and returns them. agent = the subagent name, inputs = a one-line note of what it was given."""
    return store.save_stage(lead_id, stage, data, agent=agent, inputs=inputs, seconds=seconds)


@tool
def finish_lead(lead_id: str) -> dict:
    """All six stages saved: write sources.json, REPORT.md and REPORT.html and mark the lead done."""
    return store.finish(lead_id)


@tool
def fail_lead(lead_id: str, error: str) -> dict:
    """Mark a lead failed with the reason, so it shows in the web app and can be re-run."""
    return store.fail(lead_id, error)


if __name__ == "__main__":
    mcp.run("stdio")
