// ════════════════════════════════════════════════════════════════
//  CONFIG
// ════════════════════════════════════════════════════════════════
const API = window.__CONVERTALE_API_URL__ || 'http://127.0.0.1:8000';

async function authHeaders(extra) {
  const token = window.__CONVERTALE_GET_TOKEN__ ? await window.__CONVERTALE_GET_TOKEN__() : null;
  return { ...(extra || {}), ...(token ? { Authorization: `Bearer ${token}` } : {}) };
}

// ════════════════════════════════════════════════════════════════
//  CHARACTER LOCK + LOGO UI — self-contained, no hand-written markup
//  ────────────────────────────────────────────────────────────
//  Add ONE empty mount point anywhere in your commissioning form:
//    <div id="characterLockPanel"></div>
//  injectCharacterLockPanel() (called from initDashboard) builds the
//  primary/secondary character fields and the brand-logo field into it
//  and injects their scoped styles once — same element IDs as before
//  (#primaryCharName, #primaryCharFile, #primaryCharPreview, #logoFile,
//  #logoPreview, etc.), so uploadCharacterSlot/uploadLogo/generateCampaign
//  below need no changes at all.
//  If markup with those exact IDs already exists somewhere on the page
//  (e.g. you'd already hand-written it), injection is skipped so IDs
//  never collide — see injectCharacterLockPanel. Provide the mount div
//  XOR your own markup, not both.
//  Manual recovery (only needs to be visible/enabled once a draft
//  project exists but hasn't started — see updateStartButtonState):
//    #startPipelineBtn     <button onclick="startPipeline()">
//  Everything else (rawBrief, campaignTitle, workspaceId, numEpisodes,
//  generateBtn, generateResult, bibleContent, bibleSeriesId,
//  episodeGallery, agentRail, activityStream, statusDot, statusText,
//  stat{Campaigns,Leads,Episodes}, gate*, campaignsList, leadsList)
//  is unchanged from before.
// ────────────────────────────────────────────────────────────────
//  LOGO INTEGRITY CONTRACT — read before touching anything logo-related.
//  The brand logo is the one asset in this app that must reach the final
//  video as literal, unaltered pixels: never resampled through a canvas,
//  never re-encoded, never routed through any generative/i2v/diffusion
//  step (unlike character refs, which are *meant* to condition generation
//  — see uploadCharacterSlot). End to end:
//    1. Here: the raw File object is sent untouched in FormData (no
//       canvas draw, no client-side resize/compress) — see uploadLogo.
//    2. Server (routers/brand_assets.py): writes the uploaded bytes to
//       disk as-is, no PIL/Pillow re-encode.
//    3. Compositing (agents/production/assembly.py AssemblyAgent): ffmpeg
//       scales the logo with `scale=iw*0.16:-1`, which preserves aspect
//       ratio (the -1 means "compute height from width automatically"),
//       then overlays it — never `scale=W:H`, which would stretch it.
//  The one place distortion CAN sneak in is the preview: object-fit:cover
//  crops to fill a box without stretching, which is fine for a character
//  headshot thumbnail but wrong for a logo (a wide wordmark would lose
//  its edges). That's why logo previews below use object-fit:contain —
//  the whole mark, uncropped and unstretched, every time. Don't change
//  LOGO_PREVIEW_FIT to 'cover' without re-reading this note.
// ════════════════════════════════════════════════════════════════

