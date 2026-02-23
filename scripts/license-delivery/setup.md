# FLUXION License Delivery Server — Setup Guide

## Prerequisiti

- iMac con Python 3.9+
- `fluxion-keygen` compilato (già fatto)
- `fluxion-keypair.json` presente (NON committare in git!)
- Cloudflare account gratuito
- Gmail account per invio email

---

## 1. Installazione dipendenze

```bash
cd /path/to/fluxion/scripts/license-delivery

# Crea venv (opzionale ma consigliato)
python3 -m venv venv
source venv/bin/activate

# Installa
pip install -r requirements.txt
```

---

## 2. Configurazione

```bash
cp config.example.env config.env
nano config.env    # compila tutti i valori
```

Valori da compilare:
- `LS_WEBHOOK_SECRET` → preso da LemonSqueezy dopo creazione webhook
- `SMTP_USER` + `SMTP_PASS` → account Gmail + App Password
- `FLUXION_KEYGEN_PATH` → percorso assoluto al binario
- `KEYPAIR_PATH` → percorso assoluto a `fluxion-keypair.json`
- `ACTIVATE_URL_BASE` → URL Cloudflare Tunnel (vedi step 4)

---

## 3. Test locale

```bash
# Avvia server
python3 server.py

# In un altro terminale — health check
curl http://localhost:3010/health
# → {"status":"ok","service":"fluxion-license-server"}

# Simula webhook LemonSqueezy (senza firma — solo per debug)
curl -X POST http://localhost:3010/webhook/lemonsqueezy \
  -H "Content-Type: application/json" \
  -d '{
    "meta": {"event_name": "order_created"},
    "data": {
      "id": "LS-TEST001",
      "attributes": {
        "user_email": "test@example.com",
        "first_order_item": {"product_name": "Fluxion Pro"}
      }
    }
  }'
# Nota: la firma HMAC sarà invalida — normal in dev

# Inserisci manualmente un ordine di test nel DB per testare /api/activate
python3 -c "
import sqlite3, time
conn = sqlite3.connect('orders.db')
conn.execute(\"INSERT OR REPLACE INTO orders (order_id, email, tier, created_at) VALUES ('LS-TEST001', 'test@example.com', 'pro', ?)\", (time.time(),))
conn.commit()
print('Ordine test inserito')
"

# Test attivazione
curl -X POST http://localhost:3010/api/activate \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","order_id":"LS-TEST001","fingerprint":"abc123test"}'
```

---

## 4. Cloudflare Tunnel (HTTPS pubblico — gratis)

```bash
# Installa cloudflared
brew install cloudflare/cloudflare/cloudflared

# Login (apre browser)
cloudflared tunnel login

# Crea tunnel
cloudflared tunnel create fluxion-license

# Avvia tunnel (punta al server locale)
cloudflared tunnel run --url http://localhost:3010 fluxion-license
```

Cloudflare ti darà un URL tipo:
`https://fluxion-license.nomecasuale.cfargotunnel.com`

Aggiorna `ACTIVATE_URL_BASE` in `config.env` con questo URL.

**Per rendere il tunnel permanente (avvio automatico):**
```bash
# Crea config file
mkdir -p ~/.cloudflared
cat > ~/.cloudflared/config.yml << EOF
tunnel: fluxion-license
credentials-file: /Users/gianlucadistasi/.cloudflared/<tunnel-id>.json
ingress:
  - hostname: fluxion-activate.tuodominio.com
    service: http://localhost:3010
  - service: http_status:404
EOF

# Avvio come LaunchAgent (macOS)
cloudflared service install
```

---

## 5. LemonSqueezy — Configurazione Webhook

1. Vai su [LemonSqueezy Dashboard](https://app.lemonsqueezy.com) → Settings → Webhooks
2. Clicca **Add endpoint**
3. URL: `https://tuo-tunnel.cfargotunnel.com/webhook/lemonsqueezy`
4. Events: seleziona **order_created**
5. Copia il **Signing Secret** e mettilo in `config.env` come `LS_WEBHOOK_SECRET`

---

## 6. Avvio in produzione

```bash
# Con nohup (semplice)
nohup python3 server.py > /tmp/fluxion-license-server.log 2>&1 &
echo $! > /tmp/fluxion-license-server.pid

# Stop
kill $(cat /tmp/fluxion-license-server.pid)

# Logs
tail -f /tmp/fluxion-license-server.log
```

---

## Flusso completo verificato

```
[Cliente acquista su LemonSqueezy]
  → LemonSqueezy invia webhook POST /webhook/lemonsqueezy
  → Server valida HMAC, salva ordine in orders.db
  → Server invia email al cliente con link activate.html

[Cliente apre activate.html]
  → Inserisce email + order_id + fingerprint
  → POST /api/activate
  → Server verifica ordine, chiama fluxion-keygen generate
  → Restituisce license JSON → download automatico

[Cliente carica fluxion-license.json nell'app]
  → App verifica firma Ed25519
  → Licenza attivata ✅
```

---

## Troubleshooting

| Problema | Soluzione |
|---------|-----------|
| `LS_WEBHOOK_SECRET` non valido | Rigenera il secret su LemonSqueezy |
| `fluxion-keygen` non trovato | Verifica `FLUXION_KEYGEN_PATH` con percorso assoluto |
| Email non arriva | Verifica App Password Gmail (non la password normale) |
| Tunnel non raggiungibile | `cloudflared tunnel info fluxion-license` |
| `used=1` ma cliente non ha ricevuto file | Scrivi a support, resetta manualmente: `UPDATE orders SET used=0 WHERE order_id='...'` |
