# FLUXION — Handoff Sessione 119 → 120 (2026-03-29)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni."**
> **"A PROVA DI BAMBINO. L'utente PMI non sa fare nulla se non 2 click."**
> **"LASCIALI A BOCCA APERTA!"**
> **"Capire cosa ho → capire cosa è possibile → definire insieme cosa fare. MAI codice come secondo step."**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Tauri dev porta 1420+3001 | Voice pipeline porta 3002

---

## COMPLETATO SESSIONE 119

### Bug fix
- `test_abbonamento palestra` NoneType fix → 2002 PASS (da 574)
- Pushato + sincronizzato iMac

### VoIP Sara — EHIWEB VivaVox (0972536918)
**Stato: SIP REGISTER funziona, chiamata arriva, audio INCOMPRENSIBILE**

Lavoro svolto:
1. Fixati 6 bug nel voip.py custom (answer_call Via, async callback, resampling, TTS rate, VAD)
2. Fix Python 3.9 compat: sock_recvfrom/sock_sendto → run_in_executor
3. Fix porta 5080 (5060 occupata da Traccar su iMac)
4. STUN discovery con stun.voip.vivavox.it:3478 → IP pubblico nel Contact
5. rport/received parsing da REGISTER 200 OK (RFC 3581)
6. CRLF keepalive ogni 20s per NAT mapping
7. RTP NAT pinhole (dummy packet)
8. G.711 codec fix: audioop.lin2ulaw/ulaw2lin (stdlib)
9. RTP marker bit su primo pacchetto
10. Greeting fix: SessionChannel.VOICE enum vs stringa
11. Tentato pyVoIP 1.6.8 → FALLITO (bug re-register auth)

**Risultato**: Chiamata arriva (INVITE ricevuto, 180 Ringing, 200 OK, Call Answered), Sara genera greeting TTS e lo invia via RTP, ma **l'audio al telefono è incomprensibile**. Il codec e TTS funzionano correttamente in test locale. Il problema è nel trasporto RTP (probabilmente il media proxy EHIWEB non decodifica i nostri pacchetti correttamente, o symmetric NAT per RTP).

### Decisione finale: pjsua2 (pjsip)
**Deep research CoVe 2026 completata** — 12 approcci valutati.
**VINCITORE: pjsua2 Python SWIG bindings** — lo standard mondiale per VoIP.

Vantaggi:
- ICE+STUN+TURN integrato → funziona dietro QUALSIASI NAT
- Codec negotiation automatica (G.711a/u, G.729)
- Jitter buffer, re-registration, SRTP
- AudioMediaPort per bridge audio Sara ↔ pjsua2
- Zero costi (BSD license)

Research: `.claude/cache/agents/universal-voip-solution-research.md`

---

## DA FARE S120 — PRIORITÀ ASSOLUTA: pjsua2

### Step 1: Installare prerequisiti su iMac
```bash
# Homebrew (se non installato)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install swig

# Oppure SWIG da source:
curl -L https://github.com/swig/swig/archive/refs/tags/v4.2.1.tar.gz | tar xz
cd swig-4.2.1 && ./autogen.sh && ./configure && make && sudo make install
```

### Step 2: Compilare pjsip + pjsua2 SWIG
```bash
# Clone pjsip
git clone https://github.com/pjsip/pjproject.git
cd pjproject

# Configure per macOS x86_64
./configure --enable-shared --with-python=/Library/Developer/.../Python

# Build
make dep && make

# Build Python SWIG bindings
cd pjsip-apps/src/swig/python
make
python setup.py install
```

### Step 3: Creare bridge audio Sara
- `voip_pjsua2.py` con SaraAudioPort, SaraCall, SaraAccount
- Test REGISTER su sip.vivavox.it con STUN
- Test chiamata in entrata con greeting

### Step 4: Windows build
- GitHub Actions workflow per compilazione Windows x64
- Output: `_pjsua2.pyd` + `pjsua2.py`

### Step 5: Bundle nel PyInstaller sidecar
- Aggiungere .so/.pyd al bundle
- Test installazione pulita

### Alternativa: Landing + Deploy (Phase 11)
Se pjsua2 richiede troppo tempo, procedere con Phase 11 (Landing + video YouTube) in parallelo.

---

## STATO GIT
```
Branch: master | HEAD: bbb1143
Commits S119: 12 commit (bug fix + VoIP)
type-check: 0 errori
voice tests: 2002 PASS / 4 FAIL (pre-existing VAD+VoIP)
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 9:   Screenshot Perfetti  ✅ COMPLETATO (S115)
Phase 10:  Video V7             ✅ COMPLETATO (S117)
Phase 10b: Sara Features        ✅ COMPLETATO (S118)
Phase 10c: Sara VoIP EHIWEB    🔄 IN PROGRESS — pjsua2 da compilare
Phase 11:  Landing + Deploy     ⏳ (video YT non ancora caricato)
Phase 12:  Sales Agent WA       ⏳
Phase 13:  Post-Lancio          ⏳
```

---

## FILE CHIAVE SESSIONE
- `voice-agent/src/voip.py` — custom SIP client (funziona ma audio broken)
- `voice-agent/src/voip_pyvoip.py` — pyVoIP wrapper (tentativo fallito)
- `.claude/cache/agents/universal-voip-solution-research.md` — research 12 approcci
- `.claude/cache/agents/voip-onboarding-ux-research.md` — research UX setup
- `.planning/debug/voip-debug-diagnosis.md` — diagnosi 3 bug NAT

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 120.
PRIORITÀ: Compilare pjsua2 su iMac → test chiamata EHIWEB → bridge audio Sara.
Voice agent su iMac (192.168.1.2:3002).
```
