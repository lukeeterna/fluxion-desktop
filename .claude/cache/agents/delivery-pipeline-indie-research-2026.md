# Delivery Pipeline per Software Desktop Indie — Deep Research CoVe 2026

> **Data**: 2026-03-20
> **Scope**: Analisi di 8 software desktop di riferimento + best practice per FLUXION
> **Fonti**: Web research diretta su documentazione ufficiale e community

---

## 1. ANALISI COMPARATIVA — 8 Software Desktop

### 1.1 Obsidian (Electron, freemium + paid services)

| Aspetto | Dettaglio |
|---------|-----------|
| **Post-purchase flow** | Download gratuito dal sito. Per Sync/Publish: acquisto online → account Obsidian → attivazione in-app via login. Catalyst (supporter): pagamento → badge account + accesso insider builds |
| **License activation** | Free: nessuna licenza. Paid services: account online con email/password. Catalyst: one-time donation, no license key |
| **Auto-update** | Custom Electron updater: scarica solo `asar` firmato (non tutto il binario). Due versioni: App version (auto-update) e Installer version (richiede reinstallazione per aggiornare Electron). Setting per disabilitare |
| **Code signing** | Apple Developer ID + notarizzazione macOS. Windows: EV code signing (nessun warning SmartScreen) |
| **Installer format** | macOS: DMG. Windows: EXE (NSIS). Linux: AppImage, Snap, deb, rpm |
| **Anti-piracy** | Minimal: i servizi paid (Sync/Publish) sono server-side, non piratizzabili. L'app base e gratis. Honor system per commercial license |

**Lezione per FLUXION**: Il modello "app gratis, servizi a pagamento server-side" e non piratizzabile per design. Per lifetime license, serve un approccio diverso. L'auto-update con solo asar e brillante per ridurre download size.

---

### 1.2 Raycast (Swift nativo, free + Pro subscription)

| Aspetto | Dettaglio |
|---------|-----------|
| **Post-purchase flow** | Download gratuito dal sito. Pro: checkout online → account Raycast → login in-app attiva Pro features |
| **License activation** | Account-based: email + password. Pro features sbloccate server-side dopo login |
| **Auto-update** | Sparkle framework (standard de facto macOS). Verifica firma EdDSA + Apple code signing. Aggiornamenti in background |
| **Code signing** | Apple Developer ID + notarizzazione. App nativa Swift = integrazione perfetta |
| **Installer format** | macOS only: DMG |
| **Anti-piracy** | Account-based: features Pro richiedono autenticazione server. Extensions marketplace server-side |

**Lezione per FLUXION**: Sparkle e il gold standard per auto-update macOS. Per Tauri, il plugin `updater` con firma EdDSA e l'equivalente.

---

### 1.3 1Password (Electron/Rust, subscription)

| Aspetto | Dettaglio |
|---------|-----------|
| **Post-purchase flow** | Signup online → subscription → download app → login con account. Zero license key, tutto account-based |
| **License activation** | Account + Secret Key (generato al signup). Crypto locale con SRP (Secure Remote Password). Zero license key tradizionale |
| **Auto-update** | Electron autoUpdater (Squirrel sotto). Windows: Squirrel.Windows. macOS: Squirrel.Mac. Aggiornamenti automatici silenziosi |
| **Code signing** | Apple Developer ID + notarizzazione. Windows: EV code signing Authenticode. Firmano anche componenti interni (electron-hardener) |
| **Installer format** | macOS: DMG/PKG. Windows: EXE (Squirrel). Linux: deb, rpm, snap |
| **Anti-piracy** | Subscription server-side: senza account attivo, l'app non funziona. E2E encryption con Secret Key locale |

**Lezione per FLUXION**: Il modello subscription + account e il piu sicuro contro pirateria ma non applicabile a lifetime license. L'approccio "Rust core + frontend web" e identico a Tauri.

---

### 1.4 Calibre (Python/Qt, open source + donations)

| Aspetto | Dettaglio |
|---------|-----------|
| **Post-purchase flow** | Download gratuito dal sito. Nessun acquisto, donazioni volontarie |
| **License activation** | Nessuna: open source GPL v3 |
| **Auto-update** | Notifica in-app "nuova versione disponibile" → l'utente scarica manualmente l'installer dal sito e reinstalla. Linux: script `calibre-install` con auto-download |
| **Code signing** | Windows: firma .pyd e .dll DLLs. macOS: Developer ID. Linux: package manager signature |
| **Installer format** | macOS: DMG. Windows: MSI + portable. Linux: shell script installer, AppImage |
| **Anti-piracy** | Nessuna: open source |

