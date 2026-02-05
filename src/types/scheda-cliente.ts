// ═══════════════════════════════════════════════════════════════════
// FLUXION - Schede Cliente Types
// Tipi per schede verticali specifiche per settore
// ═══════════════════════════════════════════════════════════════════

import { z } from 'zod';

// ─────────────────────────────────────────────────────────────────────
// SCHEDA ODONTOIATRICA
// ─────────────────────────────────────────────────────────────────────

export const ToothStatusSchema = z.enum(['sano', 'otturato', 'devitalizzato', 'corona', 'impianto', 'mancante', 'carie']);

export const OdontogrammaToothSchema = z.object({
  stato: ToothStatusSchema,
  note: z.string().optional(),
});

export const TrattamentoSchema = z.object({
  id: z.string(),
  data: z.string(),
  tipo: z.string(),
  dente: z.string().optional(),
  descrizione: z.string(),
  costo: z.number().optional(),
});

export const SchedaOdontoiatricaSchema = z.object({
  id: z.string().optional(),
  cliente_id: z.string(),
  
  // Odontogramma
  odontogramma: z.record(z.string(), OdontogrammaToothSchema).default({}),
  
  // Storia clinica
  prima_visita: z.string().optional(),
  ultima_visita: z.string().optional(),
  frequenza_controlli: z.enum(['6mesi', '1anno']).optional(),
  
  // Abitudini
  spazzolino: z.enum(['manuale', 'elettrico', 'ultrasuoni']).optional(),
  filo_interdentale: z.boolean().default(false),
  collutorio: z.boolean().default(false),
  
  // Allergie
  allergia_lattice: z.boolean().default(false),
  allergia_anestesia: z.boolean().default(false),
  allergie_altre: z.string().optional(),
  
  // Ortodonzia
  ortodonzia_in_corso: z.boolean().default(false),
  tipo_apparecchio: z.enum(['fisso', 'invisibile', 'rimovibile']).optional(),
  data_inizio_ortodonzia: z.string().optional(),
  
  // Trattamenti
  trattamenti: z.array(TrattamentoSchema).default([]),
  
  // Note
  note_cliniche: z.string().optional(),
  
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

export type ToothStatus = z.infer<typeof ToothStatusSchema>;
export type OdontogrammaTooth = z.infer<typeof OdontogrammaToothSchema>;
export type Trattamento = z.infer<typeof TrattamentoSchema>;
export type SchedaOdontoiatrica = z.infer<typeof SchedaOdontoiatricaSchema>;

// ─────────────────────────────────────────────────────────────────────
// SCHEDA FISIOTERAPIA
// ─────────────────────────────────────────────────────────────────────

export const SedutaSchema = z.object({
  id: z.string(),
  data: z.string(),
  trattamento: z.string(),
  note: z.string().optional(),
  completata: z.boolean().default(false),
});

export const SchedaFisioterapiaSchema = z.object({
  id: z.string().optional(),
  cliente_id: z.string(),
  
  // Motivo accesso
  motivo_primo_accesso: z.string().optional(),
  data_inizio_terapia: z.string().optional(),
  data_fine_terapia: z.string().optional(),
  
  // Diagnosi
  diagnosi_medica: z.string().optional(),
  diagnosi_fisioterapica: z.string().optional(),
  
  // Zone
  zona_principale: z.string().optional(),
  zone_secondarie: z.array(z.string()).default([]),
  
  // Valutazioni
  valutazione_iniziale: z.object({
    vas_dolore: z.number().min(0).max(10).optional(),
    rom: z.record(z.string(), z.number()).optional(),
  }).default({}),
  scale_valutazione: z.record(z.string(), z.number()).default({}),
  
  // Prescrizione
  numero_sedute_prescritte: z.number().optional(),
  frequenza_settimanale: z.enum(['1x', '2x', '3x', '4x', '5x']).optional(),
  
  // Sedute
  sedute_effettuate: z.array(SedutaSchema).default([]),
  
  // Esito
  esito_trattamento: z.enum(['miglioramento', 'stabile', 'peggioramento', 'in_corso']).optional(),
  controindicazioni: z.string().optional(),
  
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

export type Seduta = z.infer<typeof SedutaSchema>;
export type SchedaFisioterapia = z.infer<typeof SchedaFisioterapiaSchema>;

// ─────────────────────────────────────────────────────────────────────
// SCHEDA ESTETICA
// ─────────────────────────────────────────────────────────────────────

export const SchedaEsteticaSchema = z.object({
  id: z.string().optional(),
  cliente_id: z.string(),
  
  // Analisi pelle
  fototipo: z.number().min(1).max(6).optional(),
  tipo_pelle: z.enum(['secca', 'mista', 'grassa', 'sensibile', 'normale']).optional(),
  
  // Allergie
  allergie_prodotti: z.array(z.string()).default([]),
  allergie_profumi: z.boolean().default(false),
  allergie_henne: z.boolean().default(false),
  
  // Trattamenti
  trattamenti_precedenti: z.array(z.object({
    tipo: z.string(),
    data: z.string(),
    note: z.string().optional(),
  })).default([]),
  
  // Epilazione
  ultima_depilazione: z.string().optional(),
  metodo_depilazione: z.enum(['ceretta', 'laser', 'filo', 'crema']).optional(),
  
  // Unghie
  unghie_naturali: z.boolean().default(true),
  problematiche_unghie: z.string().optional(),
  
  // Viso
  problematiche_viso: z.array(z.string()).default([]),
  routine_skincare: z.string().optional(),
  
  // Corpo
  peso_attuale: z.number().optional(),
  obiettivo: z.enum(['dimagrimento', 'tonificazione', 'rilassamento', 'anticellulite']).optional(),
  
  // Controindicazioni
  gravidanza: z.boolean().default(false),
  allattamento: z.boolean().default(false),
  patologie_attive: z.array(z.string()).default([]),
  
  // Note
  note_trattamenti: z.string().optional(),
  
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

export type SchedaEstetica = z.infer<typeof SchedaEsteticaSchema>;

// ─────────────────────────────────────────────────────────────────────
// SCHEDA PARRUCCHIERE
// ─────────────────────────────────────────────────────────────────────

export const SchedaParrucchiereSchema = z.object({
  id: z.string().optional(),
  cliente_id: z.string(),
  
  // Analisi capelli
  tipo_capello: z.enum(['fino', 'medio', 'spesso', 'crepo', 'riccio', 'liscio']).optional(),
  porosita: z.enum(['bassa', 'media', 'alta']).optional(),
  lunghezza_attuale: z.enum(['corto', 'medio', 'lungo']).optional(),
  
  // Storia colore
  base_naturale: z.string().optional(),
  colore_attuale: z.string().optional(),
  
  // Storia chimica
  colorazioni_precedenti: z.array(z.object({
    colore: z.string(),
    data: z.string(),
    tipo: z.string(),
  })).default([]),
  decolorazioni: z.number().default(0),
  permanente: z.number().default(0),
  stirature_chimiche: z.number().default(0),
  
  // Allergie
  allergia_tinta: z.boolean().default(false),
  allergia_ammoniaca: z.boolean().default(false),
  test_pelle_eseguito: z.boolean().default(false),
  data_test_pelle: z.string().optional(),
  
  // Preferenze
  servizi_abituali: z.array(z.string()).default([]),
  frequenza_taglio: z.enum(['settimanale', '2settimane', 'mensile', '2mesi', '3mesi']).optional(),
  frequenza_colore: z.enum(['settimanale', '2settimane', 'mensile', '2mesi', '3mesi', '6mesi']).optional(),
  
  // Prodotti
  prodotti_casa: z.record(z.string(), z.string()).default({}),
  
  // Preferenze
  preferenze_colore: z.string().optional(),
  non_vuole: z.array(z.string()).default([]),
  
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

export type SchedaParrucchiere = z.infer<typeof SchedaParrucchiereSchema>;

// ─────────────────────────────────────────────────────────────────────
// SCHEDA VEICOLI (Auto)
// ─────────────────────────────────────────────────────────────────────

export const InterventoSchema = z.object({
  id: z.string(),
  data: z.string(),
  km: z.number(),
  tipo: z.string(),
  descrizione: z.string(),
  costo: z.number().optional(),
});

export const SchedaVeicoliSchema = z.object({
  id: z.string().optional(),
  cliente_id: z.string(),
  
  // Dati veicolo
  targa: z.string(),
  marca: z.string().optional(),
  modello: z.string().optional(),
  anno: z.number().optional(),
  alimentazione: z.enum(['benzina', 'diesel', 'gpl', 'metano', 'elettrico', 'ibrido']).optional(),
  cilindrata: z.string().optional(),
  kw: z.number().optional(),
  telaio: z.string().optional(),
  
  // Dati tecnici
  ultima_revisione: z.string().optional(),
  scadenza_revisione: z.string().optional(),
  km_attuali: z.number().optional(),
  km_ultimo_tagliando: z.number().optional(),
  
  // Gomme
  misura_gomme: z.string().optional(),
  tipo_gomme: z.enum(['estive', 'invernali', 'allseason']).optional(),
  
  // Preferenze
  preferenza_ricambi: z.enum(['originali', 'compatibili', 'entrambi']).optional(),
  note_veicolo: z.string().optional(),
  
  // Storico
  interventi: z.array(InterventoSchema).default([]),
  
  is_default: z.boolean().default(false),
  
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

export type Intervento = z.infer<typeof InterventoSchema>;
export type SchedaVeicoli = z.infer<typeof SchedaVeicoliSchema>;

// ─────────────────────────────────────────────────────────────────────
// SCHEDA CARROZZERIA
// ─────────────────────────────────────────────────────────────────────

export const SchedaCarrozzeriaSchema = z.object({
  id: z.string().optional(),
  cliente_id: z.string(),
  veicolo_id: z.string().optional(),
  
  // Danno
  tipo_danno: z.enum(['ammaccatura', 'graffio', 'urto', 'corrosione', 'rottura']).optional(),
  posizione_danno: z.string().optional(),
  entita_danno: z.enum(['lieve', 'media', 'grave']).optional(),
  descrizione_danno: z.string().optional(),
  
  // Foto
  foto_pre: z.array(z.string()).default([]),
  foto_post: z.array(z.string()).default([]),
  
  // Preventivo
  preventivo_numero: z.string().optional(),
  importo_preventivo: z.number().optional(),
  approvato: z.boolean().default(false),
  
  // Intervento
  data_ingresso: z.string().optional(),
  data_consegna_prevista: z.string().optional(),
  data_consegna_effettiva: z.string().optional(),
  
  // Dettagli
  lavorazioni: z.array(z.string()).default([]),
  verniciatura: z.boolean().default(false),
  codice_colore: z.string().optional(),
  
  // Assicurazione
  sinistro_assicurativo: z.boolean().default(false),
  compagnia: z.string().optional(),
  numero_sinistro: z.string().optional(),
  
  // Stato
  stato: z.enum(['preventivo', 'approvato', 'in_lavorazione', 'completato', 'consegnato']).default('preventivo'),
  
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

export type SchedaCarrozzeria = z.infer<typeof SchedaCarrozzeriaSchema>;

// ─────────────────────────────────────────────────────────────────────
// UNION TYPE
// ─────────────────────────────────────────────────────────────────────

export type SchedaCliente = 
  | SchedaOdontoiatrica 
  | SchedaFisioterapia 
  | SchedaEstetica 
  | SchedaParrucchiere 
  | SchedaVeicoli 
  | SchedaCarrozzeria;

// ─────────────────────────────────────────────────────────────────────
// MAPPING TIPO SCHEDA
// ─────────────────────────────────────────────────────────────────────

export const TIPO_SCHEDA_LABELS: Record<string, string> = {
  odontoiatrica: 'Scheda Odontoiatrica',
  fisioterapia: 'Scheda Fisioterapia',
  estetica: 'Scheda Estetica',
  parrucchiere: 'Scheda Parrucchiere',
  veicoli: 'Scheda Veicoli',
  carrozzeria: 'Scheda Carrozzeria',
  medica: 'Scheda Medica',
  fitness: 'Scheda Fitness',
};

// ─────────────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────────────

export function getSchedaLabel(tipo: string): string {
  return TIPO_SCHEDA_LABELS[tipo] || 'Scheda Cliente';
}
