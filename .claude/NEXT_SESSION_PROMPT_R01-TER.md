# FLUXION — anti-refund R-01-ter — EXECUTE (resume su branch esistente)

> Prompt corretto 2026-06-02 dopo ricognizione codice reale (S327-bis).
> Il prompt originale era STALE: scritto come fresh-start mentre il branch
> aveva già 4 commit che chiudono ~60% dei Task. Questo parte dal punto giusto.

RUOLO: implementatore security-critical. STOP yes/no su OGNI Edit (L0).
Niente credenziali nell'output. NON ri-diagnosticare ciò che è "GIÀ FATTO".

## STATO VERIFICATO (codice reale, branch fix/license-interop-r01-s327, NON ri-aprire)
- Branch già attivo, 4 commit. NON ricreare. `git status` pulito → checkpoint prima di ogni delete.
- ✅ Task 1+2 DONE: activate-by-email rimosso end-to-end (route, src/lib, test,
  index.ts, FE emailMode). FE = solo "Codice Licenza". 0 chiamanti sorgente (commit 23737c5).
- ✅ Task 2e DONE: refund gate KV in license-recovery.ts:107-132 (410 REFUNDED dopo HMAC).
- ✅ Task 3a DONE: email-embed payload+signature in stripe-webhook.ts:64-174.
- ✅ TF-1 RISOLTO: license_cache è SQLite upsert (license_ed25519.rs:400-421); colonna
  last_validated_at + UPDATE path GIÀ esistono (:951-993). UNICO gap = get_license_status_ed25519
  non la mette nella SELECT (:469-476). → niente secondo store; Task 3 = SELECT + cablaggio.
- Infra heartbeat GIÀ esistente da RIUSARE (non ricostruire): src/lib/phone-home.ts
  (grace_period_days), comando validate_license_online (lib.rs:1139), SaraTrialBanner,
  LicenseStatus "Valida Online". Cablarli a /validate + refund-KV per il path Ed25519.

## LAVORO RESIDUO (solo questo)
### Task 0 — webhook refund/chargeback (PREREQUISITO)
In stripe-webhook.ts, tra verifica firma (:425) e guard checkout-only (:427), gestisci
charge.refunded + charge.dispute.created → KV purchase:{email}.refunded=true + refunded_at,
key/normalizzazione = refund.ts (purchase:{email}, email.toLowerCase().trim()).
- charge.refunded: email da billing_details.email ?? receipt_email.
- charge.dispute.created: dispute non porta email → stripe.charges.retrieve(dispute.charge).
- KV-miss/parse-fail → fail-soft 200 (no retry-storm), crea record minimo refunded.
- DA VERIFICARE in impl (Stripe API ufficiale): shape Dispute.charge expandable + presenza email su Charge.
- Config (Luke, a deploy): sottoscrivere i 2 eventi nel webhook Stripe.
Evidence G-T0: Stripe TEST refund → KV mostra refunded:true.
(Diff completo già pronto: vedi cronologia sessione S327-bis, blocco "Task 0".)

### Task 3b — endpoint POST /license/validate
input license_id/email → legge KV purchase:{email} →
{status:"valid"|"revoked", server_time(firmato)}.
DECIDI esplicito: chiave KV MANCANTE → "valid" (fail-open, no brick paganti su KV flaky).

### Task 3c/3d — cablaggio path Ed25519 (riusa infra esistente)
- Aggiungi last_validated_at alla SELECT di get_license_status_ed25519 (:469-476).
- phone-home/heartbeat → punta a /validate: valid→update last_validated_at; revoked→lock subito;
  offline→consenti se now-last_validated_at<7gg, oltre→LOCK; guard now<last_validated_at→lock.
- Banner pre-lock (<2gg): "Riconnetti entro N giorni". Mai lock silenzioso.

## DEFERRED-CON-TRIGGER (registra in wiki/projects/FLUXION/DECISIONS.md come D-XX)
Binding hardware (fingerprint macchina + conteggio macchine).
Trigger: "primo abuso multi-macchina osservato su cliente reale". Costruire su evidenza, non ipotesi.

## GATE DI CHIUSURA (fatto terminale esterno)
G1: npm run type-check EXIT 0 (output reale).
G2: E2E EMAIL-EMBED (Stripe TEST 4242): webhook→email con licenza→activate_license_v1→
    license_cache POPOLATA→tamper payload→false. Evidence reale.
G3: E2E REFUND: refund test→KV refunded:true→/validate revoked→features off;
    + mock last_validated_at -8gg offline→LOCK. Evidence reale.
BLOCKED-ON (non blocca verde): deploy live (#1), count D1 (#2), smoke €1 live.

## ACCEPTANCE (onestà sul residuo — non vendere assoluti che il design non mantiene)
- Nessun payload/signature su endpoint senza HMAC (grep).  ✅ già vero
- activate-by-email rimosso (grep 0 chiamanti).            ✅ già vero
- Refund/chargeback Stripe → KV refunded:true automatico (Task 0).
- Online: revoca IMMEDIATA al primo /validate.
- Offline: lock alla scadenza grazia (7gg) con clock onesto.
- RESIDUO DOCUMENTATO (3 limiti reali del design client-enforced):
  1. binario patchabile (app ad-hoc/unsigned) → utente sofisticato salta il lock del tutto;
  2. clock-freeze locale aggira la grazia offline (non serve rollback, basta congelare l'orologio);
  3. fail-open su KV-miss → rimborsato con chiave evitta riottiene accesso (improbabile, TTL 10 anni).
  GARANZIA FORTE = revoca-online-immediata. L'offline è "fiducia nel client", non DRM.
  Binding DEFERRED-con-trigger registrato.
