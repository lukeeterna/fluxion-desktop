from pathlib import Path

p = Path('.github/tmp/finalize_live_transfer_mac.py')
src = p.read_text(encoding='utf-8')
start_marker = "old_trigger = '''"
end_marker = "old_audio = '''"
start = src.find(start_marker)
end = src.find(end_marker, start + 1)
if start < 0 or end < 0:
    raise SystemExit(f'patcher trigger block markers missing: start={start} end={end}')

replacement = r"""trigger_start = s.index("    async def _trigger_wa_escalation_call")
trigger_end = s.index("\n    async def _create_client", trigger_start)
new_trigger = r'''    async def _trigger_wa_escalation_call(self, escalation_type: str, force_notify: bool = False) -> str:
        # Notify privately and return only a caller-safe public fallback number.
        notify_phone, notify_source, escalation_phone, phone_source = await self._resolve_escalation_contacts()
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
s = s[:trigger_start] + new_trigger + s[trigger_end:]
"""

src = src[:start] + replacement + src[end:]
p.write_text(src, encoding='utf-8')
compile(src, str(p), 'exec')
print('FINALIZER_PATCHER_REPAIRED=1')
