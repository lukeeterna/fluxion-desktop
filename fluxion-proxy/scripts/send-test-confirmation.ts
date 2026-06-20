import { createHmac } from 'node:crypto';
import { buildEmailHtml } from '../src/routes/stripe-webhook';

const email = 'gianlucadistasi81@gmail.com';
const tier = 'base' as const;
const secret = process.env.LICENSE_RECOVERY_SECRET!;
const resendKey = process.env.RESEND_TEST_KEY!;
const base = 'https://fluxion-app.com';

const norm = email.toLowerCase().trim();
const token = createHmac('sha256', secret).update(norm).digest('hex');
const recoveryUrl = `${base}/api/v1/license/${encodeURIComponent(norm)}?token=${token}`;

const html = buildEmailHtml({
  tier,
  customerEmail: email,
  dmgUrl: '',
  recoveryUrl,
  licensePayload: 'SHOULD_NOT_APPEAR_payload',
  licenseSignature: 'SHOULD_NOT_APPEAR_signature',
});

// Guard: blob must NOT be in body (verdetto giudice Q5)
const banned = ['SHOULD_NOT_APPEAR', 'Payload firmato', 'Firma Ed25519', 'base64'];
const leaks = banned.filter((b) => html.includes(b));
if (leaks.length) {
  console.error('FAIL — blob/gergo presente nel corpo:', leaks);
  process.exit(1);
}
console.log('GUARD OK — nessun blob/gergo nel corpo. recoveryUrl len=', recoveryUrl.length);

const res = await fetch('https://api.resend.com/emails', {
  method: 'POST',
  headers: { Authorization: `Bearer ${resendKey}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({
    from: 'FLUXION <licenze@fluxion-app.com>',
    to: email,
    reply_to: 'fluxion.gestionale@gmail.com',
    subject: 'FLUXION — Il tuo ordine è confermato!',
    html,
  }),
});
const out = await res.json();
console.log('RESEND status', res.status, JSON.stringify(out));

// Save rendered preview for founder eyeballing
const fs = await import('node:fs');
fs.writeFileSync('../.claude/cache/mail-licenza-preview.html', html);
console.log('PREVIEW scritta in .claude/cache/mail-licenza-preview.html');
