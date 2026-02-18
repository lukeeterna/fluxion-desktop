#!/usr/bin/env python3
"""
Test Live Scenarios v0.8.1 - Fluxion Voice Agent
Simulazione dei 5 scenari di test live
"""

import sys
import sqlite3
sys.path.insert(0, '/Volumes/MacSSD - Dati/fluxion/voice-agent')

from src.disambiguation_handler import (
    DisambiguationHandler, is_phonetically_similar, 
    name_similarity, check_name_ambiguity
)
from src.booking_state_machine import BookingState

print("=" * 70)
print("🧪 TEST LIVE VOICE AGENT v0.8.1 - SCENARI AUTOMATIZZATI")
print("=" * 70)

# Connessione DB
db_path = '/Volumes/MacSSD - Dati/fluxion/fluxion.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

handler = DisambiguationHandler()
results = []

# ============================================================
# SCENARIO 1: "Gino vs Gigio" 🎭
# ============================================================
print("\n" + "=" * 70)
print("🎭 SCENARIO 1: Gino vs Gigio - Disambiguazione fonetica")
print("=" * 70)

cursor = conn.cursor()
cursor.execute("SELECT * FROM clienti WHERE cognome = 'Peruzzi'")
clienti = cursor.fetchall()

print(f"📋 Clienti 'Peruzzi' in DB: {len(clienti)}")
for c in clienti:
    print(f"   - {c['nome']} {c['cognome']} (tel: {c['telefono']})")

# Test fonetico
similarity = name_similarity("Gino", "Gigio")
print(f"\n🔍 Test name_similarity 'Gino' vs 'Gigio': {similarity:.2f}")

# Simulazione: Utente dice "Gino" ma in DB c'\u00e8 "Gigio"
# Se similarity > 0.5 c'\u00e8 potenziale ambiguit\u00e0
has_ambiguity, score, reason = check_name_ambiguity("Gino", "Gigio")
print(f"🔍 check_name_ambiguity: ambiguity={has_ambiguity}, score={score:.2f}, reason={reason}")

scenario1_pass = len(clienti) > 0 and similarity > 0.5
results.append(("SCENARIO 1: Gino vs Gigio", scenario1_pass))
print(f"✅ Scenario 1: {'PASS' if scenario1_pass else 'FAIL'}")

# ============================================================
# SCENARIO 4: "STT Confuso - Generi" 🔀
# ============================================================
print("\n" + "=" * 70)
print("🔀 SCENARIO 4: STT Confuso - Errori STT su genere (Mario/Maria)")
print("=" * 70)

cursor.execute("SELECT * FROM clienti WHERE cognome = 'Bianchi'")
clienti_bianchi = cursor.fetchall()

print(f"📋 Clienti 'Bianchi' in DB: {len(clienti_bianchi)}")
for c in clienti_bianchi:
    print(f"   - {c['nome']} {c['cognome']} (tel: {c['telefono']})")

# Test fonetico Mario vs Maria
sim_mario = name_similarity("Mario", "Maria")
phonetic_mario = is_phonetically_similar("Mario", "Maria")
print(f"\n🔍 Test name_similarity 'Mario' vs 'Maria': {sim_mario:.2f}")
print(f"🔍 is_phonetically_similar: {phonetic_mario}")

# Test disambiguazione
has_amb, score_m, reason_m = check_name_ambiguity("Mario", "Maria")
print(f"🔍 check_name_ambiguity: ambiguity={has_amb}, score={score_m:.2f}")

scenario4_pass = len(clienti_bianchi) > 0 and phonetic_mario
results.append(("SCENARIO 4: STT Confuso Generi", scenario4_pass))
print(f"✅ Scenario 4: {'PASS' if scenario4_pass else 'FAIL'}")

# ============================================================
# SCENARIO 2 & 3: Stati della State Machine 💬📞
# ============================================================
print("\n" + "=" * 70)
print("💬📞 SCENARIO 2 & 3: Verifica Stati State Machine")
print("=" * 70)

# Verifica che lo stato ASKING_CLOSE_CONFIRMATION esista
states = [s.value for s in BookingState]
print(f"📋 Stati disponibili ({len(states)}):")
for s in states:
    print(f"   - {s}")

has_close_confirmation = 'asking_close_confirmation' in states
has_waiting_close = 'waiting_close_confirmation' in states
print(f"\n🔍 Stato ASKING_CLOSE_CONFIRMATION presente: {has_close_confirmation}")
print(f"🔍 Stato WAITING_CLOSE_CONFIRMATION presente: {has_waiting_close}")

scenario2_3_pass = has_close_confirmation or has_waiting_close
results.append(("SCENARIO 2&3: Chiusura Graceful", scenario2_3_pass))
print(f"✅ Scenario 2&3: {'PASS' if scenario2_3_pass else 'FAIL'}")

# ============================================================
# SCENARIO 5: Rifiuto Booking 🙅‍♂️
# ============================================================
print("\n" + "=" * 70)
print("🙅‍♂️ SCENARIO 5: Verifica gestione rifiuto booking")
print("=" * 70)

# Verifica che lo stato CONFIRMING esista per gestire il rifiuto
has_confirming = 'confirming' in states
has_collecting = 'collecting_info' in states
print(f"🔍 Stato CONFIRMING presente: {has_confirming}")
print(f"🔍 Stato COLLECTING_INFO presente: {has_collecting}")

scenario5_pass = has_confirming
results.append(("SCENARIO 5: Rifiuto Booking", scenario5_pass))
print(f"✅ Scenario 5: {'PASS' if scenario5_pass else 'FAIL'}")

# ============================================================
# Verifica WhatsApp Integration
# ============================================================
print("\n" + "=" * 70)
print("📱 Verifica Integrazione WhatsApp")
print("=" * 70)

try:
    from src.whatsapp import WhatsAppClient
    print("✅ Modulo WhatsApp importato correttamente")
    wa_pass = True
except Exception as e:
    print(f"⚠️ Errore import WhatsApp: {e}")
    wa_pass = False

results.append(("WhatsApp Integration", wa_pass))

# ============================================================
# RIEPILOGO
# ============================================================
print("\n" + "=" * 70)
print("📊 RIEPILOGO TEST AUTOMATIZZATI")
print("=" * 70)

all_pass = True
for name, passed in results:
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    all_pass = all_pass and passed

print("\n" + "=" * 70)
if all_pass:
    print("🎉 TUTTI I TEST AUTOMATIZZATI PASSATI!")
    print("\n🔥 PRONTI PER TEST LIVE VOCALI:")
    print("   1. Avvia il Voice Agent su iMac")
    print("   2. Esegui i 5 scenari con interazione vocale")
    print("   3. Verifica WhatsApp inviati")
    print("\n🚀 Se i test live passano → BUILD v0.8.1")
else:
    print("⚠️ ALCUNI TEST FALLITI - Verificare prima dei test live")
print("=" * 70)

conn.close()
