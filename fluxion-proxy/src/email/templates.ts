// ─── Email Sequence Templates — F-3 transactional sequence ──────────
// Welcome (D+0) sent at purchase via stripe-webhook.ts.
// This file: D+1 activation / D+2 first-access / D+3 tips / D+7 power / D+30 feedback.
// Sender: onboarding@resend.dev (Resend free tier, no custom domain).
// Vincolo permanente S181: zero costi, no dominio proprietario.

export type SequenceStep = 1 | 2 | 3 | 4 | 5;

export type FluxionTier = 'base' | 'pro';

export interface SequenceTemplate {
  step: SequenceStep;
  daysAfterPurchase: number;
  subject: string;
  buildHtml(params: TemplateParams): string;
}

export interface TemplateParams {
  customerEmail: string;
  tier: FluxionTier;
  dmgUrl: string;
}

const TIER_LABEL: Record<FluxionTier, string> = { base: 'Base', pro: 'Pro' };

// ─── Shared dark-theme layout (matches welcome email style) ─────────
function wrapLayout(opts: {
  preheader: string;
  headline: string;
  intro: string;
  body: string;
  ctaLabel?: string;
  ctaUrl?: string;
  footer?: string;
}): string {
  const { preheader, headline, intro, body, ctaLabel, ctaUrl, footer } = opts;
  const ctaBlock =
    ctaLabel && ctaUrl
      ? `
          <table cellpadding="0" cellspacing="0" style="margin:24px 0 8px;">
            <tr><td style="background:#10b981;border-radius:8px;">
              <a href="${ctaUrl}" style="display:inline-block;padding:14px 28px;color:#0f0f0f;font-size:15px;font-weight:700;text-decoration:none;letter-spacing:0.2px;">${ctaLabel}</a>
            </td></tr>
          </table>`
      : '';
  return `
<!DOCTYPE html>
<html lang="it">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#0f0f0f;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <span style="display:none;visibility:hidden;color:transparent;height:0;width:0;overflow:hidden;">${preheader}</span>
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f0f0f;padding:40px 20px;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#1a1a1a;border-radius:12px;border:1px solid #2a2a2a;">
        <tr><td style="padding:40px 40px 20px;">
          <h1 style="margin:0;color:#ffffff;font-size:26px;font-weight:700;letter-spacing:-0.4px;">${headline}</h1>
        </td></tr>
        <tr><td style="padding:0 40px;"><hr style="border:none;border-top:1px solid #2a2a2a;margin:0;"></td></tr>
        <tr><td style="padding:24px 40px 30px;">
          <p style="color:#e0e0e0;font-size:16px;line-height:1.65;margin:0 0 18px;">${intro}</p>
          ${body}
          ${ctaBlock}
          <p style="color:#888;font-size:13px;line-height:1.55;margin:24px 0 0;">${footer || 'Domande? Rispondi a questa email o scrivi a <a href="mailto:fluxion.gestionale@gmail.com" style="color:#4a9eff;text-decoration:none;">fluxion.gestionale@gmail.com</a>'}</p>
        </td></tr>
        <tr><td style="padding:0 40px;"><hr style="border:none;border-top:1px solid #2a2a2a;margin:0;"></td></tr>
        <tr><td style="padding:18px 40px 26px;text-align:center;">
          <p style="color:#555;font-size:12px;margin:0 0 6px;">FLUXION &mdash; Il gestionale per la tua attivit&agrave;</p>
          <p style="color:#444;font-size:11px;margin:0;">Hai ricevuto questa email perch&eacute; hai acquistato FLUXION. <a href="mailto:fluxion.gestionale@gmail.com?subject=Disiscrivimi%20dalle%20email%20di%20onboarding" style="color:#666;text-decoration:underline;">Disiscriviti</a></p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>`.trim();
}

