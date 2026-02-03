"""
Esempi di utilizzo dell'Audit Client per Voice Agent.

Questo file mostra come integrare il logging audit nel voice agent.
"""

from audit_client import (
    audit_client,
    AuditClient,
    AuditAction,
    GdprCategory,
    UserType,
    AuditSource,
)


def example_1_basic_usage():
    """Esempio 1: Uso base del singleton audit_client."""
    
    # Log creazione cliente
    audit_id = audit_client.log_client_creation(
        session_id="voice-session-123",
        cliente_id="cust-456",
        cliente_data={
            "nome": "Mario",
            "cognome": "Rossi",
            "telefono": "+391234567890",
            "email": "mario.rossi@example.com"
        }
    )
    print(f"Audit log created: {audit_id}")
    
    # Log creazione appuntamento
    audit_id = audit_client.log_booking_creation(
        session_id="voice-session-123",
        appuntamento_id="appt-789",
        booking_data={
            "cliente_id": "cust-456",
            "servizio": "Taglio",
            "data": "2025-03-15",
            "ora": "15:00"
        }
    )
    print(f"Booking audit log: {audit_id}")


def example_2_session_lifecycle():
    """Esempio 2: Logging lifecycle di una sessione."""
    session_id = "voice-session-abc"
    
    # Sessione avviata
    audit_client.log_session_start(
        session_id=session_id,
        phone_number="+391234567890",
        verticale_id="salone_bella_vita"
    )
    
    # ... durante la sessione ...
    
    # Sessione terminata
    audit_client.log_session_end(
        session_id=session_id,
        outcome="completed",  # o "escalated"
        turns_count=8
    )


def example_3_gdpr_operations():
    """Esempio 3: Operazioni GDPR."""
    
    # Aggiornamento consenso
    audit_client.log_consent_update(
        session_id="voice-session-123",
        cliente_id="cust-456",
        consenso_marketing=True,
        consenso_whatsapp=True,
        consenso_sms=False,
        consenso_email=True
    )
    
    # Visualizzazione dati cliente (accesso)
    audit_client.log_client_view(
        session_id="voice-session-123",
        cliente_id="cust-456",
        search_query="Rossi"
    )


def example_4_booking_operations():
    """Esempio 4: Operazioni su appuntamenti."""
    session_id = "voice-session-123"
    
    # Cancellazione
    audit_client.log_booking_cancellation(
        session_id=session_id,
        appuntamento_id="appt-789",
        booking_data={
            "servizio": "Taglio",
            "data": "2025-03-15",
            "ora": "15:00"
        }
    )
    
    # Spostamento
    audit_client.log_booking_reschedule(
        session_id=session_id,
        appuntamento_id="appt-789",
        old_data={
            "data": "2025-03-15",
            "ora": "15:00"
        },
        new_data={
            "data": "2025-03-20",
            "ora": "16:00"
        }
    )


def example_5_custom_operation():
    """Esempio 5: Operazione custom con log_operation."""
    
    audit_client.log_operation(
        session_id="voice-session-123",
        action=AuditAction.EXPORT,
        entity_type="client_list",
        entity_id="export-001",
        gdpr_category=GdprCategory.PERSONAL_DATA,
        legal_basis="legal_obligation",
        notes="Export clienti per contabilità"
    )


def example_6_multiple_instances():
    """Esempio 6: Uso di istanze multiple (thread-safe)."""
    
    # Per scenario con DB diverso
    audit_v2 = AuditClient(db_path="../src-tauri/fluxion_v2.db")
    
    audit_v2.log_client_creation(
        session_id="session-xyz",
        cliente_id="cust-999",
        cliente_data={"nome": "Test"}
    )


def example_7_integration_with_orchestrator():
    """
    Esempio 7: Pattern di integrazione nell'orchestrator.
    
    Vedere implementazione reale in orchestrator.py:
    - start_session() → log_session_start()
    - _create_client() → log_client_creation()
    - _create_booking() → log_booking_creation()
    - _cancel_booking() → log_booking_cancellation()
    - _reschedule_booking() → log_booking_reschedule()
    - _search_client() → log_client_view()
    - process() end → log_session_end()
    """
    pass


def example_8_decorator_usage():
    """Esempio 8: Uso del decorator (se necessario)."""
    from audit_client import log_voice_operation
    
    # Nota: Il decorator è più adatto per funzioni sync
    # Per async, meglio log esplicito
    
    @log_voice_operation(entity_type="cliente", action=AuditAction.CREATE)
    def create_client_sync(session_id: str, data: dict):
        # Simula creazione
        return {"id": "cust-123", **data}
    
    result = create_client_sync(
        session_id="test-session",
        data={"nome": "Mario", "cognome": "Rossi"}
    )


if __name__ == "__main__":
    print("Audit Client Usage Examples")
    print("=" * 50)
    
    print("\n1. Basic Usage:")
    example_1_basic_usage()
    
    print("\n2. Session Lifecycle:")
    example_2_session_lifecycle()
    
    print("\n3. GDPR Operations:")
    example_3_gdpr_operations()
    
    print("\n4. Booking Operations:")
    example_4_booking_operations()
    
    print("\n5. Custom Operation:")
    example_5_custom_operation()
    
    print("\nAll examples completed!")
