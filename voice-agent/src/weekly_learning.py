"""
FLUXION Weekly Self-Learning Loop (G6)

Auto-analyzes conversation data to identify:
1. State abandonment: which FSM states lead to non-completion
2. State loops: repeated states in same session (user stuck)
3. Bottleneck states: longest avg time per state
4. Escalation triggers: which states precede escalation
5. Low-confidence patterns: NLU failures by state/intent

Runs weekly (Sunday 6:00am) via APScheduler.
Generates actionable insights stored in voice_analytics.db.

Revenue: compounding improvement — each week Sara gets smarter.
World-class: no PMI competitor has self-learning voice agents.
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# DB PATH — same as analytics.py
# ═══════════════════════════════════════════════════════════════════

def _get_analytics_db_path() -> str:
    fluxion_dir = Path.home() / ".fluxion"
    return str(fluxion_dir / "voice_analytics.db")


# ═══════════════════════════════════════════════════════════════════
# INSIGHT QUERIES — each returns a list of findings
# ═══════════════════════════════════════════════════════════════════

def _query_state_abandonment(conn: sqlite3.Connection, days: int = 7) -> List[Dict[str, Any]]:
    """
    Find FSM states where conversations end in ABANDONED or ERROR.
    High abandonment in a state = UX friction point.
    """
    rows = conn.execute(
        """
        SELECT
            ct.fsm_state,
            c.outcome,
            COUNT(*) AS count
        FROM conversation_turns ct
        JOIN conversations c ON ct.conversation_id = c.id
        WHERE c.started_at >= datetime('now', ? || ' days')
          AND c.outcome IN ('abandoned', 'error', 'escalated')
          AND ct.fsm_state != ''
          AND ct.turn_number = (
              SELECT MAX(ct2.turn_number)
              FROM conversation_turns ct2
              WHERE ct2.conversation_id = ct.conversation_id
          )
        GROUP BY ct.fsm_state, c.outcome
        ORDER BY count DESC
        LIMIT 10
        """,
        (str(-days),),
    ).fetchall()
    return [
        {"state": r[0], "outcome": r[1], "count": r[2]}
        for r in rows
    ]


def _query_state_loops(conn: sqlite3.Connection, days: int = 7) -> List[Dict[str, Any]]:
    """
    Find conversations where the same state appears 3+ times (user is stuck).
    """
    rows = conn.execute(
        """
        SELECT
            ct.conversation_id,
            ct.fsm_state,
            COUNT(*) AS repeat_count
        FROM conversation_turns ct
        JOIN conversations c ON ct.conversation_id = c.id
        WHERE c.started_at >= datetime('now', ? || ' days')
          AND ct.fsm_state != ''
        GROUP BY ct.conversation_id, ct.fsm_state
        HAVING repeat_count >= 3
        ORDER BY repeat_count DESC
        LIMIT 10
        """,
        (str(-days),),
    ).fetchall()
    return [
        {"conversation_id": r[0], "state": r[1], "repeat_count": r[2]}
        for r in rows
    ]


def _query_bottleneck_states(conn: sqlite3.Connection, days: int = 7) -> List[Dict[str, Any]]:
    """
    Find states with highest average latency — slow NLU or complex processing.
    """
    rows = conn.execute(
        """
        SELECT
            ct.fsm_state,
            ROUND(AVG(ct.latency_ms), 0) AS avg_latency_ms,
            COUNT(*) AS turn_count
        FROM conversation_turns ct
        JOIN conversations c ON ct.conversation_id = c.id
        WHERE c.started_at >= datetime('now', ? || ' days')
          AND ct.fsm_state != ''
          AND ct.latency_ms > 0
        GROUP BY ct.fsm_state
        HAVING turn_count >= 3
        ORDER BY avg_latency_ms DESC
        LIMIT 10
        """,
        (str(-days),),
    ).fetchall()
    return [
        {"state": r[0], "avg_latency_ms": r[1], "turn_count": r[2]}
        for r in rows
    ]


def _query_escalation_patterns(conn: sqlite3.Connection, days: int = 7) -> List[Dict[str, Any]]:
    """
    Find most common escalation reasons and the states that trigger them.
    """
    rows = conn.execute(
        """
        SELECT
            c.escalation_reason,
            COUNT(*) AS count
        FROM conversations c
        WHERE c.started_at >= datetime('now', ? || ' days')
          AND c.outcome = 'escalated'
          AND c.escalation_reason IS NOT NULL
          AND c.escalation_reason != ''
        GROUP BY c.escalation_reason
        ORDER BY count DESC
        LIMIT 10
        """,
        (str(-days),),
    ).fetchall()
    return [
        {"reason": r[0], "count": r[1]}
        for r in rows
    ]


def _query_low_confidence_patterns(conn: sqlite3.Connection, days: int = 7) -> List[Dict[str, Any]]:
    """
    Find turns with low intent confidence (<0.5) grouped by state — NLU weak spots.
    """
    rows = conn.execute(
        """
        SELECT
            ct.fsm_state,
            ct.intent,
            ROUND(AVG(ct.intent_confidence), 2) AS avg_confidence,
            COUNT(*) AS count
        FROM conversation_turns ct
        JOIN conversations c ON ct.conversation_id = c.id
        WHERE c.started_at >= datetime('now', ? || ' days')
          AND ct.intent_confidence < 0.5
          AND ct.intent_confidence > 0
          AND ct.fsm_state != ''
        GROUP BY ct.fsm_state, ct.intent
        HAVING count >= 2
        ORDER BY count DESC
        LIMIT 10
        """,
        (str(-days),),
    ).fetchall()
    return [
        {"state": r[0], "intent": r[1], "avg_confidence": r[2], "count": r[3]}
        for r in rows
    ]


def _query_frustration_hotspots(conn: sqlite3.Connection, days: int = 7) -> List[Dict[str, Any]]:
    """
    Find states where frustration level is consistently high (>=2).
    """
    rows = conn.execute(
        """
        SELECT
            ct.fsm_state,
            ROUND(AVG(ct.frustration_level), 1) AS avg_frustration,
            COUNT(*) AS turn_count
        FROM conversation_turns ct
        JOIN conversations c ON ct.conversation_id = c.id
        WHERE c.started_at >= datetime('now', ? || ' days')
          AND ct.fsm_state != ''
          AND ct.frustration_level >= 2
        GROUP BY ct.fsm_state
        HAVING turn_count >= 2
        ORDER BY avg_frustration DESC
        LIMIT 10
        """,
        (str(-days),),
    ).fetchall()
    return [
        {"state": r[0], "avg_frustration": r[1], "turn_count": r[2]}
        for r in rows
    ]


def _query_weekly_summary(conn: sqlite3.Connection, days: int = 7) -> Dict[str, Any]:
    """
    High-level weekly metrics summary.
    """
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS total_conversations,
            SUM(CASE WHEN outcome = 'completed' THEN 1 ELSE 0 END) AS completed,
            SUM(CASE WHEN outcome = 'abandoned' THEN 1 ELSE 0 END) AS abandoned,
            SUM(CASE WHEN outcome = 'escalated' THEN 1 ELSE 0 END) AS escalated,
            SUM(CASE WHEN outcome = 'error' THEN 1 ELSE 0 END) AS errors,
            SUM(CASE WHEN booking_created = 1 THEN 1 ELSE 0 END) AS bookings_created,
            ROUND(AVG(total_turns), 1) AS avg_turns,
            ROUND(AVG(total_latency_ms), 0) AS avg_latency_ms,
            SUM(groq_usage_count) AS total_groq_calls
        FROM conversations
        WHERE started_at >= datetime('now', ? || ' days')
        """,
        (str(-days),),
    ).fetchone()

    if not row or row[0] == 0:
        return {"total_conversations": 0}

    total = row[0]
    return {
        "total_conversations": total,
        "completed": row[1] or 0,
        "abandoned": row[2] or 0,
        "escalated": row[3] or 0,
        "errors": row[4] or 0,
        "bookings_created": row[5] or 0,
        "completion_rate": round((row[1] or 0) / total * 100, 1) if total > 0 else 0,
        "avg_turns": row[6] or 0,
        "avg_latency_ms": row[7] or 0,
        "total_groq_calls": row[8] or 0,
    }


