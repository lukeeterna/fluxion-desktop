use chrono::{Datelike, NaiveDate, NaiveDateTime, Utc};
use serde::{Deserialize, Serialize};

/// Nager.Date API response
#[derive(Debug, Deserialize)]
struct NagerHoliday {
    date: String, // "2026-01-01"
    #[serde(rename = "localName")]
    local_name: String,
    name: String,
    #[serde(rename = "countryCode")]
    country_code: String,
    fixed: bool,
}

/// Festivita stored in DB
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Festivita {
    pub data: NaiveDateTime,
    pub nome: String,
    pub ricorrente: bool,
}

/// Festivita Service - Auto-sync holidays
pub struct FestivitaService {
    pub http_client: reqwest::Client,
}

impl FestivitaService {
    pub fn new() -> Self {
        Self {
            http_client: reqwest::Client::new(),
        }
    }

    /// Fetch festività da Nager.Date API
    pub async fn fetch_from_nager(&self, year: i32) -> Result<Vec<Festivita>, FestivitaError> {
        let url = format!("https://date.nager.at/api/v3/PublicHolidays/{}/IT", year);

        let response = self
            .http_client
            .get(&url)
            .timeout(std::time::Duration::from_secs(10))
            .send()
            .await
            .map_err(|e| FestivitaError::ApiUnavailable(e.to_string()))?;

        if !response.status().is_success() {
            return Err(FestivitaError::ApiError(format!(
                "HTTP {}",
                response.status()
            )));
        }

        let holidays: Vec<NagerHoliday> = response
            .json()
            .await
            .map_err(|e| FestivitaError::ParseError(e.to_string()))?;

        Ok(holidays
            .into_iter()
            .filter_map(|h| {
                NaiveDate::parse_from_str(&h.date, "%Y-%m-%d")
                    .ok()
                    .map(|date| Festivita {
                        data: date.and_hms_opt(0, 0, 0).unwrap(),
                        nome: h.local_name,
                        ricorrente: h.fixed,
                    })
            })
            .collect())
    }

    /// Carica fallback da seed JSON
    pub fn load_from_seed() -> Result<Vec<Festivita>, FestivitaError> {
        let seed_json = include_str!("../../../config/festivita-italia-seed.json");

        #[derive(Deserialize)]
        struct SeedData {
            festivita: Vec<SeedFestivita>,
        }

        #[derive(Deserialize)]
        struct SeedFestivita {
            data: String,
            nome: String,
            ricorrente: bool,
        }

        let seed: SeedData =
            serde_json::from_str(seed_json).map_err(|e| FestivitaError::ParseError(e.to_string()))?;

        Ok(seed
            .festivita
            .into_iter()
            .filter_map(|f| {
                NaiveDateTime::parse_from_str(&format!("{} 00:00:00", f.data), "%Y-%m-%d %H:%M:%S")
                    .ok()
                    .map(|data| Festivita {
                        data,
                        nome: f.nome,
                        ricorrente: f.ricorrente,
                    })
            })
            .collect())
    }

    /// Sync strategy: prova API, fallback su seed
    pub async fn sync_festivita(&self, year: i32) -> Vec<Festivita> {
        match self.fetch_from_nager(year).await {
            Ok(festivita) => {
                tracing::info!("✅ Festività {} caricate da Nager.Date API", year);
                festivita
            }
            Err(e) => {
                tracing::warn!("⚠️ API Nager.Date non disponibile: {}", e);
                tracing::info!("📦 Carico festività da seed locale");

                match Self::load_from_seed() {
                    Ok(festivita) => festivita,
                    Err(e) => {
                        tracing::error!("❌ Errore caricamento seed: {}", e);
                        vec![] // Fallback vuoto
                    }
                }
            }
        }
    }

    /// Sync automatico: anno corrente + prossimo
    pub async fn auto_sync(&self) -> Vec<Festivita> {
        let current_year = Utc::now().year();
        let next_year = current_year + 1;

        let mut festivita = self.sync_festivita(current_year).await;
        festivita.extend(self.sync_festivita(next_year).await);

        festivita
    }

    /// Check se data è festività
    pub fn is_festivita(data: NaiveDateTime, festivita: &[Festivita]) -> Option<&Festivita> {
        festivita
            .iter()
            .find(|f| f.data.date() == data.date())
    }
}

impl Default for FestivitaService {
    fn default() -> Self {
        Self::new()
    }
}

#[derive(Debug, thiserror::Error)]
pub enum FestivitaError {
    #[error("API Nager.Date non disponibile: {0}")]
    ApiUnavailable(String),

    #[error("Errore API: {0}")]
    ApiError(String),

    #[error("Errore parsing: {0}")]
    ParseError(String),
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_load_from_seed_success() {
        let festivita = FestivitaService::load_from_seed().unwrap();

        assert!(!festivita.is_empty());

        let capodanno = festivita.iter().find(|f| f.nome == "Capodanno");
        assert!(capodanno.is_some());

        let capodanno = capodanno.unwrap();
        assert!(capodanno.ricorrente);
        assert_eq!(capodanno.data.month(), 1);
        assert_eq!(capodanno.data.day(), 1);
    }

    #[test]
    fn test_is_festivita() {
        let festivita = vec![Festivita {
            data: NaiveDate::from_ymd_opt(2026, 1, 1)
                .unwrap()
                .and_hms_opt(0, 0, 0)
                .unwrap(),
            nome: "Capodanno".to_string(),
            ricorrente: true,
        }];

        let capodanno = NaiveDate::from_ymd_opt(2026, 1, 1)
            .unwrap()
            .and_hms_opt(10, 0, 0)
            .unwrap();

        let result = FestivitaService::is_festivita(capodanno, &festivita);
        assert!(result.is_some());
        assert_eq!(result.unwrap().nome, "Capodanno");
    }

    #[test]
    fn test_is_festivita_not_found() {
        let festivita = vec![];

        let data = NaiveDate::from_ymd_opt(2026, 1, 15)
            .unwrap()
            .and_hms_opt(10, 0, 0)
            .unwrap();

        let result = FestivitaService::is_festivita(data, &festivita);
        assert!(result.is_none());
    }

    #[tokio::test]
    async fn test_fetch_from_nager_real_api() {
        let service = FestivitaService::new();

        // Test con anno corrente (può fallire se API offline)
        let result = service.fetch_from_nager(2026).await;

        // Se API è online, verifica dati
        if let Ok(festivita) = result {
            assert!(!festivita.is_empty());
            println!("✅ API Nager.Date funzionante: {} festività caricate", festivita.len());
        } else {
            println!("⚠️ API Nager.Date offline (test skippato)");
        }
    }

    #[tokio::test]
    async fn test_sync_with_fallback() {
        let service = FestivitaService::new();

        // Sync (prova API, fallback su seed)
        let festivita = service.sync_festivita(2026).await;

        assert!(!festivita.is_empty());
        println!("✅ Sync festivita: {} caricate", festivita.len());
    }
}
