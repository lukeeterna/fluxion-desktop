from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 occurrence, got {count}")
    return text.replace(old, new, 1)


# -----------------------------------------------------------------------------
# Rust route contract
# - staff + owner are live routes only when represented by explicit opt-in
#   operator records; role=admin sorts after normal staff and still obeys hours,
#   absences and reachability.
# - telefono_titolare remains INTERNAL notification contact only.
# - numero_trasferimento is the only public/general number Sara may read aloud.
# -----------------------------------------------------------------------------
p = Path("src-tauri/src/http_bridge.rs")
s = p.read_text()

s = replace_once(
    s,
    '''    let owner_fallback = normalize_transfer_phone(&owner_phone);
    let general_fallback = normalize_transfer_phone(&general_transfer_phone);
    let (fallback_phone, fallback_source) = if let Some(phone) = owner_fallback.clone() {
        (
            Some(phone),
            Some("impostazioni.telefono_titolare".to_string()),
        )
    } else if let Some(phone) = general_fallback.clone() {
        (
            Some(phone),
            Some("voice_agent_config.numero_trasferimento".to_string()),
        )
    } else {
        (None, None)
    };
''',
    '''    let owner_notification = normalize_transfer_phone(&owner_phone);
    let general_fallback = normalize_transfer_phone(&general_transfer_phone);

    // Privacy boundary: telefono_titolare is an internal notification contact,
    // never a public fallback and never an availability-bypassing live route.
    // A transferable owner must be configured as an admin operator with explicit
    // Sara opt-in/reachability; the normal operator query then applies schedule,
    // holiday and absence policy before putting that number into `routes`.
    let (notification_phone, notification_source) = if let Some(phone) = owner_notification {
        (
            Some(phone),
            Some("impostazioni.telefono_titolare".to_string()),
        )
    } else if let Some(phone) = general_fallback.clone() {
        (
            Some(phone),
            Some("voice_agent_config.numero_trasferimento".to_string()),
        )
    } else {
        (None, None)
    };
    let fallback_phone = general_fallback.clone();
    let fallback_source = general_fallback
        .as_ref()
        .map(|_| "voice_agent_config.numero_trasferimento".to_string());
''',
    "Rust notification/public fallback split",
)

s = replace_once(
    s,
    '''        // Owner fallback precedes the general transfer number. Both are explicit
        // business settings, never caller-supplied destinations.
        if let Some(phone) = owner_fallback {
            if !seen.contains(&phone) {
                seen.push(phone.clone());
                routes.push(json!({
                    "phone": phone,
                    "source": "impostazioni.telefono_titolare",
                    "role": "owner",
                    "priority": 10000,
                }));
            }
        }
        if let Some(phone) = general_fallback {
''',
    '''        // Public/general fallback is deliberately last. The owner is NOT
        // appended from telefono_titolare here: owner live transfer must flow
        // through an opted-in admin operator so availability policy is enforced.
        if let Some(phone) = general_fallback {
''',
    "Rust owner availability bypass removal",
)

s = replace_once(
    s,
    '''        "routes": routes,
        "fallback_phone": fallback_phone,
        "fallback_source": fallback_source,
''',
    '''        "routes": routes,
        "notification_phone": notification_phone,
        "notification_source": notification_source,
        "fallback_phone": fallback_phone,
        "fallback_source": fallback_source,
''',
    "Rust response contact split",
)
p.write_text(s)


# -----------------------------------------------------------------------------
# Python contract: internal notification number can never be spoken to caller.
# -----------------------------------------------------------------------------
p = Path("voice-agent/src/orchestrator.py")
s = p.read_text()

s = replace_once(
    s,
    '''        self._last_escalation_phone_source = ""
        self._last_escalation_wa_sent = False
        self._last_live_transfer_routes = []
        self._last_bridge_business_open = None
''',
    '''        self._last_escalation_phone_source = ""
        self._last_public_escalation_phone = ""
        self._last_public_escalation_phone_source = ""
        self._last_escalation_wa_sent = False
        self._last_live_transfer_routes = []
        self._last_bridge_business_open = None
''',
    "session public fallback reset",
)

