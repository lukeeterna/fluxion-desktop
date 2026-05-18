-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 040: Suppliers DROP UNIQUE for PII Encryption (S257 P2)
-- ═══════════════════════════════════════════════════════════════
-- Data: 2026-05-18
-- Task: S257 — GDPR encryption suppliers PII (estensione pattern S255)
--
-- CONTESTO:
-- Migration 016 ha creato `suppliers` con UNIQUE(nome) + UNIQUE(partita_iva).
-- Quando i due campi vengono cifrati (S257 P2.b: AES-256-GCM nonce-randomized),
-- ogni encrypt dello stesso plaintext produce un ciphertext diverso → UNIQUE
-- a livello SQL diventa fittizio (mai falso-positivo, mai falso-negativo:
-- NON enforcer effettivo) e blocca i legittimi update verso lo stesso valore
-- (ciphertext nuovo ≠ ciphertext esistente, UPDATE OK, ma re-encrypt full row
-- può collidere su edge case se mai due righe condividono lo stesso plaintext
-- ma ciphertext momentaneamente uguale — improbabile ma non zero).
--
-- FIX:
-- DROP UNIQUE(nome) + DROP UNIQUE(partita_iva) ricreando la tabella senza
-- i vincoli. Dedupe enforcement sposta ad application layer in
-- `commands/supplier.rs::create_supplier` (list-decrypt-compare nome +
-- partita_iva normalizzati prima dell'INSERT). Stesso pattern S249 clienti.
--
-- Nessuna view legge da `suppliers` (verificato grep migrations + src-tauri).
-- Quindi non serve un companion view-refactor analogo a migration 039.
-- ═══════════════════════════════════════════════════════════════

-- STEP 1: rinomina tabella esistente
ALTER TABLE suppliers RENAME TO suppliers_old_040;

-- STEP 2: ricrea tabella senza UNIQUE
CREATE TABLE suppliers (
    id TEXT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    telefono VARCHAR(20),
    indirizzo VARCHAR(500),
    citta VARCHAR(100),
    cap VARCHAR(10),
    partita_iva VARCHAR(20),
    status VARCHAR(50) DEFAULT 'active',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- STEP 3: copia data (ordine colonne identico)
INSERT INTO suppliers (id, nome, email, telefono, indirizzo, citta, cap, partita_iva, status, created_at, updated_at)
SELECT id, nome, email, telefono, indirizzo, citta, cap, partita_iva, status, created_at, updated_at
FROM suppliers_old_040;

-- STEP 4: drop tabella vecchia
DROP TABLE suppliers_old_040;

-- STEP 5: ricrea indici di performance (migration 016)
CREATE INDEX IF NOT EXISTS idx_supplier_email ON suppliers(email);
CREATE INDEX IF NOT EXISTS idx_supplier_phone ON suppliers(telefono);
CREATE INDEX IF NOT EXISTS idx_supplier_status ON suppliers(status);

-- ═══════════════════════════════════════════════════════════════
-- VALIDAZIONE
-- ═══════════════════════════════════════════════════════════════
-- sqlite> .schema suppliers
-- Atteso: NO `UNIQUE(nome)`, NO `partita_iva ... UNIQUE`.
-- sqlite> SELECT COUNT(*) FROM suppliers;
-- Atteso: stesso count pre-migration (row-preserving rename).
-- ═══════════════════════════════════════════════════════════════
