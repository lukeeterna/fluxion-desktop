// ═══════════════════════════════════════════════════════════════════
// FLUXION - Media Types (F06 Sprint A)
// ═══════════════════════════════════════════════════════════════════

export type MediaTipo = 'foto' | 'video';

export type MediaCategoria =
  | 'generale'
  | 'trasformazione_prima'
  | 'trasformazione_dopo'
  | 'progress'
  | 'clinica'
  | 'danno_veicolo'
  | 'post_intervento';

export type MediaVisibilita = 'interno' | 'staff' | 'paziente' | 'social';

export interface MediaRecord {
  id: number;
  cliente_id: number;
  media_path: string;
  thumb_path: string | null;
  tipo: MediaTipo;
  categoria: MediaCategoria;
  appuntamento_id: number | null;
  operatore_id: number | null;
  dimensione_bytes: number | null;
  larghezza_px: number | null;
  altezza_px: number | null;
  durata_sec: number | null;
  consenso_gdpr: number;
  visibilita: MediaVisibilita;
  watermark: number;
  note: string | null;
  tag: string | null;
  created_at: string;
  updated_at: string;
}

export interface SaveMediaImageInput {
  cliente_id: number;
  bytes_base64: string;
  original_name: string;
  larghezza_px?: number;
  altezza_px?: number;
  categoria?: MediaCategoria;
  consenso_gdpr?: boolean;
}

export interface SaveMediaVideoInput {
  cliente_id: number;
  video_base64: string;
  thumb_base64: string;
  original_name: string;
  durata_sec?: number;
  categoria?: MediaCategoria;
}

export interface MediaConsentInfo {
  consenso_interno: boolean;
  consenso_social: boolean;
  consenso_clinico: boolean;
}
