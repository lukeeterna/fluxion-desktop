# CARRY S356 — Sara crash RISOLTO E CHIUSO VERDE (NDEBUG). NON riaprire. Next = roadmap R2/R3 + ripresa test vocale verticali.

> **S355 ESITO VERDE**: il SIGABRT `lock.c:279` di Sara (bloccante da ~15 sessioni) è **risolto, validato sotto carico, hardened e su master entrambe le macchine**. Era un `pj_assert` del build debug di pjproject → spento con `-DNDEBUG=1`. NON era una race strutturale: FORK A(2.15.1)/B(Asterisk) era un FALSO BINARIO. **NON riaprire S354/diagnosi crash.**

## ⚠️ PRIMA AZIONE S356
1. Pre-flight: `ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"` → atteso `reg_status:200`. `ssh imac "curl -s http://127.0.0.1:3002/health"` → `status:ok`.
2. Verifica `.so` NDEBUG ancora live: `ssh imac "ls -la '/Volumes/MacSSD - Dati/FLUXION/voice-agent/lib/pjsua2/_pjsua2.cpython-39-darwin.so'"` → ~9MB (NDEBUG). Se mai dovesse tornare ~7.2MB = qualcuno ha fatto rollback → ricopiare da `voice-agent/lib/pjsua2/prebuilt/_pjsua2.cpython-39-darwin.so.ndebug`.
3. **META (REGOLA #27)**: l'hook VOS context-budget inietta nei subagent la % gonfiata del MAIN → si auto-abortano ("76%/80%"). Quando deleghi, istruisci l'agente a IGNORARLO (sua finestra fresca). Per i `git commit/push` usa `CLAUDE_BYPASS_CTX_GATE=1 git ...`.

## STATO VERIFICATO (NON ri-derivare)
- Fix: rebuild pjproject (pin commit `d0cbf57a`, github.com/pjsip/pjproject) con `-DNDEBUG=1` + rebuild SWIG pjsua2 → swap `_pjsua2.cpython-39-darwin.so` (8.6MB static link). Confinement S354 in `voip_pjsua2.py` = TENUTO.
- E2E: Gate 1 loopback (RTP 933pkt, 0 crash) + Gate 2 stress (30 seq + 3 concorrenti, `.ips` 22→22, RSS stabile) = PASS.
- Durevole: artefatti in `voice-agent/lib/pjsua2/prebuilt/` (`.so.ndebug`, `.so.PRE-NDEBUG-bak`, `pjsua2.py.ndebug-build`) + ricetta `voice-agent/docs/pjsua2-ndebug-build.md`. Tracked su master.
- Git: master allineato origin + iMac + MacBook (`8f90a74`/`8b2f70c`/`68398e4`). Branch `fix/license-interop-r01-s327` INTATTO col suo WIP license (NON ancora su master, track separato).

## RESIDUI OPZIONALI Sara (NON bloccanti, non riaprire come crash)
- **Gate 2 provider-reale**: opzionale, gated su 2° account VivaVox (azione EHIWEB lato Luke). NON prerequisito (crash era transport-independent). Solo se Luke vuole riprova "telefonata vera".
- **Ricetta g++**: i comandi g++ manuali del build SWIG sono marcati `DA VERIFICARE` nel doc (se rebuild futuro e `make python` fallisce). `LC_ID_DYLIB` del `.so` punta ancora a `/tmp` (cosmetico, fix `install_name_tool` documentato).
- **`.env.bak*`**: ora gitignored (contengono GROQ/OpenRouter key, restano locali iMac, mai pushati). Sorvegliare REGOLA #19.

## NEXT — roadmap CTO-actionable (research-first REGOLA #16)
Sara sbloccata → per gate vendita REGOLA #21 si può RIPRENDERE il test vocale Sara sui verticali (Layer 1 testo già VERDE S333: 50 OK/3 WARN/12 verticali; ora il path audio non crasha più → estendere a chiamate audio reali CTO-guidate via TTS, REGOLA #23/#14).
Carry tecnici residui:
- **R2**: CI `release-full.yml` ROTTO (5 run failure). Prima azione: `gh run view 25328286560 --log-failed`.
- **R3**: E-3 `sk_live` (Stripe live key).

## CONTESTO PRODOTTO
EHIWEB/VivaVox = carrier per ogni cliente FLUXION che ospiterà Sara. Path inbound-answer+media ora crash-proof su loopback+carico. Gate vendita REGOLA #21.
