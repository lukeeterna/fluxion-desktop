; ═══════════════════════════════════════════════════════════════════
; FLUXION — NSIS Installer Hooks (S184 α.3.3-C)
; ═══════════════════════════════════════════════════════════════════
;
; Pre-install checks per ridurre i bug-segnalazione su Win10 fresh:
;   1. Windows version >= 10 (build 10240+)
;   2. WebView2 runtime presente (warning soft — verrà installato dal
;      bootstrapper embedded di Tauri se mancante)
;   3. Architettura x64 (no Arm Win)
;
; Tutti i check producono messaggi parlanti in italiano (target PMI).
;
; Reference Tauri 2.x macro overrides (NsisInstaller):
;   https://v2.tauri.app/distribute/windows-installer/#installer-hooks
; ═══════════════════════════════════════════════════════════════════

; ─── Pre-install hook (called BEFORE files are copied) ─────────────
!macro NSIS_HOOK_PREINSTALL
  ; ── 1. Windows version check (Win10+ = 10.0 build 10240+) ────────
  ${If} ${AtLeastWin10}
    DetailPrint "FLUXION pre-flight: Windows 10+ rilevato (OK)"
  ${Else}
    MessageBox MB_OK|MB_ICONSTOP \
      "FLUXION richiede Windows 10 o superiore.$\r$\n$\r$\nIl sistema rilevato non è supportato.$\r$\nPer assistenza: fluxion.gestionale@gmail.com"
    Abort "Windows version non supportata"
  ${EndIf}

  ; ── 2. WebView2 runtime detection (info-only, soft check) ────────
  ; Cerca chiave registro Microsoft Edge WebView2 Runtime (HKLM o HKCU)
  ; Se mancante, l'embedBootstrapper di Tauri lo installerà comunque.
  ReadRegStr $0 HKLM "SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" "pv"
  ${If} $0 == ""
    ReadRegStr $0 HKCU "Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" "pv"
  ${EndIf}
  ${If} $0 == ""
    DetailPrint "FLUXION pre-flight: WebView2 NON rilevato — verrà installato automaticamente dall'installer."
  ${Else}
    DetailPrint "FLUXION pre-flight: WebView2 v$0 rilevato (OK)"
  ${EndIf}

  ; ── 3. Architecture sanity ───────────────────────────────────────
  ${If} ${RunningX64}
    DetailPrint "FLUXION pre-flight: architettura x64 rilevata (OK)"
  ${Else}
    MessageBox MB_OK|MB_ICONSTOP \
      "FLUXION supporta solo Windows 64-bit (x64).$\r$\n$\r$\nIl sistema rilevato è 32-bit o ARM, non supportato.$\r$\nPer assistenza: fluxion.gestionale@gmail.com"
    Abort "Architettura non supportata"
  ${EndIf}

  ; ── 4. Disk space sanity (almeno 1GB liberi su drive target) ────
  ; FLUXION + voice-agent bundle = ~520MB; lasciamo margine.
  ${GetRoot} "$INSTDIR" $1
  ${DriveSpace} "$1\" "/D=F /S=B" $2
  ; $2 = bytes free (string). Confronto numerico via System::Int64Op.
  System::Int64Op $2 / 1073741824
  Pop $3
  ${If} $3 < 1
    MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
      "Spazio disco basso sul drive $1 (meno di 1GB liberi).$\r$\n$\r$\nFLUXION + Sara richiedono ~600MB. Continui comunque?" \
      IDOK SkipDiskCheck
    Abort "Spazio disco insufficiente"
    SkipDiskCheck:
  ${EndIf}
!macroend

; ─── Post-install hook (after files copied, before "Finish") ───────
!macro NSIS_HOOK_POSTINSTALL
  DetailPrint "FLUXION installato. Post-install setup: vedi setup-win.bat per esclusione Defender (consigliato)."
!macroend

; ─── Pre-uninstall hook ────────────────────────────────────────────
!macro NSIS_HOOK_PREUNINSTALL
  DetailPrint "Disinstallazione FLUXION — i tuoi dati cliente (database SQLite) NON verranno eliminati."
  DetailPrint "Trovi i dati in: %LOCALAPPDATA%\com.fluxion.desktop"
!macroend

; ─── Post-uninstall hook ───────────────────────────────────────────
!macro NSIS_HOOK_POSTUNINSTALL
  DetailPrint "FLUXION disinstallato. Per ripristinare i dati, reinstalla la stessa versione: il database verrà rilevato automaticamente."
!macroend
