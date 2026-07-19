// ════════════════════════════════════════════════════════════════
//  CONFIG
// ════════════════════════════════════════════════════════════════
const API = window.__CONVERTALE_API_URL__ || 'http://127.0.0.1:8080';
// getAuthToken() is injected by app/dashboard/page.tsx (backed by Clerk's
// useAuth().getToken()). The dashboard previously called the API with no
// Authorization header at all, so every authenticated call (e.g.
// POST /api/campaigns, which requires a Clerk bearer token) would have
// always failed with 401 against the real backend.
async function authHeaders(extra) {
  const token = window.__CONVERTALE_GET_TOKEN__ ? await window.__CONVERTALE_GET_TOKEN__() : null;
  return { ...(extra || {}), ...(token ? { Authorization: `Bearer ${token}` } : {}) };
}

// ════════════════════════════════════════════════════════════════
//  AGENTS
// ════════════════════════════════════════════════════════════════
const AGENTS = [
  { key: 'intake',      name: 'Brand Intake',     role: 'Extracts structured brief from raw brief',       icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5.586a1 1 0 0 1 .707.293l5.414 5.414A1 1 0 0 1 20 9.414V19a2 2 0 0 1-2 2z' },
  { key: 'writers',     name: 'Writers Room',     role: 'Generates multi-episode cliffhanger arc',        icon: 'M4 20h4L19 9l-4-4L4 16v4zM14 6l4 4' },
  { key: 'storyboard',  name: 'Storyboard',       role: 'Breaks synopsis into shot sequences',            icon: 'M4 5h7v6H4zM13 5h7v6h-7zM4 13h7v6H4zM13 13h7v6h-7z' },
  { key: 'continuity',  name: 'Continuity Gate',  role: 'Validates narrative consistency',                icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0 1 12 2.944a11.955 11.955 0 0 1-8.618 3.04A12.02 12.02 0 0 0 3 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z' },
  { key: 'video',       name: 'Cinematographer',  role: 'Renders shots via Wan (Qwen Cloud)',             icon: 'M3 8a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8zM16 10l5-3v10l-5-3' },
  { key: 'critic',      name: 'Visual Critic',    role: 'Qwen-VL identity check + prompt optimizer',      icon: 'M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7zM12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6z' },
  { key: 'assembly',    name: 'Editor',           role: 'ffmpeg concat + SRT subtitle burn-in',           icon: 'M6 9a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM6 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM8.5 7.5L20 18M8.5 16.5L20 6' },
];

const railEl = document.getElementById('agentRail');
const agentNodes = {};

for (const a of AGENTS) {
  const el = document.createElement('div');
  el.className = 'agent-node';
  el.id = 'node-' + a.key;
  el.innerHTML = `
    <div class="agent-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
        <path d="${a.icon}"/>
      </svg>
    </div>
    <div class="agent-info">
      <div class="agent-name">${a.name}</div>
      <div class="agent-role">${a.role}</div>
    </div>`;
  railEl.appendChild(el);
  agentNodes[a.key] = el;
}

let activeAgent = null;
function setAgent(key) {
  if (activeAgent && key !== activeAgent) {
    agentNodes[activeAgent].classList.remove('active');
    agentNodes[activeAgent].classList.add('done');
  }
  if (key && agentNodes[key]) {
    agentNodes[key].classList.remove('done');
    agentNodes[key].classList.add('active');
  }
  activeAgent = key;
}
function resetRail() {
  for (const k in agentNodes) agentNodes[k].classList.remove('active', 'done');
  activeAgent = null;
}
function completeRail() {
  for (const k in agentNodes) { agentNodes[k].classList.remove('active'); agentNodes[k].classList.add('done'); }
  activeAgent = null;
}

// ════════════════════════════════════════════════════════════════
//  ACTIVITY LOG
// ════════════════════════════════════════════════════════════════
const streamEl = document.getElementById('activityStream');
function log(msg, cls='') {
  const empties = streamEl.querySelectorAll('.stream-empty');
  empties.forEach(e => e.remove());
  const div = document.createElement('div');
  div.className = 'log-line' + (cls ? ' ' + cls : '');
  const now = new Date().toTimeString().slice(0,8);
  div.innerHTML = `<span class="log-ts">${now}</span><span class="log-msg"></span>`;
  div.querySelector('.log-msg').textContent = msg;
  streamEl.appendChild(div);
  streamEl.scrollTop = streamEl.scrollHeight;
}
function clearStream() {
  streamEl.innerHTML = '<div class="stream-empty">Stream cleared.</div>';
}

// ════════════════════════════════════════════════════════════════
//  API STATUS CHECK
// ════════════════════════════════════════════════════════════════
const dot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');

async function checkApiStatus() {
  try {
    const res = await fetch(`${API}/health`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      dot.className = 'status-dot online';
      statusText.textContent = 'API online';
      return true;
    }
  } catch(_) {}
  dot.className = 'status-dot error';
  statusText.textContent = 'API unreachable';
  return false;
}

// ════════════════════════════════════════════════════════════════
//  STATS (mocked until real API connected)
// ════════════════════════════════════════════════════════════════
const leads = JSON.parse(localStorage.getItem('cv_leads') || '[]');
const campaigns = JSON.parse(localStorage.getItem('cv_campaigns') || '[]');

function updateStats() {
  document.getElementById('statCampaigns').textContent = campaigns.length;
  document.getElementById('statLeads').textContent = leads.length;
}
updateStats();

// ════════════════════════════════════════════════════════════════
//  GENERATE CAMPAIGN
// ════════════════════════════════════════════════════════════════
async function generateCampaign() {
  const btn = document.getElementById('generateBtn');
  const resultEl = document.getElementById('generateResult');
  const rawBrief = document.getElementById('rawBrief').value.trim();
  const title = document.getElementById('campaignTitle').value.trim();
  const workspaceId = document.getElementById('workspaceId').value.trim();
  const protName = document.getElementById('protName').value.trim();
  const protLook = document.getElementById('protLook').value.trim();
  const numEp = parseInt(document.getElementById('numEpisodes').value, 10) || 2;

  if (!rawBrief) { log('⚠ Please enter a brand brief', 'err'); return; }

  btn.disabled = true;
  btn.innerHTML = '<div class="spinner"></div> Commissioning…';
  resultEl.style.display = 'none';
  resetRail();
  dot.className = 'status-dot running';
  statusText.textContent = 'Pipeline running…';

  // Simulate agent steps while calling real API
  const steps = [
    { key: 'intake',     msg: 'Parsing brand brief…', delay: 600 },
    { key: 'writers',    msg: 'Writers Room crafting story arc…', delay: 1200 },
    { key: 'storyboard', msg: 'Storyboarding shots…', delay: 900 },
    { key: 'continuity', msg: 'Continuity Gate checking narrative…', delay: 700 },
    { key: 'video',      msg: 'Queueing Wan renders (background)…', delay: 800 },
    { key: 'critic',     msg: 'Visual Critic primed…', delay: 600 },
    { key: 'assembly',   msg: 'Editor standing by for assembly…', delay: 500 },
  ];

  log(`Commissioning "${title || 'New Campaign'}" · ${numEp} episodes`, 'sys');

  let stepIdx = 0;
  const stepInterval = setInterval(() => {
    if (stepIdx < steps.length) {
      const s = steps[stepIdx];
      setAgent(s.key);
      log(s.msg);
      stepIdx++;
    } else {
      clearInterval(stepInterval);
    }
  }, 900);

  try {
    const payload = {
      raw_brief: rawBrief,
      title: title || 'New Campaign',
      workspace_id: workspaceId,
      protagonist_name: protName,
      protagonist_look: protLook,
      n_episodes: numEp,
    };

    const res = await fetch(`${API}/api/campaigns`, {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload),
    });

    clearInterval(stepInterval);

    if (res.ok) {
      const data = await res.json();
      completeRail();

      const projectId = data.project_id;
      campaigns.push({ id: projectId, title: title || 'New Campaign', created: new Date().toISOString() });
      localStorage.setItem('cv_campaigns', JSON.stringify(campaigns));
      updateStats();

      document.getElementById('statEpisodes').textContent = numEp;
      document.getElementById('bibleSeriesId').textContent = projectId?.slice(0,8) || '';
      renderBible(protName, protLook, numEp);

      resultEl.style.display = 'block';
      resultEl.style.color = 'var(--green)';
      resultEl.textContent = `✓ Project ${projectId} queued. Background pipeline started.`;
      log(`Campaign created: ${projectId}`, 'ok');
      dot.className = 'status-dot online';
      statusText.textContent = 'Pipeline queued';
    } else {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
  } catch(e) {
    clearInterval(stepInterval);
    log(`Error: ${e.message}`, 'err');
    dot.className = 'status-dot error';
    statusText.textContent = 'Error';
    resultEl.style.display = 'block';
    resultEl.style.color = 'var(--red)';
    resultEl.textContent = `✗ ${e.message}`;
  }

  btn.disabled = false;
  btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 3l14 9-14 9V3z"/></svg> Generate Campaign`;
}

// ════════════════════════════════════════════════════════════════
//  SERIES BIBLE RENDER
// ════════════════════════════════════════════════════════════════
function renderBible(name, look, epCount, identityScore) {
  const el = document.getElementById('bibleContent');
  if (!name) { el.innerHTML = '<div class="bible-empty">No series commissioned yet.</div>'; return; }
  el.innerHTML = `
    <div class="bible-card">
      <div class="char-thumbnail">
        <div class="ph-text">Reference frame appears when Wan renders complete</div>
      </div>
      <div class="char-info">
        <div class="char-name-row">
          <span class="char-name">${escapeHtml(name || 'Protagonist')}</span>
          <span class="lock-badge">
            <svg viewBox="0 0 24 24" width="9" height="9" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>
            Locked
          </span>
        </div>
        <div class="char-look"><strong>${escapeHtml(look || 'Appearance prompt carried into every episode.')}</strong></div>
        <div class="bible-stats">
          <div class="bs"><div class="bs-label">Episodes</div><div class="bs-value accent">${epCount}</div></div>
          <div class="bs"><div class="bs-label">Look Reused</div><div class="bs-value">100%</div></div>
          ${identityScore != null ? `<div class="bs"><div class="bs-label">Identity</div><div class="bs-value gold">${Number(identityScore).toFixed(2)}</div></div>` : ''}
        </div>
      </div>
    </div>`;
}

// ════════════════════════════════════════════════════════════════
//  EPISODE GALLERY
// ════════════════════════════════════════════════════════════════
function refreshEpisodes() {
  const gallery = document.getElementById('episodeGallery');
  // Placeholder: in a real app, fetch /api/projects/:id/episodes
  gallery.innerHTML = `
    <div class="episode-grid">
      <div class="ep-card" style="animation-delay:0ms">
        <div style="width:100%;aspect-ratio:9/16;background:linear-gradient(180deg,#1a1040,#070810);display:flex;align-items:center;justify-content:center;max-height:220px">
          <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="rgba(124,92,252,0.3)" stroke-width="1.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
        </div>
        <div class="ep-card-body">
          <div class="ep-num">Episode 01</div>
          <div class="ep-title">Processing…</div>
          <div class="ep-badge processing">⏳ rendering</div>
        </div>
      </div>
    </div>`;
}

// ════════════════════════════════════════════════════════════════
//  CLIFFHANGER GATE TEST
// ════════════════════════════════════════════════════════════════
async function testGate() {
  const email = document.getElementById('gateEmail').value.trim();
  const projectId = document.getElementById('gateProjectId').value.trim();
  const episodeId = document.getElementById('gateEpisodeId').value.trim();
  const resultEl = document.getElementById('gateResult');

  if (!email) { alert('Enter an email address.'); return; }

  resultEl.className = 'gate-result show';
  resultEl.textContent = 'Contacting gate…';
  resultEl.style.background = 'var(--surface-2)';
  resultEl.style.color = 'var(--text-faint)';

  try {
    const res = await fetch(`${API}/api/gate/unlock`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, project_id: projectId, episode_id: episodeId }),
    });
    const data = await res.json();

    if (res.ok) {
      leads.push({ email, projectId, episodeId, ts: new Date().toISOString(), status: data.status });
      localStorage.setItem('cv_leads', JSON.stringify(leads));
      updateStats();

      resultEl.className = 'gate-result show ok';
      resultEl.textContent = `✓ Lead captured (${data.lead_id?.slice(0,8) || 'ok'}) · status: ${data.status}`;
      log(`Lead: ${email} → ${data.status}`, 'ok');
    } else {
      resultEl.className = 'gate-result show err';
      resultEl.textContent = `✗ ${data.detail || 'Error'}`;
    }
  } catch(e) {
    resultEl.className = 'gate-result show err';
    resultEl.textContent = `✗ ${e.message} (Is the API running on port 8000?)`;
  }
}

