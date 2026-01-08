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

#[derive(Debug, Serialize, Deserialize, Clone)]
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
    pub data_nascita: Option<String>, // Per disambiguazione cliente
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
pub async fn render_faq_template(pool: State<'_, SqlitePool>) -> Result<String, String> {
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

            // Prova con data nascita (usa campo già caricato da find_by_nome)
            if let Some(dn) = &data_nascita {
                let filtered: Vec<_> = candidati
                    .iter()
                    .filter(|c| c.data_nascita.as_ref() == Some(dn))
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
                    results.push((
                        q,
                        current_answer.trim().to_string(),
                        current_section.clone(),
                    ));
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
                    results.push((
                        q,
                        current_answer.trim().to_string(),
                        current_section.clone(),
                    ));
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

async fn find_by_telefono(
    pool: &SqlitePool,
    telefono: &str,
) -> Result<Option<ClienteMinimo>, String> {
    // Runtime query for CI compatibility
    let like_pattern = format!("%{}", telefono);
    let results = sqlx::query_as::<_, ClienteMinimo>(
        r#"SELECT id, nome, cognome, soprannome, telefono, data_nascita
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

    // Runtime query for CI compatibility (include data_nascita per disambiguazione)
    sqlx::query_as::<_, ClienteMinimo>(
        r#"SELECT id, nome, cognome, soprannome, telefono, data_nascita
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

// ═══════════════════════════════════════════════════════════════
// RAG IBRIDO: Locale (90%) + Groq Fallback (10%)
// ═══════════════════════════════════════════════════════════════

const CONFIDENCE_THRESHOLD: f32 = 0.50; // Soglia per risposta locale

#[derive(Debug, Serialize, Deserialize)]
pub struct RagHybridResponse {
    pub risposta: String,
    pub fonte: String, // "locale" | "llm" | "operatore"
    pub confidence: f32,
    pub faq_match: Option<FaqSearchResult>,
    pub richiede_operatore: bool,
}

/// RAG Ibrido: prima cerca locale, poi fallback LLM se necessario
/// - confidence >= 50%: risposta locale (GRATUITA)
/// - confidence < 50% + API key: usa Groq
/// - confidence < 50% senza API key: passa a operatore
#[tauri::command]
pub async fn rag_hybrid_answer(
    pool: State<'_, SqlitePool>,
    domanda: String,
) -> Result<RagHybridResponse, String> {
    // 1. Cerca localmente nelle FAQ
    let results = search_faq_local_internal(&pool, &domanda).await?;

    // 2. Se abbiamo match con buona confidence → risposta locale
    if let Some(best) = results.first() {
        if best.score >= CONFIDENCE_THRESHOLD {
            return Ok(RagHybridResponse {
                risposta: best.risposta.clone(),
                fonte: "locale".to_string(),
                confidence: best.score,
                faq_match: Some(best.clone()),
                richiede_operatore: false,
            });
        }
    }

    // 3. Confidence bassa - prova Groq se disponibile
    let api_key = get_groq_key(&pool).await;

    match api_key {
        Ok(key) => {
            // Abbiamo API key, usa LLM come fallback
            let context = results
                .iter()
                .take(3)
                .map(|r| format!("Q: {}\nA: {}", r.domanda, r.risposta))
                .collect::<Vec<_>>()
                .join("\n\n");

            match call_groq_simple(&key, &domanda, &context).await {
                Ok(risposta) => Ok(RagHybridResponse {
                    risposta,
                    fonte: "llm".to_string(),
                    confidence: results.first().map(|r| r.score).unwrap_or(0.0),
                    faq_match: results.first().cloned(),
                    richiede_operatore: false,
                }),
                Err(_) => {
                    // LLM fallito, passa a operatore
                    Ok(RagHybridResponse {
                        risposta: "Mi dispiace, non sono sicuro della risposta. Un operatore ti risponderà al più presto.".to_string(),
                        fonte: "operatore".to_string(),
                        confidence: results.first().map(|r| r.score).unwrap_or(0.0),
                        faq_match: results.first().cloned(),
                        richiede_operatore: true,
                    })
                }
            }
        }
        Err(_) => {
            // Nessuna API key configurata - passa a operatore
            Ok(RagHybridResponse {
                risposta: "Non ho trovato una risposta precisa nelle FAQ. Un operatore ti risponderà al più presto.".to_string(),
                fonte: "operatore".to_string(),
                confidence: results.first().map(|r| r.score).unwrap_or(0.0),
                faq_match: results.first().cloned(),
                richiede_operatore: true,
            })
        }
    }
}

/// Versione interna di search_faq_local (senza State wrapper)
async fn search_faq_local_internal(
    pool: &SqlitePool,
    query: &str,
) -> Result<Vec<FaqSearchResult>, String> {
    let rendered = render_faq_template_internal(pool).await?;
    let qas = extract_qa_pairs(&rendered);

    let query_lower = query.to_lowercase();
    let query_words: Vec<&str> = query_lower.split_whitespace().collect();

    let mut results: Vec<FaqSearchResult> = qas
        .into_iter()
        .filter_map(|(domanda, risposta, categoria)| {
            let domanda_lower = domanda.to_lowercase();
            let risposta_lower = risposta.to_lowercase();

            let mut score: f32 = 0.0;
            for word in &query_words {
                if word.len() < 3 {
                    continue;
                }
                if domanda_lower.contains(word) {
                    score += 2.0;
                }
                if risposta_lower.contains(word) {
                    score += 1.0;
                }
            }

            if score > 0.0 {
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

    results.sort_by(|a, b| b.score.partial_cmp(&a.score).unwrap());
    results.truncate(5);

    Ok(results)
}

/// Ottieni API key Groq dal DB o .env
async fn get_groq_key(pool: &SqlitePool) -> Result<String, String> {
    // 1. Try database (fluxion_ia_key from Setup Wizard)
    let result: Option<(String,)> = sqlx::query_as(
        "SELECT valore FROM impostazioni WHERE chiave = 'fluxion_ia_key' AND valore IS NOT NULL AND valore != ''"
    )
    .fetch_optional(pool)
    .await
    .map_err(|e| e.to_string())?;

    if let Some((key,)) = result {
        if !key.is_empty() {
            return Ok(key);
        }
    }

    // 2. Fallback to .env
    std::env::var("GROQ_API_KEY").map_err(|_| "No API key".to_string())
}

/// Chiamata semplice a Groq
async fn call_groq_simple(api_key: &str, domanda: &str, context: &str) -> Result<String, String> {
    let client = reqwest::Client::new();

    let system_prompt = format!(
        r#"Sei l'assistente virtuale di un'attività italiana. Rispondi in modo cordiale e conciso (max 2 frasi).

CONTESTO FAQ:
{}

REGOLE:
- Rispondi SOLO basandoti sul contesto fornito
- Se non sai, di' "Non ho informazioni su questo"
- Tono amichevole ma professionale"#,
        context
    );

    let body = serde_json::json!({
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": domanda}
        ],
        "temperature": 0.3,
        "max_tokens": 200
    });

    let response = client
        .post("https://api.groq.com/openai/v1/chat/completions")
        .header("Authorization", format!("Bearer {}", api_key))
        .header("Content-Type", "application/json")
        .json(&body)
        .send()
        .await
        .map_err(|e| e.to_string())?;

    if !response.status().is_success() {
        return Err(format!("Groq API error: {}", response.status()));
    }

    let json: serde_json::Value = response.json().await.map_err(|e| e.to_string())?;

    json["choices"][0]["message"]["content"]
        .as_str()
        .map(|s| s.to_string())
        .ok_or_else(|| "Invalid response".to_string())
}
