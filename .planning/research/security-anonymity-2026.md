# Security & Workflow Research - CoVe 2026
> Ricerca approfondita condotta il 2026-02-27
> Metodo: WebSearch multi-query + analisi fonti primarie

---

## 1. ZeroClaw Sandbox Isolation (macOS 2026)

### Raccomandazione finale: Lima VM + sandbox-exec ibrido

La soluzione ottimale per ZeroClaw v0.1.7 su macOS Big Sur/Monterey e' un approccio a **due livelli**:

1. **Livello 1 (leggero, sviluppo quotidiano)**: `sandbox-exec` con profilo `.sb` custom — blocca accesso a `~/.ssh`, `~/.aws`, portachiavi, rete non autorizzata. Zero overhead.
2. **Livello 2 (massima sicurezza)**: Lima VM — isolamento kernel completo, rete separata, nessun accesso host filesystem.

Firejail **non e' disponibile su macOS** (e' solo Linux). App Sandbox di Apple (entitlements) richiede firma del codice Apple e non si applica a tool CLI di terze parti.

---

### 1.1 Opzione A: sandbox-exec (macOS Seatbelt)

`sandbox-exec` e' il tool nativo macOS (POSIX, disponibile su Big Sur e Monterey) basato su TrustedBSD Mandatory Access Control. Usa profili `.sb` in sintassi Scheme/LISP.

**Profilo consigliato per ZeroClaw** — salva come `~/.zeroclaw/sandbox.sb`:

```scheme
(version 1)

; Nega tutto di default — approccio whitelisting
(deny default)

; Permetti lettura sistema (necessario per eseguire Python, binari)
(allow file-read*
  (subpath "/usr/lib")
  (subpath "/usr/local/lib")
  (subpath "/System/Library")
  (subpath "/Library/Frameworks")
  (subpath "/private/tmp")
  (subpath "/tmp")
  (literal "/dev/null")
  (literal "/dev/random")
  (literal "/dev/urandom"))

; Permetti lettura/scrittura solo nelle directory di lavoro ZeroClaw
(allow file-read* file-write*
  (subpath "/Volumes/MontereyT7/FLUXION")
  (subpath (param "HOME_DIR")))

; Blocco esplicito aree sensibili (defense in depth)
(deny file-read* file-write*
  (subpath (string-append (param "HOME_DIR") "/.ssh"))
  (subpath (string-append (param "HOME_DIR") "/.aws"))
  (subpath (string-append (param "HOME_DIR") "/.gnupg"))
  (subpath (string-append (param "HOME_DIR") "/Library/Keychains"))
  (subpath (string-append (param "HOME_DIR") "/Library/Cookies"))
  (subpath "/etc/ssh"))

; Blocco portachiavi macOS
(deny mach-lookup
  (global-name "com.apple.securityd")
  (global-name "com.apple.SecurityServer"))

; Rete: permetti solo verso endpoint autorizzati
; (per blocco totale rete: usa "deny network*")
(allow network-outbound
  (remote ip "0.0.0.0/0" port 443)   ; HTTPS
  (remote ip "0.0.0.0/0" port 80))   ; HTTP

; Blocca connessioni locali non autorizzate (eccetto localhost Bridge)
(allow network-outbound
  (remote ip "127.0.0.1" port 3001)  ; Tauri Bridge
  (remote ip "127.0.0.1" port 3002)) ; Voice Agent

; Permetti esecuzione processi Python/shell
(allow process-exec
  (subpath "/usr/bin")
  (subpath "/usr/local/bin")
  (subpath "/opt/homebrew/bin"))

; Permetti segnali interni
(allow signal (target self))
```

**Come avviare ZeroClaw con sandbox:**

```bash
sandbox-exec -f ~/.zeroclaw/sandbox.sb \
  -D HOME_DIR="$HOME" \
  zeroclaw agent -m "istruzioni"
```

