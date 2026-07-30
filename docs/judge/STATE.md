# STATE — Fonte di verità sessioni giudice

  HEAD ATTESO: 0eed51a
  CATENA: chiusura gap audio Sara → B3-PROMOTE → PRE-PUSH AUDIT → T-GIT-REALIGN → stress-test verticali → BRAINSYNC → WINPORT → WIZARD+KBPACK → primo cliente pagante. Scadenza produzione 27/08.
  PRIMA UNITÀ NON CHIUSA: T-F3-AUDIO-r2. Gli scenari audio SCN-08 (E6 su path audio) e SCN-09 (silenzio→reprompt) non hanno mai prodotto prove. Design obbligato: un driver script unico, scritto una volta ed eseguito una volta, che stampa ≤25 righe. Garbage SCN-08 = rumore int16 ampiezza ~±3000-6000 per ~1.5s, MAI silenzio (0 RMS viene scartato dal VAD, soglia 400). Stimolo SCN-09 = assenza di inject per >22s.
  DECISIONI CHIUSE — non si riaprono: M1 disclosure VERDE statico · M2 barge-in VERDE · M5 congedo VERDE provato live · M3 confirm-gated da FIX-C · congedo onesto senza «collega», con «richiamar» · TTS del rig = EdgeTTS IsabellaNeural (il «Piper ~50ms» era confabulazione) · taratura: reprompt 22.0s, vad_speech_threshold 400 rms, vad_silence ~1000ms, E6_threshold 3 · realign iMac FATTO (ff-merge a 4ce8b5e3, :3002 pid 31760 invariato) · untrack di fluxion.db* rinviato a T-GIT-REALIGN · repo pubblico per decisione founder, bonifica history obbligatoria in T-GIT-REALIGN · pricing €497 / €897 upgrade, mai canone.
  PENDENTI FOUNDER: GO su :3002 (solo a B3-PROMOTE) · sigillo estetico (nessuno aperto) · origine drift VectCutAPI (bassa priorità).
  DISCORDANZE APERTE: nessuna.
