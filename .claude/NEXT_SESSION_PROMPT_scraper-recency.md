# NEXT SESSION — VERIFICA EMPIRICA RECENCY FB (page_post_info.py)
> Salvato 2026-06-26. Workstream: Sales Agent FLUXION — sourcing anchor "attività viva".
> Prerequisito già fatto (sessione 2026-06-26): facebook-pages-scraper/PageInfo verificato 5/5,
> Picuki SCARTATO (morto, Cloudflare, 0/5). Report: /tmp/scraper-test/REPORT_scraper_test.md

## MANDATO: VERIFICA EMPIRICA — testa page_post_info.py per la RECENCY da Facebook. NON costruire l'integrazione.

FASE 0: git status pulito. Lavoro in scratch `/tmp/scraper-test` (riusa quello esistente). Idempotente. NIENTE subagent (main).
Done = valori reali estratti, non "il README dice". Picuki = SCARTATO (morto, 0/5 — non ritestare).

CONTESTO (test precedente): facebook-pages-scraper/PageInfo funziona 5/5 ma NON dà la recency (data ultimo post).
Lo stesso repo ha un modulo separato `page_post_info.py`. Questo task verifica SE recupera la data dell'ultimo post
dalla pagina FB — così l'anchor "attività viva" arriva dalla STESSA fonte robusta, senza reintrodurre IG/mirror fragili.

ESEGUI su 3-5 delle stesse attività già validate:
  KelvinKooMyhairmilano, spazioikosmilano, 20hourspalestre, MazdaCarozza, ladentalclinic
  - lancia `page_post_info.py` (stesso pin **curl_cffi==0.7.4** di Big Sur) su ogni pagina.
  - per ciascuna: estrae i post? con QUALE data/timestamp? il post più recente quanto è vecchio?
  Done tabella: | attività | post estratti sì/no | data ultimo post | tasso successo /5 | 429-403-captcha? |

CONTROLLI:
  - tasso di successo reale (quante delle 5) + serve curl_cffi o request base?
  - se page_post_info FALLISCE (errore/vuoto/blocco) → dichiaralo come FATTO, NON ripiegare su Picuki/IG.

PARERE TECNICO CC: page_post_info è affidabile come PageInfo, o è il modulo fragile che fa morire la recency?
Verdetto secco: la recency FB è ottenibile da questa fonte SÌ/NO. Se NO, l'anchor "vivo" si approssima dal sito
(crawl: ultime modifiche/blog/news) o si lascia cadere — quale dei due consigli.

DONE (esterna): tabella con date reali + tasso + verdetto recency-FB SÌ/NO. Oppure FATTO che blocca.
NON TOCCARE: ARGOS/FLUXION, nessun commit, nessuna build. Solo test scratch. APRI OUTPUT IN TEXTEDIT. IDEMPOTENTE.

## NOTE OPERATIVE PRONTE (dalla sessione precedente, per non ripartire da zero)
- Scratch già pronto: `/tmp/scraper-test/` con venv (`source venv/bin/activate`), repo `fb/` clonato.
- Modulo target: `/tmp/scraper-test/fb/facebook_page_scraper/page_post_info.py` (già presente).
- Pin obbligatorio Big Sur: `pip install curl_cffi==0.7.4` (l'ultima 0.13.x NON carica: `_SCDynamicStoreCopyProxies`).
- ATTENZIONE: il request_handler fa `sys.exit(1)` su errore → wrappare ogni chiamata in try/except SystemExit per non killare il batch.
- Se `/tmp` è stato pulito: riclona `git clone --depth 1 https://github.com/SSujitX/facebook-pages-scraper.git fb`.