**Lezione per FLUXION**: Anche software Python/Qt possono essere distribuiti efficacemente con installer nativi. L'auto-update "notifica + download manuale" e il piu semplice da implementare ma ha UX peggiore.

---

### 1.5 Notion (Electron, SaaS)

| Aspetto | Dettaglio |
|---------|-----------|
| **Post-purchase flow** | Signup online (free tier) → download app → login. Upgrade a paid: in-app o web |
| **License activation** | Account-based: email/password o SSO. Zero license key |
| **Auto-update** | Electron autoUpdater con Squirrel. Aggiornamenti automatici silenziosi in background. Restart per applicare |
| **Code signing** | Apple Developer ID + notarizzazione. Windows: EV Authenticode. Standard enterprise |
| **Installer format** | macOS: DMG. Windows: EXE (Squirrel/NSIS). Linux: deb, AppImage |
| **Anti-piracy** | SaaS puro: senza internet e account, l'app e un guscio vuoto |

**Lezione per FLUXION**: Per un'app desktop che deve funzionare offline, il modello SaaS non e applicabile. Ma l'auto-update silenzioso con Squirrel/Electron e l'UX target.

---

### 1.6 Sublime Text (C++, license key lifetime)

| Aspetto | Dettaglio |
|---------|-----------|
| **Post-purchase flow** | Download gratuito (evaluation illimitata con nag screen). Acquisto sul sito → license key inviata via email → inserimento in-app (Help > Enter License) |
| **License activation** | License key testuale (inizia con "SK3"). Validazione ibrida: locale + check periodico su `license.sublimehq.com`. Key legata alla versione major (ST3, ST4). Upgrade a pagamento tra major version |
| **Auto-update** | Notifica in-app "A new version is available" → download automatico del binario → riavvio. Canali: stable/dev. Controllabile via settings |
| **Code signing** | Apple Developer ID + notarizzazione macOS. Windows: Authenticode signing |
| **Installer format** | macOS: DMG. Windows: EXE installer + portable ZIP. Linux: deb, rpm, pacman, tarball |
| **Anti-piracy** | Nag screen periodico senza licenza (l'app funziona comunque). Server-side validation periodica. Key format crittografico con check anti-tampering |

**Lezione per FLUXION**: **MODELLO PIU VICINO A FLUXION.** License key via email post-acquisto, validazione ibrida (offline + check periodico), nag screen come deterrente morbido. L'evaluation gratuita genera trust prima dell'acquisto.

---

### 1.7 Bear (Swift nativo, subscription)

| Aspetto | Dettaglio |
|---------|-----------|
| **Post-purchase flow** | Download da Mac App Store (gratuito). Pro: in-app subscription via Apple/Google IAP. Cross-device via iCloud + stesso Apple ID |
| **License activation** | Apple gestisce tutto: receipt validation via App Store. Zero license key custom |
| **Auto-update** | App Store gestisce gli aggiornamenti automaticamente |
| **Code signing** | Apple gestisce: App Store review + signing automatico |
| **Installer format** | App Store bundle (nessun installer separato) |
| **Anti-piracy** | Apple IAP + receipt validation server-side |

**Lezione per FLUXION**: L'App Store semplifica tutto ma prende 15-30% e impone sandbox. Non applicabile per FLUXION (lifetime license, no commission).

---

### 1.8 Sketch (nativo macOS, license key → subscription)

| Aspetto | Dettaglio |
|---------|-----------|
| **Post-purchase flow** | **Legacy (license key)**: acquisto online → license key via email → download app → inserimento key in-app. **Attuale (subscription)**: signup online → download → login email/password |
| **License activation** | **Legacy**: key format "SK3-xxxx", legata a device. Max 1-2 device per key. "Unlink device" per spostare. Key valida per major version corrente + 1 anno updates. **Subscription**: account-based, nessuna key |
| **Auto-update** | Sparkle framework per distribuzione diretta. Check automatico all'avvio. Download + install in background |
| **Code signing** | Apple Developer ID + notarizzazione (distribuzione diretta, non App Store) |
| **Installer format** | macOS: DMG (download diretto dal sito) |
| **Anti-piracy** | Legacy: device registration + server-side check. Subscription: account-based server-side. Transizione da key a subscription per ridurre pirateria |

**Lezione per FLUXION**: Sketch ha migrato da license key a subscription. Il modello legacy key (device-locked, major version bound) e molto simile a quello che FLUXION deve implementare. La transizione di Sketch conferma che lifetime key e sostenibile solo con upgrade a pagamento tra major version.

---

## 2. MATRICE COMPARATIVA SINTETICA

| Software | Delivery | License | Auto-update | Code Sign | Installer | Anti-piracy |
|----------|----------|---------|-------------|-----------|-----------|-------------|
| **Obsidian** | Direct download | Account (services) | Custom asar update | Apple Dev ID + Windows EV | DMG/EXE/AppImage | Server-side services |
| **Raycast** | Direct download | Account-based | Sparkle (macOS) | Apple Dev ID | DMG | Server-side features |
| **1Password** | Direct download | Account + Secret Key | Squirrel (Electron) | Apple Dev ID + Windows EV | DMG/EXE | Subscription server |
| **Calibre** | Direct download | Open source | Notifica + manual | Dev ID + Windows | DMG/MSI/AppImage | Nessuna |
| **Notion** | Direct download | Account SaaS | Squirrel (Electron) | Apple Dev ID + Windows EV | DMG/EXE | SaaS server |
| **Sublime Text** | Direct download | **License key email** | Notifica + auto-download | Apple Dev ID + Windows | DMG/EXE/deb | **Nag screen + server check** |
| **Bear** | App Store | Apple IAP | App Store | Apple (auto) | App Store | Apple receipt |
| **Sketch** | Direct download | **Key → Subscription** | Sparkle | Apple Dev ID | DMG | **Device lock + server** |

---

## 3. BEST PRACTICE 2026 per Software Desktop Indie Lifetime License

### 3.1 Flow Ideale Post-Acquisto (per FLUXION via LemonSqueezy)

```
UTENTE CLICCA "ACQUISTA" (landing page / in-app)
    │
    ▼
[1] LemonSqueezy Checkout (hosted, PCI-compliant)
    - Pagamento carta/PayPal
    - LemonSqueezy genera license key automaticamente
    │
    ▼
[2] Post-checkout: 2 delivery simultanei
    │
    ├── [2a] Email receipt (automatica LemonSqueezy)
    │   - License key inclusa nel corpo email
    │   - Link download diretto al DMG/MSI (hosted su LemonSqueezy o GitHub Releases)
    │   - Link a guida installazione (fluxion-landing.pages.dev/installazione)
    │
    └── [2b] Redirect post-checkout (LemonSqueezy "Thank you" page custom)
        - Mostra license key copiabile
        - Bottone download diretto
        - QR code per scaricare su altro device
    │
    ▼
[3] Utente scarica e installa FLUXION
    │
    ▼
[4] Primo avvio → Setup Wizard
    - Step "Attivazione Licenza": campo per incollare license key
    - App chiama LemonSqueezy License API → POST /v1/licenses/activate
    - Salva instance_id + license key in SQLite locale (encrypted)
    - Se offline: accetta key, valida al primo collegamento
    │
    ▼
[5] App attivata → uso normale
    - Validazione periodica (ogni 7 giorni) via LemonSqueezy /validate
    - Se offline: grace period 30 giorni con cached validation
    - Se key revocata: nag screen dopo 30 giorni, mai blocco totale
```

### 3.2 License Validation Architecture — Offline-First con LemonSqueezy

#### Architettura a 3 livelli

```
LIVELLO 1 — LOCALE (sempre disponibile)
├── License key salvata in SQLite (AES-256 encrypted)
├── instance_id salvato con la key
├── last_validated_at timestamp
├── license_status cached ("active", "expired", "disabled")
└── Validazione locale: key non vuota + status cached = "active" + last_validated < 30 giorni

LIVELLO 2 — ONLINE (quando disponibile)
├── POST https://api.lemonsqueezy.com/v1/licenses/validate
│   body: { license_key, instance_id }
├── Verifica: store_id, product_id, variant_id hardcodati nell'app
├── Aggiorna cache locale con risposta
└── Frequenza: ogni 7 giorni (non ad ogni avvio — rispetta utenti offline)

LIVELLO 3 — GRACE PERIOD (fallback)
├── Se online validation fallisce per 30 giorni consecutivi → nag screen morbido
├── Mai blocco totale dell'app (le funzioni base devono SEMPRE funzionare)
├── Nag screen: "La tua licenza non e stata verificata da 30 giorni. Connettiti a internet."
└── Dopo 90 giorni senza validazione → downgrade a funzionalita base (calendario solo)
```

#### Flow di Attivazione (Rust/Tauri side)

```rust
// Pseudocodice — da implementare in src-tauri/
struct LicenseInfo {
    license_key: String,
    instance_id: String,
    variant_id: u64,          // Base=XXX, Pro=YYY, Clinic=ZZZ
    status: LicenseStatus,    // Active, Expired, Disabled
    last_validated: DateTime,
    activation_date: DateTime,
    customer_email: String,
}

// Activation flow
async fn activate_license(key: &str) -> Result<LicenseInfo> {
    let resp = reqwest::Client::new()
        .post("https://api.lemonsqueezy.com/v1/licenses/activate")
        .form(&[
            ("license_key", key),
            ("instance_name", &machine_identifier()),
        ])
        .send().await?;

    let data: LemonSqueezyResponse = resp.json().await?;

    // CRITICAL: Verify store_id and product_id match FLUXION
    assert_eq!(data.meta.store_id, FLUXION_STORE_ID);
    assert!(FLUXION_PRODUCT_IDS.contains(&data.meta.product_id));

    // Determine tier from variant_id
    let tier = match data.meta.variant_id {
        VARIANT_BASE => Tier::Base,
        VARIANT_PRO => Tier::Pro,
        VARIANT_CLINIC => Tier::Clinic,
        _ => return Err("Invalid product variant"),
    };

    // Save to encrypted SQLite
    save_license_to_db(LicenseInfo { ... })?;
    Ok(license_info)
}
```

#### Perche NON Ed25519 custom ma LemonSqueezy License API

| Criterio | Ed25519 Custom | LemonSqueezy License API |
|----------|---------------|--------------------------|
| **Complessita** | Alta: generare key, firmare, validare, gestire revoche | Bassa: 3 endpoint REST gia pronti |
| **Revoca licenze** | Da implementare (server custom) | Dashboard LemonSqueezy + API |
| **Refund handling** | Manuale | Automatico: LemonSqueezy revoca key al refund |
| **Device management** | Da implementare | Incluso: activation_limit + instances |
| **Costo** | Dev time + server per revoche | Zero (incluso in LemonSqueezy fees) |
| **Offline support** | Nativo (firma locale) | Cache + grace period (30 giorni) |

**Decisione raccomandata**: Usare LemonSqueezy License API come primary, con cache locale per offline. Ed25519 custom e overengineering per un indie con <1000 clienti. Se in futuro serve migrazione, il layer di astrazione lo permette.

### 3.3 Auto-Update Strategy per Tauri 2

#### Architettura Raccomandata

```
TAURI UPDATER PLUGIN (@tauri-apps/plugin-updater)
    │
    ▼
Endpoint: GitHub Releases (gratuito, affidabile, CDN globale)
    - latest.json generato da Tauri Action in CI
    - Binari firmati con EdDSA (tauri signer)
    - Firma verificata dall'app prima di installare
    │
    ▼
Flow in-app:
    1. All'avvio, check silenzioso su latest.json
    2. Se nuova versione: dialog "Aggiornamento disponibile v1.1.0"
       - Note di rilascio mostrate
       - Bottoni: "Aggiorna ora" / "Ricordamelo dopo"
    3. Download in background con progress bar
    4. Install + restart automatico
    │
    ▼
Fallback per utenti offline:
    - Pagina download manuale su fluxion-landing.pages.dev/download
    - Link diretto nell'email post-acquisto
```

#### Configurazione tauri.conf.json

```json
{
  "plugins": {
    "updater": {
      "active": true,
      "dialog": true,
      "endpoints": [
        "https://github.com/gianlucanewtech/fluxion/releases/latest/download/latest.json"
      ],
      "pubkey": "<TAURI_SIGNER_PUBLIC_KEY>"
    }
  }
}
```

#### CI/CD con GitHub Actions

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags: ['v*']

jobs:
  build:
    strategy:
      matrix:
        platform: [macos-latest, windows-latest]
    runs-on: ${{ matrix.platform }}
    steps:
      - uses: actions/checkout@v4
      - uses: tauri-apps/tauri-action@v0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          TAURI_SIGNING_PRIVATE_KEY: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY }}
          TAURI_SIGNING_PRIVATE_KEY_PASSWORD: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY_PASSWORD }}
          # macOS
          APPLE_CERTIFICATE: ${{ secrets.APPLE_CERTIFICATE }}
          APPLE_CERTIFICATE_PASSWORD: ${{ secrets.APPLE_CERTIFICATE_PASSWORD }}
          APPLE_SIGNING_IDENTITY: ${{ secrets.APPLE_SIGNING_IDENTITY }}
          APPLE_ID: ${{ secrets.APPLE_ID }}
          APPLE_PASSWORD: ${{ secrets.APPLE_PASSWORD }}
          APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
        with:
          tagName: v__VERSION__
          releaseName: 'FLUXION v__VERSION__'
          releaseBody: 'See the changelog for details.'
          releaseDraft: true
