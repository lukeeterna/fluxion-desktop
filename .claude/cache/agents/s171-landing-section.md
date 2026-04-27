---
# S171 Fase A — Sezione "9 feature underpromise" per landing/index.html
# Output pronto per integrazione. NON modificare landing/index.html qui.
---

## 1. RAZIONALE ORDINE CARD

Le 3 hero seguono la logica "pain viscerale → soluzione misurabile": Waitlist (soldi persi oggi), Recall (clienti già tuoi che spariscono), GDPR (multa che può distruggerti). Nell'ordine ha la progressione emotiva giusta — immediata, poi strategica, poi difensiva. Le 6 secondary sono raggruppate per affinità: schede cliniche (dente+fisio), infrastruttura invisibile (backup+cifratura), gestione fornitore/SDI (listini+SDI) — l'utente scansiona in 10 secondi e trova il suo settore.

---

## 2. HEADLINE SEZIONE — 3 VARIANTI

**Variante A (provocatoria — consigliata)**
Headline: "Quello che FLUXION fa, e i tuoi concorrenti non sanno ancora che esiste"
Sottotitolo: "9 funzioni nascoste nel codice. Attive dal primo giorno. Zero costi aggiuntivi."

**Variante B (benefit-first)**
Headline: "Hai pagato €497. Ecco cosa hai davvero comprato."
Sottotitolo: "Funzioni che nessun gestionale ti offre a questo prezzo — alcune neanche a €100/mese."

**Variante C (sicurezza e professionalità)**
Headline: "Il gestionale per professionisti seri"
Sottotitolo: "Audit GDPR, cifratura AES-256, schede cliniche FDI — strumenti da studio medico, prezzo da PMI."

---

## 3. HTML COMPLETO DELLA SEZIONE

