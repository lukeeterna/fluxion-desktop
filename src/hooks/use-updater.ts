// ═══════════════════════════════════════════════════════════════════
// FLUXION - Auto-Update Hooks (Phase 8)
// TanStack Query hooks for Tauri updater plugin
// ═══════════════════════════════════════════════════════════════════

import { useState, useEffect, useCallback } from 'react';
import { check, Update, type DownloadEvent } from '@tauri-apps/plugin-updater';
import { relaunch } from '@tauri-apps/plugin-process';

export interface UpdateState {
  checking: boolean;
  available: boolean;
  downloading: boolean;
  progress: number;
  error: string | null;
  update: Update | null;
}

const initialState: UpdateState = {
  checking: false,
  available: false,
  downloading: false,
  progress: 0,
  error: null,
  update: null,
};

export function useUpdater() {
  const [state, setState] = useState<UpdateState>(initialState);

  const checkForUpdates = useCallback(async () => {
    setState((s) => ({ ...s, checking: true, error: null }));

    try {
      const update = await check();

      if (update) {
        setState((s) => ({
          ...s,
          checking: false,
          available: true,
          update,
        }));
        return update;
      }

      setState((s) => ({ ...s, checking: false, available: false }));
      return null;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Errore verifica aggiornamenti';
      setState((s) => ({
        ...s,
        checking: false,
        error: message,
      }));
      return null;
    }
  }, []);

  const downloadAndInstall = useCallback(async () => {
    if (!state.update) return false;

    setState((s) => ({ ...s, downloading: true, progress: 0, error: null }));

    let downloadedBytes = 0;
    let totalBytes = 0;

    try {
      // Download with progress
      await state.update.downloadAndInstall((event: DownloadEvent) => {
        switch (event.event) {
          case 'Started':
            totalBytes = event.data.contentLength ?? 0;
            downloadedBytes = 0;
            setState((s) => ({ ...s, progress: 0 }));
            break;
          case 'Progress': {
            downloadedBytes += event.data.chunkLength;
            const progress = totalBytes > 0
              ? Math.round((downloadedBytes / totalBytes) * 100)
              : 0;
            setState((s) => ({ ...s, progress }));
            break;
          }
          case 'Finished':
            setState((s) => ({ ...s, progress: 100 }));
            break;
        }
      });

      // Relaunch app to apply update
      await relaunch();
      return true;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Errore download aggiornamento';
      setState((s) => ({
        ...s,
        downloading: false,
        error: message,
      }));
      return false;
    }
  }, [state.update]);

  const dismissUpdate = useCallback(() => {
    setState(initialState);
  }, []);

  // Check for updates on mount (optional, can be disabled)
  useEffect(() => {
    // Only check in production
    if (import.meta.env.PROD) {
      // Delay check to not block startup
      const timeout = setTimeout(() => {
        checkForUpdates();
      }, 5000);

      return () => clearTimeout(timeout);
    }
  }, [checkForUpdates]);

  return {
    ...state,
    checkForUpdates,
    downloadAndInstall,
    dismissUpdate,
  };
}
