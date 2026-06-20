// ─── Checkout Success Page — License delivery primary channel ──────
// S295: GET /success/:session_id
//
// Purpose:
//   Eliminate email as critical path. Customer arrives here from Stripe
//   success_url (https only, fluxion:// scheme NOT supported by Stripe).
//   Page shows:
//     1. License payload + signature (copy-paste activation)
//     2. Permanent recovery link (HMAC token, sopravvive a tab chiuso)
//     3. Download macOS button
//     4. Activation instructions
//
// Stripe drop-off mitigation:
//   success_url is best-effort (cliente può chiudere tab). Recovery link
//   permanent + email backup = ridondanza 3-way. Webhook idempotente
//   (FSAF-09 S279) = canonical source of truth in D1.
//
// First-visit race:
//   Stripe redirect può arrivare PRIMA che webhook completi write D1.
//   Handle: if D1 row not found, render "Pagamento ricevuto, licenza
//   in elaborazione..." with auto-refresh meta tag (5s).

import type { Context } from 'hono';
import type { AppEnv } from '../lib/types';
import { buildRecoveryUrl } from './license-recovery';

interface WebhookEventForSuccess {
  license_id: string;
  customer_email: string;
  product: string;
  license_payload: string;
  license_signature: string;
}

const TIER_LABELS: Record<string, string> = {
  base: 'Base',
  pro: 'Pro',
};

const TIER_PRICES: Record<string, string> = {
  base: '497',
  pro: '897',
};

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function renderPendingPage(sessionId: string, dmgUrl: string): string {
  const sessionIdSafe = escapeHtml(sessionId);
  return `<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="5">
<title>FLUXION — Pagamento ricevuto</title>
<style>
body{margin:0;padding:0;background:#0f0f0f;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#e0e0e0;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
.card{background:#1a1a1a;border-radius:12px;border:1px solid #2a2a2a;padding:40px;max-width:520px;width:100%;text-align:center}
.spinner{display:inline-block;width:48px;height:48px;border:4px solid #2a2a2a;border-top-color:#4a9eff;border-radius:50%;animation:spin 1s linear infinite;margin-bottom:20px}
@keyframes spin{to{transform:rotate(360deg)}}
h1{margin:0 0 12px;font-size:24px;color:#fff}
p{margin:8px 0;color:#aaa;line-height:1.6}
small{color:#666;font-size:12px;font-family:monospace}
</style>
</head>
<body>
<div class="card">
  <div class="spinner"></div>
  <h1>Pagamento ricevuto</h1>
  <p>Stiamo generando la tua licenza FLUXION.</p>
  <p>Questa pagina si aggiorna automaticamente fra 5 secondi.</p>
  <p>Se il caricamento richiede più di 30 secondi, contatta <a href="mailto:fluxion.gestionale@gmail.com" style="color:#4a9eff">fluxion.gestionale@gmail.com</a>.</p>
  <hr style="border:none;border-top:1px solid #2a2a2a;margin:24px 0">
  <small>Session: ${sessionIdSafe}</small>
</div>
</body>
</html>`;
}

interface RenderSuccessArgs {
  licenseId: string;
  tier: string;
  customerEmail: string;
  licensePayload: string;
  licenseSignature: string;
  recoveryUrl: string;
  dmgUrl: string;
}

