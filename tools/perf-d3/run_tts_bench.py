#!/usr/bin/env python3
"""
S191 D-3 — Voice TTS Latency Benchmark

Misura la latenza end-to-end (richiesta HTTP → JSON con audio completo) del
TTS engine *production* attualmente attivo nel voice-pipeline FLUXION
(porta 3002). Usa l'endpoint POST /api/voice/say (text-only, niente NLU)
per isolare il costo TTS puro.

Uso (default contro voice-pipeline iMac via 127.0.0.1 quando eseguito su iMac):
    ./run_tts_bench.py
    ./run_tts_bench.py --host http://192.168.1.2:3002 --iter 50 --warmup 5

Output:
    docs/perf/D3-voice-latency.md (report markdown con P50/P95/P99 + verdict)
    /tmp/fluxion-d3-results.json (raw timings)

SLO (architecture-distribution.md):
    - Edge-TTS (production cloud)         : target P95 ~500ms
    - Piper offline (FAST/OFFLINE)        : target P95 <800ms
    - SystemTTS (LAST RESORT)             : target P95 ~400ms

Lo script NON impone Piper: misura il tier che il pipeline serve in modalità
'auto'. Il report include /api/tts/mode + /api/tts/hardware per disambiguare.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# 50 utterance corpus realistic per saloni/PMI (mix lunghezze 5-20 parole)
# Coprono: greeting, conferma, slot, name disambiguation, errori, chiusura, WA.
CORPUS: list[str] = [
    # Greetings (5)
    "Buongiorno, sono Sara, come posso aiutarti oggi?",
    "Salve, qui Sara dell'assistenza, dimmi pure.",
    "Ciao, sono Sara, in cosa posso esserti utile?",
    "Buon pomeriggio, sono Sara, dimmi pure.",
    "Buonasera, ti rispondo io, sono Sara.",
    # Conferme appuntamento (8)
    "Perfetto, ho prenotato il taglio per giovedì alle quindici.",
    "Confermo l'appuntamento per martedì alle dieci e trenta.",
    "Ti ho fissato il colore per venerdì alle sedici.",
    "Ok, prenotato manicure mercoledì alle undici.",
    "Confermato, sabato alle nove per il taglio uomo.",
    "Va bene, lunedì alle quattordici e trenta.",
    "Ti aspettiamo giovedì alle diciassette.",
    "Perfetto, segnato per domenica mattina alle dieci.",
    # Proposta slot (8)
    "Ho disponibilità mercoledì alle nove o alle quattordici, quale preferisci?",
    "Posso offrirti giovedì alle dieci o venerdì alle sedici.",
    "Ho liberi martedì pomeriggio alle quindici e trenta.",
    "Per quel servizio il primo slot è lunedì prossimo alle undici.",
    "Posso fissarti sabato mattina alle dieci o alle dodici.",
    "Ho disponibilità solo giovedì alle nove, ti va bene?",
    "Mi dispiace, oggi siamo pieni, ti propongo domani alle quindici.",
    "Quella fascia è occupata, ho libero alle sedici e trenta.",
    # Disambiguazione nome (6)
    "Scusa, hai detto Gino o Gigio?",
    "Confermami il cognome, è Rossi con due esse?",
    "Mi ripeti il numero di telefono?",
    "Per sicurezza, il tuo nome è Marco Bianchi, corretto?",
    "Mi pare di averti già in rubrica, sei Luca Verdi?",
    "Non ho capito bene, mi ripeti il nome?",
    # Errori e recovery (8)
    "Scusa, me lo ridici? Non ho capito bene.",
    "Mi sono persa un attimo, mi ripeti l'ultima cosa?",
    "Mi scusi, sono momentaneamente sovraccarica, riproviamo.",
    "Non ho capito che servizio vuoi prenotare, puoi ripetere?",
    "Quel giorno è chiuso, ti propongo un'alternativa.",
    "C'è stato un problema, riproviamo da capo per favore.",
    "Mi dispiace, non riesco a leggere la prenotazione adesso.",
    "Aspetta un attimo che verifico il calendario.",
    # Chiusura (5)
    "Perfetto, ti ho mandato la conferma su WhatsApp, a presto!",
    "Tutto sistemato, riceverai il promemoria un giorno prima.",
    "Grazie a te, buona giornata e a presto.",
    "Ci vediamo presto, buona giornata!",
    "Perfetto, ti aspettiamo, ciao!",
    # WhatsApp / lista attesa (5)
    "Ti metto in lista d'attesa, ti scrivo appena si libera uno slot.",
    "Ti mando subito la conferma su WhatsApp.",
    "Riceverai un promemoria automatico ventiquattr'ore prima.",
    "Se non ti va più, basta che mi rispondi su WhatsApp.",
    "Ti notifico io appena c'è una disdetta.",
    # Frasi corte (5)
    "Ok, perfetto.",
    "Va bene, segnato.",
    "Confermo, grazie.",
    "Subito, un attimo.",
    "Tutto chiaro, ciao!",
]

assert len(CORPUS) == 50, f"CORPUS deve avere 50 frasi, ne ha {len(CORPUS)}"


def http_post_json(url: str, body: dict, timeout: float = 30.0) -> tuple[float, dict]:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    return elapsed_ms, payload


def http_get_json(url: str, timeout: float = 5.0) -> dict:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return {}


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * (p / 100.0)
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="http://127.0.0.1:3002", help="Voice-pipeline base URL")
    ap.add_argument("--warmup", type=int, default=3)
    ap.add_argument("--iter", type=int, default=50, help="Iterazioni (default 50 = full corpus)")
    ap.add_argument(
        "--out-md",
        default="docs/perf/D3-voice-latency.md",
        help="Path report markdown (relative al repo root)",
    )
    ap.add_argument(
        "--out-json",
        default="/tmp/fluxion-d3-results.json",
    )
    args = ap.parse_args()

    say_url = f"{args.host}/api/voice/say"
    mode_url = f"{args.host}/api/tts/mode"
    hw_url = f"{args.host}/api/tts/hardware"
    health_url = f"{args.host}/health"

    health = http_get_json(health_url)
    if not health:
        print(f"FAIL: voice-pipeline non raggiungibile su {args.host}", file=sys.stderr)
        sys.exit(2)
    mode = http_get_json(mode_url)
    hw = http_get_json(hw_url)
    print(f"[health] {health.get('service')} v{health.get('version')} TTS={health.get('features',{}).get('tts')}")
    print(f"[mode]   {mode}")
    print(f"[hw]     {hw}")

    # Warmup (non conta in stats)
    print(f"\n[warmup] {args.warmup} iter…")
    for i in range(args.warmup):
        text = CORPUS[i % len(CORPUS)]
        try:
            ms, _ = http_post_json(say_url, {"text": text})
            print(f"  warm {i+1}: {ms:.0f} ms")
        except Exception as e:
            print(f"  warm {i+1} FAIL: {e}")

    # Bench
    n = min(args.iter, len(CORPUS))
    print(f"\n[bench] {n} iter su corpus reale…")
    samples: list[dict] = []
    fails = 0
    for i in range(n):
        text = CORPUS[i]
        try:
            ms, payload = http_post_json(say_url, {"text": text})
            audio_len = len(payload.get("audio_base64", "")) if payload.get("success") else 0
            success = bool(payload.get("success"))
            if not success or audio_len == 0:
                fails += 1
            samples.append(
                {
                    "i": i,
                    "text_chars": len(text),
                    "elapsed_ms": ms,
                    "audio_hex_len": audio_len,
                    "success": success,
                }
            )
            print(f"  {i+1:>2}/{n}  {ms:>7.1f} ms  audio_hex={audio_len}  text='{text[:50]}'")
        except Exception as e:
            fails += 1
            samples.append({"i": i, "text_chars": len(text), "elapsed_ms": -1, "success": False, "error": str(e)})
            print(f"  {i+1:>2}/{n}  FAIL  {e}")

    timings = [s["elapsed_ms"] for s in samples if s.get("success") and s["elapsed_ms"] > 0]
    if not timings:
        print("FAIL: nessun campione valido", file=sys.stderr)
        sys.exit(3)

    p50 = percentile(timings, 50)
    p95 = percentile(timings, 95)
    p99 = percentile(timings, 99)
    mean = statistics.mean(timings)
    stdev = statistics.pstdev(timings) if len(timings) > 1 else 0.0
    pmin = min(timings)
    pmax = max(timings)

    # Determine TTS engine in use (best-effort from /health + /api/tts/mode)
    tts_kind = health.get("features", {}).get("tts", "unknown")
    mode_now = mode.get("current_mode", "unknown")
    model_dl = mode.get("model_downloaded", None)

    # SLO target: prendiamo 800ms come hard cap (Piper offline). Edge-TTS soft 500ms.
    HARD_SLO_MS = 800.0
    SOFT_SLO_MS = 500.0
    verdict = "PASS" if p95 < HARD_SLO_MS else "FAIL"
    soft_verdict = "PASS" if p95 < SOFT_SLO_MS else "WARN"

    payload_out = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "host": args.host,
        "n_samples": len(timings),
        "fails": fails,
        "stats_ms": {
            "min": pmin,
            "max": pmax,
            "mean": mean,
            "stdev": stdev,
            "p50": p50,
            "p95": p95,
            "p99": p99,
        },
        "slo_ms": {"hard": HARD_SLO_MS, "soft_edge_tts": SOFT_SLO_MS},
        "verdict": verdict,
        "soft_verdict": soft_verdict,
        "tts_runtime": {
            "kind": tts_kind,
            "mode": mode_now,
            "model_downloaded": model_dl,
            "hardware": hw,
        },
        "samples": samples,
    }
    Path(args.out_json).write_text(json.dumps(payload_out, indent=2))
    print(f"\n[json] {args.out_json}")

    # Markdown report
    md = []
    md.append(f"# S191 D-3 — Voice TTS Latency (production endpoint `/api/voice/say`)")
    md.append("")
    md.append(f"**Generato**: {payload_out['ts']}")
    md.append("")
    md.append(f"**Host bench**: `{args.host}` (voice-pipeline FLUXION)")
    md.append(f"**Iterazioni**: warmup={args.warmup}, bench={n}, valide={len(timings)}, fail={fails}")
    md.append(f"**Corpus**: 50 utterance italiane realistiche (greeting/conferma/slot/disambiguazione/errore/chiusura/WA/short)")
    md.append("")
    md.append("## TTS runtime osservato")
    md.append("")
    md.append(f"- `tts` reported by `/health`: `{tts_kind}`")
    md.append(f"- `/api/tts/mode`: `{mode}`")
    md.append(f"- `/api/tts/hardware`: `{hw}`")
    md.append("")
    md.append("> NB: la pipeline FLUXION usa modalità `auto` con TTS Selector 3-tier (Edge-TTS / Piper / SystemTTS).")
    md.append("> Quando `model_downloaded=false` Piper non è disponibile e il selector ricade su Edge-TTS (cloud).")
    md.append("")
    md.append("## SLO target")
    md.append("")
    md.append("- **Hard cap (Piper offline FAST tier)**: P95 < 800 ms")
    md.append("- **Soft target (Edge-TTS QUALITY tier, cloud)**: P95 ~500 ms (rule `architecture-distribution.md`)")
    md.append("")
    md.append("## Risultati")
    md.append("")
    md.append("| Metrica | Valore |")
    md.append("|---------|--------|")
    md.append(f"| min | {pmin:.1f} ms |")
    md.append(f"| mean | {mean:.1f} ms |")
    md.append(f"| stdev | {stdev:.1f} ms |")
    md.append(f"| **P50** | **{p50:.1f} ms** |")
    md.append(f"| **P95** | **{p95:.1f} ms** |")
    md.append(f"| **P99** | **{p99:.1f} ms** |")
    md.append(f"| max | {pmax:.1f} ms |")
    md.append("")
    md.append(f"**Verdict hard SLO (<800ms P95)**: `{verdict}`")
    md.append("")
    md.append(f"**Verdict soft SLO (<500ms P95 Edge-TTS)**: `{soft_verdict}`")
    md.append("")
    md.append("## Sample timings (5 frasi)")
    md.append("")
    md.append("| # | text_chars | elapsed_ms | audio_hex_len | text |")
    md.append("|---|-----------:|-----------:|---------------:|------|")
    for s in samples[:5]:
        if s.get("success"):
            md.append(
                f"| {s['i']} | {s['text_chars']} | {s['elapsed_ms']:.1f} | {s['audio_hex_len']} | "
                + (s.get('text', '') or CORPUS[s['i']])[:50].replace("|", "\\|")
                + " |"
            )
    md.append("")
    md.append("## Considerazioni")
    md.append("")
    if model_dl is False:
        md.append("- **Piper model NON installato** sul box di test (`model_downloaded=false`).")
        md.append("  L'SLO Piper offline P95 <800ms NON è verificabile su questo runtime.")
        md.append("  Tech debt: install `piper` binary + download `it_IT-paola-medium.onnx` (S192).")
        md.append("")
    md.append("- I numeri qui sopra rappresentano il path **produzione corrente** (Edge-TTS cloud) come servito dal voice-pipeline.")
    md.append("- L'endpoint `/api/voice/say` chiama `orchestrator.tts.synthesize()` quindi include: serializzazione richiesta → selector tier → sintesi audio → encoding → JSON response.")
    md.append("- Per testare offline-Piper isolato: installare il binary, riavviare pipeline, rilanciare lo stesso script (corpus identico, deterministic).")
    md.append("")
    md.append("## Reproduce")
    md.append("")
    md.append("```bash")
    md.append("# Su iMac (voice-pipeline running)")
    md.append("ssh imac \"python3 /Volumes/MacSSD\\ -\\ Dati/fluxion/tools/perf-d3/run_tts_bench.py\"")
    md.append("# Da MacBook (via LAN)")
    md.append("python3 tools/perf-d3/run_tts_bench.py --host http://192.168.1.2:3002")
    md.append("```")
    md.append("")

    out_md_path = Path(args.out_md)
    out_md_path.parent.mkdir(parents=True, exist_ok=True)
    out_md_path.write_text("\n".join(md))
    print(f"[md]   {out_md_path}")
    print(
        f"\nRESULT  P50={p50:.0f}ms  P95={p95:.0f}ms  P99={p99:.0f}ms  hard_slo={verdict}  soft_slo={soft_verdict}"
    )


if __name__ == "__main__":
    main()
