# DESIGN.md — Showrunner AI Studio Design System

**Version:** 1.0  
**Last updated:** July 3, 2026  
**Status:** Active  

This document establishes the design system and UI/UX guidelines for Showrunner AI Studio across all public and internal interfaces. All design decisions derive from the `.gemini/skills/` resources and are applied consistently across web, dashboard, and marketing surfaces.

---

## Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [Color System](#color-system)
3. [Typography](#typography)
4. [Spacing & Layout](#spacing--layout)
5. [Components & Patterns](#components--patterns)
6. [Imagery & Backgrounds](#imagery--backgrounds)
7. [Accessibility](#accessibility)
8. [Motion & Animation](#motion--animation)
9. [Responsive Design](#responsive-design)
10. [Design Resources](#design-resources)
11. [Implementation Checklist](#implementation-checklist)

---

## Design Philosophy

Showrunner's design language is **cinematic, premium, and product-forward**. Every visual element communicates production capability and creative power. We avoid generic AI hype, vague marketing abstractions, and decorative ornament.

### Core Principles

1. **Clarity First** — Every element has a purpose. No decoration without function.
2. **Cinematic Depth** — Use layering, contrast, and composition to create visual hierarchy and immersion.
3. **Precision & Polish** — Meticulous spacing, typography, and alignment reflect production-grade quality.
4. **Dark Premium** — Deep navy/black base with controlled, intentional accent colors.
5. **Product-Centric** — Visuals communicate *what the system does*, not aspirational marketing.
6. **Accessible by Default** — All users, including those with motion sensitivity or color blindness, experience a complete, usable interface.

---

## Color System

### Primitive Colors

| Name | Hex | Usage |
|---|---|---|
| Navy Base | `#0a0e27` | Primary page background |
| Navy Light | `#1a1f3a` | Card backgrounds, section dividers |
| Navy Medium | `#2a3050` | Hover states, subtle surfaces |
| Magenta Primary | `#e91e8c` | CTAs, highlights, focus accents |
| Blue Primary | `#2563eb` | Focus rings, secondary highlights, links |
| Text Primary | `#f5f5f5` | Main body text, headings |
| Text Secondary | `#a0a0a0` | Supporting text, descriptions |
| Border | `#333333` | Card borders, dividers, subtle outlines |
| Success | `#10b981` | Status indicators, success states (use sparingly) |

### Semantic Roles

```css
/* Backgrounds */
--bg-page: #0a0e27;           /* Primary page background */
--bg-section: #1a1f3a;        /* Card, surface backgrounds */
--bg-hover: #2a3050;          /* Hover state backgrounds */

/* Text */
--text-primary: #f5f5f5;      /* Main text, headings */
--text-secondary: #a0a0a0;    /* Supporting text */
--text-muted: #6b7280;        /* Disabled, placeholder text */

/* Interactive */
--color-primary: #e91e8c;     /* CTAs, primary actions */
--color-secondary: #2563eb;   /* Focus, secondary actions */
--color-accent: #e91e8c;      /* Visual highlights */

/* Borders & Dividers */
--border-light: #333333;      /* Default borders */
--border-focus: #2563eb;      /* Focus ring color */

/* States */
--state-success: #10b981;     /* Success indicator */
--state-warning: #f59e0b;     /* Warning indicator (use if needed) */
--state-error: #ef4444;       /* Error indicator (use if needed) */
```

### Color Contrast & Accessibility

All text combinations meet **WCAG AA minimum (4.5:1) for body text** and **3:1 for large text**:

| Text on Background | Contrast Ratio | WCAG Level |
|---|---|---|
| `#f5f5f5` on `#0a0e27` | 15.6:1 | AAA |
| `#a0a0a0` on `#0a0e27` | 6.8:1 | AA |
| `#f5f5f5` on `#1a1f3a` | 14.2:1 | AAA |
| `#a0a0a0` on `#1a1f3a` | 5.8:1 | AA |
| Magenta `#e91e8c` on Navy | Sufficient for accents, use with text overlay for certainty |

**Accessibility Note:** Never rely on color alone to convey meaning (e.g., red for error, green for success without text or icon). Always pair color with text, icons, or patterns.

---

## Typography

### Font Stack

```css
/* Primary Sans-Serif */
font-family: "Geist", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;

/* Monospace (for code, technical content) */
font-family: "Geist Mono", Monaco, Courier, monospace;
```

**Note:** Geist is already loaded in the Next.js app via `@next/font/google`.

### Type Scale

| Role | Size | Weight | Line Height | Letter Spacing | Use |
|---|---|---|---|---|---|
| Hero H1 | 56–64px | 600–700 | 1.2 | -1px | Page hero, main heading |
| H2 / Section | 32–40px | 600 | 1.3 | 0 | Section titles |
| H3 / Subsection | 24–28px | 600 | 1.4 | 0 | Card titles, subsections |
| Body Large | 18–20px | 400 | 1.6 | 0 | Lead copy, callouts |
| Body | 16px | 400 | 1.6 | 0 | Main body text |
| Body Small | 14px | 400 | 1.5 | 0 | Supporting text, captions |
| Label / CTA | 14–16px | 600 | 1.5 | 0.5px | Button text, labels |
| Small / Footnote | 12px | 400 | 1.5 | 0 | Footer, metadata |

### Typography Hierarchy

```
Page H1 (Hero)
    ├─ Section H2
    │   ├─ Card H3 / Feature Title
    │   └─ Body (supporting copy)
    └─ Body Small (labels, captions)
```

**Guidelines:**
- One logical `<h1>` per page (in hero section)
- Use `<h2>` for major sections
- Use `<h3>` for subsections and card titles
- Never skip heading levels (e.g., h1 → h3, skipping h2)
- Use `<strong>` or `<b>` for emphasis within body copy, not for headings

---

## Spacing & Layout

### Base Unit

All spacing derives from **8px base unit**:

```css
--space-px: 1px;
--space-1: 8px;
--space-2: 16px;
--space-3: 24px;
--space-4: 32px;
--space-5: 40px;
--space-6: 48px;
--space-8: 64px;
--space-12: 96px;
--space-16: 128px;
```

### Padding & Margins

| Context | Value | Example |
|---|---|---|
| Page horizontal (desktop) | 64px | `padding: 0 64px` |
| Page horizontal (tablet) | 48px | `padding: 0 48px` |
| Page horizontal (mobile) | 24px | `padding: 0 24px` |
| Section vertical gap | 96px | `gap: 96px` between sections |
| Card padding (desktop) | 32px | `padding: 32px` |
| Card padding (mobile) | 24px | `padding: 24px` |
| Component gap (internal) | 16–24px | `gap: 24px` between cards |
| Tight spacing | 8–12px | Button/label spacing |

### Container & Max-Width

```css
--max-width: 1280px;        /* Default container max-width */
--max-width-content: 960px; /* Narrower for text-heavy sections */
```

### Grid & Layout

**Desktop Grid (1440px+):**
- 12-column grid, 64px gutters
- Cards: 3-column (4 columns wide)
- Hero: full-width to container max

**Tablet Grid (768px–1024px):**
- 8-column grid, 48px gutters
- Cards: 2-column (4 columns wide each)
- Full-width sections remain full

**Mobile Grid (375px–768px):**
- Single-column, 24px gutters
- All cards/sections full-width

---

## Components & Patterns

### Button

**Primary CTA Button** (Magenta)
```css
background: #e91e8c;
color: #ffffff;
padding: 12px 24px;
border-radius: 6px;
font-size: 14–16px;
font-weight: 600;
text-align: center;
cursor: pointer;
transition: all 0.2s ease;

/* Hover */
&:hover {
  background: #c71670;        /* Slightly darker magenta */
  box-shadow: 0 4px 12px rgba(233, 30, 140, 0.3);
}

/* Focus */
&:focus {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}

/* Active */
&:active {
  transform: scale(0.98);
}

/* Disabled */
&:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

**Secondary Button** (Outline)
```css
background: transparent;
color: #f5f5f5;
border: 1px solid #333333;
padding: 12px 24px;
border-radius: 6px;
font-size: 14–16px;
font-weight: 600;

/* Hover */
&:hover {
  border-color: #2563eb;
  background: rgba(37, 99, 235, 0.05);
}

/* Focus */
&:focus {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}
```

**Minimum Touch Target:** 44×44px on mobile

### Card / Surface

```css
background: #1a1f3a;
border: 1px solid #333333;
border-radius: 8px;
padding: 32px;                /* Desktop */
padding: 24px;                /* Mobile */
box-shadow: none;             /* Keep flat, use border for definition */

/* Hover (optional subtle lift) */
&:hover {
  border-color: #2563eb;
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.1);
}
```

### Input Field / Form

```css
background: #0a0e27;
border: 1px solid #333333;
border-radius: 6px;
color: #f5f5f5;
padding: 12px 16px;
font-size: 16px;

::placeholder {
  color: #6b7280;
}

/* Focus */
&:focus {
  border-color: #2563eb;
  outline: none;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
}

/* Error */
&:invalid, &[aria-invalid="true"] {
  border-color: #ef4444;
}
```

### Links & Anchors

```css
color: #2563eb;
text-decoration: none;
cursor: pointer;
transition: color 0.2s ease;

&:hover {
  color: #e91e8c;
  text-decoration: underline;
}

&:focus {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}

/* Visited state (optional) */
&:visited {
  color: #1d4ed8;              /* Darker blue */
}
```

### Focus Indicators

All interactive elements must have visible focus states:

```css
/* Standard focus ring */
outline: 2px solid #2563eb;
outline-offset: 2px;

/* High-contrast focus ring (preferred for dark backgrounds) */
outline: 2px solid #2563eb;
outline-offset: 2px;
box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.2);
```

**Accessibility:** Focus must be visible with high contrast. Never use `outline: none` without providing an alternative focus indicator.

---

## Imagery & Backgrounds

### Background Images (Nano Banana 3.0 Pro via Google Stitch)

All background images are **realistic, cinematic visuals** created by Nano Banana 3.0 Pro via Google Stitch. These images should communicate production capability and creative vision:

#### Hero Background
- **Concept:** Cinematic production pipeline or agent command center in action
- **Mood:** Energetic, professional, forward-momentum
- **Colors:** Dark, moody base with magenta/blue accent lighting
- **Aspect ratio:** 16:9 or wider (scalable to fit container)
- **Size:** Optimized for web (< 500KB)
- **Responsive:** Full-width on desktop, scaled/cropped on mobile without losing key focal points

#### Product Section Backgrounds
- **Concept:** Individual production phases (writing, storyboarding, generation, editing, publishing)
- **Mood:** Professional, focused, detail-oriented
- **Colors:** Cohesive with hero; magenta/blue accents on dark base
- **Aspect ratio:** Flexible per card layout

#### How It Works Visual
- **Concept:** Episode production stages, with agents/tools at each step
- **Mood:** Clear progression, confident execution
- **Colors:** Unified visual language, step highlights in blue or magenta

### Image Implementation Guidelines

1. **Lazy loading:** Use `loading="lazy"` on off-screen images
2. **Responsive sizes:** Use `srcset` and `sizes` attributes for multiple resolutions
3. **Fallback colors:** If image fails to load, background color `#1a1f3a` or `#2a3050` should maintain readability
4. **No text directly on image:** If text overlays image, use semi-transparent overlay (`rgba(10, 14, 39, 0.4)` to `rgba(10, 14, 39, 0.7)`)
5. **Alt text:** Every image must have descriptive `alt` text for accessibility

### Text Overlays on Images

```css
background: linear-gradient(
  180deg,
  rgba(10, 14, 39, 0.2) 0%,
  rgba(10, 14, 39, 0.6) 100%
);
```

This ensures text remains readable over image variations.

---

## Accessibility

### Semantic HTML

```html
<!-- Correct structure -->
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Page Title</title>
  </head>
  <body>
    <header><!-- Navigation, branding --></header>
    <main>
      <section id="section-1">
        <h1>Page Heading</h1>
        <!-- Content -->
      </section>
      <section id="section-2">
        <h2>Section Heading</h2>
        <!-- Content -->
      </section>
    </main>
    <footer><!-- Footer --></footer>
  </body>
</html>
```

### Color Contrast

- **Text on background:** Minimum 4.5:1 (AA), 7:1 (AAA)
- **Interactive elements:** 3:1 for large text, 4.5:1 for normal text
- **Focus indicators:** Must contrast with both focused element and background

### Keyboard Navigation

- **Tab order:** Logical, visible, no traps
- **Focus visible:** Every interactive element must show focus (use CSS `outline` or `box-shadow`)
- **Skip links:** Provide skip-to-main-content link for keyboard users
- **No keyboard traps:** Users can always tab away from focused element

### Screen Reader Support

- **Semantic HTML:** Use `<header>`, `<nav>`, `<main>`, `<article>`, `<section>`, `<footer>`
- **ARIA labels:** Use `aria-label` on icon buttons, `aria-labelledby` on complex sections
- **Images:** Every `<img>` must have descriptive `alt` text
- **Form labels:** `<label>` associated with `<input>` via `for` attribute or containment
- **Headings:** Use proper hierarchy (h1 → h2 → h3, never skip levels)

### Motion & Animations

```css
/* Disable animations for users with reduced-motion preference */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

- **Entrance animations:** OK if fast (< 400ms) and optional
- **Hover effects:** OK if subtle (shadow, color change, slight scale)
- **Continuous loops:** NOT OK (decorative carousels, spinning elements, bouncing animations)

---

## Motion & Animation

### Principles

1. **Purposeful:** Every animation communicates or clarifies an interaction
2. **Fast:** Entrance animations < 400ms, transitions < 200ms
3. **Subtle:** Avoid dramatic movements or effects
4. **Respectful:** Honor `prefers-reduced-motion: reduce`

### Recommended Animations

```css
/* Smooth scroll for anchor links */
html {
  scroll-behavior: smooth;
}

/* Fade-in for page elements */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Use with caution, disable for reduced-motion users */
@media (prefers-reduced-motion: no-preference) {
  section {
    animation: fadeIn 0.4s ease-in;
  }
}

/* Hover / focus state transitions */
button, a {
  transition: all 0.2s ease;
}
```

### Avoid

- Continuous loops (carousels, animations, pulsing)
- Parallax scrolling (unless very subtle and tested for accessibility)
- Auto-playing video or audio (user must control)
- Rapid flashing (> 3 flashes per second)

---

## Responsive Design

### Breakpoints

| Device | Width | Grid | Padding |
|---|---|---|---|
| Mobile | 375px–768px | Single column | 24px |
| Tablet | 768px–1024px | 2–3 columns | 48px |
| Desktop | 1024px–1440px | 3–4 columns | 48px–64px |
| Large Desktop | 1440px+ | 4–12 columns | 64px |

### Mobile-First Approach

Start with single-column mobile layout, progressively enhance:

```css
/* Mobile (default) */
.card {
  width: 100%;
  padding: 24px;
}

/* Tablet and up */
@media (min-width: 768px) {
  .card {
    width: calc(50% - 12px);
    padding: 32px;
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .card {
    width: calc(33.333% - 16px);
    padding: 32px;
  }
}
```

### Testing Dimensions

Validate design at:
- **375px** (iPhone SE, small phones)
- **768px** (iPad, tablets)
- **1024px** (iPad Pro, small laptops)
- **1440px** (standard laptops, desktops)

**Criteria:**
- ✅ Text readable (no wrapping issues, sufficient line length)
- ✅ Navigation accessible (no overflow, tap targets > 44px)
- ✅ Images scale properly (no distortion, proper aspect ratio)
- ✅ No horizontal scrolling
- ✅ Spacing consistent (no cramped sections)

---

## Design Resources

### Gemini Skills

Design decisions are informed by these `.gemini/skills/` resources:

1. **ui-ux-pro-max** (`/.gemini/skills/ui-ux-pro-max/`)
   - 67 design styles
   - 161 color palettes (dark mode reference)
   - 57 font pairings
   - 99 UX guidelines
   - 25 chart types
   - Searchable database for pattern recommendations

2. **design-system** (`/.gemini/skills/design-system/`)
   - Token architecture (primitive → semantic → component)
   - Component specifications
   - Tailwind integration guide
   - Design-to-code handoff patterns

3. **ui-styling** (`/.gemini/skills/ui-styling/`)
   - Tailwind customization
   - Responsive design patterns
   - Component library (shadcn/ui) reference
   - Accessibility best practices
   - Dark mode implementation

### External References

- **Next.js Docs:** `node_modules/next/dist/docs/`
- **Tailwind CSS:** https://tailwindcss.com/ (v4 in this project)
- **WCAG 2.1 AA:** https://www.w3.org/WAI/WCAG21/quickref/
- **MDN Web Docs:** https://developer.mozilla.org/ (for semantic HTML, CSS, accessibility)

---

## Implementation Checklist

Use this checklist when building new pages or components:

### Setup
- [ ] Color palette configured in Tailwind/CSS variables
- [ ] Typography scale defined (font sizes, weights, line heights)
- [ ] Spacing scale applied (padding, margins, gaps)
- [ ] Focus indicator styles applied globally

### Structure
- [ ] Single `<h1>` per page, proper heading hierarchy
- [ ] Semantic HTML (`<header>`, `<main>`, `<section>`, `<footer>`)
- [ ] All interactive elements keyboard-accessible

### Visual
- [ ] Color contrast verified (WCAG AA minimum)
- [ ] Images have descriptive `alt` text
- [ ] Cards, buttons, links styled per component specs
- [ ] Hover and focus states visible and tested
- [ ] Layout responsive at all breakpoints (375px, 768px, 1024px, 1440px)

### Animation & Motion
- [ ] No continuous decorative animations
- [ ] `prefers-reduced-motion: reduce` respected
- [ ] Entrance animations < 400ms, transitions < 200ms

### Accessibility
- [ ] Form labels associated with inputs
- [ ] ARIA labels on icon buttons
- [ ] Tab order logical and visible
- [ ] No keyboard traps
- [ ] Sufficient white space and line length

### Performance
- [ ] Images optimized (< 500KB) and lazy-loaded
- [ ] No render-blocking resources
- [ ] CSS variables used for consistency
- [ ] No unnecessary animations or effects

### Validation
- [ ] HTML valid (no errors in console)
- [ ] CSS lint passes (Prettier, ESLint)
- [ ] Build succeeds without warnings (`npm run build`)
- [ ] Page speed acceptable (LCP, FID, CLS)

---

## Questions & Decisions

| Question | Decision | Owner | Status |
|---|---|---|---|
| Hero background: static image or animation? | Static realistic image (Nano Banana 3.0 Pro via Google Stitch) | Design | Resolved |
| Demo account accessibility? | Public demo route, no auth required (separate from landing page) | Product | To implement |
| Pricing section: linked to purchase flow? | Design placeholder only; no purchase integration in Sprint 001-landing-page | Product | Resolved |
| About section: company vs. product focus? | Product vision + Qwen Cloud Hackathon context | Design | To refine |

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0 | July 3, 2026 | Initial design system document; color, typography, component specs; accessibility and motion guidelines; Nano Banana 3.0 Pro imagery strategy |

---

**Last Updated:** July 3, 2026  
**Next Review:** End of Sprint 001-landing-page implementation