function renderSuccessPage(args: RenderSuccessArgs): string {
  const tierLabel = TIER_LABELS[args.tier] ?? args.tier;
  const priceLabel = TIER_PRICES[args.tier] ?? '';
  const emailSafe = escapeHtml(args.customerEmail);
  const licenseIdSafe = escapeHtml(args.licenseId);
  const payloadSafe = escapeHtml(args.licensePayload);
  const signatureSafe = escapeHtml(args.licenseSignature);
  const recoveryUrlSafe = escapeHtml(args.recoveryUrl);
  const dmgUrlSafe = escapeHtml(args.dmgUrl);

  return `<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="no-referrer">
<title>FLUXION ${tierLabel} — Licenza pronta</title>
<style>
*{box-sizing:border-box}
body{margin:0;padding:0;background:#0f0f0f;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#e0e0e0;line-height:1.6}
.wrap{max-width:680px;margin:0 auto;padding:40px 20px}
.header{text-align:center;margin-bottom:32px}
.check{display:inline-block;width:72px;height:72px;border-radius:50%;background:linear-gradient(135deg,#10b981,#059669);line-height:72px;font-size:36px;color:#fff;margin-bottom:16px}
h1{margin:0;font-size:30px;color:#fff;letter-spacing:-0.5px}
.sub{color:#888;margin-top:8px;font-size:15px}
.section{background:#1a1a1a;border-radius:12px;border:1px solid #2a2a2a;padding:24px;margin-bottom:16px}
.section h2{margin:0 0 12px;font-size:14px;color:#4a9eff;text-transform:uppercase;letter-spacing:0.5px;font-weight:700}
.section.primary{border-color:#10b981}
.section.primary h2{color:#10b981}
.btn{display:inline-block;background:#4a9eff;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;font-size:15px;border:none;cursor:pointer;font-family:inherit}
.btn.green{background:#10b981}
.btn.ghost{background:transparent;border:1px solid #2a2a2a;color:#e0e0e0}
.btn:hover{opacity:0.9}
.code{background:#0a0a0a;border:1px solid #2a2a2a;border-radius:8px;padding:14px;font-family:'SF Mono',Menlo,Monaco,monospace;font-size:12px;color:#9cdcfe;word-break:break-all;max-height:140px;overflow-y:auto;white-space:pre-wrap}
.row{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:12px}
.note{color:#888;font-size:13px;margin:8px 0 0}
.bullet{color:#ccc;font-size:14px;margin:6px 0;padding-left:20px;position:relative}
.bullet::before{content:'→';position:absolute;left:0;color:#4a9eff}
.email-box{background:#1a2a1a;border:1px solid #10b981;border-radius:6px;padding:10px 14px;font-family:monospace;font-size:15px;color:#fff;margin:8px 0}
.footer{text-align:center;color:#555;font-size:12px;margin-top:32px;padding-top:20px;border-top:1px solid #2a2a2a}
.copied{color:#10b981;font-size:13px;margin-left:8px;opacity:0;transition:opacity 0.3s}
.copied.show{opacity:1}
</style>
</head>
<body>
<div class="wrap">

  <div class="header">
    <div class="check">&#10003;</div>
    <h1>Licenza FLUXION ${tierLabel} pronta</h1>
    <p class="sub">Ordine confermato — €${priceLabel} pagati</p>
  </div>

  <div class="section primary">
    <h2>Passo 1 — Scarica FLUXION</h2>
    <p class="bullet">macOS 12 o superiore (Intel / Apple Silicon)</p>
    <div class="row">
      <a href="${dmgUrlSafe}" class="btn green">&#9660; Scarica per macOS</a>
    </div>
    <p class="note">Compatibile con macOS 12+ (Intel e Apple Silicon).</p>
  </div>

  <div class="section">
    <h2>Passo 2 — Attiva la licenza</h2>
    <p class="bullet">Apri FLUXION dopo l'installazione</p>
    <p class="bullet">Vai su <strong>Impostazioni &rarr; Il tuo piano FLUXION</strong> e clicca <strong>&ldquo;Hai gi&agrave; una licenza? Attivala&rdquo;</strong></p>
    <p class="bullet">Apri il <strong>link di recupero del Passo 3</strong> in un browser, scarica il file licenza (oppure copia payload + firma) e <strong>caricalo / incollalo</strong> nella schermata di attivazione</p>
    <p class="bullet">Premi <strong>&ldquo;Attiva Licenza&rdquo;</strong> &mdash; fatto</p>
    <div class="email-box">Account: ${emailSafe}</div>
    <p class="note">L'attivazione &egrave; offline: FLUXION verifica la firma della licenza sul tuo computer. Nessun account, nessun codice da digitare a mano.</p>
  </div>

  <div class="section primary">
    <h2>Passo 3 — Il tuo link licenza (salvalo!)</h2>
    <p class="bullet">Questo link contiene la tua licenza. Aprilo nel browser per scaricare il file da caricare in FLUXION (Passo 2). Salvalo nelle note o nel gestore password: ti serve anche se reinstalli o cambi computer:</p>
    <div class="code" id="recovery-url">${recoveryUrlSafe}</div>
    <div class="row">
      <button class="btn ghost" onclick="copyText('recovery-url', this, 'copied-recovery')">Copia link</button>
      <span class="copied" id="copied-recovery">Copiato!</span>
    </div>
    <p class="note">Apri il link in qualsiasi browser per riottenere licenza + firma in ogni momento.</p>
  </div>

  <div class="section">
    <h2>Attivazione manuale (solo se richiesta)</h2>
    <p class="bullet">License ID: <code style="color:#9cdcfe;font-size:12px">${licenseIdSafe}</code></p>
    <p class="bullet">Payload firmato (copia se FLUXION chiede attivazione manuale):</p>
    <div class="code" id="payload-data">${payloadSafe}</div>
    <div class="row" style="margin-bottom:16px">
      <button class="btn ghost" onclick="copyText('payload-data', this, 'copied-payload')">Copia payload</button>
      <span class="copied" id="copied-payload">Copiato!</span>
    </div>
    <p class="bullet">Firma Ed25519 (base64):</p>
    <div class="code" id="signature-data">${signatureSafe}</div>
    <div class="row">
      <button class="btn ghost" onclick="copyText('signature-data', this, 'copied-sig')">Copia firma</button>
      <span class="copied" id="copied-sig">Copiato!</span>
    </div>
  </div>

  <div class="footer">
    Problemi? Scrivi a <a href="mailto:fluxion.gestionale@gmail.com" style="color:#4a9eff">fluxion.gestionale@gmail.com</a>
    <br><br>FLUXION — Il gestionale per la tua attività
  </div>

</div>

<script>
function copyText(elId, btn, copiedId){
  var el = document.getElementById(elId);
  if(!el) return;
  var txt = el.innerText || el.textContent || '';
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(txt).then(function(){ showCopied(copiedId); });
  } else {
    var ta = document.createElement('textarea');
    ta.value = txt; document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); showCopied(copiedId); } catch(e) {}
    document.body.removeChild(ta);
  }
}
function showCopied(id){
  var el = document.getElementById(id);
  if(!el) return;
  el.classList.add('show');
  setTimeout(function(){ el.classList.remove('show'); }, 1800);
}
</script>

</body>
</html>`;
}

