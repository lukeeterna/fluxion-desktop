@echo off
REM ═══════════════════════════════════════════════════════════════════
REM FLUXION - Setup Windows post-installazione (S184 alpha.2)
REM Aggiunge esclusione Defender + rimuove Mark-of-the-Web da Fluxion.exe
REM Distribuito accanto al MSI sul GitHub Release
REM ═══════════════════════════════════════════════════════════════════

setlocal EnableDelayedExpansion

set "INSTALL_PATH=%ProgramFiles%\Fluxion"
set "LOG_DIR=%LOCALAPPDATA%\Fluxion\Logs"
set "LOG_FILE=%LOG_DIR%\setup-win.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>&1

echo ═══════════════════════════════════════════════════════════════ >> "%LOG_FILE%"
echo   FLUXION - Setup Windows %DATE% %TIME% >> "%LOG_FILE%"
echo ═══════════════════════════════════════════════════════════════ >> "%LOG_FILE%"

echo ═══════════════════════════════════════════════════════════════
echo   FLUXION - Setup Windows post-installazione
echo ═══════════════════════════════════════════════════════════════
echo.

REM === 1. Verifica privilegi amministratore ===
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Questo script richiede privilegi amministratore.
    echo Riavvio con UAC...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b 0
)

REM === 2. Verifica installazione Fluxion ===
if not exist "%INSTALL_PATH%\Fluxion.exe" (
    echo [ERRORE] Fluxion.exe NON trovato in:
    echo   %INSTALL_PATH%
    echo.
    echo Prima di lanciare questo script:
    echo   1. Esegui Fluxion_1.0.1_x64.msi
    echo   2. Completa l'installazione guidata
    echo   3. Torna qui e rilancia setup-win.bat come amministratore
    echo.
    pause
    exit /b 1
)

echo [OK] Fluxion.exe trovato in %INSTALL_PATH%
echo.

REM === 3. Aggiungi esclusione Microsoft Defender ===
echo Aggiunta esclusione Microsoft Defender per cartella Fluxion...
powershell -ExecutionPolicy Bypass -Command "try { Add-MpPreference -ExclusionPath '%INSTALL_PATH%' -ErrorAction Stop; Write-Host '[OK] Esclusione Defender aggiunta' } catch { Write-Host '[WARN] Impossibile aggiungere esclusione Defender:' $_.Exception.Message }" >> "%LOG_FILE%" 2>&1
powershell -ExecutionPolicy Bypass -Command "try { Add-MpPreference -ExclusionPath '%INSTALL_PATH%' -ErrorAction Stop; Write-Host '[OK] Esclusione Defender aggiunta' } catch { Write-Host '[WARN] Defender exclusion failed - probabilmente Defender disabilitato o gestito da policy aziendale' }"
echo.

REM === 4. Rimuovi Mark-of-the-Web (sblocca SmartScreen permanentemente) ===
echo Rimozione Mark-of-the-Web da binari Fluxion...
powershell -ExecutionPolicy Bypass -Command "Get-ChildItem -Path '%INSTALL_PATH%' -Recurse -Include *.exe,*.dll | Unblock-File; Write-Host '[OK] Mark-of-the-Web rimosso da exe/dll'" >> "%LOG_FILE%" 2>&1
powershell -ExecutionPolicy Bypass -Command "Get-ChildItem -Path '%INSTALL_PATH%' -Recurse -Include *.exe,*.dll | Unblock-File; Write-Host '[OK] Mark-of-the-Web rimosso da exe/dll'"
echo.

REM === 5. Apri firewall per voice-agent (porta 3002 loopback only) ===
echo Configurazione firewall Windows per voice-agent (loopback)...
powershell -ExecutionPolicy Bypass -Command "try { New-NetFirewallRule -DisplayName 'Fluxion Voice Agent (loopback)' -Direction Inbound -Program '%INSTALL_PATH%\voice-agent.exe' -Action Allow -Profile Private,Domain -ErrorAction Stop; Write-Host '[OK] Regola firewall creata' } catch { Write-Host '[WARN] Regola firewall gia esistente o creazione fallita' }" >> "%LOG_FILE%" 2>&1
powershell -ExecutionPolicy Bypass -Command "try { New-NetFirewallRule -DisplayName 'Fluxion Voice Agent (loopback)' -Direction Inbound -Program '%INSTALL_PATH%\voice-agent.exe' -Action Allow -Profile Private,Domain -ErrorAction Stop; Write-Host '[OK] Regola firewall creata' } catch { Write-Host '[INFO] Regola firewall gia esistente' }"
echo.

echo ═══════════════════════════════════════════════════════════════
echo   [OK] SETUP COMPLETATO
echo ═══════════════════════════════════════════════════════════════
echo.
echo   Ora puoi avviare Fluxion da:
echo     - Menu Start ^> Fluxion
echo     - Desktop (icona Fluxion)
echo.
echo   Log salvato in: %LOG_FILE%
echo.
echo   Se SmartScreen mostra ancora avvisi al primo avvio:
echo     1. Click su "Ulteriori informazioni"
echo     2. Click su "Esegui comunque"
echo     (Una sola volta per installazione)
echo.
pause
exit /b 0