```

### 3.4 Delivery via LemonSqueezy — Configurazione Completa

#### Setup Prodotto LemonSqueezy

1. **Product Type**: "Software License" (non "Digital Download")
2. **License Key Generation**: ABILITATO
3. **Activation Limit**: 2 per Base, 3 per Pro, 5 per Clinic (multi-device ragionevole)
4. **License Key expiry**: Never (lifetime)

#### File Hosting — Due Opzioni

| Opzione | Pro | Contro |
|---------|-----|--------|
| **GitHub Releases** (raccomandata) | Gratuito, CDN globale, integrato con auto-updater Tauri, versioning automatico | Repo deve essere public o GitHub Pro |
| **LemonSqueezy File Hosting** | Integrato nel checkout, nessun setup aggiuntivo | Limite 5GB, meno flessibile per multi-platform |

**Raccomandazione**: GitHub Releases per i binari + LemonSqueezy per license key delivery. Il checkout redirect include link a GitHub Releases.

#### Email Template Post-Acquisto (LemonSqueezy)

```
Oggetto: La tua licenza FLUXION e pronta!

Ciao {customer_name},

Grazie per aver scelto FLUXION! Ecco tutto quello che ti serve:

━━━━━━━━━━━━━━━━━━━━━━━━━━
LA TUA LICENZA
━━━━━━━━━━━━━━━━━━━━━━━━━━
{license_key}

