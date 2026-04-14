"""
FLUXION Sales Agent WA — Flask dashboard single-page.
Legge leads.db e mostra funnel AARRR.
Accesso: http://127.0.0.1:5050
"""
from __future__ import annotations

import sqlite3
import logging
from datetime import date
from flask import Flask, jsonify, render_template_string, request

from config import DB_PATH, DASHBOARD_PORT, DASHBOARD_HOST

logger = logging.getLogger(__name__)
app = Flask(__name__)

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FLUXION Sales Agent</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #0f1117; color: #e2e8f0; min-height: 100vh; }
  .header { background: linear-gradient(135deg, #1a1f2e 0%, #0f1117 100%);
            padding: 24px 32px; border-bottom: 1px solid #2d3748; }
  .header h1 { font-size: 1.5rem; font-weight: 700; color: #fff; }
  .header p  { color: #718096; font-size: 0.875rem; margin-top: 4px; }
  .container { max-width: 1200px; margin: 0 auto; padding: 32px; }
  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 16px; margin-bottom: 32px; }
  .stat-card { background: #1a1f2e; border: 1px solid #2d3748; border-radius: 12px;
               padding: 20px; }
  .stat-card .label { font-size: 0.75rem; color: #718096; text-transform: uppercase;
                      letter-spacing: 0.05em; }
  .stat-card .value { font-size: 2rem; font-weight: 700; margin-top: 8px; }
  .stat-card .sub   { font-size: 0.75rem; color: #718096; margin-top: 4px; }
  .green  { color: #48bb78; }
  .blue   { color: #4299e1; }
  .yellow { color: #ecc94b; }
  .red    { color: #fc8181; }
  .purple { color: #9f7aea; }
  .section { background: #1a1f2e; border: 1px solid #2d3748; border-radius: 12px;
             padding: 24px; margin-bottom: 24px; }
  .section h2 { font-size: 1rem; font-weight: 600; margin-bottom: 16px; color: #a0aec0; }
  table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
  th { text-align: left; padding: 10px 12px; color: #718096; font-weight: 500;
       border-bottom: 1px solid #2d3748; font-size: 0.75rem; text-transform: uppercase; }
  td { padding: 10px 12px; border-bottom: 1px solid #1e2535; }
  tr:last-child td { border-bottom: none; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 9999px;
           font-size: 0.7rem; font-weight: 600; }
  .badge-sent      { background: #2b4c7e; color: #90cdf4; }
  .badge-delivered { background: #276749; color: #9ae6b4; }
  .badge-read      { background: #744210; color: #fbd38d; }
  .badge-replied   { background: #553c9a; color: #d6bcfa; }
  .badge-failed    { background: #742a2a; color: #feb2b2; }
  .badge-pending   { background: #2d3748; color: #a0aec0; }
  .refresh-btn { background: #4299e1; color: #fff; border: none; border-radius: 8px;
                 padding: 8px 16px; cursor: pointer; font-size: 0.875rem; float: right; }
</style>
</head>
<body>
<div class="header">
  <h1>FLUXION Sales Agent</h1>
  <p id="last-update">Caricamento...</p>
</div>
<div class="container">
  <div class="stats-grid" id="kpi-cards"></div>

  <div class="section">
    <h2>FUNNEL</h2>
    <div id="funnel-chart"></div>
  </div>

  <div class="section">
    <h2>ULTIMI MESSAGGI <button class="refresh-btn" onclick="loadData()">Aggiorna</button></h2>
    <table>
      <thead>
        <tr><th>Attivita</th><th>Telefono</th><th>Categoria</th><th>Stato</th><th>Inviato</th></tr>
      </thead>
      <tbody id="messages-body"></tbody>
    </table>
  </div>

  <div class="section">
    <h2>PER CATEGORIA</h2>
    <table>
      <thead>
        <tr><th>Categoria</th><th>Lead</th><th>Contattati</th><th>Risposte</th><th>Conv. %</th></tr>
      </thead>
      <tbody id="category-body"></tbody>
    </table>
  </div>
</div>

<script>
async function loadData() {
  const [stats, messages, categories] = await Promise.all([
    fetch('/api/stats').then(r => r.json()),
    fetch('/api/messages?limit=20').then(r => r.json()),
    fetch('/api/categories').then(r => r.json()),
  ]);

  document.getElementById('last-update').textContent =
    'Aggiornato: ' + new Date().toLocaleTimeString('it-IT');

  var kpis = [
    { label: 'Lead Totali',    value: stats.total_leads,     sub: 'nel database',         color: 'blue' },
    { label: 'Contattati',     value: stats.total_sent,      sub: 'messaggi inviati',     color: 'green' },
    { label: 'Letti',          value: stats.total_read,      sub: (stats.read_rate||0).toFixed(1) + '% read rate', color: 'yellow' },
    { label: 'Risposte',       value: stats.total_replied,   sub: (stats.reply_rate||0).toFixed(1) + '% reply rate', color: 'purple' },
    { label: 'Oggi',           value: stats.sent_today,      sub: 'di ' + stats.daily_limit + ' limite', color: 'blue' },
    { label: 'Bloccati',       value: stats.total_blocked,   sub: 'segnalazioni spam',    color: 'red' },
  ];
  document.getElementById('kpi-cards').innerHTML = kpis.map(function(k) {
    return '<div class="stat-card"><div class="label">' + k.label + '</div>' +
      '<div class="value ' + k.color + '">' + (k.value || 0) + '</div>' +
      '<div class="sub">' + k.sub + '</div></div>';
  }).join('');

  var maxVal = Math.max(stats.total_leads||1, 1);
  var steps = [
    { label: 'Scraped', value: stats.total_leads, color: '#4299e1' },
    { label: 'Contattati', value: stats.total_sent, color: '#48bb78' },
    { label: 'Consegnati', value: stats.total_delivered, color: '#ecc94b' },
    { label: 'Letti', value: stats.total_read, color: '#ed8936' },
    { label: 'Risposte', value: stats.total_replied, color: '#9f7aea' },
  ];
  document.getElementById('funnel-chart').innerHTML =
    '<div style="display:flex;gap:16px;align-items:flex-end;height:140px;padding:0 8px;">' +
    steps.map(function(s) {
      var h = Math.max(8, Math.round((s.value||0) / maxVal * 120));
      return '<div style="flex:1;text-align:center;">' +
        '<div style="height:' + h + 'px;background:' + s.color + ';border-radius:4px 4px 0 0;' +
        'display:flex;align-items:flex-end;justify-content:center;padding-bottom:4px;' +
        'font-size:11px;color:#fff;font-weight:700;">' + (s.value||0) + '</div>' +
        '<div style="font-size:10px;color:#718096;margin-top:4px;">' + s.label + '</div></div>';
    }).join('') + '</div>';

  document.getElementById('messages-body').innerHTML = messages.map(function(m) {
    return '<tr><td>' + (m.business_name||'-') + '</td>' +
      '<td><code>' + (m.phone||'-') + '</code></td>' +
      '<td>' + (m.category||'-') + '</td>' +
      '<td><span class="badge badge-' + m.status + '">' + m.status + '</span></td>' +
      '<td>' + (m.sent_at ? new Date(m.sent_at).toLocaleString('it-IT') : '-') + '</td></tr>';
  }).join('') || '<tr><td colspan="5" style="color:#718096;text-align:center;padding:24px;">Nessun messaggio ancora</td></tr>';

  document.getElementById('category-body').innerHTML = categories.map(function(c) {
    var cls = c.conv_pct >= 2 ? 'green' : c.conv_pct >= 1 ? 'yellow' : 'red';
    return '<tr><td style="text-transform:capitalize;">' + c.category + '</td>' +
      '<td>' + c.total_leads + '</td><td>' + c.contacted + '</td>' +
      '<td>' + c.replied + '</td><td class="' + cls + '">' + (c.conv_pct||0).toFixed(2) + '%</td></tr>';
  }).join('') || '<tr><td colspan="5" style="color:#718096;text-align:center;padding:24px;">Nessun dato</td></tr>';
}

loadData();
setInterval(loadData, 30000);
</script>
</body>
</html>
"""


def _db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template_string(DASHBOARD_HTML)


@app.route("/api/stats")
def api_stats():
    conn = _db()
    today = date.today().isoformat()

    total_leads     = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    total_sent      = conn.execute("SELECT COUNT(*) FROM messages WHERE status != 'pending'").fetchone()[0]
    total_delivered = conn.execute("SELECT COUNT(*) FROM messages WHERE status IN ('delivered','read','replied')").fetchone()[0]
    total_read      = conn.execute("SELECT COUNT(*) FROM messages WHERE status IN ('read','replied')").fetchone()[0]
    total_replied   = conn.execute("SELECT COUNT(*) FROM messages WHERE status = 'replied'").fetchone()[0]
    total_blocked   = conn.execute("SELECT COUNT(*) FROM messages WHERE status = 'blocked'").fetchone()[0]
    sent_today      = conn.execute(
        "SELECT COALESCE(sent,0) FROM daily_stats WHERE date = ?", (today,)
    ).fetchone()
    sent_today = sent_today[0] if sent_today else 0

    state_row = conn.execute(
        "SELECT value FROM agent_state WHERE key = 'daily_limit'"
    ).fetchone()
    daily_limit = int(state_row[0]) if state_row else 20

    conn.close()

    read_rate  = (total_read  / total_sent * 100) if total_sent > 0 else 0
    reply_rate = (total_replied / total_sent * 100) if total_sent > 0 else 0

    return jsonify({
        "total_leads":     total_leads,
        "total_sent":      total_sent,
        "total_delivered": total_delivered,
        "total_read":      total_read,
        "total_replied":   total_replied,
        "total_blocked":   total_blocked,
        "sent_today":      sent_today,
        "daily_limit":     daily_limit,
        "read_rate":       read_rate,
        "reply_rate":      reply_rate,
    })


@app.route("/api/messages")
def api_messages():
    limit = int(request.args.get("limit", 50))
    conn = _db()
    rows = conn.execute("""
        SELECT m.id, l.business_name, l.phone, l.category,
               m.status, m.sent_at, m.template_key
        FROM messages m
        JOIN leads l ON l.id = m.lead_id
        ORDER BY m.created_at DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/categories")
def api_categories():
    conn = _db()
    rows = conn.execute("""
        SELECT
            l.category,
            COUNT(DISTINCT l.id) as total_leads,
            COUNT(DISTINCT CASE WHEN m.status IN ('sent','delivered','read','replied') THEN l.id END) as contacted,
            COUNT(DISTINCT CASE WHEN m.status = 'replied' THEN l.id END) as replied
        FROM leads l
        LEFT JOIN messages m ON m.lead_id = l.id
        GROUP BY l.category
        ORDER BY total_leads DESC
    """).fetchall()
    conn.close()
    result = []
    for r in rows:
        r = dict(r)
        r["conv_pct"] = (r["replied"] / r["contacted"] * 100) if r["contacted"] > 0 else 0
        result.append(r)
    return jsonify(result)


@app.route("/api/daily")
def api_daily():
    """Ultimi 14 giorni di stats."""
    conn = _db()
    rows = conn.execute("""
        SELECT date, sent, delivered, read_count, replied, failed, blocked
        FROM daily_stats
        ORDER BY date DESC
        LIMIT 14
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


def run_dashboard():
    logger.info("Dashboard: http://%s:%d", DASHBOARD_HOST, DASHBOARD_PORT)
    app.run(host=DASHBOARD_HOST, port=DASHBOARD_PORT, debug=False)
