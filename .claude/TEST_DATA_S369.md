============================================================
 FLUXION — DATI TEST E2E S369  (acquisto €1 + onboarding)
 Mail di test: ilcombeeretrasher@gmail.com
============================================================

ORDINE OBBLIGATORIO: paga → apri mail → ATTIVA via link recovery → wizard → clienti → SOLO ALLA FINE rimborso.
(Se rimborsi prima dell'attivazione, il recovery va in errore 410.)

------------------------------------------------------------
 PASSO 1 — ACQUISTO €1 DAL FUNNEL LANDING REALE
------------------------------------------------------------
URL landing: https://fluxion-landing.pages.dev/checkout-consent?plan=test
   -> mostra "FLUXION Base (test €1)" a €1
   -> spunta le 2 caselle consenso A e B
   -> "Procedi" reindirizza alla pagina Stripe Checkout (€1 reale)
Email:      ilcombeeretrasher@gmail.com        <-- IMPORTANTE: questa identica, non altre
Importo:    € 1,00 (reale, lo rimborso io a fine test)
Carta:      la tua carta vera (verrà rimborsata)
Nome su carta / intestatario: Gianluca Di Stasi
Indirizzo fatturazione (se chiesto):
   Via Roma 15 — 85024 Lavello (PZ) — Italia

------------------------------------------------------------
 PASSO 2 — MAIL LICENZA
------------------------------------------------------------
Apri la casella ilcombeeretrasher@gmail.com.
Mittente atteso: FLUXION <licenze@fluxion-app.com>
Verifica: la mail ARRIVA e si apre. Copia il LINK DI RECOVERY (o il payload) dalla mail.
NON usare "carica file". Usa il percorso DEFAULT (link/payload dalla mail).

------------------------------------------------------------
 PASSO 3 — SETUP WIZARD (7 step) — dati pronti da incollare
------------------------------------------------------------

>>> STEP 1 — Dati Attività
   Nome Attività:   Combe Barber Shop
   Partita IVA:     [PRIMA prova quella ERRATA per il test #2 — vedi sotto]
                    poi quella corretta: 12345678903
   Codice Fiscale:  (lascia vuoto, opzionale)
   Telefono:        0972800123
   Email:           ilcombeeretrasher@gmail.com

   *** TEST #2 (riepilogo errori): allo STEP 1 metti P.IVA = 123456789 (9 cifre)
       e premi Avanti -> DEVE comparire un toast "Controlla i campi" / riepilogo errori
       e il campo P.IVA evidenziato. Poi correggi in 12345678903 e prosegui.

>>> STEP 2 — Sede Legale
   Indirizzo:       Via Roma 15
   CAP:             85024
   Città:           Lavello
   Provincia:       PZ
   PEC:             (lascia vuoto, opzionale)

>>> STEP 3 — Tipo Attività (macro)
   Scegli:          Hair / Parrucchieri  (💇)

>>> STEP 4 — Specializzazione (micro)
   Scegli:          Barbiere

>>> STEP 5 — Licenza
   Tier:            Base (€497)   [il €1 di test attiva la Base]
   Chiave IA:       (lascia vuoto — arriva con la licenza)

>>> STEP 6 — Configurazione Finale
   *** TEST #3 (dropdown): apri i menu a tendina e verifica che NON si sovrappongano
       al contenuto sotto (devono aprirsi verso il basso, senza coprire altri campi).
   Categoria attività: Salone
   Regime fiscale:     RF19 — Forfettario
   WhatsApp:           393331234567
   Numero EHIWEB:      0972536918

>>> STEP 7 — Firma Contratto
   Nome firmatario:    Gianluca Di Stasi
   Email firmatario:   ilcombeeretrasher@gmail.com
   Stile firma:        (scegli il primo)
   [X] Accetto il contratto

------------------------------------------------------------
 PASSO 4 — TEST CLIENTI (B1) — validazione form
------------------------------------------------------------
Vai in Clienti -> Nuovo Cliente.
   Nome:       Mario
   Cognome:    Rossi
   Telefono:   (LASCIA VUOTO)
   -> premi SALVA
   *** ATTESO: toast "Controlla i campi del modulo" (NON salva in silenzio).

------------------------------------------------------------
 PASSO 5 — TEST CRUD CLIENTI (giro completo)
------------------------------------------------------------
1) CREA cliente valido:
   Nome:       Mario
   Cognome:    Rossi
   Telefono:   3331112222
   Email:      mario.rossi@example.com
   -> Salva (deve salvare)
2) CERCA / FILTRA: cerca "Mario" -> deve comparire.
3) MODIFICA: cambia telefono in 3334445555 -> Salva.
4) ARCHIVIA o ELIMINA: con richiesta di CONFERMA.
   *** ATTESO: nessun errore bloccante in tutto il giro.

------------------------------------------------------------
 NOTE
------------------------------------------------------------
- Cosmetici / piccole imperfezioni -> segnali a me, vanno in backlog (non bloccano).
- Bloccanti veri (crash, salvataggio impossibile, mail non arriva) -> stop, me lo dici.
- Quando hai pagato dimmelo: verifico io via API Stripe (charge + D1 + invio mail).
- A fine giro: ti rimborso il €1 e disattivo il link di test.
============================================================