**Limitazioni di sandbox-exec:**
- Su macOS Big Sur+, le app Apple (launchd, XPC) bypassano sandbox-exec tramite Content Filter Extension — e' un bug/feature noto.
- Non protegge da privilege escalation via vulnerabilita' kernel.
- Fonte: [A New Era of macOS Sandbox Escapes](https://jhftss.github.io/A-New-Era-of-macOS-Sandbox-Escapes/)

---

### 1.2 Opzione B: Lima VM (Raccomandato per massima sicurezza)

Lima (CNCF project, ~20k stars) avvia VM Linux leggere su macOS con accesso condiviso controllato.

**Installazione:**

```bash
brew install lima
```

**Template Lima per ZeroClaw** — salva come `~/.zeroclaw/lima-zeroclaw.yaml`:

```yaml
# Lima VM per ZeroClaw - isolamento massimo
vmType: qemu
os: Linux
arch: x86_64
memory: "2GiB"
disk: "20GiB"

# Mount SOLO la directory di lavoro FLUXION (read-write)
# Il resto del filesystem host NON e' accessibile
mounts:
  - location: "/Volumes/MontereyT7/FLUXION"
    writable: true
  - location: "/tmp/zeroclaw-output"
    writable: true

# Rete: NAT isolato (non espone porte host)
networks:
  - lima: user-v2

# Forwarding porte: solo quelle necessarie
portForwards:
  - guestPort: 3001
    hostIP: "127.0.0.1"
  - guestPort: 3002
    hostIP: "127.0.0.1"

# Provisioning: installa ZeroClaw nella VM
provision:
  - mode: user
    script: |
      #!/bin/bash
      # Installa dipendenze ZeroClaw nella VM isolata
      pip3 install zeroclaw-agent 2>/dev/null || true
```

**Avvio e uso:**

```bash
# Crea VM ZeroClaw (prima volta)
limactl create --name=zeroclaw ~/.zeroclaw/lima-zeroclaw.yaml
limactl start zeroclaw

# Esegui ZeroClaw DENTRO la VM
limactl shell zeroclaw zeroclaw agent -m "istruzioni"

# Ferma VM
limactl stop zeroclaw
```

**Cosa e' isolato in Lima:**
- `~/.ssh` host: NON visibile (Lima genera chiavi proprie in `$LIMA_HOME/_config/`)
- `~/.aws`, `~/.gnupg`: NON visibili
- Portachiavi macOS: NON accessibile
- Rete: traffico passa per NAT della VM, separato dall'host
- Filesystem host: solo i mount esplicitamente dichiarati

Fonti: [Lima docs](https://lima-vm.io/docs/), [Safe Yolo Mode LLM Agents](https://www.metachris.dev/2026/02/safe-yolo-mode-running-llm-agents-with-libvirt-and-virsh/), [Northflank Sandbox Guide](https://northflank.com/blog/how-to-sandbox-ai-agents)

---

### 1.3 Opzione C: Docker Desktop (alternativa Lima)

Docker Sandboxes usa microVM per ogni container, con Docker daemon isolato. Permette agli agenti di costruire ed eseguire container senza toccare l'host.

**Pro**: DX migliore, integrazione VS Code, unica soluzione che permette all'agente di fare `docker build` isolato.
**Contro**: Richiede licenza Docker Desktop (non free per uso commerciale >250 dipendenti), consumo RAM piu' alto di Lima.

```bash
# Avvia ZeroClaw in Docker sandbox
docker run --rm \
  --network=none \
  -v /Volumes/MontereyT7/FLUXION:/workspace:rw \
  -v /tmp/zeroclaw-output:/output:rw \
  --security-opt no-new-privileges \
  --cap-drop ALL \
  zeroclaw-image zeroclaw agent -m "istruzioni"
```

Fonti: [Docker Sandboxes](https://docs.docker.com/ai/sandboxes), [Docker Blog](https://www.docker.com/blog/docker-sandboxes-run-claude-code-and-other-coding-agents-unsupervised-but-safely/), [Infralovers Sandboxing](https://www.infralovers.com/blog/2026-02-15-sandboxing-claude-code-macos/)

---

### 1.4 Tabella comparativa

| Soluzione | Isolamento | Overhead | Setup | macOS Big Sur | Rete controllabile |
|-----------|-----------|----------|-------|---------------|-------------------|
| `sandbox-exec` | Medio | Minimo | 10 min | Si | Si (con proxy) |
| Lima VM | Alto | Basso (QEMU) | 30 min | Si | Si (NAT) |
| Docker Desktop | Alto | Medio | 20 min | Si (Intel) | Si (`--network=none`) |
| UTM full VM | Massimo | Alto | 1 ora | Si | Si (Shared Network) |

**Raccomandazione pratica per ZeroClaw su MacBook Big Sur:**
- Uso quotidiano: `sandbox-exec` con profilo sopra → zero overhead, protezione adeguata
- Task ad alto rischio (web scraping, codice sconosciuto): Lima VM

---

## 2. Anonimato / Privacy Online (2026 Best Practice)

### Stack raccomandato 2026 per developer italiano

#### 2.1 VPN No-Log: Confronto Mullvad vs ProtonVPN vs IVPN

| Criterio | Mullvad | ProtonVPN | IVPN |
|----------|---------|-----------|------|
| **Account anonimo** | Si (numero random, no email) | No (email richiesta) | Si (no email opzionale) |
| **Pagamento anonimo** | Cash + Monero + Bitcoin | Bitcoin | Cash + Monero + Bitcoin |
| **Giurisdizione** | Svezia | Svizzera | Gibraltar |
| **Audit no-log** | Si (annuale) | Si (SOC 2 Type II) | Si |
| **Open source client** | Si | Si | Si |
| **Prezzo** | €5/mese flat | Free tier / €4+ | €2+ |
| **Server fleet** | ~800 | ~9000 | ~100 |
| **Velocita'** | Alta | Molto alta | Media |
| **Tor-over-VPN** | No | Si (Tor servers) | No |
| **Classificazione Privacy Guides** | Raccomandato | Raccomandato | Raccomandato |

**Vincitore per anonimato massimo**: **Mullvad** — unico che non richiede nemmeno un'email, accetta cash in busta per posta, e usa numeri account casuali.

**Vincitore per feature/prezzo**: **ProtonVPN** — SOC 2 Type II, Secure Core (multi-hop), Tor-over-VPN, free tier.

Per un developer italiano che vuole separare identita' reale da attivita' online (es. Fluxion/LemonSqueezy): **Mullvad** e' la scelta corretta.

Fonti: [Privacy Guides VPN](https://www.privacyguides.org/en/vpn/), [Mullvad vs ProtonVPN CyberInsider](https://cyberinsider.com/vpn/comparison/mullvad-vs-proton-vpn/), [Best No-Log VPN 2026](https://tegant.com/articles/best-no-log-vpn/)

---

#### 2.2 DNS over HTTPS + DNS Leak Prevention

**Setup macOS nativo (Big Sur/Monterey)**:

macOS Big Sur+ supporta profili DoH via `.mobileconfig`. Il metodo piu' semplice:

```bash
# Installa profilo DoH Mullvad (se usi Mullvad VPN)
# Scarica da: https://mullvad.net/en/help/dns-over-https-and-dns-over-tls
# Vai in System Settings > Privacy & Security > Profiles > install

# Alternativa: cloudflared locale
brew install cloudflare/cloudflare/cloudflared
cloudflared service install
# Poi imposta DNS manuale su 127.0.0.1 in Network Settings
```

**Verifica DNS leak:**
```bash
# Test da terminale
dig +short whoami.akamai.net
# Verifica su: https://www.dnsleaktest.com
```

**Repository profili DoH per macOS/iOS:**
- [paulmillr/encrypted-dns](https://github.com/paulmillr/encrypted-dns) — profili pronti per Mullvad, Cloudflare, AdGuard

**Con VPN attiva**: il DNS viene gestito automaticamente dal client VPN. Il rischio di DNS leak e' principalmente quando si usano tool di sistema che bypassano il tunnel (es. `nslookup` su macOS Big Sur).

Fonti: [Mullvad DoH](https://mullvad.net/en/help/dns-over-https-and-dns-over-tls), [Coronium DNS Leak Guide](https://www.coronium.io/blog/dns-leak-detection-prevention-guide-2025)

---

#### 2.3 Browser Fingerprinting Protection

| Browser | Fingerprint | Complessita' setup | Raccomandato per |
|---------|-------------|-------------------|-----------------|
| **Brave** | Randomizzazione valori | Zero (default) | Uso quotidiano, non tecnici |
| **Firefox + arkenfox** | Normalizzazione (blending) | Media (user.js) | Developer attenti |
| **Mullvad Browser** | Blending massimo (come Tor) | Bassa | Massima anonimita' |
| **Tor Browser** | Massima protezione | Zero | Attivita' sensibili |

**Note importanti 2026:**
- Brave **randomizza** i valori → potenzialmente piu' unico (ma piu' difficile da linkare tra sessioni)
- arkenfox **normalizza** → ti fa sembrare come altri utenti arkenfox (crowd hiding)
- Mullvad Browser e Tor Browser: unica strategia veramente efficace contro fingerprinting avanzato perche' si tenta di sembrare **identico** a migliaia di altri utenti
- I browser Chrome-based hanno superficie di fingerprinting molto piu' ampia di Firefox/Gecko

**Setup pratico per developer:**
- Browser 1 (lavoro Fluxion/identita' reale): Firefox + arkenfox user.js
- Browser 2 (acquisti anonimi, ricerca sensibile): Mullvad Browser o Brave con profili separati
- Browser 3 (massima anonimita'): Tor Browser

Fonti: [Privacy Guides Desktop Browsers](https://www.privacyguides.org/en/desktop-browsers/), [Brave Fingerprinting Wiki](https://github.com/brave/brave-browser/wiki/Fingerprinting-Protections), [Brside Fingerprint Test](https://www.brside.com/blog/brave-firefox-safari-only-two-survived-this-fingerprinting-test)

---

#### 2.4 Separazione Identita' Digitale

**Struttura consigliata per developer italiano con progetto commerciale:**

```
Identita' A (Personale/reale)
├── Email: gmail/protonmail con nome reale
├── Browser: Firefox profilo "Personale"
├── Social: LinkedIn personale
└── IP: ISP normale / VPN opzionale

Identita' B (Fluxion/Professionale pubblica)
├── Email: alias SimpleLogin → casella Proton
├── Browser: Firefox profilo "Fluxion" (separato)
├── Social: LinkedIn professionale Fluxion
├── LemonSqueezy: account con P.IVA italiana (richiede vera identita'!)
└── IP: Mullvad VPN

Identita' C (Ricerca/Anonima)
├── Email: alias usa-e-getta Addy.io
├── Browser: Mullvad Browser o Tor
├── Payment: Monero → prepaid card
└── IP: Mullvad VPN o Tor
```

**Email alias - SimpleLogin vs Addy.io:**
- **SimpleLogin** (ora parte di Proton): integrazione Proton Mail nativa, interfaccia pulita, piani da €3/mese. Open source, self-hostable.
- **Addy.io**: open source, tier gratuito generoso, self-hostable. Preferito dalla community Privacy Guides per il free tier.
- Entrambi: forward email a casella reale, reply senza rivelare email reale.

**ATTENZIONE LemonSqueezy**: LemonSqueezy richiede verifica identita' obbligatoria per tutti i venditori (documento + conto bancario). Non e' possibile vendere in modo completamente anonimo. Tuttavia:
- L'identita' del venditore NON e' visibile ai compratori (LemonSqueezy agisce come MoR)
- Si puo' usare una P.IVA italiana (che e' pubblica per legge) senza esporre dati personali aggiuntivi
- Il collegamento tra nome reale e brand "Fluxion" e' inevitabile tramite LemonSqueezy

Fonti: [SimpleLogin](https://simplelogin.io/), [Addy.io](https://addy.io/), [Privacy Guides Email Aliasing](https://www.privacyguides.org/en/email-aliasing/), [LemonSqueezy Identity Verification](https://docs.lemonsqueezy.com/help/getting-started/verify-your-identity)

---

#### 2.5 macOS Privacy Hardening

**Little Snitch 6 (firewall applicativo):**

Little Snitch 6 e' lo strumento chiave per developer macOS. Caratteristiche principali:
- Regole per-applicazione (non solo per porta/IP)
- DNS encryption integrato
- Blocklists per tracker/telemetria
- Control Center nel menu bar
- Alert in tempo reale per ogni nuova connessione

**Configurazione rapida per ZeroClaw/Fluxion:**
1. Default: "Deny all incoming, ask for outgoing"
2. Crea regola: `zeroclaw` → allow solo `api.groq.com:443`
3. Crea regola: blocco `*.apple.com` per telemetria (eccetto update.apple.com)
4. Alternativa gratuita: **LuLu** (open source, Patrick Wardle) — stessa funzione, no blocklist

**IMPORTANTE su macOS Big Sur+**: Le app Apple (processo `trustd`, daemon di sistema) bypassano i firewall applicativi tramite Content Filter Extension Framework. Little Snitch e LuLu intercettano tutto il resto. E' un comportamento documentato/intenzionale di Apple.

**Hardening aggiuntivo macOS:**

```bash
# Disabilita Spotlight suggerimenti (invia ricerche a Apple)
defaults write com.apple.lookup.shared LookupSuggestionsDisabled -bool true

# Disabilita diagnostica e utilizzo
sudo defaults write /Library/Application\ Support/CrashReporter/DiagnosticMessagesHistory.plist AutoSubmit -bool false

# Disabilita Siri (se non usato)
defaults write com.apple.assistant.support 'Assistant Enabled' -bool false

# Verifica app con accesso microfono/webcam
# System Settings > Privacy & Security > Microphone/Camera
```

Fonti: [Little Snitch obdev.at](https://obdev.at/littlesnitch), [Arcjet DevContainers Little Snitch](https://blog.arcjet.com/devcontainers-little-snitch-macos-tcc-protecting-developer-laptops/), [IntelTechniques macOS 26](https://inteltechniques.com/blog/2026/01/05/macos-26-settings/)

---

#### 2.6 Pagamenti Anonimi (contesto Italia 2026)

**Monero (XMR):**
- Privacy nativa: nasconde mittente, destinatario E importo per default
- Legale in Italia (nessun ban specifico su Monero)
- Problema: pochissimi exchange italiani supportano XMR (KYC richiesto all'acquisto iniziale)
- Strategia: acquista BTC con P.IVA → converti in XMR su exchange decentralizzato (TradeOgre, Haveno)

**Carte prepagate anonime in Italia 2026:**
- PostePay anonima: limite €1000/anno, nessun KYC per importi bassi
- Hype: richiede documento ma spendibile con alias
- Carte Monero → prepaid: servizi come Cake Wallet permettono pagamento diretto con XMR

**Per tool/abbonamenti tech (non LemonSqueezy che richiede KYC):**
- Acquista gift card Amazon/Google con contanti → paga abbonamenti
- Usa Mullvad VPN (accetta contanti per posta) → nessuna traccia digitale

**Nota realistica**: la separazione totale identita' reale/commerciale e' difficile in Italia per via della normativa antiriciclaggio (AML) e PSD2. Ogni conto bancario/paypal richiede KYC. Il meglio raggiungibile e' **pseudonimato strutturato**, non anonimato assoluto.

Fonti: [Privacy Guides Payments](https://www.privacyguides.org/en/advanced/payments/), [Monero.org](https://www.getmonero.org/), [Anonymous Payment Methods 2026](https://cyberinsider.com/private-anonymous-payment-methods/)

---

### 2.7 Implementazione per Fluxion/LemonSqueezy

**Stack minimo raccomandato (ordine di priorita'):**

1. **Mullvad VPN** (~€5/mese, pagato con Monero o cash) — IP anonimizzato
2. **Firefox + arkenfox** per navigazione legata a Fluxion
3. **SimpleLogin** alias per email store (non rivela email personale)
4. **LuLu** (gratuito) o **Little Snitch** (€45 una tantum) per firewall app
5. **Profilo DoH** Mullvad installato su macOS
6. **Separazione browser** profili: Fluxion vs Personale vs Anonimo

**Non possibile**: LemonSqueezy richiede identita' reale → il brand "Fluxion" sara' inevitabilmente collegato alla P.IVA del developer. E' accettabile perche' LemonSqueezy e' MoR e non espone dati venditore ai clienti.

---

## 3. Anti-Context-Rot Workflow per Claude Code 2026

### Pattern raccomandato

Il problema principale: Claude Code ha 200k token di contesto ma si consuma rapidamente. Dopo ~30 minuti di lavoro intensivo, il contesto e' pieno e la qualita' delle risposte degrada.

#### 3.1 Architettura Memory a 3 Livelli

```
Livello 1 — CLAUDE.md (sempre in contesto, caricato all'avvio)
├── Regole critiche (immutabili)
├── Stack tecnologico
├── Comandi rapidi
└── Stato sprint attivo (max 50 righe)

Livello 2 — MEMORY.md (~/.claude/projects/.../memory/)
├── Stato sessione corrente
├── Decisioni architetturali recenti
├── Task board prioritizzato
└── Lezioni apprese (lessons.md)

Livello 3 — HANDOFF.md (snapshot punto-nel-tempo)
├── Cosa e' stato fatto in questa sessione
├── Stato esatto dei file modificati
├── Next step immediato (1-2 azioni)
└── Blockers identificati
```

**Regola**: CLAUDE.md e' versionato su git (stable). MEMORY.md e' auto-aggiornato dall'agente. HANDOFF.md e' temporaneo (overwrite ad ogni sessione).

---

#### 3.2 Soglie /compact e /clear

Basato su ricerca 2026:

| Soglia contesto | Azione | Comando |
|----------------|--------|---------|
| < 60% | Continua normalmente | — |
| 60-70% | Compatta se task correlati | `/compact Focus su [area]` |
| 70-80% | Compatta obbligatoriamente | `/compact` |
| > 80% | Nuova sessione con HANDOFF | `/clear` + nuova sessione |
| Task diverso | Sempre clear | `/clear` |

**Come usare /compact con istruzioni:**
```
/compact Focus sulle modifiche a booking_state_machine.py e i test relativi.
         Preserva: stato FSM 23 stati, config Groq, path iMac.
         Rimuovi: output dettagliato dei test gia' passati.
```

Fonti: [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices), [SFEIR Context Tips](https://institute.sfeir.com/en/claude-code/claude-code-context-management/tips/), [Medium: Clear vs Compact](https://medium.com/@nustianrwp/managing-your-context-window-clear-vs-compact-in-claude-code-8b00ae2ed91b)

---

#### 3.3 Subagent Delegation — Protezione Contesto Principale

I subagenti (Claude Code custom agents) girano in **contesti isolati** — il loro consumo di token NON impatta il contesto principale.

**Pattern corretto (file-based coordination):**

```markdown
# In CLAUDE.md o prompt:
"Usa un subagente per esplorare X, poi riportami solo il summary in un file."
```

**ATTENZIONE**: `TaskOutput` ritorna l'intero transcript del subagente → puo' aggiungere 70k+ token al contesto principale. Usare sempre **file-based output**:

```python
# Il subagente scrive risultati qui:
.claude/cache/agents/research-output.md

# Il main agent legge solo il summary:
Read(".claude/cache/agents/research-output.md")
```

**Regola pratica**: task di ricerca, esplorazione codebase, analisi multi-file → delegare a subagenti. Task che richiedono modifiche dirette → fare nel contesto principale.

Fonti: [Claude Code Sub-agents Docs](https://code.claude.com/docs/en/sub-agents), [PubNub Subagents Best Practices](https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/), [Continuous Claude v3](https://github.com/parcadei/Continuous-Claude-v3)

---

#### 3.4 HANDOFF.md — Struttura Ottimale

Template basato su best practice 2026 (SFEIR + Continuous-Claude-v3):

```markdown
# HANDOFF - [DATA] [ORA]
> Generato: fine sessione [N]
> Prossima sessione: leggi questo file PRIMA di fare qualsiasi cosa

## Stato Corrente
- Branch: master | Ultimo commit: [HASH] [MSG]
- File modificati in questa sessione: [lista]
- Test passati: [N/M] | Blockers: [lista]

## Cosa e' stato fatto
1. [Azione concreta 1] → [risultato verificato]
2. [Azione concreta 2] → [risultato verificato]

## Next Step IMMEDIATO (1 azione)
> [Azione specifica con file e comando esatto]
> Esempio: "Esegui test T1 su iMac: python3 t1_live_test.py"

## Contesto Critico (NON perdere)
- [Decisione architetturale chiave]
- [Configurazione speciale attiva]
- [Warning / gotcha scoperto]

## File Chiave Toccati
| File | Stato | Note |
|------|-------|------|
| voice-agent/main.py | Modificato | Bug fix RIFF header |
| src-tauri/Cargo.toml | Invariato | — |
```

**Quando scrivere HANDOFF.md:**
- Prima di `/clear`
- Prima di chiudere Claude Code
- Dopo ogni commit significativo
- Quando context > 70%

---

#### 3.5 Hooks per Auto-aggiornamento Memory

Continuous-Claude-v3 implementa 30 hook sugli eventi lifecycle di Claude Code. I piu' utili per anti-context-rot:

| Hook Event | Azione | Implementazione |
|-----------|--------|-----------------|
| `PreCompact` | Salva stato prima di compact | Script che scrive HANDOFF.md |
| `Stop` | Estrae learnings, crea handoff | Script che aggiorna MEMORY.md |
| `SubagentStop` | Coordina output subagenti | Scrive in `.claude/cache/agents/` |
| `PostToolUse` | Traccia file modificati | Appende a `.claude/session-log.md` |

**Hook pratico per Fluxion** — `.claude/hooks/pre-compact.sh`:

```bash
#!/bin/bash
# Salva stato sessione prima di compact
TIMESTAMP=$(date +%Y%m%d-%H%M)
HANDOFF_FILE="/Volumes/MontereyT7/FLUXION/HANDOFF.md"

echo "# HANDOFF - Auto-saved pre-compact $TIMESTAMP" > "$HANDOFF_FILE"
echo "## Git Status" >> "$HANDOFF_FILE"
git -C /Volumes/MontereyT7/FLUXION status --short >> "$HANDOFF_FILE"
echo "## Last Commit" >> "$HANDOFF_FILE"
git -C /Volumes/MontereyT7/FLUXION log --oneline -3 >> "$HANDOFF_FILE"
echo "## Hook: context was near limit, compact triggered" >> "$HANDOFF_FILE"
```

**Registrazione hook in `.claude/settings.json`:**

```json
{
  "hooks": {
    "PreCompact": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash /Volumes/MontereyT7/FLUXION/.claude/hooks/pre-compact.sh"
          }
        ]
      }
    ]
  }
}
```

Fonti: [Claude Code Hooks Mastery](https://github.com/disler/claude-code-hooks-mastery), [Continuous Claude v3](https://github.com/parcadei/Continuous-Claude-v3), [Claude Code Release Notes Feb 2026](https://releasebot.io/updates/anthropic/claude-code)

---

#### 3.6 Workflow Multi-sessione con Git Checkpoint

**Pattern "Sprint-Commit-Handoff"** (raccomandato per Fluxion):

```
Sessione N:
  1. Leggi HANDOFF.md + MEMORY.md (30s)
  2. Lavora su task specifico (max 45 min o 70% context)
  3. Commit parziale con stato chiaro: "wip: [task] - [% completato]"
  4. Scrivi/aggiorna HANDOFF.md
  5. /clear o chiudi sessione

Sessione N+1:
  1. Leggi HANDOFF.md → context immediato
  2. Continua da next step esatto
```

**Commit come checkpoint di contesto:**

```bash
# Commit checkpoint (non deve essere "perfetto")
git add voice-agent/src/booking_state_machine.py
git commit -m "wip: fix handle_api_error - 80% done, manca test E2E stato RETRY"

# Il messaggio del commit e' parte del contesto per la prossima sessione
git log --oneline -5  # leggi all'inizio della prossima sessione
```

---

### 3.7 Regole da Aggiungere a CLAUDE.md

```markdown
## Anti-Context-Rot Rules (2026)

### Soglie contesto
- < 60%: lavora normalmente
- 60-70%: valuta /compact se task correlati
- > 70%: /compact OBBLIGATORIO prima di continuare
- Task diverso: /clear SEMPRE

### /compact con focus
- Usa SEMPRE: `/compact Focus su [area specifica]. Preserva: [X,Y,Z].`
- Non usare compact senza istruzioni (perde contesto critico)

### Subagenti
- Ricerca/esplorazione → delega subagente
- Output subagente → sempre su file .claude/cache/agents/, MAI TaskOutput diretto
- Subagenti compattano da soli, non impattano contesto principale

### HANDOFF
- Scrivi HANDOFF.md PRIMA di /clear o chiusura
- Struttura: Stato | Fatto | Next Step IMMEDIATO | Contesto Critico
- Leggi HANDOFF.md come PRIMA cosa ogni nuova sessione

### Git come checkpoint
- Commit parziali con "wip: [task] - [stato]" sono accettabili
- Il messaggio commit e' memoria per la prossima sessione
- Dopo ogni feature: commit + push + aggiorna MEMORY.md
```

---

## Summary Esecutivo

| Topic | Soluzione scelta | Priorita' implementazione |
|-------|-----------------|--------------------------|
| ZeroClaw sandbox | `sandbox-exec` quotidiano + Lima per task rischiosi | Media (fai ora) |
| VPN anonima | Mullvad (cash/Monero) | Alta |
| DNS | Profilo DoH Mullvad su macOS | Alta |
| Browser | Firefox arkenfox (lavoro) + Mullvad Browser (anonimo) | Media |
| Email alias | SimpleLogin via Proton per Fluxion | Alta (prima di LemonSqueezy) |
| Firewall app | LuLu (free) o Little Snitch | Media |
| Pagamenti | PostePay anonima + Monero dove accettato | Bassa |
| Context-rot | /compact a 70% + HANDOFF.md + subagenti file-based | Alta (applica subito) |
| Hooks Claude | pre-compact.sh → auto-save HANDOFF | Bassa (setup una tantum) |

---

*Fonti principali usate in questa ricerca:*
- [Northflank: How to sandbox AI agents 2026](https://northflank.com/blog/how-to-sandbox-ai-agents)
- [Infralovers: Sandboxing Claude Code on macOS](https://www.infralovers.com/blog/2026-02-15-sandboxing-claude-code-macos/)
- [agent-seatbelt-sandbox (GitHub)](https://github.com/michaelneale/agent-seatbelt-sandbox)
- [claude-code-sandbox (GitHub)](https://github.com/neko-kai/claude-code-sandbox)
- [Privacy Guides VPN](https://www.privacyguides.org/en/vpn/)
- [Privacy Guides Desktop Browsers](https://www.privacyguides.org/en/desktop-browsers/)
- [Privacy Guides Email Aliasing](https://www.privacyguides.org/en/email-aliasing/)
- [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)
- [Continuous-Claude-v3 (GitHub)](https://github.com/parcadei/Continuous-Claude-v3)
- [Claude Code Sub-agents Docs](https://code.claude.com/docs/en/sub-agents)
- [Lima VM](https://lima-vm.io/)
- [Little Snitch](https://obdev.at/littlesnitch)
- [Mullvad DoH](https://mullvad.net/en/help/dns-over-https-and-dns-over-tls)
