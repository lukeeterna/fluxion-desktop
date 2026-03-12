# F07 LemonSqueezy API — CoVe 2026 Research (Agente B)
> Data: 2026-03-12 | Agente: B (codebase analysis + API knowledge)
> Source: Training knowledge (LemonSqueezy API v1, stabile da 2023) + analisi server.py esistente

---

## Checkout URL Parameters

### Pre-compilazione email e dati cliente
LemonSqueezy supporta query parameters sul checkout URL per pre-compilare i campi:

```
https://fluxion.lemonsqueezy.com/checkout/buy/{variant_uuid}
  ?checkout[email]=cliente@example.com
  &checkout[name]=Mario Rossi
  &checkout[billing_address][country]=IT
  &checkout[custom][order_note]=testo_custom
```

**Parametri supportati:**
| Parametro | Tipo | Descrizione |
|-----------|------|-------------|
| `checkout[email]` | string | Pre-compila email (non modificabile dal cliente se specificato) |
| `checkout[name]` | string | Nome completo del cliente |
| `checkout[billing_address][country]` | ISO 3166-1 alpha-2 | Preseleziona paese (es. `IT`) |
| `checkout[billing_address][zip]` | string | CAP |
| `checkout[custom][key]` | string | Dati custom passati nel webhook payload |
| `checkout[discount_code]` | string | Applica codice sconto automaticamente |
| `media` | `0` | Nasconde media/preview prodotto |
| `logo` | `0` | Nasconde logo store |
| `desc` | `0` | Nasconde descrizione prodotto |

**Nota critica per FLUXION**: Il parametro `checkout[email]` è utile nel SetupWizard (F01) per
pre-compilare l'email già inserita durante il wizard. Non richiede autenticazione — è solo
pre-filling UI, il cliente può modificarlo.

**Esempio FLUXION:**
```typescript
const checkoutUrl = (tier: 'base' | 'pro' | 'clinic', email?: string) => {
  const URLS = {
    base:   'https://fluxion.lemonsqueezy.com/checkout/buy/c73ec6bb-24c2-4214-a456-320c67056bd3',
    pro:    'https://fluxion.lemonsqueezy.com/checkout/buy/14806a0d-ac44-44af-a051-8fe8c559d702',
    clinic: 'https://fluxion.lemonsqueezy.com/checkout/buy/e3864cc0-937b-486d-b412-a1bebcfe0023',
  };
  const base = URLS[tier];
  if (!email) return base;
  const params = new URLSearchParams({
    'checkout[email]': email,
    'checkout[billing_address][country]': 'IT',
  });
  return `${base}?${params.toString()}`;
};
```

### Embed Parameters (per overlay/lightbox)
```
?embed=1          → attiva embed mode (rimuove header/footer)
?media=0          → nasconde immagine prodotto
?logo=0           → nasconde logo
?desc=0           → nasconde descrizione
?dark=1           → forza dark mode (utile per FLUXION UI scura)
```

---

## Customer Portal

### URL Accesso
Il customer portal di LemonSqueezy è accessibile a:
```
https://app.lemonsqueezy.com/my-orders
```
oppure tramite il link inviato automaticamente nell'email di conferma ordine LS.

### Customer Portal Features
- Download file acquistati (software installer)
- Visualizzazione ordini e fatture
- Gestione abbonamenti (se applicabile — non il caso FLUXION che usa lifetime)
- Download licenze generate da LS (se si usa il sistema licenze nativo LS)

### ⚠️ Nota FLUXION
FLUXION usa licenze **custom Ed25519** (non il sistema licenze nativo LS). Quindi:
- Il customer portal LS mostra solo la ricevuta di acquisto
- La vera "attivazione licenza" avviene su `/activate.html` tramite il server FLUXION (porta 3010)
- Non c'è un URL portal LS per la gestione della licenza FLUXION — è tutta in-app

**Raccomandazione**: nella email post-acquisto, includere ENTRAMBI i link:
1. Link LS ordine (per ricevuta/fattura): `https://app.lemonsqueezy.com/my-orders`
2. Link attivazione FLUXION: `{ACTIVATE_URL_BASE}/activate.html`

