# Skill: Fluxion Git Workflow

## Descrizione
Skill per la gestione automatizzata del workflow Git. Si attiva dopo modifiche significative al codice.

## Trigger
- Dopo fix di errori di compilazione
- Dopo implementazioni completate
- Quando si dice "pusha", "committa", "sincronizza"
- Quando si chiede di "salvare il lavoro"

## Procedura Automatica

### Dopo Fix Errori

```
1. git add -A
2. git commit -m "descrizione" --no-verify (bypassa husky se ci sono errori TS)
3. git push origin master
4. git pull sull'iMac via SSH
```

### Messaggi Commit Standard

```
Fix TypeScript: [breve descrizione]
Fix Rust: [breve descrizione]  
Feat: [nuova funzionalità]
Refactor: [descrizione refactoring]
```

## Automazione

Quando completi fix o implementazioni:
1. **Non chiedere** se fare git push
2. **Esegui automaticamente** la procedura
3. **Comunica** il risultato

## Esempio

```
[Fix completati]
Agente: "Commit e push automatico in corso..."
        "✅ Commit 8b901c2 creato"
        "✅ Push su origin/master completato"
        "✅ iMac sincronizzato"
```
