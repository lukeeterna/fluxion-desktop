# FLUXION License Generator

Tool ufficiale per generare licenze Ed25519 firmate per FLUXION.

⚠️ **IMPORTANTE SICUREZZA**: Questo tool contiene la CHIAVE PRIVATA. Conservalo in luogo sicuro e non condividerlo mai!

## 📁 Posizione

```
/Volumes/MontereyT7/FLUXION/fluxion-license-generator/
```

Questa directory è SEPARATA dal progetto principale FLUXION per motivi di sicurezza.

## 🚀 Installazione

```bash
cd fluxion-license-generator
cargo build --release
```

L'eseguibile si troverà in:
```
target/release/fluxion-keygen
```

## 📖 Utilizzo

### 1. Genera Keypair (una sola volta)

```bash
./target/release/fluxion-keygen init
```

Questo crea `fluxion-keypair.json` con:
- Chiave privata (🔒 **TOP SECRET**)
- Chiave pubblica (da inserire nel codice FLUXION)

**Conserva `fluxion-keypair.json` in luogo sicuro e offline!**

### 2. Genera Licenza

```bash
./target/release/fluxion-keygen generate \
  --tier pro \
  --fingerprint "a1b2c3d4e5f6..." \
  --name "Studio Dentistico Rossi" \
  --email "info@studio.it" \
  --verticals "odontoiatrica" \
  --output "license-studio-rossi.json"
```

Parametri:
- `--tier`: `trial` | `base` | `pro` | `enterprise`
- `--fingerprint`: Hardware fingerprint del cliente (da FLUXION > Impostazioni > Licenza)
- `--name`: Nome del licenziatario
- `--email`: Email del licenziatario
- `--verticals`: Lista verticali separate da virgola (es: "odontoiatrica,estetica")
- `--days`: Giorni validità (omesso = lifetime)
- `--output`: Path file output

### 3. Verifica Licenza

```bash
./target/release/fluxion-keygen verify --license license-studio-rossi.json
```

### 4. Info Licenza

```bash
./target/release/fluxion-keygen info --license license-studio-rossi.json
```

### 5. Fingerprint Locale (test)

```bash
./target/release/fluxion-keygen fingerprint
```

## 💰 Tier Disponibili

| Tier | Prezzo | Verticali | Voice Agent | API Access |
|------|--------|-----------|-------------|------------|
| Trial | Gratis | Tutte | ✅ | ✅ |
| Base | €199 | 1 | ❌ | ❌ |
| Pro | €399 | 3 | ✅ | ❌ |
| Enterprise | €799 | Tutte | ✅ | ✅ |

## 🔒 Sicurezza

1. **Chiave Privata**: Tenere offline, backup su USB cifrata
2. **Generazione**: Fare su macchina air-gapped se possibile
3. **Distribuzione**: Inviare solo il file `license.json` al cliente
4. **Revoca**: Non c'è revoca offline (vantaggio: funziona sempre)

## 📝 Workflow Vendita

1. Cliente ti manda il **fingerprint** dalla app FLUXION
2. Tu generi licenza con `fluxion-keygen generate`
3. Invi file `license.json` al cliente
4. Cliente carica file in FLUXION > Impostazioni > Attiva Licenza
5. Profit! 💰

## ⚠️ Troubleshooting

**Errore: "Chiave privata non trovata"**
→ Assicurati di avere `fluxion-keypair.json` nella directory corrente o specifica `--keypair`

**Licenza non valida su FLUXION**
→ Verifica che la chiave pubblica in `license_ed25519.rs` corrisponda alla privata usata

**Fingerprint diverso**
→ Il fingerprint è hardware-locked. Se il cliente cambia PC, serve nuova licenza.