// ─── STEP 1 — D+1 Activation Reminder ───────────────────────────────
const stepActivation: SequenceTemplate = {
  step: 1,
  daysAfterPurchase: 1,
  subject: 'FLUXION — Hai gi\u00e0 attivato la tua licenza?',
  buildHtml: (p) =>
    wrapLayout({
      preheader: 'Bastano 30 secondi: scarica, apri, inserisci la tua email.',
      headline: 'Tutto pronto per attivare FLUXION',
      intro: `Ciao, ieri hai acquistato <strong style="color:#fff;">FLUXION ${TIER_LABEL[p.tier]}</strong>. Volevamo assicurarci che tutto sia andato a buon fine.`,
      body: `
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#111;border-radius:8px;border:1px solid #2a2a2a;margin:0 0 16px;">
          <tr><td style="padding:18px 22px;">
            <p style="color:#10b981;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin:0 0 8px;">Se non hai ancora installato</p>
            <p style="color:#ccc;font-size:14px;line-height:1.6;margin:0 0 4px;">1. <a href="${p.dmgUrl}" style="color:#4a9eff;text-decoration:none;">Scarica FLUXION per macOS</a></p>
            <p style="color:#ccc;font-size:14px;line-height:1.6;margin:0 0 4px;">2. Apri il file e trascina FLUXION in Applicazioni</p>
            <p style="color:#ccc;font-size:14px;line-height:1.6;margin:0;">3. Al primo avvio inserisci: <strong style="color:#fff;font-family:monospace;">${p.customerEmail}</strong></p>
          </td></tr>
        </table>
        <p style="color:#aaa;font-size:14px;line-height:1.6;margin:0;">Hai gi&agrave; installato? Perfetto, ignora questa email. Hai problemi? Scrivici, rispondiamo entro 24h.</p>`,
      ctaLabel: 'Scarica FLUXION',
      ctaUrl: p.dmgUrl,
    }),
};

// ─── STEP 2 — D+2 First Access Tutorial ─────────────────────────────
const stepFirstAccess: SequenceTemplate = {
  step: 2,
  daysAfterPurchase: 2,
  subject: 'FLUXION — Inizia da qui: i 3 passi del primo giorno',
  buildHtml: (p) =>
    wrapLayout({
      preheader: 'Configura il tuo studio in 5 minuti: settore, orari, primi clienti.',
      headline: 'I 3 passi per iniziare con FLUXION',
      intro: `Ora che FLUXION ${TIER_LABEL[p.tier]} \u00e8 attivo, ecco la sequenza pi\u00f9 veloce per renderlo davvero tuo. 5 minuti totali.`,
      body: `
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#111;border-radius:8px;border:1px solid #2a2a2a;margin:0 0 12px;">
          <tr><td style="padding:18px 22px;">
            <p style="color:#4a9eff;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin:0 0 8px;">Passo 1 &mdash; Setup Wizard</p>
            <p style="color:#ccc;font-size:14px;line-height:1.6;margin:0;">Al primo avvio scegli il <strong style="color:#fff;">settore</strong> (parrucchiere, palestra, officina&hellip;) e gli orari di apertura. FLUXION crea automaticamente i servizi tipici della tua categoria.</p>
          </td></tr>
        </table>
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#111;border-radius:8px;border:1px solid #2a2a2a;margin:0 0 12px;">
          <tr><td style="padding:18px 22px;">
            <p style="color:#4a9eff;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin:0 0 8px;">Passo 2 &mdash; Importa i clienti</p>
            <p style="color:#ccc;font-size:14px;line-height:1.6;margin:0;">Hai un Excel o un CSV? <strong style="color:#fff;">Clienti &rarr; Importa</strong> &mdash; FLUXION riconosce nomi, telefoni e email anche da file disordinati.</p>
          </td></tr>
        </table>
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#111;border-radius:8px;border:1px solid #2a2a2a;margin:0 0 12px;">
          <tr><td style="padding:18px 22px;">
            <p style="color:#4a9eff;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin:0 0 8px;">Passo 3 &mdash; Primo appuntamento</p>
            <p style="color:#ccc;font-size:14px;line-height:1.6;margin:0;">Clicca su uno slot del calendario e crea il primo appuntamento. Se hai attivato WhatsApp, il cliente riceve subito la conferma automatica.</p>
          </td></tr>
        </table>`,
      ctaLabel: 'Apri la guida completa',
      ctaUrl: 'https://fluxion-landing.pages.dev/come-installare',
    }),
};

