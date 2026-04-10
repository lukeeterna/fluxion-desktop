"""
FLUXION Voice Agent — Escalation Manager (E5)

Generates structured context handoff when escalating to human operator.
Provides the operator with a summary of what Sara collected so far.
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def build_escalation_summary(context: Any, reason: str = "richiesta utente") -> Dict[str, Any]:
    """
    Build a structured escalation summary from booking context.

    Args:
        context: BookingContext with collected fields
        reason: Why escalation was triggered

    Returns:
        Dict with summary fields for operator handoff
    """
    summary = {
        "motivo_escalation": reason,
        "stato_conversazione": context.state.value if context.state else "unknown",
    }

    # Client info
    if context.client_name:
        nome = context.client_name
        if context.client_surname:
            nome += f" {context.client_surname}"
        summary["cliente"] = nome
    if context.client_id:
        summary["cliente_id"] = context.client_id
    if context.client_phone:
        summary["telefono"] = context.client_phone

    # Booking info collected so far
    if context.service_display or context.service:
        summary["servizio"] = context.service_display or context.service
    if context.date_display or context.date:
        summary["data"] = context.date_display or context.date
    if context.time_display or context.time:
        summary["ora"] = context.time_display or context.time
    if context.operator_name:
        summary["operatore_richiesto"] = context.operator_name

    # New client flag
    if context.is_new_client:
        summary["nuovo_cliente"] = True

    return summary


def format_escalation_response(summary: Dict[str, Any]) -> str:
    """
    Format escalation summary as a human-readable message for the operator.

    Args:
        summary: Dict from build_escalation_summary

    Returns:
        Italian string for operator handoff
    """
    parts = ["Riepilogo conversazione:"]

    if "cliente" in summary:
        parts.append(f"- Cliente: {summary['cliente']}")
    if "telefono" in summary:
        parts.append(f"- Telefono: {summary['telefono']}")
    if summary.get("nuovo_cliente"):
        parts.append("- Nuovo cliente (non ancora registrato)")
    if "servizio" in summary:
        parts.append(f"- Servizio richiesto: {summary['servizio']}")
    if "data" in summary:
        parts.append(f"- Data: {summary['data']}")
    if "ora" in summary:
        parts.append(f"- Ora: {summary['ora']}")
    if "operatore_richiesto" in summary:
        parts.append(f"- Operatore: {summary['operatore_richiesto']}")

    parts.append(f"- Motivo: {summary.get('motivo_escalation', 'richiesta utente')}")

    return "\n".join(parts)


def build_caller_message(summary: Dict[str, Any]) -> str:
    """
    Build the message Sara says to the caller during escalation.

    Acknowledges what was collected and provides reassurance.
    """
    collected = []
    if "servizio" in summary:
        collected.append(summary["servizio"])
    if "data" in summary:
        collected.append(summary["data"])
    if "ora" in summary:
        collected.append(summary["ora"])

    if collected:
        info = ", ".join(collected)
        return (
            f"La passo subito a un collega. "
            f"Ho già annotato: {info}. "
            f"Non dovrà ripetere nulla!"
        )
    return "La passo subito a un collega che potrà aiutarla al meglio."
