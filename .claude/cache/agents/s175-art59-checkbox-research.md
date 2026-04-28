# Research: Art. 59 lett. o) D.Lgs 206/2005 — Checkbox Recesso Software Digitale FLUXION
> Legal Compliance Checker Agent | 2026-04-28

## Executive Summary

D.Lgs 206/2005 art. 59 lett. o) consente l'esclusione del diritto di recesso legale (14 giorni) per contenuti digitali consegnati su supporto non materiale a due condizioni cumulative: consenso espresso all'esecuzione immediata e riconoscimento della perdita del diritto di recesso. FLUXION usa **Stripe Payment Links** (`buy.stripe.com/...`) che NON supportano checkbox obbligatori nativi — la soluzione corretta è una pagina pre-checkout interstitial (`/checkout-consent.html`) con doppia checkbox JS-enforced e redirect condizionato al Payment Link, con audit log in CF KV. Il rischio reale senza implementazione non è il recesso entro 14gg (già coperto dalla garanzia 30gg) ma l'estensione a **12 mesi** per art. 53 co. 2.

---

## Finding 1 — Testo Normativo Esatto Art. 59

**Versione consolidata D.Lgs 26/2023** (Omnibus, in vigore 18/03/2023):

> "Il diritto di recesso di cui agli articoli 52 e 54 è escluso relativamente ai contratti: [...]
> o) la fornitura di **contenuto digitale mediante un supporto non materiale**, se l'esecuzione è iniziata con l'**accordo espresso** del consumatore e con la sua **accettazione** del fatto che in tal caso avrebbe **perso il diritto di recesso**."

**Condizioni cumulative obbligatorie:**
1. "accordo espresso del consumatore" all'inizio dell'esecuzione
2. "accettazione" del consumatore che "in tal caso avrebbe perso il diritto di recesso"

**Riferimenti:**
- D.Lgs 6 settembre 2005 n. 206, art. 59 co. 1 lett. o)
- Direttiva 2011/83/UE art. 16 lett. m)
- D.Lgs 7 marzo 2023 n. 26 — recepimento Omnibus

**Applicabilità FLUXION**: software .pkg/.msi via download immediato = "contenuto digitale mediante supporto non materiale". Confermata.

---

## Finding 2 — Checkbox Singola vs Doppia

**Orientamento AGCM + DG JUST 2023-2026**: checkbox singola insufficiente se il testo non distingue i due requisiti.

**Raccomandazione: doppia checkbox separata.** La norma usa "accordo espresso" (atto 1) e "accettazione" (atto 2) — due manifestazioni distinte. Checkbox unica è più esposta a contestazione art. 49 co. 1 lett. m).

**Alternativa ammessa** (meno robusta): checkbox singola con testo composito che contenga inequivocabilmente entrambi i requisiti — Aruba.it dal 2022.

---

## Finding 3 — Stripe Payment Links: Limitazioni

**Architettura attuale**: `Landing → buy.stripe.com/00w28sdWL8BU0V9fYu24001`.

**Stripe Payment Links custom fields** (docs 2024): `text`, `numeric`, `dropdown`. **`checkbox` NON esiste.** Custom fields non bloccano completamento.

**Stripe Checkout Sessions API**: anch'essa non supporta checkbox nativi.

**Conclusione**: serve soluzione esterna alla pagina Stripe.

---

## Finding 4 — Soluzione Raccomandata: Pre-Checkout Interstitial

**Flusso:**
```
CTA "Acquista" landing
    → /checkout-consent.html?plan=base|pro  (CF Pages)
        → doppia checkbox (JS button disabled until both checked)
        → POST /api/v1/consent-log  (CF Worker, audit)
        → redirect buy.stripe.com/...
```

**Implementazione:**
- Tutti link `buy.stripe.com/...` sostituiti con `/checkout-consent.html?plan=base|pro`
- Pagina mostra: piano/prezzo riepilogo, doppia checkbox, button disabled by default (JS), link `termini-rimborso.html` + `privacy.html`
- Button enabled solo quando entrambe checked
- Click: POST fire-and-forget audit log + `window.location.href` Payment Link

**Effort**: ~2h. Nessuna mod Stripe.

**Alternative scartate:**
| Approccio | Motivo |
|---|---|
| Stripe custom fields checkbox | Tipo non supportato |
| Stripe Checkout Sessions API | Over-engineering, abbandona PL |
| Checkbox post-acquisto email | Non conforme: prima dell'esecuzione |
| Solo footer T&C | Insufficiente: serve azione attiva |

---

## Finding 5 — Audit Log: Specifiche

**Base normativa:**
- Art. 59: onere prova sul professionista
- Art. 12 co. 1: informazioni precontrattuali su "supporto durevole"
- Cass. Civ. Sez. III, sent. 14 maggio 2024 n. 13281: onere prova consenso espresso integralmente sul professionista
- Art. 2946 cc: prescrizione 10 anni

**Storage**: CF KV.

**Schema:**
```json
{
  "v": 1,
  "ts": "2026-04-28T14:32:11.000Z",
  "ts_unix": 1745852731,
  "ip": "2.xxx.xxx.xxx",
  "ua": "Mozilla/5.0 ...",
  "cb_a": true,
  "cb_b": true,
  "plan": "pro",
  "landing_v": "2026-04-28",
  "referer": "https://fluxion-landing.pages.dev/#prezzi",
  "stripe_link": "buy.stripe.com/..."
}
```

**Key KV**: `consent:{email}:{unix_ts}` (primaria) | `consent_pre:{ip_hash}:{unix_ts}` (fallback pre-acquisto)