# ═══════════════════════════════════════════════════════════════════
# REPORT GENERATION
# ═══════════════════════════════════════════════════════════════════

def generate_weekly_report(days: int = 7) -> Dict[str, Any]:
    """
    Generate a complete weekly learning report.

    Returns structured dict with all insights — can be stored in DB,
    sent via WhatsApp to owner, or displayed in dashboard.
    """
    db_path = _get_analytics_db_path()
    if not Path(db_path).exists():
        logger.warning("[WeeklyLearning] Analytics DB not found at %s", db_path)
        return {"error": "Analytics DB not found", "generated_at": datetime.now().isoformat()}

    try:
        with sqlite3.connect(db_path, timeout=5) as conn:
            report = {
                "generated_at": datetime.now().isoformat(),
                "period_days": days,
                "summary": _query_weekly_summary(conn, days),
                "state_abandonment": _query_state_abandonment(conn, days),
                "state_loops": _query_state_loops(conn, days),
                "bottleneck_states": _query_bottleneck_states(conn, days),
                "escalation_patterns": _query_escalation_patterns(conn, days),
                "low_confidence": _query_low_confidence_patterns(conn, days),
                "frustration_hotspots": _query_frustration_hotspots(conn, days),
            }

            # Generate actionable insights from data
            report["insights"] = _derive_insights(report)

            # Persist report
            _store_report(conn, report)

            return report
    except sqlite3.Error as e:
        logger.error("[WeeklyLearning] DB error: %s", e)
        return {"error": str(e), "generated_at": datetime.now().isoformat()}


