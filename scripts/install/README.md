# Fluxion Post-Install Scripts (S184 α.2)

Script di setup post-installazione per ridurre frizione cold-traffic
(Gatekeeper macOS, SmartScreen Windows, falsi positivi AV).

## File

| File | OS | Scopo |
|------|----|-------|
| `setup-mac.command` | macOS | Rimuove `com.apple.quarantine` xattr da `/Applications/Fluxion.app` |
| `setup-win.bat` | Windows | Add Defender exclusion + remove Mark-of-the-Web + firewall rule loopback |

## Distribuzione

### macOS — bundle nel DMG
1. Build PKG/DMG via `npm run tauri build` su iMac (vedi `scripts/build-on-imac.sh`)
2. Aggiungi `setup-mac.command` dentro al DMG accanto a `Fluxion.app`:
   ```bash
   # Pseudo-step (da automatizzare in build-on-imac.sh):
   hdiutil convert "Fluxion_1.0.1_x64.dmg" -format UDRW -o "tmp.dmg"
   hdiutil attach "tmp.dmg" -mountpoint /Volumes/Fluxion-RW
   cp scripts/install/setup-mac.command /Volumes/Fluxion-RW/
   chmod +x /Volumes/Fluxion-RW/setup-mac.command
   hdiutil detach /Volumes/Fluxion-RW
   hdiutil convert "tmp.dmg" -format UDZO -o "Fluxion_1.0.1_x64.dmg"
   ```
3. Utente: monta DMG → drag Fluxion.app → /Applications → double-click `setup-mac.command`

### Windows — distribuzione separata
1. Build MSI via GitHub Actions Win runner (vedi S183-bis pipeline)
2. Pubblica `setup-win.bat` come asset GitHub Release accanto al MSI
3. Documenta in landing/come-installare.html: istruzioni
   - Installa MSI
   - Click destro su `setup-win.bat` → "Esegui come amministratore"

## Logging

| Script | Log path |
|--------|----------|
| `setup-mac.command` | `~/Library/Logs/Fluxion/setup-mac.log` |
| `setup-win.bat` | `%LOCALAPPDATA%\Fluxion\Logs\setup-win.log` |

## Test

### macOS — locale
```bash
# Su Mac con Fluxion.app installato:
./scripts/install/setup-mac.command
# Verifica che xattr lista NON contenga com.apple.quarantine:
xattr /Applications/Fluxion.app
```

### Windows — VM UTM iMac (S184 α.3)
```cmd
:: Su Win11 VM con Fluxion installato:
:: Click destro setup-win.bat -> Esegui come amministratore
:: Verifica esclusione Defender:
powershell -Command "Get-MpPreference | Select-Object -ExpandProperty ExclusionPath"
```

## Rationale

**Perché non firmiamo i binari?**
ZERO COSTI guardrail (CLAUDE.md): Apple Developer ID = €99/anno, Windows EV cert = €300+/anno.
Strategia ad-hoc signing + post-install scripts mantiene gratuito mantenendo UX accettabile.

Detail in `.claude/rules/architecture-distribution.md`.
