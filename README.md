# Convertale

**One brand brief. A complete, published short-drama ad campaign.**

Convertale is an autonomous, agent-based production platform that turns a
single brand brief into a produced short-drama ad campaign — series bible,
scripts, storyboards, AI-generated video, continuity checking, and a
Cliffhanger email-capture gate — with minimal human involvement.

> **Implementation status:** this README describes the full product vision.
> Today's implemented agents cover brand intake, the writers' room,
> storyboarding, continuity checking, video routing/rendering, assembly, and
> the Cliffhanger gate. Voice synthesis, musical scoring, trailer/shorts
> cutdowns, thumbnail generation, SEO metadata, and YouTube publishing are
> **not yet implemented** — the routers, agents, and env vars for them
> don't exist yet. Treat sections below describing those as roadmap, not
> shipped functionality.

Built for the **Qwen Cloud Hackathon (AI Showrunner track)**.

---

## The Problem

Episodic video production requires an entire crew — showrunner, writers' room, storyboard artist, director, video production, voice actors, composer, editor, marketing, publisher — working in sequence over days or weeks. Independent creators, small studios, educators, and brand teams have the ideas but not the production capacity. Existing AI video tools generate isolated clips with zero memory across sessions: characters drift, world rules contradict, plot threads drop.

## How Showrunner AI Solves It

A user submits a concept — *"a noir detective series set in Lagos, 2095"* — and **18+ specialized AI agents** organized into five divisions autonomously produce everything:

```
Creative → Production → Generation & Assembly → Quality → Distribution
```

| Division | Agents | Responsibility |
|---|---|---|
| **Creative** | ExecutiveProducer, ShowBible, WorldArchitect, CharacterArchitect, StoryArchitect, Screenwriter, DialogueWriter | Series bible, world-building, character profiles, episode outlines, full screenplays |
| **Production** | StoryboardArtist, Cinematographer, VideoPromptEngineer | Shot-by-shot breakdown, camera direction, generation-optimized prompts |
| **Generation & Assembly** | VideoOrchestrator, VoiceDirector, TTSSynthesizer, MusicComposer, SceneMerge, EpisodeAssembly | Parallel video generation (Wan 2.7 / HappyHorse), voice synthesis, scoring, FFmpeg assembly |
| **Quality** | CriticAgent, ContinuityChecker, TokenBudgetManager | Pacing/narrative scoring, graph-based contradiction detection, budget enforcement |
| **Distribution** | TrailerGenerator, ShortsGenerator, ThumbnailDesigner, SEOAgent, YouTubePublisher, AnalyticsAgent | Trailers, 9:16 shorts, thumbnails, SEO metadata, real YouTube OAuth upload, performance analytics |

Every agent reads from and writes to a **persistent Neo4j knowledge graph** — the show's memory. Characters, world rules, and plot facts are never lost between episodes. The Continuity Checker queries this graph to flag contradictions before publishing.

---

## Architecture

**Microservice-ready modular monolith** — one FastAPI process at launch, organized by agent division with clean interface boundaries designed for future extraction into per-division microservices.

```
                     ┌───────────────────────────┐
                     │   Next.js 16 Frontend      │
                     │  (App Router, SSE client)   │
                     └─────────────┬──────────────┘
                                   │ HTTPS / SSE
                     ┌─────────────▼──────────────┐
                     │      FastAPI Backend         │
                     │  (async, Pydantic v2)        │
                     │  agents/ by division          │
                     └──┬─────────┬─────────┬──────┘
                        │         │         │
            ┌───────────▼──┐ ┌────▼────┐ ┌──▼───────────────┐
            │  Neon DB      │ │ Neo4j   │ │ Celery + Redis   │
            │  (Postgres)   │ │ AuraDB  │ │ (task queue)     │
            │  transactional│ │ graph + │ │ video/render jobs│
            │  system of    │ │ vector  │ │                  │
            │  record       │ │ grounding│ │                 │
            └───────────────┘ └─────────┘ └──────┬───────────┘
                                                  │
                                    ┌─────────────▼─────────────┐
                                    │   FastMCP Connector Layer   │
                                    │ youtube / github / slack /  │
                                    │ neondb-mcp                  │
                                    └─────────────┬───────────────┘
                                                   │
                              ┌────────────────────┼────────────────────┐
                              ▼                    ▼                    ▼
                        YouTube Data API      DashScope (Qwen,     Alibaba OSS
                        v3                    Wan, HappyHorse,      (assets)
                                               CosyVoice, Embed)
```

