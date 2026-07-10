# PER IL GIUDICE — Sistema Marketing/Fidelizzazione FLUXION: stato di implementazione reale

> Artefatto durevole (repo, non /tmp). Sessione 2026-07-10. Verifica statica di cablaggio, non test E2E runtime.

**Metodo di verifica (vince il disco):** ogni feature tracciata lungo la catena completa `migration DB → comando Rust registrato in invoke_handler → hook React Query → componente UI → pagina montata`. "🟢 piena" solo se tutti e 5 gli anelli esistono. "🟡 parziale" se il backend esiste ma manca la superficie UI.

## Stato per sottosistema

| # | Sottosistema | Stato | Evidenza catena completa |
|---|---|---|---|
| 1 | **Tessera Timbri** (loyalty a soglia) | 🟢 PIENA | mig `005_loyalty_pacchetti_vip.sql` → `get_loyalty_info`/`increment_loyalty_visits`/`set_loyalty_threshold` (lib.rs:1029-1032) → `useLoyaltyInfo` → `LoyaltyProgress.tsx` → montato in `ClienteDialog.tsx` |
| 2 | **Status VIP** | 🟢 PIENA | `toggle_vip_status` (lib.rs:1031) → `useToggleVipStatus` → toggle+Switch in `LoyaltyProgress.tsx:216` |
| 3 | **Pacchetti** (bundle, ciclo di vita completo) | 🟢 PIENA | mig `006_pacchetto_servizi.sql` → 11 comandi CRUD+lifecycle (lib.rs:1038-1049) → hooks → `PacchettiAdmin.tsx`+`PacchettiList.tsx` → montati in `Impostazioni.tsx` + `ClienteDialog.tsx` |
| 4 | **WhatsApp bulk marketing** | 🟢 PIENA | mig `022_whatsapp_invii_pacchetti.sql` (lib.rs:349) → `get_clienti_per_invio_whatsapp`+`invia_pacchetto_whatsapp_bulk` (lib.rs:1051-1052) → `WhatsAppPacchettiSender` in `PacchettiAdmin.tsx:71` (filtri tutti/vip/vip_3_plus + template personalizzato) |
| 5 | **Compleanni** (automazione +8% return) | 🟢 PIENA | `get_clienti_compleanno_settimana` (lib.rs:1036) → `useCompeanniSettimana` → widget in `Dashboard.tsx:373` |
| 6 | **Milestones** (clienti a ridosso del premio) | 🟢 PIENA | `get_loyalty_milestones` (lib.rs:1035) → `useLoyaltyMilestones(3)` → surface in `Clienti.tsx:51` |
| 7 | **Referral / passaparola** | 🟡 **PARZIALE** | backend completo (`set_referral_source` lib.rs:1033, `get_top_referrers` lib.rs:1034, mig con `referral_cliente_id`) MA nessuna UI lo usa — vedi gap sotto |

## Cosa manca (gap onesti, verificati)

**Gap 1 — Referral non impostabile da UI.** Comando `set_referral_source` + hook `useSetReferralSource` esistono, ma grep su tutti i `.tsx` = 0 occorrenze d'uso. `LoyaltyProgress.tsx:228` mostra `referral_source` solo in lettura ("Consigliato da: …"). Conseguenza: il campo referral non può essere popolato dall'app → dati passaparola vuoti salvo scrittura diretta in DB.

**Gap 2 — Classifica Top Referrer mai mostrata.** `get_top_referrers` + `useTopReferrers` esistono, ma 0 componenti li usano. Classifica ambasciatori = dato morto: calcolabile, mai visualizzato → impossibile premiare chi porta clienti.

**Gap 3 — Loop di riscossione premio non chiuso in software.** Al 100% l'UI mostra "Premio sbloccato!" (`LoyaltyProgress.tsx:135`) e disabilita il tasto +Timbro (`disabled={…||isAtMilestone}`), ma non esiste comando di redemption: nessun reset tessera, nessuno sconto auto-applicato. Consegna premio = gesto manuale fuori dal software.

**Gap 4 — Nessuna automazione premio su conversione referral.** `set_referral_source` registra soltanto; non concede punti/sconto automatici a chi ha portato il cliente. "Premiazione" passaparola interamente manuale.

## Sintesi

5 dei 7 sottosistemi (tessera timbri, VIP, pacchetti, WhatsApp bulk, compleanni) + milestones sono pienamente implementati e montati in pagine reali. Il **referral è a metà**: backend e schema pronti, privo di UI in scrittura (Gap 1) e in lettura-classifica (Gap 2). Trasversalmente, la **chiusura del ciclo premio** (riscossione loyalty + reward referral automatico, Gap 3-4) non è implementata: il software traccia e segnala, ma erogazione premio = azione manuale operatore.

**Nota di cautela CTO:** verifica di *cablaggio* (i 5 anelli esistono), non test E2E runtime. App non eseguita, rami non esercitati a runtime in questa sessione. "🟢" attesta catena collegata, non ogni ramo provato con dati reali.
