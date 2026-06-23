// Prova fedele: importa la STESSA buildEmailHtml esportata che usa il webhook (1 def, 1 call-site).
import { buildEmailHtml } from '../../fluxion-proxy/src/routes/stripe-webhook.ts';

const html = buildEmailHtml({
  tier: 'base',
  customerEmail: 'cliente.pagante@example.com',
  // dmgUrl = identico a env.DMG_DOWNLOAD_URL_MACOS in PROD (verificato 200 questa sessione)
  dmgUrl: 'https://github.com/lukeeterna/fluxion-desktop/releases/download/v1.0.0/Fluxion_1.0.0_x64.dmg',
  recoveryUrl: 'https://fluxion-app.com/api/v1/license/cliente.pagante%40example.com?token=HMAC_REAL_TOKEN',
  licensePayload: 'eyJsaWNlbnNlX2lkIjoiVEVTVCJ9', // passato negli args ma NON deve finire nel corpo (Q5)
  licenseSignature: 'ZmFrZV9zaWduYXR1cmVfZWQyNTUxOQ==',
});

console.log(html);
