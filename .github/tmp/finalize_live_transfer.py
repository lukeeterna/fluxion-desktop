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


# Orchestrator: Rust resolver owns business-open truth for live VoIP transfer.
p = Path("voice-agent/src/orchestrator.py")
s = p.read_text()
s = replace_once(
    s,
    '''        self._last_escalation_wa_sent = False
        self._last_live_transfer_routes = []
''',
    '''        self._last_escalation_wa_sent = False
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

old_trigger = '''        is_bh = self._is_business_hours()
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
'''
new_trigger = '''        is_voip = getattr(self, "_is_voip_call", False)
        live_routes = []
        # P0 LIVE TRANSFER: ask Rust before deciding whether a VoIP call is in-hours.
        # It knows weekday, holidays, pauses, operator hours and absences.
        if is_voip and not force_notify:
            live_routes = await self._resolve_live_transfer_routes()
            self._last_live_transfer_routes = live_routes
        is_bh = self._live_transfer_business_open() if is_voip else self._is_business_hours()
        if is_voip and is_bh and not force_notify and live_routes:
            logger.info("[ESC] %d live transfer route(s); WhatsApp deferred", len(live_routes))
            return escalation_phone

        urgency = "URGENTE" if is_bh else "NON URGENTE (fuori orario)"
'''
s = replace_once(s, old_trigger, new_trigger, "WA escalation schedule authority")

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


# Regression tests: bridge schedule truth wins over contradictory Python clock.
p = Path("voice-agent/tests/test_live_transfer_orchestrator.py")
s = p.read_text()
s = replace_once(
    s,
    '''    o._last_live_transfer_routes = []
    o._is_business_hours = MagicMock(return_value=True)
''',
    '''    o._last_live_transfer_routes = []
    o._last_bridge_business_open = None
    o._is_business_hours = MagicMock(return_value=True)
''',
    "orchestrator test state",
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
    o._fetch_escalation_route_payload = AsyncMock(return_value={
        "business_open": False,
        "routes": [{"phone": "3331234567", "source": "operator:op-1"}],
    })

    routes = await VoiceOrchestrator._resolve_live_transfer_routes(o)

    assert routes == []
    assert o._last_bridge_business_open is False
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