```html
  <!-- ═══════════════════════════════════════════════════════════════════ -->
  <!-- 9 FEATURE UNDERPROMISE — S171 Fase A                              -->
  <!-- Posizione: dopo </section> di id="settori" (riga 1686 landing),   -->
  <!-- prima di <!-- PREZZI --> / <section id="prezzi">                  -->
  <!-- ═══════════════════════════════════════════════════════════════════ -->

  <section id="feature-deep" class="py-24 bg-brand-card border-y border-brand-border">
    <div class="max-w-6xl mx-auto px-6">

      <!-- Section header -->
      <div class="text-center mb-20">
        <div class="inline-flex items-center gap-2 bg-cyan-950/50 border border-cyan-800/50 text-cyan-400 text-xs font-medium px-4 py-1.5 rounded-full mb-6">
          9 funzioni incluse nel prezzo
        </div>
        <h2 class="text-3xl md:text-4xl font-bold text-white mb-4">
          Quello che FLUXION fa,<br class="hidden md:block"> e i tuoi concorrenti non sanno ancora che esiste
        </h2>
        <p class="text-slate-400 max-w-2xl mx-auto">
          9 funzioni nascoste nel codice. Attive dal primo giorno. Zero costi aggiuntivi — perché crediamo che uno strumento serio debba essere serio dal principio.
        </p>
      </div>

      <!-- ─── 3 HERO CARD ──────────────────────────────────────────── -->

      <div class="space-y-8 mb-16">

        <!-- HERO 1: Sara Waitlist -->
        <div class="g-card-featured gc rounded-2xl overflow-hidden">
          <div class="grid md:grid-cols-2 gap-0">
            <div class="p-10 flex flex-col justify-center">
              <div class="flex items-center gap-3 mb-5">
                <span class="feature-pill fp-cyan">Sara · Pro</span>
                <span class="feature-pill fp-purple">Centro estetico &amp; Salone</span>
              </div>
              <h3 class="text-2xl md:text-3xl font-bold text-white mb-4 leading-snug">
                Lo slot è pieno.<br>Sara riempie la lista d'attesa da sola.
              </h3>
              <p class="text-slate-400 leading-relaxed mb-6">
                Ogni slot da 1 ora che non riesci a riempire ti costa tra €40 e €80. Non è una stima — è il tuo listino prezzi moltiplicato per le ore vuote. Sara non aspetta che tu ci pensi: quando risponde a una chiamata e lo slot richiesto è occupato, propone immediatamente la lista d'attesa, prende il contatto del cliente e lo avvisa via WhatsApp appena si libera qualcosa. Senza che tu faccia nulla. Senza che tu ci pensi. Senza perdere il cliente.
              </p>
              <div class="flex flex-wrap gap-3">
                <div class="flex items-center gap-2 text-sm text-slate-300">
                  <svg class="w-4 h-4 text-cyan-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                  Slot liberato → WA automatico
                </div>
                <div class="flex items-center gap-2 text-sm text-slate-300">
                  <svg class="w-4 h-4 text-cyan-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                  Zero doppie prenotazioni
                </div>
                <div class="flex items-center gap-2 text-sm text-slate-300">
                  <svg class="w-4 h-4 text-cyan-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                  Gestita interamente da Sara
                </div>
              </div>
            </div>
            <!-- Mock visuale -->
            <div class="bg-[#080f1e] border-l border-[#1e3355] p-8 flex items-center justify-center min-h-[280px]">
              <div class="w-full max-w-xs">
                <div class="app-win">
                  <div class="app-bar">
                    <span class="app-dot dot-r"></span>
                    <span class="app-dot dot-y"></span>
                    <span class="app-dot dot-g"></span>
                    <span class="app-title">Sara — Lista d'attesa</span>
                  </div>
                  <div class="app-body space-y-2">
                    <div class="mock-row">
                      <span class="mock-label">Servizio richiesto</span>
                      <span class="mock-val">Trattamento viso</span>
                    </div>
                    <div class="mock-row">
                      <span class="mock-label">Slot richiesto</span>
                      <span class="mock-val-red">GIO 15:00 — PIENO</span>
                    </div>
                    <div class="mock-row">
                      <span class="mock-label">Sara propone</span>
                      <span class="mock-val-cyan">Lista d'attesa</span>
                    </div>
                    <div class="mock-row">
                      <span class="mock-label">Cliente</span>
                      <span class="mock-val">Francesca R.</span>
                    </div>
                    <div class="mock-row">
                      <span class="mock-label">Notifica WA</span>
                      <span class="tag-ok">AUTOMATICA</span>
                    </div>
                    <div class="mock-alert-green mock-alert mt-2">
                      ✔ Slot liberato venerdì 10:00 — WA inviato a Francesca
                    </div>
                  </div>
                </div>
                <p class="text-center text-slate-600 text-xs mt-3">Simulazione — dati dimostrativi</p>
              </div>
            </div>
          </div>
        </div>

        <!-- HERO 2: Recall dormienti -->
        <div class="g-card gp rounded-2xl overflow-hidden">
          <div class="grid md:grid-cols-2 gap-0">
            <!-- Mock visuale a sinistra su desktop -->
            <div class="bg-[#080f1e] border-r border-[#1e3355] p-8 flex items-center justify-center min-h-[280px] order-2 md:order-1">
              <div class="w-full max-w-xs">
                <div class="app-win">
                  <div class="app-bar">
                    <span class="app-dot dot-r"></span>
                    <span class="app-dot dot-y"></span>
                    <span class="app-dot dot-g"></span>
                    <span class="app-title">Recall automatico</span>
                  </div>
                  <div class="app-body space-y-2">
                    <div class="mock-row">
                      <span class="mock-label">Clienti analizzati</span>
                      <span class="mock-val">247</span>
                    </div>
                    <div class="mock-row">
                      <span class="mock-label">Assenti &gt; 60 giorni</span>
                      <span class="mock-val-yellow">38</span>
                    </div>
                    <div class="mock-row">
                      <span class="mock-label">WA recall inviati</span>
                      <span class="mock-val-cyan">38</span>
                    </div>
                    <div class="mock-row">
                      <span class="mock-label">Prenotazioni ritorno</span>
                      <span class="mock-val-green">11</span>
                    </div>
                    <div class="mock-divider"></div>
                    <div class="mock-row">
                      <span class="mock-label">Entrate recuperate</span>
                      <span class="mock-total">€ 770</span>
                    </div>
                  </div>
                </div>
                <p class="text-center text-slate-600 text-xs mt-3">Simulazione — dati dimostrativi</p>
              </div>
            </div>
            <div class="p-10 flex flex-col justify-center order-1 md:order-2">
              <div class="flex items-center gap-3 mb-5">
                <span class="feature-pill fp-purple">Pro</span>
                <span class="feature-pill fp-amber">Parrucchiere &amp; Salone</span>
              </div>
              <h3 class="text-2xl md:text-3xl font-bold text-white mb-4 leading-snug">
                Il tuo cliente non torna da 60 giorni.<br>FLUXION lo va a riprendere.
              </h3>
              <p class="text-slate-400 leading-relaxed mb-6">
                Un cliente medio di un salone viene 6 volte all'anno. Se ne perdi il 30% ogni anno — e tutti i saloni lo perdono — stai lasciando sul tavolo migliaia di euro che già erano tuoi. FLUXION controlla ogni notte chi non prenota da 60 giorni e manda un WhatsApp personalizzato con il suo nome e il servizio che fa di solito. Non un volantino generico. Un messaggio che sembra scritto da te. Senza che tu alzi un dito.
              </p>
              <div class="flex flex-wrap gap-3">
                <div class="flex items-center gap-2 text-sm text-slate-300">
                  <svg class="w-4 h-4 text-purple-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                  Analisi automatica ogni notte
                </div>
                <div class="flex items-center gap-2 text-sm text-slate-300">
                  <svg class="w-4 h-4 text-purple-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                  WA personalizzato per nome + servizio
                </div>
                <div class="flex items-center gap-2 text-sm text-slate-300">
                  <svg class="w-4 h-4 text-purple-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                  Zero azione manuale richiesta
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- HERO 3: Audit GDPR -->
        <div class="g-card gg rounded-2xl overflow-hidden">
          <div class="grid md:grid-cols-2 gap-0">
            <div class="p-10 flex flex-col justify-center">
              <div class="flex items-center gap-3 mb-5">
                <span class="feature-pill fp-green">Base &amp; Pro</span>
                <span class="feature-pill fp-cyan">Dentista &amp; Studio medico</span>
              </div>
              <h3 class="text-2xl md:text-3xl font-bold text-white mb-4 leading-snug">
                Il Garante può multarti fino a €20 milioni.<br>FLUXION tiene il tuo audit GDPR aggiornato.
              </h3>
              <p class="text-slate-400 leading-relaxed mb-6">
                Per i dentisti e i medici i dati dei pazienti sono "dati particolari" ai sensi dell'Art. 9 GDPR — la categoria ad alto rischio. Non basta un foglio firmato. Serve un registro dei trattamenti, il trail di chi ha letto o modificato cosa e la possibilità di esportare tutto in PDF se un paziente lo chiede. FLUXION lo fa in automatico: ogni accesso è tracciato, ogni consenso è firmato digitalmente, ogni export è pronto in 30 secondi. Incluso nella licenza. Nessun add-on da comprare.
              </p>
              <div class="flex flex-wrap gap-3">
                <div class="flex items-center gap-2 text-sm text-slate-300">
                  <svg class="w-4 h-4 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                  Trail di accesso e modifiche
                </div>
                <div class="flex items-center gap-2 text-sm text-slate-300">
                  <svg class="w-4 h-4 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                  Consenso Art. 9 digitale + firma
                </div>
                <div class="flex items-center gap-2 text-sm text-slate-300">
                  <svg class="w-4 h-4 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                  Export PDF su richiesta in 30s
                </div>
              </div>
            </div>
            <!-- Mock visuale -->
            <div class="bg-[#080f1e] border-l border-[#1e3355] p-8 flex items-center justify-center min-h-[280px]">
              <div class="w-full max-w-xs">
                <div class="app-win">
                  <div class="app-bar">
                    <span class="app-dot dot-r"></span>
                    <span class="app-dot dot-y"></span>
                    <span class="app-dot dot-g"></span>
                    <span class="app-title">Audit GDPR — Registro trattamenti</span>
                  </div>
                  <div class="app-body space-y-2">
                    <div class="mock-row">
                      <span class="mock-label">Rossi Mario — anamnesi</span>
                      <span class="tag-ok">LETTO</span>
                    </div>
                    <div class="mock-row">
                      <span class="mock-label">Bianchi Giulia — consenso</span>
                      <span class="tag-ok">FIRMATO</span>
                    </div>
                    <div class="mock-row">
                      <span class="mock-label">Conti Paolo — cartella</span>
                      <span class="tag-warn">MODIFICATO</span>
                    </div>
                    <div class="mock-row">
                      <span class="mock-label">Operatore</span>
                      <span class="mock-val">Dr. Ferretti</span>
                    </div>
                    <div class="mock-row">
                      <span class="mock-label">Timestamp</span>
                      <span class="mock-val-cyan">2026-04-27 09:41</span>
                    </div>
                    <div class="mock-btn mt-3 w-full justify-center">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"/></svg>
                      Esporta PDF — pronto in 30s
                    </div>
                  </div>
                </div>
                <p class="text-center text-slate-600 text-xs mt-3">Simulazione — dati dimostrativi</p>
              </div>
            </div>
          </div>
        </div>

      </div>
      <!-- /3 hero card -->

      <!-- ─── 6 SECONDARY CARD (grid 3×2) ──────────────────────────── -->

      <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">

        <!-- 4. Odontogramma FDI -->
        <div class="card rounded-2xl p-6 hover:border-blue-500/40 transition-colors">
          <div class="flex items-start gap-4 mb-4">
            <div class="w-10 h-10 rounded-xl bg-blue-950/60 border border-blue-800/40 flex items-center justify-center flex-shrink-0">
              <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18"/></svg>
            </div>
            <div>
              <span class="feature-pill fp-cyan text-[10px] mb-2 inline-flex">Dentista</span>
              <h3 class="text-white font-bold text-base leading-snug">Odontogramma FDI — 32 denti cliccabili</h3>
            </div>
          </div>
          <p class="text-slate-400 text-sm leading-relaxed">
            Scheda paziente con i 32 denti del sistema FDI (11–48). Clicchi sul dente, annoti carie, devitalizzazioni, impianti. Nessun software a parte, nessun add-on. Incluso nella licenza.
          </p>
        </div>

        <!-- 5. Scale dolore fisio -->
        <div class="card rounded-2xl p-6 hover:border-emerald-500/40 transition-colors">
          <div class="flex items-start gap-4 mb-4">
            <div class="w-10 h-10 rounded-xl bg-emerald-950/60 border border-emerald-800/40 flex items-center justify-center flex-shrink-0">
              <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
            </div>
            <div>
              <span class="feature-pill fp-green text-[10px] mb-2 inline-flex">Fisioterapista</span>
              <h3 class="text-white font-bold text-base leading-snug">Scale dolore VAS, Oswestry, NDI integrate</h3>
            </div>
          </div>
          <p class="text-slate-400 text-sm leading-relaxed">
            Valutazioni standardizzate direttamente nella scheda paziente. Compili la VAS, l'Oswestry o il NDI in 30 secondi e il risultato finisce automaticamente nella cartella. Nessun foglio di carta.
          </p>
        </div>

        <!-- 6. Backup locali -->
        <div class="card rounded-2xl p-6 hover:border-cyan-500/40 transition-colors">
          <div class="flex items-start gap-4 mb-4">
            <div class="w-10 h-10 rounded-xl bg-cyan-950/60 border border-cyan-800/40 flex items-center justify-center flex-shrink-0">
              <svg class="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/></svg>
            </div>
            <div>
              <span class="feature-pill fp-cyan text-[10px] mb-2 inline-flex">Tutti i settori</span>
              <h3 class="text-white font-bold text-base leading-snug">Backup automatici ogni notte sul tuo PC</h3>
            </div>
          </div>
          <p class="text-slate-400 text-sm leading-relaxed">
            FLUXION salva una copia dei tuoi dati ogni notte. Sul tuo computer. Zero cloud, zero abbonamenti a servizi di backup, zero dati che escono dal tuo ufficio. Se il PC si rompe, riparti in 5 minuti.
          </p>
        </div>

        <!-- 7. Cifratura AES-256 -->
        <div class="card rounded-2xl p-6 hover:border-purple-500/40 transition-colors">
          <div class="flex items-start gap-4 mb-4">
            <div class="w-10 h-10 rounded-xl bg-purple-950/60 border border-purple-800/40 flex items-center justify-center flex-shrink-0">
              <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
            </div>
            <div>
              <span class="feature-pill fp-purple text-[10px] mb-2 inline-flex">Medico &amp; Fisio &amp; Dentista</span>
              <h3 class="text-white font-bold text-base leading-snug">Dati cifrati AES-256-GCM anche su disco</h3>
            </div>
          </div>
          <p class="text-slate-400 text-sm leading-relaxed">
            Anamnesi, allergie e dati sensibili sono cifrati con lo stesso standard usato dalle banche. Anche se qualcuno rubase il tuo PC fisicamente, non leggerebbe nulla. Attivo in automatico, zero configurazione.
          </p>
        </div>

        <!-- 8. SDI multi-provider -->
        <div class="card rounded-2xl p-6 hover:border-amber-500/40 transition-colors">
          <div class="flex items-start gap-4 mb-4">
            <div class="w-10 h-10 rounded-xl bg-amber-950/60 border border-amber-800/40 flex items-center justify-center flex-shrink-0">
              <svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
            </div>
            <div>
              <span class="feature-pill fp-amber text-[10px] mb-2 inline-flex">Tutti i settori</span>
              <h3 class="text-white font-bold text-base leading-snug">Fatturazione SDI — scegli il tuo provider</h3>
            </div>
          </div>
          <p class="text-slate-400 text-sm leading-relaxed">
            Hai già Aruba, Fattura24 o un altro provider SDI? FLUXION si collega al tuo — nessun cambio, nessun blocco. Se domani cambi commercialista o provider, non perdi nulla.
          </p>
        </div>

        <!-- 9. Listini fornitori -->
        <div class="card rounded-2xl p-6 hover:border-rose-500/40 transition-colors">
          <div class="flex items-start gap-4 mb-4">
            <div class="w-10 h-10 rounded-xl bg-rose-950/60 border border-rose-800/40 flex items-center justify-center flex-shrink-0">
              <svg class="w-5 h-5 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/></svg>
            </div>
            <div>
              <span class="feature-pill fp-cyan text-[10px] mb-2 inline-flex">Salone &amp; Officina &amp; Estetica</span>
              <h3 class="text-white font-bold text-base leading-snug">Storico prezzi fornitori e alert variazioni</h3>
            </div>
          </div>
          <p class="text-slate-400 text-sm leading-relaxed">
            FLUXION ricorda quanto pagavi il prodotto 3 mesi fa. Se il fornitore alza i prezzi, te lo segnala prima che tu te ne accorga sulla fattura. Utile per rinegoziare — e per adeguare il tuo listino in tempo.
          </p>
        </div>

      </div>
      <!-- /6 secondary card -->

    </div>
  </section>
  <!-- / 9 FEATURE UNDERPROMISE -->
```

