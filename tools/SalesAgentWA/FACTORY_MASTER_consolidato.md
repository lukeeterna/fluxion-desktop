# FACTORY_MASTER — documento consolidato (fabbrica di progetti generalista + caso FLUXION)

**Creato**: 2026-06-06 · **Owner**: Luke · **Tipo**: master consolidato, agnostico al verticale
**Supersedea**: `factory-line v0.1`
**Scopo del file**: raccogliere in un unico deliverable tutta la catena di ragionamento dal primo prompt (review brutale del blueprint "Factory Line") fino al merge AMBRA + Sales Agent WA. Da committare con CC.

> **Regola di lettura**: la misura della fabbrica NON è il numero di stazioni documentate, ma **una `venture-dossier` portata dal seme al gate terminale** (pagamento reale o kill motivato). Tutto il resto è strumentale a questo.

---

## INDICE

0. Verdetto sintetico
1. Critica strutturale di Factory Line v0.1 (cosa rompeva)
2. FACTORY_MASTER v0.2 — la macchina corretta (3 strati, 3 stazioni, gate esterni, kill)
3. VOS_RUN_SPEC — esecuzione seme → vendita (niche-free) + firewall di validazione
4. Principio di leva-AI: il vincolo si sposta, non si elimina
5. Caso "primo €": validazione GTM FLUXION (le 5 domande, il difetto strutturale)
6. R1 tecnico: strato conversazione → handoff → checkout (codice)
7. KV vs D1 + benchmark AMBRA vs Sales Agent WA + piano di merge
8. Vincoli non-negoziabili (consolidati)
9. Tabella tool per validare la fabbrica (COMPITO 2 del primo prompt)
10. Prossima azione unica + voci aperte
— Fonti / riferimenti

---

## 0. VERDETTO SINTETICO

La fabbrica sembra costruita all'80%, ma quell'80% sono gli **organi facili** (orchestrazione, fetch-dati, agenti di build, rail di pagamento). Mancano due cose di natura diversa:

1. **Una decisione, non codice**: cos'è "Componente 0" in una fabbrica *generalista*. Un'audience è verticale e non riusabile; la primitiva riusabile è un **motore di outbound generico** (= AMBRA genericizzata).
2. **L'astrazione che rende la macchina vertical-agnostic**: lo schema `vertical_profile` + la genericizzazione di CoVe e AMBRA. Senza, hai un'istanza-auto, non una fabbrica.

Più una **forcing function** mancante: il **kill binario applicato dall'orchestratore**, che sostituisce il voto-IC degli studio e separa una fabbrica da un cimitero di idee mezze-fatte (cioè dal track-record di 2 anni a €0).

Il super-agente unito (AMBRA + WA) **è** il build di Componente 0. Va costruito **dopo** il primo €, o è di nuovo "linea su carta".

---

## 1. CRITICA STRUTTURALE DI FACTORY LINE v0.1 (cosa rompeva)

### 1.1 La logica della "linea" non regge come metafora (cargo-cult)
- La catena di montaggio crea valore da **parallelismo + specializzazione**: team diversi per stazione, più unità in linea insieme. Il solo-founder è **sequenziale**, una persona in context-switch. Tolti quei due ingredienti, la "linea" è una checklist con cerimonia (scocca, nastro, WIP-limit).
- Il **processo** stage-gate (idea → valida → build → lancia) trasferisce. La **metafora** fabbrica no: copia l'organigramma dello studio, non il suo processo.
- Pieter Levels non ha costruito una fabbrica: ha fatto prodotti, e il canale è **emerso** dal build-in-public in ~10 anni. La fabbrica è un'astrazione *post-hoc*; costruirla a priori è al contrario.

### 1.2 Il bottleneck dichiarato ("distribuzione") era un'assunzione comoda
- v0.1 citava CB Insights per giustificare "distribuzione = vincolo", ma il dato dice che la causa #1 di fallimento è **scarso product-market fit (~43%)**, mentre l'esaurimento del capitale (~70%) è il **sintomo finale**, non la causa. "No market need" è fallimento di **validazione** (stazioni a monte), non di distribuzione.
- L'aforisma di Thiel ("scarsa distribuzione, non il prodotto, è la causa #1") riguarda lo **scalare** un canale post-PMF con capitale: categoria sbagliata per un founder a €0 pre-ricavo che deve solo prendere il primo cliente.
- Teoria dei Vincoli vera: il vincolo è dove il WIP si accumula in un sistema **che gira**. Non si conosce a priori. Dichiararlo prima di far passare un'unità = l'assunzione comoda.

### 1.3 Solo 1 gate su 6 era esterno-binario; gli altri erano deliverable interni mascherati
- **Pulito**: il gate terminale (€ incassato).
- **Interno mascherato**: gate "Build" ("job-core funziona, test E2E") — "funziona" lo verifica il founder. Esterno = **un utente ≠ founder completa il job-core senza assistenza**.
- **Soft**: gate "Distribution" ("≥N buyer, risposte tracciate", N indefinito). Esterno-binario = **reply-rate qualificato ≥ soglia fissata prima**.
- **Non verificabili**: i gate A–E della demand-validation (spec non fornita).
- **Già corretto in v0.1**: gate "Offer" portato a "segnale di prezzo reale". Ma un segnale di prezzo richiede **traffico** → richiede il canale: quindi le stazioni a monte sono **a valle** del canale, non a monte.