old_resolve = '''    async def _resolve_escalation_phone(self) -> tuple:
        """Resolve a safe notification/fallback phone without reading encrypted operator PII."""
        payload = await self._fetch_escalation_route_payload()
        phone = str(payload.get("fallback_phone") or "").strip()
        source = str(payload.get("fallback_source") or "").strip()
        if phone:
            return phone, source or "bridge.fallback"
        routes = payload.get("routes") or []
        if routes and isinstance(routes[0], dict):
            phone = str(routes[0].get("phone") or "").strip()
            if phone:
                return phone, str(routes[0].get("source") or "bridge.route")

        # Bridge may be unavailable while the sidecar is starting. Fallback only
        # to non-encrypted business settings; never query operatori.telefono here.
        db_path = self._find_db_path()
        if not db_path:
            return None, None
        try:
            import sqlite3 as _sq
            with _sq.connect(db_path, timeout=3) as conn:
                try:
                    rows = conn.execute(
                        "SELECT chiave, valore FROM impostazioni WHERE chiave = ?",
                        ("telefono_titolare",),
                    ).fetchall()
                    for row in rows:
                        if row[1] and row[1].strip():
                            return row[1].strip(), "impostazioni.telefono_titolare"
                except Exception:
                    pass
                try:
                    row = conn.execute(
                        "SELECT numero_trasferimento FROM voice_agent_config LIMIT 1"
                    ).fetchone()
                    if row and row[0] and row[0].strip():
                        return row[0].strip(), "voice_agent_config"
                except Exception:
                    pass
        except Exception as exc:
            logger.warning("[ESC] DB error resolving fallback phone: %s", exc)
        return None, None

'''
new_resolve = '''    async def _resolve_escalation_phone(self) -> tuple:
        """Resolve internal notification contact and separately retain public fallback."""
        payload = await self._fetch_escalation_route_payload()
        public_phone = str(payload.get("fallback_phone") or "").strip()
        public_source = str(payload.get("fallback_source") or "").strip()
        self._last_public_escalation_phone = public_phone
        self._last_public_escalation_phone_source = public_source

        phone = str(payload.get("notification_phone") or public_phone or "").strip()
        source = str(payload.get("notification_source") or public_source or "").strip()
        if phone:
            return phone, source or "bridge.notification"

        # Bridge may be unavailable while the sidecar is starting. Direct DB
        # fallback preserves the same privacy split: owner is notification-only,
        # while numero_trasferimento is the only number eligible to be read aloud.
        db_path = self._find_db_path()
        if not db_path:
            return None, None
        try:
            import sqlite3 as _sq
            with _sq.connect(db_path, timeout=3) as conn:
                general = ""
                try:
                    row = conn.execute(
                        "SELECT numero_trasferimento FROM voice_agent_config LIMIT 1"
                    ).fetchone()
                    if row and row[0] and row[0].strip():
                        general = row[0].strip()
                        self._last_public_escalation_phone = general
                        self._last_public_escalation_phone_source = "voice_agent_config.numero_trasferimento"
                except Exception:
                    pass
                try:
                    rows = conn.execute(
                        "SELECT chiave, valore FROM impostazioni WHERE chiave = ?",
                        ("telefono_titolare",),
                    ).fetchall()
                    for row in rows:
                        if row[1] and row[1].strip():
                            return row[1].strip(), "impostazioni.telefono_titolare"
                except Exception:
                    pass
                if general:
                    return general, "voice_agent_config.numero_trasferimento"
        except Exception as exc:
            logger.warning("[ESC] DB error resolving escalation contacts: %s", exc)
        return None, None

    def _public_escalation_phone(self) -> str:
        """Number safe to disclose to a caller; personal/internal contacts never qualify."""
        return str(getattr(self, "_last_public_escalation_phone", "") or "").strip()

'''
s = replace_once(s, old_resolve, new_resolve, "Python notification/public split")

old_response = '''    def _build_escalation_response(self, esc_phone: str, is_bh: bool, prefix: str = "") -> str:
        """Build escalation response based on business hours and phone availability."""
        if not esc_phone:
            return prefix + "Mi dispiace, al momento non riesco a metterla in contatto con un operatore. Può riprovare più tardi."
        if is_bh and getattr(self, "_is_voip_call", False):
            return prefix + "Capisco. Rimanga in linea, provo a passarla subito a un operatore."
        if is_bh:
            return (
                f"{prefix}Capisco, la metto in contatto con un operatore. "
                f"Ho inviato una notifica, la ricontatteranno a breve. "
                f"In alternativa può chiamare direttamente il {esc_phone}."
            )
        return (
            f"{prefix}Al momento siamo fuori dall'orario di apertura. "
            f"Ho lasciato un messaggio, la ricontatteranno domani mattina. "
            f"In alternativa può chiamare il {esc_phone} in orario di apertura."
        )
'''
new_response = '''    def _build_escalation_response(self, esc_phone: str, is_bh: bool, prefix: str = "") -> str:
        """Build escalation response without ever disclosing internal/personal contacts."""
        public_phone = self._public_escalation_phone()
        if not esc_phone and not public_phone:
            return prefix + "Mi dispiace, al momento non riesco a metterla in contatto con un operatore. Può riprovare più tardi."
        if is_bh and getattr(self, "_is_voip_call", False):
            return prefix + "Capisco. Rimanga in linea, provo a passarla subito a un operatore."
        if is_bh:
            if public_phone:
                return (
                    f"{prefix}Capisco, ho inviato una notifica allo staff e la ricontatteranno a breve. "
                    f"In alternativa può chiamare direttamente il {public_phone}."
                )
            return prefix + "Capisco, ho inviato una notifica allo staff e la ricontatteranno a breve."
        if public_phone:
            return (
                f"{prefix}Al momento siamo fuori dall'orario di apertura. "
                f"Ho lasciato un messaggio allo staff. In alternativa può chiamare il {public_phone} in orario di apertura."
            )
        return prefix + "Al momento siamo fuori dall'orario di apertura. Ho lasciato un messaggio allo staff e la ricontatteranno appena possibile."
'''
s = replace_once(s, old_response, new_response, "caller disclosure guard")

