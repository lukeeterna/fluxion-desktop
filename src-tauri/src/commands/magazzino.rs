// ═══════════════════════════════════════════════════════════════════
// FLUXION - Magazzino Commands
// Articoli + movimenti carico/scarico + alert sottoscorta automatici
// WIP=1 magazzino: NON tocca licenze, Sara, payload firmato, encryption.
// ═══════════════════════════════════════════════════════════════════

use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use tauri::State;

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Articolo {
    pub id: String,
    pub nome: String,
    pub categoria: Option<String>,
    pub giacenza: i64,
    pub soglia_minima: i64,
    pub prezzo_acquisto: Option<f64>,
    pub prezzo_vendita: Option<f64>,
    pub ean: Option<String>,
    pub fornitore_id: Option<String>,
    pub alert_notificato: i64,
    pub attivo: i64,
    pub created_at: String,
    pub updated_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct MovimentoMagazzino {
    pub id: String,
    pub articolo_id: String,
    pub tipo: String,
    pub quantita: i64,
    pub causale: Option<String>,
    pub riferimento: Option<String>,
    pub created_at: String,
}

// ───────────────────────────────────────────────────────────────────
// Comandi - CRUD articoli
// ───────────────────────────────────────────────────────────────────

/// Crea un nuovo articolo di magazzino
#[tauri::command]
pub async fn articolo_crea(
    pool: State<'_, SqlitePool>,
    nome: String,
    categoria: Option<String>,
    soglia_minima: i64,
    prezzo_acquisto: Option<f64>,
    prezzo_vendita: Option<f64>,
    ean: Option<String>,
    fornitore_id: Option<String>,
) -> Result<Articolo, String> {
    let id = uuid::Uuid::new_v4().to_string();

    sqlx::query(
        r#"
        INSERT INTO articoli (
            id, nome, categoria, soglia_minima,
            prezzo_acquisto, prezzo_vendita, ean, fornitore_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        "#,
    )
    .bind(&id)
    .bind(&nome)
    .bind(&categoria)
    .bind(soglia_minima)
    .bind(prezzo_acquisto)
    .bind(prezzo_vendita)
    .bind(&ean)
    .bind(&fornitore_id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Errore creazione articolo: {}", e))?;

    fetch_articolo(pool.inner(), &id).await
}

/// Aggiorna i campi anagrafici di un articolo (NON la giacenza: quella passa dai movimenti)
#[tauri::command]
pub async fn articolo_aggiorna(
    pool: State<'_, SqlitePool>,
    id: String,
    nome: String,
    categoria: Option<String>,
    soglia_minima: i64,
    prezzo_acquisto: Option<f64>,
    prezzo_vendita: Option<f64>,
    ean: Option<String>,
    fornitore_id: Option<String>,
) -> Result<Articolo, String> {
    sqlx::query(
        r#"
        UPDATE articoli SET
            nome = ?, categoria = ?, soglia_minima = ?,
            prezzo_acquisto = ?, prezzo_vendita = ?, ean = ?, fornitore_id = ?,
            updated_at = datetime('now')
        WHERE id = ? AND attivo = 1
        "#,
    )
    .bind(&nome)
    .bind(&categoria)
    .bind(soglia_minima)
    .bind(prezzo_acquisto)
    .bind(prezzo_vendita)
    .bind(&ean)
    .bind(&fornitore_id)
    .bind(&id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Errore aggiornamento articolo: {}", e))?;

    fetch_articolo(pool.inner(), &id).await
}

/// Lista articoli attivi
#[tauri::command]
pub async fn articolo_lista(pool: State<'_, SqlitePool>) -> Result<Vec<Articolo>, String> {
    sqlx::query_as::<_, Articolo>(
        "SELECT * FROM articoli WHERE attivo = 1 ORDER BY nome COLLATE NOCASE ASC",
    )
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Errore lettura articoli: {}", e))
}

/// Soft-delete di un articolo (attivo = 0)
#[tauri::command]
pub async fn articolo_elimina(pool: State<'_, SqlitePool>, id: String) -> Result<(), String> {
    sqlx::query("UPDATE articoli SET attivo = 0, updated_at = datetime('now') WHERE id = ?")
        .bind(&id)
        .execute(pool.inner())
        .await
        .map_err(|e| format!("Errore eliminazione articolo: {}", e))?;
    Ok(())
}

/// Imposta la soglia minima e riallinea l'alert in base alla giacenza corrente
#[tauri::command]
pub async fn articolo_set_soglia(
    pool: State<'_, SqlitePool>,
    id: String,
    soglia_minima: i64,
) -> Result<Articolo, String> {
    // alert_notificato coerente con la nuova soglia:
    // sotto/uguale -> 1 (alert attivo), sopra -> 0 (resettato).
    sqlx::query(
        r#"
        UPDATE articoli SET
            soglia_minima = ?,
            alert_notificato = CASE WHEN giacenza <= ? THEN 1 ELSE 0 END,
            updated_at = datetime('now')
        WHERE id = ? AND attivo = 1
        "#,
    )
    .bind(soglia_minima)
    .bind(soglia_minima)
    .bind(&id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Errore impostazione soglia: {}", e))?;

    fetch_articolo(pool.inner(), &id).await
}

// ───────────────────────────────────────────────────────────────────
// Comandi - Movimenti (carico/scarico) in transazione
// ───────────────────────────────────────────────────────────────────

/// Registra un movimento (carico/scarico) aggiornando la giacenza in UNA transazione.
/// carico  -> giacenza += quantita
/// scarico -> giacenza -= quantita (Err+rollback se porterebbe sotto zero)
/// Gestisce anche l'anti-spam alert (alert_notificato) nella stessa transazione.
#[tauri::command]
pub async fn movimento_registra(
    pool: State<'_, SqlitePool>,
    articolo_id: String,
    tipo: String,
    quantita: i64,
    causale: Option<String>,
    riferimento: Option<String>,
) -> Result<MovimentoMagazzino, String> {
    if quantita <= 0 {
        return Err("La quantita deve essere maggiore di zero".to_string());
    }
    if tipo != "carico" && tipo != "scarico" {
        return Err(format!("Tipo movimento non valido: {} (atteso 'carico'|'scarico')", tipo));
    }

    let mut tx = pool
        .begin()
        .await
        .map_err(|e| format!("Errore apertura transazione: {}", e))?;

    // Leggi stato corrente dell'articolo (lock implicito nella tx)
    let (giacenza_attuale, soglia, attivo): (i64, i64, i64) =
        sqlx::query_as("SELECT giacenza, soglia_minima, attivo FROM articoli WHERE id = ?")
            .bind(&articolo_id)
            .fetch_optional(&mut *tx)
            .await
            .map_err(|e| format!("Errore lettura articolo: {}", e))?
            .ok_or_else(|| "Articolo non trovato".to_string())?;

    if attivo != 1 {
        return Err("Articolo non attivo".to_string());
    }

    let nuova_giacenza = match tipo.as_str() {
        "carico" => giacenza_attuale + quantita,
        "scarico" => {
            let n = giacenza_attuale - quantita;
            if n < 0 {
                // rollback automatico al drop di tx
                return Err(format!(
                    "Giacenza insufficiente: disponibili {}, richiesti {}",
                    giacenza_attuale, quantita
                ));
            }
            n
        }
        _ => unreachable!(),
    };

    // Anti-spam alert:
    // - scesa a <= soglia e alert era 0 -> 1 (alert "scattato", da emettere)
    // - risalita sopra soglia          -> 0 (reset, riemettibile in futuro)
    // - altrimenti invariato
    let nuovo_alert: i64 = if nuova_giacenza <= soglia {
        1
    } else {
        0
    };

    sqlx::query(
        r#"
        UPDATE articoli SET
            giacenza = ?,
            alert_notificato = ?,
            updated_at = datetime('now')
        WHERE id = ?
        "#,
    )
    .bind(nuova_giacenza)
    .bind(nuovo_alert)
    .bind(&articolo_id)
    .execute(&mut *tx)
    .await
    .map_err(|e| format!("Errore aggiornamento giacenza: {}", e))?;

    // TODO(magazzino-3c): notifica email titolare — riusare SMTP esistente via nuova fn
    // Python send_lowstock_alert + endpoint bridge. Decisione founder pendente.
    // NON implementare qui. L'alert scatta quando alert_notificato passa 0 -> 1.

    let id = uuid::Uuid::new_v4().to_string();
    sqlx::query(
        r#"
        INSERT INTO movimenti_magazzino (
            id, articolo_id, tipo, quantita, causale, riferimento
        ) VALUES (?, ?, ?, ?, ?, ?)
        "#,
    )
    .bind(&id)
    .bind(&articolo_id)
    .bind(&tipo)
    .bind(quantita)
    .bind(&causale)
    .bind(&riferimento)
    .execute(&mut *tx)
    .await
    .map_err(|e| format!("Errore inserimento movimento: {}", e))?;

    let movimento = sqlx::query_as::<_, MovimentoMagazzino>(
        "SELECT * FROM movimenti_magazzino WHERE id = ?",
    )
    .bind(&id)
    .fetch_one(&mut *tx)
    .await
    .map_err(|e| format!("Errore lettura movimento: {}", e))?;

    tx.commit()
        .await
        .map_err(|e| format!("Errore commit transazione: {}", e))?;

    Ok(movimento)
}

// ───────────────────────────────────────────────────────────────────
// Comandi - Alert sottoscorta
// ───────────────────────────────────────────────────────────────────

/// Articoli attivi sottoscorta (giacenza <= soglia_minima)
#[tauri::command]
pub async fn magazzino_sottoscorta(
    pool: State<'_, SqlitePool>,
) -> Result<Vec<Articolo>, String> {
    sqlx::query_as::<_, Articolo>(
        r#"
        SELECT * FROM articoli
        WHERE attivo = 1 AND giacenza <= soglia_minima
        ORDER BY (soglia_minima - giacenza) DESC, nome COLLATE NOCASE ASC
        "#,
    )
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Errore lettura sottoscorta: {}", e))
}

/// Conteggio articoli sottoscorta (badge sidebar)
#[tauri::command]
pub async fn magazzino_alert_count(pool: State<'_, SqlitePool>) -> Result<i64, String> {
    sqlx::query_scalar::<_, i64>(
        "SELECT COUNT(*) FROM articoli WHERE attivo = 1 AND giacenza <= soglia_minima",
    )
    .fetch_one(pool.inner())
    .await
    .map_err(|e| format!("Errore conteggio alert: {}", e))
}

/// Ricalcola alert_notificato per tutti gli articoli attivi (chiamare al boot).
/// Idempotente: allinea il flag allo stato giacenza vs soglia. Ritorna il count sottoscorta.
#[tauri::command]
pub async fn magazzino_recompute_alerts(pool: State<'_, SqlitePool>) -> Result<i64, String> {
    sqlx::query(
        r#"
        UPDATE articoli
        SET alert_notificato = CASE WHEN giacenza <= soglia_minima THEN 1 ELSE 0 END
        WHERE attivo = 1
        "#,
    )
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Errore recompute alert: {}", e))?;

    magazzino_alert_count(pool).await
}

// ───────────────────────────────────────────────────────────────────
// Helpers
// ───────────────────────────────────────────────────────────────────

async fn fetch_articolo(pool: &SqlitePool, id: &str) -> Result<Articolo, String> {
    sqlx::query_as::<_, Articolo>("SELECT * FROM articoli WHERE id = ?")
        .bind(id)
        .fetch_one(pool)
        .await
        .map_err(|e| format!("Errore lettura articolo: {}", e))
}

// ───────────────────────────────────────────────────────────────────
// Tests (sqlx in-memory)
// ───────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    // Schema inline (sottoinsieme di 042_magazzino.sql). FK suppliers omessa:
    // i test non la esercitano e la sua assenza non altera la logica testata.
    async fn setup() -> SqlitePool {
        let pool = SqlitePool::connect(":memory:").await.unwrap();
        sqlx::query("PRAGMA foreign_keys=ON")
            .execute(&pool)
            .await
            .unwrap();
        sqlx::query(
            r#"
            CREATE TABLE articoli (
                id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                nome TEXT NOT NULL,
                categoria TEXT,
                giacenza INTEGER NOT NULL DEFAULT 0,
                soglia_minima INTEGER NOT NULL DEFAULT 0,
                prezzo_acquisto REAL,
                prezzo_vendita REAL,
                ean TEXT,
                fornitore_id TEXT,
                alert_notificato INTEGER NOT NULL DEFAULT 0,
                attivo INTEGER NOT NULL DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            )
            "#,
        )
        .execute(&pool)
        .await
        .unwrap();
        sqlx::query(
            r#"
            CREATE TABLE movimenti_magazzino (
                id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                articolo_id TEXT NOT NULL REFERENCES articoli(id),
                tipo TEXT NOT NULL,
                quantita INTEGER NOT NULL,
                causale TEXT,
                riferimento TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
            "#,
        )
        .execute(&pool)
        .await
        .unwrap();
        pool
    }

    async fn insert_articolo(pool: &SqlitePool, nome: &str, giacenza: i64, soglia: i64) -> String {
        let id = uuid::Uuid::new_v4().to_string();
        sqlx::query(
            "INSERT INTO articoli (id, nome, giacenza, soglia_minima) VALUES (?, ?, ?, ?)",
        )
        .bind(&id)
        .bind(nome)
        .bind(giacenza)
        .bind(soglia)
        .execute(pool)
        .await
        .unwrap();
        id
    }

    async fn registra(
        pool: &SqlitePool,
        articolo_id: &str,
        tipo: &str,
        q: i64,
    ) -> Result<MovimentoMagazzino, String> {
        // Replica della logica di movimento_registra senza il wrapper Tauri State.
        if q <= 0 {
            return Err("La quantita deve essere maggiore di zero".to_string());
        }
        if tipo != "carico" && tipo != "scarico" {
            return Err(format!("Tipo movimento non valido: {}", tipo));
        }
        let mut tx = pool.begin().await.unwrap();
        let (giacenza_attuale, soglia, attivo): (i64, i64, i64) =
            sqlx::query_as("SELECT giacenza, soglia_minima, attivo FROM articoli WHERE id = ?")
                .bind(articolo_id)
                .fetch_optional(&mut *tx)
                .await
                .unwrap()
                .ok_or_else(|| "Articolo non trovato".to_string())?;
        if attivo != 1 {
            return Err("Articolo non attivo".to_string());
        }
        let nuova_giacenza = match tipo {
            "carico" => giacenza_attuale + q,
            "scarico" => {
                let n = giacenza_attuale - q;
                if n < 0 {
                    return Err(format!(
                        "Giacenza insufficiente: disponibili {}, richiesti {}",
                        giacenza_attuale, q
                    ));
                }
                n
            }
            _ => unreachable!(),
        };
        let nuovo_alert: i64 = if nuova_giacenza <= soglia { 1 } else { 0 };
        sqlx::query(
            "UPDATE articoli SET giacenza = ?, alert_notificato = ?, updated_at = datetime('now') WHERE id = ?",
        )
        .bind(nuova_giacenza)
        .bind(nuovo_alert)
        .bind(articolo_id)
        .execute(&mut *tx)
        .await
        .unwrap();
        let id = uuid::Uuid::new_v4().to_string();
        sqlx::query(
            "INSERT INTO movimenti_magazzino (id, articolo_id, tipo, quantita) VALUES (?, ?, ?, ?)",
        )
        .bind(&id)
        .bind(articolo_id)
        .bind(tipo)
        .bind(q)
        .execute(&mut *tx)
        .await
        .unwrap();
        let m = sqlx::query_as::<_, MovimentoMagazzino>(
            "SELECT * FROM movimenti_magazzino WHERE id = ?",
        )
        .bind(&id)
        .fetch_one(&mut *tx)
        .await
        .unwrap();
        tx.commit().await.unwrap();
        Ok(m)
    }

    async fn giacenza_di(pool: &SqlitePool, id: &str) -> i64 {
        sqlx::query_scalar::<_, i64>("SELECT giacenza FROM articoli WHERE id = ?")
            .bind(id)
            .fetch_one(pool)
            .await
            .unwrap()
    }

    async fn alert_di(pool: &SqlitePool, id: &str) -> i64 {
        sqlx::query_scalar::<_, i64>("SELECT alert_notificato FROM articoli WHERE id = ?")
            .bind(id)
            .fetch_one(pool)
            .await
            .unwrap()
    }

    #[tokio::test]
    async fn test_carico_scarico_giacenza() {
        let pool = setup().await;
        let id = insert_articolo(&pool, "Shampoo", 0, 0).await;

        registra(&pool, &id, "carico", 10).await.unwrap();
        assert_eq!(giacenza_di(&pool, &id).await, 10);

        registra(&pool, &id, "scarico", 3).await.unwrap();
        assert_eq!(giacenza_di(&pool, &id).await, 7);
    }

    #[tokio::test]
    async fn test_scarico_sotto_zero_rollback() {
        let pool = setup().await;
        let id = insert_articolo(&pool, "Balsamo", 5, 0).await;

        let res = registra(&pool, &id, "scarico", 8).await;
        assert!(res.is_err(), "scarico oltre giacenza deve fallire");
        // Giacenza invariata (rollback)
        assert_eq!(giacenza_di(&pool, &id).await, 5);
        // Nessun movimento inserito
        let count: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM movimenti_magazzino")
            .fetch_one(&pool)
            .await
            .unwrap();
        assert_eq!(count, 0);
    }

    #[tokio::test]
    async fn test_sottoscorta_query() {
        let pool = setup().await;
        // sotto soglia
        insert_articolo(&pool, "A", 2, 5).await;
        // uguale soglia (incluso: <=)
        insert_articolo(&pool, "B", 5, 5).await;
        // sopra soglia (escluso)
        insert_articolo(&pool, "C", 10, 5).await;

        let sotto = sqlx::query_as::<_, Articolo>(
            "SELECT * FROM articoli WHERE attivo = 1 AND giacenza <= soglia_minima ORDER BY nome",
        )
        .fetch_all(&pool)
        .await
        .unwrap();
        assert_eq!(sotto.len(), 2);
        let nomi: Vec<&str> = sotto.iter().map(|a| a.nome.as_str()).collect();
        assert!(nomi.contains(&"A"));
        assert!(nomi.contains(&"B"));
        assert!(!nomi.contains(&"C"));
    }

    #[tokio::test]
    async fn test_antispam_alert() {
        let pool = setup().await;
        let id = insert_articolo(&pool, "Cera", 10, 5).await;
        assert_eq!(alert_di(&pool, &id).await, 0);

        // scarico che porta a 4 (<=5) -> alert scatta a 1
        registra(&pool, &id, "scarico", 6).await.unwrap();
        assert_eq!(giacenza_di(&pool, &id).await, 4);
        assert_eq!(alert_di(&pool, &id).await, 1);

        // ulteriore scarico a 2 (ancora <=5) -> resta 1, non rioscilla
        registra(&pool, &id, "scarico", 2).await.unwrap();
        assert_eq!(giacenza_di(&pool, &id).await, 2);
        assert_eq!(alert_di(&pool, &id).await, 1);

        // carico che risale a 12 (>5) -> alert torna 0
        registra(&pool, &id, "carico", 10).await.unwrap();
        assert_eq!(giacenza_di(&pool, &id).await, 12);
        assert_eq!(alert_di(&pool, &id).await, 0);
    }
}
