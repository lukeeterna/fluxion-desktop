# ADR-002: Auto-Sync Festività da API Governativa

**Status**: Accepted
**Date**: 2026-01-03
**Deciders**: Backend Team, Integration Specialist

## Context

Le festività italiane cambiano annualmente (Pasqua mobile, nuove festività). L'hardcoding porta a:
- Manutenzione manuale annuale
- Errori umani (dimenticare aggiornamenti)
- Impossibilità di gestire festività regionali

## Decision

Implementare **sync automatico** da API pubblica governativa con fallback locale.

### API Primaria: Nager.Date

**Endpoint**: `https://date.nager.at/api/v3/PublicHolidays/{year}/IT`

**Esempio response 2026**:
```json
[
  {
    "date": "2026-01-01",
    "localName": "Capodanno",
    "name": "New Year's Day",
    "countryCode": "IT",
    "fixed": true,
    "global": true,
    "types": ["Public"]
  },
  {
    "date": "2026-04-05",
    "localName": "Pasqua",
    "name": "Easter Sunday",
    "countryCode": "IT",
    "fixed": false,
    "global": true
  }
]
```

### Sync Strategy

1. **Startup**: Fetch festività anno corrente + prossimo
2. **Cron Job**: Ogni 1° gennaio, fetch anno nuovo
3. **Fallback**: Se API offline, usa `config/festivita-italia-seed.json`
4. **Cache**: Salva in `giorni_festivi` table con index su `data`

### Gestione Errori

- **Rate limit (429)**: Retry con exponential backoff
- **API offline (5xx)**: Fallback immediato a seed
- **Seed obsoleto**: Log warning, operatore notificato

## Rationale

**Vantaggi**:
- **Zero manutenzione**: Aggiornamenti automatici
- **Affidabilità**: Nager.Date è FOSS, 99.9% uptime documentato
- **Festività regionali**: API supporta codici regionali (`/IT/LO` per Lombardia)

**Alternative considerate**:
- iCal governativo: Parsing complesso, nessun JSON API
- Hardcoding: Inaccettabile per produzione

## Consequences

**Positivi**:
- Sistema sempre aggiornato senza deploy
- Supporto festività future automatico

**Negativi**:
- Dipendenza esterna (mitigata da fallback)
- Necessità di monitoraggio sync (Sentry alert se fallisce)

## Implementation Notes

```rust
// src-tauri/src/services/festivita_service.rs
pub async fn sync_festivita(anno: i32) -> Result<Vec<Festivita>, ServiceError> {
    match fetch_nager_api(anno).await {
        Ok(data) => {
            db::upsert_festivita(anno, data).await?;
            Ok(data)
        }
        Err(e) => {
            log::warn!("API Nager offline: {}, using seed", e);
            load_seed_festivita(anno)
        }
    }
}
```