// ════════════════════════════════════════════════════════════════
//  VIEW ROUTING
// ════════════════════════════════════════════════════════════════
function showView(name, evt) {
  ['studio','campaigns','leads'].forEach(v => {
    const el = document.getElementById(`view-${v}`);
    el.style.display = v === name ? 'block' : 'none';
  });
  document.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
  // Use the passed element if available, fall back to event target
  const trigger = (evt && evt.currentTarget) || (typeof event !== 'undefined' && event && event.target);
  if (trigger) trigger.classList.add('active');
  if (name === 'campaigns') loadCampaigns();
  if (name === 'leads') loadLeads();
}

function loadCampaigns() {
  const el = document.getElementById('campaignsList');
  if (!campaigns.length) { el.innerHTML = '<div style="color:var(--text-faint);font-size:13px;padding:20px 0;text-align:center;">No campaigns yet. Commission one from the Studio.</div>'; return; }
  el.innerHTML = campaigns.map(c => `
    <div style="display:flex;align-items:center;justify-content:space-between;padding:12px 0;border-bottom:1px solid var(--border);">
      <div>
        <div style="font-weight:600;font-size:13.5px;">${escapeHtml(c.title)}</div>
        <div style="font-family:var(--mono);font-size:10.5px;color:var(--text-faint);margin-top:2px;">${c.id}</div>
      </div>
      <div style="font-family:var(--mono);font-size:11px;color:var(--text-faint);">${new Date(c.created).toLocaleDateString()}</div>
    </div>`).join('');
}