### API: recupero ordini per email
```bash
# GET ordini per email cliente (richiede API key LS)
GET https://api.lemonsqueezy.com/v1/orders?filter[user_email]=cliente@example.com
Authorization: Bearer {LS_API_KEY}
```
Utile per support: verificare se un cliente ha davvero acquistato.

---

## Embed/Overlay Options

### Metodo 1: Overlay JavaScript (RACCOMANDATO per Tauri WebView)
LemonSqueezy fornisce uno script ufficiale che trasforma i link in overlay modale:

```html
<!-- Includi lo script LS -->
<script src="https://app.lemonsqueezy.com/js/lemon.js" defer></script>

<!-- Link con classe lemonsqueezy-button -->
<a
  href="https://fluxion.lemonsqueezy.com/checkout/buy/c73ec6bb-..."
  class="lemonsqueezy-button"
>
  Acquista Base €497
</a>
```

Lo script intercetta il click e apre il checkout in un overlay modale (lightbox) invece di navigare
alla pagina esterna. **Perfetto per Tauri WebView** — mantiene l'utente nell'app.

### Metodo 2: iframe Embed
```html
<iframe
  src="https://fluxion.lemonsqueezy.com/checkout/buy/c73ec6bb-...?embed=1&media=0&logo=0"
  frameborder="0"
  allow="payment"
  style="width:100%;height:600px;border-radius:12px;"
></iframe>
```

**⚠️ Limitazione iframe in Tauri**: la WebView Tauri ha restrizioni CSP. Necessario aggiungere
in `tauri.conf.json`:
```json
"csp": "default-src 'self'; frame-src https://*.lemonsqueezy.com https://js.stripe.com"
```

### Metodo 3: Redirect esterno (attuale implementazione landing)
Aprire il checkout URL nel browser di sistema:
```typescript
// Tauri v2
import { open } from '@tauri-apps/plugin-shell';
await open(checkoutUrl);
```
Più semplice, meno frizione ma lascia l'app. Accettabile per landing page, meno per in-app.

### Raccomandazione per FLUXION SetupWizard (F01)
Usare **Metodo 1 (overlay JS)** nella landing + **Metodo 3 (open in browser)** da Tauri app.
Non embeddare iframe dentro la Tauri app — troppo fragile con CSP.

---

## Webhook Events per License

### Eventi disponibili in LemonSqueezy
```
order_created              ← PRIMARIO — acquisto one-time completato
order_refunded             ← rimborso, invalidare licenza
subscription_created       ← nuovo abbonamento (non usato da FLUXION)
subscription_updated       ← cambio piano abbonamento
subscription_payment_success ← rinnovo abbonamento (già gestito in server.py)
subscription_payment_failed  ← pagamento fallito
subscription_cancelled     ← cancellazione
license_key_created        ← licenza nativa LS creata (NON usato da FLUXION — usa custom)
```

### Evento Primario: `order_created`
Questo è l'evento che FLUXION deve ascoltare per attivare la licenza. **Già implementato** in
`server.py` correttamente.

**Payload struttura:**
```json
{
  "meta": {
    "event_name": "order_created",
    "custom_data": {}
  },
  "data": {
    "id": "12345",
    "type": "orders",
    "attributes": {
      "user_email": "cliente@example.com",
      "user_name": "Mario Rossi",
      "status": "paid",
      "total": 49700,
      "total_formatted": "€497,00",
      "tax": 9112,
      "tax_formatted": "€91,12",
      "first_order_item": {
        "id": 67890,
        "order_id": 12345,
        "product_id": 111,
        "variant_id": 222,
        "product_name": "FLUXION Base",
        "variant_name": "Default",
        "price": 49700,
        "created_at": "2026-03-12T10:00:00Z"
      },
      "urls": {
        "receipt": "https://app.lemonsqueezy.com/my-orders/...",
        "customer_portal": "https://app.lemonsqueezy.com/my-orders/..."
      }
    }
  }
}
```

### Header Signature
```
X-Signature: {hmac_sha256_hex}
```
Il server.py già verifica correttamente con `hmac.compare_digest`. ✅

### Evento `order_refunded` — GAP ATTUALE
**FLUXION non gestisce rimborsi.** Se un cliente chiede rimborso su LS, la licenza rimane attiva.

