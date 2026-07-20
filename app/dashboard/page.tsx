"use client";

import { useAuth } from "@clerk/nextjs";
import Script from "next/script";
import { useEffect, useRef, memo } from "react";

/**
 * Convertale operator dashboard.
 *
 * This route replaces the old standalone `dashboard.html` file that used to
 * sit at the project root, completely disconnected from the Next.js App
 * Router (so it was never reachable at a real URL, was never protected by
 * Clerk's `proxy.ts` middleware, called a hardcoded `http://localhost:8000`,
 * hit `/healthz` when the API only ever exposed `/health`, and never sent
 * an Authorization header despite `/api/campaigns` requiring one).
 *
 * The markup/CSS/JS are kept close to the original (now served from
 * `/dashboard/dashboard.css` and `/dashboard/dashboard.js`) rather than
 * hand-rewritten line-by-line into JSX, to avoid introducing transcription
 * bugs into a fairly large, already-working UI. The two real defects
 * (wrong health endpoint, missing auth header) are fixed in the JS file
 * itself. This page's job is just to: mount the markup, expose the live
 * API base URL and a Clerk-backed token getter as `window` globals the
 * script reads, and load the script after the DOM is in place.
 */

// Memoized sub-component to ensure React never re-renders the injected DOM,
// protecting form values and input state from being reset on parent re-renders.
const StaticDashboard = memo(() => {
  return (
    <>
      <link rel="stylesheet" href="/dashboard/dashboard.css" />
      {/* eslint-disable-next-line react/no-danger */}
      <div dangerouslySetInnerHTML={{ __html: DASHBOARD_BODY_HTML }} />
      <Script
        id="convertale-dashboard-script"
        src="/dashboard/dashboard.js"
        strategy="afterInteractive"
      />
    </>
  );
});
StaticDashboard.displayName = "StaticDashboard";

export default function DashboardPage() {
  const { getToken } = useAuth();
  const getTokenRef = useRef(getToken);

  // Keep the ref up-to-date with the latest getToken function from Clerk
  useEffect(() => {
    getTokenRef.current = getToken;
  }, [getToken]);

  useEffect(() => {
    (window as unknown as Record<string, unknown>).__CONVERTALE_API_URL__ =
      process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080";
    
    // Set a stable global token getter that reads from the mutable ref
    (window as unknown as Record<string, unknown>).__CONVERTALE_GET_TOKEN__ = async () => {
      try {
        return await getTokenRef.current();
      } catch {
        return null;
      }
    };
  }, []);

  return <StaticDashboard />;
}

