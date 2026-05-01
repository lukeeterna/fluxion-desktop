# Vendor AV Submission Guide (S184 α.2 STEP 2)

**Obiettivo**: ridurre falsi positivi su FLUXION DMG e MSI sottomettendo
i binari ai principali vendor antivirus.

**Quando**: dopo ogni release stable (v1.0.1, v1.0.2, ...).
**Frequenza submission**: 1× per release per vendor.
**Costo**: €0.

---

## Binari da sottomettere

| Asset | Path GitHub Release | SHA256 |
|-------|--------------------|--------|
| Fluxion_1.0.1_x64.dmg | https://github.com/lukeeterna/fluxion-desktop/releases/download/v1.0.1/Fluxion_1.0.1_x64.dmg | (vedi GitHub Release page) |
| Fluxion_1.0.1_x64.msi | https://github.com/lukeeterna/fluxion-desktop/releases/download/v1.0.1/Fluxion_1.0.1_x64.msi | (vedi GitHub Release page) |

**Pre-step**: scarica ENTRAMBI i binari in locale prima di iniziare le submission
(alcuni portali richiedono upload diretto, non URL).

---

## 1. Microsoft Defender (PRIORITÀ MASSIMA — copre ~80% Win Italia)

**URL**: https://www.microsoft.com/en-us/wdsi/filesubmission

**Step**:
1. Login con account Microsoft (gratuito — uso `fluxion.gestionale@gmail.com`)
2. Selezione: **Submit a file as enterprise customer** = NO (siamo home/dev)
3. **Software vendor or developer** → SI
4. Upload: `Fluxion_1.0.1_x64.msi`
5. Detection name: lascia vuoto (non sappiamo se rileva qualcosa)
6. **What do you believe this file is?** → Incorrectly detected as malware/malicious
7. Definition version: latest
8. Submit → ottieni **Submission ID** (es. `7300011234567890`)
9. Submit anche `Fluxion_1.0.1_x64.dmg` (Defender scansiona anche DMG su Mac con WD installato)
10. Salva entrambi gli ID

**Tempo risposta**: 24-72h. Email automatica risultato.

---

## 2. Norton / Symantec / NortonLifeLock

**URL**: https://submit.norton.com/

**Step**:
1. **Submit a False Positive**
2. Email: `fluxion.gestionale@gmail.com`
3. Upload MSI + DMG (uno alla volta, due submission separate)
4. **File category**: Software / Application
5. **Reason**: "FLUXION is a legitimate desktop business management software. Built with Tauri 2.x + Rust + Python sidecar. Code-signed ad-hoc only (Apple Developer ID is paid €99/year, not affordable for solo dev)."
6. Submit → ottieni Norton case ID

**Tempo risposta**: 48h tipico.

---

## 3. Kaspersky

**URL**: email diretta a `newvirus@kaspersky.com`

**Subject**: `False Positive — FLUXION v1.0.1 — Fluxion_1.0.1_x64.msi`

**Body** (template):
```
Dear Kaspersky team,

I am the developer of FLUXION (https://fluxion-landing.pages.dev),
a desktop business management software built with Tauri 2.x + Rust.

Kaspersky may flag the attached binary as suspicious due to:
- ad-hoc code signing (no paid certificate)
- bundled Python interpreter (PyInstaller for voice agent)
- self-update capability (Tauri updater)

These are legitimate features. The file is NOT malware.

Source code: https://github.com/lukeeterna/fluxion-desktop
VirusTotal: <link your VirusTotal scan here>

Please whitelist this binary in your next definitions update.

Best regards,
Gianluca Di Stasi
fluxion.gestionale@gmail.com
```

**Allegati**: MSI + DMG (compressi in ZIP se >25MB).

**Tempo risposta**: 3-5 giorni.

---

## 4. Avast / AVG

**URL**: email a `virus@avast.com`

**Subject**: `Whitelist Request — FLUXION v1.0.1`

**Body**: stesso template Kaspersky, allegando MSI + DMG.

In aggiunta: submit anche tramite https://www.avast.com/en-us/false-positive-file-form-submit
(form web piu' veloce di email).

---

## 5. ESET / NOD32 (opzionale, copre Italia ~5%)

**URL**: https://www.eset.com/int/support/contact/false-positive/

**Tempo risposta**: 24-48h.

---

## Tracking — salvare in `~/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/reference_av_submissions.md`

Dopo ogni submission, aggiornare la memory con:

```markdown
## v1.0.1 Submissions (2026-05-XX)

| Vendor | Submission ID | Status | Last check |
|--------|--------------|--------|------------|
| Microsoft Defender | 7300011234567890 | Submitted | 2026-05-XX |
| Norton | 90234567 | Submitted | 2026-05-XX |
| Kaspersky | (email reply) | Pending | - |
| Avast | (email reply) | Pending | - |
| ESET | XYZ123 | Submitted | 2026-05-XX |
```

---

## VirusTotal pre-check (gratuito, raccomandato)

PRIMA di sottomettere ai vendor, scansiona su VirusTotal per
identificare quali AV già flaggano FLUXION:

```bash
# Upload via CLI (dopo aver creato API key gratuita su virustotal.com)
curl -F "file=@Fluxion_1.0.1_x64.msi" \
     -H "x-apikey: YOUR_VT_API_KEY" \
     https://www.virustotal.com/api/v3/files

# Recupera risultato
curl https://www.virustotal.com/api/v3/files/<sha256> \
     -H "x-apikey: YOUR_VT_API_KEY" | jq .data.attributes.last_analysis_stats
```

Salva il **link al report VirusTotal** nella email post-purchase
(già implementato in `landing/come-installare.html` sezione `#virustotal`).

---

## Strategia long-term

Se i falsi positivi persistono dopo 2-3 release con submission:
1. Investiga uso di **packer/obfuscator** (es. UPX disabilitato in PyInstaller)
2. Considera **EV code-signing certificate** Windows (~€350/anno) — ma rompe guardrail ZERO COSTI di CLAUDE.md
3. Alternativa: **reproducible build** + **public CI** → vendor whitelist piu' veloce

Per ora rimaniamo su submission manuale post-release. Se >10 cliente reali
segnalano AV blocking, riconsiderare EV cert.