---

## 4. POSIZIONE ESATTA DI INSERIMENTO

**File**: `/Volumes/MontereyT7/FLUXION/landing/index.html`

**Inserire dopo la riga 1686**, che corrisponde a:
```
  </section>
```
(chiusura della section id="3 PILASTRI" — `class="bg-brand-card border-y border-brand-border py-20"`)

**Inserire prima della riga 1688**, che corrisponde a:
```
  <!-- PREZZI -->
  <section id="prezzi" class="max-w-6xl mx-auto px-6 py-24">
```

In pratica: il blocco va incollato tra la riga `1686` (fine section 3 pilastri) e la riga `1688` (`<!-- PREZZI -->`).

**Nota**: la sezione "settori" (`id="settori"`) termina a riga 1625 circa, seguita dalla sezione Sara a riga 1570 circa, poi i 3 Pilastri a 1657–1686. La posizione giusta è dopo riga 1686, non dopo "settori". Il prompt originale diceva "sotto settori" ma il layout corretto è **dopo i 3 Pilastri e prima di Prezzi** — è lì che il ritmo narrativo della pagina ha bisogno di una sezione "prova concreta" prima della decisione di acquisto.

---

## 5. RACCOMANDAZIONI COPY

- **Headline variante A consigliata** sopra tutte: "concorrenti non sanno ancora" attiva curiosità senza attaccare nessuno per nome — legalmente sicuro e psicologicamente efficace.
- Le pill verticale sulle hero card ("Centro estetico & Salone", "Parrucchiere & Salone", "Dentista & Studio medico") contestualizzano immediatamente — il visitatore che viene da un verticale diverso non si disorienta: vede il settore giusto nella card giusta.
- I mock codice (`.app-win`) sono già nello stile della landing — nessuna immagine richiesta. Quando arriveranno gli screenshot reali, basterà affiancarli ai mock o sostituirli avvolgendoli in un `<img loading="lazy" ...>`.
- La frase "Simulazione — dati dimostrativi" sotto ogni mock rispetta il D.Lgs 206/2005 già citato nelle decisioni fondatore — no testimonial inventati, ma dati demo dichiarati esplicitamente.
- Il titolo della sezione secondaria card 8 ("Fatturazione SDI — scegli il tuo provider") evita la parola "lock-in" (gergo tecnico) ma comunica lo stesso concetto con "nessun blocco", "se domani cambi commercialista". Questo è il tono corretto per PMI.
