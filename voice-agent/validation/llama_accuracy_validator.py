#!/usr/bin/env python3
"""Llama 3.2 3B Accuracy Validation - Italian Intent Classification
Validation script for Fluxion Voice Agent
Target: >= 85% accuracy on Italian intents
"""

import json
import time
import sys
from datetime import datetime

try:
    from ollama import Client
except ImportError:
    print("Installing ollama python package...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ollama"])
    from ollama import Client


class LlamaAccuracyValidator:
    def __init__(self, model: str = "llama3.2:3b"):
        self.client = Client(host='http://localhost:11434')
        self.model = model
        self.results = []

    def test_intent_classification(self):
        """Test su 50 utterance italiani (5 verticali, 10 intent)"""

        # Test cases realistici per PMI italiane
        test_cases = [
            # SALONE (taglio, colore, piega, barba)
            ("Vorrei un taglio per sabato", "book_appointment", "salone"),
            ("Quanto costa il taglio?", "ask_info", "salone"),
            ("Avete disponibilità giovedì?", "check_availability", "salone"),
            ("Mi chiamo Marco Rossi", "provide_info", "salone"),
            ("Posso spostare a lunedì?", "modify_appointment", "salone"),
            ("Buongiorno", "greet", "salone"),
            ("Arrivederci, grazie", "goodbye", "salone"),
            ("Che servizi avete?", "list_services", "salone"),
            ("Devo annullare l'appuntamento", "cancel_appointment", "salone"),
            ("Non ho capito, può ripetere?", "clarify", "salone"),

            # PALESTRA (yoga, pilates, personal trainer, iscrizione)
            ("Vorrei una lezione di yoga", "book_appointment", "palestra"),
            ("Quanto costa l'iscrizione?", "ask_info", "palestra"),
            ("Avete corsi di pilates?", "list_services", "palestra"),
            ("Posso prenotare un personal trainer?", "book_appointment", "palestra"),
            ("Domani mattina siete aperti?", "check_availability", "palestra"),

            # MEDICAL (visita, esami, cardiologia, ortopedia)
            ("Vorrei una visita dal cardiologo", "book_appointment", "medical"),
            ("Quando mi fate gli esami del sangue?", "check_availability", "medical"),
            ("Quanto costa una visita specialistica?", "ask_info", "medical"),
            ("Devo cancellare la mia visita", "cancel_appointment", "medical"),
            ("Che specialisti avete?", "list_services", "medical"),

            # AUTO (revisione, gomme, tagliando, riparazione)
            ("Il mio motore fa un rumore strano", "ask_info", "auto"),
            ("Prenotazione revisione per marzo", "book_appointment", "auto"),
            ("Quanto costa cambiare le gomme?", "ask_info", "auto"),
            ("Posso portare la macchina domani?", "check_availability", "auto"),
            ("Devo spostare l'appuntamento del tagliando", "modify_appointment", "auto"),

            # RISTORANTE (pranzo, cena, tavolo, menu)
            ("Un tavolo per 4 sabato sera", "book_appointment", "ristorante"),
            ("Che piatti avete?", "ask_info", "ristorante"),
            ("Siete aperti a pranzo?", "check_availability", "ristorante"),
            ("Devo cancellare la prenotazione", "cancel_appointment", "ristorante"),
            ("Avete menu vegetariano?", "ask_info", "ristorante"),

            # Varianti colloquiali e dialettali
            ("Devo prenotare dal barbiere", "book_appointment", "salone"),
            ("Me fai un prezzo?", "ask_info", "salone"),
            ("Ce l'avete giovedi pomeriggio?", "check_availability", "salone"),
            ("Ciao, sono Mario", "provide_info", "salone"),
            ("Va bene, ci vediamo sabato", "goodbye", "salone"),

            # Edge cases
            ("Sì", "provide_info", "generic"),
            ("No grazie", "goodbye", "generic"),
            ("Ok perfetto", "provide_info", "generic"),
            ("Allora facciamo sabato alle 10", "book_appointment", "generic"),
            ("Mmm... non so, forse martedì", "provide_info", "generic"),

            # Frasi ambigue (test robustezza)
            ("Io non sono mai stato da voi", "provide_info", "salone"),
            ("È la mia prima volta qui", "provide_info", "salone"),
            ("Sono un cliente nuovo", "provide_info", "salone"),
            ("Il mio numero è 333 123 4567", "provide_info", "generic"),
            ("La mia email è mario@example.com", "provide_info", "generic"),

            # Intent complessi
            ("Vorrei prenotare un taglio e colore per sabato mattina verso le 10", "book_appointment", "salone"),
            ("Mi servirebbero informazioni sui prezzi dei trattamenti", "ask_info", "salone"),
            ("Posso sapere quando c'è disponibilità la prossima settimana?", "check_availability", "salone"),
        ]

        correct = 0
        latencies = []
        start_time = time.time()

        print(f"\n{'='*60}")
        print(f"  LLAMA 3.2 3B INTENT CLASSIFICATION TEST")
        print(f"  Model: {self.model}")
        print(f"  Samples: {len(test_cases)}")
        print(f"  Target: >= 85% accuracy")
        print(f"{'='*60}\n")

        for idx, (utterance, expected_intent, verticale) in enumerate(test_cases, 1):
            prompt = f"""Sei un classificatore di intent per un sistema vocale italiano.
Classifica l'intent del seguente messaggio.

Intent possibili (scegli UNO solo):
- book_appointment: prenotare, fissare appuntamento, riservare
- check_availability: chiedere disponibilità, quando siete aperti
- cancel_appointment: annullare, cancellare, disdire
- modify_appointment: spostare, modificare, cambiare appuntamento
- ask_info: chiedere informazioni, prezzi, costi
- provide_info: dare nome, telefono, email, confermare
- greet: saluto iniziale (buongiorno, ciao, salve)
- goodbye: saluto finale (arrivederci, grazie, ci vediamo)
- clarify: non capito, ripetere
- list_services: quali servizi, cosa fate

Messaggio: "{utterance}"

Rispondi SOLO con l'intent (una sola parola, minuscolo)."""

            try:
                req_start = time.time()
                response = self.client.generate(
                    model=self.model,
                    prompt=prompt,
                    stream=False,
                    options={"temperature": 0.1}
                )
                req_time = time.time() - req_start
                latencies.append(req_time)

                predicted_intent = response['response'].strip().lower()
                # Clean up response (sometimes model adds explanation)
                predicted_intent = predicted_intent.split()[0].strip('.,!')

                is_correct = predicted_intent == expected_intent

                self.results.append({
                    "utterance": utterance,
                    "verticale": verticale,
                    "expected": expected_intent,
                    "predicted": predicted_intent,
                    "correct": is_correct,
                    "latency_ms": req_time * 1000
                })

                if is_correct:
                    correct += 1
                    status = "✅"
                else:
                    status = "❌"

                print(f"{idx:2d}. {status} [{req_time*1000:.0f}ms] {utterance[:45]}")
                if not is_correct:
                    print(f"      Expected: {expected_intent}, Got: {predicted_intent}")

            except Exception as e:
                print(f"{idx:2d}. ⚠️  ERROR: {e}")
                self.results.append({
                    "utterance": utterance,
                    "verticale": verticale,
                    "expected": expected_intent,
                    "predicted": "ERROR",
                    "correct": False,
                    "latency_ms": 0
                })

        elapsed = time.time() - start_time
        accuracy = (correct / len(test_cases)) * 100
        avg_latency = sum(latencies) / len(latencies) if latencies else 0

        print(f"\n{'='*60}")
        print(f"  RESULTS")
        print(f"{'='*60}")
        print(f"  Overall Accuracy: {accuracy:.1f}% ({correct}/{len(test_cases)})")
        print(f"  Avg Latency:      {avg_latency*1000:.0f} ms per utterance")
        print(f"  Total Time:       {elapsed:.1f} sec")
        print(f"{'='*60}")

        # Per verticale breakdown
        print("\n  Accuracy per verticale:")
        verticali = set(v[2] for v in test_cases)
        for vert in sorted(verticali):
            vert_results = [r for r in self.results if r['verticale'] == vert]
            if vert_results:
                vert_acc = sum(1 for r in vert_results if r['correct']) / len(vert_results) * 100
                print(f"    {vert:12s}: {vert_acc:.1f}%")

        # Errori comuni
        errors = [r for r in self.results if not r['correct']]
        if errors:
            print(f"\n  Errori comuni:")
            error_patterns = {}
            for e in errors:
                key = f"{e['expected']} -> {e['predicted']}"
                error_patterns[key] = error_patterns.get(key, 0) + 1
            for pattern, count in sorted(error_patterns.items(), key=lambda x: -x[1])[:5]:
                print(f"    {pattern}: {count}x")

        result = {
            "model": self.model,
            "timestamp": datetime.now().isoformat(),
            "overall_accuracy": accuracy,
            "avg_latency_ms": avg_latency * 1000,
            "total_samples": len(test_cases),
            "correct": correct,
            "pass_criteria": accuracy >= 85,
            "results": self.results
        }

        # Save results
        with open("llama_validation_results.json", "w") as f:
            json.dump(result, f, indent=2)

        print(f"\n{'='*60}")
        if result['pass_criteria']:
            print(f"  ✅ PASS: Llama 3.2 3B accuracy {accuracy:.1f}% >= 85%")
            print(f"  Recommendation: Proceed with Llama 3.2 3B for intent classification")
        elif accuracy >= 75:
            print(f"  ⚠️  YELLOW: Accuracy {accuracy:.1f}% (75-85%)")
            print(f"  Recommendation: Consider Llama 3.2 8B or fine-tuning")
        else:
            print(f"  ❌ FAIL: Accuracy {accuracy:.1f}% < 75%")
            print(f"  Recommendation: Use larger model or cloud solution")
        print(f"{'='*60}\n")

        return result


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  FLUXION VOICE AGENT - LLAMA VALIDATION")
    print("="*60)
    print("\nPrerequisites:")
    print("  1. ollama serve (running)")
    print("  2. ollama pull llama3.2:3b (completed)")
    print()

    validator = LlamaAccuracyValidator()
    results = validator.test_intent_classification()