Conserva questa email — ti servira per attivare FLUXION.

━━━━━━━━━━━━━━━━━━━━━━━━━━
DOWNLOAD
━━━━━━━━━━━━━━━━━━━━━━━━━━
- macOS: [Download DMG](https://github.com/.../releases/latest/download/Fluxion.dmg)
- Windows: [Download MSI](https://github.com/.../releases/latest/download/Fluxion.msi)

━━━━━━━━━━━━━━━━━━━━━━━━━━
INSTALLAZIONE (2 minuti)
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Scarica e installa FLUXION
2. Al primo avvio, incolla la licenza quando richiesto
3. Configura la tua attivita nel wizard guidato
4. Fatto! FLUXION e pronto all'uso.

Guida completa: https://fluxion-landing.pages.dev/installazione

━━━━━━━━━━━━━━━━━━━━━━━━━━
SUPPORTO
━━━━━━━━━━━━━━━━━━━━━━━━━━
- Centro assistenza: https://fluxion-landing.pages.dev/help
- Email: fluxion.gestionale@gmail.com

Garanzia 30 giorni soddisfatti o rimborsati.

— Il team FLUXION
```

#### Webhook LemonSqueezy → Cloudflare Worker

```
POST /webhook/lemonsqueezy → fluxion-proxy.gianlucanewtech.workers.dev

Eventi da gestire:
- order_created → log vendita + invio email benvenuto custom (opzionale)
- license_key_created → log in KV per phone-home correlation
- subscription_payment_success → (futuro, per Pro subscription se cambia modello)
- order_refunded → revoca automatica license key via API
```

---

## 4. RACCOMANDAZIONI FINALI per FLUXION

### 4.1 Flow Post-Acquisto Raccomandato (priorita implementazione)

```
PRIORITA 1 (prima vendita):
├── LemonSqueezy product con license key generation
├── Email automatica con key + link download GitHub Releases
├── Setup Wizard: step "Incolla licenza" → LemonSqueezy /activate
└── Cache locale in SQLite encrypted

PRIORITA 2 (settimana 2):
├── Tauri updater plugin con GitHub Releases endpoint
├── Webhook LemonSqueezy → CF Worker per tracking vendite
└── Thank-you page custom post-checkout

PRIORITA 3 (mese 1):
├── Validazione periodica (7 giorni) con grace period (30 giorni)
├── Dashboard in-app: stato licenza, tier, scadenza Sara trial
└── Deactivation: "Sposta licenza" → deactivate instance → activate su nuovo device
```

### 4.2 Cosa NON Fare

| Errore comune | Perche evitarlo |
|---------------|-----------------|
| Ed25519 custom key generation | Overengineering: LemonSqueezy lo fa gia. Aggiunge complessita senza valore |
| Hardware fingerprint rigido | Frustra utenti che cambiano PC. LemonSqueezy instance management e sufficiente |
| Blocco totale app senza licenza | Genera supporto. Meglio nag screen + downgrade graduale (come Sublime Text) |
| Auto-update forzato | Utenti PMI odiano sorprese. Dialog con "Aggiorna ora / Dopo" |
| Hosting binari su LemonSqueezy | Limite 5GB, nessun CDN. GitHub Releases e superiore |
| Server custom per license management | Costo + manutenzione. LemonSqueezy API + CF Worker e sufficiente |

### 4.3 Modello di Riferimento per FLUXION

**Il modello piu vicino e Sublime Text** (lifetime license, nag screen, validation ibrida), con queste differenze:

| Aspetto | Sublime Text | FLUXION (raccomandato) |
|---------|-------------|------------------------|
| Evaluation | Illimitata con nag | 30 giorni trial Sara (Base), poi solo gestionale |
| License delivery | Email diretta | LemonSqueezy email automatica |
| Validation | Server custom | LemonSqueezy License API |
| Auto-update | Custom C++ | Tauri updater plugin |
| Code signing | Apple Dev ID + Windows EV | Apple Dev ID + Windows (Azure Trusted Signing) |
| Anti-piracy | Nag screen + server check | Nag screen + LemonSqueezy validation + feature gating per tier |

---

## 5. FONTI

- [Obsidian License Overview](https://obsidian.md/license)
- [Obsidian Update Mechanism](https://help.obsidian.md/updates)
- [Sublime Text Sales FAQ](https://www.sublimetext.com/sales_faq)
- [Sublime Text Portable License Keys](https://www.sublimetext.com/docs/portable_license_keys.html)
- [Sketch License Overview](https://www.sketch.com/license/)
- [Sketch Device Registration](https://www.sketch.com/support/mac-only-licenses/manage/register-a-device/)
- [Bear Pro Features & Price](https://bear.app/faq/features-and-price-of-bear-pro/)
- [Sparkle Framework](https://sparkle-project.org/)
- [Tauri v2 Updater Plugin](https://v2.tauri.app/plugin/updater/)
- [Tauri v2 Auto-Update and Distribution Guide](https://www.oflight.co.jp/en/columns/tauri-v2-auto-update-distribution)
- [LemonSqueezy License API](https://docs.lemonsqueezy.com/api/license-api)
- [LemonSqueezy License Key Generation](https://docs.lemonsqueezy.com/help/licensing/generating-license-keys)
- [LemonSqueezy Activate License Key](https://docs.lemonsqueezy.com/api/license-api/activate-license-key)
- [LemonSqueezy Validate License Key](https://docs.lemonsqueezy.com/api/license-api/validate-license-key)
- [Keygen.sh Offline Licensing](https://keygen.sh/docs/choosing-a-licensing-model/offline-licenses/)
- [Keygen.sh Ed25519 Verification](https://github.com/keygen-sh/example-cpp-ed25519-verification)
- [Electron Code Signing](https://www.electronjs.org/docs/latest/tutorial/code-signing)
- [Apple Developer ID Distribution](https://developer.apple.com/developer-id/)
- [Apple Notarization](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution)
- [Code Signing and Notarization with Sparkle](https://steipete.me/posts/2025/code-signing-and-notarization-sparkle-and-tears)
- [Mac App Store vs Direct Distribution 2026](https://www.hendoi.in/blog/mac-app-store-vs-direct-distribution-macos-app-2026)
- [Distributing Mac Apps Outside App Store](https://www.rambo.codes/posts/2021-01-08-distributing-mac-apps-outside-the-app-store)
