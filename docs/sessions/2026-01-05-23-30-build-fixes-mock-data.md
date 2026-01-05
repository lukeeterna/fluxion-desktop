# Sessione: Build Fixes + Mock Data + Pianificazione Fase 7

**Data**: 2026-01-05T23:30:00
**Fase**: 6 (completata) → preparazione Fase 7
**Agente**: devops, react-frontend

## Modifiche

### Build Fixes
- `vite.config.ts`: Aggiunto chunk splitting per ridurre bundle size
  - vendor-react: 65KB
  - vendor-tanstack: 48KB
  - vendor-ui: 115KB
  - vendor-utils: 89KB
  - vendor-pdf: 607KB (jspdf + html2canvas)
  - index: 812KB (da 1.7MB originale)
- `tauri.conf.json`: Cambiato identifier da `com.fluxion.app` a `com.fluxion.desktop`
- `fatture.rs`: Aggiunto `#[allow(dead_code)]` su struct inutilizzate

### WhatsApp QR Kit Fixes
- `WhatsAppQRKit.tsx`: Fix ESLint errors (window.alert, window.URL)
- Aggiunto import `@tauri-apps/plugin-opener` per aprire URL in Tauri
- Migliorato error handling con fallback per clipboard e PDF export

### Mock Data
- `scripts/mock_data.sql`: Script SQL con dati demo
  - 10 clienti
  - 8 servizi
  - 4 operatori
  - 3 pacchetti
  - 15 appuntamenti
  - 1 configurazione fatturazione
- `data/faq_salone.md`: FAQ placeholder per futuro RAG system

### Pianificazione Fase 7
- Discusso architettura WhatsApp locale con whatsapp-web.js (ZERO API costs)
- Pianificato RAG semplice con FAQ per categoria PMI + Groq
- Documentato workflow Waitlist con priorità VIP
- Integrazione Voice Agent con stesso RAG

## Test Pendenti (iMac)
1. Pull da GitHub: `git pull`
2. Import mock data: `sqlite3 ~/Library/Application\ Support/com.fluxion.desktop/fluxion.db < scripts/mock_data.sql`
3. Test pagina Fatture (prima configurare Impostazioni Fatturazione)
4. Test WhatsApp QR Kit (Test Link, Copia Link, PDF export)

## Commits
- `fix: chunk splitting + suppress unused struct warnings` (7111112)
- `fix: change bundle identifier to com.fluxion.desktop` (5939da1)
- `fix: WhatsApp QR Kit + add mock data SQL` (9194201)
- `feat: add FAQ data file for RAG system` (c782ddc)

## Prossima Sessione
- Test completo su iMac
- Semplificare QR Kit a singolo QR "Contattaci"
- Iniziare Fase 7: whatsapp-web.js + RAG
