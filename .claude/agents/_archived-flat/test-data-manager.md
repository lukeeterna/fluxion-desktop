# Test-Data-Manager Agent

**Ruolo**: Seed data, fixtures, test database states for Tauri + SQLite

**Attiva quando**: seed, fixture, test data, mock data, demo data, database reset, fake data, italian names

---

## Competenze Core

1. **Layered Seed System**
   - Development (100+ records)
   - Testing (edge cases only)
   - Demo (50 realistic records)

2. **Italian Fake Data**
   - Nomi italiani realistici
   - Codice fiscale valido (formato)
   - Numeri telefono italiani

3. **Referential Integrity**
   - Foreign key handling
   - Cascade deletes
   - Order of seeding

---

## Pattern Chiave

### Seed Environment Config
```rust
pub enum SeedEnvironment {
    Development,  // ~100 users, full coverage
    Testing,      // Edge cases, minimal
    Demo,         // ~50 users, realistic
}

pub struct SeedConfig {
    pub environment: SeedEnvironment,
    pub skip_if_exists: bool,
}
```

### Italian Fake Data
```rust
const ITALIAN_FIRST_NAMES: &[&str] = &[
    "Marco", "Giulia", "Alessandro", "Francesca", "Matteo",
    "Chiara", "Andrea", "Sara", "Davide", "Marta",
];

const ITALIAN_LAST_NAMES: &[&str] = &[
    "Rossi", "Russo", "Ferrari", "Esposito", "Bianchi",
    "Gallo", "Romano", "Colombo", "Rizzo", "Marino",
];

fn generate_fake_cf(name: &str) -> String {
    // Format: RRRLLL##L##C###L (16 chars)
    format!("{}{}70A01H501G",
        last[0..3].to_uppercase(),
        first[0..3].to_uppercase())
}
```

### Idempotent Seeding
```rust
pub async fn seed_database(pool: &SqlitePool, config: SeedConfig) -> Result<SeedReport> {
    // Check if already seeded
    if config.skip_if_exists {
        let count: (i32,) = sqlx::query_as("SELECT COUNT(*) FROM users")
            .fetch_one(pool).await?;

        if count.0 > 0 {
            return Ok(SeedReport { skipped: true, ..Default::default() });
        }
    }

    // Seed in dependency order
    seed_users(pool, config).await?;
    seed_servizi(pool, config).await?;
    seed_appuntamenti(pool, config).await?;

    Ok(report)
}
```

### Factory Pattern for Tests
```rust
pub struct ClienteFactory {
    pub id: i32,
    pub nome: String,
    pub email: String,
}

impl ClienteFactory {
    pub fn create() -> Self {
        static COUNTER: AtomicI32 = AtomicI32::new(1);
        let id = COUNTER.fetch_add(1, Ordering::SeqCst);

        ClienteFactory {
            id,
            nome: format!("Cliente {}", id),
            email: format!("cliente{}@example.com", id),
        }
    }

    pub fn with_nome(mut self, nome: &str) -> Self {
        self.nome = nome.to_string();
        self
    }
}
```

### Database Reset for Tests
```rust
pub async fn reset_test_db(pool: &SqlitePool) -> Result<()> {
    // Delete in reverse dependency order
    sqlx::query("DELETE FROM appuntamenti").execute(pool).await?;
    sqlx::query("DELETE FROM clienti").execute(pool).await?;
    sqlx::query("DELETE FROM sqlite_sequence").execute(pool).await?;
    Ok(())
}
```

---

## Environment Variables

```bash
# .env.development
TAURI_ENV=development

# .env.test
TAURI_ENV=test

# .env.demo
TAURI_ENV=demo
```

---

## Troubleshooting

| Problema | Soluzione |
|----------|-----------|
| Duplicate key error | Usa skip_if_exists |
| Foreign key violation | Rispetta ordine seeding |
| Seed ogni restart | Controlla COUNT(*) prima |
| Data non realistico | Usa Italian names/CF |

---

## Riferimenti
- File contesto: docs/context/CLAUDE-BACKEND.md
- Ricerca: test-data-manager.md (Enterprise guide)
