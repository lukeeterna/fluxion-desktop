# FLUXION — Handoff Sessione 35 (2026-03-09)

## ⚡ PRINCIPIO CoVe 2026 — SEMPRE IN OGNI TASK (CTO Approvato Sessione 31)

> **"Non implementare feature. Colma gap reali delle PMI italiane."**
>
> Ogni commento, ogni componente deve portare la risposta: *"perché questo è world-class?"*
>
> Deep Research CoVe 2026 = **identifica il gap reale** → implementa il salto competitivo.

---

## ⚠️ LEGGERE PRIMA DI TUTTO — GUARDRAIL SESSIONE

**Working directory corretta**: `/Volumes/MontereyT7/FLUXION`
**Memory corretta**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`

---

## STATO GIT

```
Branch: master | HEAD: f45d528
CI: ✅ verde
type-check: 0 errori
Modifiche pendenti: nessuna (working tree pulito)
```

---

## COMPLETATO SESSIONE 35

| Lavoro | Commit | Note |
|--------|--------|------|
| Commit schede F06 (tab layout + video upload) | f45d528 | 8 schede, 311 righe |
| Verifica server.py enterprise→clinic | — | già fixato in a6d0d1f, confermato |
| Foto stock CC0 Pexels — 44 foto, 8 categorie | — | in `_bmad-output/f06-media/` |
| Script `scripts/download-stock-photos.py` | — | PEXELS_API_KEY in .env |
| MEMORY.md aggiornata con Pexels key | — | NON chiedere mai all'utente |
| Descrizioni prodotti LemonSqueezy | — | nomi esatti: FLUXION Base/Pro/Clinic |

---

## PROSSIMO TASK: F07 completamento + Menu fix

### A — Menu Sidebar (da fixare PRIMA degli screenshot)
- Utente ha segnalato formattazione non corretta
- File: `src/components/layout/Sidebar.tsx`
- **Da fare**: chiedere all'utente screenshot/descrizione del problema e fixare

### B — Screenshot app per LemonSqueezy
- Avviare `npm run dev` su MacBook
- Screenshot: Dashboard, Calendario, Sara Voice, Scheda cliente con media, Impostazioni/SDI, WhatsApp AI, Multi-verticale
- Upload su LemonSqueezy (1600×1200 4:3 raccomandato)

### C — LemonSqueezy store (Luke deve fare manualmente)
Prodotti da creare con nomi ESATTI (server fa `.lower()` + exact match):

| Nome prodotto | Prezzo | Tax |
|---|---|---|
| `FLUXION Base` | €497 | eCommerce standard |
| `FLUXION Pro` | €897 | eCommerce standard |
| `FLUXION Clinic` | €1.497 | eCommerce standard |

- Generate license keys: ❌ OFF (il server genera chiavi Ed25519)
- Dopo creazione prodotti → crea Webhook → fornire **Signing Secret**

### D — config.env (dopo aver le credenziali da LemonSqueezy)

```env
LS_WEBHOOK_SECRET=<da LemonSqueezy webhook settings>
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=gianlucanewtech@gmail.com
SMTP_PASS=lzhx yujp hvel epyb        # già in .env
FLUXION_KEYGEN_PATH=<path a fluxion-keygen binary>
KEYPAIR_PATH=<path a keypair.json>
PORT=3010
ACTIVATE_URL_BASE=<URL Cloudflare Tunnel>
```

### E — Server iMac + Cloudflare Tunnel
```bash
# iMac — avvia server
cd '/Volumes/MacSSD - Dati/FLUXION/scripts/license-delivery'
pip3 install aiohttp aiosmtplib
python3 server.py

# Cloudflare Tunnel (se già configurato)
cloudflared tunnel run fluxion
```

### F — In-app upgrade path UI Tauri (STEP 6)
- LicenseManager già implementato (F05, commit a4af4fc)
- Da aggiungere: modale upgrade Base→Pro→Clinic con link checkout LemonSqueezy
- File: `src/components/license/` — vedi LicenseManager esistente

---

## ACCEPTANCE CRITERIA F07 (tutti da completare)

- [ ] Menu Sidebar formattato correttamente
- [ ] Screenshot app pronti per LemonSqueezy (min 3 per prodotto)
- [ ] 3 prodotti LemonSqueezy creati con nomi esatti
- [ ] Webhook configurato → Signing Secret nel config.env
- [ ] config.env compilato su iMac
- [ ] Server avviato su iMac porta 3010
- [ ] Cloudflare Tunnel espone `/webhook/lemonsqueezy`
- [ ] Test acquisto end-to-end → licenza in <5s
- [ ] In-app upgrade UI (Base → Pro → Clinic)

---

## NOTE TECNICHE

- **SMTP password** già disponibile in `.env`: `lzhx yujp hvel epyb` (Gmail App Password)
- **PEXELS_API_KEY** in `.env` — non chiedere mai all'utente
- **Foto stock**: `_bmad-output/f06-media/{fitness|fisioterapia|odontoiatrica|veicoli|estetica|parrucchiere|medica|carrozzeria}/` — 44 foto CC0
- **server.py**: già completo e bugfixato — solo config.env mancante

---

## PROMPT RIPARTENZA SESSIONE 36

```
Sessione 36 — F07 LemonSqueezy completamento

⚠️ PRIMA DI TUTTO:
- Working dir: /Volumes/MontereyT7/FLUXION
- Leggi MEMORY.md da /Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md
- HEAD: f45d528 | CI ✅ verde | working tree pulito

STATO F07:
- server.py ✅ completo e bugfixato
- Foto stock 44 CC0 Pexels ✅ in _bmad-output/f06-media/
- Menu Sidebar: segnalato problema formattazione — da fixare PRIMA degli screenshot
- LemonSqueezy store: NON ancora creato (Luke deve creare 3 prodotti)
- config.env: NON esiste — attesa credenziali da LemonSqueezy

PROSSIMI STEP:
1. Fix menu Sidebar (chiedere descrizione/screenshot problema)
2. npm run dev → screenshot app → upload LemonSqueezy
3. Luke crea store + 3 prodotti + webhook → fornisce Signing Secret
4. Creare config.env → avviare server iMac porta 3010
5. Cloudflare Tunnel → test end-to-end
6. In-app upgrade UI Tauri

Procedi con RESEARCH → PLAN → IMPLEMENT → VERIFY → DEPLOY
```