// ─── STEP 3 — D+3 Tips & Tricks ─────────────────────────────────────
const stepDay3: SequenceTemplate = {
  step: 3,
  daysAfterPurchase: 3,
  subject: 'FLUXION — 3 cose che la maggior parte non sa di fare',
  buildHtml: (p) =>
    wrapLayout({
      preheader: 'Promemoria automatici, cassetto fiscale, e la modalita\u0301 calendario settimanale.',
      headline: '3 trucchi che rendono FLUXION 10× pi\u00f9 utile',
      intro: 'Dopo qualche giorno di uso, ecco le tre cose che i nostri utenti pi\u00f9 attenti ci dicono di amare.',
      body: `
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#111;border-radius:8px;border:1px solid #2a2a2a;margin:0 0 12px;">
          <tr><td style="padding:18px 22px;">
            <p style="color:#10b981;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin:0 0 8px;">1. Promemoria WhatsApp 24h prima</p>
            <p style="color:#ccc;font-size:14px;line-height:1.6;margin:0;">Settings &rarr; WhatsApp &rarr; <strong style="color:#fff;">attiva &laquo;Promemoria automatico 24h&raquo;</strong>. I no-show calano in media del <strong style="color:#fff;">40%</strong>.</p>
          </td></tr>
        </table>
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#111;border-radius:8px;border:1px solid #2a2a2a;margin:0 0 12px;">
          <tr><td style="padding:18px 22px;">
            <p style="color:#10b981;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin:0 0 8px;">2. Vista settimanale</p>
            <p style="color:#ccc;font-size:14px;line-height:1.6;margin:0;">Premi <strong style="color:#fff;font-family:monospace;">W</strong> sul calendario per la vista settimanale. Drag&amp;drop per spostare un appuntamento &mdash; il cliente riceve automaticamente la nuova ora.</p>
          </td></tr>
        </table>
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#111;border-radius:8px;border:1px solid #2a2a2a;margin:0 0 12px;">
          <tr><td style="padding:18px 22px;">
            <p style="color:#10b981;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin:0 0 8px;">3. Backup automatico</p>
            <p style="color:#ccc;font-size:14px;line-height:1.6;margin:0;">Settings &rarr; Backup &rarr; <strong style="color:#fff;">scegli una cartella iCloud/Drive</strong>. FLUXION salva il database ogni notte. Niente cloud forzato, controllo totale dei tuoi dati.</p>
          </td></tr>
        </table>${p.tier === 'pro' ? `
        <p style="color:#10b981;font-size:13px;line-height:1.6;margin:12px 0 0;font-weight:600;">Bonus Pro: hai anche Sara, l\u2019assistente vocale 24/7. Provala dalla sezione &laquo;Voice&raquo; del menu.</p>` : ''}`,
    }),
};

// ─── STEP 4 — D+7 Power User ────────────────────────────────────────
const stepDay7: SequenceTemplate = {
  step: 4,
  daysAfterPurchase: 7,
  subject: 'FLUXION — Una settimana insieme. Come va?',
  buildHtml: (_p) =>
    wrapLayout({
      preheader: 'Hai usato FLUXION per 7 giorni. Cosa funziona, cosa migliorare?',
      headline: 'Una settimana di FLUXION',
      intro: 'Se hai usato FLUXION ogni giorno questa settimana, sei gi\u00e0 in vantaggio sul 90% dei nuovi utenti. Volevamo dirti grazie e chiederti una cosa.',
      body: `
        <p style="color:#e0e0e0;font-size:15px;line-height:1.65;margin:0 0 16px;">In una riga: <strong style="color:#fff;">cosa funziona meglio per te</strong> e <strong style="color:#fff;">cosa ti farebbe risparmiare ancora pi\u00f9 tempo</strong>?</p>
        <p style="color:#aaa;font-size:14px;line-height:1.6;margin:0 0 16px;">Non serve una recensione lunga. Anche solo &laquo;mi piace il calendario, vorrei pi\u00f9 colori per i servizi&raquo; \u00e8 oro per noi. Le 3 risposte pi\u00f9 ricorrenti diventano feature nelle prossime release.</p>
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#111;border-radius:8px;border:1px solid #2a2a2a;margin:8px 0 0;">
          <tr><td style="padding:16px 22px;">
            <p style="color:#888;font-size:13px;line-height:1.55;margin:0;">Rispondi a questa email con i tuoi pensieri. Leggo personalmente ogni messaggio.<br><span style="color:#666;">&mdash; il team FLUXION</span></p>
          </td></tr>
        </table>`,
      ctaLabel: 'Rispondi con il tuo feedback',
      ctaUrl: 'mailto:fluxion.gestionale@gmail.com?subject=Feedback%20FLUXION%20%E2%80%94%20settimana%201',
    }),
};

