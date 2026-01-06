// FLUXION - RAG (Retrieval Augmented Generation) with Groq
// Simple FAQ-based RAG for WhatsApp and Voice Agent

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;
use tauri::{AppHandle, Manager};

/// Single FAQ entry
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FaqEntry {
    pub section: String,
    pub question: String,
    pub answer: String,
}

/// RAG response from Groq
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RagResponse {
    pub answer: String,
    pub sources: Vec<FaqEntry>,
    pub confidence: f32,
    pub model: String,
}

/// Groq API request
#[derive(Debug, Serialize)]
struct GroqRequest {
    model: String,
    messages: Vec<GroqMessage>,
    temperature: f32,
    max_tokens: u32,
}

#[derive(Debug, Serialize)]
struct GroqMessage {
    role: String,
    content: String,
}

/// Groq API response
#[derive(Debug, Deserialize)]
struct GroqApiResponse {
    choices: Vec<GroqChoice>,
    model: String,
}

#[derive(Debug, Deserialize)]
struct GroqChoice {
    message: GroqMessageResponse,
}

#[derive(Debug, Deserialize)]
struct GroqMessageResponse {
    content: String,
}

/// Get data directory path
fn get_data_dir(app: &AppHandle) -> PathBuf {
    let resource_dir = app.path().resource_dir().unwrap_or_default();
    resource_dir.join("data")
}

/// Parse FAQ markdown file into entries
fn parse_faq_markdown(content: &str) -> Vec<FaqEntry> {
    let mut entries = Vec::new();
    let mut current_section = String::new();
    let mut current_question = String::new();
    let mut current_answer = Vec::new();

    for line in content.lines() {
        let trimmed = line.trim();

        if trimmed.starts_with("## ") {
            // Save previous entry if exists
            if !current_question.is_empty() {
                entries.push(FaqEntry {
                    section: current_section.clone(),
                    question: current_question.clone(),
                    answer: current_answer.join("\n").trim().to_string(),
                });
                current_answer.clear();
            }
            current_section = trimmed[3..].to_string();
            current_question.clear();
        } else if trimmed.starts_with("### ") {
            // Save previous entry if exists
            if !current_question.is_empty() {
                entries.push(FaqEntry {
                    section: current_section.clone(),
                    question: current_question.clone(),
                    answer: current_answer.join("\n").trim().to_string(),
                });
                current_answer.clear();
            }
            current_question = trimmed[4..].to_string();
        } else if trimmed.starts_with("- ") && current_question.is_empty() {
            // Simple list format (like faq_salone.md)
            let parts: Vec<&str> = trimmed[2..].splitn(2, ':').collect();
            if parts.len() == 2 {
                entries.push(FaqEntry {
                    section: current_section.clone(),
                    question: parts[0].trim().to_string(),
                    answer: parts[1].trim().to_string(),
                });
            }
        } else if !current_question.is_empty() && !trimmed.is_empty() {
            current_answer.push(trimmed.to_string());
        }
    }

    // Save last entry
    if !current_question.is_empty() {
        entries.push(FaqEntry {
            section: current_section,
            question: current_question,
            answer: current_answer.join("\n").trim().to_string(),
        });
    }

    entries
}

/// Simple keyword-based retrieval (TF-IDF lite)
fn find_relevant_faqs(query: &str, faqs: &[FaqEntry], top_k: usize) -> Vec<(FaqEntry, f32)> {
    let query_lower = query.to_lowercase();
    let query_words: Vec<&str> = query_lower
        .split_whitespace()
        .filter(|w| w.len() > 2) // Skip short words
        .collect();

    if query_words.is_empty() {
        return vec![];
    }

    let mut scores: Vec<(FaqEntry, f32)> = faqs
        .iter()
        .map(|faq| {
            let text = format!(
                "{} {} {}",
                faq.section.to_lowercase(),
                faq.question.to_lowercase(),
                faq.answer.to_lowercase()
            );

            let mut score: f32 = 0.0;
            for word in &query_words {
                if text.contains(word) {
                    score += 1.0;
                    // Bonus for question match
                    if faq.question.to_lowercase().contains(word) {
                        score += 0.5;
                    }
                }
            }
            // Normalize by query length
            score /= query_words.len() as f32;

            (faq.clone(), score)
        })
        .filter(|(_, score)| *score > 0.0)
        .collect();

    scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
    scores.truncate(top_k);
    scores
}

