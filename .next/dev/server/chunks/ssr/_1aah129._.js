module.exports = [
"[project]/app/dashboard/page.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>DashboardPage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$16$2e$2$2e$10_$40$babel$2b$core$40$7$2e$_54fe0b4b34f39aa1bf7e10b73832e4f5$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/.pnpm/next@16.2.10_@babel+core@7._54fe0b4b34f39aa1bf7e10b73832e4f5/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f40$clerk$2b$react$40$6$2e$11$2e$3_react$2d$d_67468934040b8a7508984050430fd46a$2f$node_modules$2f40$clerk$2f$react$2f$dist$2f$hooks$2d$BiY5Zgpp$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__$3c$export__b__as__useAuth$3e$__ = __turbopack_context__.i("[project]/node_modules/.pnpm/@clerk+react@6.11.3_react-d_67468934040b8a7508984050430fd46a/node_modules/@clerk/react/dist/hooks-BiY5Zgpp.mjs [app-ssr] (ecmascript) <locals> <export b as useAuth>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$16$2e$2$2e$10_$40$babel$2b$core$40$7$2e$_54fe0b4b34f39aa1bf7e10b73832e4f5$2f$node_modules$2f$next$2f$script$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/.pnpm/next@16.2.10_@babel+core@7._54fe0b4b34f39aa1bf7e10b73832e4f5/node_modules/next/script.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$16$2e$2$2e$10_$40$babel$2b$core$40$7$2e$_54fe0b4b34f39aa1bf7e10b73832e4f5$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/.pnpm/next@16.2.10_@babel+core@7._54fe0b4b34f39aa1bf7e10b73832e4f5/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
"use client";
;
;
;
;
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
 */ // Memoized sub-component to ensure React never re-renders the injected DOM,
// protecting form values and input state from being reset on parent re-renders.
const StaticDashboard = /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$16$2e$2$2e$10_$40$babel$2b$core$40$7$2e$_54fe0b4b34f39aa1bf7e10b73832e4f5$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["memo"])(()=>{
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$16$2e$2$2e$10_$40$babel$2b$core$40$7$2e$_54fe0b4b34f39aa1bf7e10b73832e4f5$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$16$2e$2$2e$10_$40$babel$2b$core$40$7$2e$_54fe0b4b34f39aa1bf7e10b73832e4f5$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Fragment"], {
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$16$2e$2$2e$10_$40$babel$2b$core$40$7$2e$_54fe0b4b34f39aa1bf7e10b73832e4f5$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("link", {
                rel: "stylesheet",
                href: "/dashboard/dashboard.css"
            }, void 0, false, {
                fileName: "[project]/app/dashboard/page.tsx",
                lineNumber: 32,
                columnNumber: 7
            }, ("TURBOPACK compile-time value", void 0)),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$16$2e$2$2e$10_$40$babel$2b$core$40$7$2e$_54fe0b4b34f39aa1bf7e10b73832e4f5$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                dangerouslySetInnerHTML: {
                    __html: DASHBOARD_BODY_HTML
                }
            }, void 0, false, {
                fileName: "[project]/app/dashboard/page.tsx",
                lineNumber: 34,
                columnNumber: 7
            }, ("TURBOPACK compile-time value", void 0)),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$16$2e$2$2e$10_$40$babel$2b$core$40$7$2e$_54fe0b4b34f39aa1bf7e10b73832e4f5$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$16$2e$2$2e$10_$40$babel$2b$core$40$7$2e$_54fe0b4b34f39aa1bf7e10b73832e4f5$2f$node_modules$2f$next$2f$script$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"], {
                id: "convertale-dashboard-script",
                src: "/dashboard/dashboard.js",
                strategy: "afterInteractive"
            }, void 0, false, {
                fileName: "[project]/app/dashboard/page.tsx",
                lineNumber: 35,
                columnNumber: 7
            }, ("TURBOPACK compile-time value", void 0))
        ]
    }, void 0, true);
});
StaticDashboard.displayName = "StaticDashboard";
function DashboardPage() {
    const { getToken } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f40$clerk$2b$react$40$6$2e$11$2e$3_react$2d$d_67468934040b8a7508984050430fd46a$2f$node_modules$2f40$clerk$2f$react$2f$dist$2f$hooks$2d$BiY5Zgpp$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__$3c$locals$3e$__$3c$export__b__as__useAuth$3e$__["useAuth"])();
    const getTokenRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$16$2e$2$2e$10_$40$babel$2b$core$40$7$2e$_54fe0b4b34f39aa1bf7e10b73832e4f5$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useRef"])(getToken);
    // Keep the ref up-to-date with the latest getToken function from Clerk
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$16$2e$2$2e$10_$40$babel$2b$core$40$7$2e$_54fe0b4b34f39aa1bf7e10b73832e4f5$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        getTokenRef.current = getToken;
    }, [
        getToken
    ]);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$16$2e$2$2e$10_$40$babel$2b$core$40$7$2e$_54fe0b4b34f39aa1bf7e10b73832e4f5$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        window.__CONVERTALE_API_URL__ = ("TURBOPACK compile-time value", "http://localhost:8000") || "http://127.0.0.1:8080";
        // Set a stable global token getter that reads from the mutable ref
        window.__CONVERTALE_GET_TOKEN__ = async ()=>{
            try {
                return await getTokenRef.current();
            } catch  {
                return null;
            }
        };
    }, []);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f2e$pnpm$2f$next$40$16$2e$2$2e$10_$40$babel$2b$core$40$7$2e$_54fe0b4b34f39aa1bf7e10b73832e4f5$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(StaticDashboard, {}, void 0, false, {
        fileName: "[project]/app/dashboard/page.tsx",
        lineNumber: 68,
        columnNumber: 10
    }, this);
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
}),
"[project]/node_modules/.pnpm/next@16.2.10_@babel+core@7._54fe0b4b34f39aa1bf7e10b73832e4f5/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

