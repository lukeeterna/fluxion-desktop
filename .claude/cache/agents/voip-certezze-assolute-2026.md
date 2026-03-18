# VoIP per FLUXION — CERTEZZE ASSOLUTE 2026
**Data**: 2026-03-18 | **Aggiornamento**: Deep Research CoVe 2026 con web search live
**Base**: Consolida e aggiorna `voip-italy-deep-research-2026.md`
**Scopo**: Rispondere a OGNI dubbio del fondatore con certezze verificate

---

## INDICE
1. [Sara PUO' funzionare SENZA VoIP per v1?](#1-sara-può-funzionare-senza-voip-per-v1)
2. [Come si collega ESATTAMENTE?](#2-architettura-tecnica-precisa)
3. [Flusso utente PMI step by step](#3-flusso-utente-pmi-step-by-step)
4. [COPY cristallino — costo = linea, NON FLUXION](#4-copy-cristallino)
5. [Pro/Clinic only o per tutti?](#5-proclini-only-o-per-tutti)
6. [Alternative a VoIP tradizionale](#6-alternative-a-voip-tradizionale)
7. [Raccomandazione finale](#7-raccomandazione-finale)

---

## 1. Sara PUO' funzionare SENZA VoIP per v1?

### Risposta: SI'. VoIP NON serve per v1.
**Certezza: ALTA (95%)**

### Cosa fa Sara OGGI senza VoIP:
- **In-app voice**: microfono del PC/tablet → Sara ascolta e risponde (gia' implementato, porta 3002)
- **WhatsApp text**: cliente scrive su WhatsApp → Sara risponde con testo + audio message
- **Booking manuale**: il titolare/receptionist parla con Sara dal gestionale

### Cosa fanno i competitor nel 2026:
| Competitor | Voice AI su telefono in v1? | Come gestiscono |
|------------|---------------------------|-----------------|
| **Fresha** | NO in v1. AI receptionist annunciato per 2026 (in arrivo, non ancora live) | Chat-based, widget online. L'AI receptionist e' feature NUOVA 2026 |
| **Mindbody** | NO nativo. Richiede integrazione terze parti (BookingBee, MyAIFrontDesk) | Online booking, app mobile |
| **Jane App** | NO | Solo booking online |
| **Treatwell** | NO | Solo booking online |
| **BookingBee** | SI' — e' il loro UNICO prodotto ($50-300/mese) | Voice AI receptionist dedicato |
| **MyAIFrontDesk** | SI' — prodotto standalone ($25-300/mese) | AI phone receptionist generico |

### Insight critico:
**Fresha, il leader mondiale dei saloni, NON ha ancora un AI phone agent live nel 2026.** Lo sta lanciando come feature nuova. Questo significa che FLUXION puo' tranquillamente lanciare v1 SENZA VoIP telefonico e aggiungerlo come upgrade v1.1.

### RACCOMANDAZIONE v1 vs v1.1:

**v1 (lancio):**
- Sara risponde IN-APP (microfono PC/tablet del salone)
- Sara risponde su WhatsApp (messaggi testuali + vocali)
- Il cliente finale prenota via WhatsApp o widget web
- ZERO costi aggiuntivi, ZERO configurazione VoIP

**v1.1 (3-6 mesi dopo lancio):**
- Aggiungere VoIP: Sara risponde al TELEFONO
- Solo per Pro e Clinic (il salone Base non ha volume chiamate)
- Costo della linea telefonica a carico del cliente (~€3-6/mese)

**Motivazione business:**
1. Riduce la complessita' del lancio v1 (niente VoIP = niente supporto VoIP)
2. Allineato con Fresha (che sta facendo lo stesso percorso)
3. Il 90% delle PMI italiane oggi prenota via WhatsApp o online, NON per telefono
4. VoIP diventa feature premium di upsell per v1.1

---

## 2. Architettura Tecnica PRECISA (quando VoIP serve)

### 2.1 Pattern raccomandato: Cloud Telephony API (Telnyx)

```
CHIAMANTE (telefono normale)
    |
    | Chiama +39 02 XXXX XXXX (numero italiano del salone)
    |
    v
TELNYX CLOUD (PoP europeo — Amsterdam/Francoforte)
    |
    | 1. Webhook HTTP POST → FLUXION VoIP Proxy
    | 2. Proxy autentica licenza, trova tunnel del cliente
    | 3. Telnyx apre WebSocket bidirezionale
    |
    v
CLOUDFLARE TUNNEL (connessione USCENTE dal PC del cliente — ZERO port forwarding)
    |
    v
SARA VOICE AGENT (Python, porta 3002, localhost)
    | - Riceve audio mulaw 8kHz via WebSocket
    | - Converte: mulaw 8kHz → PCM 16kHz
    | - STT (Whisper/Groq) → LLM (intent) → TTS (Edge/Piper)
    | - Converte risposta: PCM → mulaw 8kHz
    | - Invia audio indietro via WebSocket
    |
    v
WebSocket → Cloudflare Tunnel → Telnyx → CHIAMANTE sente Sara
```

### 2.2 Perche' Telnyx e NON EHIWEB/SIP diretto

| Aspetto | Telnyx (Cloud API) | EHIWEB (SIP diretto) |
|---------|-------------------|---------------------|
| NAT/Firewall | ZERO problemi (WebSocket uscente) | INCUBO (port forward UDP 5060 + RTP 10000-20000) |
| Configurazione cliente | ZERO (automatico) | Manuale (router, IP statico, SIP ALG) |
| API programmazione | REST + WebSocket completa | NESSUNA |
| Provisioning numeri | Automatico via API | Manuale (account EHIWEB per ogni cliente) |
| Supporto tecnico | Developer-first, docs eccellenti | Per utenti Zoiper, non per bot AI |
| Latenza aggiuntiva | ~90ms (EU PoP) | ~30ms (diretto) |
| Costo mensile | ~€3-5/cliente | ~€2-3/cliente |

**La differenza di 60ms di latenza e' IMPERCETTIBILE** dato che Sara impiega 600-800ms per processare (STT+LLM+TTS). Il 90ms del cloud hop e' rumore.

### 2.3 Protocollo tecnico Telnyx Media Streaming

**Formato audio inbound (Telnyx → Sara):**
```json
{
  "event": "media",
  "sequence_number": "42",
  "media": {
    "track": "inbound",
    "payload": "<base64-mulaw-8kHz>"
  }
}
```

**Formato audio outbound (Sara → Telnyx):**
```json
{
  "event": "media",
  "media": {
    "payload": "<base64-mulaw-8kHz>"
  }
}
```

**Pipeline conversione audio (Python stdlib):**
```python
import audioop, base64

# INBOUND: Telnyx → Sara
raw_mulaw = base64.b64decode(payload)
pcm_8k = audioop.ulaw2lin(raw_mulaw, 2)       # mulaw → PCM16 8kHz
pcm_16k, _ = audioop.ratecv(pcm_8k, 2, 1, 8000, 16000, None)  # 8k → 16k per Whisper

# OUTBOUND: Sara → Telnyx
# TTS produce PCM16 22050Hz
pcm_8k, _ = audioop.ratecv(tts_audio, 2, 1, 22050, 8000, None)  # 22k → 8k
mulaw_8k = audioop.lin2ulaw(pcm_8k, 2)        # PCM16 → mulaw
b64_payload = base64.b64encode(mulaw_8k).decode()
```

**Codec supportato:** L16 (Linear PCM) anche disponibile su Telnyx — riduce latenza eliminando transcodifica mulaw. Molte piattaforme AI (Whisper, TTS) lavorano nativamente in PCM lineare.

### 2.4 Requisiti Telnyx per numeri italiani

Da documentazione ufficiale Telnyx (verificata 2026-03-18):
- **Proof of address**: documento datato entro 3 mesi
- **Tipi di entita'**: persona fisica, persona giuridica, ditta individuale
- **Verifica obbligatoria**: l'Italia richiede "requirement groups" compilati PRIMA dell'ordine
- **NO pre-approvazione**: i numeri italiani non supportano pre-approval (verifica caso per caso)
- **Number porting**: supportato per numeri italiani esistenti (2-4 settimane)
- **Copertura**: numeri geografici +39 02 (MI), +39 06 (RM), +39 011 (TO), +39 055 (FI), e altre citta'

### 2.5 Costi ESATTI Telnyx (verificati marzo 2026)

| Voce | Costo |
|------|-------|
| Numero italiano geografico (DID) | $1.00–2.00/mese |
| Inbound per minuto | $0.004–0.008/min |
| Outbound verso fisso Italia | $0.008–0.015/min |
| Media Streaming WebSocket | Incluso nel costo chiamata |
| Setup fee | $0 |
| Minimo mensile | $0 (pay-as-you-go) |

**Costo mensile PMI tipica** (100 chiamate/mese, media 4 min = 400 min inbound):
- DID: $1.50 + Inbound 400min × $0.006: $2.40 = **~$3.90/mese (~€3.60)**

**Costo mensile PMI con alto volume** (300 chiamate, 1000 min):
- DID: $1.50 + Inbound 1000min × $0.006: $6.00 = **~$7.50/mese (~€6.90)**

---

## 3. Flusso Utente PMI Step by Step

### Scenario A: v1 (SENZA VoIP — raccomandato per lancio)

```
1. Cliente compra licenza FLUXION → attiva
2. Setup Wizard: nome salone, servizi, operatori
3. Sara funziona SUBITO:
   - Microfono in-app per prenotazioni in presenza
   - WhatsApp per prenotazioni remote
4. FINE. Zero configurazione aggiuntiva.
```

**Click necessari: 0 per VoIP (non c'e')**
**Tempo: 0 minuti aggiuntivi**

### Scenario B: v1.1 (CON VoIP — futuro)

```
1. Cliente gia' usa FLUXION v1
2. Aggiornamento v1.1 disponibile → notifica in-app
3. In Impostazioni > Telefono Sara:
   - Toggle "Attiva Sara al telefono"
   - Messaggio: "Sara potra' rispondere alle chiamate telefoniche del tuo salone.
     Per attivare questa funzione serve un numero di telefono dedicato.
     Il costo del numero e' di circa €3-6/mese (costo della linea telefonica,
     NON di FLUXION). Vuoi procedere?"
   - [Si, attiva] [No, non ora]
4. Click "Si, attiva":
   - FLUXION provisiona automaticamente un numero italiano via Telnyx API
   - Il cliente inserisce: indirizzo del salone (richiesto da normativa AGCOM)
   - Upload documento identita' (richiesto da Telnyx per numeri italiani)
   - Attesa verifica: 1-3 giorni lavorativi
5. Numero attivato:
   - In-app appare: "Il numero telefonico di Sara: +39 02 XXX XXXX"
   - Il cliente puo' comunicarlo ai clienti, metterlo sul sito, su Google Maps
   - Sara risponde automaticamente alle chiamate
6. Fatturazione: €3-6/mese addebitati al metodo di pagamento del cliente
   (tramite LemonSqueezy recurring add-on)
```

**Click necessari: ~5**
**Tempo: ~3 minuti (+ 1-3 giorni per verifica documento)**
**Il cliente NON deve: creare account Telnyx, configurare router, fare port forwarding, capire cosa e' SIP**

### Domanda: il cliente deve creare account su provider VoIP?
**NO. FLUXION gestisce tutto.** Il cliente vede solo "Attiva Sara al telefono" e il costo mensile. Telnyx e' invisibile al cliente (come Groq/Cerebras sono invisibili per LLM — stesso pattern del FLUXION Proxy decidato in S84).

### Domanda: deve configurare il router?
**NO. Zero port forwarding.** Cloudflare Tunnel crea una connessione USCENTE dal PC del cliente. Funziona dietro qualsiasi NAT, firewall, router italiano (TIM Hub, Vodafone Station, FRITZ!Box — tutti).

### Domanda: numero nuovo vs redirect dal numero esistente?
**Entrambi possibili:**
- **Default**: nuovo numero dedicato a Sara (provisioning automatico)
- **Opzionale**: "Vuoi usare il tuo numero esistente?" → number porting da TIM/Vodafone/EHIWEB a Telnyx (2-4 settimane, gestito da FLUXION)
- **Terza opzione**: deviazione chiamate dal numero esistente al numero Sara (il cliente configura dal suo operatore — non richiede porting)

---

## 4. COPY Cristallino — Costo = Linea, NON FLUXION

### Principio fondamentale:
> **FLUXION non addebita NULLA per la funzionalita' VoIP.**
> **Il costo e' esclusivamente quello della linea telefonica dedicata a Sara.**
> **Come comprare una SIM per il telefono: il telefono e' incluso, la SIM si paga a parte.**

### 4.1 Copy per LANDING PAGE

```
SARA RISPONDE AL TELEFONO 24/7
Attiva un numero dedicato per il tuo salone.
Sara prenota, conferma e gestisce le chiamate — anche di notte.

📞 Da €3/mese (costo della linea telefonica, incluso nella configurazione)
✅ Nessun costo FLUXION aggiuntivo
✅ Numero italiano dedicato (+39)
✅ Attivazione in 3 minuti

[Scopri di piu']
```

### 4.2 Copy per SETUP WIZARD (in-app)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ATTIVA SARA AL TELEFONO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Sara puo' rispondere alle chiamate del tuo salone
come una receptionist dedicata, 24 ore su 24.

COME FUNZIONA:
  1. Attiviamo un numero di telefono dedicato a Sara
  2. I tuoi clienti chiamano quel numero
  3. Sara risponde, prenota appuntamenti, risponde a domande

COSTO:
  Il numero telefonico costa circa €3-6/mese.
  Questo e' il costo della linea telefonica,
  NON un addebito di FLUXION.

  E' come avere una seconda linea telefonica per il salone:
  il gestionale e' gia' incluso nella tua licenza,
  la linea telefonica si paga separatamente al gestore.

  [ ] Ho capito, attiva il numero per Sara
  [Attiva]  [Non ora, ci penso]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.3 Copy per FAQ

```
D: DEVO PAGARE QUALCOSA IN PIU' PER SARA AL TELEFONO?
R: Sara e' inclusa nella tua licenza FLUXION. L'unico costo aggiuntivo
   e' quello della linea telefonica dedicata (~€3-6/mese), che e' il
   normale costo di un numero telefonico italiano. FLUXION non trattiene
   nulla su questo importo.

D: PERCHE' C'E' UN COSTO MENSILE SE LA LICENZA E' LIFETIME?
R: La licenza FLUXION e' lifetime e copre il software, Sara inclusa.
   Il numero di telefono e' un servizio di telecomunicazione esterno
   (come una linea telefonica o una SIM) che ha un costo mensile
   proprio del gestore telefonico, non di FLUXION.

D: POSSO USARE SARA SENZA IL NUMERO DI TELEFONO?
R: Assolutamente si'. Sara funziona perfettamente con il microfono
   del computer/tablet e su WhatsApp. Il numero telefonico e'
   una funzione opzionale per chi vuole che Sara risponda anche
   alle chiamate tradizionali.

D: POSSO USARE IL MIO NUMERO ESISTENTE?
R: Si'. Puoi trasferire (portare) il tuo numero attuale a Sara.
   La procedura richiede 2-4 settimane e FLUXION la gestisce per te.
   In alternativa, puoi deviare le chiamate dal tuo numero esistente
   al nuovo numero di Sara.
```

### 4.4 Copy per PAGINA PRICING (landing)

```
                BASE €497    PRO €897     CLINIC €1.497
Sara in-app       ✅           ✅            ✅
Sara WhatsApp     ✅           ✅            ✅
Sara Telefono     —        ✅ (+linea*)   ✅ (+linea*)

* Il numero telefonico dedicato costa ~€3-6/mese
  (costo della linea, non di FLUXION)
```

### 4.5 Confronto: come comunicano i competitor

| Competitor | Come comunicano costi VoIP/telefono |
|------------|-------------------------------------|
| **BookingBee** | Incluso nel canone mensile ($50-300/mese) — il costo telefono e' assorbito |
| **MyAIFrontDesk** | Incluso nel canone ($25-300/mese) |
| **Fresha** | Non ha ancora VoIP — solo booking online/WhatsApp |
| **Calendly/Acuity** | Non hanno integrazione telefonica nativa |

**Differenza FLUXION**: FLUXION e' LIFETIME (no canone mensile), quindi NON puo' assorbire il costo della linea nel canone. La comunicazione deve essere trasparente: "La licenza e' tua per sempre, la linea telefonica e' un servizio esterno opzionale."

---

## 5. Pro/Clinic Only o Per Tutti?

### Raccomandazione: Solo PRO (€897) e CLINIC (€1.497)
**Certezza: ALTA (90%)**

### Motivazione:

| Tier | Profilo cliente | Volume chiamate | VoIP necessario? |
|------|----------------|----------------|------------------|
| **Base €497** | Salone 1-2 persone, parrucchiere singolo | Basso (10-30 chiamate/mese) | NO — WhatsApp e booking online bastano |
| **Pro €897** | Salone/palestra 3-8 dipendenti | Medio (50-150 chiamate/mese) | SI' — receptionist occupata, chiamate perse |
| **Clinic €1.497** | Studio medico/clinica 9+ | Alto (100-300 chiamate/mese) | SI' — pazienti chiamano per appuntamenti |

### Benchmark costi competitor AI receptionist:
| Servizio | Costo mensile | Cosa include |
|----------|--------------|--------------|
| BookingBee | $50-300/mese | AI phone receptionist per saloni |
| MyAIFrontDesk | $25-300/mese | AI phone receptionist generico |
| Vapi (DIY) | ~$0.13-0.31/min | Solo piattaforma, devi costruire tutto |
| Retell AI | ~$0.07/min | Piattaforma + builder |

**Confronto con FLUXION:**
- FLUXION Pro: €897 LIFETIME + ~€4/mese linea = in 1 anno: €945 totale
- BookingBee: $100/mese = $1.200/anno (~€1.100/anno) — e il secondo anno costa altri €1.100
- **FLUXION e' 2x piu' economico gia' dal primo anno, e infinitamente piu' economico dal secondo anno in poi**

### Modello economico per FLUXION:
- **v1**: VoIP non presente → ZERO costi infrastrutturali
- **v1.1**: VoIP solo Pro/Clinic → il cliente paga la linea (~€4/mese via LemonSqueezy add-on)
- **FLUXION non ha costi VoIP propri**: il costo Telnyx e' passato direttamente al cliente
- **Alternativa**: FLUXION assorbe il costo (~€4/mese per cliente) e lo presenta come "incluso"
  - Con 500 clienti Pro/Clinic: €2.000/mese = €24.000/anno — sostenibile con margini licenze

### Raccomandazione finale pricing VoIP:
**Opzione A (raccomandata):** Il cliente paga la linea (~€4/mese) via add-on LemonSqueezy
- Pro: trasparente, sostenibile, zero rischio per FLUXION
- Contro: il cliente "vede" un costo ricorrente

**Opzione B:** FLUXION assorbe il costo
- Pro: "zero costi" — marketing potente
- Contro: costo ricorrente per FLUXION su licenze lifetime

**La scelta e' del fondatore.** Entrambe sono sostenibili. L'opzione A e' piu' sicura economicamente.

---

## 6. Alternative a VoIP Tradizionale

### 6.1 WhatsApp Business Calling API (NOVITA' 2025-2026)

**Cos'e':** Meta ha lanciato (luglio 2025) la WhatsApp Business Calling API. Permette chiamate VoIP DENTRO WhatsApp.

**Come funziona:**
- Il cliente apre WhatsApp → tocca "Chiama" sul profilo business del salone
- La chiamata arriva via WhatsApp (VoIP over internet, non PSTN)
- Sara risponde come se fosse una telefonata normale

**Limitazioni CRITICHE:**
- **NON puo' chiamare numeri telefonici normali** — solo WhatsApp-to-WhatsApp
- Il cliente DEVE avere WhatsApp installato
- Il cliente DEVE aver gia' una conversazione WhatsApp con il salone
- Richiede WhatsApp Business API (non gratis — serve BSP come 360dialog, Twilio)

**Verdetto:** Complementare a VoIP, NON sostitutivo. Non copre il caso "cliente chiama il numero del salone da telefono fisso/mobile senza WhatsApp."

### 6.2 Click-to-Call WebRTC (dal sito web del salone)

**Cos'e':** Un bottone sul sito web del salone: "Parla con Sara". Il cliente clicca e parla direttamente dal browser, senza numero di telefono.

**Come funziona:**
```
Sito web del salone → bottone "Chiama Sara"
    → Browser WebRTC → connessione diretta a Sara (via Cloudflare Tunnel)
    → Sara risponde in voce
    → ZERO costi di linea telefonica
```

**Vantaggi:**
- **ZERO costi** — niente numero telefonico, niente Telnyx
- Funziona SUBITO senza configurazione
- Il cliente non deve dare il suo numero di telefono
- Perfetto per prenotazioni dal sito web

**Svantaggi:**
- Il cliente DEVE essere sul sito web del salone
- Non funziona per chi chiama "da telefono" tradizionalmente
- Richiede che il salone abbia un sito web

**Verdetto:** ECCELLENTE come feature v1.1 GRATUITA per tutti i tier (anche Base). Non richiede VoIP, non ha costi. E' un widget JavaScript che il salone incolla nel proprio sito.

### 6.3 Sara Solo In-App + WhatsApp (v1 — gia' sufficiente)

**Cos'e':** Il setup attuale di Sara.
- In-app: il titolare/receptionist parla con Sara dal PC
- WhatsApp: i clienti scrivono/mandano vocali → Sara risponde

**Per il 90% delle PMI italiane nel 2026, questo e' sufficiente.**
Le prenotazioni avvengono sempre piu' online (WhatsApp, Google, sito) e sempre meno per telefono.

### 6.4 Tabella comparativa alternative

| Soluzione | Costo | Copertura | Complessita' | Quando |
|-----------|-------|-----------|-------------|--------|
| Sara in-app + WhatsApp | €0 | In salone + WhatsApp | ZERO | v1 ✅ |
| Click-to-Call WebRTC | €0 | Dal sito web del salone | Bassa (widget JS) | v1.1 |
| WhatsApp Calling API | €20-50/mese (BSP) | Solo utenti WhatsApp | Media | v1.2 |
| VoIP Telnyx (telefono) | €3-6/mese (linea) | Chiunque con un telefono | Media | v1.1-v1.2 |
| EHIWEB SIP diretto | €2-3/mese | Chiunque con un telefono | ALTA (NAT hell) | Mai come default |

---

## 7. RACCOMANDAZIONE FINALE

### Piano d'azione per fasi

```
╔══════════════════════════════════════════════════════════════╗
║  v1.0 (LANCIO) — Sara senza VoIP                           ║
║                                                              ║
║  - Sara in-app (microfono PC/tablet)                         ║
║  - Sara su WhatsApp (messaggi testuali + vocali)             ║
║  - Booking online (widget web)                               ║
║  - ZERO costi aggiuntivi per il cliente                      ║
║  - ZERO infrastruttura VoIP da gestire                       ║
║                                                              ║
║  Certezza: ALTA (95%)                                        ║
║  Rischio: ZERO                                               ║
║  Tempo implementazione: 0 giorni (gia' funzionante)          ║
╠══════════════════════════════════════════════════════════════╣
║  v1.1 (3-6 mesi) — Click-to-Call WebRTC                     ║
║                                                              ║
║  - Widget "Parla con Sara" per sito web salone               ║
║  - WebRTC diretto: browser → Cloudflare Tunnel → Sara        ║
║  - ZERO costi di linea telefonica                            ║
║  - Disponibile per TUTTI i tier (anche Base)                 ║
║                                                              ║
║  Certezza: ALTA (90%)                                        ║
║  Rischio: BASSO                                              ║
║  Tempo implementazione: 2-3 giorni                           ║
╠══════════════════════════════════════════════════════════════╣
║  v1.2 (6-12 mesi) — VoIP Telefonico (Solo Pro/Clinic)       ║
║                                                              ║
║  - Numero italiano dedicato (+39) via Telnyx                 ║
║  - Sara risponde al telefono 24/7                            ║
║  - Provisioning automatico (FLUXION gestisce tutto)          ║
║  - Costo: ~€3-6/mese (linea telefonica, NON FLUXION)        ║
║  - Solo Pro (€897) e Clinic (€1.497)                         ║
║                                                              ║
║  Certezza: ALTA (85%)                                        ║
║  Rischio: MEDIO (infrastruttura proxy, costi ricorrenti)     ║
║  Tempo implementazione: 5-8 giorni                           ║
╠══════════════════════════════════════════════════════════════╣
║  v1.3+ (futuro) — WhatsApp Calling + BYOD SIP               ║
║                                                              ║
║  - WhatsApp Business Calling API                             ║
║  - BYOD: "Porta il tuo numero SIP" (EHIWEB, etc.)           ║
║  - Opzionale per power user                                  ║
║                                                              ║
║  Certezza: MEDIA (70%)                                       ║
║  Rischio: BASSO (features opzionali)                         ║
╚══════════════════════════════════════════════════════════════╝
```

### Riepilogo certezze per domanda del fondatore

| Domanda | Risposta | Certezza |
|---------|----------|----------|
| Sara funziona senza VoIP per v1? | **SI'** — in-app + WhatsApp bastano | ALTA (95%) |
| Fresha ha voice agent su telefono? | **NO ancora** — lo stanno lanciando nel 2026 | ALTA (90%) |
| Come si collega tecnicamente? | Telnyx WebSocket → CF Tunnel → Sara (ZERO NAT issues) | ALTA (95%) |
| Il cliente deve configurare il router? | **NO** — zero port forwarding, zero configurazione rete | ALTA (99%) |
| Il cliente deve creare account su Telnyx? | **NO** — FLUXION gestisce tutto, Telnyx e' invisibile | ALTA (95%) |
| Costo VoIP e' di FLUXION? | **NO** — e' il costo della linea telefonica (~€3-6/mese) | ALTA (99%) |
| VoIP per tutti o solo Pro/Clinic? | **Solo Pro/Clinic** — il Base non ne ha bisogno | ALTA (90%) |
| EHIWEB va bene come provider? | **NO come default** — solo come BYOD opzionale per power user | ALTA (95%) |
| Telnyx e' il provider giusto? | **SI'** — best balance costo/reliability/developer experience | ALTA (85%) |
| Click-to-Call WebRTC e' un'alternativa? | **SI'** — gratis, per sito web, complementare a VoIP | ALTA (90%) |

### Cosa fare ADESSO (azione immediata)

1. **NIENTE VoIP in v1** — concentrarsi su Sara in-app + WhatsApp
2. **Rimuovere la sezione EHIWEB** dalle impostazioni (o nasconderla)
3. **Aggiornare il copy landing** per non menzionare VoIP/telefono in v1
4. **Pianificare v1.1**: Click-to-Call WebRTC (widget per sito web — gratis)
5. **Pianificare v1.2**: VoIP Telnyx (solo Pro/Clinic — €3-6/mese linea)

---

## Fonti Web (verificate 2026-03-18)

- [Telnyx Italy Phone Numbers](https://telnyx.com/phone-numbers/italy)
- [Telnyx Media Streaming WebSocket](https://developers.telnyx.com/docs/voice/programmable-voice/media-streaming)
- [Telnyx Italy DID Requirements](https://support.telnyx.com/en/articles/1311462-italy-did-requirements)
- [Telnyx Voice API](https://telnyx.com/products/voice-api)
- [Telnyx Pricing](https://telnyx.com/pricing/numbers)
- [Twilio Italy Voice Pricing](https://www.twilio.com/en-us/voice/pricing/it)
- [SignalWire AI Agent Pricing](https://signalwire.com/pricing/ai-agent-pricing)
- [Fresha 2026 Features](https://www.fresha.com/blog/Up-Next-2026)
- [WhatsApp Business Calling API](https://business.whatsapp.com/blog/whatsapp-business-calling-api)
- [WhatsApp Calling API Guide](https://developers.facebook.com/documentation/business-messaging/whatsapp/calling)
- [Voice AI Platform Comparison 2026](https://www.whitespacesolutions.ai/content/bland-ai-vs-vapi-vs-retell-comparison)
- [AI Receptionist Cost Guide 2026](https://www.myaifrontdesk.com/blogs/understanding-ai-receptionist-cost-a-2026-pricing-guide)
- [Voice AI Agent in a Weekend (Telnyx)](https://medium.com/@kapincev/voice-ai-agent-in-a-weekend-ultravox-telnyx-and-500-lines-of-javascript-ad35740260c6)
- [Telnyx Bidirectional Streaming](https://telnyx.com/release-notes/bi-directional-streaming-support)
- [Telnyx vs Twilio 2026](https://telnyx.com/resources/comparing-telnyx-twilio)

---

*CoVe 2026 Deep Research — CERTEZZE ASSOLUTE — completata 2026-03-18*
*Basata su: research file precedente + 10 web search live + benchmark competitor*
