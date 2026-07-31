# stress_verticali_v2_debug.md — diagnostica per Sol

## 1. Ambiente
- Data/ora: 2026-07-31T20:13:21.121+02:00
- OS: Darwin 21.6.0 / Python 3.9.6
- Directory esecuzione: /Volumes/MacSSD - Dati/FLUXION
- Commit HEAD: 4ce8b5e3
- Repository root: /Volumes/MacSSD - Dati/FLUXION
- Database clienti: /Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db
- Vertical DBs path: /Volumes/MacSSD - Dati/FLUXION/voice-agent/data/vertical_dbs
- FLUXION_DB_PATH env: non impostato

### Porte
- :3002 (voice agent): vedi preflight
- :3003: non usata da questo script

## 2. File
- Script: /Volumes/MacSSD - Dati/FLUXION/vos/runs/20260731/stress_verticali_v2.py
- SHA-256: 66dc5ad094780838a24057e2d69e62aa405e02fa99b3d4c60248dc4338f9fb41
- Asset E2E: /Volumes/MacSSD - Dati/FLUXION/voice-agent/tests/e2e/test_sara_stress_per_verticale.py (presente)
- Modifiche v1→v2: vedi header del file

## 3. Preflight e note di esecuzione

- 1. commit HEAD: 4ce8b5e3
- 2. processo :3002: UP
- 3. /health: HTTP 200 status=ok
- 4. /api/voice/voip/status: HTTP 200
- 5. SIP registered: True
- 6. reg_status: 200
- 7. linea occupata: False
- 8. verticale corrente: ?
- 9. asset E2E: /Volumes/MacSSD - Dati/FLUXION/voice-agent/tests/e2e/test_sara_stress_per_verticale.py — PRESENTE
- 10. DB verticali trovati: ['salone', 'auto', 'odontoiatra', 'fisioterapia', 'palestra', 'beauty']
- 11. DB clienti: /Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db
- 12. sintassi script: OK (importato correttamente)

## 4. Debug booking

[BOOKING:Parrucchiere / Barbiere] loop FSM rilevato: stato 'waiting_date' ripetuto 4x consecutivi

[BOOKING:Officina Auto] loop FSM rilevato: stato 'waiting_date' ripetuto 4x consecutivi

[BOOKING:Studio Odontoiatrico] FSM=completed ma action=booking_in_progress (atteso booking_created)
  sequenza: waiting_name → waiting_name → disambiguating_name → registering_surname → registering_phone → confirming_phone → waiting_date → waiting_date → waiting_date → waiting_time → confirming → confirming → completed

[BOOKING:Studio di Fisioterapia] FSM=completed ma action=booking_in_progress (atteso booking_created)
  sequenza: waiting_name → waiting_name → waiting_date → confirming → completed

[BOOKING:Palestra / Centro Fitness] loop FSM rilevato: stato 'waiting_time' ripetuto 4x consecutivi

[BOOKING:Centro Estetico] loop FSM rilevato: stato 'waiting_time' ripetuto 4x consecutivi


## 5. Fixture e cleanup
- Tag run: stress-v2:20260731T201106:19113:b37fb379
- DB: /Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db
- Clienti creati: 6
  - parrucchiere: id=cea581ff78907fc156540a9f5123ae4c tel=3895521466
  - officina: id=78bf7eac6e5e3da5cdb730ce7321f0c6 tel=3895521467
  - dentista: id=8b2a84fe3f270a9b5b41a2591d21fa77 tel=3895521468
  - fisioterapia: id=7d69749546180e2fbcc573541d5229bf tel=3895521469
  - palestra: id=b3bc71da97357b653a173776bcbae117 tel=3895521470
  - estetica: id=3d765d2fed91dc1538684ea2d2b01f87 tel=3895521471
- Stato cleanup: OK: rimosse 6 fixture e relativi dati
- Verticale ripristinato: OK: salone ripristinato

## Richiesta di correzione a Sol

Se ci sono problemi, descrivili qui:
