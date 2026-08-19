from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 occurrence, got {count}")
    return text.replace(old, new, 1)


def add_dependency(path: str, anchor: str, dep: str) -> None:
    p = Path(path)
    s = p.read_text()
    if dep in s:
        return
    if s.count(anchor) != 1:
        raise SystemExit(f"{path}: dependency anchor mismatch")
    p.write_text(s.replace(anchor, anchor + dep + "\n", 1))


# Python 3.13+: audioop left the stdlib. Keep older interpreters untouched.
dep = 'audioop-lts>=0.2.2; python_version >= "3.13"'
add_dependency(
    "voice-agent/requirements.txt",
    "# ── Audio ────────────────────────────────────────────────────────────\n",
    dep,
)
add_dependency("voice-agent/requirements-ci.txt", "# Core\n", dep)
add_dependency("voice-agent/requirements-windows.txt", "# Audio processing\n", dep)


# Rust operator integration fixtures: dedicated transfer policy fields + roundtrip.
p = Path("src-tauri/tests/integration_operatori.rs")
s = p.read_text()
needle = "        genere: None,\n    };"
count = s.count(needle)
if count != 2:
    raise SystemExit(f"integration_operatori fixtures: expected 2 literals, got {count}")
s = s.replace(
    needle,
    "        genere: None,\n"
    "        voice_transfer_enabled: None,\n"
    "        voice_transfer_reachable: None,\n"
    "        voice_transfer_priority: None,\n"
    "    };",
)
marker = (
    "// ═══════════════════════════════════════════════════════════════════\n"
    "// PII encryption at-rest — verify ciphertext per i 4 campi PII"
)
test = r'''// ═══════════════════════════════════════════════════════════════════
// P0 Sara live-transfer policy — dedicated fields roundtrip through encrypted
// operator CRUD without changing encrypted personal-phone semantics.
// ═══════════════════════════════════════════════════════════════════

#[tokio::test]
async fn test_voice_transfer_policy_roundtrip() {
    setup_test_encryption();
    let (pool, db_file) = create_test_database().await;

    let mut input = make_input("Luca", "Transfer", Some("luca@example.com"), Some("3332221111"));
    input.voice_transfer_enabled = Some(1);
    input.voice_transfer_reachable = Some(1);
    input.voice_transfer_priority = Some(7);

    let created = internal_create_operatore(&pool, input)
        .await
        .expect("create operator with transfer policy");
    assert_eq!(created.voice_transfer_enabled, 1);
    assert_eq!(created.voice_transfer_reachable, 1);
    assert_eq!(created.voice_transfer_priority, 7);

    let updated = internal_update_operatore(
        &pool,
        &created.id,
        UpdateOperatoreInput {
            nome: None,
            cognome: None,
            email: None,
            telefono: None,
            ruolo: None,
            colore: None,
            avatar_url: None,
            attivo: None,
            genere: None,
            voice_transfer_enabled: Some(1),
            voice_transfer_reachable: Some(0),
            voice_transfer_priority: Some(22),
        },
    )
    .await
    .expect("update transfer policy");

    assert_eq!(updated.voice_transfer_enabled, 1);
    assert_eq!(updated.voice_transfer_reachable, 0);
    assert_eq!(updated.voice_transfer_priority, 22);

    cleanup_test_database(pool, db_file).await;
}

'''
if s.count(marker) != 1:
    raise SystemExit("integration_operatori insertion marker missing")
s = s.replace(marker, test + marker, 1)
p.write_text(s)


