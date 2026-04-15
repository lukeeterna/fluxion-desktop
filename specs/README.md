# Specs FLUXION

Una directory per feature, creata da `/spec nome-feature`.

## Struttura
```
specs/{nome-feature}/
  requirements.md  ← EARS criteria (testabili con cargo test / npm test)
  design.md        ← architettura Tauri2 + React19, pattern esistenti
  tasks.md         ← task atomici + comando verifica + expected output
```

Il validator legge requirements.md — non la memoria del chat.