// ─── STEP 5 — D+30 Feedback Request ─────────────────────────────────
const stepDay30: SequenceTemplate = {
  step: 5,
  daysAfterPurchase: 30,
  subject: 'FLUXION — Un mese insieme: ti va di lasciare una recensione?',
  buildHtml: (_p) =>
    wrapLayout({
      preheader: 'Le tue parole aiutano altre PMI italiane a scegliere bene.',
      headline: 'Un mese con FLUXION',
      intro: 'Sono passati 30 giorni dal tuo acquisto. Se FLUXION ti sta aiutando, una tua recensione pu\u00f2 fare la differenza per altre PMI italiane che stanno valutando uno strumento simile.',
      body: `
        <p style="color:#e0e0e0;font-size:15px;line-height:1.65;margin:0 0 16px;">Bastano <strong style="color:#fff;">2 minuti</strong>. Puoi farlo dove preferisci:</p>
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#111;border-radius:8px;border:1px solid #2a2a2a;margin:0 0 12px;">
          <tr><td style="padding:14px 22px;">
            <p style="color:#ccc;font-size:14px;line-height:1.6;margin:0;">&bull; <a href="https://www.capterra.it" style="color:#4a9eff;text-decoration:none;">Capterra</a> (per software gestionali)</p>
          </td></tr>
        </table>
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#111;border-radius:8px;border:1px solid #2a2a2a;margin:0 0 12px;">
          <tr><td style="padding:14px 22px;">
            <p style="color:#ccc;font-size:14px;line-height:1.6;margin:0;">&bull; <a href="https://it.trustpilot.com" style="color:#4a9eff;text-decoration:none;">Trustpilot</a> (recensioni generali)</p>
          </td></tr>
        </table>
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#111;border-radius:8px;border:1px solid #2a2a2a;margin:0 0 16px;">
          <tr><td style="padding:14px 22px;">
            <p style="color:#ccc;font-size:14px;line-height:1.6;margin:0;">&bull; Anche solo una risposta a questa email \u00e8 perfetta &mdash; la pubblichiamo come testimonial (con il tuo permesso).</p>
          </td></tr>
        </table>
        <p style="color:#aaa;font-size:14px;line-height:1.6;margin:16px 0 0;">Se invece qualcosa non va, dimmelo direttamente. Hai 30 giorni di garanzia rimborso totale e nessuna domanda imbarazzante.</p>`,
      ctaLabel: 'Scrivici una recensione',
      ctaUrl: 'mailto:fluxion.gestionale@gmail.com?subject=Recensione%20FLUXION%20%E2%80%94%20un%20mese%20dopo',
      footer:
        'Garanzia 30gg ancora attiva fino al giorno seguente. Per il rimborso: <a href="mailto:fluxion.gestionale@gmail.com?subject=Richiesta%20rimborso" style="color:#4a9eff;text-decoration:none;">scrivici qui</a>.',
    }),
};

// ─── Registry ───────────────────────────────────────────────────────
export const SEQUENCE_TEMPLATES: Record<SequenceStep, SequenceTemplate> = {
  1: stepActivation,
  2: stepFirstAccess,
  3: stepDay3,
  4: stepDay7,
  5: stepDay30,
};

export const SEQUENCE_ORDER: SequenceStep[] = [1, 2, 3, 4, 5];
