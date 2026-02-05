# Skill: Fluxion Build Verification

## Descrizione
Skill automatica per la verifica pre-build del progetto FLUXION. Viene attivata automaticamente quando si parla di build, deploy o produzione.

## Trigger
Questa skill si attiva quando:
- L'utente chiede "build di produzione"
- L'utente chiede "deploy"
- L'utente chiede "rilascia l'app"
- L'utente chiede "fai il build"
- L'utente chiede se l'app è pronta per produzione
- Vengono fatte modifiche significative al codice

## Procedura Automatica (NON NEGOZIABILE)

Quando attivata, ESEGUI SEMPRE in ordine:

```
┌─────────────────────────────────────────────────────────┐
│ STEP 1: Verifica TypeScript                              │
│ Comando: npm run type-check                             │
│ Se errore → STOP, lista errori, chiedi se fixare        │
│ Se OK → prosegui                                        │
├─────────────────────────────────────────────────────────┤
│ STEP 2: Verifica Rust                                    │
│ Comando: cargo check --lib                              │
│ Se errore → STOP, lista errori, chiedi se fixare        │
│ Se OK → prosegui                                        │
├─────────────────────────────────────────────────────────┤
│ STEP 3: Verifica Test Rust                               │
│ Comando: cargo test --lib (se esistono test)            │
│ Se errore → STOP, lista test falliti                    │
│ Se OK → prosegui                                        │
├─────────────────────────────────────────────────────────┤
│ STEP 4: Report Risultati                                 │
│ Comunica: "✅ Verifica completata. X errori, Y warning" │
│ Solo se 0 errori → suggerisci build produzione          │
└─────────────────────────────────────────────────────────┘
```

## Regola Fondamentale

**MAI suggerire `npm run tauri build` o `cargo build --release` senza aver completato la procedura di verifica.**

Se la verifica fallisce:
1. NON suggerire il build
2. Mostra gli errori trovati
3. Chiedi: "Vuoi che fixo questi errori prima di procedere?"
4. Solo dopo il fix e nuova verifica OK → suggerisci build

## Comandi di Verifica Rapida

```bash
# TypeScript
npm run type-check

# Rust
pushd src-tauri && cargo check --lib && popd

# Test Rust  
pushd src-tauri && cargo test --lib && popd

# Tutti insieme (su iMac via SSH)
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && npm run type-check && cd src-tauri && cargo check --lib"
```

## Gestione Errori Comuni

### Errori TypeScript
- Componenti UI mancanti → Crea componenti base
- Type mismatch → Aggiungi type assertions
- Import non usati → Rimuovi import
- Export duplicati → Unifica export

### Errori Rust
- Borrow checker → Usa `.clone()` o `.unwrap_or_else()`
- Type mismatch → Aggiungi type annotations
- Missing fields → Aggiungi campi mancanti alle struct

## Output Standard

Dopo ogni verifica, comunica sempre:
```
## Stato Verifica

| Check | Stato | Dettagli |
|-------|-------|----------|
| TypeScript | ✅/❌ | X errori, Y warning |
| Rust | ✅/❌ | X errori, Y warning |
| Test | ✅/❌ | X passati, Y falliti |

**Risultato**: Pronto per produzione / NON pronto
```

## Esempio di Conversazione

### ❌ SBAGLIATO (NON FARE)
```
Utente: "Fai il build di produzione"
Agente: "Ok, ecco il comando: npm run tauri build"
```

### ✅ CORRETTO (DA FARE)
```
Utente: "Fai il build di produzione"
Agente: "Verifico lo stato del progetto prima del build..."
       [esegue verifica automatica]
       "Trovati 34 errori TypeScript. Vuoi che li fixo prima?"
       [dopo fix]
       "✅ Verifica completata. 0 errori. Ora posso procedere con il build."
```

## Note Tecniche

- Ambiente iMac: `/Volumes/MacSSD - Dati/fluxion`
- Ambiente MacBook: `/Volumes/MontereyT7/FLUXION`
- Per verifiche veloci usa sempre l'iMac via SSH (ha Rust/Node)
- Il comando `npm run type-check` usa `tsc --noEmit`
- Il comando `cargo check` è più veloce di `cargo build`

## Aggiornamenti

Questa skill viene aggiornata quando:
- Vengono trovati nuovi pattern di errori
- Cambia lo stack tecnologico
- Si aggiungono nuovi comandi di verifica
