// ═══════════════════════════════════════════════════════════════════
// FLUXION - Diagnostics Panel (Fase 4 - Fluxion Care)
// UI per diagnostica, backup, export bundle, remote assist
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState } from 'react';
import { save } from '@tauri-apps/plugin-dialog';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import {
  useDiagnosticsInfo,
  useBackups,
  useRemoteAssistInstructions,
  useBackupDatabase,
  useRestoreDatabase,
  useExportSupportBundle,
} from '@/hooks/use-support';

export const DiagnosticsPanel: FC = () => {
  const { data: diagnostics, isLoading: loadingDiagnostics, refetch: refetchDiagnostics } = useDiagnosticsInfo();
  const { data: backups, isLoading: loadingBackups } = useBackups();
  const { data: remoteAssist } = useRemoteAssistInstructions();

  const backupMutation = useBackupDatabase();
  const restoreMutation = useRestoreDatabase();
  const exportBundleMutation = useExportSupportBundle();

  const [includeDbInBundle, setIncludeDbInBundle] = useState(true);

  // ─────────────────────────────────────────────────────────────────
  // Handlers
  // ─────────────────────────────────────────────────────────────────

  const handleBackup = async () => {
    try {
      await backupMutation.mutateAsync();
      window.alert('Backup completato con successo!');
    } catch (error) {
      window.alert(`Errore backup: ${error}`);
    }
  };

  const handleRestore = async (backupPath: string) => {
    const confirmed = window.confirm(
      'ATTENZIONE: Il ripristino sovrascriverà il database attuale.\n\n' +
      'Una copia di sicurezza verrà salvata automaticamente.\n\n' +
      'Continuare?'
    );
    if (!confirmed) return;

    try {
      const result = await restoreMutation.mutateAsync(backupPath);
      window.alert(result + '\n\nRiavvia l\'applicazione per applicare le modifiche.');
    } catch (error) {
      window.alert(`Errore ripristino: ${error}`);
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

      window.alert(
        `Support Bundle creato!\n\n` +
        `Percorso: ${result.path}\n` +
        `Dimensione: ${result.size_human}\n` +
        `Contenuto: ${result.contents.join(', ')}`
      );
    } catch (error) {
      window.alert(`Errore export bundle: ${error}`);
    }
  };

  const handleOpenRemoteAssist = () => {
    if (!remoteAssist?.button_action) return;

    // Usa window.open per link di sistema (macOS/Windows)
    // In Tauri 2.x possiamo usare il plugin opener
    if (remoteAssist.os === 'macos') {
      // Copia istruzioni negli appunti
      window.navigator.clipboard.writeText(remoteAssist.steps.join('\n'));
      window.alert(
        'Istruzioni copiate negli appunti!\n\n' +
        'Apri manualmente:\nPreferenze di Sistema → Condivisione → Condivisione Schermo'
      );
    } else if (remoteAssist.os === 'windows') {
      window.navigator.clipboard.writeText(remoteAssist.steps.join('\n'));
      window.alert(
        'Istruzioni copiate negli appunti!\n\n' +
        'Premi Win + Ctrl + Q per aprire Assistenza Rapida'
      );
    }
  };

  // ─────────────────────────────────────────────────────────────────
  // Render
  // ─────────────────────────────────────────────────────────────────

  return (
    <div className="space-y-6">
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
              {backups.map((backup) => (
                <div
                  key={backup.path}
                  className="flex items-center justify-between p-3 rounded-lg bg-slate-950 border border-slate-800"
                >
                  <div>
                    <p className="text-white font-mono text-sm">
                      {backup.path.split('/').pop()}
                    </p>
                    <p className="text-xs text-slate-400">
                      {backup.created_at} • {((backup.size_bytes / 1024 / 1024)).toFixed(2)} MB
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleRestore(backup.path)}
                    disabled={restoreMutation.isPending}
                    className="text-orange-400 border-orange-500/30 hover:bg-orange-500/10"
                  >
                    Ripristina
                  </Button>
                </div>
              ))}
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
                onClick={() => {
                  window.navigator.clipboard.writeText(
                    `Fluxion Support Request\n\n` +
                    `App: ${diagnostics?.app_version || 'N/A'}\n` +
                    `OS: ${diagnostics?.os_type} ${diagnostics?.os_version}\n` +
                    `DB Size: ${diagnostics?.db_size_human || 'N/A'}\n`
                  );
                  window.alert('Info sistema copiate negli appunti!');
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
