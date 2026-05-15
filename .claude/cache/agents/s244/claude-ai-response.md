# Claude.ai response S244 — Analisi smoking gun S243 + Opzioni operative

**Data**: 2026-05-15 inizio S244
**Input**: smoking gun S243 (`live-test-log-s243.txt`) + prompt diagnostico (`claude-ai-prompt.md`)

## Diagnosi raffinata

T1/T1.5/T2 hanno funzionato meccanicamente (`S243 T1: bridge wiring enqueued` confermato nel log) ma il bug fires PRIMA che `drain_pending_bridges` venga raggiunto al successivo tick di `_pjsua2_thread`.

**Sequenza ricostruita**:
1. `libHandleEvents(20)` dispatcha callback `onCallMediaState`
2. Callback ritorna senza chiamare `startTransmit` (T1 attivo)
3. Stessa chiamata `libHandleEvents` continua a processare eventi pendenti del batch
4. Uno di quegli eventi triggera cross-thread `grp_lock` release
5. `_pjsua2_thread` aborta con `grp_lock_unset_owner_thread`

**Conclusione**: il bug NON è causato da `startTransmit`. È causato da eventi pjmedia che pjsip emette automaticamente al passaggio `PJSUA_CALL_MEDIA_LOCAL_HOLD → PJSUA_CALL_MEDIA_ACTIVE`. T1 era razionale ma viene falsificato dal timing.

## Hypothesis ranking (Claude.ai)

**Dominante: N1 — pjmedia clock master spawnato durante media activation**. Quando media diventa ACTIVE, pjsua internamente:
- Crea conf bridge slot
- Setta clock master del bridge (primo "consumer")
- Emette `PJMEDIA_EVENT_*` drenati nello stesso batch `libHandleEvents`

Se uno di questi eventi interni triggera lock release cross-thread, T1/T1.5/T2 non possono toccarlo — succede tutto dentro pjsua C, non in codice Python.

Coerente con N1 dossier (`.claude/cache/agents/s238/pjsua2-clock-master-pattern.md`). **B1 (downgrade 2.15.1) è il test corretto di falsificazione "regression dev branch vs bug strutturale"**.

## Raccomandazione Claude.ai

**Opzione 2** — diagnostica pjsip log level 5 + stderr redirect PRIMA di B1.
- Tempo: 15-20 min
- Output: ultimo evento pjmedia C-side prima del crash
- Discrimina N1 (clock master) vs N2 (conf event) vs altro

Tre scenari post-diagnostica:
1. `pjmedia_clock` log → conferma N1 → B1 ha senso
2. `pjmedia_conf` event interno → bug strutturale conf bridge → B2 mossa
3. Inaspettato → nuova superficie analisi

## Decisione CTO S244 (no founder review)

**Opzione 2 ADOPTED**. Razionale:
- Investire 15-20 min in diagnostica precisa per evitare 4-8h B2 alla cieca se B1 fallisce
- B1 worst case 2h, B2 4-8h → ordine corretto: diagnostica → B1 → (se serve) B2
- Logs pjsua livello 5 già parzialmente visibili nel log S243 (buffered stderr post-crash mostra `pjsua state changed`, `registration success`) → forzare flush + redirect a file separato pre-crash è cheap win
- Anti-pattern S159 rispettato: NO switch architetturale fine sessione esausta

## Plan operativo S244

1. Backup `lib/pjsua2.backup-2.16dev-20260515` su iMac (~2 min)
2. Patch `voip_pjsua2.py`: `ep_cfg.logConfig.level=5 + consoleLevel=5 + filename=/tmp/sara-pjsip-s244.log + decor` (~5 min)
3. Sync iMac via git push + ssh imac git pull (~2 min)
4. Restart pipeline iMac VOIP_LOCAL_PORT=6080 (~30s)
5. Founder chiama 0972536918 da 3281536308 (~30s)
6. Leggo `/tmp/sara-pjsip-s244.log` → discrimino N1 vs altro
7. Decisione: B1 se N1 confermato, B2 se conf strutturale, diagnostica++ se inaspettato
