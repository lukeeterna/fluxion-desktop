# FLUXION — Handoff Sessione 84 → 85 (2026-03-18)

## CTO MANDATE — NON NEGOZIABILE
> **"Completare FLUXION al 100%, pacchetti verificati, landing perfetta. POI vendere."**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Voice pipeline: porta 3002 | License server: porta 3010

---

## STATO GIT
```
Branch: master | HEAD: 87e0efc
Push: da fare
iMac: sincronizzato manualmente (scp) ✅
type-check: 0 errori ✅
test: 1551 PASS / 1 FAIL (pre-esistente vad_file) ✅
```

---

## COMPLETATO SESSIONE 84

### Edge-TTS IsabellaNeural wired ✅
- QwenTTSEngine → EdgeTTSEngine in `tts_engine.py`
- `main.py:963`: `use_piper_tts=True` — FluxionTTS Adaptive ATTIVO
- Edge-TTS 7.2.7 installato su iMac, afconvert per MP3→WAV
- 3-tier: Edge-TTS (quality 9/10) → Piper (fast 7/10) → SystemTTS (last resort)
- TTSCache: 31 frasi pre-warmed con IsabellaNeural
- Test T1-T5 PASS su iMac
- 14 test TTS PASS (test_tts_adaptive.py)

### Architettura distribuzione definitiva in CLAUDE.md ✅
- TTS 3-tier cross-platform
- FLUXION Proxy API per LLM (~$34/mese per 1000 clienti)
- Code signing obbligatorio (Apple $99 + Windows $120/anno)
- PyInstaller sidecar per Python voice agent
- Requisiti sistema definitivi
- Disclaimer pre-acquisto
- Self-healing + diagnostica
- Sprint distribuzione (FASE 0-1-2)

### Deep Research CoVe 2026 (4 subagenti) ✅
- TTS cross-platform: `.claude/cache/agents/tts-crossplatform-install-research.md`
- LLM API onboarding: `.claude/cache/agents/llm-api-onboarding-research.md`
- Install compatibility: `.claude/cache/agents/install-compatibility-research.md`
- TTS wiring analysis: `.claude/cache/agents/tts-wiring-analysis.md`

### ROADMAP aggiornata ✅
- Nuove priorità: Completare → Pacchetti → Landing+Video → Sales
- Foundation aggiornata con feature S83-S84

### Riferimenti Anthropic rimossi dal codice distribuito ✅

---

## ⚠️ PROBLEMI APERTI

### P1: guida-pmi.html — prezzi errati
- Dice: Base €297 / Pro €497 / Enterprise €897
- Deve dire: Base €497 / Pro €897 / Clinic €1.497
- Allineare con landing page e LemonSqueezy

### P2: IP iMac — DHCP reservation da aggiornare
- iMac ora su `192.168.1.2` — TODO: fissare sul router

### P3: VAD — da testare live con microfono
- Fix silence_window deployato ma NON testato live

### P4: Push git pendente
- Commit 87e0efc da pushare

---

## AZIONE IMMEDIATA S85

### FASE 1: Completare FLUXION al 100%
1. **Audit completo** — aprire OGNI schermata, verificare OGNI flusso
2. **Fix bug residui** — qualsiasi cosa non funzioni
3. **Fix guida-pmi.html** — prezzi corretti
4. **Test VAD live** con microfono su iMac
5. **Push git** e sync iMac

### FASE 2: Pacchetti installazione (dopo audit)
1. Apple Developer Program enrollment
2. Windows code signing
3. PyInstaller sidecar build
4. FLUXION Proxy API (Cloudflare Workers)
5. Test pacchetti su Mac + Windows reali

### FASE 3: Landing + Video (dopo pacchetti)
1. Screenshot TUTTE le funzioni
2. Copy enterprise-grade con esempi PMI concreti
3. Video demo YouTube
4. Aggiornare landing con tutte le feature

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 85:
1. Audit completo FLUXION — verificare ogni schermata e flusso
2. Fix bug residui + guida-pmi.html prezzi
3. Push git + inizio FASE 2 (pacchetti)
```
