/* Inbound Lead Desk - plain JavaScript, no build step. Talks to app/server.py. */
(function () {
  'use strict';

  // ------------------------------------------------------------ helpers
  const $ = (s, el) => (el || document).querySelector(s);
  const $$ = (s, el) => Array.from((el || document).querySelectorAll(s));
  const esc = (v) => String(v == null ? '' : v).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const arr = (v) => (Array.isArray(v) ? v : v ? [v] : []);
  const has = (v) => v != null && v !== '' && !(Array.isArray(v) && !v.length);
  const icon = {
    caret: '<svg class="ico" width="14" height="14" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>',
    check: '<svg class="ico" width="12" height="12" viewBox="0 0 24 24" aria-hidden="true" style="stroke-width:3"><path d="M5 12l5 5L20 7"/></svg>',
    x: '<svg class="ico" width="12" height="12" viewBox="0 0 24 24" aria-hidden="true" style="stroke-width:3"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    ext: '<svg class="ico" width="13" height="13" viewBox="0 0 24 24" aria-hidden="true"><path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/></svg>',
    copy: '<svg class="ico" width="13" height="13" viewBox="0 0 24 24" aria-hidden="true"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a1 1 0 0 1 1-1h10"/></svg>',
    redo: '<svg class="ico" width="13" height="13" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 11a8 8 0 1 0-2.3 5.7M20 5v6h-6"/></svg>',
    plus: '<svg class="ico" width="13" height="13" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>',
  };

  async function api(path, opts) {
    const o = Object.assign({ headers: { 'Content-Type': 'application/json' } }, opts || {});
    if (o.body && typeof o.body !== 'string') o.body = JSON.stringify(o.body);
    const r = await fetch(path, o);
    if (!r.ok) {
      let msg = r.status + ' ' + r.statusText;
      try { const j = await r.json(); if (j.detail) msg = typeof j.detail === 'string' ? j.detail : JSON.stringify(j.detail); } catch (e) { /* keep status text */ }
      throw new Error(msg);
    }
    return r.json();
  }

  function toast(msg, bad) {
    const el = $('#toast');
    el.innerHTML = `<div class="toast${bad ? ' bad' : ''}" role="status"><span class="dot"></span>${esc(msg)}</div>`;
    clearTimeout(toast.t);
    toast.t = setTimeout(() => { el.innerHTML = ''; }, bad ? 5000 : 2600);
  }

  async function copyText(text, label) {
    try { await navigator.clipboard.writeText(text); toast(label || 'Copied'); }
    catch (e) { toast('Copy failed: your browser blocked the clipboard', true); }
  }

  function when(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    const s = (Date.now() - d.getTime()) / 1000;
    if (s < 60) return 'just now';
    if (s < 3600) return Math.floor(s / 60) + 'm ago';
    if (s < 86400) return Math.floor(s / 3600) + 'h ago';
    if (s < 86400 * 7) return Math.floor(s / 86400) + 'd ago';
    return d.toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' });
  }
  const stamp = (iso) => (iso ? new Date(iso).toLocaleString(undefined, { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : '');
  const initials = (name) => (name || '?').split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0]).join('').toUpperCase();
  const human = (k) => String(k || '').replace(/_/g, ' ').replace(/^./, (c) => c.toUpperCase());

  // ------------------------------------------------------------ vocabulary
  const STAGES = [ // run order
    { key: 'lead', n: '00', name: 'Intake', does: 'reads the email into structured fields' },
    { key: 'qualification', n: '01', name: 'Qualify', does: 'MEDDPICC, scored in code' },
    { key: 'research', n: '02', name: 'Research', does: 'cited, then fact-checked' },
    { key: 'case_study', n: '04', name: 'Case study', does: 'matched from the live flytbase.com sitemap' },
    { key: 'partner', n: '05', name: 'Partner / GTM', does: 'direct or co-sell, partner names verified' },
    { key: 'emails', n: '03', name: 'Reply sequence', does: 'four emails, each aimed at a gap' },
    { key: 'handoff', n: '06', name: 'AE handoff', does: 'next step with an owner' },
  ];
  const TABS = [
    { id: 'handoff', label: 'AE handoff', n: '06', needs: 'handoff' },
    { id: 'qualification', label: 'Qualification', n: '01', needs: 'qualification' },
    { id: 'research', label: 'Research', n: '02', needs: 'research' },
    { id: 'emails', label: 'Emails', n: '03', needs: 'emails' },
    { id: 'case_study', label: 'Case study', n: '04', needs: 'case_study' },
    { id: 'partner', label: 'Partner', n: '05', needs: 'partner' },
    { id: 'sources', label: 'Sources', needs: 'done' },
    { id: 'trace', label: 'AI trace', needs: 'run' },
    { id: 'notes', label: 'Notes' },
    { id: 'input', label: 'Original email' },
  ];
  const CRM = { new: 'New', working: 'Working', meeting_booked: 'Meeting booked', handed_off: 'Handed to AE', nurture: 'Nurture', disqualified: 'Disqualified' };
  const RUN = { queued: 'Queued', running: 'Running', failed: 'Failed', done: 'Done' };
  const stageName = (k) => (STAGES.find((s) => s.key === k) || {}).name || k;

  function tierPill(s) {
    const t = s && s.tier;
    const label = t === 'P1' ? 'P1 hot' : t === 'P2' ? 'P2 warm' : t === 'P3' ? 'P3 nurture' : 'unscored';
    return `<span class="pill p-${t || 'none'}" title="${esc(s && s.tier_label)}">${label}</span>`;
  }
  function statusPill(d) {
    if (d.status && d.status !== 'done') {
      const extra = d.status === 'running' && d.stage ? ' · ' + stageName(d.stage).toLowerCase() : '';
      return `<span class="pill s-${d.status}">${d.status === 'running' ? '<span class="dot busy live"></span>' : ''}${RUN[d.status]}${esc(extra)}</span>`;
    }
    const c = (d.crm && d.crm.status) || 'new';
    return `<span class="pill s-${c}">${CRM[c] || c}</span>`;
  }

  // ------------------------------------------------------------ state
  const S = {
    leads: [], health: null, filter: 'all', crm: 'any', query: '', openRow: null,
    lead: null, tab: null, openM: null, openTrace: null, trace: null, srcQuery: '', after: 0,
    poll: null, listPoll: null, paletteSel: 0,
  };

  // ------------------------------------------------------------ citations
  function srcMap() {
    const m = {};
    arr(S.lead && S.lead.sources).forEach((s) => { m[s.id] = s; });
    return m;
  }
  function chip(id, m) {
    const s = m[id];
    return s ? `<a class="cite" href="${esc(s.url)}" target="_blank" rel="noopener noreferrer" title="${esc(s.title)}">${esc(id)}</a>` : `<span class="cite">${esc(id)}</span>`;
  }
  function cite(text, m) {
    m = m || srcMap();
    return esc(text).replace(/\[(S\d+(?:\s*,\s*S\d+)*)\]/g, (_, ids) => ids.split(/\s*,\s*/).map((i) => chip(i, m)).join(''));
  }
  function idChips(ids, text, m) {
    m = m || srcMap();
    return arr(ids).filter((i) => !String(text || '').includes(i)).map((i) => chip(i, m)).join('');
  }

  // ------------------------------------------------------------ shell
  function navCounts() {
    const live = S.leads.filter((l) => l.status === 'queued' || l.status === 'running').length;
    return { leads: S.leads.length ? String(S.leads.length) : '', new: live ? live + ' live' : '' };
  }
  function renderNav(route) {
    const c = navCounts();
    const items = [
      { href: '#/leads', label: 'Leads', dot: '#141414', count: c.leads, on: route === 'leads' || route === 'lead' },
      { href: '#/new', label: 'New lead', dot: '#c4501f', count: c.new, on: route === 'new' },
      { href: '#/activity', label: 'Activity', dot: '#2d55a6', count: '', on: route === 'activity' },
      { href: '#/system', label: 'System', dot: '#8b8f95', count: '', on: route === 'system' },
    ];
    $('#nav').innerHTML = items.map((i) => `<a class="nav ease${i.on ? ' is-active' : ''}" href="${i.href}"${i.on ? ' aria-current="page"' : ''}>
      <span class="sq" style="background:${i.dot}"></span><span>${i.label}</span><span class="count">${esc(i.count)}</span></a>`).join('');
  }
  function renderWorker() {
    const h = S.health;
    const dot = $('#workerDot'), title = $('#workerTitle'), note = $('#workerNote');
    if (!h) { dot.className = 'dot bad'; title.textContent = 'Server unreachable'; note.textContent = 'start: py -m app.server'; return; }
    if (!h.mongo || (h.missing_keys && h.missing_keys.length)) {
      dot.className = 'dot bad'; title.textContent = 'Setup needed';
      note.textContent = !h.mongo ? 'mongodb not connected' : 'missing ' + h.missing_keys.join(', ').toLowerCase();
      return;
    }
    if (h.running) {
      dot.className = 'dot busy live'; title.textContent = 'Agent running';
      note.textContent = h.queued ? h.queued + ' more queued' : 'one lead at a time';
    } else {
      dot.className = 'dot ok live'; title.textContent = 'Agent ready';
      note.textContent = 'mongodb · ' + (h.database || 'connected');
    }
  }
  async function refreshHealth() {
    try { S.health = await api('/api/health'); } catch (e) { S.health = null; }
    renderWorker();
  }
  async function refreshLeads() {
    try { S.leads = await api('/api/leads'); } catch (e) { /* keep last list */ }
    renderNav(route().name);
  }

  function route() {
    const parts = (location.hash || '#/leads').replace(/^#\/?/, '').split('/');
    return { name: parts[0] || 'leads', id: parts[1], tab: parts[2] };
  }

  function stopPolls() {
    clearInterval(S.poll); S.poll = null;
    clearInterval(S.listPoll); S.listPoll = null;
  }

  async function render() {
    const r = route();
    stopPolls();
    renderNav(r.name);
    const main = $('#main');
    if (r.name === 'lead' && r.id) return showLead(r.id, r.tab);
    S.lead = null;
    if (r.name === 'new') return showNew(main);
    if (r.name === 'activity') return showActivity(main);
    if (r.name === 'system') return showSystem(main);
    return showLeads(main);
  }

  // ------------------------------------------------------------ leads list
  function filtered() {
    const q = S.query.trim().toLowerCase();
    return S.leads.filter((l) => {
      const s = l.summary || {};
      const live = l.status === 'queued' || l.status === 'running';
      if (S.filter === 'live' && !live) return false;
      if (S.filter === 'failed' && l.status !== 'failed') return false;
      if (/^P\d$/.test(S.filter) && s.tier !== S.filter) return false;
      if (S.crm !== 'any' && ((l.crm && l.crm.status) || 'new') !== S.crm) return false;
      if (q && ![s.name, s.company, s.company_full, s.subject, s.email, s.title].join(' ').toLowerCase().includes(q)) return false;
      return true;
    });
  }

  function showLeads(main) {
    main.innerHTML = `<div class="view col gap16" style="gap:24px">
      <div class="phead">
        <div class="col gap4"><h1 class="title">Inbound leads</h1>
          <span class="muted">Every email that came in through the contact form, qualified by the agent.</span></div>
        <a class="btn btn-accent ease" href="#/new">${icon.plus}New lead</a>
      </div>
      <div class="stats" id="leadStats"></div>
      <div class="row wrap between gap12">
        <div class="row wrap gap8">
          <div class="segs" role="group" aria-label="Filter by priority" id="leadSegs"></div>
          <label><span class="sr">Lead status</span>
            <select class="field" id="crmSel">${['any'].concat(Object.keys(CRM)).map((k) => `<option value="${k}">${k === 'any' ? 'Any status' : CRM[k]}</option>`).join('')}</select></label>
          <label style="flex:0 1 240px"><span class="sr">Search leads</span>
            <input class="field ease" id="leadQ" type="search" placeholder="Search name, company, subject" style="height:40px"></label>
        </div>
        <span class="mono sm muted" id="leadCount"></span>
      </div>
      <div class="tbl"><div class="tbl-in">
        <div class="thead"><span></span><span>lead</span><span>priority</span><span>gtm motion</span><span>status</span><span>received</span></div>
        <div id="leadRows"></div>
      </div></div>
    </div>`;
    $('#crmSel').value = S.crm;
    $('#leadQ').value = S.query;
    $('#leadQ').addEventListener('input', (e) => { S.query = e.target.value; S.openRow = null; renderLeadTable(); });
    $('#crmSel').addEventListener('change', (e) => { S.crm = e.target.value; S.openRow = null; renderLeadTable(); });
    renderLeadTable();
    refreshLeads().then(renderLeadTable);
    S.listPoll = setInterval(async () => {
      if (S.leads.some((l) => l.status === 'queued' || l.status === 'running')) { await refreshLeads(); renderLeadTable(); }
    }, 4000);
  }

  function renderLeadTable() {
    if (!$('#leadRows')) return;
    const L = S.leads;
    const done = L.filter((l) => l.status === 'done' && l.meta && l.meta.seconds);
    const avg = done.length ? Math.round(done.reduce((a, l) => a + l.meta.seconds, 0) / done.length) + ' s' : '--';
    const live = L.filter((l) => l.status === 'queued' || l.status === 'running').length;
    const p1 = L.filter((l) => (l.summary || {}).tier === 'P1').length;
    const handed = L.filter((l) => l.crm && (l.crm.status === 'handed_off' || l.crm.status === 'meeting_booked')).length;
    $('#leadStats').innerHTML = [
      [L.length, 'leads'], [p1, 'P1 hot'], [live || '0', 'in progress'], [handed + ' / ' + avg, 'handed off / avg run']
    ].map(([v, l]) => `<div class="stat"><span class="v">${esc(v)}</span><span class="l">${esc(l)}</span></div>`).join('');

    const count = (f) => L.filter((l) => (f === 'all') || (f === 'live' ? (l.status === 'queued' || l.status === 'running') : f === 'failed' ? l.status === 'failed' : (l.summary || {}).tier === f)).length;
    const segs = [['all', 'All'], ['P1', 'P1'], ['P2', 'P2'], ['P3', 'P3'], ['live', 'In progress'], ['failed', 'Failed']];
    $('#leadSegs').innerHTML = segs.filter(([k]) => k === 'all' || k === 'P1' || count(k)).map(([k, label]) =>
      `<button type="button" class="seg ease${S.filter === k ? ' is-active' : ''}" aria-pressed="${S.filter === k}" data-seg="${k}">${label}<span class="n">${count(k)}</span></button>`).join('');
    $$('#leadSegs [data-seg]').forEach((b) => b.addEventListener('click', () => { S.filter = b.dataset.seg; S.openRow = null; renderLeadTable(); }));

    const rows = filtered();
    $('#leadCount').textContent = rows.length + ' of ' + L.length;
    if (!L.length) {
      $('#leadRows').innerHTML = `<div class="empty"><span class="strong">No leads yet</span><span class="muted">Paste an inbound email to run the agent on it.</span><a class="btn btn-accent ease" href="#/new" style="margin-top:8px">New lead</a></div>`;
      return;
    }
    if (!rows.length) {
      $('#leadRows').innerHTML = `<div class="empty"><span class="strong">Nothing matches${S.query ? ' “' + esc(S.query) + '”' : ''}</span><span class="muted">Try a name or company, or clear the filters.</span><button type="button" class="btn ease" id="clearF" style="margin-top:8px">Clear filters</button></div>`;
      $('#clearF').addEventListener('click', () => { S.query = ''; S.filter = 'all'; S.crm = 'any'; $('#leadQ').value = ''; $('#crmSel').value = 'any'; renderLeadTable(); });
      return;
    }
    $('#leadRows').innerHTML = rows.map((l) => {
      const s = l.summary || {};
      const open = S.openRow === l._id;
      const sub = [s.title, s.company].filter(Boolean).join(' · ');
      return `<div>
        <button type="button" class="erow ease" aria-expanded="${open}" data-row="${esc(l._id)}">
          <span class="caret${open ? ' is-open' : ''}">${icon.caret}</span>
          <span class="cell2"><span class="a">${esc(s.name || 'Unknown sender')}</span><span class="b">${esc(sub || s.subject || '')}</span></span>
          <span class="row gap8">${tierPill(s)}${has(s.priority) ? `<span class="mono sm ink2">${esc(s.priority)}</span>` : ''}</span>
          <span class="trunc ink2" title="${esc(s.motion)}">${esc(s.motion || (l.status === 'done' ? '--' : ''))}</span>
          <span>${statusPill(l)}</span>
          <span class="mono sm ink2" title="${esc(stamp(l.created_at))}">${esc(when(l.created_at))}</span>
        </button>
        ${open ? `<div class="rowopen open">
          ${s.subject ? `<span class="strong">${esc(s.subject)}</span>` : ''}
          ${s.one_line ? `<span class="ink2">${esc(s.one_line)}</span>` : l.status === 'failed' ? `<span style="color:var(--red)">${esc(l.error || 'The run stopped.')}</span>` : `<span class="muted">The agent is still working on this lead.</span>`}
          <span class="mono sm muted">${esc([s.referral ? 'referred by ' + s.referral : '', s.partners && s.partners.length ? 'partner: ' + s.partners.join(', ') : '', s.icp != null ? 'icp ' + s.icp : '', s.completeness != null ? 'meddpicc ' + s.completeness + '%' : ''].filter(Boolean).join(' · '))}</span>
          <div class="row gap8 wrap"><a class="btn btn-accent ease" href="#/lead/${esc(l._id)}">Open lead</a>
          ${l.status === 'done' ? `<a class="btn ease" href="/api/leads/${esc(l._id)}/report" target="_blank" rel="noopener">${icon.ext}Report</a>` : ''}</div>
        </div>` : ''}
      </div>`;
    }).join('');
    $$('#leadRows [data-row]').forEach((b) => b.addEventListener('click', () => { S.openRow = S.openRow === b.dataset.row ? null : b.dataset.row; renderLeadTable(); }));
  }

  // ------------------------------------------------------------ new lead
  function showNew(main) {
    const blocked = S.health && (!S.health.mongo || (S.health.missing_keys || []).length);
    main.innerHTML = `<div class="view split">
      <div class="wide">
        <div class="col gap4"><h1 class="title">New inbound lead</h1>
          <span class="muted">Paste the email exactly as it arrived. The agent reads it, then runs all six stages.</span></div>
        <form class="card pad col gap16" id="newForm" novalidate>
          <label class="col gap8"><span class="s13 strong">Inbound email</span>
            <textarea class="field ease" id="emailText" rows="12" placeholder="From: Name (email)&#10;Title: …&#10;Company: …&#10;Subject: …&#10;&#10;Message…"></textarea>
            <span class="sm" id="emailErr" style="color:var(--red)" hidden>Paste the full email: at least a few lines.</span></label>
          ${blocked ? `<span class="sm" style="color:var(--red)">The agent can’t run yet: ${!S.health.mongo ? 'MongoDB isn’t connected' : 'missing ' + esc(S.health.missing_keys.join(', ')) + ' in .env'}.</span>` : ''}
          <div class="row wrap gap8">
            <button type="submit" class="btn btn-accent ease" id="runBtn" style="min-width:128px;height:40px"${blocked ? ' disabled' : ''}><span>Run agent</span></button>
            <button type="button" class="btn ease" id="sampleBtn" style="height:40px">Load sample (SQM)</button>
            <span class="sm muted">About 2–5 minutes on the free tiers. You can leave this page.</span>
          </div>
        </form>
      </div>
      <div class="narrow">
        <div class="card pad col gap12">
          <span class="sh">what happens next</span>
          <ol class="steps">${STAGES.map((s) => `<li class="stepi" style="grid-template-columns:32px minmax(0,1fr)"><span class="sn">${s.n}</span><span><span class="strong">${s.name}</span> <span class="muted">· ${s.does}</span></span></li>`).join('')}</ol>
        </div>
        <div class="card pad16 col gap4" style="background:var(--side)"><span class="strong s13">Nothing is sent</span><span class="sm muted">The agent drafts emails for you to review. It never emails the lead.</span></div>
      </div>
    </div>`;
    const ta = $('#emailText');
    ta.focus();
    ta.addEventListener('input', () => { ta.classList.remove('has-error'); $('#emailErr').hidden = true; });
    $('#sampleBtn').addEventListener('click', async () => {
      try { ta.value = (await api('/api/sample')).email_text; ta.focus(); } catch (e) { toast(e.message, true); }
    });
    $('#newForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = $('#runBtn');
      if (btn.disabled) return;
      if (ta.value.trim().length < 40) { ta.classList.add('has-error'); $('#emailErr').hidden = false; ta.focus(); return; }
      btn.disabled = true; btn.innerHTML = '<span class="spin"></span><span>Starting</span>';
      try {
        const r = await api('/api/leads', { method: 'POST', body: { email_text: ta.value } });
        toast(r.position > 1 ? 'Lead queued behind ' + (r.position - 1) + ' other' : 'Agent started');
        await refreshLeads();
        location.hash = '#/lead/' + r.id;
      } catch (err) {
        toast(err.message, true);
        btn.disabled = false; btn.innerHTML = '<span>Run agent</span>';
      }
    });
  }

  // ------------------------------------------------------------ lead detail
  async function showLead(id, tab) {
    const main = $('#main');
    if (!S.lead || S.lead._id !== id) {
      main.innerHTML = `<div class="row gap8 muted"><span class="spin dark"></span>Loading lead…</div>`;
      try { S.lead = await api('/api/leads/' + encodeURIComponent(id)); }
      catch (e) { main.innerHTML = `<div class="empty"><span class="strong">Couldn’t open this lead</span><span class="muted">${esc(e.message)}</span><a class="btn ease" href="#/leads">Back to leads</a></div>`; return; }
      S.trace = null; S.openM = null; S.openTrace = null; S.after = (S.lead.events || []).length; S.srcQuery = '';
    }
    S.tab = pickTab(tab);
    main.innerHTML = `<div class="view col" style="gap:24px">
      <a class="crumb" href="#/leads">← leads</a>
      <div id="lHead"></div>
      <div class="rule"></div>
      <div id="lProg"></div>
      <div class="split">
        <div class="wide" style="gap:16px"><div class="tabs" role="tablist" id="lTabs"></div><div id="lBody"></div></div>
        <div class="narrow" id="lSide"></div>
      </div>
    </div>`;
    paintLead(true);
    if (isLive()) startLeadPoll();
  }

  const isLive = () => S.lead && (S.lead.status === 'queued' || S.lead.status === 'running');
  const doneSet = () => new Set(S.lead.stages_done || []);
  function tabEnabled(t) {
    if (!t.needs) return true;
    if (t.needs === 'done') return S.lead.status === 'done';
    if (t.needs === 'run') return !!S.lead.run_dir;
    return doneSet().has(t.needs) && S.lead.result && S.lead.result[t.needs];
  }
  function pickTab(want) {
    const t = TABS.find((x) => x.id === want);
    if (t && tabEnabled(t)) return t.id;
    if (S.lead.status === 'done' && S.lead.result && S.lead.result.handoff) return 'handoff';
    const last = STAGES.slice().reverse().find((s) => doneSet().has(s.key) && TABS.find((x) => x.id === s.key));
    return last ? last.key : 'input';
  }

  function paintLead(all) {
    paintHead(); paintProgress(); paintTabs(); paintSide();
    if (all || S.tab !== 'notes') paintBody();
  }

  function paintHead() {
    const d = S.lead, s = d.summary || {};
    const em = d.result && d.result.emails && arr(d.result.emails.emails)[0];
    $('#lHead').innerHTML = `<div class="phead">
      <div class="row gap16" style="min-width:0">
        <div class="avatar">${esc(initials(s.name))}</div>
        <div class="col gap4" style="min-width:0">
          <h1 class="title">${esc(s.name || 'Unknown sender')}</h1>
          <div class="chips">${[s.title, s.company, s.country, s.sub_industry || s.industry].filter(Boolean).map((c) => `<span class="chip">${esc(String(c).toLowerCase())}</span>`).join('')}
            ${tierPill(s)}</div>
        </div>
      </div>
      <div class="row wrap gap8">
        <label><span class="sr">Lead status</span><select class="field" id="crmStatus"${d.status !== 'done' ? ' disabled' : ''}>
          ${Object.keys(CRM).map((k) => `<option value="${k}"${((d.crm && d.crm.status) || 'new') === k ? ' selected' : ''}>${CRM[k]}</option>`).join('')}</select></label>
        ${em ? `<button type="button" class="btn ease" id="copyE1">${icon.copy}Copy email 1</button>` : ''}
        ${d.status === 'done' ? `<a class="btn ease" href="/api/leads/${esc(d._id)}/report" target="_blank" rel="noopener">${icon.ext}Report</a>` : ''}
        ${!isLive() ? `<button type="button" class="btn ease" id="rerunBtn" title="Run the agent again on the same email">${icon.redo}Re-run</button>` : ''}
      </div>
    </div>`;
    const sel = $('#crmStatus');
    sel.addEventListener('change', async () => {
      try { await api('/api/leads/' + d._id, { method: 'PATCH', body: { status: sel.value } }); d.crm = Object.assign({}, d.crm, { status: sel.value }); toast('Status: ' + CRM[sel.value]); refreshLeads(); }
      catch (e) { toast(e.message, true); }
    });
    if (em) $('#copyE1').addEventListener('click', () => copyText('Subject: ' + em.subject + '\n\n' + em.body, 'Email 1 copied'));
    const rb = $('#rerunBtn');
    if (rb) rb.addEventListener('click', async () => {
      rb.disabled = true;
      try { const r = await api('/api/leads/' + d._id + '/rerun', { method: 'POST' }); toast('Re-run started as a new lead'); await refreshLeads(); location.hash = '#/lead/' + r.id; }
      catch (e) { toast(e.message, true); rb.disabled = false; }
    });
  }

  function paintProgress() {
    const d = S.lead, el = $('#lProg');
    if (d.status === 'done') { el.innerHTML = ''; el.style.display = 'none'; return; }
    el.style.display = '';
    const done = doneSet();
    const pct = Math.round((done.size / STAGES.length) * 100);
    const failedAt = d.status === 'failed' ? (STAGES.find((s) => !done.has(s.key)) || {}).key : null;
    const head = d.status === 'queued' ? 'queued · waiting for the agent' : d.status === 'running' ? 'running · ' + (d.stage ? stageName(d.stage).toLowerCase() : 'starting') : 'stopped';
    el.innerHTML = `<div class="card">
      <div class="cardhead"><span class="row gap8">${d.status === 'running' ? '<span class="dot busy live"></span>' : ''}${esc(head)}</span><span>${done.size} / ${STAGES.length} stages</span></div>
      <div style="padding:0 16px"><div class="bar" style="margin-top:12px"><span style="width:${pct}%"></span></div></div>
      ${d.status === 'failed' ? `<div style="margin:16px 16px 0;padding:12px;border-radius:6px;background:var(--red-soft);color:var(--red);font-size:13px">${esc(d.error || 'The run stopped.')}</div>` : ''}
      <div class="split" style="padding:8px 16px 16px;gap:16px">
        <ol class="steps wide" style="gap:0">${STAGES.map((s) => {
          const st = done.has(s.key) ? 'done' : s.key === failedAt ? 'fail' : d.stage === s.key && d.status === 'running' ? 'active' : '';
          return `<li class="stepi"><span class="sico ${st}">${st === 'done' ? icon.check : st === 'fail' ? icon.x : ''}</span><span class="sn">${s.n}</span>
            <span><span class="strong">${s.name}</span> <span class="muted">· ${s.does}</span></span>
            ${done.has(s.key) && TABS.find((t) => t.id === s.key) ? `<button type="button" class="btn btn-sm ease" data-goto="${s.key}">View</button>` : '<span></span>'}</li>`;
        }).join('')}</ol>
        <div class="narrow card" style="align-self:stretch;min-width:0">
          <div class="cardhead"><span>live log</span><span>${(d.events || []).length} lines</span></div>
          <ol class="loglist" id="logList">${logLines(d.events || [])}</ol>
        </div>
      </div>
    </div>`;
    $$('[data-goto]', el).forEach((b) => b.addEventListener('click', () => setTab(b.dataset.goto)));
    const ll = $('#logList'); if (ll) ll.scrollTop = ll.scrollHeight;
  }
  function logLines(ev) {
    if (!ev.length) return '<li><span></span><span></span><span class="muted">Waiting for the first stage…</span></li>';
    return ev.map((e) => {
      if (e.kind === 'stage') { const [n, t] = String(e.msg).split('|'); return `<li class="stage"><span class="t">${e.t != null ? esc(e.t) + 's' : ''}</span><span class="k-stage">#</span><span>Stage ${esc(n)} · ${esc(t)}</span></li>`; }
      const sym = e.kind === 'ok' ? '✓' : e.kind === 'warn' ? '!' : '→';
      return `<li><span class="t">${e.t != null ? esc(e.t) + 's' : ''}</span><span class="k-${esc(e.kind)}">${sym}</span><span class="${e.kind === 'step' ? 'muted' : ''}">${esc(e.msg)}</span></li>`;
    }).join('');
  }

  function paintTabs() {
    const el = $('#lTabs');
    el.innerHTML = TABS.map((t) => {
      const on = tabEnabled(t);
      return `<button type="button" role="tab" class="tab ease${S.tab === t.id ? ' is-active' : ''}" aria-selected="${S.tab === t.id}" data-tab="${t.id}"${on ? '' : ' disabled title="Ready when this stage finishes"'}>${t.n ? `<span class="tn">${t.n}</span>` : ''}${t.label}</button>`;
    }).join('') + '<span class="ind" id="tabInd"></span>';
    $$('[data-tab]', el).forEach((b) => b.addEventListener('click', () => setTab(b.dataset.tab)));
    requestAnimationFrame(moveInd);
  }
  function moveInd() {
    const a = $('#lTabs .tab.is-active'), ind = $('#tabInd');
    if (!a || !ind) return;
    ind.style.width = a.offsetWidth + 'px';
    ind.style.transform = `translateX(${a.offsetLeft}px)`;
  }
  function setTab(id) {
    S.tab = id;
    history.replaceState(null, '', '#/lead/' + S.lead._id + '/' + id);
    $$('#lTabs .tab').forEach((b) => { const on = b.dataset.tab === id; b.classList.toggle('is-active', on); b.setAttribute('aria-selected', on); });
    moveInd();
    paintBody();
  }

  function paintSide() {
    const d = S.lead, s = d.summary || {}, m = d.meta || {};
    const facts = [
      ['Email', s.email ? `<a href="mailto:${esc(s.email)}">${esc(s.email)}</a>` : ''],
      ['Title', esc(s.title)], ['Division', esc(s.division)], ['Seniority', esc(s.seniority)],
      ['Company', esc(s.company_full || s.company)], ['Region', esc([s.country, s.region].filter(Boolean).join(' · '))],
      ['Industry', esc([s.industry, s.sub_industry].filter(Boolean).join(' · '))],
      ['Referral', esc(s.referral)],
      ['Priority', has(s.priority) ? `<span class="mono">${esc(s.priority)}</span> <span class="muted sm">icp ${esc(s.icp)} · meddpicc ${esc(s.completeness)}%</span>` : ''],
      ['Received', esc(stamp(d.created_at))],
      ['Run', d.status === 'done' ? `<span class="mono sm">${[m.seconds != null ? m.seconds + ' s' : '', m.llm_calls != null ? m.llm_calls + ' AI calls' : '', arr(d.sources).length + ' sources'].filter(Boolean).join(' · ')}</span>` : esc(RUN[d.status])],
    ].filter(([, v]) => v);
    $('#lSide').innerHTML = `<div class="facts">${facts.map(([k, v]) => `<span class="k">${k}</span><span class="v">${v}</span>`).join('')}
      <span class="k"><label for="ownerIn">Owner</label></span><span class="v"><input class="field ease" id="ownerIn" style="height:32px;font-size:13px" placeholder="Assign an AE or BDR" value="${esc((d.crm && d.crm.owner) || '')}"></span></div>
      ${d.imported ? '<span class="sm muted">Imported from an earlier command-line run.</span>' : ''}`;
    const own = $('#ownerIn');
    own.addEventListener('change', async () => {
      try { await api('/api/leads/' + d._id, { method: 'PATCH', body: { owner: own.value } }); d.crm = Object.assign({}, d.crm, { owner: own.value }); toast(own.value ? 'Owner: ' + own.value : 'Owner cleared'); }
      catch (e) { toast(e.message, true); }
    });
  }

  function startLeadPoll() {
    clearInterval(S.poll);
    S.poll = setInterval(async () => {
      if (!S.lead) return;
      const id = S.lead._id;
      let p;
      try { p = await api(`/api/leads/${id}/progress?after=${S.after}`); } catch (e) { return; }
      if (!S.lead || S.lead._id !== id) return;
      const before = (S.lead.stages_done || []).length;
      S.lead.events = (S.lead.events || []).concat(p.events);
      S.after = p.total;
      const statusChanged = p.status !== S.lead.status;
      Object.assign(S.lead, { status: p.status, stage: p.stage, stages_done: p.stages_done, error: p.error, summary: p.summary || S.lead.summary });
      if (p.stages_done.length !== before || statusChanged) {
        try { const full = await api('/api/leads/' + id); full.events = S.lead.events; S.lead = full; S.after = full.events.length; } catch (e) { /* next tick */ }
        if (S.lead.status === 'done') { clearInterval(S.poll); toast('Lead qualified: ' + ((S.lead.summary || {}).tier || 'scored')); S.tab = 'handoff'; history.replaceState(null, '', '#/lead/' + id + '/handoff'); refreshLeads(); }
        if (S.lead.status === 'failed') { clearInterval(S.poll); toast('Run stopped: ' + (S.lead.error || 'see the log'), true); refreshLeads(); }
        if (S.tab === 'input' || !tabEnabled(TABS.find((t) => t.id === S.tab) || {})) S.tab = pickTab();
        paintLead(S.tab !== 'notes');
      } else if (p.events.length || statusChanged) {
        paintProgress();
      }
    }, 2500);
  }

  // ------------------------------------------------------------ stage views
  function paintBody() {
    const el = $('#lBody'), r = S.lead.result || {};
    const views = { handoff: vHandoff, qualification: vQual, research: vResearch, emails: vEmails, case_study: vCase, partner: vPartner, sources: vSources, trace: vTrace, notes: vNotes, input: vInput };
    try { el.innerHTML = `<div class="view">${(views[S.tab] || vInput)(r)}</div>`; }
    catch (e) { console.error(e); el.innerHTML = `<div class="card pad"><span class="strong">This stage’s output has an unexpected shape.</span><pre class="code" style="margin-top:12px">${esc(JSON.stringify(r[S.tab], null, 2))}</pre></div>`; }
    wireBody(el);
  }

  function wireBody(el) {
    $$('[data-copy]', el).forEach((b) => b.addEventListener('click', () => copyText(b.dataset.copyText || decodeURIComponent(b.dataset.copy), b.dataset.label || 'Copied')));
    $$('[data-m]', el).forEach((b) => b.addEventListener('click', () => { S.openM = S.openM === b.dataset.m ? null : b.dataset.m; paintBody(); }));
    $$('[data-tr]', el).forEach((b) => b.addEventListener('click', () => { S.openTrace = S.openTrace === b.dataset.tr ? null : b.dataset.tr; paintBody(); }));
    $$('[data-goto]', el).forEach((b) => b.addEventListener('click', () => setTab(b.dataset.goto)));
    const sq = $('#srcQ', el);
    if (sq) sq.addEventListener('input', () => { S.srcQuery = sq.value; const pos = sq.selectionStart; paintBody(); const n = $('#srcQ'); n.focus(); n.setSelectionRange(pos, pos); });
    const nf = $('#noteForm', el);
    if (nf) nf.addEventListener('submit', async (e) => {
      e.preventDefault();
      const ta = $('#noteText'), text = ta.value.trim();
      if (!text) { ta.classList.add('has-error'); ta.focus(); return; }
      try {
        const n = await api('/api/leads/' + S.lead._id + '/notes', { method: 'POST', body: { text, author: (S.lead.crm && S.lead.crm.owner) || '' } });
        S.lead.crm = S.lead.crm || {}; S.lead.crm.notes = arr(S.lead.crm.notes).concat([n]);
        toast('Note added'); paintBody();
      } catch (err) { toast(err.message, true); }
    });
    if (S.tab === 'trace' && S.trace === null) {
      S.trace = 'loading';
      api('/api/leads/' + S.lead._id + '/trace').then((t) => { S.trace = t; if (S.tab === 'trace') paintBody(); }).catch((e) => { S.trace = { error: e.message }; if (S.tab === 'trace') paintBody(); });
    }
  }

  const sect = (title, body, right) => `<div class="card"><div class="cardhead"><span>${esc(title)}</span>${right || ''}</div><div class="pad16">${body}</div></div>`;
  const bul = (items, cls, m) => arr(items).length ? `<ul class="bul ${cls || ''}">${arr(items).map((i) => `<li><span>${cite(typeof i === 'string' ? i : JSON.stringify(i), m)}</span></li>`).join('')}</ul>` : '<span class="muted">None.</span>';

  function vHandoff(r) {
    const h = r.handoff || {}, m = srcMap(), bc = h.buyer_context || {}, qs = h.qualification_status || {}, ns = h.suggested_next_step || {}, rc = h.recommended_case_study || {};
    return `<div class="col gap16">
      <p class="lead" style="margin:0">${cite(h.one_line_summary, m)}</p>
      <div class="next">
        <span class="sh">suggested next step</span>
        <span class="h2">${cite(ns.action, m)}</span>
        <div class="row wrap gap8">${ns.owner ? `<span class="pill s-known">owner · ${esc(ns.owner)}</span>` : ''}${ns.by_when ? `<span class="pill p-P1">${esc(ns.by_when)}</span>` : ''}${h.gtm_motion ? `<span class="pill s-new">${esc(h.gtm_motion)}</span>` : ''}</div>
        ${ns.rationale ? `<span class="ink2">${cite(ns.rationale, m)}</span>` : ''}
      </div>
      ${sect('buyer context', `<div class="col gap12">
        <span class="strong">${esc(bc.who)}</span>
        <div class="col gap8"><span class="sh">what he cares about</span>${bul(bc.what_he_cares_about, '', m)}</div>
        ${arr(bc.others_involved).length ? `<div class="col gap8"><span class="sh">who else is involved</span><ul class="bul">${arr(bc.others_involved).map((o) => `<li><span><span class="strong">${esc(o.name_or_role || o.name || o)}</span>${o.why ? ' <span class="ink2">· ' + cite(o.why, m) + '</span>' : ''}</span></li>`).join('')}</ul></div>` : ''}
      </div>`)}
      ${sect('top 3 research findings', `<ol class="steps">${arr(h.top_3_research_highlights).map((f, i) => `<li class="stepi" style="grid-template-columns:32px minmax(0,1fr);align-items:start">
        <span class="sn" style="padding-top:2px">0${i + 1}</span>
        <span class="col gap4"><span>${cite(f.finding, m)} ${idChips(f.source_ids, f.finding, m)}</span>${f.why_ae_should_care ? `<span class="sowhat"><b>why it matters</b>${cite(f.why_ae_should_care, m)}</span>` : ''}</span></li>`).join('')}</ol>`, '<button type="button" class="btn btn-sm ease" data-goto="research">All research</button>')}
      <div class="split" style="gap:16px">
        <div class="wide" style="gap:16px">${sect('qualification status', `<div class="col gap12">
          <span><span class="strong">${esc(qs.framework)}</span> <span class="ink2">· ${esc(qs.scores)}</span></span>
          <div class="split" style="gap:16px"><div class="wide col gap8"><span class="sh">known</span>${bul(qs.knowns, '', m)}</div><div class="narrow col gap8"><span class="sh">still unknown</span>${bul(qs.unknowns, 'q', m)}</div></div>
        </div>`, '<button type="button" class="btn btn-sm ease" data-goto="qualification">MEDDPICC</button>')}</div>
      </div>
      ${sect('recommended case study', `<div class="col gap8"><a href="${esc(rc.url)}" target="_blank" rel="noopener noreferrer" class="strong">${esc(rc.title)}</a><span class="ink2">${cite(rc.why, m)}</span></div>`, '<button type="button" class="btn btn-sm ease" data-goto="case_study">Ranking</button>')}
      ${arr(h.watch_outs).length ? sect('watch-outs', bul(h.watch_outs, 'warn', m)) : ''}
    </div>`;
  }

  function vQual(r) {
    const q = r.qualification || {}, sc = q.scores || {}, m = srcMap();
    const els = arr(q.elements);
    const fits = Object.entries(q.fit_ratings || {});
    const w = q.fit_weights || {};
    return `<div class="col gap16">
      <div class="tiles">
        <div class="tile"><span class="v">${esc(sc.icp_fit_score)}</span><span class="l">ICP fit / 100</span></div>
        <div class="tile"><span class="v">${esc(sc.meddpicc_completeness)}%</span><span class="l">MEDDPICC known</span></div>
        <div class="tile"><span class="v">${esc(sc.priority_score)}</span><span class="l">priority score</span></div>
        <div class="tile"><span class="v">${esc((sc.priority_tier || '').split(/\s/)[0])}</span><span class="l">${esc((sc.priority_tier || '').split(':')[0].replace(/^P\d\s*-\s*/, '') || 'tier')}</span></div>
      </div>
      ${sc.priority_tier ? `<span class="ink2">${esc(sc.priority_tier)}</span>` : ''}
      ${sc.formula ? `<span class="mono sm muted">${esc(sc.formula)} · calculated in Python, not by the AI</span>` : ''}
      ${sect('framework · ' + (q.framework || ''), `<span class="ink2">${cite(q.framework_rationale, m)}</span>`)}
      <div class="card">
        <div class="cardhead"><span>meddpicc · ${els.filter((e) => e.status === 'known').length} known, ${els.filter((e) => e.status === 'partial').length} partial, ${els.filter((e) => e.status === 'unknown').length} unknown</span><span>click a row</span></div>
        ${els.map((e) => {
          const open = S.openM === e.key;
          return `<div><button type="button" class="mrow ease" aria-expanded="${open}" data-m="${esc(e.key)}">
            <span class="caret${open ? ' is-open' : ''}">${icon.caret}</span><span class="mkey">${esc(e.key)}</span>
            <span class="cell2"><span class="a">${esc(e.name)}</span><span class="b">${esc(e.status === 'known' ? e.evidence : e.missing)}</span></span>
            <span class="pill s-${esc(e.status)}">${esc(e.status)}</span></button>
            ${open ? `<div class="rowopen open">
              ${e.evidence ? `<span><span class="sh">from the email · </span>${cite(e.evidence, m)}</span>` : ''}
              ${e.missing ? `<span><span class="sh">missing · </span>${cite(e.missing, m)}</span>` : ''}
              ${e.discovery_question ? `<span class="row gap8" style="align-items:flex-start"><span class="sh" style="white-space:nowrap">ask ·</span><span class="strong">${esc(e.discovery_question)}</span></span>
              <button type="button" class="btn btn-sm ease" data-copy="${encodeURIComponent(e.discovery_question)}" data-label="Question copied">${icon.copy}Copy question</button>` : ''}
            </div>` : ''}</div>`;
        }).join('')}
      </div>
      ${sect('icp fit · rated 0-5 by the AI with evidence, weighted in code', fits.map(([k, v]) => {
        const rt = Number((v && v.rating) || 0);
        return `<div class="meter"><span class="col"><span class="strong">${esc(human(k))}</span><span class="sm muted">${esc(v && v.reason)}</span></span>
          <span class="pips" aria-label="${rt} of 5">${[1, 2, 3, 4, 5].map((i) => `<i class="${i <= rt ? 'on' : ''}"></i>`).join('')}</span>
          <span class="mono sm" style="text-align:right">${rt}/5${w[k] != null ? `<br><span class="muted xs">w${esc(w[k])}</span>` : ''}</span></div>`;
      }).join(''))}
      ${arr(q.risks).length ? sect('risks', bul(q.risks, 'warn', m)) : ''}
      ${q.summary ? sect('summary', `<span class="ink2">${cite(q.summary, m)}</span>`) : ''}
    </div>`;
  }

  function claims(list, m) {
    list = arr(list);
    if (!list.length) return '<span class="muted">Nothing verified in public sources.</span>';
    return list.map((f) => `<div class="finding">
      <span>${cite(f.claim, m)} ${idChips(f.source_ids, f.claim, m)} ${f.verification === 'partial' ? '<span class="pill s-partial">partly verified</span>' : ''}</span>
      ${f.so_what ? `<span class="sowhat"><b>so what</b>${cite(f.so_what, m)}</span>` : ''}
      ${f.verification_note ? `<span class="vnote">fact-check · ${esc(f.verification_note)}</span>` : ''}
    </div>`).join('');
  }
  function vResearch(r) {
    const R = r.research || {}, m = srcMap(), pos = R.positioning_recommendation || {}, org = R.org_structure || {};
    const kept = ['company_snapshot', 'budget_signals', 'recent_news', 'investor_priorities', 'operations_context', 'technology_adoption'].reduce((a, k) => a + arr(R[k]).length, 0) + arr(org.findings).length;
    return `<div class="col gap16">
      <div class="tiles">
        <div class="tile"><span class="v">${kept}</span><span class="l">claims kept</span></div>
        <div class="tile"><span class="v">${arr(R.removed_by_fact_check).length}</span><span class="l">removed by fact-check</span></div>
        <div class="tile"><span class="v">${arr(R.queries_run).length}</span><span class="l">searches run</span></div>
        <div class="tile"><span class="v">${arr(S.lead.sources).length}</span><span class="l">sources</span></div>
      </div>
      ${sect('how flytbase should position itself', `<div class="col gap12"><span>${cite(pos.summary, m)}</span>
        ${arr(pos.angles).length ? `<div class="col gap8"><span class="sh">angles</span>${bul(pos.angles, '', m)}</div>` : ''}
        ${arr(pos.risks_or_objections).length ? `<div class="col gap8"><span class="sh">likely objections</span>${bul(pos.risks_or_objections, 'warn', m)}</div>` : ''}</div>`)}
      ${sect('company snapshot', claims(R.company_snapshot, m))}
      ${sect('org structure and reporting lines', `${claims(org.findings, m)}
        ${org.likely_reporting_line ? `<div class="finding"><span class="sh">reporting line</span><span class="ink2">${cite(org.likely_reporting_line, m)}</span></div>` : ''}
        ${arr(org.relevant_stakeholders).length ? `<div class="finding"><span class="sh">stakeholders</span>${bul(arr(org.relevant_stakeholders).map((s) => typeof s === 'string' ? s : [s.name, s.title || s.role, s.relevance || s.why].filter(Boolean).join(' · ')), '', m)}</div>` : ''}`)}
      ${sect('budget signals · capex, opex, technology', claims(R.budget_signals, m))}
      ${sect('recent news and announcements', claims(R.recent_news, m))}
      ${sect('investor and stakeholder priorities', claims(R.investor_priorities, m))}
      ${sect('operations context', claims(R.operations_context, m))}
      ${sect('technology adoption', claims(R.technology_adoption, m))}
      ${arr(R.not_found).length ? sect('not found in public sources', bul(R.not_found, 'q', m)) : ''}
      ${arr(R.removed_by_fact_check).length ? sect('removed by the fact-checker · never shown to the AE as fact', arr(R.removed_by_fact_check).map((f) => `<div class="finding"><span class="struck">${esc(f.claim)}</span><span class="vnote" style="color:var(--red)">${esc(f.verification_note || 'unsupported')}</span></div>`).join('')) : ''}
      ${arr(R.queries_run).length ? sect('searches the AI planned', `<div class="col gap8">${arr(R.queries_run).map((q) => `<div class="row gap8 wrap"><span class="chip mono xs">${esc(q.category)}</span><span class="mono sm ink2">${esc(q.query)}</span></div>`).join('')}</div>`) : ''}
    </div>`;
  }

  function vEmails(r) {
    const E = r.emails || {}, m = srcMap();
    return `<div class="col gap16">
      ${E.sequence_strategy ? sect('sequence strategy', `<span>${cite(E.sequence_strategy, m)}</span>`) : ''}
      <ol class="timeline">${arr(E.emails).map((e, i, a) => `<li>
        <span class="mono sm muted" style="padding-top:2px">${esc(e.send_when)}</span>
        <span class="tl-dot"><span style="border-color:var(--accent)"></span>${i < a.length - 1 ? '<span></span>' : ''}</span>
        <div class="tl-body"><div class="mail">
          <div class="mailhead"><span class="col" style="min-width:0"><span class="mono xs" style="color:var(--accent)">email ${esc(e.step)}</span><span class="strong">${esc(e.subject)}</span></span>
            <button type="button" class="btn btn-sm ease" data-copy="${encodeURIComponent('Subject: ' + e.subject + '\n\n' + e.body)}" data-label="Email ${esc(e.step)} copied">${icon.copy}Copy</button></div>
          ${e.goal ? `<div style="padding:12px 16px 0" class="sm"><span class="sh">goal · </span>${esc(e.goal)}</div>` : ''}
          <div class="mailbody">${esc(e.body)}</div>
          <div class="mailmeta">
            <span><b>meddpicc gaps targeted</b>${arr(e.meddpicc_gaps_targeted).map((g) => `<span class="pill s-unknown" style="margin:4px 4px 0 0">${esc(g)}</span>`).join('') || '--'}</span>
            <span><b>research used</b>${idChips(e.research_used, '', m) || '--'}</span>
            <span><b>why this email now</b>${cite(e.why_this_email_now, m)}</span>
            <span><b>success signal</b>${esc(e.success_signal)}</span>
          </div>
        </div></div></li>`).join('')}</ol>
      ${arr(E.branches).length ? sect('if he replies', arr(E.branches).map((b) => `<div class="finding">
        <span class="row gap8 wrap"><span class="pill s-partial">if: ${esc(b.if_reply)}</span><span class="ink2">→ ${esc(b.next_action)}</span></span>
        ${b.draft_reply ? `<div class="mailbody" style="padding:12px;border:1px solid var(--line2);border-radius:6px;background:var(--side);font-size:13px">${esc(b.draft_reply)}</div>
        <button type="button" class="btn btn-sm ease" style="align-self:flex-start" data-copy="${encodeURIComponent(b.draft_reply)}" data-label="Reply copied">${icon.copy}Copy reply</button>` : ''}
      </div>`).join('')) : ''}
    </div>`;
  }

  function vCase(r) {
    const C = r.case_study || {}, m = srcMap(), p = C.primary || {}, ex = C.existing_relationship || {}, ref = C.referral_connection || {}, sec = C.secondary || {};
    return `<div class="col gap16">
      ${ex.found ? `<div class="card pad16" style="border-color:var(--green);background:var(--green-soft)"><span class="row gap8 strong" style="color:var(--green)">${icon.check}Already a FlytBase customer</span><span class="ink2 s13">${cite(ex.explanation, m)} ${ex.source_id ? chip(ex.source_id, m) : ''}</span></div>` : ''}
      <div class="card pad col gap12">
        <span class="sh">strongest fit</span>
        <a class="h2" href="${esc(p.url)}" target="_blank" rel="noopener noreferrer" style="color:var(--ink)">${esc(p.title)} ${p.source_id ? chip(p.source_id, m) : ''}</a>
        <span class="ink2">${cite(p.why_strongest_fit, m)}</span>
        ${arr(p.key_proof_points).length ? `<div class="tiles">${arr(p.key_proof_points).map((x) => `<div class="tile"><span class="s13">${esc(x)}</span></div>`).join('')}</div>` : ''}
        ${p.how_to_use_it ? `<span class="sowhat"><b>how to use it</b>${cite(p.how_to_use_it, m)}</span>` : ''}
      </div>
      ${sect('referral connection' + (ref.found ? ' · found' : ' · not found'), `<div class="col gap8">${ref.url ? `<a href="${esc(ref.url)}" target="_blank" rel="noopener noreferrer">${esc(ref.url.replace(/^https?:\/\/(www\.)?/, ''))}</a>` : ''}<span class="ink2">${cite(ref.explanation, m)}</span></div>`)}
      ${sec.url ? sect('second case study', `<div class="col gap8"><a href="${esc(sec.url)}" target="_blank" rel="noopener noreferrer">${esc(sec.title || sec.url.replace(/^https?:\/\/(www\.)?/, ''))}</a><span class="ink2">${cite(sec.why, m)}</span></div>`) : ''}
      ${arr(C.people_named).length ? sect('people named on flytbase.com', bul(arr(C.people_named).map((x) => `${x.name} · ${x.title || ''}${x.company ? ', ' + x.company : ''}${x.relevance ? ' — ' + x.relevance : ''}${x.source_id ? ' [' + x.source_id + ']' : ''}`), '', m)) : ''}
      ${sect(`ranking · ${C.case_studies_scanned || arr(C.pre_scores).length} case studies scanned from the sitemap`, arr(C.ranking).map((x) => `<div class="finding">
        <span class="row between gap12"><a href="${esc(x.url)}" target="_blank" rel="noopener noreferrer" class="strong trunc">${esc(String(x.title || x.url).replace(/\s*\|\s*FlytBase.*$/, ''))}</a><span class="mono sm">${esc(x.fit_score)}</span></span>
        <div class="bar"><span style="width:${Math.max(0, Math.min(100, Number(x.fit_score) || 0))}%"></span></div>
        <span class="sm ink2">${['industry_match', 'use_case_match', 'context_match'].filter((k) => x[k]).map((k) => `<span class="muted">${human(k).replace(' match', '')}:</span> ${esc(x[k])}`).join(' &nbsp;·&nbsp; ')}</span>
        ${x.reason || x.why ? `<span class="sm muted">${esc(x.reason || x.why)}</span>` : ''}
      </div>`).join(''))}
    </div>`;
  }

  function vPartner(r) {
    const P = r.partner || {}, m = srcMap(), j = P.justification || {}, roles = P.roles || {};
    return `<div class="col gap16">
      <div class="next"><span class="sh">recommended motion</span><span class="h2">${esc(P.motion)}</span>${P.partner_type_needed ? `<span class="ink2">${cite(P.partner_type_needed, m)}</span>` : ''}</div>
      ${sect('why', `<div class="facts" style="border:0;padding:0;background:transparent">${Object.entries(j).map(([k, v]) => `<span class="k">${esc(human(k))}</span><span class="v">${cite(v, m)}</span>`).join('')}</div>`)}
      ${arr(P.recommended_partners).map((x) => `<div class="card pad16 col gap8">
        <span class="row between wrap gap8"><span class="strong">${esc(x.name)}</span><span class="row gap8">${x.type ? `<span class="chip mono xs">${esc(x.type)}</span>` : ''}${x.country ? `<span class="chip mono xs">${esc(x.country)}</span>` : ''}
          <span class="pill ${x.verified_in_sources ? 's-supported' : 's-unsupported'}">${x.verified_in_sources ? 'name found in sources' : 'not verified'}</span></span></span>
        ${x.evidence ? `<span class="sm ink2">${cite(x.evidence, m)}</span>` : ''}
        ${x.role_in_deal ? `<span class="sowhat"><b>role in the deal</b>${cite(x.role_in_deal, m)}</span>` : ''}
      </div>`).join('')}
      ${Object.keys(roles).length ? sect('who does what', `<div class="facts" style="border:0;padding:0;background:transparent">${Object.entries(roles).map(([k, v]) => `<span class="k">${esc(k === 'flytbase_ae' ? 'FlytBase AE' : k === 'bdr' ? 'BDR' : human(k))}</span><span class="v">${cite(v, m)}</span>`).join('')}</div>`) : ''}
      ${arr(P.risks).length ? sect('risks', bul(P.risks, 'warn', m)) : ''}
    </div>`;
  }

  function vSources() {
    const q = S.srcQuery.trim().toLowerCase();
    const all = arr(S.lead.sources);
    const list = all.filter((s) => !q || [s.id, s.title, s.url, s.kind, s.query].join(' ').toLowerCase().includes(q));
    return `<div class="col gap16">
      <div class="row between wrap gap12"><label style="flex:0 1 300px"><span class="sr">Filter sources</span><input class="field ease" id="srcQ" type="search" placeholder="Filter sources" value="${esc(S.srcQuery)}"></label><span class="mono sm muted">${list.length} of ${all.length}</span></div>
      <div class="card">${list.map((s) => `<div class="finding" style="padding:12px 16px">
        <span class="row gap8" style="min-width:0"><span class="cite">${esc(s.id)}</span><a class="trunc strong" href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.title)}</a></span>
        <span class="row gap8 wrap sm muted"><span class="chip mono xs">${esc(s.kind)}</span>${s.published ? `<span class="mono xs">${esc(s.published)}</span>` : ''}${s.query ? `<span class="mono xs trunc">“${esc(s.query)}”</span>` : ''}</span>
      </div>`).join('') || '<div class="empty"><span class="muted">No source matches.</span></div>'}</div>
    </div>`;
  }

  function vTrace() {
    const t = S.trace;
    if (t === null || t === 'loading') return '<div class="row gap8 muted"><span class="spin dark"></span>Loading every prompt and response…</div>';
    if (t.error) return `<span style="color:var(--red)">${esc(t.error)}</span>`;
    if (!t.length) return '<span class="muted">No AI calls recorded yet.</span>';
    return `<div class="col gap12"><span class="muted s13">Every prompt the agent sent and every answer it got, in order. ${t.length} calls · ${Math.round(t.reduce((a, x) => a + (x.seconds || 0), 0))} s of model time.</span>
      <div class="card">${t.map((x, i) => {
        const open = S.openTrace === String(i);
        return `<div><button type="button" class="mrow ease" aria-expanded="${open}" data-tr="${i}">
          <span class="caret${open ? ' is-open' : ''}">${icon.caret}</span><span class="mono sm muted">${String(i + 1).padStart(2, '0')}</span>
          <span class="cell2"><span class="a mono s13">${esc(x.stage)}</span><span class="b">${esc(x.model)}</span></span><span class="mono sm ink2">${esc(x.seconds)} s</span></button>
          ${open ? `<div class="rowopen open" style="padding-left:16px;align-items:stretch">
            ${x.system ? `<span class="sh">system</span><pre class="code">${esc(x.system)}</pre>` : ''}
            <span class="sh">prompt</span><pre class="code">${esc(x.prompt)}</pre>
            <span class="sh">response</span><pre class="code">${esc(x.response)}</pre></div>` : ''}</div>`;
      }).join('')}</div></div>`;
  }

  function vNotes() {
    const notes = arr(S.lead.crm && S.lead.crm.notes).slice().reverse();
    return `<div class="col gap16">
      <form class="card pad16 col gap12" id="noteForm" novalidate>
        <label class="col gap8"><span class="s13 strong">Add a note</span>
          <textarea class="field ease" id="noteText" style="min-height:96px;font-family:var(--sans);font-size:14px" placeholder="Call outcome, what Rodrigo said, next step…"></textarea></label>
        <button type="submit" class="btn btn-accent ease" style="align-self:flex-start">Save note</button>
      </form>
      <div class="card pad16">${notes.length ? notes.map((n) => `<div class="note"><span class="mono xs muted">${esc(stamp(n.at))}${n.author ? ' · ' + esc(n.author) : ''}</span><span style="white-space:pre-wrap">${esc(n.text)}</span></div>`).join('') : '<span class="muted">No notes yet. Notes are saved to MongoDB with the lead.</span>'}</div>
    </div>`;
  }

  function vInput() {
    const t = S.lead.email_text || '';
    return `<div class="card"><div class="cardhead"><span>the only input the agent got</span><button type="button" class="btn btn-sm ease" data-copy="${encodeURIComponent(t)}" data-label="Email copied">${icon.copy}Copy</button></div>
      <pre class="code" style="border:0;border-radius:0 0 8px 8px;max-height:none;font-size:13px">${esc(t)}</pre></div>`;
  }

  // ------------------------------------------------------------ activity
  async function showActivity(main) {
    main.innerHTML = `<div class="view col" style="gap:24px"><div class="col gap4"><h1 class="title">Activity</h1><span class="muted">Leads received, runs finished, notes added.</span></div><div id="act" class="row gap8 muted"><span class="spin dark"></span>Loading…</div></div>`;
    let items;
    try { items = await api('/api/activity'); } catch (e) { $('#act').innerHTML = `<span style="color:var(--red)">${esc(e.message)}</span>`; return; }
    const color = { received: 'var(--blue)', imported: 'var(--faint)', qualified: 'var(--green)', failed: 'var(--red)', note: 'var(--accent)' };
    $('#act').outerHTML = items.length ? `<ol class="timeline" style="max-width:760px">${items.map((i, n) => `<li>
      <span class="mono sm muted" style="padding-top:2px">${esc(stamp(i.at))}</span>
      <span class="tl-dot"><span style="border-color:${color[i.kind] || 'var(--muted)'}"></span>${n < items.length - 1 ? '<span></span>' : ''}</span>
      <span class="tl-body"><span class="mono xs" style="color:${color[i.kind] || 'var(--muted)'}">${esc(i.kind)}</span>
        <a class="strong" href="#/lead/${esc(i.lead)}" style="color:var(--ink);text-decoration:none">${esc(i.title)}</a>
        ${i.note ? `<span class="ink2 s13">${esc(i.note)}</span>` : ''}</span></li>`).join('')}</ol>`
      : '<div class="empty dashed"><span class="strong">Nothing yet</span><span class="muted">Run the agent on a lead and it shows up here.</span></div>';
  }

  // ------------------------------------------------------------ system
  async function showSystem(main) {
    await refreshHealth();
    const h = S.health || {};
    const okp = (ok, yes, no) => `<span class="pill ${ok ? 's-known' : 's-failed'}">${ok ? yes : no}</span>`;
    main.innerHTML = `<div class="view split">
      <div class="wide">
        <div class="card pad col" style="gap:24px">
          <div class="col gap8"><span class="mono sm muted">python · gemini · tavily · mongodb</span>
            <span class="h2" style="font-size:20px">Inbound Lead Agent</span>
            <span class="ink2">Takes one raw inbound email and does a BDR’s first hour of work. Stages run in the order below: emails are written last so they can use the research, case study and partner.</span></div>
          <ol class="steps">${STAGES.map((s) => `<li class="stepi" style="grid-template-columns:32px minmax(0,1fr)"><span class="sn">${s.n}</span><span><span class="strong">${s.name}</span> <span class="muted">· ${s.does}</span></span></li>`).join('')}</ol>
        </div>
        <div class="card pad col gap12"><span class="b6">How it decides</span>
          <ul class="bul">
            <li><span><span class="strong">The AI reads, Python decides.</span> <span class="ink2">Scores, tiers, fact-check removal and partner verification are plain code.</span></span></li>
            <li><span><span class="strong">No unsourced claims.</span> <span class="ink2">Research may only cite source IDs, and a second model call checks each claim against the cited text.</span></span></li>
            <li><span><span class="strong">Nothing hard-coded.</span> <span class="ink2">Case studies come from the live flytbase.com sitemap; partners from the partner directory and search.</span></span></li>
            <li><span><span class="strong">Everything is inspectable.</span> <span class="ink2">Each lead keeps its stage outputs, sources and the full AI trace.</span></span></li>
          </ul></div>
      </div>
      <div class="narrow">
        <div class="facts">
          <span class="k">MongoDB</span><span class="v">${okp(h.mongo, 'connected', 'not connected')} ${h.database ? `<span class="mono sm">${esc(h.database)}</span>` : ''}${h.mongo_error ? `<br><span class="sm" style="color:var(--red)">${esc(h.mongo_error)}</span>` : ''}</span>
          <span class="k">API keys</span><span class="v">${okp(!(h.missing_keys || []).length, 'gemini + tavily', 'missing ' + esc((h.missing_keys || []).join(', ')))}</span>
          <span class="k">Models</span><span class="v mono sm">${esc((h.models || []).join(', '))}</span>
          <span class="k">Worker</span><span class="v">${h.running ? 'running a lead' : 'idle'}${h.queued ? ` · ${h.queued} queued` : ''}</span>
          <span class="k">Access</span><span class="v">Internal only. Bound to this machine (127.0.0.1).</span>
          <span class="k">API</span><span class="v"><a href="/api/docs" target="_blank" rel="noopener">/api/docs</a></span>
        </div>
        <div class="dashed pad col gap8"><span class="b6">Not wired yet</span><span class="muted s13">Contact-form webhook, CRM sync and Slack approval for email 1 would plug into POST /api/leads.</span></div>
      </div>
    </div>`;
  }

  // ------------------------------------------------------------ command palette
  function commands(q) {
    const go = (h) => () => { location.hash = h; };
    const base = [
      { sym: '→', label: 'Go to leads', group: 'navigate', run: go('#/leads') },
      { sym: '+', label: 'New lead', group: 'action', run: go('#/new') },
      { sym: '→', label: 'Go to activity', group: 'navigate', run: go('#/activity') },
      { sym: '→', label: 'Go to system', group: 'navigate', run: go('#/system') },
    ];
    if (S.lead) {
      base.push({ sym: '⧉', label: 'Copy email 1 for ' + ((S.lead.summary || {}).name || 'this lead'), group: 'action', run: () => { const b = $('#copyE1'); if (b) b.click(); else toast('No email drafted yet', true); } });
      TABS.filter(tabEnabled).forEach((t) => base.push({ sym: '#', label: 'Show ' + t.label.toLowerCase(), group: 'this lead', run: () => setTab(t.id) }));
    }
    S.leads.forEach((l) => { const s = l.summary || {}; base.push({ sym: s.tier || '·', label: (s.name || 'Unknown') + ' · ' + (s.company || ''), group: 'lead', run: go('#/lead/' + l._id) }); });
    q = (q || '').trim().toLowerCase();
    return base.filter((c) => !q || c.label.toLowerCase().includes(q)).slice(0, 40);
  }
  function openPalette() {
    const el = $('#palette');
    el.innerHTML = `<div class="pal"><button type="button" class="scrim" aria-label="Close" id="palScrim"></button>
      <div class="modal" role="dialog" aria-label="Jump to"><label><span class="sr">Search commands</span><input class="pin" id="palIn" placeholder="Type a command or a lead’s name" autocomplete="off"></label>
      <div class="cmds" id="palList"></div>
      <div class="palfoot"><span>↑↓ to move</span><span>enter to run</span><span>esc to close</span></div></div></div>`;
    S.paletteSel = 0;
    const input = $('#palIn');
    const paint = () => {
      const list = commands(input.value);
      S.paletteSel = Math.min(S.paletteSel, Math.max(0, list.length - 1));
      $('#palList').innerHTML = list.length ? list.map((c, i) => `<button type="button" class="cmd ease${i === S.paletteSel ? ' is-sel' : ''}" data-i="${i}"><span class="sym">${esc(c.sym)}</span><span class="trunc">${esc(c.label)}</span><span class="grp">${esc(c.group)}</span></button>`).join('')
        : `<div class="empty" style="padding:24px 12px"><span>No command matches “${esc(input.value)}”</span><span class="sm muted">Try “new” or a company name.</span></div>`;
      $$('#palList [data-i]').forEach((b) => b.addEventListener('click', () => { closePalette(); list[+b.dataset.i].run(); }));
      const sel = $('#palList .is-sel'); if (sel) sel.scrollIntoView({ block: 'nearest' });
      return list;
    };
    let list = paint();
    input.addEventListener('input', () => { S.paletteSel = 0; list = paint(); });
    input.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowDown') { e.preventDefault(); S.paletteSel = Math.min(S.paletteSel + 1, list.length - 1); paint(); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); S.paletteSel = Math.max(S.paletteSel - 1, 0); paint(); }
      else if (e.key === 'Enter') { e.preventDefault(); const c = list[S.paletteSel]; if (c) { closePalette(); c.run(); } }
      else if (e.key === 'Escape') { closePalette(); }
    });
    $('#palScrim').addEventListener('click', closePalette);
    input.focus();
  }
  function closePalette() { $('#palette').innerHTML = ''; }

  // ------------------------------------------------------------ boot
  $('#jumpBtn').addEventListener('click', openPalette);
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); $('#palIn') ? closePalette() : openPalette(); }
  });
  window.addEventListener('hashchange', render);
  window.addEventListener('resize', moveInd);
  refreshHealth();
  setInterval(refreshHealth, 5000);
  refreshLeads().then(render);
})();