function loadLeads() {
  const el = document.getElementById('leadsList');
  if (!leads.length) { el.innerHTML = '<div style="color:var(--text-faint);font-size:13px;padding:20px 0;text-align:center;">No leads yet. Test the Cliffhanger Gate from the Studio.</div>'; return; }
  el.innerHTML = `
    <table style="width:100%;border-collapse:collapse;font-size:12.5px;">
      <thead><tr style="color:var(--text-faint);font-family:var(--mono);font-size:10px;letter-spacing:.08em;text-transform:uppercase;text-align:left;border-bottom:1px solid var(--border);">
        <th style="padding:8px 0;">Email</th><th>Project</th><th>Status</th><th>Time</th>
      </tr></thead>
      <tbody>
      ${leads.map(l => `<tr style="border-bottom:1px solid var(--border);">
        <td style="padding:10px 0;color:var(--text);">${escapeHtml(l.email)}</td>
        <td style="font-family:var(--mono);font-size:10.5px;color:var(--text-faint);">${(l.projectId||'').slice(0,8)}</td>
        <td><span class="ep-badge ${l.status === 'delivered' ? 'completed' : 'processing'}">${l.status || '?'}</span></td>
        <td style="font-family:var(--mono);font-size:10.5px;color:var(--text-faint);">${new Date(l.ts).toLocaleTimeString()}</td>
      </tr>`).join('')}
      </tbody>
    </table>`;
}

