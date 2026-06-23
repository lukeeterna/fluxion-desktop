import { readFileSync } from 'node:fs';

const key = process.env.RESEND_KEY;
if (!key) { console.error('NO_KEY'); process.exit(1); }
const html = readFileSync('/tmp/email_manuel.html', 'utf8');

const res = await fetch('https://api.resend.com/emails', {
  method: 'POST',
  headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({
    from: 'FLUXION <licenze@fluxion-app.com>',
    to: ['manueldx2014@gmail.com'],
    reply_to: ['fluxion.gestionale@gmail.com'],
    subject: 'FLUXION — Il tuo ordine è confermato!',
    html,
  }),
});
const body = await res.text();
console.log('HTTP', res.status);
console.log(body);