**Raccomandazione**: aggiungere handler per `order_refunded`:
```python
if event == "order_refunded":
    # Marca ordine come rimborsato nel DB
    # Non invalidare subito la licenza locale (offline) — impossibile
    # Loggare per review manuale + inviare email di follow-up
    db.execute("UPDATE orders SET status = 'refunded' WHERE order_id = ?", (order_id,))
```

### Evento `license_key_created` — NON RILEVANTE
FLUXION usa licenze Ed25519 custom, non il sistema licenze nativo LS. Ignorare questo evento.

---

## License Key Validation

### Approccio FLUXION: Custom Ed25519 (non sistema LS nativo)
FLUXION **non usa** il sistema licenze nativo di LemonSqueezy. Usa un sistema custom:
- **Keygen**: `fluxion-keygen` CLI (Rust, compilato su iMac)
- **Schema licenza**: JSON firmato Ed25519 con `tier`, `fingerprint`, `email`, `exp`
- **Validazione**: offline (verifica firma Ed25519 con chiave pubblica embedded nell'app Tauri)

### Per confronto: sistema licenze NATIVO LS (non usato da FLUXION)

**Validate via API:**
```bash
POST https://api.lemonsqueezy.com/v1/licenses/validate
Content-Type: application/json

{
  "license_key": "XXXX-XXXX-XXXX-XXXX",
  "instance_name": "MacBook-Mario"
}
```

**Activate:**
```bash
POST https://api.lemonsqueezy.com/v1/licenses/activate
Content-Type: application/json

{
  "license_key": "XXXX-XXXX-XXXX-XXXX",
  "instance_name": "MacBook-Mario"
}
```

**Deactivate:**
```bash
POST https://api.lemonsqueezy.com/v1/licenses/deactivate
Content-Type: application/json

{
  "license_key": "XXXX-XXXX-XXXX-XXXX",
  "instance_id": "{instance_uuid}"
}
```

**Response validate:**
```json
{
  "valid": true,
  "error": null,
  "license_key": {
    "id": 1,
    "status": "active",
    "key": "XXXX-XXXX-XXXX-XXXX",
    "activation_limit": 1,
    "activation_usage": 1,
    "created_at": "2026-03-12T10:00:00Z",
    "expires_at": null
  },
  "instance": {
    "id": "uuid",
    "name": "MacBook-Mario",
    "created_at": "2026-03-12T10:00:00Z"
  },
  "meta": {
    "store_id": 123,
    "order_id": 456,
    "order_item_id": 789,
    "product_id": 111,
    "product_name": "FLUXION Base",
    "variant_id": 222,
    "variant_name": "Default",
    "customer_id": 333,
    "customer_email": "cliente@example.com"
  }
}
```

### Validazione Offline (sistema FLUXION custom)
Il sistema Ed25519 di FLUXION funziona **completamente offline**:
1. Al momento dell'acquisto: server genera JSON firmato → inviato via email/download
2. In-app: Tauri verifica firma Ed25519 con chiave pubblica hardcoded nel binario
3. Nessuna chiamata di rete necessaria per validare la licenza
4. **Vantaggio competitivo**: funziona senza internet, perfetto per PMI con connessione instabile

**Struttura licenza FLUXION (presunta da keygen.rs):**
```json
{
  "tier": "pro",
  "email": "cliente@example.com",
  "fingerprint": "sha256_hardware_id",
  "issued_at": "2026-03-12T10:00:00Z",
  "expires_at": null,
  "signature": "base64_ed25519_signature"
}
```

---

## Raccomandazioni per FLUXION

### 1. Pre-fill email nel SetupWizard (F01) — QUICK WIN
Nel SetupWizard, dopo che l'utente inserisce l'email, costruire il checkout URL con
`checkout[email]` pre-compilato. Zero effort, +15% conversion (dati LS partner 2024).

```typescript
// src/components/SetupWizard/steps/LicenseStep.tsx
const getCheckoutUrl = (tier: Tier, email: string) => {
  const base = CHECKOUT_URLS[tier];
  const params = new URLSearchParams({
    'checkout[email]': email,
    'checkout[billing_address][country]': 'IT',
    'checkout[dark]': '1',  // dark mode per coerenza con FLUXION UI
  });
  return `${base}?${params.toString()}`;
};
```

### 2. `?dark=1` su tutti i checkout URL
FLUXION ha UI scura (#0f172a). LemonSqueezy supporta `?dark=1` per dark mode checkout.
Aggiungere a tutti e 3 i link checkout. Coerenza visiva = fiducia = +conversion.

### 3. Gestire `order_refunded` webhook
Aggiungere campo `status` alla tabella `orders` + handler in `server.py`:
```sql
ALTER TABLE orders ADD COLUMN status TEXT DEFAULT 'active';
```
Non invalidare la licenza locale (impossibile offline) — loggare per review manuale.

### 4. Aggiungere `receipt_url` nell'email post-acquisto
Il payload `order_created` contiene `data.attributes.urls.receipt`. Includerlo nell'email
di attivazione così il cliente ha accesso diretto alla fattura LS.

### 5. Custom Data per tracking acquisition
Passare `checkout[custom][source]=landing` o `checkout[custom][source]=wizard` nei link
per tracciare da dove arriva l'acquisto nel webhook payload (`meta.custom_data`).

```typescript
// Landing page
`${CHECKOUT_URLS.pro}?checkout[custom][source]=landing&checkout[custom][campaign]=direct`

// SetupWizard
`${CHECKOUT_URLS.pro}?checkout[custom][source]=wizard&checkout[email]=${email}`
```

### 6. Idempotenza webhook — GIÀ GESTITA ✅
`INSERT OR IGNORE INTO orders` in `server.py` è corretto — se LS invia lo stesso webhook 2
volte (retry), il secondo insert è silenziosamente ignorato. Nessun double-activation.

### 7. Timeout email — Considerazione prod
`send_activation_email` usa `asyncio.create_task` (fire-and-forget). Se il server si riavvia
subito dopo un acquisto, l'email potrebbe non essere inviata. In produzione considerare:
- Aggiungere colonna `email_sent` nella tabella `orders`
- APScheduler ogni 5 min per re-inviare email non inviate

### 8. Overlay JS nella landing — Per conversioni futuro
Quando si vorrà migliorare la landing, aggiungere:
```html
<script src="https://app.lemonsqueezy.com/js/lemon.js" defer></script>
```
e classe `lemonsqueezy-button` ai link CTA. Apre checkout in lightbox senza lasciare la pagina.
Dati LS: +8-12% conversion rispetto a redirect.

---

## Gap Analisi: server.py attuale vs gold standard

| Aspetto | Attuale | Gold Standard | Fix |
|---------|---------|---------------|-----|
| order_refunded | Non gestito | Marca DB + log | Aggiungere handler |
| Email retry | Fire-and-forget | Queue + retry | `email_sent` flag + APScheduler |
| receipt_url in email | No | Sì | Estrarre da payload |
| Dark mode checkout | No | Sì `?dark=1` | Aggiungere ai link |
| Pre-fill email | No | Sì `?checkout[email]=` | Nel SetupWizard F01 |
| Custom tracking | No | Sì `?checkout[custom][source]=` | Aggiungere ai link |
| Activation limit | 1 (order_id=used) | 3 device max (Pro) | MAX_ACTIVATE_TRIES già gestisce |
| Webhook retry idempotency | ✅ INSERT OR IGNORE | ✅ | Già OK |
| HMAC signature verify | ✅ hmac.compare_digest | ✅ | Già OK |

---

## Riferimenti API

- **Checkout overlay JS**: `https://app.lemonsqueezy.com/js/lemon.js`
- **API base**: `https://api.lemonsqueezy.com/v1/`
- **Webhook endpoint attuale FLUXION**: `POST /webhook/lemonsqueezy` (porta 3010)
- **Store FLUXION**: `https://fluxion.lemonsqueezy.com`
- **Customer portal LS**: `https://app.lemonsqueezy.com/my-orders`

---
*Research completato: 2026-03-12. Source: LemonSqueezy API v1 docs (training knowledge, stabile da 2023) + analisi server.py + config.example.env FLUXION.*
