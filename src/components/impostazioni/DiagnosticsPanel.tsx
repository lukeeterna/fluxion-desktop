// ═══════════════════════════════════════════════════════════════════
// FLUXION - Diagnostics Panel (Fase 4 - Fluxion Care)
// UI per diagnostica, backup, export bundle, remote assist
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState } from 'react';
import { save, ask, message } from '@tauri-apps/plugin-dialog';
import { exit } from '@tauri-apps/plugin-process';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import {
  useDiagnosticsInfo,
  useBackups,
  useRemoteAssistInstructions,
  useBackupDatabase,
  useRestoreDatabase,
  useExportSupportBundle,
  useDeleteBackup,
  useExportClientiCsv,
  useExportAppuntamentiCsv,
} from '@/hooks/use-support';

export const DiagnosticsPanel: FC = () => {
  const { data: diagnostics, isLoading: loadingDiagnostics, refetch: refetchDiagnostics } = useDiagnosticsInfo();
  const { data: backups, isLoading: loadingBackups } = useBackups();
  const { data: remoteAssist } = useRemoteAssistInstructions();

  const backupMutation = useBackupDatabase();
  const restoreMutation = useRestoreDatabase();
  const exportBundleMutation = useExportSupportBundle();
  const deleteMutation = useDeleteBackup();
  const exportClientiCsv = useExportClientiCsv();
  const exportAppuntamentiCsv = useExportAppuntamentiCsv();

  const [includeDbInBundle, setIncludeDbInBundle] = useState(true);

  // ─────────────────────────────────────────────────────────────────
  // Handlers
  // ─────────────────────────────────────────────────────────────────

  const handleBackup = async () => {
    try {
      await backupMutation.mutateAsync();
      await message('Backup completato con successo!', { title: 'Fluxion', kind: 'info' });
    } catch (error) {
      await message(`Errore backup: ${error}`, { title: 'Errore', kind: 'error' });
    }
  };

  const handleRestore = async (backupPath: string) => {
    const confirmed = await ask(
      'ATTENZIONE: Il ripristino sovrascriverà il database attuale.\n\n' +
      'Una copia di sicurezza verrà salvata automaticamente.\n\n' +
      'L\'applicazione verrà CHIUSA dopo il ripristino.\n' +
      'Dovrai riaprirla manualmente.\n\n' +
      'Continuare?',
      { title: 'Conferma Ripristino', kind: 'warning' }
    );
    if (!confirmed) return;

    try {
      await restoreMutation.mutateAsync(backupPath);
      await message(
        'Database ripristinato con successo!\n\n' +
        'L\'applicazione si chiuderà ora.\n' +
        'Riapri FLUXION per caricare i nuovi dati.',
        { title: 'Ripristino Completato', kind: 'info' }
      );
      // Exit app cleanly - user must reopen manually
      // Using exit() instead of relaunch() to avoid crash due to SQLite pool state
      await exit(0);
    } catch (error) {
      await message(`Errore ripristino: ${error}`, { title: 'Errore', kind: 'error' });
    }
  };

  const handleDeleteBackup = async (backupPath: string, filename: string) => {
    // ADMIN ONLY - doppia conferma
    const confirmed = await ask(
      `⚠️ OPERAZIONE IRREVERSIBILE ⚠️\n\n` +
      `Stai per eliminare definitivamente:\n${filename}\n\n` +
      `Questa azione NON può essere annullata.\n\n` +
      `Solo l'AMMINISTRATORE può eliminare i backup.\n\n` +
      `Sei sicuro di voler procedere?`,
      { title: 'Conferma Eliminazione (ADMIN)', kind: 'warning' }
    );
    if (!confirmed) return;

    try {
      const result = await deleteMutation.mutateAsync(backupPath);
      await message(result, { title: 'Backup Eliminato', kind: 'info' });
    } catch (error) {
      await message(`Errore eliminazione: ${error}`, { title: 'Errore', kind: 'error' });
    }
  };

  const handleExportBundle = async () => {
    try {
      const outputPath = await save({
        title: 'Salva Support Bundle',
        defaultPath: `fluxion_support_${new Date().toISOString().slice(0, 10)}.zip`,
        filters: [{ name: 'ZIP Archive', extensions: ['zip'] }],
      });

      if (!outputPath) return;

      const result = await exportBundleMutation.mutateAsync({
        includeDatabase: includeDbInBundle,
        outputPath,
      });

      await message(
        `Support Bundle creato!\n\n` +
        `Percorso: ${result.path}\n` +
        `Dimensione: ${result.size_human}\n` +
        `Contenuto: ${result.contents.join(', ')}`,
        { title: 'Export Completato', kind: 'info' }
      );
    } catch (error) {
      await message(`Errore export bundle: ${error}`, { title: 'Errore', kind: 'error' });
    }
  };

  const handleExportCsv = async (type: 'clienti' | 'appuntamenti') => {
    const today = new Date().toISOString().slice(0, 10);
    const defaultName = type === 'clienti'
      ? `Fluxion_Clienti_${today}.csv`
      : `Fluxion_Appuntamenti_${today}.csv`;

    const outputPath = await save({
      title: `Esporta ${type === 'clienti' ? 'Clienti' : 'Appuntamenti'} CSV`,
      defaultPath: defaultName,
      filters: [{ name: 'CSV', extensions: ['csv'] }],
    });
    if (!outputPath) return;

    try {
      const result = type === 'clienti'
        ? await exportClientiCsv.mutateAsync(outputPath)
        : await exportAppuntamentiCsv.mutateAsync(outputPath);
      await message(result, { title: 'Export completato', kind: 'info' });
    } catch (error) {
      await message(`Errore export CSV: ${error}`, { title: 'Errore', kind: 'error' });
    }
  };

  const handleOpenRemoteAssist = async () => {
    if (!remoteAssist?.button_action) return;

    // Copia istruzioni negli appunti
    await window.navigator.clipboard.writeText(remoteAssist.steps.join('\n'));

    if (remoteAssist.os === 'macos') {
      // Apri pagina download AnyDesk
      window.open(remoteAssist.button_action, '_blank');
      await message(
        'Istruzioni copiate negli appunti!\n\n' +
        'Scarica AnyDesk dal link aperto nel browser.\n' +
        'Dopo l\'installazione, comunica il tuo ID a 9 cifre al supporto.',
        { title: 'Assistenza Remota', kind: 'info' }
      );
    } else if (remoteAssist.os === 'windows') {
      await message(
        'Istruzioni copiate negli appunti!\n\n' +
        'Premi Win + Ctrl + Q per aprire Assistenza Rapida',
        { title: 'Assistenza Remota', kind: 'info' }
      );
    }
  };

  // ─────────────────────────────────────────────────────────────────
  // Render
  // ─────────────────────────────────────────────────────────────────

  // F13: alert se backup mancante o > 7 giorni
  const backupAge = diagnostics?.days_since_last_backup;
  const showBackupAlert = !loadingDiagnostics && (backupAge === null || backupAge === undefined || backupAge > 7);

  return (
    <div className="space-y-6">
      {/* ─────────────────────────────────────────────────────────────── */}
      {/* F13: Banner alert backup */}
      {/* ─────────────────────────────────────────────────────────────── */}
      {showBackupAlert && (
        <Card className="p-4 bg-amber-950/30 border-amber-500/40">
          <div className="flex items-start gap-3">
            <span className="text-xl shrink-0">⚠️</span>
            <div className="flex-1">
              <p className="text-amber-300 font-medium text-sm">
                {backupAge === null || backupAge === undefined
                  ? 'Nessun backup trovato — i dati non sono protetti'
                  : `Ultimo backup ${backupAge} giorni fa — si consiglia un backup settimanale`}
              </p>
              <p className="text-slate-400 text-xs mt-1">
                Crea un backup ora per proteggere clienti, appuntamenti e impostazioni.
              </p>
            </div>
            <Button
              size="sm"
              onClick={handleBackup}
              disabled={backupMutation.isPending}
              className="bg-amber-600 hover:bg-amber-700 text-white shrink-0"
            >
              {backupMutation.isPending ? 'Backup...' : 'Backup ora'}
            </Button>
          </div>
        </Card>
      )}

      {/* ─────────────────────────────────────────────────────────────── */}
      {/* SEZIONE: Informazioni Sistema */}
      {/* ─────────────────────────────────────────────────────────────── */}
      <Card className="p-6 bg-slate-900 border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <span className="text-2xl">🔍</span> Diagnostica Sistema
            </h2>
            <p className="text-sm text-slate-400">Informazioni su app, sistema e database</p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetchDiagnostics()}
            className="text-cyan-400 border-cyan-500/30 hover:bg-cyan-500/10"
          >
            ↻ Aggiorna
          </Button>
        </div>

        {loadingDiagnostics ? (
          <p className="text-slate-400">Caricamento diagnostica...</p>
        ) : diagnostics ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* App Info */}
            <div className="p-4 rounded-lg bg-slate-950 border border-slate-800">
              <p className="text-xs text-slate-500 uppercase mb-1">Applicazione</p>
              <p className="text-white font-semibold">
                {diagnostics.app_name} v{diagnostics.app_version}
              </p>
            </div>

            {/* OS Info */}
            <div className="p-4 rounded-lg bg-slate-950 border border-slate-800">
              <p className="text-xs text-slate-500 uppercase mb-1">Sistema Operativo</p>
              <p className="text-white font-semibold">
                {diagnostics.os_type} {diagnostics.os_version}
              </p>
              <p className="text-xs text-slate-400">{diagnostics.arch}</p>
            </div>

            {/* DB Size */}
            <div className="p-4 rounded-lg bg-slate-950 border border-slate-800">
              <p className="text-xs text-slate-500 uppercase mb-1">Database</p>
              <p className="text-white font-semibold">{diagnostics.db_size_human}</p>
              <p className="text-xs text-slate-400">{diagnostics.tables_count} tabelle</p>
            </div>

            {/* Clienti Count */}
            <div className="p-4 rounded-lg bg-slate-950 border border-slate-800">
              <p className="text-xs text-slate-500 uppercase mb-1">Clienti</p>
              <p className="text-2xl text-cyan-400 font-bold">{diagnostics.clienti_count}</p>
            </div>

            {/* Appuntamenti Count */}
            <div className="p-4 rounded-lg bg-slate-950 border border-slate-800">
              <p className="text-xs text-slate-500 uppercase mb-1">Appuntamenti</p>
              <p className="text-2xl text-teal-400 font-bold">{diagnostics.appuntamenti_count}</p>
            </div>

            {/* Disk Free */}
            <div className="p-4 rounded-lg bg-slate-950 border border-slate-800">
              <p className="text-xs text-slate-500 uppercase mb-1">Spazio Disco Libero</p>
              <p className={`text-white font-semibold ${
                diagnostics.disk_free_bytes < 1024 * 1024 * 1024 ? 'text-red-400' : ''
              }`}>
                {diagnostics.disk_free_human}
              </p>
            </div>

            {/* Last Backup */}
            <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 md:col-span-2">
              <p className="text-xs text-slate-500 uppercase mb-1">Ultimo Backup</p>
              <p className={`font-semibold ${diagnostics.last_backup ? 'text-green-400' : 'text-orange-400'}`}>
                {diagnostics.last_backup || 'Nessun backup trovato'}
              </p>
            </div>

            {/* Data Dir */}
            <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 lg:col-span-3">
              <p className="text-xs text-slate-500 uppercase mb-1">Directory Dati</p>
              <p className="text-slate-300 font-mono text-sm break-all">{diagnostics.data_dir}</p>
            </div>
          </div>
        ) : null}
      </Card>

      {/* ─────────────────────────────────────────────────────────────── */}
      {/* SEZIONE: Backup & Restore */}
      {/* ─────────────────────────────────────────────────────────────── */}
      <Card className="p-6 bg-slate-900 border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <span className="text-2xl">💾</span> Backup Database
            </h2>
            <p className="text-sm text-slate-400">Crea e ripristina copie di sicurezza</p>
          </div>
          <Button
            onClick={handleBackup}
            disabled={backupMutation.isPending}
            className="bg-green-600 hover:bg-green-700 text-white"
          >
            {backupMutation.isPending ? 'Backup in corso...' : '+ Crea Backup'}
          </Button>
        </div>

        {loadingBackups ? (
          <p className="text-slate-400">Caricamento backup...</p>
        ) : backups && backups.length > 0 ? (
          <div className="space-y-2">
            <p className="text-sm text-slate-400 mb-3">
              {backups.length} backup disponibil{backups.length === 1 ? 'e' : 'i'}
            </p>
            <div className="max-h-48 overflow-y-auto space-y-2">
              {backups.filter(Boolean).map((backup) => {
                const filename = backup.path?.split('/').pop() ?? backup.path ?? '';
                return (
                <div
                  key={backup.path ?? backup.created_at}
                  className="flex items-center justify-between p-3 rounded-lg bg-slate-950 border border-slate-800"
                >
                  <div>
                    <p className="text-white font-mono text-sm">
                      {filename}
                    </p>
                    <p className="text-xs text-slate-400">
                      {backup.created_at} • {((backup.size_bytes / 1024 / 1024)).toFixed(2)} MB
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleRestore(backup.path)}
                      disabled={restoreMutation.isPending}
                      className="text-orange-400 border-orange-500/30 hover:bg-orange-500/10"
                    >
                      Ripristina
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteBackup(backup.path, filename)}
                      disabled={deleteMutation.isPending}
                      className="text-red-400 border-red-500/30 hover:bg-red-500/10"
                      title="Elimina (solo Admin)"
                    >
                      🗑️
                    </Button>
                  </div>
                </div>
                );
              })}
            </div>
          </div>
        ) : (
          <p className="text-slate-500 italic">Nessun backup trovato. Crea il tuo primo backup!</p>
        )}
      </Card>

      {/* ─────────────────────────────────────────────────────────────── */}
      {/* SEZIONE: Export Support Bundle */}
      {/* ─────────────────────────────────────────────────────────────── */}
      <Card className="p-6 bg-slate-900 border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <span className="text-2xl">📦</span> Support Bundle
            </h2>
            <p className="text-sm text-slate-400">
              Esporta un pacchetto con diagnostica e log per il supporto tecnico
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 mb-4">
          <label className="flex items-center gap-2 text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={includeDbInBundle}
              onChange={(e) => setIncludeDbInBundle(e.target.checked)}
              className="w-4 h-4 rounded border-slate-600 bg-slate-800 text-cyan-500 focus:ring-cyan-500"
            />
            Includi database nel bundle
          </label>
          <span className="text-xs text-slate-500">
            (contiene dati clienti)
          </span>
        </div>

        <Button
          onClick={handleExportBundle}
          disabled={exportBundleMutation.isPending}
          className="bg-purple-600 hover:bg-purple-700 text-white"
        >
          {exportBundleMutation.isPending ? 'Esportazione...' : 'Esporta Support Bundle'}
        </Button>
      </Card>

      {/* ─────────────────────────────────────────────────────────────── */}
      {/* F13: Export CSV */}
      {/* ─────────────────────────────────────────────────────────────── */}
      <Card className="p-6 bg-slate-900 border-slate-800">
        <div className="mb-4">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <span className="text-2xl">📊</span> Esporta Dati CSV
          </h2>
          <p className="text-sm text-slate-400">Esporta clienti o appuntamenti in formato CSV</p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={() => handleExportCsv('clienti')}
            disabled={exportClientiCsv.isPending}
            className="text-cyan-400 border-cyan-500/30 hover:bg-cyan-500/10"
          >
            {exportClientiCsv.isPending ? 'Esportazione...' : '↓ Esporta Clienti CSV'}
          </Button>
          <Button
            variant="outline"
            onClick={() => handleExportCsv('appuntamenti')}
            disabled={exportAppuntamentiCsv.isPending}
            className="text-teal-400 border-teal-500/30 hover:bg-teal-500/10"
          >
            {exportAppuntamentiCsv.isPending ? 'Esportazione...' : '↓ Esporta Appuntamenti CSV'}
          </Button>
        </div>
      </Card>

      {/* ─────────────────────────────────────────────────────────────── */}
      {/* SEZIONE: Remote Assist */}
      {/* ─────────────────────────────────────────────────────────────── */}
      <Card className="p-6 bg-slate-900 border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <span className="text-2xl">🖥️</span> Assistenza Remota
            </h2>
            <p className="text-sm text-slate-400">
              Istruzioni per condividere lo schermo con il supporto tecnico
            </p>
          </div>
        </div>

        {remoteAssist && (
          <div className="space-y-4">
            <div className="p-4 rounded-lg bg-slate-950 border border-slate-800">
              <h3 className="text-lg font-semibold text-cyan-400 mb-3">
                {remoteAssist.title}
              </h3>
              <ol className="space-y-2">
                {remoteAssist.steps.map((step, idx) => (
                  <li key={idx} className="text-slate-300 text-sm">
                    {step}
                  </li>
                ))}
              </ol>
            </div>

            <div className="flex gap-3">
              <Button
                onClick={handleOpenRemoteAssist}
                className="bg-teal-600 hover:bg-teal-700 text-white"
              >
                📋 Copia Istruzioni
              </Button>
              <Button
                variant="outline"
                onClick={async () => {
                  await window.navigator.clipboard.writeText(
                    `Fluxion Support Request\n\n` +
                    `App: ${diagnostics?.app_version || 'N/A'}\n` +
                    `OS: ${diagnostics?.os_type} ${diagnostics?.os_version}\n` +
                    `DB Size: ${diagnostics?.db_size_human || 'N/A'}\n`
                  );
                  await message('Info sistema copiate negli appunti!', { title: 'Copiato', kind: 'info' });
                }}
                className="text-slate-300 border-slate-600 hover:bg-slate-800"
              >
                📝 Copia Info Sistema
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};