def _derive_insights(report: Dict[str, Any]) -> List[str]:
    """
    Derive human-readable actionable insights from raw data.
    These are the "so what?" — what should Sara's developer fix.
    """
    insights = []
    summary = report.get("summary", {})

    # Completion rate insight
    cr = summary.get("completion_rate", 0)
    total = summary.get("total_conversations", 0)
    if total >= 5 and cr < 70:
        insights.append(
            f"⚠️ Completion rate {cr}% — below 70% target. "
            f"{summary.get('abandoned', 0)} abandoned, {summary.get('escalated', 0)} escalated."
        )
    elif total >= 5 and cr >= 90:
        insights.append(f"✅ Excellent completion rate: {cr}%")

    # State abandonment insight
    for sa in report.get("state_abandonment", [])[:3]:
        if sa["count"] >= 3:
            insights.append(
                f"🔴 {sa['count']} conversations end at state '{sa['state']}' "
                f"with outcome '{sa['outcome']}' — investigate UX at this step."
            )

    # State loops insight (stuck users)
    loops = report.get("state_loops", [])
    if loops:
        worst = loops[0]
        insights.append(
            f"🔁 Users getting stuck: state '{worst['state']}' repeated "
            f"{worst['repeat_count']}x in a single conversation — simplify this step."
        )

    # Latency insight
    for bs in report.get("bottleneck_states", [])[:2]:
        if bs["avg_latency_ms"] > 3000:
            insights.append(
                f"🐌 State '{bs['state']}' has {bs['avg_latency_ms']}ms avg latency "
                f"({bs['turn_count']} turns) — optimize NLU/DB for this state."
            )

    # Frustration insight
    for fh in report.get("frustration_hotspots", [])[:2]:
        insights.append(
            f"😤 High frustration in state '{fh['state']}': avg {fh['avg_frustration']}/4 "
            f"({fh['turn_count']} turns) — review prompts and error recovery."
        )

    # Low confidence insight
    for lc in report.get("low_confidence", [])[:2]:
        if lc["count"] >= 3:
            insights.append(
                f"🎯 NLU weak: intent '{lc['intent']}' in state '{lc['state']}' "
                f"has {lc['avg_confidence']} confidence ({lc['count']} times) — add training data."
            )

    if not insights:
        insights.append("✅ No significant issues detected this week.")

    return insights