### 1.4 Sovradimensionato: la pipeline 4+2 del §8b era la risposta, non il fallback
- Fondere: discovery + demand-validation (trovare una nicchia con segnale di spesa È validare la domanda); offer dentro demand; distribution + payment (sono un'unica cosa).
- Risultato: **Ricerca → Build → Distribuisci+Valida** = 3 stazioni, 2 gate. Le 6 stazioni vanno **guadagnate** da una corsa reale che rivela una stazione mancante, non disegnate a tavolino.

### 1.5 Finding topologico (il più importante)
Per un solo-founder a €0, il canale/audience **non è la stazione 5**: è la **precondizione di OGNI gate esterno** (serve audience per il segnale di domanda, per quello di prezzo, **e** per la vendita). Metterlo a 5/6 è topologicamente al contrario. L'audience viene **prima** e alimenta tutto.

---

## 2. FACTORY_MASTER v0.2 — LA MACCHINA CORRETTA

**Principio**: la macchina è vertical-agnostic; i verticali sono **config**, non codice. Unità di valore = una scocca portata al gate terminale.

### 2.1 Architettura a 3 strati

#### Strato A — Servizi condivisi (la "rete elettrica", GIÀ COSTRUITI)
| Servizio | Implementazione esistente | Ruolo |
|---|---|---|
| Orchestratore (nastro) | `vos-auto-router` | muove la scocca, applica i gate |
| Motore ricerca | `research.py` (Gemini grounding, €0) | discovery + triangolazione domanda |
| Motore scoring | CoVe v4 (Si = μ − λσ, λ=0.25) | kill/proceed quantitativo |
| **Motore outbound** | **AMBRA (genericizzata)** = Componente 0 | outreach a scala, GDPR-aware |
| Rail pagamento | Stripe Payment Links | gate terminale |

Questi NON si ricostruiscono. Quello che manca è lo Strato B.

#### Strato B — Config verticale (l'UNICA cosa che cambia per nicchia) — *il cuore, oggi inesistente*
```yaml
vertical_profile:
  id: <slug>                       # es. estetica-it
  type: B2B-global | local-services | consumer
  discovery:
    data_sources: [...]            # famiglie per tipo; le interroga research.py
    spend_signal: "<segnale di SPESA esistente da cercare>"
  scoring:                         # ingressi PLUGGABLE di CoVe; la formula resta Si=μ−λσ
    criteria: [{name, weight, source}]
    threshold_proceed: 0.75
  offer:
    what: "<cosa vendi>"
    price_floor: <€>               # sotto questo → kill
  prospect_source:
    how: "<dove prendere buyer contattabili, GDPR-safe>"
  outreach:
    channel: email                 # canale primario durevole
    template_id: <...>
  gates:
    A_demand: "<soglia segnale domanda esterno>"
    B_price:  "<soglia segnale prezzo: pre-ordine/LOI/carta>"
    terminal: "≥1 pagamento reale"
```

#### Strato C — Scocca (WIP unit) — `venture-dossier.md`, oggi inesistente
Interfaccia di handoff tra stazioni. Ogni stazione legge solo la sezione precedente, scrive la propria. Markdown + git.

| Stato | Dopo | Sezioni compilate |
|---|---|---|
| S0 seed | intake | seme + classificazione tipo-verticale |
| S1 nicchia+segnale | Discovery+Validazione | nicchia + segnale di spesa (URL) + tesi triangolata |
| S2 offerta | Build | offerta minima: cosa, prezzo ≥ floor |
| S3 MVP | Build | repo, URL deploy, esito test E2E job-core |
| S4 outreach | Distribuzione | canale, buyer, risposte tracciate |
| TERMINALE | Validazione | SHIPPED (€ incassato) o KILLED (motivo + URL) |

### 2.2 La linea (3 stazioni, gate esterni-binari)
| # | Stazione | Servizi usati | Transform | GATE (esterno-binario) |
|---|---|---|---|---|
| 1 | Discover + Valida domanda | ricerca + scoring + outbound | seme → nicchia con spesa + tesi → test outbound su prospect reali | **A**: volume su query transazionali ≥ soglia **+** ≥N reply qualificate. Fail → kill |
| 2 | Build MVP (timebox 1–3 sett) | agent build + Stripe + outbound | offerta → job-core funzionante → test prezzo | **B**: utente ≠ founder completa il job-core **AND** ≥1 segnale di prezzo reale. Fail → kill |
| 3 | Monetizza / scala-o-uccidi | outbound + Stripe | MVP → spinta → incasso | **TERMINALE**: ≥1 € reale → SHIPPED; verso ≥10 CLOSED_WON. Niente € → kill motivato |

**Fix topologico**: il motore outbound (AMBRA) è chiamato a **OGNI** gate, non solo a st.3. È servizio condiviso, non stazione tardiva. **WIP limit = 1.**

### 2.3 Il kill (forcing function — sostituisce il voto-IC)
Gate fallito → `vos-auto-router` archivia il dossier con motivo + URL evidenza. **Nessun override senza giustificazione loggata.** È questa regola che separa la fabbrica dal cimitero di idee.

### 2.4 Componente 0, ridefinito
NON è un'audience riusabile (un'audience è verticale: estetiste ≠ compratori d'auto; non esiste audience generalista a €0, salvo diventare tu il brand-nodo — decisione di identità non presa). La primitiva riusabile da una fabbrica generalista è un **motore di outbound generico**: prospect del verticale X → messaggio personalizzato a scala → risposte tracciate. Ce l'hai: è **AMBRA**, una volta scollata dall'auto.

### 2.5 Stato build + sequenza
| Componente | Stato | Azione |
|---|---|---|
| `vos-auto-router` | esiste | cablare sulle 3 stazioni + applicare kill |
| `research.py` | esiste | nessuna |
| CoVe v4 | esiste, criteri cablati su auto | **genericizzare** → criteri pluggable da profile |
| AMBRA | esiste, cablata su auto/dealer | **genericizzare** → `prospect_source` + `template` da profile |
| Stripe | esiste | nessuna |
| schema `vertical_profile` | **NON esiste** | **costruire — è il cuore** |
| `venture-dossier.md` | **NON esiste** | costruire |
| kill binario nel router | **NON esiste** | costruire |
| prima corsa E2E su nicchia nuova | mai fatta | **eseguire — è la misura** |

**Sequenza** (vincolo = "non ancora vertical-agnostic"): (1) profile schema → (2) genericizza CoVe → (3) genericizza AMBRA → (4) scocca → (5) kill binario → (6) cabla router sulle 3 stazioni → (7) **corsa E2E su UNA nicchia nuova**.

---

## 3. VOS_RUN_SPEC — ESECUZIONE SEME → VENDITA (niche-free)

**Consuma**: FACTORY_MASTER v0.2. **Esegue**: `vos-auto-router`. **AI**: Claude via prompt incollati (G-NOAPI-AI).

### 3.1 Firewall di validazione (perché la nicchia NON la sceglie l'advisor)
Regola del VOS: **evidenza, mai fiducia**. Se la nicchia la sceglie l'advisor, il run testa l'advisor, non la stazione 1, e la discovery resta non validata per sempre.
- L'advisor scrive le regole **una volta**; da lì non tocca scelte di contenuto.
- VOS partorisce la nicchia alla stazione 1 da un **seme = envelope di vincoli** (non un verticale).
- Validazione: a ogni gate VOS logga un **dato verificabile da terzi**; la selezione nicchia è valida **se ricostruibile dai criteri loggati** (ripercorri gli Si → tornano = VOS ha scelto; non tornano = prior nascosto, test sporco). Audit di **provenienza**, non di parola.

### 3.2 Input (l'UNICA cosa fornita)
```yaml
seed_envelope:                     # NON una nicchia. Solo i vincoli fissi.
  founder: solo, Italia/UE, €0 costo fisso
  build_capacity: MVP software/automazione in 1–3 settimane con CC
  reach: buyer B2B con contatti pubblici, raggiungibili GDPR-safe
  monetization: one-time basso OPPURE success-fee
  exclude: nicchie già killate (lista crescente)
```

### 3.3 Stazione 1 — Discovery + Validazione domanda (qui NASCE la nicchia)
| Step | Worker | Esegue | Artefatto loggato |
|---|---|---|---|
| 1.1 | `research.py` | dal seed genera K=10 nicchie con SEGNALE DI SPESA esistente, ognuna con URL | `candidates[]` = {nicchia, spend_signal, URL} |
| 1.2 | CoVe (criteri pluggable) | scora: forza spend-evidence, raggiungibilità buyer, build-feasibility solo+CC, price-floor, saturazione. Si=μ−λσ | `scores[]` |
| 1.3 | router | seleziona Si max > 0.75 = nicchia; istanzia `vertical_profile` | nicchia + Si ricostruibile |
| 1.4 | `research.py` | triangola domanda da ≥3 fonti indipendenti | tesi + URL |
| 1.5 | AMBRA + HITL | micro-probe outbound (20–30 prospect reali). **Tu approvi l'invio** | bozza + lista; poi reply grezze |

**GATE A**: volume query transazionali ≥ soglia **AND** ≥N reply qualificate. PASS → avanza. FAIL → archivia branch, il router **promuove la candidata successiva** e ri-esegue. Dopo M=3 fallimenti → escala (la *generazione* nicchie è starata).

### 3.4 Stazione 2 — Build MVP (timebox 1–3 settimane)
| Step | Worker | Esegue |
|---|---|---|
| 2.1 | Claude (Opus) + `research.py` | offerta minima: cosa, prezzo ≥ floor |
| 2.2 | CC (backend/frontend/rapid) | job-core; deploy CF Pages/Vercel (free) |
| 2.3 | Tally + Stripe Link | cattura segnale di prezzo |

**GATE B**: utente ≠ founder completa il job-core **senza assistenza** (log) **AND** ≥1 segnale di prezzo reale. FAIL → kill motivato.

### 3.5 Stazione 3 — Monetizza / scala-o-uccidi
| Step | Worker | Esegue |
|---|---|---|
| 3.1 | AMBRA + HITL | outbound a scala; **ogni send approvato da te** finché < 10 CLOSED_WON |
| 3.2 | Stripe | incasso |

**GATE TERMINALE**: ≥1 € reale → SHIPPED, verso ≥10 CLOSED_WON (a quota → autonomia esterna sbloccata). Nessun € → KILL motivato.

### 3.6 Glue deterministica (`vos-auto-router`)
Per stazione: leggi artefatto → valuta gate (check binario sul dato loggato) → `GO | KILL | REWORK(max 1)`. KILL@S1 = pop prossima candidata. KILL@S2/S3 = archivia. WIP=1. Loop-detection: `vos-childwatch`.

### 3.7 Provenienza obbligatoria (= la leva di validazione)
- **S1**: `candidates[]` + `scores[]` + ogni URL spend-signal (ricostruibilità della scelta).
- **Gate A**: numero di volume (query+data) + reply grezze.
- **Gate B**: log completamento utente terzo + ID Stripe/Tally del segnale prezzo.
- **Terminale**: charge ID Stripe.

### 3.8 Checklist a ogni gate (audit, non rifacimento)
1. Il dato del gate è verificabile da un terzo senza fiducia? (numero, reply, charge)
2. La nicchia è ricostruibile dai criteri loggati? Sì = VOS ha scelto. No = prior nascosto, ferma.
3. Il kill è stato applicato dal router o c'è un override non loggato?

---

## 4. PRINCIPIO DI LEVA-AI: IL VINCOLO SI SPOSTA, NON SI ELIMINA

Gli agenti **sono** il team multi-funzione per le stazioni interne (ricerca, build, contenuti, monitoring): lì il vincolo "una persona sola" è davvero sollevato. Ma l'AI non **elimina** il vincolo, lo **sposta** — e si sposta dove fa male:

1. **Il canale (Componente 0) è un asset di fiducia.** Gli agenti comprimono la *produzione* di contenuti, non il **tempo-calendario** in cui un'audience decide che sei credibile. Più output = più tentativi, non latenza azzerata. (Levels: 10 anni, non 10 agenti.)
2. **L'azione esterna è gated** — non dall'advisor, dalla **tua** regola VOS: autonomia esterna bloccata fino a ≥10 CLOSED_WON. Alla stazione-collo l'agente assiste, non sostituisce; ci sei tu (HITL). Un agente che "chiude da solo" su prospect UE tocca anche l'art. 22 GDPR.

Conclusione: leva piena su 5/6 della linea; sull'ultimo 1/6 (canale + primo close esterno) gli agenti assistono ma non sostituiscono, in parte per limite tecnologico, in parte per tua decisione di design. Lo spreco non è la visione AI-leva: è **architettare prima di far girare**.

---

## 5. CASO "PRIMO €": VALIDAZIONE GTM FLUXION

**Contesto verificato**: payment rail Stripe LIVE + licenza + email da dominio verificato (`fluxion-app.com`) — FUNZIONA. App distribuibile **solo macOS Intel** oggi; Windows in draft. Mercato PMI IT ~80% Windows. "Sara" voice agent bloccato (SIP) → non è il canale. Canale scelto = Sales Agent WhatsApp (scrape Google Maps → primo messaggio template per verticale → monitor risposte). Stato: scraper + sender + 6 template + monitor + LaunchAgent fatti; girato 15 apr (205 lead, 5 messaggi, 3 risposte). Mancava: strato conversazione→checkout (CTA su landing generica, non checkout reale).

### 5.1 Difetto strutturale (verdetto)
Il piano ottimizza il **vincolo sbagliato**: perfeziona una macchina di chiusura a freddo (R1) puntata su PMI generiche ~80% Windows → l'80%+ di chi lo scraper trova **non può comprare** il prodotto che esiste oggi. E il canale è puntato in gran parte su non-acquirenti.

### 5.2 Le 5 domande
1. **Scopo / funnel**: chiudere €497 one-time *desktop* in chat a freddo è irrealistico (zero fiducia + acquisto ponderato + install con Gatekeeper/SmartScreen). Funnel minimo credibile: contatto → risposta positiva → **demo screen-share di 15 min con te** → trial o acquisto assistito. Lo step "agente manda link Stripe su risposta positiva" converte ~0: il vero handoff è a un **umano (tu)**.
2. **Sequenza R1→R2→R3**: sbagliata come posta. Con outreach di massa, **Windows è prerequisito**, non step 2 (non rilevi l'OS dallo scrape → messaggi ~85% che non comprano). "Mac-first" non è eseguibile via quello scrape (non targettizzi i Mac). Risoluzione: non sequenziare R1/R2; fai prima il test di domanda a mano (vedi 5.3).
3. **Legale + ban + statistica** (dati, vedi Fonti):
   - *Legale (IT)*: le Linee guida del Garante in materia di spam affermano esplicitamente che la rintracciabilità di un numero online **non autorizza** a usarlo per comunicazioni; il marketing via WhatsApp richiede consenso preventivo, documentato, come SMS/email. Sanzioni reali: noicompriamoauto.it €45.000; Università E-Campus €75.000 (SMS senza consenso). *(Non è consulenza legale: conferma con un avvocato privacy.)*
   - *Piattaforma (ban)*: l'automazione non ufficiale di WhatsApp Web + primo messaggio promozionale non richiesto è un innesco-ban da manuale; Meta ha intensificato il rilevamento nel 2025-26; un saluto non costituisce consenso; se l'automazione resta attiva durante il ricorso, il ban è confermato. La sezione "compra una SIM nuova" del blueprint è l'ammissione che il canale gira su violazione ripetuta — tapis roulant.
   - *Statistica*: 3/5 è **rumore** (IC 95% ≈ 23–88%). "Risposta" è il KPI sbagliato (a freddo include "chi sei?/come hai il mio numero?", che È l'esposizione GDPR che affiora). KPI corretto: **risposta-positiva-qualificata → demo prenotata**.
4. **Buchi evidenti**: nessuna qualificazione OS pre-contatto (il buco che uccide); nessun umano nel loop per €497; asset demo rotto (CTA su `pages.dev`, non checkout `fluxion-app.com`; `VIDEO_LINKS` tutti uguali); scraper primario morto (crediti GCP esauriti → Google Places skippato); nessun piano install-support post-vendita; fatturazione/P.IVA non gestita (Stripe ≠ compliance fiscale IT).
5. **Esperimento più economico (zero dev)**: NON costruire R1/R2. Scegli a mano 15–20 PMI servibili **oggi** (Mac o disposte ad aspettare) raggiungibili su canale caldo/atteso. Offri demo screen-share 15 min. Successo: ≥1 prenota **e** ≥1 dice "pago €497" con **carta/acconto**. Se da 20 contatti caldi non esce 1 impegno pagato, la macchina automatica avrebbe fatto peggio. Se esce, sai **quale OS usa chi paga** e costruisci esattamente quello.

> Nota di coerenza: per ARGOS era già stato deciso "email-first, GDPR-safe, no cold WhatsApp". Stesso founder, stessa Italia, stesso regime: l'incoerenza di posture è un campanello.

---

## 6. R1 TECNICO — STRATO CONVERSAZIONE → HANDOFF → CHECKOUT (codice)

Vincoli rispettati: classificatore **deterministico a keyword** (no API key → G-NOAPI-AI, costo zero); notifica handoff **separata dal bot Telegram ARGOS**; zero dipendenze nuove (stdlib 3.9). Il codice è **channel-neutral**: gira identico sia che il primo messaggio sia inviato a mano sia via automazione.

### 6.1 Migration DB
```sql
-- migrate_r1.sql — eseguire una volta: sqlite3 leads.db < migrate_r1.sql
ALTER TABLE messages ADD COLUMN reply_intent TEXT;          -- hot|negative|risk|other
ALTER TABLE messages ADD COLUMN handoff_status TEXT DEFAULT 'none';  -- none|queued|claimed|closed
ALTER TABLE messages ADD COLUMN checkout_url TEXT;
ALTER TABLE messages ADD COLUMN converted_at TEXT;

ALTER TABLE leads ADD COLUMN do_not_contact INTEGER DEFAULT 0;  -- suppression list
ALTER TABLE leads ADD COLUMN outcome TEXT;                       -- won|lost|null

CREATE INDEX IF NOT EXISTS idx_messages_handoff ON messages(handoff_status);
CREATE INDEX IF NOT EXISTS idx_messages_intent  ON messages(reply_intent);
CREATE INDEX IF NOT EXISTS idx_leads_dnc        ON leads(do_not_contact);
```

### 6.2 `replies.py` — classificazione intent + trigger handoff
```python
# replies.py
"""
Classifica le risposte loggate dal monitor e instrada:
- hot      -> coda handoff (rispondi TU, demo)
- risk     -> do_not_contact=1 + alert (chi chiede "come hai il mio numero" va soppresso subito)
- negative -> do_not_contact=1, nessuna azione
- other    -> coda handoff (review manuale)
Deterministico, zero API (G-NOAPI-AI).
"""
import re
import sqlite3
import logging
from config import DB_PATH

logger = logging.getLogger(__name__)

# Ordine di controllo: RISK -> NEGATIVE -> HOT -> OTHER
RISK = [
    "come hai avuto", "come hai preso", "dove hai preso", "chi ti ha dato",
    "come fai ad avere", "da dove hai", "numero da dove", "spam",
    "ti segnalo", "segnalo", "denuncio", "querela", "garante", "avvocato",
]
NEGATIVE = [
    "non mi interessa", "non interessa", "no grazie", "non sono interessat",
    "stop", "basta", "smettila", "lasciami", "non scrivetemi", "non scrivermi",
    "toglietemi", "toglimi", "rimuovi", "cancellami", "non voglio",
]
HOT = [
    "quanto costa", "quanto viene", "prezzo", "costo", "come funziona",
    "demo", "fammi vedere", "vorrei vedere", "mi interessa", "interessato",
    "interessata", "info", "informazioni", "dettagli", "quando", "prova",
    "va bene", "ok ", "ok,", "si mi", "sì mi", "mi piacerebbe",
]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def classify(reply_text: str) -> str:
    t = _normalize(reply_text)
    if not t:
        return "other"
    if any(p in t for p in RISK):
        return "risk"
    if any(p in t for p in NEGATIVE):
        return "negative"
    if any(p in t for p in HOT):
        return "hot"
    return "other"


def process_new_replies() -> dict:
    """
    Scansiona i messaggi con status='replied' non ancora classificati,
    assegna intent e instrada. Ritorna conteggi.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT m.id, m.lead_id, m.reply_text, l.business_name, l.phone, l.city
        FROM messages m JOIN leads l ON l.id = m.lead_id
        WHERE m.status = 'replied' AND m.reply_intent IS NULL
    """).fetchall()

    counts = {"hot": 0, "negative": 0, "risk": 0, "other": 0}
    alerts = []

    for r in rows:
        intent = classify(r["reply_text"])
        counts[intent] += 1

        if intent in ("hot", "other"):
            conn.execute(
                "UPDATE messages SET reply_intent=?, handoff_status='queued' WHERE id=?",
                (intent, r["id"]),
            )
            alerts.append((intent, dict(r)))
        elif intent == "negative":
            conn.execute("UPDATE messages SET reply_intent=? WHERE id=?", (intent, r["id"]))
            conn.execute("UPDATE leads SET do_not_contact=1 WHERE id=?", (r["lead_id"],))
        elif intent == "risk":
            conn.execute("UPDATE messages SET reply_intent=?, handoff_status='queued' WHERE id=?",
                         (intent, r["id"]))
            conn.execute("UPDATE leads SET do_not_contact=1 WHERE id=?", (r["lead_id"],))
            alerts.append(("risk", dict(r)))

    conn.commit()
    conn.close()

    if alerts:
        from handoff import notify_batch
        notify_batch(alerts)

    logger.info(f"Replies processate: {counts}")
    return counts
```

### 6.3 `handoff.py` — notifica locale + claim
```python
# handoff.py
"""
Handoff a umano. Canale: notifica macOS nativa (zero infra) + coda in dashboard.
NON usa il bot Telegram ARGOS. Per push, crea un bot Telegram SEPARATO per FLUXION.
"""
import subprocess
import logging

logger = logging.getLogger(__name__)


def _macos_notify(title: str, message: str):
    """Notifica nativa macOS via osascript (nessuna dipendenza)."""
    try:
        safe = message.replace('"', "'")
        subprocess.run(
            ["osascript", "-e",
             f'display notification "{safe}" with title "{title}" sound name "Glass"'],
            check=False, timeout=5,
        )
    except Exception as e:
        logger.warning(f"Notifica macOS fallita: {e}")


def notify_batch(alerts: list[tuple]):
    hot = [a for a in alerts if a[0] == "hot"]
    risk = [a for a in alerts if a[0] == "risk"]
    other = [a for a in alerts if a[0] == "other"]

    if hot:
        names = ", ".join(a[1]["business_name"] for a in hot[:3])
        _macos_notify(f"FLUXION — {len(hot)} risposte CALDE",
                      f"Rispondi tu: {names}. Apri dashboard.")
    if risk:
        _macos_notify(f"FLUXION — {len(risk)} alert",
                      "Contatti che chiedono dei dati: soppressi + da gestire a mano.")
    if other:
        _macos_notify(f"FLUXION — {len(other)} risposte da rivedere", "Apri dashboard.")

    # OPZIONALE: push su Telegram FLUXION (bot separato, non ARGOS)
    # send_telegram(f"{len(hot)} caldi, {len(risk)} alert, {len(other)} review")


def claim(message_id: int):
    """Segna la conversazione come presa in carico da te: l'automazione non risponde più."""
    import sqlite3
    from config import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE messages SET handoff_status='claimed' WHERE id=?", (message_id,))
    conn.commit()
    conn.close()
```

### 6.4 `checkout.py` — link Stripe reale + attribuzione per-lead
```python
# checkout.py
"""
Genera il link di checkout REALE (fluxion-app.com), non la pages.dev,
con client_reference_id=lead_<id> per attribuire la conversione al lead.
NB: i due payment link LIVE (Base €497, Pro €897) li metti tu.
Conferma client_reference_id sui Payment Link nei docs Stripe prima del go-live.
"""
from urllib.parse import urlencode

# <-- INSERISCI I TUOI PAYMENT LINK LIVE REALI -->
PAYMENT_LINKS = {
    "base": "https://buy.stripe.com/XXXXXXXX_BASE_497",   # €497
    "pro":  "https://buy.stripe.com/XXXXXXXX_PRO_897",     # €897
}


def build_checkout_link(lead_id: int, plan: str = "base",
                        category: str = "", city: str = "") -> str:
    base = PAYMENT_LINKS.get(plan, PAYMENT_LINKS["base"])
    params = {
        "client_reference_id": f"lead_{lead_id}",   # ritorna nel webhook -> attribuzione
        "utm_source": "wa", "utm_campaign": category,
        "utm_content": (city or "").lower().replace(" ", "_"),
    }
    sep = "&" if "?" in base else "?"
    return base + sep + urlencode(params)
```

### 6.5 Aggiunte CLI in `agent.py`
```python
def cmd_inbox(args):
    """Mostra le conversazioni da gestire (coda handoff)."""
    init_db()
    import sqlite3
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT m.id, m.reply_intent, m.reply_text, l.business_name, l.phone, l.city
        FROM messages m JOIN leads l ON l.id = m.lead_id
        WHERE m.handoff_status = 'queued'
        ORDER BY CASE m.reply_intent WHEN 'hot' THEN 0 WHEN 'risk' THEN 1 ELSE 2 END
    """).fetchall()
    conn.close()
    if not rows:
        print("Inbox vuota."); return
    for r in rows:
        from checkout import build_checkout_link
        link = build_checkout_link(r["id"], "base", "", r["city"]) if r["reply_intent"] == "hot" else "-"
        print(f"\n[{r['reply_intent'].upper()}] {r['business_name']} ({r['phone']}, {r['city']})")
        print(f"  Risposta: {r['reply_text']}")
        if link != "-":
            print(f"  Checkout da mandare in chat: {link}")

def cmd_process(args):
    """Classifica le nuove risposte e popola la coda handoff."""
    from replies import process_new_replies
    print(process_new_replies())

def cmd_won(args):
    """Registra una conversione (il DB locale non riceve il webhook: confermi tu)."""
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE leads SET outcome='won' WHERE id=?", (args.lead,))
    conn.execute("UPDATE messages SET converted_at=datetime('now'), handoff_status='closed' WHERE lead_id=?",
                 (args.lead,))
    conn.commit(); conn.close()
    print(f"Lead {args.lead} -> WON")

# registra in main():
#   subparsers.add_parser("process", help="Classifica risposte e popola handoff")
#   subparsers.add_parser("inbox",   help="Conversazioni da gestire")
#   p_won = subparsers.add_parser("won", help="Segna conversione"); p_won.add_argument("--lead", type=int, required=True)
```

### 6.6 Filtro suppression nel sender (1 riga, importante)
Nel `_get_pending_leads()` di `sender.py`, aggiungi alla WHERE:
```python
          AND l.do_not_contact = 0
```

### 6.7 Worker — attribuzione conversione (lato `fluxion-proxy`, usare D1)
```javascript
// fluxion-proxy — dentro l'handler checkout.session.completed
const ref = session.client_reference_id;          // "lead_123"
if (ref?.startsWith("lead_")) {
  const leadId = ref.slice(5);
  // Scrittura su D1 (NON KV — vedi §7): tabella conversions(lead_id, amount, email, at)
  await env.DB.prepare(
    "INSERT INTO conversions (lead_id, amount, email, at) VALUES (?, ?, ?, ?)"
  ).bind(leadId, session.amount_total, session.customer_details?.email ?? null,
         new Date().toISOString()).run();
}
```
Poi sul Mac: `python3 agent.py won --lead 123` (il DB locale non è raggiungibile dal Worker; la chiusura del loop la confermi tu o con un fetch periodico da D1).

**Flusso R1 completo**: monitor logga reply → `agent.py process` (classifica) → notifica macOS → `agent.py inbox` (lead caldo + link checkout reale pronto) → rispondi tu / demo / incolli link → cliente paga → `client_reference_id` attribuisce → `agent.py won --lead`.
**Da te**: i due payment link LIVE reali in `checkout.py` + conferma `client_reference_id` nei docs Stripe.

---

## 7. KV vs D1 + BENCHMARK AMBRA vs SALES AGENT WA + MERGE

### 7.1 KV, semplice — e perché usare D1
**KV** = "Key-Value", un mini-DB chiave→valore sulla rete Cloudflare, accanto al Worker (un dizionario gigante: `won:123 → {importo, email, data}`). Serviva da ponte perché il Worker riceve il webhook Stripe ma **non può scrivere nel `leads.db` sul Mac** (mondi separati): il Worker deposita l'esito in rete, il Mac lo legge.
**Correzione di coerenza**: per FLUXION hai già scelto **D1** (DB SQL di Cloudflare) per evitare l'*eventual consistency* di KV. Per non mischiare due storage, usa **D1** con una tabella `conversions`. KV era pigrizia; D1 è la scelta coerente con la tua architettura.

### 7.2 Benchmark
| Dimensione | Sales Agent WA | AMBRA (ARGOS) | Migliore + nota |
|---|---|---|---|
| Qualificazione pre-contatto | nessuna — contatta tutti | CoVe v4 bayesiano, 2.955 run, scora *prima* | **AMBRA**, nettamente |
| Canale outreach | WhatsApp Web (apertura alta, fragile/non-durevole) | email (durevole, scalabile) | dipende: AMBRA più durevole, WA più "aperto" ma a termine |
| Lead sourcing | 3 fonti con fallback, generalista | autoscout24 `__NEXT_DATA__` + regex — profondo ma mono-verticale | **WA** per generalità/robustezza |
| Motore messaggi | 6 verticali, multi-parte, variazione Jaccard >40% | persona "Luca Ferretti", variazione meno strutturata | **WA** |
| Classificazione risposte | classifier deterministico (R1) | reattiva, non formalizzata | **pari** (WA col patch) |
| HITL / gating | assente in origine; R1 aggiunge coda+claim | gate HITL + gating pagamento progettati | **AMBRA** — filosofia più matura |
| Loop outbound autonomo | sender autonomo (LaunchAgent, batch, warm-up) | oggi reattiva (Priority #2) | **WA** |
| Tracking / osservabilità | dashboard Flask funnel AARRR + UTM | log decisione CoVe (DuckDB) | **WA** funnel; AMBRA log-decisione |
| Battle-testing reale | 5 messaggi una volta | 2.955 run CoVe sul core | **AMBRA** sul core; WA quasi non testato |

**Verdetto**: complementari, non "uno migliore". WA = **braccio** (sourcing+invio+funnel); AMBRA = **cervello** (qualificazione+gating). Braccio senza cervello spara nel mucchio; cervello senza braccio resta reattivo.

### 7.3 Merge = Componente 0 (cosa hai già progettato)
Il merge è **esattamente** "AMBRA genericizzata = Componente 0" del FACTORY_MASTER. Pipeline dell'agente unito:
`scrape multi-fonte → CoVe score + soglia → outreach personalizzato (canale email primario) → reply classifier → HITL handoff → attribuzione checkout (D1) → dashboard funnel + log CoVe`

Chi dona cosa:
- **Da AMBRA**: CoVe scoring (qualifica), canale email durevole, filosofia HITL-gate.
- **Da WA**: scraper multi-fonte, motore template + variazione, reply classifier (R1), dashboard funnel.
- **Collante nuovo**: schema `vertical_profile` (parametrizza criteri-CoVe + template + sorgente *per verticale*). È questo che rende il merge **generalista**.

### 7.4 Disciplina + borrow immediato
Il super-agente unito è il build di **Componente 0**, non ciò che chiude il primo cliente FLUXION questa settimana. Costruiscilo **dopo** il primo €.
**Unico pezzo del merge che vale subito**: **CoVe come pre-filtro davanti al sender** — scora i 205 lead, contatta solo i top. Alza l'hit-rate e abbassa il volume di invii. Borrow piccolo, leva alta. Interfaccia: `score_lead(lead, vertical_profile) -> float`, infilata come `ORDER BY cove_score DESC` in `_get_pending_leads()`.

---

## 8. VINCOLI NON-NEGOZIABILI (consolidati)

- **G-NOAPI-AI**: livello AI = Claude via prompt incollati, **zero API key**. Niente repo-agente con `.env` (es. SalesGPT). Soglia **€30/mese** LLM.
- **HITL**: azione esterna (contatto reale, pagamenti) **bloccata fino a ≥10 CLOSED_WON**; fino ad allora il gate terminale è HITL via G-APPROVAL CLI (non Telegram/env-var bypass), non autonomo.
- **Hardware**: Python 3.13 (VOS) / 3.9 (Sales Agent), Big Sur + iMac 2012 no-AVX2, **no Docker**. Tool OSS/free via npm/pip, niente librerie pesanti.
- **Budget**: €240/mese; ogni tool free-tier/OSS, con **script di monitoraggio quote** (i free-tier cambiano ogni settimana).
- **GDPR**: outbound **email-first**, no cold WhatsApp; art. 22 — nessuna chiusura automatica su prospect UE finché HITL attivo. La rintracciabilità pubblica di un contatto non è base giuridica per contattarlo.
- **Telegram**: il bot ARGOS (Chat ID 931063621) è **riservato all'HITL operativo ARGOS**; per FLUXION, bot separato.
- **Anti-bottleneck-a-priori**: NON pre-dichiarare "distribuzione". Il vincolo è dove il primo run si pianta. WIP=1 per vederlo.

---

## 9. TABELLA TOOL PER VALIDARE LA FABBRICA (COMPITO 2 del primo prompt)

Ordinata per priorità-vincolo. Tutti €0/free-tier/OSS. **I free-tier cambiano di settimana in settimana**: riconferma le quote prima di impegnarti.

| Cosa va validato | Famiglia | Candidati (free/OSS, URL) | Costo reale | Prova (dato esterno) |
|---|---|---|---|---|
| **[#1] Componente 0 — canale che PRECEDE il prodotto** | audience/newsletter + build-in-public | Substack (sub illimitati) substack.com · beehiiv (free <2.500 sub, 0% fee, referral) beehiiv.com · X/LinkedIn/Reddit organico | €0 | crescita lista + ≥N reply qualificate da un post senza ads. Se a 60gg 0 conversazioni → vincolo qui |
| **[#1] Distribution — outreach consegnato** | mail-merge personale + automazione OSS | Mailmeteor (free, Gmail-native) mailmeteor.com · n8n self-host via npm (gira su Big Sur senza Docker) github.com/n8n-io/n8n · Snov.io (50 crediti/mese) | €0. Cold-email tool dedicati NON free reale (Instantly nessun free, GMass trial 50/gg) | reply-rate ≥ soglia su ≥N invii reali; reply → call |
| **CLAIM "bottleneck = distribuzione"** | una corsa E2E reale | 1 venture-dossier S0→S6 su nicchia nuova, log markdown+git | €0 | lo stadio dove il WIP si accumula nella 1ª corsa = vero vincolo. CB Insights: causa #1 = "no market need" (43%) = stazioni a monte → ipotesi da testare |
| **Validation — gate terminale (pagamento)** | payment link / Merchant-of-Record | Stripe Payment Links stripe.com/payments/payment-links · Polar (4%, no fee fissa, MoR) polar.sh · Lemon Squeezy (5%+$0,50, MoR, parte di Stripe) lemonsqueezy.com | €0 fisso, solo % | carta addebitata. Venditore IT: MoR rimuove l'IVA cross-UE; per il solo primo € Stripe Link è il più rapido |
| **Offer — gate prezzo esterno** | fake-door/smoke-test landing + cattura prezzo | Tally (form free) tally.so · Carrd (landing free) carrd.co · + Stripe Link per deposito/pre-ordine | €0 fisso | segnale comportamentale: click "Compra"+carta con prezzo reale — NON email signup. Caveat: serve traffico → dipende da Componente 0 |
| **Discovery — segnale di SPESA esistente** | volume ricerca + pain-mining + deep research | Google Trends trends.google.com · Keyword Planner (volume bucketato senza spend) ads.google.com · Reddit search + Subreddit Stats + GummySearch gummysearch.com · research.py (Gemini grounding) | €0 | volume su query transazionali + post "frustrato con/vorrei". Caveat: upvote ≠ volume di ricerca, vanno incrociati |
| **CLAIM "gate esterni" + "scocca interfaccia"** | audit + WIP versionato | venture-dossier.md in git · checklist "un estraneo verifica questo gate?" | €0 | ogni gate = fatto osservabile da terzi (numero, reply, charge). Scocca: dossier S0→S6 leggendo solo la sezione precedente. Rischio "linea su carta": se nessuno lo porta a S6, vale 0 |
| **Build** (de-prioritizzata) | build + deploy free | Claude Code (dentro soglia €30/mese) · CF Pages / Vercel hobby | ~€0 + quota LLM | un utente esterno completa il job-core senza assistenza |

---

## 10. PROSSIMA AZIONE UNICA + VOCI APERTE

### 10.1 Azione unica (questa settimana)
Per **FLUXION**: NON costruire R1/R2. Esegui il test a mano (§5.2 punto 5) — 20 PMI servibili oggi, canale caldo, demo 15 min, target ≥1 impegno pagato con carta/acconto. Decide tutto il resto (incluso quale OS buildare).

Per la **fabbrica**: il primo mattone concreto è `score_lead(lead, vertical_profile) -> float` (CoVe genericizzato sui criteri PMI), che serve **sia** a FLUXION (pre-filtro sui 205 lead) **sia** alla fabbrica (Strato B).

### 10.2 Voci aperte (da decidere/costruire)
- [ ] Schema `vertical_profile` come YAML reale per CC (il cuore dello Strato B).
- [ ] Template `venture-dossier.md` (la scocca).
- [ ] Kill binario dentro `vos-auto-router` (la forcing function).
- [ ] CoVe genericizzato: interfaccia `score_lead(lead, vertical_profile)`.
- [ ] AMBRA genericizzata: `prospect_source` + `template` da profile.
- [ ] FLUXION R1: payment link LIVE in `checkout.py` + conferma `client_reference_id` (Stripe docs).
- [ ] FLUXION: tabella `conversions` su D1 + (opz.) fetch periodico per chiudere il loop `won`.
- [ ] Decisione identità: Luke diventa o no un brand-nodo build-in-public? (impatta se Componente 0 può mai essere un'audience anziché solo outbound.)

---

## FONTI / RIFERIMENTI

**Framework (foundational, non cutoff-sensitive)**
- Teoria dei Vincoli — E. Goldratt, *The Goal* (1984)
- Stage-Gate — R. Cooper, *Winning at New Products*
- Build-Measure-Learn — E. Ries, *The Lean Startup*

**Dati startup / distribuzione**
- CB Insights, top reasons startups fail: https://www.cbinsights.com/research/report/startup-failure-reasons-top/
- Pieter Levels (pipeline ripetibile + asset canale): https://www.fast-saas.com/blog/pieter-levels-success-story/
- Distribuzione come asset 10-anni: https://www.softwareseni.com/building-in-public-the-10-year-distribution-strategy-behind-solo-founder-revenue/
- Venture studio (PSL, High Alpha, eFounders) — riferimenti nel blueprint v0.1

**GDPR / outreach Italia**
- Garante Privacy, Provvedimenti e Linee guida spam: https://www.garanteprivacy.it
- Caso noicompriamoauto.it (€45.000): https://www.giambronelaw.it/site/sezione-notizie/multa-mail-marketing-garante
- WhatsApp/SMS marketing e GDPR (consenso, casi sanzione): https://ecommercelegale.it/gdpr/sms-whatsapp-marketing/
- Marketing indesiderato — Garante (Verisure): https://www.diritto.it/marketing-indesiderato-consenso-forzato-garante/

**WhatsApp — policy / ban (consultati 2026)**
- WhatsApp Business Messaging Policy: https://whatsappbusiness.com/policy/
- Ban per automazione/bulk non ufficiale (guide 2026): https://chakrahq.com/article/whatsapp-business-account-restricted-fix/ · https://blog.omnichat.ai/whatsapp-business-account-block/ · https://www.activecampaign.com/blog/how-to-avoid-whatsapp-account-ban

**Repo "sales agent" valutati (claim NON comprovati)**
- SalesGPT (reale, ~2.4k★, MIT, ultimo rilascio v0.1.2 mar 2024, richiede API key): https://github.com/filip-michalsky/SalesGPT
- Gong (NON open source, NON un repo, ~$1.400-1.600/utente/anno; "+35% win rate" = dato del blog Gong Labs): https://www.gong.io

**Tool (free-tier / OSS — riconfermare quote)**
- Substack https://substack.com · beehiiv https://www.beehiiv.com · Stripe Payment Links https://stripe.com/payments/payment-links · Polar https://polar.sh · Lemon Squeezy https://www.lemonsqueezy.com · Tally https://tally.so · Carrd https://carrd.co · n8n https://github.com/n8n-io/n8n · Mailmeteor https://mailmeteor.com · GummySearch https://gummysearch.com · Google Trends https://trends.google.com · Google Keyword Planner https://ads.google.com

---

*Fine documento. Misura della fabbrica: una `venture-dossier` portata dal seme al gate terminale — pagamento reale o kill motivato. Non il numero di stazioni documentate.*
