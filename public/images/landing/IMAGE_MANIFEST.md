# Image Manifest — Landing Page (Sprint 001)

All images referenced in the landing page code. Save generated assets to this directory
(`public/images/landing/`). Use optimized JPEG or WebP under 500KB each.

Prompts for generating these images are in `docs/showrunner-architect/planning/sprints/001-landing-page/prompts-v2.md`.

---

## hero-control-room.jpg

**File path:** `/public/images/landing/hero-control-room.jpg`
**Referenced in:** `components/landing/Hero.tsx`
**Usage:** Full-bleed hero background with dark gradient overlay

**Visual:** High-end TV broadcast production control room. U-shaped layout with 6–8 large
broadcast monitors, professional video switcher (Blackmagic ATEM / Grass Valley), operator
consoles with control surfaces, audio monitoring speakers. Dim, focused lighting with monitor
glow as primary light source. Subtle magenta and cyan accent lighting from LED strips.

**Specs:**
- Resolution: 2560×1440px minimum (16:9)
- Format: JPEG or WebP
- File size: < 500KB
- Aspect ratio: 16:9, object-fit cover
- Color space: sRGB

---

## pipeline-studio.jpg

**File path:** `/public/images/landing/pipeline-studio.jpg`
**Referenced in:** `components/landing/PipelineSection.tsx`
**Usage:** Background at 20% opacity with dark overlay

**Visual:** Professional post-production editing suite / color grading bay. Large curved
reference monitor (55" Sony BVM-class), DaVinci Resolve color grading control surface with
trackballs, editing workstation with dual monitors, acoustic treatment on walls. Dim lighting
with bias lighting behind reference monitor.

**Specs:**
- Resolution: 2560×1440px minimum (16:9)
- Format: JPEG or WebP
- File size: < 500KB
- Aspect ratio: 16:9, object-fit cover
- Will be displayed at 20% opacity — composition should work when heavily faded

---

## agents-holographic.jpg

**File path:** `/public/images/landing/agents-holographic.jpg`
**Referenced in:** `components/landing/AgentsSection.tsx`
**Usage:** Background at 10% opacity with dark overlay

**Visual:** Modern TV writers' room / creative workspace. Large conference table with chairs,
whiteboards and cork boards covered in index cards, story beats, character relationship maps,
color-coded sticky notes. Breakout areas with comfortable seating. Warm, inviting lighting
with mix of natural light and practical lamps.

**Specs:**
- Resolution: 2560×1440px minimum (16:9)
- Format: JPEG or WebP
- File size: < 500KB

- Aspect ratio: 16:9, object-fit cover
- Will be displayed at 10% opacity — very subtle, adds texture only

---

## cta-clapperboard.jpg

**File path:** `/public/images/landing/cta-clapperboard.jpg`
**Referenced in:** `components/landing/CTASection.tsx`
**Usage:** Full background with heavy dark gradient overlay

**Visual:** Professional film production set in action. Cinema camera (ARRI Alexa / RED) on
dolly with follow focus and matte box, film lights with atmospheric haze, clapperboard/slate
in foreground. Cinematic motivated lighting with high contrast. Crew silhouettes partially
visible. Subtle magenta and cyan accent lighting from set practicals.

**Specs:**
- Resolution: 2560×1440px minimum (16:9)
- Format: JPEG or WebP
- File size: < 500KB
- Aspect ratio: 16:9, object-fit cover
- Will be displayed with heavy dark overlay — composition should work when darkened

---

## Image Generation Notes

- All images should be photorealistic, grounded in real production environments
- Use the prompts in `prompts-v2.md` with Nano Banana 3.0 Pro via Google Stitch
- Color palette: deep charcoal base (#0a0a0f), magenta (#d946ef) and cyan (#06b6d4) as subtle accents
- Avoid: sci-fi holographic displays, generic tech dashboards, stock photo aesthetic
- Each image should feel authentic — real equipment, real lighting, real production spaces
