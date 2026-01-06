# Sessione: RAG con Groq LLM - Implementazione Completa

**Data**: 2026-01-06T10:30:00
**Fase**: 7
**Agente**: rust-backend + react-frontend

## Obiettivo
Implementare sistema RAG (Retrieval Augmented Generation) con Groq LLM per rispondere automaticamente alle domande dei clienti basandosi sulle FAQ.

## Implementazione

### Backend Rust (rag.rs)
- **5 Tauri commands**:
  - `load_faqs`: Carica FAQ da file markdown per categoria
  - `list_faq_categories`: Lista categorie disponibili (salone, auto, wellness, medical)
  - `rag_answer`: Pipeline completa RAG (retrieval + Groq LLM)
  - `quick_faq_search`: Solo retrieval, no LLM
  - `test_groq_connection`: Test connessione API Groq

- **Groq API Integration**:
  - Model: `llama-3.1-8b-instant` (veloce, economico)
  - Temperature: 0.3 (risposte consistenti)
  - Max tokens: 500

- **FAQ Parser**:
  - Supporta formato `## Sezione` + `### Domanda` + risposta
  - Supporta formato lista `- Key: Value`
  - Estrae section, question, answer

- **Keyword Retrieval (TF-IDF lite)**:
  - Tokenizzazione lowercase
  - Skip parole < 3 caratteri
  - Bonus per match in domanda
  - Top-K risultati ordinati per score

### Frontend TypeScript

**types/rag.ts**:
- Zod schemas per FaqEntry, RagResponse
- Helper functions (buildBusinessContext, getConfidenceLabel)
- Category labels per UI

**hooks/use-rag.ts**:
- `useFaqCategories()`: Lista categorie
- `useFaqs(category)`: Carica FAQ
- `useRagAnswer()`: Mutation per domande
- `useQuickFaqSearch()`: Search veloce
- `useTestGroq()`: Test connessione
- `useRagChat()`: Hook combinato per chat UI

### Bundle Configuration
- `tauri.conf.json`: Aggiunto `"resources": ["../data/*"]`
- FAQ files inclusi nel pacchetto di installazione

## CI/CD Results

### Run #20743696869 (primo tentativo)
- ❌ Backend Tests (macos-latest): FAILED
- Errore: `error[E0716]: temporary value dropped while borrowed`
- Causa: `query.to_lowercase()` creava temporary value

### Run #20743767261 (dopo fix)
| Job | Status |
|-----|--------|
| ✅ Code Quality | success |
| ✅ Frontend Tests | success |
| ✅ Backend Tests (ubuntu) | success |
| ✅ Backend Tests (macos) | success |
| ✅ Backend Tests (windows) | success |
| ✅ Build Tauri (ubuntu) | success |
| ✅ Build Tauri (macos) | success |
| ✅ Build Tauri (windows) | success |
| ✅ Status Check | success |

**9/9 JOBS SUCCESS su tutti i 3 OS**

## Fix Applicati
1. **Rust borrow checker**: Creato binding `query_lower` prima di usare `.split_whitespace()`
2. **Bundle resources**: Aggiunto `data/*` a tauri.conf.json

## File Creati/Modificati
- `src-tauri/src/commands/rag.rs` (NEW - 350+ righe)
- `src-tauri/src/commands/mod.rs` (MOD - aggiunto modulo)
- `src-tauri/src/lib.rs` (MOD - registrati 5 commands)
- `src-tauri/tauri.conf.json` (MOD - bundle resources)
- `src/types/rag.ts` (NEW)
- `src/hooks/use-rag.ts` (NEW)

## Prossimi Passi
1. Test RAG su iMac con Groq API key
2. Creare UI per chat RAG
3. Integrare con WhatsApp automation
4. Aggiungere più FAQ per categoria
