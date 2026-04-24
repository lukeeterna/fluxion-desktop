# NORTH STAR — FLUXION

**Ultimo aggiornamento**: 2026-04-24 (S167)
**Stato**: Stabile — modificare SOLO con approvazione esplicita del fondatore (Gianluca Di Stasi).

> Questo file è il contratto strategico del progetto.
> Prima di ogni nuova feature, refactor significativo o decisione di prodotto,
> Claude DEVE rileggere questo file e verificare l'allineamento.
> In caso di ambiguità → fermarsi e chiedere a Luke, NON procedere.

---

## Chi è il cliente
**PMI italiane 1–15 dipendenti**, in settori "hands-on" dove il titolare/staff NON può rispondere al telefono mentre lavora:
- Saloni di bellezza (parrucchieri, barbieri, estetisti, nail artist)
- Wellness (palestre, centri fitness)
- Salute (cliniche, studi dentistici, fisioterapisti)
- Automotive (officine, carrozzerie, gommisti)

Profilo decisore: **titolare unico o piccolo team**, età 30–55, bassa alfabetizzazione digitale, usa WhatsApp quotidianamente, NON conosce (né vuole conoscere) concetti come "SaaS", "API", "LLM".

## Dolore risolto (frase del cliente)
> "Quando sono sotto le mani di una cliente o sul pezzo, non posso rispondere al telefono. Perdo appuntamenti ogni settimana. E non ho tempo/soldi per una segretaria."

Il cliente NON dice mai "voglio un gestionale". Dice "sto perdendo clienti".

## Valore unico — perché FLUXION vs alternative
1. **Sara — segretaria AI vocale 24/7** che risponde al telefono come una persona, prende appuntamenti nel gestionale, manda conferma WhatsApp. Non esiste in nessun competitor italiano a questo prezzo.
2. **Lifetime, non abbonamento** — €497 una volta, tua per sempre. Contrapposto a Fresha/Treatwell/Mindbody che prendono %/mese.
3. **Zero configurazione cloud** — app desktop, DB locale SQLite, dati del cliente fisicamente sulla sua macchina. Nessun account da creare, nessuna API key.
4. **Verticalizzato per settore** — wizard iniziale domanda "che lavoro fai?" e configura schede, FAQ, gergo, terminologia per quel verticale specifico.
5. **WhatsApp Business nativo** — reminder, pacchetti, recall, non "nice to have" ma core.

## Modello di ricavo
- **Base €497 lifetime** — gestionale + WhatsApp + Sara trial 30 giorni
- **Pro €897 lifetime** — gestionale completo + Sara per sempre + 1 nicchia configurata
- **Pagamento**: Stripe checkout (commissione 1.5%) → Ed25519 license key → email Resend → download
- **Nessun revenue ricorrente**. Nessun costo per cliente dopo vendita (proxy API su CF Workers free tier, licensing self-hosted).

## NON facciamo (scope esclusioni esplicite)
- **NO SaaS, NO abbonamento, NO download gratuito, NO trial senza carta** → rompe il modello.
- **NO multi-nicchia per cliente** — 1 cliente = 1 verticale configurato. Chi cambia settore, ricompra.
- **NO assistenza clienti manuale scalabile** — tutto deve essere self-service (wizard + video per settore + AI support responder). "Supporto zero" è un vincolo permanente.
- **NO multi-lingua** — solo italiano. Target esplicito: mercato IT.
- **NO versione mobile nativa** — desktop Tauri su Mac/Windows. Mobile è solo companion (WA link).
- **NO integrazioni con gestionali esistenti** (Fatture in Cloud, TeamSystem, ecc.) — FLUXION È il gestionale.
- **NO AI feature "nice to have"** — ogni feature AI deve misurare un risparmio concreto in minuti/euro per il cliente.
- **NO architetture enterprise se non strettamente necessarie** — K8s, microservizi, cloud DB = overkill per PMI 1–15 dip.

## Vincoli immutabili (business + etico)
1. **ZERO COSTI variabili per cliente** — nessuna subscription AI/cloud che scali con l'uso. Solo Cloudflare free tier, Groq free tier, Stripe 1.5%. Questo è ciò che rende possibile il lifetime pricing.
2. **ENTERPRISE-GRADE code quality** — zero `any`, zero `--no-verify`, zero workaround. Il fondatore non è developer, ma ESIGE gold standard mondiale.
3. **Dati del cliente SONO del cliente** — DB locale SQLite, mai cloud sync obbligatorio. Compliance GDPR by design (localizzazione fisica).
4. **Deep research obbligatoria** prima di ogni feature Sara — MAI improvvisare comportamento di un AI che parla coi clienti finali del cliente.
5. **"Tutto si può fare. Basta solo trovare il modo."** — Mantra del fondatore. Non dire "impossibile" o "non supportato". Se manca una tecnologia, si trova un workaround open-source. Se manca un budget, si rinuncia alla feature (non si aumenta il prezzo).

## Riferimenti vivi
- Stato operativo corrente → `HANDOFF.md`
- Procedure correnti → `.claude/PLAYBOOK.md`
- Roadmap pending → `ROADMAP_REMAINING.md`
- PRD completo → `PRD-FLUXION-COMPLETE.md`
