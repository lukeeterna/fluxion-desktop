# Prompt ripartenza S320 — Post-validation completa, decisioni Luke residue

> **Generato S319 chiusura verde**: #1 chiusa SENZA self-purchase €497 (validato per simmetria + smoke €1-pro). #2 decisa (€0 ad-hoc → task implementativo). #7 audit chiuso (no action). #8/#9 deferred per context budget 52% (BLOCK_CRITICAL).

## ✅ S319 OUTCOME

| Task | Status | Evidence |
|------|--------|----------|
| #1 Primo CLOSED_WON strategy | ✅ RISOLTA — self-purchase €497 NON necessario | Vedi sotto |
| Smoke €1 ramo PRO end-to-end | ✅ PASS | `~/venture-os/state/s319-pro-smoke-evidence.json` |
| #2 macOS code signing | ✅ DECISA = €0 ad-hoc (NO Apple $99) | diventa task implementativo S320+ |
| #7 audit `ED25519_KID` secret | ✅ CHIUSO — no action | grep 0 ref + wrangler secret list (13, nessun zombie); kid hardcoded 'v1' → ED25519_PUBLIC_KEY_V1 esiste |

### Perché #1 chiusa senza €497 (data-driven)
- Stripe API LIVE read: Payment Link reali Base `{plan:base}`, Pro `{plan:pro}`.
- `detectTier` (stripe-webhook.ts:43) legge `metadata.plan` PRIMO → ramo identico per Base €497 e smoke €1.
- S317 smoke €1 base (metadata.plan=base) = stesso branch del link Base €497 reale → Base già validato.
- S319 smoke €1 pro (metadata.plan=pro) = chiude unico ramo non-testato live → **entrambi i tier validati end-to-end**.
- Self-purchase €497 dava solo metrica business (founder tasca propria, net-zero P.IVA), NON necessità tecnica. Costo netto 2× smoke €1 = €0 dopo refund.

### Smoke €1-pro evidence (S319)
- Session `cs_live_a1u5S0sk7uuuFNCHJo5FpBMHx31jthNwlNXKqNNqU5eDeQSVBpOxUnKpzX` paid, `metadata.plan=pro`
- Webhook `tier: pro` PRIMO delivery 200 (NO bug — fix FBUG-DETECT-TIER-METADATA-KEY-01 S317 regge)
- License `6a951527e374acf6ecb570526dd611b07073393e6cb69f1bc6e81a3fa04cca94`
- `/success` 200 render "Pro" + Resend email `602df8e8` delivered da licenze@fluxion-app.com
- Refund `re_3Tctq7IW4bHDTsaH0jXYcoGy` succeeded + link `plink_1Tctnj` deactivated

## 🚦 SCOPE S320 — residuo S319

### Priorità ALTA
2b. **#2 IMPLEMENT — macOS ad-hoc signing (€0)** [DECISO Luke S319]
   - Ad-hoc codesign nel build Tauri + pagina istruzioni bypass Gatekeeper PMI.
   - Research-first (REGOLA #16): friction Gatekeeper macOS 13+ per PMI italiane non-tech, best-practice 2026.
   - CTO autonomous post-research.

3. **#3 verticali canonical source** [DECISIONE LUKE richiesta]
   - 3 fonti discordi: `src/types/setup.ts` (5 macro), `switch_vertical.sh` (9 verticali), CLAUDE.md ("8 macro × 50 micro").
   - Luke sceglie canonical → CTO riallinea multi-file autonomo.

### Priorità MEDIA-BASSA (CTO autonomous, context fresco)
4. Magazzino scope v1.0 o post-launch (dipende da #3)
5. Nuovo CF token Zone DNS Edit 90d TTL
6. DMARC `p=none`→`p=quarantine` post 100 email prod
8. **Fix cosmetic Pro feature** — glitch `+`/encoding nel testo features Pro. DA LOCALIZZARE con certezza (vincolo #1: no edit alla cieca). Candidato: `landing/checkout-consent.html:130` o Stripe marketing_features (set S316). 1-line.
9. **Hardening pre-action-check** REGOLA #16 — grep handler metadata key PRIMA di script Stripe API (preveniva bug S317). Edit `~/.claude/skills/pre-action-check/SKILL.md`.

## ARTEFATTI PRODUCTION READY (invariati post-S319)
- Stripe LIVE: Base `plink_1TcpAk...8boabwRX` €497, Pro `plink_1TcpAk...fn8dioIo` €897
- Webhook LIVE `we_1TcpBL...IIap86lRB` (3 eventi), Worker prod `2a1b79bc-...`
- Landing prod `fluxion-landing.pages.dev/checkout-consent.html` (slug LIVE verified)
- Email `fluxion-app.com` Resend verified (DKIM+SPF+DMARC delivery confirmed entrambi i tier)
- VOS gate VERDE (zero CRITIQUE [OPEN])

## REGOLE ATTIVE S320
- **#4** critica + autocritica 4 punti
- **#13** pre-action-check D-XX rif
- **#14** CTO autonomous (#2b post-research, #4/#5/#6/#8/#9)
- **#15** NO A/B (eccezione: #3 scope decision)
- **#16** research-first (#2b friction Gatekeeper, #8 localizzare glitch PRIMA di edit)
- **#22** critique-then-ignore mitigation

## QUICK START S320
```bash
cd /Volumes/MontereyT7/FLUXION
cat .claude/NEXT_SESSION_PROMPT.manual.md
# Luke decide ordine. CTO autonomous dove possibile.
# #2b: deep-research Gatekeeper PMI → ad-hoc codesign + bypass page
# #3: Luke sceglie canonical verticali → CTO multi-file realign
# #8: localizzare glitch + → space PRIMA di edit (vincolo #1)
```

## CONTEXT BUDGET S319
- Chiusura a 52% (BLOCK_CRITICAL 50-70%: solo cleanup + closing). #7 cleanup safe eseguito; #8/#9 (edit file) deferred per disciplina vincolo + lezione S185-A.
- Files toccati S319: questo file + MEMORY.md + rm SESSION_DIRTY.md (stale). Zero source-code edit, zero file critici per slugs.
