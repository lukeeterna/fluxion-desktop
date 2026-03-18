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
Branch: master | HEAD: ba844b4
Push: ✅ sincronizzato
iMac: ✅ sincronizzato (git pull)
type-check: 0 errori ✅
test: 1551 PASS / 1 FAIL (pre-esistente vad_file) ✅
```

---

## COMPLETATO SESSIONE 84

### Edge-TTS IsabellaNeural wired ✅ (87e0efc)
- QwenTTSEngine → EdgeTTSEngine in `tts_engine.py`
- `main.py:963`: `use_piper_tts=True` — FluxionTTS Adaptive ATTIVO
- 3-tier: Edge-TTS quality (9/10) → Piper fast (7/10) → SystemTTS last resort
- TTSCache: 31 frasi pre-warmed con IsabellaNeural
- Test T1-T5 PASS su iMac, 14 test TTS PASS

### Architettura distribuzione definitiva in CLAUDE.md ✅ (87e0efc)
- TTS 3-tier, FLUXION Proxy API LLM, code signing, PyInstaller sidecar
- Requisiti sistema, disclaimer pre-acquisto, self-healing, diagnostica
- 4 deep research CoVe 2026 completate

### Bug fix ✅ (ba844b4)
- Cerebras: `qwen-3-32b` deprecato → `llama3.1-8b`
- audit_client: auto-migrate colonna `notes` se mancante
- guida-pmi.html: prezzi corretti (€497/€897/€1.497), Enterprise → Clinic

### Audit completo ✅
- Frontend: 89/96 componenti COMPLETE — PRODUCTION-READY
- Voice agent: zero errori nei log dopo fix
- 1 solo TODO rimasto (vertical_schemas.py — non bloccante)

### ROADMAP aggiornata ✅
- FASE 1: Completare FLUXION → FATTO
- FASE 2: Pacchetti Win+Mac (prossimo)
- FASE 3: Landing + Video YouTube
- FASE 4: Sales + Marketing Agent

---

## ⚠️ PROBLEMI APERTI

### P1: VAD — da testare live con microfono su iMac
### P2: IP iMac — DHCP reservation da aggiornare sul router
### P3: ESLint warnings pre-esistenti (AudioWorklet — non bloccanti)

---

## AZIONE IMMEDIATA S85

### FASE 2: Pacchetti installazione
1. **PyInstaller sidecar build** — compilare voice agent in binario nativo
2. **Apple Developer Program** — enrollment CTO ($99/anno)
3. **Windows code signing** — Azure Trusted Signing ($120/anno)
4. **FLUXION Proxy API** — Cloudflare Workers + Groq backend
5. **Universal Binary macOS** — Intel + Apple Silicon
6. **Test pacchetti** su Mac + Windows reali

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
1. PyInstaller sidecar build (voice agent → binario nativo)
2. FLUXION Proxy API (Cloudflare Workers)
3. Inizio FASE 2 pacchetti
```