# Rust bridge: owner setting is internal notification only; never a public route.
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
    '''    // `telefono_titolare` is a private notification contact, never a caller-facing
    // transfer destination. A live owner leg must come from an explicit `operatori`
    // admin record with voice_transfer_enabled + voice_transfer_reachable.
    let owner_notification = normalize_transfer_phone(&owner_phone);
    let general_fallback = normalize_transfer_phone(&general_transfer_phone);
    let fallback_phone = general_fallback.clone();
    let fallback_source = fallback_phone
        .as_ref()
        .map(|_| "voice_agent_config.numero_trasferimento".to_string());
    let notification_phone = owner_notification
        .clone()
        .or_else(|| general_fallback.clone());
    let notification_source = if owner_notification.is_some() {
        Some("impostazioni.telefono_titolare".to_string())
    } else if general_fallback.is_some() {
        Some("voice_agent_config.numero_trasferimento".to_string())
    } else {
        None
    };
''',
    "bridge private owner/public fallback split",
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
    '''        // The general transfer number is an explicit public business route.
        // `telefono_titolare` is intentionally excluded here: owner live transfer
        // is allowed only through an opted-in/reachable admin operator row above.
        if let Some(phone) = general_fallback {
''',
    "bridge owner route removal",
)
s = replace_once(
    s,
    '''        "fallback_phone": fallback_phone,
        "fallback_source": fallback_source,
              })),
''',
    '''        "fallback_phone": fallback_phone,
        "fallback_source": fallback_source,
        "notification_phone": notification_phone,
        "notification_source": notification_source,
              })),
''',
    "bridge notification fields",
)
p.write_text(s)


# Orchestrator: Rust resolver owns business-open truth and private/public contacts split.
p = Path("voice-agent/src/orchestrator.py")
s = p.read_text()
s = replace_once(
    s,
    '''        self._last_escalation_phone = ""
        self._last_escalation_phone_source = ""
        self._last_escalation_wa_sent = False
        self._last_live_transfer_routes = []
''',
    '''        self._last_escalation_phone = ""
        self._last_escalation_phone_source = ""
        self._last_escalation_notification_phone = ""
        self._last_escalation_notification_source = ""
        self._last_escalation_wa_sent = False
        self._last_live_transfer_routes = []
        self._last_bridge_business_open = None
''',
    "session escalation state",
)
old_resolver = '''    async def _resolve_live_transfer_routes(self) -> list:
        """Return ordered (phone, source) routes already trusted/filtered by Rust."""
        payload = await self._fetch_escalation_route_payload()
        if not payload.get("business_open", False):
            return []
        routes = []
        seen = set()
        for item in payload.get("routes") or []:
            if not isinstance(item, dict):
                continue
            phone = str(item.get("phone") or "").strip()
            source = str(item.get("source") or "bridge").strip()
            if phone and phone not in seen:
                seen.add(phone)
                routes.append((phone, source))
        return routes

'''
new_resolver = '''    async def _resolve_live_transfer_routes(self) -> list:
        """Return ordered trusted routes; Rust owns current business-open truth."""
        payload = await self._fetch_escalation_route_payload()
        bridge_open = payload.get("business_open")
        self._last_bridge_business_open = bridge_open if isinstance(bridge_open, bool) else None
        if self._last_bridge_business_open is not True:
            return []
        routes = []
        seen = set()
        for item in payload.get("routes") or []:
            if not isinstance(item, dict):
                continue
            phone = str(item.get("phone") or "").strip()
            source = str(item.get("source") or "bridge").strip()
            if phone and phone not in seen:
                seen.add(phone)
                routes.append((phone, source))
        return routes

    def _live_transfer_business_open(self) -> bool:
        """Use Rust schedule truth for VoIP; local clock is availability fallback only."""
        if getattr(self, "_is_voip_call", False):
            bridge_open = getattr(self, "_last_bridge_business_open", None)
            if isinstance(bridge_open, bool):
                return bridge_open
        return self._is_business_hours()

'''
s = replace_once(s, old_resolver, new_resolver, "live route resolver authority")
old_contact = '''    async def _resolve_escalation_phone(self) -> tuple:
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
new_contact = '''    async def _resolve_escalation_contacts(self) -> tuple:
        """Resolve private notification and public fallback contacts without operator PII reads."""
        payload = await self._fetch_escalation_route_payload()
        public_phone = str(payload.get("fallback_phone") or "").strip()
        public_source = str(payload.get("fallback_source") or "").strip()
        notify_phone = str(payload.get("notification_phone") or "").strip()
        notify_source = str(payload.get("notification_source") or "").strip()
        if notify_phone or public_phone:
            if not notify_phone:
                notify_phone, notify_source = public_phone, public_source
            return (
                notify_phone or None,
                notify_source or ("bridge.notification" if notify_phone else None),
                public_phone or None,
                public_source or ("bridge.fallback" if public_phone else None),
            )

        # Bridge may be unavailable while the sidecar is starting. Direct SQLite
        # fallback preserves the same privacy split: owner is notification-only;
        # the only caller-facing number is voice_agent_config.numero_trasferimento.
        db_path = self._find_db_path()
        if not db_path:
            return None, None, None, None
        notify_phone = None
        notify_source = None
        public_phone = None
        public_source = None
        try:
            import sqlite3 as _sq
            with _sq.connect(db_path, timeout=3) as conn:
                try:
                    row = conn.execute(
                        "SELECT valore FROM impostazioni WHERE chiave = ? LIMIT 1",
                        ("telefono_titolare",),
                    ).fetchone()
                    if row and row[0] and row[0].strip():
                        notify_phone = row[0].strip()
                        notify_source = "impostazioni.telefono_titolare"
                except Exception:
                    pass
                try:
                    row = conn.execute(
                        "SELECT numero_trasferimento FROM voice_agent_config LIMIT 1"
                    ).fetchone()
                    if row and row[0] and row[0].strip():
                        public_phone = row[0].strip()
                        public_source = "voice_agent_config.numero_trasferimento"
                except Exception:
                    pass
        except Exception as exc:
            logger.warning("[ESC] DB error resolving escalation contacts: %s", exc)
        if not notify_phone and public_phone:
            notify_phone, notify_source = public_phone, public_source
        return notify_phone, notify_source, public_phone, public_source

'''
s = replace_once(s, old_contact, new_contact, "private/public escalation contacts")
old_build = '''    def _build_escalation_response(self, esc_phone: str, is_bh: bool, prefix: str = "") -> str:
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
new_build = '''    def _build_escalation_response(self, esc_phone: str, is_bh: bool, prefix: str = "") -> str:
        """Build escalation response; esc_phone is always caller-safe/public."""
        if (is_bh and getattr(self, "_is_voip_call", False)
                and getattr(self, "_last_live_transfer_routes", None)):
            return prefix + "Capisco. Rimanga in linea, provo a passarla subito a un operatore."
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
s = replace_once(s, old_build, new_build, "caller-safe escalation response")
old_trigger = '''        escalation_phone, phone_source = await self._resolve_escalation_phone()
        self._last_escalation_phone = escalation_phone or ""
        self._last_escalation_phone_source = phone_source or ""
        self._last_escalation_wa_sent = False
        if not escalation_phone:
            logger.warning("[WA-ESC] No escalation phone found in any source")
            return ""

        logger.info(f"[WA-ESC] Resolved escalation phone from {phone_source}")

        # Build context message
        client_name = self.booking_sm.context.client_name or "Sconosciuto"
        ctx = self.booking_sm.context
        context_parts = []
        if ctx.service_display or ctx.service:
            context_parts.append(f"Servizio: {ctx.service_display or ctx.service}")
        if ctx.date_display or ctx.date:
            context_parts.append(f"Data: {ctx.date_display or ctx.date}")
        if ctx.time_display or ctx.time:
            context_parts.append(f"Ora: {ctx.time_display or ctx.time}")
        if ctx.client_phone:
            context_parts.append(f"Tel cliente: {ctx.client_phone}")
        context_str = " | ".join(context_parts) if context_parts else "nessuna prenotazione in corso"

        is_bh = self._is_business_hours()
        # P0 LIVE TRANSFER: defer WhatsApp only when at least one trusted,
        # currently reachable live route actually exists. If routing is empty
        # (holiday, absence, opt-out, closed schedule), notify immediately.
        if getattr(self, "_is_voip_call", False) and is_bh and not force_notify:
            live_routes = await self._resolve_live_transfer_routes()
            self._last_live_transfer_routes = live_routes
            if live_routes:
                logger.info("[ESC] %d live transfer route(s); WhatsApp deferred", len(live_routes))
                return escalation_phone

        urgency = "URGENTE" if is_bh else "NON URGENTE (fuori orario)"

        msg = (
            f"[{urgency}] Richiesta escalation ({escalation_type}) da: {client_name}.\n"
            f"Stato: {ctx.state.value} | {context_str}.\n"
            f"Richiamarlo al più presto."
        )

        # Try WhatsApp notification
        wa_sent = False
        if self._wa_client:
            try:
                normalized = self._wa_client.normalize_phone(escalation_phone)
                result = await self._wa_client.send_message_async(normalized, msg)
                if result.get("success"):
                    logger.info(f"[WA-ESC] Notification sent to {phone_source}")
                    wa_sent = True
                    self._last_escalation_wa_sent = True
                else:
                    logger.warning(f"[WA-ESC] WA failed: {result.get('error')}")
            except Exception as e:
                logger.warning("[WA-ESC] WA error: %s", e)

        if not wa_sent:
            logger.info("[WA-ESC] WA not available, phone will be read to client")

        return escalation_phone
