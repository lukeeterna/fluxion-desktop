"""Audit client for voice agent GDPR compliance.

Questo modulo fornisce un client per il logging audit trail delle operazioni
effettuate dal voice agent, garantendo conformità GDPR.

Usage:
    from audit_client import audit_client
    
    # Log creazione cliente
    audit_client.log_client_creation(
        session_id="sess-123",
        cliente_id="cust-456",
        cliente_data={"nome": "Mario", "cognome": "Rossi", "telefono": "+39..."}
    )
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from enum import Enum
import sqlite3
import threading
import logging

logger = logging.getLogger(__name__)


class UserType(str, Enum):
    """Tipo di utente che effettua l'operazione."""
    VOICE_SESSION = "voice_session"
    SYSTEM = "system"
    OPERATOR = "operator"


class AuditAction(str, Enum):
    """Tipo di azione audit."""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    VIEW = "VIEW"
    EXPORT = "EXPORT"
    ANONYMIZE = "ANONYMIZE"


class GdprCategory(str, Enum):
    """Categoria GDPR dei dati."""
    PERSONAL_DATA = "personal_data"
    CONSENT = "consent"
    BOOKING = "booking"
    VOICE_SESSION = "voice_session"
    FINANCIAL_DATA = "financial_data"
    HEALTH_DATA = "health_data"


class AuditSource(str, Enum):
    """Sorgente dell'operazione audit."""
    VOICE = "voice"
    API = "api"
    SYSTEM = "system"
    ADMIN = "admin"


