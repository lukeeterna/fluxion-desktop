// ═══════════════════════════════════════════════════════════════
// FAQ TEMPLATE SYSTEM - RAG Locale Leggero
// Sostituisce {{variabile}} con valori dal DB
// ═══════════════════════════════════════════════════════════════

use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use std::collections::HashMap;
use tauri::State;

#[derive(Debug, Serialize, Deserialize, Clone, sqlx::FromRow)]
pub struct FaqSetting {
    pub chiave: String,
    pub valore: String,
    pub categoria: Option<String>,
    pub descrizione: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct FaqSearchResult {
    pub domanda: String,
    pub risposta: String,
    pub score: f32,
    pub categoria: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ClienteIdentificato {
    pub id: String,
    pub nome: String,
    pub cognome: String,
    pub soprannome: Option<String>,
    pub telefono: String,
    pub match_type: String, // "telefono", "nome", "soprannome", "data_nascita"
    pub ambiguo: bool,
    pub candidati: Vec<ClienteMinimo>,
}

#[derive(Debug, Serialize, Deserialize, Clone, sqlx::FromRow)]
pub struct ClienteMinimo {
    pub id: String,
    pub nome: String,
    pub cognome: String,
    pub soprannome: Option<String>,
    pub telefono: String,
}

// ─────────────────────────────────────────────────────────────────
// TAURI COMMANDS
// ─────────────────────────────────────────────────────────────────

/// Ottieni tutte le impostazioni FAQ
#[tauri::command]
pub async fn get_faq_settings(
    pool: State<'_, SqlitePool>,
    categoria: Option<String>,
) -> Result<Vec<FaqSetting>, String> {
    // Runtime query for CI compatibility
    let result = if let Some(cat) = categoria {
        sqlx::query_as::<_, FaqSetting>(
            r#"SELECT chiave, valore, categoria, descrizione
               FROM faq_settings
               WHERE categoria = ?
               ORDER BY chiave"#,
        )
        .bind(cat)
        .fetch_all(pool.inner())
        .await
    } else {
        sqlx::query_as::<_, FaqSetting>(
            r#"SELECT chiave, valore, categoria, descrizione
               FROM faq_settings
               ORDER BY categoria, chiave"#,
        )
        .fetch_all(pool.inner())
        .await
    };

    result.map_err(|e| format!("Errore lettura FAQ settings: {}", e))
}

/// Aggiorna una singola impostazione FAQ
#[tauri::command]
pub async fn update_faq_setting(
    pool: State<'_, SqlitePool>,
    chiave: String,
    valore: String,
) -> Result<(), String> {
    // Runtime query for CI compatibility
    sqlx::query(
        r#"UPDATE faq_settings
           SET valore = ?, updated_at = datetime('now')
           WHERE chiave = ?"#,
    )
    .bind(&valore)
    .bind(&chiave)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Errore aggiornamento FAQ setting: {}", e))?;

    Ok(())
}

/// Renderizza il file FAQ sostituendo {{variabili}} con valori DB
#[tauri::command]
pub async fn render_faq_template(
    pool: State<'_, SqlitePool>,
) -> Result<String, String> {
    // 1. Leggi tutte le impostazioni (runtime query for CI compatibility)
    let settings: Vec<FaqSetting> = sqlx::query_as::<_, FaqSetting>(
        "SELECT chiave, valore, categoria, descrizione FROM faq_settings",
    )
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Errore lettura settings: {}", e))?;

    // 2. Crea mappa chiave -> valore
    let mut vars: HashMap<String, String> = HashMap::new();
    for s in settings {
        vars.insert(s.chiave, s.valore);
    }

    // 3. Leggi template FAQ
    let template = include_str!("../../../data/faq_salone_variabili.md");

    // 4. Sostituisci {{variabile}} con valori
    let mut rendered = template.to_string();
    for (key, value) in &vars {
        let placeholder = format!("{{{{{}}}}}", key);
        rendered = rendered.replace(&placeholder, value);
    }

    Ok(rendered)
}

/// Cerca nelle FAQ (RAG locale leggero - keyword matching)
#[tauri::command]
pub async fn search_faq_local(
    pool: State<'_, SqlitePool>,
    query: String,
) -> Result<Vec<FaqSearchResult>, String> {
    // 1. Renderizza FAQ con variabili
    let rendered = render_faq_template_internal(&pool).await?;

    // 2. Estrai Q&A dal markdown
    let qas = extract_qa_pairs(&rendered);

    // 3. Cerca per keyword matching
    let query_lower = query.to_lowercase();
    let query_words: Vec<&str> = query_lower.split_whitespace().collect();

    let mut results: Vec<FaqSearchResult> = qas
        .into_iter()
        .filter_map(|(domanda, risposta, categoria)| {
            let domanda_lower = domanda.to_lowercase();
            let risposta_lower = risposta.to_lowercase();

            // Calcola score basato su keyword match
            let mut score: f32 = 0.0;
            for word in &query_words {
                if word.len() < 3 {
                    continue; // Ignora parole troppo corte
                }
                if domanda_lower.contains(word) {
                    score += 2.0; // Match in domanda vale di più
                }
                if risposta_lower.contains(word) {
                    score += 1.0;
                }
            }

            if score > 0.0 {
                // Normalizza score (0-1)
                let normalized = (score / (query_words.len() as f32 * 3.0)).min(1.0);
                Some(FaqSearchResult {
                    domanda,
                    risposta,
                    score: normalized,
                    categoria,
                })
            } else {
                None
            }
        })
        .collect();

    // 4. Ordina per score decrescente
    results.sort_by(|a, b| b.score.partial_cmp(&a.score).unwrap());

    // 5. Limita a top 5
    results.truncate(5);

    Ok(results)
}

/// Identifica cliente da WhatsApp (nome → soprannome → data_nascita)
#[tauri::command]
pub async fn identifica_cliente_whatsapp(
    pool: State<'_, SqlitePool>,
    telefono: Option<String>,
    nome: Option<String>,
    soprannome: Option<String>,
    data_nascita: Option<String>,
) -> Result<ClienteIdentificato, String> {
    // 1. Prima prova per telefono (più affidabile)
    if let Some(tel) = &telefono {
        let tel_clean = tel.replace("+", "").replace(" ", "");
        if let Some(cliente) = find_by_telefono(&pool, &tel_clean).await? {
            return Ok(ClienteIdentificato {
                id: cliente.id.clone(),
                nome: cliente.nome.clone(),
                cognome: cliente.cognome.clone(),
                soprannome: cliente.soprannome.clone(),
                telefono: cliente.telefono.clone(),
                match_type: "telefono".to_string(),
                ambiguo: false,
                candidati: vec![],
            });
        }
    }

    // 2. Prova per nome
    if let Some(n) = &nome {
        let candidati = find_by_nome(&pool, n).await?;
        if candidati.len() == 1 {
            let c = &candidati[0];
            return Ok(ClienteIdentificato {
                id: c.id.clone(),
                nome: c.nome.clone(),
                cognome: c.cognome.clone(),
                soprannome: c.soprannome.clone(),
                telefono: c.telefono.clone(),
                match_type: "nome".to_string(),
                ambiguo: false,
                candidati: vec![],
            });
        } else if !candidati.is_empty() {
            // Ambiguo - prova con soprannome
            if let Some(sopran) = &soprannome {
                let filtered: Vec<_> = candidati
                    .iter()
                    .filter(|c| {
                        c.soprannome
                            .as_ref()
                            .map(|s| s.to_lowercase().contains(&sopran.to_lowercase()))
                            .unwrap_or(false)
                    })
                    .cloned()
                    .collect();

                if filtered.len() == 1 {
                    let c = &filtered[0];
                    return Ok(ClienteIdentificato {
                        id: c.id.clone(),
                        nome: c.nome.clone(),
                        cognome: c.cognome.clone(),
                        soprannome: c.soprannome.clone(),
                        telefono: c.telefono.clone(),
                        match_type: "soprannome".to_string(),
                        ambiguo: false,
                        candidati: vec![],
                    });
                }
            }

            // Prova con data nascita
            if let Some(dn) = &data_nascita {
                let filtered: Vec<_> = candidati
                    .iter()
                    .filter(|c| {
                        sqlx::query_scalar!(
                            "SELECT data_nascita FROM clienti WHERE id = ?",
                            c.id
                        )
                        .fetch_one(pool.inner())
                        .map(|d: Option<String>| d.as_ref() == Some(dn))
                        .unwrap_or(Ok(false))
                        .unwrap_or(false)
                    })
                    .cloned()
                    .collect();

                if filtered.len() == 1 {
                    let c = &filtered[0];
                    return Ok(ClienteIdentificato {
                        id: c.id.clone(),
                        nome: c.nome.clone(),
                        cognome: c.cognome.clone(),
                        soprannome: c.soprannome.clone(),
                        telefono: c.telefono.clone(),
                        match_type: "data_nascita".to_string(),
                        ambiguo: false,
                        candidati: vec![],
                    });
                }
            }

            // Ancora ambiguo
            return Ok(ClienteIdentificato {
                id: String::new(),
                nome: String::new(),
                cognome: String::new(),
                soprannome: None,
                telefono: String::new(),
                match_type: "ambiguo".to_string(),
                ambiguo: true,
                candidati,
            });
        }
    }

    // 3. Non trovato
    Err("Cliente non trovato. Fornisci più informazioni.".to_string())
}

// ─────────────────────────────────────────────────────────────────
// HELPER FUNCTIONS
// ─────────────────────────────────────────────────────────────────

async fn render_faq_template_internal(pool: &SqlitePool) -> Result<String, String> {
    // Runtime query for CI compatibility
    let settings: Vec<FaqSetting> = sqlx::query_as::<_, FaqSetting>(
        "SELECT chiave, valore, categoria, descrizione FROM faq_settings",
    )
    .fetch_all(pool)
    .await
    .map_err(|e| format!("Errore: {}", e))?;

    let mut vars: HashMap<String, String> = HashMap::new();
    for s in settings {
        vars.insert(s.chiave, s.valore);
    }

    let template = include_str!("../../../data/faq_salone_variabili.md");
    let mut rendered = template.to_string();
    for (key, value) in &vars {
        let placeholder = format!("{{{{{}}}}}", key);
        rendered = rendered.replace(&placeholder, value);
    }

    Ok(rendered)
}

fn extract_qa_pairs(markdown: &str) -> Vec<(String, String, Option<String>)> {
    let mut results = Vec::new();
    let mut current_section: Option<String> = None;
    let mut current_question: Option<String> = None;
    let mut current_answer = String::new();

    for line in markdown.lines() {
        let trimmed = line.trim();

        // Sezione (## Titolo)
        if trimmed.starts_with("## ") {
            // Salva Q&A precedente
            if let Some(q) = current_question.take() {
                if !current_answer.trim().is_empty() {
                    results.push((q, current_answer.trim().to_string(), current_section.clone()));
                }
            }
            current_answer.clear();
            current_section = Some(trimmed[3..].to_string());
            continue;
        }

        // Domanda (### Titolo)
        if trimmed.starts_with("### ") {
            // Salva Q&A precedente
            if let Some(q) = current_question.take() {
                if !current_answer.trim().is_empty() {
                    results.push((q, current_answer.trim().to_string(), current_section.clone()));
                }
            }
            current_answer.clear();
            current_question = Some(trimmed[4..].to_string());
            continue;
        }

        // Contenuto (lista o testo)
        if current_question.is_some() && !trimmed.is_empty() {
            if trimmed.starts_with("- ") {
                current_answer.push_str(&trimmed[2..]);
                current_answer.push('\n');
            } else {
                current_answer.push_str(trimmed);
                current_answer.push('\n');
            }
        }
    }

    // Ultimo Q&A
    if let Some(q) = current_question {
        if !current_answer.trim().is_empty() {
            results.push((q, current_answer.trim().to_string(), current_section));
        }
    }

    results
}

async fn find_by_telefono(pool: &SqlitePool, telefono: &str) -> Result<Option<ClienteMinimo>, String> {
    // Runtime query for CI compatibility
    let like_pattern = format!("%{}", telefono);
    let results = sqlx::query_as::<_, ClienteMinimo>(
        r#"SELECT id, nome, cognome, soprannome, telefono
           FROM clienti
           WHERE deleted_at IS NULL
           AND (
               REPLACE(REPLACE(telefono, '+', ''), ' ', '') = ?
               OR REPLACE(REPLACE(telefono, '+', ''), ' ', '') LIKE ?
           )
           LIMIT 1"#,
    )
    .bind(telefono)
    .bind(&like_pattern)
    .fetch_optional(pool)
    .await
    .map_err(|e| format!("Errore ricerca telefono: {}", e))?;

    Ok(results)
}

async fn find_by_nome(pool: &SqlitePool, nome: &str) -> Result<Vec<ClienteMinimo>, String> {
    let nome_pattern = format!("%{}%", nome.to_lowercase());

    // Runtime query for CI compatibility
    sqlx::query_as::<_, ClienteMinimo>(
        r#"SELECT id, nome, cognome, soprannome, telefono
           FROM clienti
           WHERE deleted_at IS NULL
           AND (
               LOWER(nome) LIKE ?
               OR LOWER(cognome) LIKE ?
               OR LOWER(soprannome) LIKE ?
           )
           LIMIT 10"#,
    )
    .bind(&nome_pattern)
    .bind(&nome_pattern)
    .bind(&nome_pattern)
    .fetch_all(pool)
    .await
    .map_err(|e| format!("Errore ricerca nome: {}", e))
}