module.exports = __turbopack_context__.r("[project]/node_modules/.pnpm/next@16.2.10_@babel+core@7._54fe0b4b34f39aa1bf7e10b73832e4f5/node_modules/next/dist/server/route-modules/app-page/module.compiled.js [app-ssr] (ecmascript)").vendored['react-ssr'].ReactJsxDevRuntime;
}),
"[project]/node_modules/.pnpm/next@16.2.10_@babel+core@7._54fe0b4b34f39aa1bf7e10b73832e4f5/node_modules/next/dist/server/route-modules/app-page/vendored/contexts/head-manager-context.js [app-ssr] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

module.exports = __turbopack_context__.r("[project]/node_modules/.pnpm/next@16.2.10_@babel+core@7._54fe0b4b34f39aa1bf7e10b73832e4f5/node_modules/next/dist/server/route-modules/app-page/module.compiled.js [app-ssr] (ecmascript)").vendored['contexts'].HeadManagerContext;
}),
"[project]/node_modules/.pnpm/next@16.2.10_@babel+core@7._54fe0b4b34f39aa1bf7e10b73832e4f5/node_modules/next/dist/client/set-attributes-from-props.js [app-ssr] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});
Object.defineProperty(exports, "setAttributesFromProps", {
    enumerable: true,
    get: function() {
        return setAttributesFromProps;
    }
});
const DOMAttributeNames = {
    acceptCharset: 'accept-charset',
    className: 'class',
    htmlFor: 'for',
    httpEquiv: 'http-equiv',
    noModule: 'noModule'
};
const ignoreProps = [
    'onLoad',
    'onReady',
    'dangerouslySetInnerHTML',
    'children',
    'onError',
    'strategy',
    'stylesheets'
];
function isBooleanScriptAttribute(attr) {
    return [
        'async',
        'defer',
        'noModule'
    ].includes(attr);
}
function setAttributesFromProps(el, props) {
    for (const [p, value] of Object.entries(props)){
        if (!props.hasOwnProperty(p)) continue;
        if (ignoreProps.includes(p)) continue;
        // we don't render undefined props to the DOM
        if (value === undefined) {
            continue;
        }
        const attr = DOMAttributeNames[p] || p.toLowerCase();
        if (el.tagName === 'SCRIPT' && isBooleanScriptAttribute(attr)) {
            // Correctly assign boolean script attributes
            // https://github.com/vercel/next.js/pull/20748
            ;
            el[attr] = !!value;
        } else {
            el.setAttribute(attr, String(value));
        }
        // Remove falsy non-zero boolean attributes so they are correctly interpreted
        // (e.g. if we set them to false, this coerces to the string "false", which the browser interprets as true)
        if (value === false || el.tagName === 'SCRIPT' && isBooleanScriptAttribute(attr) && (!value || value === 'false')) {
            // Call setAttribute before, as we need to set and unset the attribute to override force async:
            // https://html.spec.whatwg.org/multipage/scripting.html#script-force-async
            el.setAttribute(attr, '');
            el.removeAttribute(attr);
        }
    }
}
if ((typeof exports.default === 'function' || typeof exports.default === 'object' && exports.default !== null) && typeof exports.default.__esModule === 'undefined') {
    Object.defineProperty(exports.default, '__esModule', {
        value: true
    });
    Object.assign(exports.default, exports);
    module.exports = exports.default;
}
}),
"[project]/node_modules/.pnpm/next@16.2.10_@babel+core@7._54fe0b4b34f39aa1bf7e10b73832e4f5/node_modules/next/dist/client/request-idle-callback.js [app-ssr] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});
0 && (module.exports = {
    cancelIdleCallback: null,
    requestIdleCallback: null
});
function _export(target, all) {
    for(var name in all)Object.defineProperty(target, name, {
        enumerable: true,
        get: all[name]
    });
}
_export(exports, {
    cancelIdleCallback: function() {
        return cancelIdleCallback;
    },
    requestIdleCallback: function() {
        return requestIdleCallback;
    }
});
const requestIdleCallback = typeof self !== 'undefined' && self.requestIdleCallback && self.requestIdleCallback.bind(window) || function(cb) {
    let start = Date.now();
    return self.setTimeout(function() {
        cb({
            didTimeout: false,
            timeRemaining: function() {
                return Math.max(0, 50 - (Date.now() - start));
            }
        });
    }, 1);
};
const cancelIdleCallback = typeof self !== 'undefined' && self.cancelIdleCallback && self.cancelIdleCallback.bind(window) || function(id) {
    return clearTimeout(id);
};
if ((typeof exports.default === 'function' || typeof exports.default === 'object' && exports.default !== null) && typeof exports.default.__esModule === 'undefined') {
    Object.defineProperty(exports.default, '__esModule', {
        value: true
    });
    Object.assign(exports.default, exports);
    module.exports = exports.default;
}
}),
"[project]/node_modules/.pnpm/next@16.2.10_@babel+core@7._54fe0b4b34f39aa1bf7e10b73832e4f5/node_modules/next/dist/shared/lib/htmlescape.js [app-ssr] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

