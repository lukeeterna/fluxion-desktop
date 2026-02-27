
## Sprint 2026-02-27 — Aggiunte CTO

### P0 — Revenue (in corso)
- [x] **Video marketing 70s** — `out/marketing_70s.mp4` ✅ 71.4s 1280x720 €297
- [ ] **LemonSqueezy approvazione** — risposta a Kashish in corso
- [ ] **Landing deploy** — https://lukeeterna.github.io/fluxion-desktop/

### P1 — Post-approvazione LemonSqueezy
- [ ] **Tutorial video ibrido** (10-15min per verticale)
  - Approccio: Intro/Outro Remotion + screencap OBS su iMac
  - Piano completo: `scripts/video-remotion/TUTORIAL_PLAN.md` (705 righe, 82 scene, 6 verticali)
  - Da fare: installare OBS su iMac, registrare screencap per ogni verticale
  - Priorità: Salone → Palestra → Odontoiatria → Fisioterapia → Estetica → Officina
- [ ] **Test live voice agent** — scenari T1 su iMac
- [ ] **Build v0.9.0 → tag** — solo dopo test live

### P2 — Sicurezza & Privacy (da fare dopo video marketing)
- [ ] **ZeroClaw sandbox**: Docker isolato o macOS Sandbox profile — vedi `.planning/research/security-anonymity-2026.md`
- [ ] **Anonimato operativo**: VPN no-log + DNS-over-HTTPS + browser hardening (ricerca in corso)
- [ ] **Voice agent 0.0.0.0 → 127.0.0.1**: bind locale se Bridge non è su rete pubblica

### P3 — Anti-Context-Rot (workflow permanente)
- [ ] Hook pre-task: auto-write HANDOFF ogni N tool calls
- [ ] /compact obbligatorio a 40% context
- [ ] Commit frequenti come checkpoint (ogni feature = commit)
