-- 016_suppliers.sql
-- Supplier Management for FLUXION
-- Created: 2026-01-15

-- Suppliers table
CREATE TABLE IF NOT EXISTS suppliers (
    id TEXT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    telefono VARCHAR(20),
    indirizzo VARCHAR(500),
    citta VARCHAR(100),
    cap VARCHAR(10),
    partita_iva VARCHAR(20) UNIQUE,
    status VARCHAR(50) DEFAULT 'active',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(nome)
);

-- Supplier Orders table
CREATE TABLE IF NOT EXISTS supplier_orders (
    id TEXT PRIMARY KEY,
    supplier_id TEXT NOT NULL,
    ordine_numero VARCHAR(50) NOT NULL,
    data_ordine TEXT NOT NULL,
    data_consegna_prevista TEXT NOT NULL,
    importo_totale REAL NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    items TEXT NOT NULL,  -- JSON array
    notes VARCHAR(1000),
    created_at TEXT NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    UNIQUE(ordine_numero)
);

-- Supplier interactions (messages, logs)
CREATE TABLE IF NOT EXISTS supplier_interactions (
    id TEXT PRIMARY KEY,
    supplier_id TEXT NOT NULL,
    order_id TEXT,
    tipo VARCHAR(50),  -- email, whatsapp, call, note
    messaggio TEXT,
    status VARCHAR(50),  -- sent, received, failed, processed
    created_at TEXT NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    FOREIGN KEY (order_id) REFERENCES supplier_orders(id)
);

-- Create indices for performance
CREATE INDEX IF NOT EXISTS idx_supplier_email ON suppliers(email);
CREATE INDEX IF NOT EXISTS idx_supplier_phone ON suppliers(telefono);
CREATE INDEX IF NOT EXISTS idx_supplier_status ON suppliers(status);
CREATE INDEX IF NOT EXISTS idx_order_supplier ON supplier_orders(supplier_id);
CREATE INDEX IF NOT EXISTS idx_order_status ON supplier_orders(status);
CREATE INDEX IF NOT EXISTS idx_order_date ON supplier_orders(data_ordine);
CREATE INDEX IF NOT EXISTS idx_interaction_supplier ON supplier_interactions(supplier_id);
CREATE INDEX IF NOT EXISTS idx_interaction_order ON supplier_interactions(order_id);