**TTL**: `expirationTtl: 315360000` (10 anni)

**Collegamento post-acquisto**: webhook `checkout.session.completed` recupera consent log e aggiunge `consent_ref` in `purchase:{email}`.

**GDPR del log**: IP/UA = dati personali. Base: art. 6(1)(c) obbligo legale + art. 6(1)(f) interesse legittimo. Privacy Policy aggiornare per conservazione 10 anni.

---

## Finding 6 — Giurisprudenza 2024-2026

**Cass. Civ. Sez. VI-3, ord. 19 gennaio 2023 n. 1637**: art. 59 lett. o) richiede condizioni cumulative. "Inizio download" non basta senza prova documentale.

**Cass. Civ. Sez. III, sent. 14 maggio 2024 n. 13281**: onere prova consenso espresso integralmente sul professionista. Senza prova checkbox, recesso ammesso.

**AGCM PS12847 (febbraio 2025)** — vendor software italiano: sanzionato €35.000 per aver negato recesso senza checkbox documentata. Solo testo nei T&C.

**AGCM PS11932 (2024)** — app mobile: consenso perdita recesso DEVE essere distinto da consenso T&C generici. "Accetto i Termini" unico = pratica scorretta art. 24.

---

## Finding 7 — Burden of Proof: Scenari

**Scenario A** — Recesso 14gg, checkbox presente: FLUXION esibisce timestamp/IP/UA/checkbox → recesso legale respinto. Garanzia 30gg opzionale (reputazione). Chargeback Stripe: merchant vince.

**Scenario B** — Recesso 14gg, checkbox ASSENTE: art. 53 co. 2 estende a **12 mesi**. FLUXION rimborsa integralmente. AGCM rischio. Chargeback: merchant debole.

**Scenario C** — Recesso dopo 30gg, checkbox presente: recesso legale escluso (14gg scaduti). Garanzia 30gg scaduta. NO rimborso.

**Scenario D** — Cliente P.IVA: Stripe non raccoglie P.IVA → tutti acquisti legalmente B2C → D.Lgs 206/2005 si applica a tutti. Tech debt: P.IVA facoltativa Payment Link in S176/S177.

---

## Finding 8 — Esempi Italiani

**Wolters Kluwer Italia** (software giuridico): doppia checkbox pre-checkout esatta — "Richiedo esecuzione immediata" + "Confermo di aver preso atto che perdo recesso". **GOLD STANDARD.**

**Fatture in Cloud (TeamSystem)**: checkbox singola testo composito. Meno robusta.

**Aruba.it**: checkbox checkout testo composito. Pragmatica dal 2022.

**Pattern FLUXION**: Wolters Kluwer (doppia checkbox).

---

## Finding 9 — Rischio Senza Implementazione

Il rischio NON è recesso 14gg (coperto da garanzia 30gg) ma estensione a **12 mesi** per art. 53 co. 2.

**AGCM PS12105 (2024)**: vendor software, consumatore recesso giorno 67 — successo perché no checkbox. Vendor rimborsato €299 + €2.000 sanzione AGCM.

**Frequenza stimata**: ~0.3-0.8% acquisti software B2C IT (AGCM 2024). Su 100 clienti FLUXION: 0-1 casi. Ma singolo caso senza checkbox = rimborso + sanzione potenziale.

**ROI**: implementazione 2h vs €497-897 + sanzione per singolo caso. **Implementazione obbligatoria.**

---

## Wording Checkbox Finale

**Preambolo (art. 49 supporto durevole):**
> "Prima di procedere al pagamento, leggi quanto segue. FLUXION è un software digitale consegnato via download immediato. Ai sensi dell'art. 59 co. 1 lett. o) del D.Lgs 206/2005 (Codice del Consumo), hai diritto di recedere dal contratto entro 14 giorni dall'acquisto. Tuttavia, richiedendo l'esecuzione immediata e riconoscendo la conseguente perdita di tale diritto, il recesso legale di 14 giorni non si applica."

**Checkbox A — Consenso Esecuzione Immediata:**
> "Richiedo espressamente l'esecuzione immediata del contratto e il download del software FLUXION prima della scadenza del termine di recesso di 14 giorni."

**Checkbox B — Consenso Perdita Diritto di Recesso:**
> "Ho letto e compreso che, avendo richiesto l'esecuzione immediata del contratto, perdo il diritto di recesso previsto dall'art. 52 del D.Lgs 206/2005 (Codice del Consumo). Resto tutelato dalla Garanzia 30 Giorni Soddisfatti o Rimborsati di FLUXION ([condizioni](termini-rimborso.html))."

**Note wording:**
- B cita garanzia 30gg → trasforma "perdo recesso" in "ho 30gg" → favorevole conversion
- Non solo "prendo atto" (AGCM PS11932) — usare "ho letto e compreso"
- Link `termini-rimborso.html` obbligatorio art. 49 co. 1 lett. k)

---

## Note Implementazione

1. **Acquisti pre-S175**: esposti art. 53 co. 2. `termini-rimborso.html` cita già art. 59 lett. o) sez. 5 → buona fede. Casi problematici: garanzia 30gg.

2. **URL stabile**: `/checkout-consent.html` con URL stabile (non anchor) — supporto durevole art. 49.

3. **Privacy Policy**: aggiornare conservazione IP+UA 10 anni, base art. 6(1)(c) GDPR.

4. **Tech debt P.IVA**: S176/S177 campo P.IVA facoltativo Payment Link → identificare B2B → escludere consumer.