/// Call Groq API for LLM completion
async fn call_groq(
    api_key: &str,
    system_prompt: &str,
    user_message: &str,
    model: &str,
) -> Result<(String, String), String> {
    let client = reqwest::Client::new();

    let request = GroqRequest {
        model: model.to_string(),
        messages: vec![
            GroqMessage {
                role: "system".to_string(),
                content: system_prompt.to_string(),
            },
            GroqMessage {
                role: "user".to_string(),
                content: user_message.to_string(),
            },
        ],
        temperature: 0.3,
        max_tokens: 500,
    };

    let response = client
        .post("https://api.groq.com/openai/v1/chat/completions")
        .header("Authorization", format!("Bearer {}", api_key))
        .header("Content-Type", "application/json")
        .json(&request)
        .send()
        .await
        .map_err(|e| format!("HTTP request failed: {}", e))?;

    if !response.status().is_success() {
        let status = response.status();
        let error_text = response.text().await.unwrap_or_default();
        return Err(format!("Groq API error {}: {}", status, error_text));
    }

    let api_response: GroqApiResponse = response
        .json()
        .await
        .map_err(|e| format!("Failed to parse Groq response: {}", e))?;

    let content = api_response
        .choices
        .first()
        .map(|c| c.message.content.clone())
        .unwrap_or_default();

    Ok((content, api_response.model))
}

// ============================================================================
// TAURI COMMANDS
// ============================================================================

/// Load all FAQs from a category file
#[tauri::command]
pub fn load_faqs(app: AppHandle, category: String) -> Result<Vec<FaqEntry>, String> {
    let filename = format!("faq_{}.md", category.to_lowercase());

    // Try resource dir first, then app data dir
    let resource_path = get_data_dir(&app).join(&filename);
    let app_data_path = app
        .path()
        .app_data_dir()
        .map_err(|e| e.to_string())?
        .join("data")
        .join(&filename);

    // Also try project root /data/ (for development)
    let dev_path = PathBuf::from("data").join(&filename);

    let content = fs::read_to_string(&resource_path)
        .or_else(|_| fs::read_to_string(&app_data_path))
        .or_else(|_| fs::read_to_string(&dev_path))
        .map_err(|e| format!("FAQ file not found ({}): {}", filename, e))?;

    Ok(parse_faq_markdown(&content))
}

/// List available FAQ categories
#[tauri::command]
pub fn list_faq_categories(app: AppHandle) -> Result<Vec<String>, String> {
    let mut categories = Vec::new();

    // Check resource dir
    let resource_dir = get_data_dir(&app);
    if let Ok(entries) = fs::read_dir(&resource_dir) {
        for entry in entries.flatten() {
            if let Some(name) = entry.file_name().to_str() {
                if name.starts_with("faq_") && name.ends_with(".md") {
                    let category = name
                        .strip_prefix("faq_")
                        .unwrap()
                        .strip_suffix(".md")
                        .unwrap();
                    categories.push(category.to_string());
                }
            }
        }
    }

    // Also check dev path
    if let Ok(entries) = fs::read_dir("data") {
        for entry in entries.flatten() {
            if let Some(name) = entry.file_name().to_str() {
                if name.starts_with("faq_") && name.ends_with(".md") {
                    let category = name
                        .strip_prefix("faq_")
                        .unwrap()
                        .strip_suffix(".md")
                        .unwrap()
                        .to_string();
                    if !categories.contains(&category) {
                        categories.push(category);
                    }
                }
            }
        }
    }

    Ok(categories)
}

