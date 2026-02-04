# 🔄 PROMPT RIPARTENZA - 2026-02-04

**Stato**: Context compacted, ripartire da file  
**Fonte di verità**: `docs/VERTICALS-FINAL-6.md`, `CLAUDE.md`

---

## ✅ COSA È STATO FATTO (2026-02-03)

### Research Completa
- **6 Verticali confermati**: Parrucchiere, Estetista, Fisioterapia, Dentista, Fitness, Meccanico + Chirurgia estetica
- **100+ Micro-categorie** mappate (es: dentista → implantologo/ortodontista/parodontologo)
- **Benchmark 20+ competitor**: Fluxion 97% più economico (Lifetime €199-799 vs SaaS €50-100/mese)
- **Sistema licenze**: Ed25519 offline, hardware-locked, 3 tier

### Documenti Pronti
```
docs/VERTICALS-FINAL-6.md              ← Schema dati 6 verticali
docs/BENCHMARK-COMPETITORS.md          ← Analisi prezzi
docs/MICRO-CATEGORIE-PMI.md            ← 100+ categorie
.kimi/prompts/IDENTIFICA-MICRO-CATEGORIE-VOICE-STACK.prompt.md  ← Per ricerca
```

### Problemi Voice Agent Noti
1. Nomi/cognomi composti ("Gino Di Nanni" → perde parti)
2. Date relative complesse ("settimana prossima" - fix parziale)
3. Vincoli orari ("dopo le 17" → ignora)
4. Servizi multipli (a volte perde pezzi)
5. Persistenza contesto (dopo prenotazione, resetta)

---

## 📥 INPUT ATTESO DA UTENTE

L'utente eseguirà il prompt `IDENTIFICA-MICRO-CATEGORIE-VOICE-STACK.prompt.md` e fornirà:

```json
{
  "output_ricerca": [
    {
      "pmi_target": "Studio Dentistico Rossi",
      "micro_categoria": "implantologo_multi",
      "servizi": ["implantologia", "parodontologia", "ortodonzia"],
      "voice_compatibility": "media",
      "workarounds": ["prenota solo 'visita consulenza'", "dettagli in sede"]
    },
    {
      "pmi_target": "Salone Bella",
      "micro_categoria": "salone_donna",
      "servizi": ["taglio", "colore", "piega"],
      "voice_compatibility": "alta",
      "workarounds": []
    }
  ]
}
```

---

## 🎯 OBIETTIVO IMPLEMENTAZIONE

### Fase 1 (Priorità Alta)
1. **Sistema Licenze Ed25519**
   - Crypto module (sign/verify)
   - LicenseManager (cache, validation)
   - CLI generator (admin tool)
   - UI LicenseStatus

2. **Parrucchiere (Vertical 1)**
   - DB: `par_colorazioni`, `par_tagli`
   - Rust: models, repository, service
   - React: ColorazioniTab, TagliTab
   - Voice: base handler

3. **Estetista (Vertical 2)**
   - DB: `est_analisi_pelle`, `est_trattamenti`
   - Rust: models, repository, service
   - React: AnalisiPelleTab, TrattamentiTab
   - Voice: base handler

### Fase 2-5 (Dopo)
- Fisioterapia → Dentista → Fitness → Meccanico

---

## 🏗️ ARCHITETTURA DA IMPLEMENTARE

### License System
```rust
// src-tauri/src/license/
- crypto.rs      // Ed25519 verify/sign
- models.rs      // License, Tier, VerticalType
- manager.rs     // LicenseManager cache
- cli.rs         // Generator tool
```

### Vertical Module Pattern
```rust
// src-tauri/src/verticals/parrucchiere/
- models.rs      // Colorazione, Taglio
- repository.rs  // SQLite CRUD
- service.rs     // Business logic
```

### React Pattern
```tsx
// src/verticals/Parrucchiere/
- index.tsx      // Export
- ColorazioniTab.tsx
- TagliTab.tsx
- forms/
  - ColorazioneForm.tsx
```

---

## ⚠️ VINCOLI IMPORTANTI

### Voice Agent Limitazioni (Da rispettare)
- **NON** aggiungere intents vertical-specifici → confonde classifier
- **NON** estrarre entità complesse → usa solo: nome, data, ora, servizio, telefono
- **SEMPRE** fallback a operatore per casi complessi
- **OK** per prenotazioni semplici: (nome → servizio → data → ora)

### Database
- SQLite con JSON1 extension
- Migrations numerate 019, 020, 021...
- Foreign keys a `clienti(id)`

### Licenze
- 3 Tier: Base (€199, 1 verticale), Intermedia (€399, 3 verticali), Full (€799, 6 verticali)
- Voice Agent solo in Full tier
- Hardware fingerprint (CPU+Disk+Board)
- Offline verification (no server)

---

## 📝 CHECKLIST IMPLEMENTAZIONE

### Pre-codice
- [ ] Ricevere output ricerca micro-categorie dall'utente
- [ ] Scegliere 2 verticali da implementare prima (Parrucchiere + Estetista)
- [ ] Definire schema DB preciso

### Codice
- [ ] Migration 019: vertical_type in clienti
- [ ] Migration 020: licenze_config
- [ ] Migration 021: par_colorazioni, par_tagli
- [ ] Migration 022: est_analisi_pelle, est_trattamenti
- [ ] Rust: License crypto + manager
- [ ] Rust: Domain layer parrucchiere
- [ ] Rust: Domain layer estetista
- [ ] React: UI verticals
- [ ] Voice: Base handlers (no custom intents)

### Test
- [ ] Test licenze: verify con chiave corretta/errata
- [ ] Test licenze: hardware fingerprint check
- [ ] Test DB: CRUD operazioni
- [ ] Test Voice: prenotazione semplice end-to-end

---

## 🔗 FILE DA LEGGERE ALL'AVVIO

1. `CLAUDE.md` - Stato progetto
2. `docs/VERTICALS-FINAL-6.md` - Schema 6 verticali
3. `docs/BENCHMARK-COMPETITORS.md` - Business model
4. Output fornito dall'utente dalla ricerca micro-categorie

---

## 💬 COMANDO UTENTE ATTESO

"Ecco l'output della ricerca: [JSON]. Procedi con implementazione Fase 1 - Parrucchiere + Estetista + License System"

---

*Checkpoint 2026-02-03 18:45 | Context: 71.4% | Ready for tomorrow*
