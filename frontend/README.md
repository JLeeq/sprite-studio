## Hybrid Frontend (Next.js + Tailwind)

This folder hosts the presentation-only part of the UI. It complements the existing Gradio application by handling lightweight “portfolio” screens while Gradio continues to power interactive generation workflows.

### Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS

### Goals

1. Showcase a modern landing/dashboard experience that matches the enhanced-inspired styling.
2. Keep complex interactions (file uploads, preview canvases, generation buttons) inside Gradio until the FastAPI backend is complete.
3. Provide a clean hand-off path: the Next.js app talks to the Gradio UI through an embedded iframe today, and can switch to direct FastAPI calls later without redesigning the surface layer.

### Getting Started

```bash
cd frontend
npm install
npm run dev
```

Set the Gradio deployment URL (local or remote) so the iframe knows where to point:

```bash
export NEXT_PUBLIC_GRADIO_URL="http://127.0.0.1:7860"
```

### Directory Layout

- `app/` – App Router entry points and shared layout
- `components/` – Lightweight UI primitives (Hero, FeatureCard, HybridIframe, etc.)
- `app/globals.css` – Tailwind + design tokens consistent with the Gradio theme
- `docs/ui_inventory.md` (root) – Source of truth for the shared design language used by both stacks

### Migration Path

1. **Phase 1 (current)** – Next.js shows marketing/overview content and embeds the Gradio Blocks UI for heavy interactions.
2. **Phase 2** – Introduce FastAPI endpoints that mirror Gradio actions; Next.js starts calling them directly while Gradio remains as a fallback/staging interface.
3. **Phase 3** – Decommission Gradio UI once the React components reach feature parity.

This structure satisfies the “hybrid” requirement today and keeps the repo ready for a deeper split later. Feel free to extend the Next.js app with additional routes (e.g., `/docs`, `/showcase`) or to add authenticated dashboards when Supabase is introduced.

