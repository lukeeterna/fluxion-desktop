// ═══════════════════════════════════════════════════════════════════
// FLUXION - Types Index
// Esportazioni centralizzate di tutti i tipi
// ═══════════════════════════════════════════════════════════════════

// Setup
export * from './setup';

// Schede Cliente
export * from './scheda-cliente';

// License (license-ed25519 è il sistema principale)
// Nota: './license' esporta LICENSE_TIERS che è in conflitto con './setup'
// export * from './license';
export * from './license-ed25519';

// Altri tipi esistenti
export * from './cliente';
export * from './appuntamento';
export * from './servizio';
export * from './operatore';