### Key Architectural Decisions

- **Dual-database design** — Neon DB (serverless Postgres) for transactional/billing/audit data; Neo4j AuraDB for show memory (graph + vector grounding). Each is load-bearing; neither replaces the other.
- **Graph-grounded continuity** — Every `Character`, `Scene`, and `Location` node carries a Qwen-generated 1536-dim embedding stored in Neo4j native vector indexes. Similarity search is a pure vector-index read with no LLM call in the hot path.
- **FastMCP connector registry** — Agents never call third-party APIs directly. All external integrations (YouTube, GitHub, Slack, Neon DB) go through registered MCP servers resolved at runtime. Credentials are Fernet-encrypted, audit-logged, and scoped to the workspace.
- **Token budget management** — A monitoring sidecar runs alongside all pipeline stages. Pre-flight budget checks, per-call metering, automatic model downgrading (`qwen-max` → `qwen-plus` → `qwen-flash`), and `PlanGuard` middleware that rejects video-generation jobs before enqueue if quota would be exceeded.
- **Quality loop with bounded retries** — The Critic Agent can loop back to the Screenwriter (max 2 retries per episode). After 2 retries, the episode proceeds with a "Review Recommended" flag.

### Extraction Order (binding)

1. `video-service` — highest compute; GPU/high-CPU node pool already isolates it
2. `grounding-service` — wraps all Neo4j access behind gRPC
3. `distribution-service` — independent publish cadence
4. Full per-division services at scale

---

## Technology Stack

| Concern | Choice |
|---|---|
| **Cloud** | Alibaba Cloud (ACK, OSS, ACR, KMS, CloudMonitor, ARMS) |
| **Frontend** | Next.js 16 (App Router) + Tailwind CSS v4 + TypeScript |
| **Backend** | FastAPI (Python 3.11), async, Pydantic v2 |
| **Relational DB** | Neon DB (serverless Postgres) |
| **Graph + Vector** | Neo4j AuraDB (native vector index, 1536-dim cosine similarity) |
| **Cache / Queue** | ApsaraDB for Redis + Celery |
| **Auth / Billing** | Clerk + Clerk Billing (Stripe) |
| **Primary LLM** | Qwen via DashScope (`qwen-max` / `qwen-plus` / `qwen-flash`) |
| **Complex Reasoning** | Anthropic Claude (Critic, Continuity, Story Architect) |
| **Video Generation** | Wan 2.7 + HappyHorse 1.0 (DashScope) |
| **TTS** | Qwen CosyVoice v3-plus |
| **Embeddings** | Qwen Embedding API, 1536-dim |
| **Connectors** | FastMCP registry |
| **CI/CD** | GitHub Actions → ACR → ACK (Helm) |

---

## Data Model

### Relational (Neon DB — 11 core tables)

| Table | Purpose |
|---|---|
| `users` | Clerk-managed, synced via webhook |
| `workspaces` | Clerk Organization; billing and team isolation boundary |
| `projects` | One series per project; status tracks pipeline progress |
| `series_bibles` | Creative foundation: logline, themes, world/character snapshots |
| `episodes` | One installment: script, assembled video, publish record |
| `scenes` / `shots` | Narrative and generation-atomic units |
| `agent_jobs` | Audit trail of every agent invocation (status, tokens, model) |
| `assets` | Binary outputs: clips, audio, thumbnails, trailers, shorts |
| `mcp_connectors` | Registered external integrations with encrypted credentials |
| `publish_records` | YouTube upload state and analytics |
| `usage_records` | Append-only metering: render minutes, tokens, TTS chars |

### Graph + Vector (Neo4j AuraDB)

Node types: `Project`, `Character`, `Location`, `Episode`, `Scene`, `Fact`, `WorldRule`

Key relationships: `APPEARS_IN`, `PRESENT_IN`, `ESTABLISHED`, `KNOWS`, `CONFLICTS_WITH`, `PART_OF`, `SET_IN`, `CONTRADICTS`, `HAS_RULE`

Vector indexes on `Character.embedding`, `Scene.embedding`, `Location.embedding` — 1536 dimensions, cosine similarity.

All graph access goes through `GraphMemoryService` — typed methods, no raw Cypher outside the service.

---

## Subscription Plans

