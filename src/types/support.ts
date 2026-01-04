// ═══════════════════════════════════════════════════════════════════
// FLUXION - Support & Diagnostics Types (Fase 4 - Fluxion Care)
// ═══════════════════════════════════════════════════════════════════

export interface DiagnosticsInfo {
  app_version: string;
  app_name: string;
  os_type: string;
  os_version: string;
  arch: string;
  data_dir: string;
  db_path: string;
  db_size_bytes: number;
  db_size_human: string;
  last_backup: string | null;
  disk_free_bytes: number;
  disk_free_human: string;
  tables_count: number;
  clienti_count: number;
  appuntamenti_count: number;
  collected_at: string;
}

export interface SupportBundleResult {
  path: string;
  size_bytes: number;
  size_human: string;
  contents: string[];
}

export interface BackupResult {
  path: string;
  size_bytes: number;
  created_at: string;
}

export interface RemoteAssistInstructions {
  os: string;
  title: string;
  steps: string[];
  button_action: string;
}