/// Main RAG command: answer a question using FAQ knowledge + Groq LLM
#[tauri::command]
pub async fn rag_answer(
    app: AppHandle,
    question: String,
    category: String,
    business_context: Option<HashMap<String, String>>,
) -> Result<RagResponse, String> {
    // 1. Load FAQs
    let faqs = load_faqs(app.clone(), category.clone())?;

    if faqs.is_empty() {
        return Err(format!("No FAQs found for category: {}", category));
    }

    // 2. Find relevant FAQs (retrieval)
    let relevant = find_relevant_faqs(&question, &faqs, 5);

    // 3. Build context for LLM
    let mut context = String::new();
    for (faq, score) in &relevant {
        context.push_str(&format!(
            "Q: {}\nA: {}\n(relevance: {:.2})\n\n",
            faq.question, faq.answer, score
        ));
    }

    // 4. Build business context string
    let business_info = business_context
        .as_ref()
        .map(|ctx| {
            ctx.iter()
                .map(|(k, v)| format!("{}: {}", k, v))
                .collect::<Vec<_>>()
                .join("\n")
        })
        .unwrap_or_default();

    // 5. Build system prompt
    let system_prompt = format!(
        r#"Sei l'assistente virtuale di un'attività italiana. Rispondi in modo cordiale, professionale e conciso.

INFORMAZIONI ATTIVITÀ:
{}

KNOWLEDGE BASE (FAQ):
{}

REGOLE:
- Rispondi SOLO basandoti sulle FAQ fornite
- Se la domanda non è coperta dalle FAQ, di' "Mi dispiace, non ho informazioni su questo. Ti consiglio di contattarci direttamente."
- Usa un tono amichevole ma professionale
- Risposte brevi (max 2-3 frasi)
- Puoi usare 1-2 emoji se appropriato
- Se ci sono variabili tipo {{TELEFONO}}, usa i valori dalle INFORMAZIONI ATTIVITÀ"#,
        business_info, context
    );

    // 6. Get API key
    let api_key = std::env::var("GROQ_API_KEY")
        .map_err(|_| "GROQ_API_KEY non trovato. Assicurati che il file .env sia nella directory del progetto e contenga GROQ_API_KEY=...")?;

    // 7. Call Groq
    let (answer, model) = call_groq(
        &api_key,
        &system_prompt,
        &question,
        "llama-3.1-8b-instant", // Fast and cheap
    )
    .await?;

    // 8. Calculate confidence based on retrieval scores
    let confidence = if relevant.is_empty() {
        0.0
    } else {
        relevant.iter().map(|(_, s)| s).sum::<f32>() / relevant.len() as f32
    };

    Ok(RagResponse {
        answer,
        sources: relevant.into_iter().map(|(faq, _)| faq).collect(),
        confidence,
        model,
    })
}

/// Quick answer without full RAG (just retrieval, no LLM)
#[tauri::command]
pub fn quick_faq_search(
    app: AppHandle,
    question: String,
    category: String,
) -> Result<Vec<FaqEntry>, String> {
    let faqs = load_faqs(app, category)?;
    let results = find_relevant_faqs(&question, &faqs, 3);
    Ok(results.into_iter().map(|(faq, _)| faq).collect())
}

/// Test Groq API connection
#[tauri::command]
pub async fn test_groq_connection() -> Result<String, String> {
    let api_key = std::env::var("GROQ_API_KEY")
        .map_err(|_| "GROQ_API_KEY non trovato. Crea un file .env nella root del progetto con: GROQ_API_KEY=gsk_...")?;

    let (response, model) = call_groq(
        &api_key,
        "You are a helpful assistant.",
        "Say 'Ciao!' in Italian",
        "llama-3.1-8b-instant",
    )
    .await?;

    Ok(format!("Groq OK! Model: {} | Response: {}", model, response))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_faq_simple_format() {
        let content = r#"# FAQ Test

## Orari
- Apertura: 9:00 - 18:00
- Chiusura: Domenica

## Servizi
- Taglio: €20
"#;
        let faqs = parse_faq_markdown(content);
        assert_eq!(faqs.len(), 3);
        assert_eq!(faqs[0].section, "Orari");
        assert_eq!(faqs[0].question, "Apertura");
        assert_eq!(faqs[0].answer, "9:00 - 18:00");
    }

    #[test]
    fn test_parse_faq_qa_format() {
        let content = r#"# FAQ Test

## Informazioni

### Dove siete?
Siamo in Via Roma 123.

### Orari apertura?
Lun-Ven 9-18.
"#;
        let faqs = parse_faq_markdown(content);
        assert_eq!(faqs.len(), 2);
        assert_eq!(faqs[0].question, "Dove siete?");
        assert!(faqs[0].answer.contains("Via Roma"));
    }

    #[test]
    fn test_find_relevant_faqs() {
        let faqs = vec![
            FaqEntry {
                section: "Orari".into(),
                question: "Quando siete aperti?".into(),
                answer: "Lunedì-Venerdì 9-18".into(),
            },
            FaqEntry {
                section: "Prezzi".into(),
                question: "Quanto costa taglio?".into(),
                answer: "20 euro".into(),
            },
            FaqEntry {
                section: "Servizi".into(),
                question: "Fate colore?".into(),
                answer: "Sì, colore e meches".into(),
            },
        ];

        let results = find_relevant_faqs("orari apertura", &faqs, 2);
        assert!(!results.is_empty());
        assert!(results[0].0.question.contains("aperti"));
    }
}
