// ═══════════════════════════════════════════════════════════════════
// FLUXION - Impostazioni Status Hook (P1.0)
// Calcola il badge di stato per ogni sezione delle impostazioni
// ═══════════════════════════════════════════════════════════════════

import { useQuery } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';
import { useSetupConfig } from './use-setup';
import { useOrariLavoro } from './use-orari';
import { useImpostazioniFatturazione } from './use-fatture';

// ─────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────

export type SectionStatus = 'ok' | 'warning' | 'error' | 'optional';

export interface ImpostazioniStatus {
  orari: SectionStatus;
  festivita: SectionStatus;
  whatsapp: SectionStatus;
  'risposte-wa': SectionStatus;
  email: SectionStatus;
  sara: SectionStatus;
  ia: SectionStatus;
  fatturazione: SectionStatus;
  fedelta: SectionStatus;
  licenza: SectionStatus;
  diagnostica: SectionStatus;
  isLoading: boolean;
}

export const STATUS_LABELS: Record<SectionStatus, string> = {
  ok:       'Configurato',
  warning:  'Da configurare',
  error:    'Non attivo',
  optional: 'Opzionale',
};

// ─────────────────────────────────────────────────────────────────
// Internal: SMTP query (mirrored from SmtpSettings component)
// ─────────────────────────────────────────────────────────────────

interface SmtpSettingsData {
  smtp_host: string;
  smtp_port: number;
  smtp_email_from: string;
  smtp_password: string;
  smtp_enabled: boolean;
}

function useSmtpSettingsData() {
  return useQuery({
    queryKey: ['smtp-settings'],
    queryFn: () => invoke<SmtpSettingsData>('get_smtp_settings'),
    staleTime: 5 * 60 * 1000,
  });
}

// ─────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────

export function useImpostazioniStatus(): ImpostazioniStatus {
  const setupConfig = useSetupConfig();
  const smtp = useSmtpSettingsData();
  const orariLavoro = useOrariLavoro();
  const fatturazione = useImpostazioniFatturazione();

  const isLoading = setupConfig.isLoading || smtp.isLoading;

  const groqKey = setupConfig.data?.groq_api_key ?? '';
  const whatsappNumber = setupConfig.data?.whatsapp_number ?? '';
  const fluxionIaKey = setupConfig.data?.fluxion_ia_key ?? '';
  const orariCount = orariLavoro.data?.length ?? 0;

  // Email: ok se smtp_email_from presente E smtp_enabled; warning se presente ma disabilitato
  const smtpData = smtp.data;
  let emailStatus: SectionStatus = 'optional';
  if (smtpData?.smtp_email_from) {
    emailStatus = smtpData.smtp_enabled ? 'ok' : 'warning';
  }

  // Sara: ok se groq_api_key valida (gsk_..., lunghezza > 10); error altrimenti (critico)
  const saraStatus: SectionStatus =
    groqKey.startsWith('gsk_') && groqKey.length > 10 ? 'ok' : 'error';

  // Fatturazione: ok se denominazione configurata, opzionale altrimenti
  const fatturazioneStatus: SectionStatus =
    fatturazione.data?.denominazione ? 'ok' : 'optional';

  return {
    orari:        orariCount > 0 ? 'ok' : 'warning',
    festivita:    'optional',
    whatsapp:     whatsappNumber ? 'ok' : 'optional',
    'risposte-wa': 'optional',
    email:        emailStatus,
    sara:         saraStatus,
    ia:           fluxionIaKey ? 'ok' : 'optional',
    fatturazione: fatturazioneStatus,
    fedelta:      'optional',
    licenza:      'ok',
    diagnostica:  'ok',
    isLoading,
  };
}
