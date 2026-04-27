---
name: funnel_audit_s170
description: S170 conversion funnel audit — WA cold outreach to Stripe checkout. Key drop-off points, top 10 issues, quick wins, anti-patterns, mobile checklist.
type: project
---

Full funnel audit completed 2026-04-27. Report at `.claude/cache/agents/s170-conversion-research/02-funnel-ux-audit.md`.

Estimated end-to-end conversion: 0.2–0.3%. Optimized target: 0.6–1.2%.

Top 3 critical issues:
1. No OG meta tags → WA link preview is blank (fix: add og:image/og:description to landing head)
2. No copy above video → play rate low (fix: add headline + 1-line teaser above iframe)
3. Garanzia 30 giorni invisible → checkout blocker (fix: dedicated section before pricing)

Quick wins already identified with exact line numbers in landing/index.html and templates.py.

**Why:** Cold WA to €497 one-time purchase is a high-friction funnel. Italian PMI owners 40–55 are skeptical of cold messages. Every friction point compounds.

**How to apply:** When reviewing landing or WA templates, prioritize trust signal visibility and reducing friction before price is shown.