'''
new_trigger = '''        notify_phone, notify_source, escalation_phone, phone_source = await self._resolve_escalation_contacts()
        self._last_escalation_phone = escalation_phone or ""
        self._last_escalation_phone_source = phone_source or ""
        self._last_escalation_notification_phone = notify_phone or ""
        self._last_escalation_notification_source = notify_source or ""
        self._last_escalation_wa_sent = False
        if not notify_phone and not escalation_phone:
            logger.warning("[WA-ESC] No escalation contact found in any source")

        if escalation_phone:
            logger.info("[ESC] Public fallback resolved from %s", phone_source)
        if notify_phone:
            logger.info("[WA-ESC] Private notification contact resolved from %s", notify_source)

        # Build context message
        client_name = self.booking_sm.context.client_name or "Sconosciuto"
        ctx = self.booking_sm.context
        context_parts = []
        if ctx.service_display or ctx.service:
            context_parts.append(f"Servizio: {ctx.service_display or ctx.service}")
        if ctx.date_display or ctx.date:
            context_parts.append(f"Data: {ctx.date_display or ctx.date}")
        if ctx.time_display or ctx.time:
            context_parts.append(f"Ora: {ctx.time_display or ctx.time}")
        if ctx.client_phone:
            context_parts.append(f"Tel cliente: {ctx.client_phone}")
        context_str = " | ".join(context_parts) if context_parts else "nessuna prenotazione in corso"

        is_voip = getattr(self, "_is_voip_call", False)
        live_routes = []
        # Rust owns holiday/pause/absence/current schedule truth for VoIP.
        if is_voip and not force_notify:
            live_routes = await self._resolve_live_transfer_routes()
            self._last_live_transfer_routes = live_routes
        is_bh = self._live_transfer_business_open() if is_voip else self._is_business_hours()
        if is_voip and is_bh and not force_notify and live_routes:
            logger.info("[ESC] %d live transfer route(s); WhatsApp deferred", len(live_routes))
            return escalation_phone or ""

        urgency = "URGENTE" if is_bh else "NON URGENTE (fuori orario)"

        msg = (
            f"[{urgency}] Richiesta escalation ({escalation_type}) da: {client_name}.\n"
            f"Stato: {ctx.state.value} | {context_str}.\n"
            f"Richiamarlo al più presto."
        )

        # Try WhatsApp notification only to the private/internal notification target.
        wa_sent = False
        if self._wa_client and notify_phone:
            try:
                normalized = self._wa_client.normalize_phone(notify_phone)
                result = await self._wa_client.send_message_async(normalized, msg)
                if result.get("success"):
                    logger.info("[WA-ESC] Notification sent to %s", notify_source)
                    wa_sent = True
                    self._last_escalation_wa_sent = True
                else:
                    logger.warning(f"[WA-ESC] WA failed: {result.get('error')}")
            except Exception as e:
                logger.warning("[WA-ESC] WA error: %s", e)

        if not wa_sent:
            logger.info("[WA-ESC] WA not available; no private number will be read to caller")

        # Return only the public caller-safe fallback. Never return telefono_titolare.
        return escalation_phone or ""