class AuditClient:
    """Client per logging audit trail da voice agent.
    
    Features:
        - Thread-safe SQLite connections (una per thread)
        - Retention policy configurabile per categoria GDPR
        - Fallback su defaults se DB non disponibile
        - Campi GDPR: legal_basis, retention_until
    
    Example:
        >>> client = AuditClient()
        >>> audit_id = client.log_client_creation(
        ...     session_id="sess-123",
        ...     cliente_id="cust-456",
        ...     cliente_data={"nome": "Mario", "telefono": "+39123..."}
        ... )
        >>> print(f"Audit logged: {audit_id}")
    """
    
    # Retention defaults (in giorni)
    DEFAULT_RETENTION = {
        GdprCategory.PERSONAL_DATA: 2555,  # 7 anni
        GdprCategory.CONSENT: 1825,        # 5 anni
        GdprCategory.BOOKING: 1095,        # 3 anni
        GdprCategory.VOICE_SESSION: 365,   # 1 anno
        GdprCategory.FINANCIAL_DATA: 2555, # 7 anni
        GdprCategory.HEALTH_DATA: 2555,    # 7 anni
    }
    
    def __init__(self, db_path: str = "../src-tauri/fluxion.db"):
        """Inizializza il client audit.
        
        Args:
            db_path: Percorso al database SQLite (default: ../src-tauri/fluxion.db)
        """
        self.db_path = db_path
        self._local = threading.local()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local DB connection.
        
        SQLite non supporta connessioni condivise tra thread,
        quindi creiamo una connessione per thread usando threading.local().
        
        Returns:
            sqlite3.Connection: Connessione al database per il thread corrente
        """
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(self.db_path)
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection
    
    def _close_connection(self):
        """Close thread-local connection (call on thread exit)."""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
    
    def log_operation(
        self,
        session_id: str,
        action: AuditAction,
        entity_type: str,
        entity_id: str,
        data_before: Optional[Dict] = None,
        data_after: Optional[Dict] = None,
        gdpr_category: GdprCategory = GdprCategory.VOICE_SESSION,
        legal_basis: str = "consent",
        user_type: UserType = UserType.VOICE_SESSION,
        source: AuditSource = AuditSource.VOICE,
        notes: Optional[str] = None
    ) -> Optional[str]:
        """Log operazione CRUD su entità.
        
        Args:
            session_id: ID della sessione voice
            action: Tipo di azione (CREATE, UPDATE, DELETE, VIEW)
            entity_type: Tipo di entità (cliente, appuntamento, etc.)
            entity_id: ID dell'entità modificata
            data_before: Dati precedenti (per UPDATE/DELETE)
            data_after: Dati nuovi (per CREATE/UPDATE)
            gdpr_category: Categoria GDPR dei dati
            legal_basis: Base giuridica GDPR (consent, contract, legal_obligation, etc.)
            user_type: Tipo di utente
            source: Sorgente dell'operazione
            notes: Note aggiuntive
        
        Returns:
            str: ID dell'audit log creato, o None se il logging fallisce
        """
        try:
            # Calcola retention
            retention_days = self._get_retention_days(gdpr_category)
            retention_until = datetime.now() + timedelta(days=retention_days)
            
            # Calcola changed_fields se UPDATE
            changed_fields = None
            if action == AuditAction.UPDATE and data_before and data_after:
                changed_fields = json.dumps(self._calculate_diff(data_before, data_after))
            
            audit_id = str(uuid.uuid4())
            
            conn = self._get_connection()
            conn.execute("""
                INSERT INTO audit_log (
                    id, timestamp, user_id, user_type, action,
                    entity_type, entity_id, data_before, data_after,
                    changed_fields, gdpr_category, source, legal_basis,
                    retention_until, notes
                ) VALUES (?, datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                audit_id, session_id, user_type.value, action.value, 
                entity_type, entity_id,
                json.dumps(data_before, ensure_ascii=False) if data_before else None,
                json.dumps(data_after, ensure_ascii=False) if data_after else None,
                changed_fields,
                gdpr_category.value, source.value, legal_basis,
                retention_until.isoformat(),
                notes
            ))
            conn.commit()
            
            logger.debug(f"[AUDIT] Logged {action.value} on {entity_type}:{entity_id}")
            return audit_id
            
        except sqlite3.Error as e:
            logger.error(f"[AUDIT] SQLite error logging operation: {e}")
            return None
        except Exception as e:
            logger.error(f"[AUDIT] Unexpected error logging operation: {e}")
            return None
    
    def log_client_creation(
        self,
        session_id: str,
        cliente_id: str,
        cliente_data: Dict[str, Any],
        legal_basis: str = "consent"
    ) -> Optional[str]:
        """Log creazione cliente da voice.
        
        Args:
            session_id: ID della sessione voice
            cliente_id: ID del cliente creato
            cliente_data: Dati del cliente (nome, cognome, telefono, etc.)
            legal_basis: Base giuridica (default: consent)
        
        Returns:
            str: ID dell'audit log, o None se fallisce
        """
        # Sanitizza dati sensibili per l'audit log
        audit_data = self._sanitize_client_data(cliente_data)
        
        return self.log_operation(
            session_id=session_id,
            action=AuditAction.CREATE,
            entity_type="cliente",
            entity_id=cliente_id,
            data_after=audit_data,
            gdpr_category=GdprCategory.PERSONAL_DATA,
            legal_basis=legal_basis,
            notes="Cliente creato via Voice Agent"
        )
    
    def log_booking_creation(
        self,
        session_id: str,
        appuntamento_id: str,
        booking_data: Dict[str, Any],
        legal_basis: str = "contract"
    ) -> Optional[str]:
        """Log creazione appuntamento da voice.
        
        Args:
            session_id: ID della sessione voice
            appuntamento_id: ID dell'appuntamento creato
            booking_data: Dati dell'appuntamento (data, ora, servizio, etc.)
            legal_basis: Base giuridica (default: contract)
        
        Returns:
            str: ID dell'audit log, o None se fallisce
        """
        return self.log_operation(
            session_id=session_id,
            action=AuditAction.CREATE,
            entity_type="appuntamento",
            entity_id=appuntamento_id,
            data_after=booking_data,
            gdpr_category=GdprCategory.BOOKING,
            legal_basis=legal_basis,
            notes="Appuntamento creato via Voice Agent"
        )
    
    def log_booking_cancellation(
        self,
        session_id: str,
        appuntamento_id: str,
        booking_data: Dict[str, Any],
        legal_basis: str = "contract"
    ) -> Optional[str]:
        """Log cancellazione appuntamento.
        
        Args:
            session_id: ID della sessione voice
            appuntamento_id: ID dell'appuntamento cancellato
            booking_data: Dati dell'appuntamento cancellato
            legal_basis: Base giuridica (default: contract)
        
        Returns:
            str: ID dell'audit log, o None se fallisce
        """
        return self.log_operation(
            session_id=session_id,
            action=AuditAction.DELETE,
            entity_type="appuntamento",
            entity_id=appuntamento_id,
            data_before=booking_data,
            gdpr_category=GdprCategory.BOOKING,
            legal_basis=legal_basis,
            notes="Appuntamento cancellato via Voice Agent"
        )
    
    def log_booking_reschedule(
        self,
        session_id: str,
        appuntamento_id: str,
        old_data: Dict[str, Any],
        new_data: Dict[str, Any],
        legal_basis: str = "contract"
    ) -> Optional[str]:
        """Log spostamento appuntamento.
        
        Args:
            session_id: ID della sessione voice
            appuntamento_id: ID dell'appuntamento spostato
            old_data: Dati precedenti (data/ora vecchia)
            new_data: Dati nuovi (data/ora nuova)
            legal_basis: Base giuridica (default: contract)
        
        Returns:
            str: ID dell'audit log, o None se fallisce
        """
        return self.log_operation(
            session_id=session_id,
            action=AuditAction.UPDATE,
            entity_type="appuntamento",
            entity_id=appuntamento_id,
            data_before=old_data,
            data_after=new_data,
            gdpr_category=GdprCategory.BOOKING,
            legal_basis=legal_basis,
            notes="Appuntamento spostato via Voice Agent"
        )
    
    def log_consent_update(
        self,
        session_id: str,
        cliente_id: str,
        consenso_marketing: bool,
        consenso_whatsapp: bool,
        consenso_sms: Optional[bool] = None,
        consenso_email: Optional[bool] = None,
        legal_basis: str = "consent"
    ) -> Optional[str]:
        """Log aggiornamento consenso GDPR.
        
        Args:
            session_id: ID della sessione voice
            cliente_id: ID del cliente
            consenso_marketing: Stato consenso marketing
            consenso_whatsapp: Stato consenso WhatsApp
            consenso_sms: Stato consenso SMS (optional)
            consenso_email: Stato consenso email (optional)
            legal_basis: Base giuridica (default: consent)
        
        Returns:
            str: ID dell'audit log, o None se fallisce
        """
        consent_data = {
            "consenso_marketing": consenso_marketing,
            "consenso_whatsapp": consenso_whatsapp,
            "timestamp": datetime.now().isoformat()
        }
        if consenso_sms is not None:
            consent_data["consenso_sms"] = consenso_sms
        if consenso_email is not None:
            consent_data["consenso_email"] = consenso_email
        
        return self.log_operation(
            session_id=session_id,
            action=AuditAction.UPDATE,
            entity_type="consenso",
            entity_id=cliente_id,
            data_after=consent_data,
            gdpr_category=GdprCategory.CONSENT,
            legal_basis=legal_basis,
            notes="Consenso GDPR aggiornato via Voice Agent"
        )
    
    def log_client_view(
        self,
        session_id: str,
        cliente_id: str,
        search_query: Optional[str] = None,
        legal_basis: str = "contract"
    ) -> Optional[str]:
        """Log visualizzazione dati cliente.
        
        Args:
            session_id: ID della sessione voice
            cliente_id: ID del cliente visualizzato
            search_query: Query di ricerca usata (se applicabile)
            legal_basis: Base giuridica (default: contract)
        
        Returns:
            str: ID dell'audit log, o None se fallisce
        """
        notes = "Accesso dati cliente via Voice Agent"
        if search_query:
            notes += f" (ricerca: '{search_query}')"
        
        return self.log_operation(
            session_id=session_id,
            action=AuditAction.VIEW,
            entity_type="cliente",
            entity_id=cliente_id,
            gdpr_category=GdprCategory.PERSONAL_DATA,
            legal_basis=legal_basis,
            notes=notes
        )
    
    def log_session_start(
        self,
        session_id: str,
        phone_number: Optional[str] = None,
        verticale_id: Optional[str] = None
    ) -> Optional[str]:
        """Log inizio sessione voice.
        
        Args:
            session_id: ID della sessione voice
            phone_number: Numero di telefono del chiamante (opzionale)
            verticale_id: ID della verticale/business
        
        Returns:
            str: ID dell'audit log, o None se fallisce
        """
        session_data = {
            "session_id": session_id,
            "started_at": datetime.now().isoformat(),
            "verticale_id": verticale_id,
        }
        if phone_number:
            # Maschera il numero per privacy
            session_data["phone_masked"] = self._mask_phone(phone_number)
        
        return self.log_operation(
            session_id=session_id,
            action=AuditAction.CREATE,
            entity_type="voice_session",
            entity_id=session_id,
            data_after=session_data,
            gdpr_category=GdprCategory.VOICE_SESSION,
            legal_basis="legitimate_interest",
            notes="Sessione voice avviata"
        )
    
    def log_session_end(
        self,
        session_id: str,
        outcome: str = "completed",
        turns_count: int = 0,
        escalation_reason: Optional[str] = None
    ) -> Optional[str]:
        """Log fine sessione voice.
        
        Args:
            session_id: ID della sessione voice
            outcome: Esito della sessione (completed, escalated, etc.)
            turns_count: Numero di turni di conversazione
            escalation_reason: Motivo escalation (se applicabile)
        
        Returns:
            str: ID dell'audit log, o None se fallisce
        """
        session_data = {
            "session_id": session_id,
            "ended_at": datetime.now().isoformat(),
            "outcome": outcome,
            "turns_count": turns_count,
        }
        if escalation_reason:
            session_data["escalation_reason"] = escalation_reason
        
        return self.log_operation(
            session_id=session_id,
            action=AuditAction.UPDATE,
            entity_type="voice_session",
            entity_id=session_id,
            data_after=session_data,
            gdpr_category=GdprCategory.VOICE_SESSION,
            legal_basis="legitimate_interest",
            notes=f"Sessione voice terminata: {outcome}"
        )
    
    def _get_retention_days(self, category: GdprCategory) -> int:
        """Get retention days from DB settings o default.
        
        Args:
            category: Categoria GDPR
        
        Returns:
            int: Giorni di retention
        """
        try:
            conn = self._get_connection()
            row = conn.execute(
                "SELECT value FROM gdpr_settings WHERE key = ?",
                (f"retention_{category.value}",)
            ).fetchone()
            if row:
                return int(row["value"])
        except sqlite3.Error as e:
            logger.debug(f"[AUDIT] Could not load retention from DB, using defaults: {e}")
        except Exception as e:
            logger.debug(f"[AUDIT] Unexpected error loading retention: {e}")
        
        # Fallback ai default
        return self.DEFAULT_RETENTION.get(category, 365)
    
    def _calculate_diff(self, before: Dict, after: Dict) -> list:
        """Calculate changed fields between two dicts.
        
        Args:
            before: Dizionario dati precedenti
            after: Dizionario dati nuovi
        
        Returns:
            list: Lista dei campi modificati
        """
        changed = []
        all_keys = set(before.keys()) | set(after.keys())
        
        for key in all_keys:
            if key.startswith('_'):  # Skip private fields
                continue
            if before.get(key) != after.get(key):
                changed.append(key)
        
        return changed
    
    def _sanitize_client_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitizza dati cliente per audit log.
        
        Maschera dati sensibili come numero di telefono completo.
        
        Args:
            data: Dati cliente originali
        
        Returns:
            Dict: Dati sanitizzati
        """
        sanitized = {}
        for key, value in data.items():
            if key in ('telefono', 'phone', 'mobile') and isinstance(value, str):
                sanitized[key] = self._mask_phone(value)
            elif key in ('email',) and isinstance(value, str) and '@' in value:
                sanitized[key] = self._mask_email(value)
            else:
                sanitized[key] = value
        return sanitized
    
    def _mask_phone(self, phone: str) -> str:
        """Maschera numero di telefono mostrando solo ultime 4 cifre.
        
        Args:
            phone: Numero di telefono
        
        Returns:
            str: Numero mascherato (es. "+39******1234")
        """
        digits = ''.join(c for c in phone if c.isdigit())
        if len(digits) >= 4:
            return '*' * (len(phone) - 4) + phone[-4:]
        return '*' * len(phone)
    
    def _mask_email(self, email: str) -> str:
        """Maschera email mostrando solo dominio.
        
        Args:
            email: Indirizzo email
        
        Returns:
            str: Email mascherata (es. "m***@example.com")
        """
        if '@' not in email:
            return '*' * len(email)
        local, domain = email.split('@', 1)
        if len(local) <= 1:
            return f"{local}***@{domain}"
        return f"{local[0]}***@{domain}"


# Singleton instance
audit_client = AuditClient()


def log_voice_operation(entity_type: str, action: AuditAction = AuditAction.CREATE):
    """Decorator per auto-log operazioni voice.
    
    Usage:
        @log_voice_operation(entity_type="cliente")
        async def create_client(session_id, cliente_data):
            # ... creazione cliente ...
            return cliente_id
    
    Args:
        entity_type: Tipo di entità
        action: Tipo di azione
    
    Returns:
        Decorator function
    """
    def decorator(func):
        import functools
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Estrai session_id dai kwargs o args
            session_id = kwargs.get('session_id', 'unknown')
            
            try:
                result = await func(*args, **kwargs)
                
                # Log success se result contiene ID
                if isinstance(result, dict):
                    entity_id = result.get('id') or result.get('cliente_id') or result.get('appuntamento_id')
                    if entity_id:
                        audit_client.log_operation(
                            session_id=session_id,
                            action=action,
                            entity_type=entity_type,
                            entity_id=entity_id,
                            data_after=result,
                            notes=f"{action.value} {entity_type} via {func.__name__}"
                        )
                
                return result
                
            except Exception as e:
                # Log error
                audit_client.log_operation(
                    session_id=session_id,
                    action=action,
                    entity_type=entity_type,
                    entity_id="error",
                    notes=f"Error in {func.__name__}: {str(e)}"
                )
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            session_id = kwargs.get('session_id', 'unknown')
            
            try:
                result = func(*args, **kwargs)
                
                if isinstance(result, dict):
                    entity_id = result.get('id') or result.get('cliente_id') or result.get('appuntamento_id')
                    if entity_id:
                        audit_client.log_operation(
                            session_id=session_id,
                            action=action,
                            entity_type=entity_type,
                            entity_id=entity_id,
                            data_after=result,
                            notes=f"{action.value} {entity_type} via {func.__name__}"
                        )
                
                return result
                
            except Exception as e:
                audit_client.log_operation(
                    session_id=session_id,
                    action=action,
                    entity_type=entity_type,
                    entity_id="error",
                    notes=f"Error in {func.__name__}: {str(e)}"
                )
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# Import asyncio qui per evitare circular import
import asyncio
