---
name: Dentista/Odontoiatrico Needs Research 2026
description: Pain points, competitor pricing, compliance requirements, killer features and DB schema implications for Italian dental practice vertical (47k studi)
type: project
---

Research completed 2026-03-31 for vertical: Studio Odontoiatrico (dentista).

Output file: `/Volumes/MontereyT7/FLUXION/.claude/cache/agents/vertical-needs-dentista.md`

**Why:** Dental is FLUXION's highest-WTP vertical — dentists bill €400-€800k/year, lose €15-30k/year to no-shows, and pay €150-300/month for bad software.

**Key findings:**
- Market: ~47.000 studi, 70% piccoli, 30-40% ancora su Excel/carta
- No-show cost: €48-60/hour chair cost, 8-12% no-show rate = €15-30k/year lost per studio
- Competitor pricing: XDENT €59-200+/mese, AlfaDocs €69-109/mese, DentalTrey €150-250/mese
- Biggest pain: phone rings during procedures (dentist can't answer), no-shows on expensive procedures, compliance (GDPR, consenso, sterilization logs, Sistema TS)
- Killer feature: Sara answers the phone while dentist is with patient — ROI in 3-7 days
- Schema needs: multi-chair calendar, odontogramma, anamnesi medica, sterilization log table
- Italian-specific: 95%+ private (no SSN), fatture cartacee (not SDI), Sistema TS annual filing

**How to apply:** When implementing dental vertical, prioritize multi-chair calendar view, quick anamnesi flags (allergies/meds), and Sara's qualification of urgency vs routine booking.
