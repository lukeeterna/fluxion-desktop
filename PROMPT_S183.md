# PROMPT RIPARTENZA — Sessione 183 (Sprint Gate 1: BUILD)

**Copia tutto sotto in nuova sessione Claude Code (MacBook):**

---

```
Sessione 183. Sprint Gate 1 — Categoria A (Build & Distribution).

STEP 0 OBBLIGATORIO: leggi DIRETTIVA FOUNDER S181 in cima HANDOFF.md.
CTO autonomo, founder paga €220/mese. NO compromessi, gate strict.

CONTEXT:
- S182 ha prodotto PRE-LAUNCH-AUDIT.md (22 P0 / 21 P1 / 12 P2) + ROADMAP_S183_S190.md
- Verdetto: lancio NON ammissibile. Soft-launch dopo Gate 2, lancio dopo Gate 4.
- iMac reachable via SSH alias "imac" (192.168.1.2), repo sync su ea6fa7e0.
- Servizi 3001/3002 NON serve avviare in S183 (sono per E2E S184).

GOAL S183 (~12h, 9 task):
1. A-1 PyInstaller arm64 voice-agent (iMac SSH)
2. A-1 Tauri Universal Binary x86_64+arm64 + lipo
3. A-4 Code-sign ad-hoc + entitlements + spctl verify
4. A-2 GitHub Actions Win MSI build (free tier)
5. A-2 Win MSI smoke test su Win10/Win11 VM
6. A-3 Tauri auto-updater configure + chiave + GitHub Releases endpoint
7. A-5 landing/come-installare.html aggiungi sezione SmartScreen Windows
8. A-6 HW test matrix Mac Intel + Mac M1 + Win10 + Win11
9. A-7 GitHub Releases v1.0.1 universal DMG + Win MSI + auto-update manifest
10. A-8 cleanup *.backup* files + .gitignore

VERIFY E2E PASS obbligatorio prima chiusura S183:
- [ ] Universal DMG: lipo -info mostra x86_64+arm64
- [ ] DMG installabile su Mac Intel + Mac M1
- [ ] Win MSI installabile su Win10 + Win11
- [ ] App lancia su 4/4 OS senza errori
- [ ] Auto-updater controlla GitHub Releases endpoint OK (200 + manifest valido)
- [ ] landing/come-installare.html HTTP 200 con sezione SmartScreen presente

VINCOLI:
- Zero costi (GitHub Actions free tier per Win build)
- NO --no-verify (pre-commit hook deve passare)
- E2E PASS obbligatorio prima done
- Rust/build SOLO su iMac via SSH (NO MacBook)
- macOS: ad-hoc signing + Gatekeeper doc (no certificato Apple Developer)
- Windows: MSI unsigned + SmartScreen doc (no certificato EV)

PROTOCOLLO ESECUZIONE PER OGNI TASK A-N:
1. Subagent specialista (vedi ROADMAP_S183_S190.md colonna Agent)
2. Implementa
3. Test E2E
4. Commit atomico (S183-AN: ...)
5. Verifica passing prima del prossimo

PRIMO COMANDO S183:
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && ls -la build/ dist/ 2>/dev/null; uname -m; python3 --version"

(verifica stato voice-agent + arch iMac + Python disponibile per PyInstaller arm64)

POI procedi A-1: subagent installer-builder + imac-operator paralleli per:
- PyInstaller arm64 venv setup su iMac
- Tauri targets setup (rustup target add aarch64-apple-darwin)

Riferimenti chiave:
- PRE-LAUNCH-AUDIT.md (audit completo)
- ROADMAP_S183_S190.md (sprint plan dettagliato)
- HANDOFF.md (stato + direttiva founder S181)
- .claude/cache/agents/s182-*.md (research subagent S182)

Founder ON iMac (gianlucadistasi@iMac-di-gianluca, IP 192.168.1.2).
Tu CTO decidi tutto. Founder valida solo se: blocker fuori budget /
legalmente ambiguo / scope vision business.

GO.
```

---

## QUICK START (alternativa più corta se nuova sessione fresh context)

```
Leggi PRE-LAUNCH-AUDIT.md sezione "CATEGORIA A" + ROADMAP_S183_S190.md sezione "SPRINT S183".
Esegui A-1..A-8 in ordine. CTO autonomo, founder paga €220/mese, NO compromessi.
PRIMO COMANDO: ssh imac "uname -m && python3 --version && cd '/Volumes/MacSSD - Dati/fluxion' && git log --oneline -1"
```

---

**File**: `PROMPT_S183.md` (root repo)
**Generato**: 2026-04-30 fine S182, context 83%
**Per ripartenza**: copia il blocco ``` in nuova sessione Claude Code MacBook.