// Static markup extracted from the original dashboard.html <body>. Kept as
// a single injected block (rather than transcribed JSX) so the existing
// dashboard.js — which addresses elements by id/class — keeps working
// unmodified. See public/dashboard/dashboard.js for the interactive logic.
const DASHBOARD_BODY_HTML = String.raw`
<!-- ── NAV ── -->
<nav>
  <div class="nav-brand">
    <div class="logo-mark">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polygon points="5 3 19 12 5 21 5 3"/>
      </svg>
    </div>
    <span>Conver<em>tale</em></span>
  </div>
  <div class="nav-pills">
    <div class="pill active" onclick="showView('studio')">Studio</div>
    <div class="pill" onclick="showView('campaigns')">Campaigns</div>
    <div class="pill" onclick="showView('leads')">Leads</div>
  </div>
  <div class="nav-status">
    <div class="status-dot" id="statusDot"></div>
    <span id="statusText">Connecting…</span>
  </div>
</nav>

<!-- ── WRAP ── -->
<div class="wrap" id="appWrap">

  <!-- STUDIO VIEW -->
  <div id="view-studio">
    <!-- Stats -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-label">Campaigns</div>
        <div class="stat-value" id="statCampaigns">0</div>
        <div class="stat-sub">Total projects</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Episodes</div>
        <div class="stat-value" id="statEpisodes">0</div>
        <div class="stat-sub">Generated</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Leads Captured</div>
        <div class="stat-value gold" id="statLeads">0</div>
        <div class="stat-sub">Cliffhanger gate</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Identity Score</div>
        <div class="stat-value accent" id="statIdentity">—</div>
        <div class="stat-sub">Cross-episode avg.</div>
      </div>
    </div>

    <div class="grid">
      <!-- LEFT: commission panel -->
      <div>
        <div class="card">
          <div class="card-head">
            <div class="card-title"><span class="idx">01</span> Commission Campaign</div>
          </div>
          <div class="card-body">
            <div class="key-alert">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              <span>Make sure <code>QWEN_API_KEY</code> is set in your <code>.env</code> file. The API endpoint is <code>http://localhost:8000</code>.</span>
            </div>
            <div class="form-group">
              <label class="field-label" for="rawBrief">Brand Brief</label>
              <textarea id="rawBrief" rows="4" placeholder="e.g. We sell premium cold brew coffee. Our target is busy professionals who skip breakfast. Create a short drama showing a hero product moment…"></textarea>
            </div>
            <div class="form-group">
              <label class="field-label" for="campaignTitle">Campaign Title</label>
              <input type="text" id="campaignTitle" placeholder="e.g. Morning Rush – ColdBrew Launch" />
            </div>
            <div class="form-group">
              <label class="field-label" for="workspaceId">Workspace ID</label>
              <input type="text" id="workspaceId" value="00000000-0000-0000-0000-000000000001" />
            </div>
            <div class="form-group">
              <label class="field-label">Protagonist</label>
              <div class="row-2">
                <div>
                  <input type="text" id="protName" placeholder="Name (e.g. Mei)" />
                </div>
                <div>
                  <input type="number" id="numEpisodes" value="2" min="1" max="6" />
                </div>
              </div>
              <div style="margin-top:6px">
                <input type="text" id="protLook" placeholder="Locked appearance (e.g. 30s woman, short black bob, charcoal trench coat…)" />
              </div>
              <!-- Character Image Upload Section -->
              <div class="character-upload-section" style="margin-top:12px;padding:12px;background:var(--surface-2);border-radius:8px;border:1px dashed var(--border);">
                <label class="field-label" style="margin-bottom:8px;display:flex;align-items:center;gap:6px;">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                  Character Reference Image (Optional)
                </label>
                <div class="upload-area" id="characterUploadArea" style="position:relative;">
                  <input type="file" id="characterImage" accept="image/*" style="display:none;" onchange="handleCharacterImageSelect(this)" />
                  <div class="upload-placeholder" id="uploadPlaceholder" onclick="document.getElementById('characterImage').click()" style="cursor:pointer;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:20px;text-align:center;">
                    <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="var(--text-faint)" stroke-width="1.5" style="margin-bottom:8px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>
                    <div style="font-size:12px;color:var(--text-faint);">Click to upload or drag and drop</div>
                    <div style="font-size:10px;color:var(--text-faint);margin-top:4px;">PNG, JPG up to 5MB</div>
                  </div>
                  <div class="upload-preview" id="uploadPreview" style="display:none;">
                    <img id="previewImage" src="" alt="Character preview" style="max-width:100%;max-height:150px;border-radius:6px;display:block;margin:0 auto;" />
                    <button class="btn btn-secondary" onclick="removeCharacterImage(event)" style="margin-top:8px;font-size:11px;padding:4px 10px;">Remove</button>
                  </div>
                </div>
              </div>
            </div>
            <button class="btn btn-primary" id="generateBtn" onclick="generateCampaign()">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 3l14 9-14 9V3z"/></svg>
              Generate Campaign
            </button>
            <div id="generateResult" style="margin-top:10px;font-family:var(--mono);font-size:12px;color:var(--text-faint);display:none;"></div>
          </div>
        </div>

        <!-- Agent Pipeline -->
        <div class="card">
          <div class="card-head">
            <div class="card-title"><span class="idx">02</span> Agent Pipeline</div>
          </div>
          <div class="card-body">
            <div class="rail" id="agentRail"></div>
          </div>
        </div>

        <!-- Live Activity -->
        <div class="card">
          <div class="card-head">
            <div class="card-title"><span class="idx">03</span> Live Activity</div>
            <button class="btn btn-secondary" onclick="clearStream()" style="padding:4px 10px;font-size:11px;">Clear</button>
          </div>
          <div class="card-body">
            <div class="stream" id="activityStream">
              <div class="stream-empty">Awaiting pipeline events…</div>
            </div>
          </div>
        </div>

        <!-- Lead Gate Tester -->
        <div class="card">
          <div class="card-head">
            <div class="card-title"><span class="idx">04</span> Test Cliffhanger Gate</div>
          </div>
          <div class="card-body">
            <p style="font-size:12.5px;color:var(--text-faint);margin-bottom:12px;">Simulate a viewer entering their email to unlock the next episode.</p>
            <div class="row-2" style="margin-bottom:10px;">
              <input type="text" id="gateProjectId" placeholder="Project ID (UUID)" />
              <input type="text" id="gateEpisodeId" placeholder="Episode ID (UUID)" />
            </div>
            <div class="gate-form">
              <input type="text" id="gateEmail" placeholder="viewer@example.com" />
              <button class="btn btn-secondary" onclick="testGate()">Unlock</button>
            </div>
            <div class="gate-result" id="gateResult"></div>
          </div>
        </div>
      </div>

      <!-- RIGHT: monitor wall -->
      <div>
        <!-- Series Bible -->
        <div class="card">
          <div class="card-head">
            <div class="card-title"><span class="idx">05</span> Series Bible</div>
            <span style="font-family:var(--mono);font-size:10.5px;color:var(--text-faint)" id="bibleSeriesId"></span>
          </div>
          <div class="card-body">
            <div id="bibleContent">
              <div class="bible-empty">No active series. Commission a campaign to lock the protagonist's appearance and build the Series Bible.</div>
            </div>
          </div>
        </div>

        <!-- Episodes -->
        <div class="card">
          <div class="card-head">
            <div class="card-title"><span class="idx">06</span> Episodes</div>
            <div style="display:flex;gap:6px">
              <button class="btn btn-secondary" onclick="refreshEpisodes()" style="padding:5px 10px;font-size:11px;">↻ Refresh</button>
            </div>
          </div>
          <div class="card-body">
            <div id="episodeGallery">
              <div class="gallery-empty">Rendered episodes will appear here as the studio completes them.</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- CAMPAIGNS VIEW -->
  <div id="view-campaigns" style="display:none">
    <div class="card">
      <div class="card-head">
        <div class="card-title"><span class="idx">01</span> All Campaigns</div>
        <button class="btn btn-secondary" onclick="loadCampaigns()" style="padding:5px 10px;font-size:11px;">↻ Refresh</button>
      </div>
      <div class="card-body">
        <div id="campaignsList" style="color:var(--text-faint);font-size:13px;">No campaigns yet.</div>
      </div>
    </div>
  </div>

  <!-- LEADS VIEW -->
  <div id="view-leads" style="display:none">
    <div class="card">
      <div class="card-head">
        <div class="card-title"><span class="idx">01</span> Lead Capture Log</div>
      </div>
      <div class="card-body">
        <div id="leadsList" style="color:var(--text-faint);font-size:13px;">No leads captured yet. Test the Cliffhanger gate from the Studio view.</div>
      </div>
    </div>
  </div>

</div><!-- /wrap -->

`;