s = replace_once(
    s,
    '''            esc_phone = getattr(self, "_last_escalation_phone", "") or ""

            if transfer_routes:
''',
    '''            esc_phone = getattr(self, "_last_escalation_phone", "") or ""
            public_phone = self._public_escalation_phone()

            if transfer_routes:
''',
    "VoIP public phone capture",
)

s = replace_once(
    s,
    '''                    elif esc_phone:
                        response_text = (
                            "Non riesco a completare il passaggio in linea in questo momento. "
                            f"Può chiamare direttamente il {esc_phone}."
                        )
''',
    '''                    elif public_phone:
                        response_text = (
                            "Non riesco a completare il passaggio in linea in questo momento. "
                            f"Può chiamare direttamente il {public_phone}."
                        )
''',
    "VoIP in-hours disclosure guard",
)

s = replace_once(
    s,
    '''                elif esc_phone:
                    if getattr(self, "_last_escalation_wa_sent", False):
                        response_text = (
                            "Al momento siamo fuori dall'orario di apertura. "
                            "Ho inviato una notifica allo staff e la ricontatteranno appena possibile."
                        )
                    else:
                        response_text = (
                            "Al momento siamo fuori dall'orario di apertura. "
                            f"Può chiamare direttamente il {esc_phone} in orario di apertura."
                        )
''',
    '''                elif public_phone:
                    if getattr(self, "_last_escalation_wa_sent", False):
                        response_text = (
                            "Al momento siamo fuori dall'orario di apertura. "
                            "Ho inviato una notifica allo staff e la ricontatteranno appena possibile."
                        )
                    else:
                        response_text = (
                            "Al momento siamo fuori dall'orario di apertura. "
                            f"Può chiamare direttamente il {public_phone} in orario di apertura."
                        )
                elif getattr(self, "_last_escalation_wa_sent", False):
                    response_text = (
                        "Al momento siamo fuori dall'orario di apertura. "
                        "Ho inviato una notifica allo staff e la ricontatteranno appena possibile."
                    )
                else:
                    response_text = (
                        "Al momento siamo fuori dall'orario di apertura. "
                        "La prego di riprovare durante l'orario di apertura."
                    )
''',
    "VoIP after-hours disclosure guard",
)
p.write_text(s)


# -----------------------------------------------------------------------------
# Regression tests for privacy split.
# -----------------------------------------------------------------------------
p = Path("voice-agent/tests/test_live_transfer_orchestrator.py")
s = p.read_text()
marker = '''

@pytest.mark.asyncio
async def test_force_notify_sends_whatsapp_after_live_transfer_failure():
'''
tests = '''

@pytest.mark.asyncio
async def test_owner_notification_phone_is_never_public_fallback():
    o = _orchestrator()
    o._last_public_escalation_phone = ""
    o._last_public_escalation_phone_source = ""
    o._fetch_escalation_route_payload = AsyncMock(return_value={
        "business_open": False,
        "notification_phone": "3331112222",
        "notification_source": "impostazioni.telefono_titolare",
        "fallback_phone": "0612345678",
        "fallback_source": "voice_agent_config.numero_trasferimento",
        "routes": [],
    })

    notification, source = await VoiceOrchestrator._resolve_escalation_phone(o)

    assert notification == "3331112222"
    assert source == "impostazioni.telefono_titolare"
    assert o._public_escalation_phone() == "0612345678"
    response = o._build_escalation_response(notification, False)
    assert "3331112222" not in response
    assert "0612345678" in response


def test_private_notification_without_public_number_is_not_spoken():
    o = _orchestrator()
    o._last_public_escalation_phone = ""
    response = o._build_escalation_response("3331112222", False)
    assert "3331112222" not in response
    assert "fuori dall'orario" in response
'''
if s.count(marker) != 1:
    raise SystemExit("privacy test insertion marker missing")
s = s.replace(marker, tests + marker, 1)
p.write_text(s)

print("LIVE_TRANSFER_PRIVACY_HARDENING=READY")