| Feature | Free (Backlot) | Creator ($39/mo) | Studio ($149/mo) | Enterprise |
|---|---|---|---|---|
| Active projects | 1 | 5 | Unlimited | Unlimited |
| Render minutes/month | 6 | 60 | 300 | Negotiated |
| Seats | 1 | 3 | 10 | Unlimited |
| YouTube publish | Manual export | ✓ | ✓ | ✓ |
| Trailers + Shorts | — | ✓ | ✓ | ✓ |
| MCP connectors | — | — | ✓ | ✓ (custom) |
| Team roles & permissions | — | — | ✓ | ✓ |
| Multi-season memory | — | — | — | ✓ |
| Dedicated render capacity | — | — | — | ✓ |

---

## Project Structure

```
qwen-ai-showrunner/
├── app/                    # Next.js frontend (App Router)
├── apps/api/               # FastAPI backend (Python)
├── components/             # Shared React components
├── infra/
│   ├── terraform/          # ACK, OSS, ACR, KMS provisioning
│   └── helm/showrunner/    # API, Celery worker, Redis workloads
├── packages/shared/        # Future shared contracts
├── scripts/                # Neo4j init, utilities
├── docs/                   # PRD, architecture, sprint plans
├── DESIGN.md               # Design system (colors, typography, components)
└── AGENTS.md               # Agent configuration
```

---

## Getting Started

### Prerequisites

- Node.js 20+, pnpm
- Python 3.11+, Poetry
- Clerk account (auth/billing)
- Neon DB project
- Neo4j AuraDB instance
- Alibaba Cloud account (OSS, ACR, ACK)
- DashScope API key (Qwen models)

### Environment Setup

```bash
cp .env.example .env
# Fill in Clerk, Neon, Neo4j, Alibaba Cloud, and DashScope credentials
```

### Frontend

```bash
pnpm install
pnpm dev          # → http://localhost:3000
pnpm lint
pnpm build
```

### Backend API

```bash
cd apps/api
poetry install
poetry run alembic upgrade head
poetry run uvicorn showrunner_api.main:app --reload
# Health check:
curl http://localhost:8000/health
```

### Neo4j Initialization

```bash
python scripts/init_neo4j.py
```

Creates node constraints and vector indexes (`character_embeddings`, `scene_embeddings`, `location_embeddings`).

### Infrastructure

```bash
# Terraform
cd infra/terraform && terraform init && terraform plan

# Helm
helm upgrade --install showrunner infra/helm/showrunner
```

---

## Development Roadmap

| Sprint | Scope | Status |
|---|---|---|
| **001 — Foundation & Infrastructure** | Monorepo, databases, Clerk auth, FastAPI skeleton, ACK deployment | 🟡 In Progress |
| **001 — Landing Page** | Cinematic public marketing page (no backend dependency) | 🟡 Planning |
| **002 — Executive Pipeline** | ExecutiveProducer, ShowBible, World/Character agents | ⏳ Pending |
| **003 — Story Generation** | StoryArchitect, Screenwriter, DialogueWriter agents | ⏳ Pending |
| **004 — Video & Distribution** | Storyboarding, video generation, voice, assembly, YouTube publishing | ⏳ Pending |
| **005 — Quality & Continuity** | Critic agent, Continuity agent with Neo4j graph queries | ⏳ Pending |

**Critical path:** 001-foundation → 002 → 003 → 004 → 005  
**Parallel track:** 001-landing-page (independent of foundation)

---

## Design System

The UI follows a **cinematic, premium, product-forward** design language. Deep navy/black base (`#0a0e27`), magenta primary accents (`#e91e8c`), blue secondary (`#2563eb`). Geist font stack. 8px spacing grid. WCAG AA compliant.

See [DESIGN.md](./DESIGN.md) for the full design system specification.

---

## Documentation

| Document | Location |
|---|---|
| Product Requirements (PRD v2) | `docs/showrunner-architect/docs/prdV2.md` |
| Architecture | `docs/showrunner-architect/docs/ARCHITECTURE.md` |
| Data Model | `docs/showrunner-architect/docs/DATA_MODEL.md` |
| Architecture Decisions | `docs/showrunner-architect/planning/DECISIONS.md` |
| Domain Model | `docs/showrunner-architect/planning/DOMAIN.md` |
| Sprint Plans | `docs/showrunner-architect/planning/sprints/` |
| Design System | `DESIGN.md` |
| Sprint Tracker | `docs/PLAN.md` |

---

## License

Private — Qwen Cloud Hackathon project.