'''
s = replace_once(s, old_trigger, new_trigger, "WA escalation contact/privacy + schedule authority")
old_audio = '''        if result.should_escalate and result.intent != "content_filter_severe":
            is_bh = self._is_business_hours()
            live_routes = list(getattr(self, "_last_live_transfer_routes", []) or [])
            if is_bh and not live_routes:
                live_routes = await self._resolve_live_transfer_routes()
                self._last_live_transfer_routes = live_routes
            transfer_routes = [phone for phone, _source in live_routes if phone]
'''
new_audio = '''        if result.should_escalate and result.intent != "content_filter_severe":
            is_voip = getattr(self, "_is_voip_call", False)
            live_routes = list(getattr(self, "_last_live_transfer_routes", []) or [])
            if is_voip:
                # Re-resolve at transfer time so stale per-turn state cannot override
                # holidays, pauses, reachability or a just-started operator absence.
                live_routes = await self._resolve_live_transfer_routes()
                self._last_live_transfer_routes = live_routes
                is_bh = self._live_transfer_business_open()
            else:
                is_bh = self._is_business_hours()
            transfer_routes = [phone for phone, _source in live_routes if phone]
'''
s = replace_once(s, old_audio, new_audio, "process_audio schedule authority")
one_line = "response = self._build_escalation_response(esc_phone, self._is_business_hours())"
if s.count(one_line) != 2:
    raise SystemExit(f"escalation response one-line callsites: expected 2, got {s.count(one_line)}")
s = s.replace(
    one_line,
    "response = self._build_escalation_response(esc_phone, self._live_transfer_business_open())",
)
s = replace_once(
    s,
    '''                response = self._build_escalation_response(
                    esc_phone, self._is_business_hours(), prefix="Mi scusi per il disagio. "
                )
''',
    '''                response = self._build_escalation_response(
                    esc_phone, self._live_transfer_business_open(), prefix="Mi scusi per il disagio. "
                )
''',
    "frustration escalation response callsite",
)
p.write_text(s)


# Regression tests: schedule authority + private owner notification/public fallback split.
p = Path("voice-agent/tests/test_live_transfer_orchestrator.py")
s = p.read_text()
s = replace_once(
    s,
    '''    o._is_voip_call = True
    o._resolve_escalation_phone = AsyncMock(return_value=("3331234567", "voice_agent_config"))
    o._resolve_live_transfer_routes = AsyncMock(return_value=[("3331234567", "operator:op-1")])
    o._last_live_transfer_routes = []
    o._is_business_hours = MagicMock(return_value=True)
''',
    '''    o._is_voip_call = True
    o._resolve_escalation_contacts = AsyncMock(return_value=(
        "3399999999", "impostazioni.telefono_titolare",
        "3331234567", "voice_agent_config.numero_trasferimento",
    ))
    o._resolve_live_transfer_routes = AsyncMock(return_value=[("3331234567", "operator:op-1")])
    o._last_live_transfer_routes = []
    o._last_bridge_business_open = True
    o._is_business_hours = MagicMock(return_value=True)
''',
    "orchestrator test state",
)
s = replace_once(
    s,
    '''    o._wa_client.send_message_async.assert_awaited_once()
    assert o._last_escalation_wa_sent is True