// ════════════════════════════════════════════════════════════════
//  UTILS
// ════════════════════════════════════════════════════════════════
function escapeHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ════════════════════════════════════════════════════════════════
//  FORM PERSISTENCE  (survive navigation away-and-back)
// ════════════════════════════════════════════════════════════════
const FORM_FIELDS = [
  'rawBrief', 'campaignTitle', 'workspaceId',
  'protName', 'protLook', 'numEpisodes',
];

function saveFormFields() {
  const saved = {};
  FORM_FIELDS.forEach(id => {
    const el = document.getElementById(id);
    if (el) saved[id] = el.value;
  });
  localStorage.setItem('cv_form_draft', JSON.stringify(saved));
}

function restoreFormFields() {
  try {
    const saved = JSON.parse(localStorage.getItem('cv_form_draft') || '{}');
    FORM_FIELDS.forEach(id => {
      const el = document.getElementById(id);
      if (el && saved[id] != null) el.value = saved[id];
    });
  } catch(_) {}
}

// Attach listeners to persist on every change
FORM_FIELDS.forEach(id => {
  const el = document.getElementById(id);
  if (el) {
    el.addEventListener('input', saveFormFields);
    el.addEventListener('change', saveFormFields);
  }
});

// Restore saved values immediately
restoreFormFields();


// ════════════════════════════════════════════════════════════════
//  INIT
// ════════════════════════════════════════════════════════════════
checkApiStatus();
setInterval(checkApiStatus, 15000);

// Keyboard shortcut
document.addEventListener('keydown', e => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
    const btn = document.getElementById('generateBtn');
    if (!btn.disabled) generateCampaign();
  }
});