// This utility is based on https://github.com/zertosh/htmlescape
// License: https://github.com/zertosh/htmlescape/blob/0527ca7156a524d256101bb310a9f970f63078ad/LICENSE
Object.defineProperty(exports, "__esModule", {
    value: true
});
0 && (module.exports = {
    ESCAPE_REGEX: null,
    htmlEscapeAttributeString: null,
    htmlEscapeJsonString: null
});
function _export(target, all) {
    for(var name in all)Object.defineProperty(target, name, {
        enumerable: true,
        get: all[name]
    });
}
_export(exports, {
    ESCAPE_REGEX: function() {
        return ESCAPE_REGEX;
    },
    htmlEscapeAttributeString: function() {
        return htmlEscapeAttributeString;
    },
    htmlEscapeJsonString: function() {
        return htmlEscapeJsonString;
    }
});
const ESCAPE_LOOKUP = {
    '&': '\\u0026',
    '>': '\\u003e',
    '<': '\\u003c',
    '\u2028': '\\u2028',
    '\u2029': '\\u2029'
};
const ESCAPE_REGEX = /[&><\u2028\u2029]/g;
const ATTRIBUTE_ESCAPE_LOOKUP = {
    '&': '&amp;',
    '"': '&quot;',
    "'": '&#39;',
    '<': '&lt;',
    '>': '&gt;'
};
const ATTRIBUTE_ESCAPE_REGEX = /[&"'<>]/g;
function htmlEscapeJsonString(str) {
    return str.replace(ESCAPE_REGEX, (match)=>ESCAPE_LOOKUP[match]);
}
function htmlEscapeAttributeString(str) {
    return str.replace(ATTRIBUTE_ESCAPE_REGEX, (match)=>ATTRIBUTE_ESCAPE_LOOKUP[match]);
}
}),
"[project]/node_modules/.pnpm/next@16.2.10_@babel+core@7._54fe0b4b34f39aa1bf7e10b73832e4f5/node_modules/next/dist/client/script.js [app-ssr] (ecmascript)", ((__turbopack_context__, module, exports) => {
"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});
0 && (module.exports = {
    default: null,
    handleClientScriptLoad: null,
    initScriptLoader: null
});
function _export(target, all) {
    for(var name in all)Object.defineProperty(target, name, {
        enumerable: true,
        get: all[name]
    });
}
_export(exports, {
    default: function() {
        return _default;
    },
    handleClientScriptLoad: function() {
        return handleClientScriptLoad;
    },
    initScriptLoader: function() {
        return initScriptLoader;
    }
});
const _interop_require_default = __turbopack_context__.r("[project]/node_modules/.pnpm/@swc+helpers@0.5.15/node_modules/@swc/helpers/cjs/_interop_require_default.cjs [app-ssr] (ecmascript)");
const _interop_require_wildcard = __turbopack_context__.r("[project]/node_modules/.pnpm/@swc+helpers@0.5.15/node_modules/@swc/helpers/cjs/_interop_require_wildcard.cjs [app-ssr] (ecmascript)");
const _jsxruntime = __turbopack_context__.r("[project]/node_modules/.pnpm/next@16.2.10_@babel+core@7._54fe0b4b34f39aa1bf7e10b73832e4f5/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-runtime.js [app-ssr] (ecmascript)");
const _reactdom = /*#__PURE__*/ _interop_require_default._(__turbopack_context__.r("[project]/node_modules/.pnpm/next@16.2.10_@babel+core@7._54fe0b4b34f39aa1bf7e10b73832e4f5/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-dom.js [app-ssr] (ecmascript)"));
const _react = /*#__PURE__*/ _interop_require_wildcard._(__turbopack_context__.r("[project]/node_modules/.pnpm/next@16.2.10_@babel+core@7._54fe0b4b34f39aa1bf7e10b73832e4f5/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)"));
const _headmanagercontextsharedruntime = __turbopack_context__.r("[project]/node_modules/.pnpm/next@16.2.10_@babel+core@7._54fe0b4b34f39aa1bf7e10b73832e4f5/node_modules/next/dist/server/route-modules/app-page/vendored/contexts/head-manager-context.js [app-ssr] (ecmascript)");
const _setattributesfromprops = __turbopack_context__.r("[project]/node_modules/.pnpm/next@16.2.10_@babel+core@7._54fe0b4b34f39aa1bf7e10b73832e4f5/node_modules/next/dist/client/set-attributes-from-props.js [app-ssr] (ecmascript)");
const _requestidlecallback = __turbopack_context__.r("[project]/node_modules/.pnpm/next@16.2.10_@babel+core@7._54fe0b4b34f39aa1bf7e10b73832e4f5/node_modules/next/dist/client/request-idle-callback.js [app-ssr] (ecmascript)");
const _htmlescape = __turbopack_context__.r("[project]/node_modules/.pnpm/next@16.2.10_@babel+core@7._54fe0b4b34f39aa1bf7e10b73832e4f5/node_modules/next/dist/shared/lib/htmlescape.js [app-ssr] (ecmascript)");
const ScriptCache = new Map();
const LoadCache = new Set();
const insertStylesheets = (stylesheets)=>{
    // Case 1: Styles for afterInteractive/lazyOnload with appDir injected via handleClientScriptLoad
    //
    // Using ReactDOM.preinit to feature detect appDir and inject styles
    // Stylesheets might have already been loaded if initialized with Script component
    // Re-inject styles here to handle scripts loaded via handleClientScriptLoad
    // ReactDOM.preinit handles dedup and ensures the styles are loaded only once
    if (_reactdom.default.preinit) {
        stylesheets.forEach((stylesheet)=>{
            _reactdom.default.preinit(stylesheet, {
                as: 'style'
            });
        });
        return;
    }
    // Case 2: Styles for afterInteractive/lazyOnload with pages injected via handleClientScriptLoad
    //
    // We use this function to load styles when appdir is not detected
    // TODO: Use React float APIs to load styles once available for pages dir
    if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
    ;
};
const loadScript = (props)=>{
    const { src, id, onLoad = ()=>{}, onReady = null, dangerouslySetInnerHTML, children = '', strategy = 'afterInteractive', onError, stylesheets } = props;
    const cacheKey = id || src;
    // Script has already loaded
    if (cacheKey && LoadCache.has(cacheKey)) {
        return;
    }
    // Contents of this script are already loading/loaded
    if (ScriptCache.has(src)) {
        LoadCache.add(cacheKey);
        // It is possible that multiple `next/script` components all have same "src", but has different "onLoad"
        // This is to make sure the same remote script will only load once, but "onLoad" are executed in order
        ScriptCache.get(src).then(onLoad, onError);
        return;
    }
    /** Execute after the script first loaded */ const afterLoad = ()=>{
        // Run onReady for the first time after load event
        if (onReady) {
            onReady();
        }
        // add cacheKey to LoadCache when load successfully
        LoadCache.add(cacheKey);
    };
    const el = document.createElement('script');
    const loadPromise = new Promise((resolve, reject)=>{
        el.addEventListener('load', function(e) {
            resolve();
            if (onLoad) {
                onLoad.call(this, e);
            }
            afterLoad();
        });
        el.addEventListener('error', function(e) {
            reject(e);
        });
    }).catch(function(e) {
        if (onError) {
            onError(e);
        }
    });
    if (dangerouslySetInnerHTML) {
        // Casting since lib.dom.d.ts doesn't have TrustedHTML yet.
        el.innerHTML = dangerouslySetInnerHTML.__html || '';
        afterLoad();
    } else if (children) {
        el.textContent = typeof children === 'string' ? children : Array.isArray(children) ? children.join('') : '';
        afterLoad();
    } else if (src) {
        el.src = src;
        // do not add cacheKey into LoadCache for remote script here
        // cacheKey will be added to LoadCache when it is actually loaded (see loadPromise above)
        ScriptCache.set(src, loadPromise);
    }
    (0, _setattributesfromprops.setAttributesFromProps)(el, props);
    if (strategy === 'worker') {
        el.setAttribute('type', 'text/partytown');
    }
    el.setAttribute('data-nscript', strategy);
    // Load styles associated with this script
    if (stylesheets) {
        insertStylesheets(stylesheets);
    }
    document.body.appendChild(el);
};
function handleClientScriptLoad(props) {
    const { strategy = 'afterInteractive' } = props;
    if (strategy === 'lazyOnload') {
        window.addEventListener('load', ()=>{
            (0, _requestidlecallback.requestIdleCallback)(()=>loadScript(props));
        });
    } else {
        loadScript(props);
    }
}
function loadLazyScript(props) {
    if (document.readyState === 'complete') {
        (0, _requestidlecallback.requestIdleCallback)(()=>loadScript(props));
    } else {
        window.addEventListener('load', ()=>{
            (0, _requestidlecallback.requestIdleCallback)(()=>loadScript(props));
        });
    }
}
function addBeforeInteractiveToCache() {
    const scripts = [
        ...document.querySelectorAll('[data-nscript="beforeInteractive"]'),
        ...document.querySelectorAll('[data-nscript="beforePageRender"]')
    ];
    scripts.forEach((script)=>{
        const cacheKey = script.id || script.getAttribute('src');
        LoadCache.add(cacheKey);
    });
}
function initScriptLoader(scriptLoaderItems) {
    scriptLoaderItems.forEach(handleClientScriptLoad);
    addBeforeInteractiveToCache();
}
/**
 * Load a third-party scripts in an optimized way.
 *
 * Read more: [Next.js Docs: `next/script`](https://nextjs.org/docs/app/api-reference/components/script)
 */ function Script(props) {
    const { id, src = '', onLoad = ()=>{}, onReady = null, strategy = 'afterInteractive', onError, stylesheets, ...restProps } = props;
    // Context is available only during SSR
    let { updateScripts, scripts, getIsSsr, appDir, nonce } = (0, _react.useContext)(_headmanagercontextsharedruntime.HeadManagerContext);
    // if a nonce is explicitly passed to the script tag, favor that over the automatic handling
    nonce = restProps.nonce || nonce;
    /**
   * - First mount:
   *   1. The useEffect for onReady executes
   *   2. hasOnReadyEffectCalled.current is false, but the script hasn't loaded yet (not in LoadCache)
   *      onReady is skipped, set hasOnReadyEffectCalled.current to true
   *   3. The useEffect for loadScript executes
   *   4. hasLoadScriptEffectCalled.current is false, loadScript executes
   *      Once the script is loaded, the onLoad and onReady will be called by then
   *   [If strict mode is enabled / is wrapped in <OffScreen /> component]
   *   5. The useEffect for onReady executes again
   *   6. hasOnReadyEffectCalled.current is true, so entire effect is skipped
   *   7. The useEffect for loadScript executes again
   *   8. hasLoadScriptEffectCalled.current is true, so entire effect is skipped
   *
   * - Second mount:
   *   1. The useEffect for onReady executes
   *   2. hasOnReadyEffectCalled.current is false, but the script has already loaded (found in LoadCache)
   *      onReady is called, set hasOnReadyEffectCalled.current to true
   *   3. The useEffect for loadScript executes
   *   4. The script is already loaded, loadScript bails out
   *   [If strict mode is enabled / is wrapped in <OffScreen /> component]
   *   5. The useEffect for onReady executes again
   *   6. hasOnReadyEffectCalled.current is true, so entire effect is skipped
   *   7. The useEffect for loadScript executes again
   *   8. hasLoadScriptEffectCalled.current is true, so entire effect is skipped
   */ const hasOnReadyEffectCalled = (0, _react.useRef)(false);
    (0, _react.useEffect)(()=>{
        const cacheKey = id || src;
        if (!hasOnReadyEffectCalled.current) {
            // Run onReady if script has loaded before but component is re-mounted
            if (onReady && cacheKey && LoadCache.has(cacheKey)) {
                onReady();
            }
            hasOnReadyEffectCalled.current = true;
        }
    }, [
        onReady,
        id,
        src
    ]);
    const hasLoadScriptEffectCalled = (0, _react.useRef)(false);
    (0, _react.useEffect)(()=>{
        if (!hasLoadScriptEffectCalled.current) {
            if (strategy === 'afterInteractive') {
                loadScript(props);
            } else if (strategy === 'lazyOnload') {
                loadLazyScript(props);
            }
            hasLoadScriptEffectCalled.current = true;
        }
    }, [
        props,
        strategy
    ]);
    if (strategy === 'beforeInteractive' || strategy === 'worker') {
        if (updateScripts) {
            scripts[strategy] = (scripts[strategy] || []).concat([
                {
                    id,
                    src,
                    onLoad,
                    onReady,
                    onError,
                    ...restProps,
                    nonce
                }
            ]);
            updateScripts(scripts);
        } else if (getIsSsr && getIsSsr()) {
            // Script has already loaded during SSR
            LoadCache.add(id || src);
        } else if (getIsSsr && !getIsSsr()) {
            loadScript({
                ...props,
                nonce
            });
        }
    }
    // For the app directory, we need React Float to preload these scripts.
    if (appDir) {
        // Injecting stylesheets here handles beforeInteractive and worker scripts correctly
        // For other strategies injecting here ensures correct stylesheet order
        // ReactDOM.preinit handles loading the styles in the correct order,
        // also ensures the stylesheet is loaded only once and in a consistent manner
        //
        // Case 1: Styles for beforeInteractive/worker with appDir - handled here
        // Case 2: Styles for beforeInteractive/worker with pages dir - Not handled yet
        // Case 3: Styles for afterInteractive/lazyOnload with appDir - handled here
        // Case 4: Styles for afterInteractive/lazyOnload with pages dir - handled in insertStylesheets function
        if (stylesheets) {
            stylesheets.forEach((styleSrc)=>{
                _reactdom.default.preinit(styleSrc, {
                    as: 'style'
                });
            });
        }
        // Before interactive scripts need to be loaded by Next.js' runtime instead
        // of native <script> tags, because they no longer have `defer`.
        if (strategy === 'beforeInteractive') {
            if (!src) {
                // For inlined scripts, we put the content in `children`.
                if (restProps.dangerouslySetInnerHTML) {
                    // Casting since lib.dom.d.ts doesn't have TrustedHTML yet.
                    restProps.children = restProps.dangerouslySetInnerHTML.__html;
                    delete restProps.dangerouslySetInnerHTML;
                }
                return /*#__PURE__*/ (0, _jsxruntime.jsx)("script", {
                    nonce: nonce,
                    dangerouslySetInnerHTML: {
                        __html: `(self.__next_s=self.__next_s||[]).push(${(0, _htmlescape.htmlEscapeJsonString)(JSON.stringify([
                            0,
                            {
                                ...restProps,
                                id
                            }
                        ]))})`
                    }
                });
            } else {
                // @ts-ignore
                _reactdom.default.preload(src, restProps.integrity ? {
                    as: 'script',
                    integrity: restProps.integrity,
                    nonce,
                    crossOrigin: restProps.crossOrigin
                } : {
                    as: 'script',
                    nonce,
                    crossOrigin: restProps.crossOrigin
                });
                return /*#__PURE__*/ (0, _jsxruntime.jsx)("script", {
                    nonce: nonce,
                    dangerouslySetInnerHTML: {
                        __html: `(self.__next_s=self.__next_s||[]).push(${(0, _htmlescape.htmlEscapeJsonString)(JSON.stringify([
                            src,
                            {
                                ...restProps,
                                id
                            }
                        ]))})`
                    }
                });
            }
        } else if (strategy === 'afterInteractive') {
            if (src) {
                // @ts-ignore
                _reactdom.default.preload(src, restProps.integrity ? {
                    as: 'script',
                    integrity: restProps.integrity,
                    nonce,
                    crossOrigin: restProps.crossOrigin
                } : {
                    as: 'script',
                    nonce,
                    crossOrigin: restProps.crossOrigin
                });
            }
        }
    }
    return null;
}
Object.defineProperty(Script, '__nextScript', {
    value: true
});
const _default = Script;
if ((typeof exports.default === 'function' || typeof exports.default === 'object' && exports.default !== null) && typeof exports.default.__esModule === 'undefined') {
    Object.defineProperty(exports.default, '__esModule', {
        value: true
    });
    Object.assign(exports.default, exports);
    module.exports = exports.default;
}
}),
"[project]/node_modules/.pnpm/next@16.2.10_@babel+core@7._54fe0b4b34f39aa1bf7e10b73832e4f5/node_modules/next/script.js [app-ssr] (ecmascript)", ((__turbopack_context__, module, exports) => {

module.exports = __turbopack_context__.r("[project]/node_modules/.pnpm/next@16.2.10_@babel+core@7._54fe0b4b34f39aa1bf7e10b73832e4f5/node_modules/next/dist/client/script.js [app-ssr] (ecmascript)");
}),
];

//# sourceMappingURL=_1aah129._.js.map