VALIDAZIONE CLAUDE AI — R-01-bis GATE (FLUXION license interop)

Sei il giudice tecnico. Valida l'output del GATE di sicurezza eseguito dal CTO
sul blocker revenue di FLUXION (attivazione licenze Ed25519 post-Stripe).
Rispondi CONFERMA / CONFUTA per ciascun punto + motivazione. Non assumere nulla
oltre i fatti riportati (tutti con file:riga reale del codebase).

═══════════════════════════════════════════════════════════════════
CONTESTO
═══════════════════════════════════════════════════════════════════
- Worker CF `fluxion-proxy` (in prod, INTOCCABILE) firma una licenza V1: payload
  JSON 6 campi {kid, license_id, customer_email, product, session_id,
  issued_at(int epoch)}, firma Ed25519 chiave v1. NESSUN hardware fingerprint
  nella firma.
- Client Tauri ha 2 path di attivazione:
  1. EMAIL (primario, ciò che l'email dice al cliente): FE activateByEmail() →
     POST /api/v1/activate-by-email → Worker lookup KV → ritorna {activated,
     tier, features}.
  2. PASTE MANUALE (fallback): invoke('activate_license_ed25519') → chiave
     LEGACY, struct 11 campi, hardware-lock rigido → incompatibile con V1.
- La UI legge lo stato licenza via command Rust get_license_status_ed25519 (legge
  tabella SQLite `license_cache`), NON da localStorage.
- Esiste recovery HMAC: GET /api/v1/license/:email?token={hmac}, token =
  HMAC-SHA256(LICENSE_RECOVERY_SECRET, email), constant-time compare. Ritorna
  {license_id, tier, license_payload, license_signature, issued_at}.

═══════════════════════════════════════════════════════════════════
OUTPUT GATE (3 grep di sicurezza, file:riga reali)
═══════════════════════════════════════════════════════════════════

GATE #1 — WRITER di `license_cache`
- save_license() = src-tauri/src/commands/license_ed25519.rs:362-460 (id=1, ON
  CONFLICT UPDATE → re-bind automatico su ri-attivazione).
- Oggi popolata SOLO da activate_license_ed25519 (path paste, chiave legacy).
- Path EMAIL (src/lib/activate-by-email.ts) scriveva SOLO localStorage, mai un
  command Rust → mai save_license → SPLIT-BRAIN: cliente vede "attivato" ma UI
  (che legge license_cache) resta trial → feature bloccate → refund.
- FIX applicato (commit d46e32f): email path ora chiama un nuovo command Rust
  activate_license_v1 → verifica firma V1 + deriva FluxionLicense + save_license.

GATE #2 — PROTEZIONE esposizione payload+firma  [DIVERGENZA TROVATA]
- Recovery HMAC = fluxion-proxy/src/routes/license-recovery.ts:42-46,107-110
  (HMAC-SHA256 + constant-time compare). Protezione forte contro enumeration.
- MA il fix d46e32f ha esposto license_payload+license_signature anche su
  fluxion-proxy/src/routes/activate-by-email.ts:124-159, endpoint che NON ha
  HMAC: controlla solo email.includes('@') (riga :67).
- CONSEGUENZA: chiunque conosca/indovini l'email di un cliente può estrarre la
  sua licenza firmata da un endpoint non protetto (vettore enumeration /
  esfiltrazione / replay).
- DIRETTIVA CTO (Luke): l'esposizione di payload+firma DEVE usare la STESSA HMAC
  del recovery URL, non un endpoint meno protetto. → il fix d46e32f VIOLA questa
  direttiva.

GATE #3 — TIPO di `issued_at`
- fluxion-proxy/src/lib/ed25519-sign.ts:132 → issued_at: number // unix epoch
  seconds (INT confermato). Canonical key-order righe 157,168.
- Rust WorkerLicensePayloadV1.issued_at: i64 = MATCH. La firma è verificata sui
  byte raw del payload string (key-order preservato), int intatto. Conversione a
  RFC3339 string solo per storage locale FluxionLicense.issued_at: String (no
  migration, no view, no UNIQUE toccati).

═══════════════════════════════════════════════════════════════════
CORRECTIVE PROPOSTO DAL CTO (da validare)
═══════════════════════════════════════════════════════════════════
Revertare l'esposizione su activate-by-email.ts e far chiamare al client il
recovery HMAC-protetto (che già ritorna payload+firma) → activate_license_v1.
Rispetta GATE #2, Worker resta minimale, split-brain comunque chiuso.
NODO APERTO: il client deve ottenere il token HMAC = HMAC-SHA256(SECRET, email).
Opzioni non ancora decise: (a) token/link nell'email Resend post-acquisto;
(b) meccanismo client-side (ma il client NON deve avere LICENSE_RECOVERY_SECRET).

═══════════════════════════════════════════════════════════════════
DOMANDE
═══════════════════════════════════════════════════════════════════
1. GATE #1: lo split-brain è descritto correttamente, o esiste un meccanismo non
   citato per cui il path email popolava già license_cache?
2. GATE #2: confermi che esporre payload+firma su activate-by-email (solo email,
   no HMAC) è un rischio reale che giustifica il revert? La firma Ed25519 protegge
   l'integrità ma NON impedisce a un terzo di OTTENERE la licenza di un altro:
   è corretto, o l'integrità basta perché senza fingerprint nella firma la
   licenza rubata è comunque inutilizzabile da terzi?
3. CORRECTIVE: il client B2B desktop non deve possedere LICENSE_RECOVERY_SECRET.
   Qual è il modo corretto e zero-cost di consegnargli il token HMAC senza
   esporre il secret né riaprire il vettore enumeration? (es. link firmato
   nell'email Resend vs. altro)
4. GATE #3: tenere issued_at int→string lato Rust è la scelta che rompe meno, o
   conviene unificare a int anche in FluxionLicense?

Rispondi punto per punto. Se il corrective ha un buco, indicalo.
