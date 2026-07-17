# TRANSCRIPT — chiamata reale 2026-07-17 (~21:50:16 → 21:54:30, engine go)

> Dialogo ricostruito da `sara_go.log`. Caller = trascrizioni STT esatte (dove loggate).
> Sara = testo TTS **troncato a ~40 char dal logger** (limite del log, non recuperabile qui → «…»).
> Righe di log tra parentesi.

**Sara (greeting, 21:50:16-17)**: «Salone Demo FLUXION, buonasera! Sono Sar…» *(disclosure «assistente virtuale» NON presente nel testo loggato → ND)* (138-145)

**Caller (21:50:18)**: «Dbeat» → NLU intent=ALTRO conf=0.50 (149-150)
**Sara (21:50:19)**: «Non trovo Dbeat tra i nostri clienti. Mi…» (158) *[bare-name captato come nome, S142]*

**Caller (21:50:34)**: «Ciao Sara, vorrei prenotare un taglio e colore per la barba, è possibile?» → PRENOTAZIONE conf=0.80 (208)
**Sara (21:50:35)**: «Capisco. Chiaro. Grazie Dbeat Ciao Sara,…» (211)

**Sara (21:51:31)**: «Ha ragione. Mi ripete il numero di telef…» (398)
**Sara (21:51:41)**: «Mi dispiace. Mi ripete il numero di tele…» (431)
**Caller (21:51:42)**: «E' IL MIO NOME» → CORREZIONE (439-441); GroqNLU correzione_nome (444); [E6] 3-strike (445)
**Sara (21:51:45)**: «Comprendo. La passo subito a un collega.» (451) → HANGUP soppresso FSM-guard (455)
**Sara (21:51:46)**: «Mi scusi. Mi ripete il numero di telefon…» (466)

**Caller (21:52:30)**: «Le comunico il numero che non risponde più.» → ALTRO (618-619)
**Sara (21:52:31)**: «Capisco. Mi ripete il numero di telefono…» (624)
**Caller (21:52:37)**: «Si è bloccata lì, mi ha richiesto il numero, gliel'ho ripornito.» → ALTRO; [E6] 3-strike (646-647)
**Sara (21:52:38)**: «Ha ragione. Certo. La passo subito a un…» (650) → HANGUP soppresso (655)
**Caller (21:52:42)**: «Ma è ferma di non risponde più. Sara ci sei?» → ESCALATION (669-671)
**Sara (21:52:55)**: «Comprendo. Mi ripete il numero di telefo…» (712)

**Caller (21:53:03)**: [ESCALATION] (741); [E6] 3-strike (869)
**Sara (21:53:05)**: «Mi scusi. La passo subito a un collega. » (874) → HANGUP soppresso (880)
**Sara (21:53:13)**: «Ha ragione. Perfetto, mi dica il numero …» (915)
**Caller (21:53:35)**: [CORTESIA]; [E6] 3-strike (1005-1007)
**Sara (21:53:36)**: «Mi dispiace. La passo subito a un colleg…» (1011) → HANGUP soppresso (1016)

**Caller (21:54:00)**: [PRENOTAZIONE] (1088); (21:54:06) [ESCALATION] (1115)
→ [WA-ESC] WA non disponibile, telefono letto al cliente (1111-1113)
**Sara (21:54:08)**: «Al momento siamo fuori dall'orario di ap…» (1119) *[fuori orario]*
**Caller (21:54:18)**: STT garbage «ttwchBJflQxLGNZBKx4HJwbAo2hW4QJz0EU5CXQ CNiFf.tFmBBA 4GlOnLYpYgkjvLAQJbVs&4LM3GQ» conf=0.00 → regex fallback (1157)
**Sara (21:54:20)**: «Mi scusi. Certo. Ho capito 444385516126,…» (1161) → BARGE-IN caller (riga BARGE-IN)
**Caller (21:54:23)**: «Occhiunando a dire comprendo, intercalare lievemente fuori posto.» → ALTRO (1175)
**Sara (21:54:24)**: «Capisco. Per confermare, il numero è 444…» (1181) → BARGE-IN caller
**Caller (21:54:29)**: «Grazie, arrivederci.» → CORTESIA conf=0.90 → S142 standalone goodbye exit=True (1197-1199)
**Sara (21:54:29)**: «Ha ragione. Prego. Arrivederci, buona gi…» (1202) → fine chiamata ~21:54:30

## Sintesi narrativa
Caller apre, «Dbeat» (probabile mis-STT del saluto) registrato come NOME. Chiede «taglio e colore per la barba». La macchina entra in `REGISTERING_PHONE` e **non ne esce mai**: STT del numero fallisce ripetutamente (vuoto/garbage), 3-strike E6 scatta più volte con «la passo a un collega» ma HANGUP soppresso dalla FSM-guard → Sara resta in linea in loop di reprompt («Mi ripete il numero…») con prefissi di scuse ripetuti («Comprendo/Capisco/Mi scusi/Ha ragione»). Numero infine «capito» come `444385516126` (12 cifre, non valido). Caller chiude con «Grazie, arrivederci».