# ═══════════════════════════════════════════════════════════════════
# REPORT PERSISTENCE — stored in analytics DB
# ═══════════════════════════════════════════════════════════════════

_CREATE_REPORTS_TABLE = """
CREATE TABLE IF NOT EXISTS weekly_reports (
    id TEXT PRIMARY KEY,
    generated_at DATETIME NOT NULL,
    period_days INTEGER NOT NULL,
    report_json TEXT NOT NULL,
    insights_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


def _store_report(conn: sqlite3.Connection, report: Dict[str, Any]) -> None:
    """Persist weekly report to DB for historical tracking."""
    try:
        conn.execute(_CREATE_REPORTS_TABLE)
        report_id = f"weekly_{report['generated_at'][:10]}"
        conn.execute(
            """
            INSERT OR REPLACE INTO weekly_reports (id, generated_at, period_days, report_json, insights_count)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                report_id,
                report["generated_at"],
                report["period_days"],
                json.dumps(report, ensure_ascii=False, default=str),
                len(report.get("insights", [])),
            ),
        )
        conn.commit()
        logger.info("[WeeklyLearning] Report stored: %s (%d insights)", report_id, len(report.get("insights", [])))
    except sqlite3.Error as e:
        logger.error("[WeeklyLearning] Failed to store report: %s", e)


def get_latest_report() -> Optional[Dict[str, Any]]:
    """Retrieve the most recent weekly report."""
    db_path = _get_analytics_db_path()
    if not Path(db_path).exists():
        return None
    try:
        with sqlite3.connect(db_path, timeout=3) as conn:
            # Table may not exist yet
            try:
                row = conn.execute(
                    "SELECT report_json FROM weekly_reports ORDER BY generated_at DESC LIMIT 1"
                ).fetchone()
            except sqlite3.OperationalError:
                return None
            if row:
                return json.loads(row[0])
    except sqlite3.Error:
        pass
    return None


# ═══════════════════════════════════════════════════════════════════
# SCHEDULER ENTRY POINT
# ═══════════════════════════════════════════════════════════════════

async def run_weekly_learning() -> None:
    """
    G6 weekly job (Sunday 6:00am).
    Generates report and logs insights.
    """
    logger.info("[WeeklyLearning] Starting weekly analysis...")
    report = generate_weekly_report(days=7)

    if "error" in report:
        logger.warning("[WeeklyLearning] Report failed: %s", report["error"])
        return

    summary = report.get("summary", {})
    insights = report.get("insights", [])

    logger.info(
        "[WeeklyLearning] ✅ Report complete — %d conversations, %.1f%% completion, %d insights",
        summary.get("total_conversations", 0),
        summary.get("completion_rate", 0),
        len(insights),
    )
    for insight in insights:
        logger.info("[WeeklyLearning] %s", insight)


def format_report_for_wa(report: Dict[str, Any]) -> str:
    """Format report as WhatsApp-friendly message for business owner."""
    summary = report.get("summary", {})
    insights = report.get("insights", [])
    total = summary.get("total_conversations", 0)

    if total == 0:
        return "📊 Report settimanale Sara: nessuna conversazione questa settimana."

    lines = [
        f"📊 *Report Settimanale Sara*",
        f"Periodo: ultimi {report.get('period_days', 7)} giorni\n",
        f"📞 Conversazioni: {total}",
        f"✅ Completate: {summary.get('completed', 0)} ({summary.get('completion_rate', 0)}%)",
        f"📅 Prenotazioni: {summary.get('bookings_created', 0)}",
        f"⚡ Turni medi: {summary.get('avg_turns', 0)}",
    ]

    if insights:
        lines.append("\n💡 *Punti di attenzione:*")
        for insight in insights[:5]:
            lines.append(f"  • {insight}")

    return "\n".join(lines)