''',
    '''    o._wa_client.send_message_async.assert_awaited_once()
    o._wa_client.normalize_phone.assert_called_once_with("3399999999")
    assert o._last_escalation_wa_sent is True
''',
    "force notify private target assertion",
)
insertion = '''

@pytest.mark.asyncio
async def test_bridge_closed_overrides_python_open_for_voip_escalation():
    o = _orchestrator()

    async def closed_routes():
        o._last_bridge_business_open = False
        return []

    o._resolve_live_transfer_routes = AsyncMock(side_effect=closed_routes)
    o._is_business_hours = MagicMock(return_value=True)
    phone = await o._trigger_wa_escalation_call("explicit_request")

    assert phone == "3331234567"
    o._wa_client.send_message_async.assert_awaited_once()
    sent_message = o._wa_client.send_message_async.await_args.args[1]
    assert "NON URGENTE (fuori orario)" in sent_message


@pytest.mark.asyncio
async def test_bridge_open_overrides_python_closed_and_keeps_live_transfer_first():
    o = _orchestrator()

    async def open_routes():
        o._last_bridge_business_open = True
        return [("3331234567", "operator:op-1")]

    o._resolve_live_transfer_routes = AsyncMock(side_effect=open_routes)
    o._is_business_hours = MagicMock(return_value=False)
    phone = await o._trigger_wa_escalation_call("explicit_request")

    assert phone == "3331234567"
    o._wa_client.send_message_async.assert_not_called()
    assert o._live_transfer_business_open() is True


@pytest.mark.asyncio
async def test_resolver_records_bridge_closed_and_rejects_routes_when_closed():
    o = _orchestrator()
    o._last_bridge_business_open = None
    o._fetch_escalation_route_payload = AsyncMock(return_value={
        "business_open": False,
        "routes": [{"phone": "3331234567", "source": "operator:op-1"}],
    })

    routes = await VoiceOrchestrator._resolve_live_transfer_routes(o)

    assert routes == []
    assert o._last_bridge_business_open is False


@pytest.mark.asyncio
async def test_owner_contact_is_private_notification_only():
    o = _orchestrator()
    o._fetch_escalation_route_payload = AsyncMock(return_value={
        "notification_phone": "3399999999",
        "notification_source": "impostazioni.telefono_titolare",
        "fallback_phone": "3331234567",
        "fallback_source": "voice_agent_config.numero_trasferimento",
    })

    notify, notify_src, public, public_src = await VoiceOrchestrator._resolve_escalation_contacts(o)

    assert notify == "3399999999"
    assert notify_src == "impostazioni.telefono_titolare"
    assert public == "3331234567"
    assert public_src == "voice_agent_config.numero_trasferimento"


@pytest.mark.asyncio
async def test_owner_only_contact_is_never_returned_to_caller():
    o = _orchestrator()
    o._fetch_escalation_route_payload = AsyncMock(return_value={
        "notification_phone": "3399999999",
        "notification_source": "impostazioni.telefono_titolare",
        "fallback_phone": None,
        "fallback_source": None,
    })

    notify, _notify_src, public, _public_src = await VoiceOrchestrator._resolve_escalation_contacts(o)

    assert notify == "3399999999"
    assert public is None


def test_voip_live_route_does_not_require_public_fallback_to_offer_transfer():
    o = _orchestrator()
    o._last_live_transfer_routes = [("3331234567", "operator:op-1")]
    text = o._build_escalation_response("", True)
    assert "passarla" in text.lower()
    assert "3399999999" not in text
'''
marker = '''

@pytest.mark.asyncio
async def test_force_notify_sends_whatsapp_after_live_transfer_failure():
'''
if s.count(marker) != 1:
    raise SystemExit("orchestrator regression insertion marker missing")
s = s.replace(marker, insertion + marker, 1)
p.write_text(s)

print("LIVE_TRANSFER_PRODUCT_PATCH=READY")