// ─── Route handler ──────────────────────────────────────────────────

export async function checkoutSuccess(c: Context<AppEnv>) {
  // Security headers
  c.header('Referrer-Policy', 'no-referrer');
  c.header('Cache-Control', 'no-store');
  c.header('X-Content-Type-Options', 'nosniff');
  c.header('Content-Type', 'text/html; charset=utf-8');

  const sessionId = c.req.param('session_id');
  if (!sessionId) {
    return c.html('<h1>Missing session_id</h1>', 400);
  }

  if (!c.env.DB) {
    console.error('D1 binding DB missing — checkout success requires D1');
    return c.html('<h1>Service not configured</h1>', 500);
  }

  if (!c.env.LICENSE_RECOVERY_SECRET) {
    console.error('LICENSE_RECOVERY_SECRET not configured');
    return c.html('<h1>Recovery not configured</h1>', 500);
  }

  // Lookup D1 by session_id (NOT by event_id — Stripe redirect uses session_id)
  const row = await c.env.DB
    .prepare(
      `SELECT license_id, customer_email, product, license_payload, license_signature
       FROM webhook_events
       WHERE session_id = ?
       ORDER BY created_at DESC
       LIMIT 1`,
    )
    .bind(sessionId)
    .first<WebhookEventForSuccess>();

  if (!row) {
    // Webhook race — pending. Render auto-refresh page.
    return c.html(renderPendingPage(sessionId, c.env.DMG_DOWNLOAD_URL_MACOS));
  }

  // Build permanent recovery URL
  const baseUrl = new URL(c.req.url).origin;
  const recoveryUrl = await buildRecoveryUrl(
    baseUrl,
    c.env.LICENSE_RECOVERY_SECRET,
    row.customer_email,
  );

  return c.html(
    renderSuccessPage({
      licenseId: row.license_id,
      tier: row.product,
      customerEmail: row.customer_email,
      licensePayload: row.license_payload,
      licenseSignature: row.license_signature,
      recoveryUrl,
      dmgUrl: c.env.DMG_DOWNLOAD_URL_MACOS,
    }),
  );
}
