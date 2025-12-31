// ═══════════════════════════════════════════════════════════════════
// FLUXION E2E - Test Data Fixtures
// Predefined test data for consistent E2E tests
// ═══════════════════════════════════════════════════════════════════

import { generateEmail, generatePhone, generateUniqueData } from '../utils/test-helpers';

export const TestData = {
  // ───────────────────────────────────────────────────────────────────
  // Clienti
  // ───────────────────────────────────────────────────────────────────
  clienti: {
    mario: {
      nome: 'Mario',
      cognome: 'Rossi',
      email: generateEmail('mario.rossi'),
      telefono: '+39 333 1234567',
      indirizzo: 'Via Roma 1, Milano',
      note: 'Cliente abituale',
    },
    laura: {
      nome: 'Laura',
      cognome: 'Bianchi',
      email: generateEmail('laura.bianchi'),
      telefono: '+39 333 7654321',
      indirizzo: 'Via Garibaldi 10, Torino',
    },
    giovanni: {
      nome: 'Giovanni',
      cognome: 'Verdi',
      email: generateEmail('giovanni.verdi'),
      telefono: '+39 333 9876543',
    },
    // Generate unique cliente for isolation
    getUnique: () => ({
      nome: generateUniqueData('Nome'),
      cognome: generateUniqueData('Cognome'),
      email: generateEmail('test'),
      telefono: generatePhone(),
    }),
  },

  // ───────────────────────────────────────────────────────────────────
  // Servizi
  // ───────────────────────────────────────────────────────────────────
  servizi: {
    taglioUomo: {
      nome: 'Taglio Uomo',
      categoria: 'Taglio',
      descrizione: 'Taglio classico per uomo',
      prezzo: 25.0,
      iva: 22,
      durata: 30,
      buffer: 5,
      colore: '#22D3EE',
      ordine: 0,
    },
    piegaDonna: {
      nome: 'Piega Donna',
      categoria: 'Styling',
      descrizione: 'Piega con phon e spazzola',
      prezzo: 30.0,
      iva: 22,
      durata: 45,
      buffer: 10,
      colore: '#14B8A6',
      ordine: 1,
    },
    coloreCompleto: {
      nome: 'Colore Completo',
      categoria: 'Colore',
      descrizione: 'Colorazione totale con trattamento',
      prezzo: 65.0,
      iva: 22,
      durata: 120,
      buffer: 15,
      colore: '#C084FC',
      ordine: 2,
    },
    // Generate unique servizio
    getUnique: () => ({
      nome: generateUniqueData('Servizio'),
      categoria: 'Test',
      prezzo: 50.0,
      durata: 60,
    }),
  },

  // ───────────────────────────────────────────────────────────────────
  // Operatori
  // ───────────────────────────────────────────────────────────────────
  operatori: {
    marioBianchi: {
      nome: 'Mario',
      cognome: 'Bianchi',
      email: generateEmail('mario.bianchi'),
      telefono: '+39 333 7654321',
      ruolo: 'operatore' as const,
      colore: '#C084FC',
    },
    luigiVerdi: {
      nome: 'Luigi',
      cognome: 'Verdi',
      email: generateEmail('luigi.verdi'),
      telefono: '+39 333 1111111',
      ruolo: 'operatore' as const,
      colore: '#14B8A6',
    },
    paolaRossi: {
      nome: 'Paola',
      cognome: 'Rossi',
      email: generateEmail('paola.rossi'),
      telefono: '+39 333 2222222',
      ruolo: 'admin' as const,
      colore: '#F472B6',
    },
    // Generate unique operatore
    getUnique: () => ({
      nome: generateUniqueData('Nome'),
      cognome: generateUniqueData('Cognome'),
      email: generateEmail('operatore'),
      telefono: generatePhone(),
      ruolo: 'operatore' as const,
      colore: '#22D3EE',
    }),
  },

  // ───────────────────────────────────────────────────────────────────
  // Edge Cases for Validation Testing
  // ───────────────────────────────────────────────────────────────────
  edgeCases: {
    servizi: {
      nomeCorto: {
        nome: 'X', // Too short (min 2 chars)
        prezzo: 25.0,
        durata: 30,
      },
      prezzoZero: {
        nome: 'Servizio Gratuito',
        prezzo: 0,
        durata: 15,
      },
      prezzoAlto: {
        nome: 'Servizio Premium',
        prezzo: 999.99,
        durata: 180,
      },
      prezzoNegativo: {
        nome: 'Invalid',
        prezzo: -10.0, // Should fail
        durata: 30,
      },
      durataZero: {
        nome: 'Invalid Duration',
        prezzo: 25.0,
        durata: 0, // Should fail
      },
      durataLunga: {
        nome: 'Trattamento Giornata',
        prezzo: 300.0,
        durata: 480, // 8 hours
      },
      nomeSpecialChars: {
        nome: 'Taglio & Piega',
        prezzo: 30.0,
        durata: 45,
      },
      nomeEmoji: {
        nome: 'Manicure 💅',
        prezzo: 20.0,
        durata: 30,
      },
      nomeLungo: {
        nome: 'Trattamento Completo con Massaggio Rilassante e Cura del Viso Anti-Age con Prodotti Bio Certificati',
        prezzo: 100.0,
        durata: 120,
      },
    },
    clienti: {
      emailInvalida: {
        nome: 'Test',
        cognome: 'Invalid',
        email: 'not-an-email', // Should fail
        telefono: '+39 333 1234567',
      },
      telefonoSenzaPrefisso: {
        nome: 'Test',
        cognome: 'Phone',
        email: generateEmail('test'),
        telefono: '3331234567', // No +39
      },
    },
  },
};

export default TestData;
