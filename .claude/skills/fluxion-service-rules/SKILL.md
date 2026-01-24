# FLUXION Service Management Rules

## REGOLA CRITICA: Riavvio Servizi Dopo Modifiche

### Python Voice Agent
Dopo QUALSIASI modifica ai file in `voice-agent/src/`:
```bash
# OBBLIGATORIO: Riavviare la pipeline Python su iMac
ssh imac "pkill -f 'python main.py' && cd /Volumes/MacSSD\ -\ Dati/fluxion/voice-agent && source venv/bin/activate && nohup python main.py > /tmp/voice-pipeline.log 2>&1 &"
```

### Rust HTTP Bridge
Dopo QUALSIASI modifica ai file in `src-tauri/src/`:
```bash
# L'app Tauri deve essere riavviata (manualmente o con tauri dev)
ssh imac "pkill -f tauri-app || true"
# Poi riavviare con: npm run tauri dev
```

## Checklist Pre-Test Voice Agent

Prima di testare il Voice Agent con curl o UI:

1. ✅ Verificare che la pipeline Python sia stata riavviata dopo le modifiche
2. ✅ Verificare PID del processo Python:
   ```bash
   ssh imac "ps aux | grep 'python main.py' | grep -v grep"
   ```
3. ✅ Confrontare timestamp avvio con timestamp ultimo file modificato

## Verifica Servizi

```bash
# Script automatico
bash .claude/hooks/check-services.sh

# Manuale
ssh imac "lsof -i :3001"  # HTTP Bridge
ssh imac "lsof -i :3002"  # Voice Pipeline
```

## Riavvio Completo

```bash
bash .claude/hooks/restart-services.sh
```

## Warning Signs

Se i test passano ma l'app non funziona:
1. ❌ Pipeline NON riavviata dopo modifiche Python
2. ❌ App Tauri NON ricompilata dopo modifiche Rust
3. ❌ Git non sincronizzato tra MacBook e iMac

## Sync Workflow

```
1. Modifica file su MacBook
2. scp file su iMac (o git push + pull)
3. Ricompila/Riavvia servizio
4. Test
```