// ════════════════════════════════════════════════════════════════
//  AGENTS
// ════════════════════════════════════════════════════════════════
const AGENTS = [
  { key: 'intake',      name: 'Brand Intake',     role: 'Extracts structured brief from raw brief',       icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5.586a1 1 0 0 1 .707.293l5.414 5.414A1 1 0 0 1 20 9.414V19a2 2 0 0 1-2 2z' },
  { key: 'writers',     name: 'Writers Room',     role: 'Generates multi-episode cliffhanger arc',        icon: 'M4 20h4L19 9l-4-4L4 16v4zM14 6l4 4' },
  { key: 'storyboard',  name: 'Storyboard',       role: 'Breaks synopsis into shot sequences',            icon: 'M4 5h7v6H4zM13 5h7v6h-7zM4 13h7v6H4zM13 13h7v6h-7z' },
  { key: 'continuity',  name: 'Continuity Gate',  role: 'Validates narrative consistency',                icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0 1 12 2.944a11.955 11.955 0 0 1-8.618 3.04A12.02 12.02 0 0 0 3 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z' },
  { key: 'video',       name: 'Cinematographer',  role: 'Renders shots via Wan (i2v when a character is locked)', icon: 'M3 8a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8zM16 10l5-3v10l-5-3' },
  { key: 'critic',      name: 'Visual Critic',    role: 'Judges each shot against locked reference stills', icon: 'M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7zM12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6z' },
  { key: 'assembly',    name: 'Editor',           role: 'ffmpeg concat + subtitle burn-in + logo watermark', icon: 'M6 9a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM6 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM8.5 7.5L20 18M8.5 16.5L20 6' },
];

// DOM refs — assigned once the DOM is ready
let railEl, streamEl, dot, statusText;
const agentNodes = {};

let currentProjectId = null;
let episodePollTimer = null;
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
function log(msg, cls='') {
  if (!streamEl) return;
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
  if (!streamEl) return;
  streamEl.innerHTML = '<div class="stream-empty">Stream cleared.</div>';
}

// ════════════════════════════════════════════════════════════════
//  API STATUS CHECK
// ════════════════════════════════════════════════════════════════
async function checkApiStatus() {
  if (!dot || !statusText) return false;
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
  const statCampaigns = document.getElementById('statCampaigns');
  const statLeads = document.getElementById('statLeads');
  if (statCampaigns) statCampaigns.textContent = campaigns.length;
  if (statLeads) statLeads.textContent = leads.length;
}

// ════════════════════════════════════════════════════════════════
//  CHARACTER LOCK + LOGO — panel injection (markup + scoped styles)
//  ────────────────────────────────────────────────────────────
//  Built directly on your real dashboard.css: reuses .form-group,
//  label.field-label, .field-hint, .char-thumbnail, .btn/.btn-secondary,
//  and the --surface/--border/--accent/--mono tokens verbatim, so this
//  sits inside the existing "01 COMMISSION CAMPAIGN" card as just more
//  form-groups — not a visually separate box. Only truly new bits (file
//  input styling, the logo frame, tag pills, inline errors) get their
//  own small `.charlock-*` rules below.
// ════════════════════════════════════════════════════════════════
const _PANEL_MOUNT_ID = 'characterLockPanel';
const _PANEL_STYLE_ID = 'charlock-injected-styles';

const _PANEL_CSS = `
.charlock-uploadrow { display: flex; gap: 14px; align-items: flex-start; margin-top: 6px; }
.charlock-fields { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 8px; }
.charlock-fields textarea { min-height: 56px; }
.charlock-filerow { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.charlock-filebtn { position: relative; overflow: hidden; }
.charlock-filebtn input[type="file"] { position: absolute; inset: 0; opacity: 0; cursor: pointer; }
.charlock-tag {
  font-family: var(--mono); font-size: 9px; letter-spacing: .1em; text-transform: uppercase;
  color: var(--text-faint); border: 1px solid var(--border-2); border-radius: 99px;
  padding: 1px 7px; margin-left: 6px; font-weight: 400;
}
.charlock-tag.required { color: var(--accent-2); border-color: var(--accent); }
.charlock-error {
  display: none; font-family: var(--mono); font-size: 11px; color: var(--red);
}
/* Logo frame: deliberately NOT the same shape as .char-thumbnail. A
   character ref can be usefully cropped to a portrait card; a logo must
   never be — this box is wide and uses object-fit:contain (set inline by
   wirePreview) so the whole mark shows, uncropped and unstretched, every
   time. The dashed inset is a visual promise of that, not decoration. */
.charlock-logo-frame {
  width: 100%; height: 108px; margin-top: 6px;
  border-radius: 10px; background: var(--surface-3); border: 1px dashed var(--border-2);
  overflow: hidden; display: flex; align-items: center; justify-content: center;
  position: relative;
}
.charlock-logo-frame::after {
  content: ""; position: absolute; inset: 6px;
  border: 1px dashed var(--accent-glow); border-radius: 6px; pointer-events: none;
}
`;

// Same element IDs generateCampaign()/uploadCharacterSlot()/uploadLogo()
// already expect — this just builds them instead of requiring hand-written
// HTML. Reuses .char-thumbnail (already used for locked references in the
// Series Bible) so the pre-upload preview and the post-lock card look
// identical — no separate visual language for "picking" vs. "locked".
const _PANEL_HTML = `
<div class="form-group">
  <label class="field-label">Primary character <span class="charlock-tag required">Required</span></label>
  <div class="charlock-uploadrow">
    <div class="char-thumbnail" id="primaryCharPreview"><div class="ph-text">No image yet</div></div>
    <div class="charlock-fields">
      <input type="text" id="primaryCharName" placeholder="Character name">
      <textarea id="primaryCharPrompt" placeholder="Appearance notes (optional) — the reference image is the real anchor, this just adds detail the image alone might not carry"></textarea>
      <div class="charlock-filerow">
        <label class="btn btn-secondary charlock-filebtn">Choose reference image
          <input type="file" id="primaryCharFile" accept="image/png,image/jpeg,image/webp">
        </label>
        <span class="field-hint" style="margin:0;">PNG / JPEG / WEBP, up to 8MB</span>
      </div>
      <div class="charlock-error" id="primaryCharError"></div>
    </div>
  </div>
</div>
<div class="form-group">
  <label class="field-label">Secondary character <span class="charlock-tag">Optional</span></label>
  <div class="charlock-uploadrow">
    <div class="char-thumbnail" id="secondaryCharPreview"><div class="ph-text">No image yet</div></div>
    <div class="charlock-fields">
      <input type="text" id="secondaryCharName" placeholder="Character name">
      <textarea id="secondaryCharPrompt" placeholder="Appearance notes (optional)"></textarea>
      <div class="charlock-filerow">
        <label class="btn btn-secondary charlock-filebtn">Choose reference image
          <input type="file" id="secondaryCharFile" accept="image/png,image/jpeg,image/webp">
        </label>
        <span class="field-hint" style="margin:0;">Leave both fields empty to skip</span>
      </div>
      <div class="charlock-error" id="secondaryCharError"></div>
    </div>
  </div>
</div>
<div class="form-group">
  <label class="field-label">Brand logo <span class="charlock-tag">Optional</span></label>
  <div class="field-hint">Composited as a small corner watermark on every episode — shown below exactly as it will appear: never cropped, never stretched.</div>
  <div class="charlock-logo-frame" id="logoPreview"><div class="ph-text">No logo yet</div></div>
  <div class="charlock-filerow" style="margin-top:8px;">
    <label class="btn btn-secondary charlock-filebtn">Choose logo file
      <input type="file" id="logoFile" accept="image/png,image/jpeg,image/webp">
    </label>
    <span class="field-hint" style="margin:0;">PNG with transparency recommended · up to 5MB</span>
  </div>
  <div class="charlock-error" id="logoError"></div>
</div>
`;

// Builds the character-lock + logo fields into #characterLockPanel. Safe
// to call even if that mount isn't on the page (no-op), and safe to call
// on a page that already has hand-written markup with these IDs (skips,
// so IDs never collide — see the header comment for the XOR contract).
function injectCharacterLockPanel() {
  const mount = document.getElementById(_PANEL_MOUNT_ID);
  if (!mount) return;
  if (document.getElementById('primaryCharFile')) return; // already present somewhere — don't duplicate

  if (!document.getElementById(_PANEL_STYLE_ID)) {
    const style = document.createElement('style');
    style.id = _PANEL_STYLE_ID;
    style.textContent = _PANEL_CSS;
    document.head.appendChild(style);
  }
  mount.innerHTML = _PANEL_HTML;
}

// ════════════════════════════════════════════════════════════════
//  CHARACTER LOCK + LOGO — local previews (instant, before upload)
// ════════════════════════════════════════════════════════════════
const _ACCEPTED_IMAGE_TYPES = new Set(['image/png', 'image/jpeg', 'image/webp']);

// Mirrors the server-side caps (routers/characters.py, routers/brand_assets.py)
// so a bad file gets caught instantly instead of after a round trip that
// leaves a half-finished draft project behind.
const _MAX_BYTES = { character: 8 * 1024 * 1024, logo: 5 * 1024 * 1024 };

// Every preview <img> we create from a local file gets an object URL —
// these are never garbage-collected on their own, so we track one per
// preview slot and revoke the previous one before minting a new one
// (re-picking a file repeatedly would otherwise leak a blob URL each time).
const _previewUrls = {};

function _clearPreviewSlot(previewId, errorId) {
  if (_previewUrls[previewId]) {
    URL.revokeObjectURL(_previewUrls[previewId]);
    delete _previewUrls[previewId];
  }
  const preview = document.getElementById(previewId);
  if (preview) preview.innerHTML = '';
  const errEl = errorId && document.getElementById(errorId);
  if (errEl) { errEl.textContent = ''; errEl.style.display = 'none'; }
}

function _showSlotError(previewId, errorId, message) {
  _clearPreviewSlot(previewId, errorId);
  const errEl = errorId && document.getElementById(errorId);
  if (errEl) { errEl.textContent = message; errEl.style.display = 'block'; }
  else console.warn(message); // no dedicated error element wired up — don't fail silently
}

function validateImageFile(file, maxBytes) {
  if (!_ACCEPTED_IMAGE_TYPES.has(file.type)) {
    return `Unsupported file type "${file.type || 'unknown'}" — use PNG, JPEG, or WEBP.`;
  }
  if (file.size > maxBytes) {
    return `File is ${(file.size / (1024 * 1024)).toFixed(1)}MB, max is ${(maxBytes / (1024 * 1024)).toFixed(0)}MB.`;
  }
  return null;
}

// fit: 'cover' crops to fill the box (fine for a square character
// headshot). 'contain' shows the whole image with no cropping and no
// stretching (required for the logo — see LOGO INTEGRITY CONTRACT above).
// This only ever changes CSS on the preview <img>; the File object handed
// to uploadLogo/uploadCharacterSlot below is never touched by this function.
function wirePreview(fileInputId, previewId, { fit = 'cover', maxBytes, errorId } = {}) {
  const input = document.getElementById(fileInputId);
  const preview = document.getElementById(previewId);
  if (!input || !preview) return;
  input.addEventListener('change', () => {
    const file = input.files && input.files[0];
    if (!file) { _clearPreviewSlot(previewId, errorId); return; }

    const problem = validateImageFile(file, maxBytes ?? _MAX_BYTES.character);
    if (problem) {
      _showSlotError(previewId, errorId, problem);
      input.value = ''; // don't let an invalid file linger and get submitted anyway
      return;
    }

    if (_previewUrls[previewId]) URL.revokeObjectURL(_previewUrls[previewId]);
    const url = URL.createObjectURL(file);
    _previewUrls[previewId] = url;

    const errEl = errorId && document.getElementById(errorId);
    if (errEl) { errEl.textContent = ''; errEl.style.display = 'none'; }

    const bg = fit === 'contain'
      ? 'background:repeating-conic-gradient(#2a2a35 0% 25%, #22222b 0% 50%) 0 0/16px 16px;' // reveals transparent PNGs honestly, doesn't imply the logo has a color it doesn't
      : '';
    preview.innerHTML = `<img src="${url}" alt="preview" style="width:100%;height:100%;object-fit:${fit};border-radius:inherit;${bg}">`;
  });
}

// Restores the currently-locked logo from the server (e.g. after a page
// view switch, or simply to let the user visually confirm the exact file
// the pipeline has on disk — the same bytes that will be composited onto
// every episode, per the LOGO INTEGRITY CONTRACT above).
async function refreshLogo(projectId) {
  const preview = document.getElementById('logoPreview');
  if (!preview || !projectId) return;
  try {
    const res = await fetch(`${API}/api/projects/${projectId}/logo`, { headers: await authHeaders() });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (!data.logo_url) { preview.innerHTML = ''; return; }
    // Remote URL — no object URL involved, nothing to revoke.
    preview.innerHTML = `<img src="${escapeHtml(data.logo_url)}" alt="brand logo" style="width:100%;height:100%;object-fit:contain;border-radius:inherit;background:repeating-conic-gradient(#2a2a35 0% 25%, #22222b 0% 50%) 0 0/16px 16px;">`;
  } catch (e) {
    console.warn(`Couldn't refresh logo preview: ${e.message}`);
  }
}

// One upload helper shared by primary/secondary character slots and the
// logo — same multipart pattern, different endpoint/field name.
async function uploadCharacterSlot(projectId, slot, name, appearancePrompt, file) {
  const form = new FormData();
  form.append('name', name);
  form.append('appearance_prompt', appearancePrompt || '');
  form.append('image', file);
  const res = await fetch(`${API}/api/projects/${projectId}/characters/${slot}`, {
    method: 'POST',
    headers: await authHeaders(), // do NOT set Content-Type — browser sets the multipart boundary
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(`${slot} character: ${err.detail || `HTTP ${res.status}`}`);
  }
  return res.json();
}

async function uploadLogo(projectId, file) {
  const form = new FormData();
  form.append('logo', file);
  const res = await fetch(`${API}/api/projects/${projectId}/logo`, {
    method: 'POST',
    headers: await authHeaders(),
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(`logo: ${err.detail || `HTTP ${res.status}`}`);
  }
  return res.json();
}

// ════════════════════════════════════════════════════════════════
//  GENERATE CAMPAIGN
// ════════════════════════════════════════════════════════════════
function updateStartButtonState(projectId, canStart) {
  const btn = document.getElementById('startPipelineBtn');
  if (!btn) return;
  btn.style.display = canStart ? 'inline-flex' : 'none';
  btn.disabled = !canStart;
  btn.dataset.projectId = projectId || '';
}

// Manual fallback: if a draft project exists (created but not yet
// started, e.g. because a character/logo upload failed partway), this
// lets the user retry starting it without re-creating the campaign or
// re-uploading whatever already succeeded.
async function startPipeline() {
  const btn = document.getElementById('startPipelineBtn');
  const projectId = (btn && btn.dataset.projectId) || currentProjectId;
  if (!projectId) return;
  try {
    const res = await fetch(`${API}/api/projects/${projectId}/start`, {
      method: 'POST',
      headers: await authHeaders(),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
    log(data.already_started ? `Pipeline already running for ${projectId}` : `Pipeline started for ${projectId}`, 'ok');
    updateStartButtonState(null, false);
    await refreshCharacterBible(projectId);
    await refreshLogo(projectId);
    startEpisodePolling(projectId);
  } catch (e) {
    log(`Couldn't start pipeline: ${e.message}`, 'err');
  }
}

async function generateCampaign() {
  const btn = document.getElementById('generateBtn');
  const resultEl = document.getElementById('generateResult');
  const rawBrief = document.getElementById('rawBrief').value.trim();
  const title = document.getElementById('campaignTitle').value.trim();
  const workspaceId = document.getElementById('workspaceId').value.trim();
  const numEp = parseInt(document.getElementById('numEpisodes').value, 10) || 2;

  const primaryName = (document.getElementById('primaryCharName')?.value || '').trim();
  const primaryPrompt = (document.getElementById('primaryCharPrompt')?.value || '').trim();
  const primaryFile = document.getElementById('primaryCharFile')?.files?.[0] || null;

  const secondaryName = (document.getElementById('secondaryCharName')?.value || '').trim();
  const secondaryPrompt = (document.getElementById('secondaryCharPrompt')?.value || '').trim();
  const secondaryFile = document.getElementById('secondaryCharFile')?.files?.[0] || null;

  const logoFile = document.getElementById('logoFile')?.files?.[0] || null;

  if (!rawBrief) { log('⚠ Please enter a brand brief', 'err'); return; }
  if (!primaryName || !primaryFile) {
    log('⚠ Primary character needs both a name and a reference image', 'err');
    return;
  }
  // Secondary is optional as a whole, but if either half is filled in,
  // require both — a name with no image (or vice versa) can't be locked.
  if ((secondaryName && !secondaryFile) || (!secondaryName && secondaryFile)) {
    log('⚠ Secondary character needs both a name and an image, or leave both empty', 'err');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<div class="spinner"></div> Commissioning…';
  resultEl.style.display = 'none';
  updateStartButtonState(null, false);
  resetRail();
  if (dot) dot.className = 'status-dot running';
  if (statusText) statusText.textContent = 'Commissioning…';

  log(`Commissioning "${title || 'New Campaign'}" · ${numEp} episodes (target — Writers Room sets the actual count)`, 'sys');

  let projectId = null;

  try {
    // 1) Create the project WITHOUT starting the pipeline yet. The
    // pipeline reads locked characters/logo the moment episode 1 starts
    // storyboarding — dispatching before uploads finish would race it.
    setAgent('intake');
    log('Creating campaign (draft — pipeline not started yet)…');
    const createRes = await fetch(`${API}/api/campaigns`, {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({
        raw_brief: rawBrief,
        title: title || 'New Campaign',
        workspace_id: workspaceId,
        autostart: false,
      }),
    });
    const createData = await createRes.json().catch(() => ({}));
    if (!createRes.ok) throw new Error(createData.detail || `HTTP ${createRes.status}`);
    projectId = createData.project_id;
    currentProjectId = projectId;
    updateStartButtonState(projectId, true); // manual recovery available from this point on

    // 2) Lock the primary character (required).
    log(`Locking primary character "${primaryName}"…`);
    await uploadCharacterSlot(projectId, 'primary', primaryName, primaryPrompt, primaryFile);

    // 3) Lock the secondary character (optional).
    if (secondaryName && secondaryFile) {
      log(`Locking secondary character "${secondaryName}"…`);
      await uploadCharacterSlot(projectId, 'secondary', secondaryName, secondaryPrompt, secondaryFile);
    }

    // 4) Upload the brand logo (optional).
    if (logoFile) {
      log('Uploading brand logo…');
      await uploadLogo(projectId, logoFile);
    }

    // 5) Everything that needed to exist before rendering starts now
    // does — dispatch the pipeline for real.
    log('Starting pipeline…');
    const startRes = await fetch(`${API}/api/projects/${projectId}/start`, {
      method: 'POST',
      headers: await authHeaders(),
    });
    const startData = await startRes.json().catch(() => ({}));
    if (!startRes.ok) throw new Error(startData.detail || `HTTP ${startRes.status}`);
    updateStartButtonState(null, false); // started cleanly, hide the manual fallback

    // Simulated step ticker for the agent rail — the pipeline itself runs
    // in the background and is tracked for real via episode polling below;
    // this just gives immediate visual feedback that something is moving.
    const steps = [
      { key: 'writers',    msg: 'Writers Room crafting story arc…' },
      { key: 'storyboard', msg: 'Storyboarding shots (characters tagged per shot)…' },
      { key: 'continuity', msg: 'Continuity Gate checking narrative…' },
      { key: 'video',      msg: 'Queueing Wan renders (i2v for locked characters)…' },
      { key: 'critic',     msg: 'Visual Critic checking shots against reference stills…' },
      { key: 'assembly',   msg: 'Editor standing by for assembly…' },
    ];
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

    completeRail();
    campaigns.push({ id: projectId, title: title || 'New Campaign', created: new Date().toISOString() });
    localStorage.setItem('cv_campaigns', JSON.stringify(campaigns));
    updateStats();

    const statEpisodes = document.getElementById('statEpisodes');
    if (statEpisodes) statEpisodes.textContent = numEp;
    const bibleSeriesId = document.getElementById('bibleSeriesId');
    if (bibleSeriesId) bibleSeriesId.textContent = projectId?.slice(0,8) || '';

    resultEl.style.display = 'block';
    resultEl.style.color = 'var(--green)';
    resultEl.textContent = `✓ Project ${projectId} queued. Background pipeline started.`;
    log(`Campaign started: ${projectId}`, 'ok');
    if (dot) dot.className = 'status-dot online';
    if (statusText) statusText.textContent = 'Pipeline queued';

    await refreshCharacterBible(projectId);
    await refreshLogo(projectId);
    startEpisodePolling(projectId);
  } catch (e) {
    log(`Error: ${e.message}`, 'err');
    if (dot) dot.className = 'status-dot error';
    if (statusText) statusText.textContent = 'Error';
    resultEl.style.display = 'block';
    resultEl.style.color = 'var(--red)';
    if (projectId) {
      // The draft project exists — nothing is lost. Surface the manual
      // start button so the user can fix the failing step (re-pick a
      // file, check the network tab) and retry without starting over.
      resultEl.textContent = `✗ ${e.message} — project ${projectId} is saved as a draft; fix the issue above and click "Start Pipeline".`;
      updateStartButtonState(projectId, true);
    } else {
      resultEl.textContent = `✗ ${e.message}`;
    }
  }

  btn.disabled = false;
  btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 3l14 9-14 9V3z"/></svg> Generate Campaign`;
}

// ════════════════════════════════════════════════════════════════
//  SERIES BIBLE RENDER — real locked characters, real reference stills
// ════════════════════════════════════════════════════════════════
function characterCardHtml(slotLabel, char) {
  if (!char) {
    return `
      <div class="bible-card bible-card-empty">
        <div class="char-thumbnail"><div class="ph-text">No ${slotLabel} character locked</div></div>
        <div class="char-info"><div class="char-name-row"><span class="char-name" style="opacity:.5">— ${slotLabel} (optional) —</span></div></div>
      </div>`;
  }
  const thumb = char.ref_image_url
    ? `<img src="${escapeHtml(char.ref_image_url)}" alt="${escapeHtml(char.name)}" style="width:100%;height:100%;object-fit:cover;border-radius:inherit;">`
    : `<div class="ph-text">Reference frame appears once locked</div>`;
  return `
    <div class="bible-card">
      <div class="char-thumbnail">${thumb}</div>
      <div class="char-info">
        <div class="char-name-row">
          <span class="char-name">${escapeHtml(char.name)}</span>
          ${char.locked ? `
            <span class="lock-badge">
              <svg viewBox="0 0 24 24" width="9" height="9" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>
              Locked${char.lock_source === 'auto_bootstrap' ? ' (auto)' : ''}
            </span>` : ''}
        </div>
        <div class="char-look"><strong>${escapeHtml(char.appearance_prompt || 'No appearance prompt given — reference image is the anchor.')}</strong></div>
      </div>
    </div>`;
}

async function refreshCharacterBible(projectId) {
  const el = document.getElementById('bibleContent');
  if (!el || !projectId) return;
  try {
    const res = await fetch(`${API}/api/projects/${projectId}/characters`, { headers: await authHeaders() });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const c = data.characters || {};
    el.innerHTML = characterCardHtml('primary', c.primary) + characterCardHtml('secondary', c.secondary);
  } catch (e) {
    el.innerHTML = `<div class="bible-empty">Couldn't load character locks: ${escapeHtml(e.message)}</div>`;
  }
}

// ════════════════════════════════════════════════════════════════
//  EPISODE GALLERY
// ════════════════════════════════════════════════════════════════
async function refreshEpisodes() {
  const gallery = document.getElementById('episodeGallery');
  if (!gallery) return;

  if (!currentProjectId) {
    gallery.innerHTML = `<div style="color:var(--text-faint);font-size:13px;padding:20px 0;text-align:center;">No campaign commissioned yet.</div>`;
    return;
  }

  let data;
  try {
    const res = await fetch(`${API}/api/projects/${currentProjectId}/episodes`, {
      headers: await authHeaders(),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    data = await res.json();
  } catch (e) {
    gallery.innerHTML = `<div style="color:var(--red);font-size:13px;padding:20px 0;text-align:center;">Couldn't load episodes: ${escapeHtml(e.message)}</div>`;
    return;
  }

  const statEpisodes = document.getElementById('statEpisodes');
  if (statEpisodes) statEpisodes.textContent = data.episode_count;

  if (!data.episodes.length) {
    gallery.innerHTML = `<div style="color:var(--text-faint);font-size:13px;padding:20px 0;text-align:center;">Writers Room is still drafting the episode list…</div>`;
    return;
  }

  gallery.innerHTML = `
    <div class="episode-grid">
      ${data.episodes.map((ep, i) => {
        const isDone = ep.status === 'completed' && ep.assembled_video_url;
        const num = String(ep.episode_number ?? i + 1).padStart(2, '0');
        const badge = isDone
          ? `<div class="ep-badge completed">✓ ready</div>`
          : `<div class="ep-badge processing">⏳ ${escapeHtml(ep.status || 'rendering')}</div>`;
        const thumb = isDone
          ? `<video src="${escapeHtml(ep.assembled_video_url)}" controls preload="metadata" style="width:100%;aspect-ratio:9/16;max-height:220px;background:#070810;"></video>`
          : `<div style="width:100%;aspect-ratio:9/16;background:linear-gradient(180deg,#1a1040,#070810);display:flex;align-items:center;justify-content:center;max-height:220px">
               <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="rgba(124,92,252,0.3)" stroke-width="1.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
             </div>`;
        return `
          <div class="ep-card" style="animation-delay:${i * 60}ms">
            ${thumb}
            <div class="ep-card-body">
              <div class="ep-num">Episode ${num}</div>
              <div class="ep-title">${escapeHtml(ep.title || 'Untitled')}</div>
              ${badge}
            </div>
          </div>`;
      }).join('')}
    </div>`;

  const allDone = data.episodes.length > 0 && data.episodes.every(ep => ep.status === 'completed');
  if (allDone && episodePollTimer) {
    clearInterval(episodePollTimer);
    episodePollTimer = null;
    log('All episodes rendered.', 'ok');
  }
}

function startEpisodePolling(projectId) {
  currentProjectId = projectId;
  if (episodePollTimer) clearInterval(episodePollTimer);
  refreshEpisodes();
  episodePollTimer = setInterval(refreshEpisodes, 5000);
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
    if (el) el.style.display = v === name ? 'block' : 'none';
  });
  document.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
  const trigger = (evt && evt.currentTarget) || (typeof event !== 'undefined' && event && event.target);
  if (trigger) trigger.classList.add('active');
  if (name === 'campaigns') loadCampaigns();
  if (name === 'leads') loadLeads();
}

function loadCampaigns() {
  const el = document.getElementById('campaignsList');
  if (!el) return;
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
  if (!el) return;
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
//  FORM PERSISTENCE (text fields only — file inputs can't be restored)
// ════════════════════════════════════════════════════════════════
const FORM_FIELDS = [
  'rawBrief', 'campaignTitle', 'workspaceId', 'numEpisodes',
  'primaryCharName', 'primaryCharPrompt',
  'secondaryCharName', 'secondaryCharPrompt',
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

// ════════════════════════════════════════════════════════════════
//  INIT — DEFERRED UNTIL DOM IS READY
// ════════════════════════════════════════════════════════════════
function initDashboard() {
  railEl = document.getElementById('agentRail');
  streamEl = document.getElementById('activityStream');
  dot = document.getElementById('statusDot');
  statusText = document.getElementById('statusText');

  if (railEl) {
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
  }

  updateStats();
  checkApiStatus();
  setInterval(checkApiStatus, 15000);

  injectCharacterLockPanel();

  wirePreview('primaryCharFile', 'primaryCharPreview', { fit: 'cover', maxBytes: _MAX_BYTES.character, errorId: 'primaryCharError' });
  wirePreview('secondaryCharFile', 'secondaryCharPreview', { fit: 'cover', maxBytes: _MAX_BYTES.character, errorId: 'secondaryCharError' });
  // 'contain', not 'cover' — a logo must never be cropped or stretched,
  // see the LOGO INTEGRITY CONTRACT note near the top of this file.
  wirePreview('logoFile', 'logoPreview', { fit: 'contain', maxBytes: _MAX_BYTES.logo, errorId: 'logoError' });
  updateStartButtonState(null, false);

  FORM_FIELDS.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('input', saveFormFields);
      el.addEventListener('change', saveFormFields);
    }
  });
  restoreFormFields();

  document.addEventListener('keydown', e => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      const btn = document.getElementById('generateBtn');
      if (btn && !btn.disabled) generateCampaign();
    }
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initDashboard);
} else {
  initDashboard();
}