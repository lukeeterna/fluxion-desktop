# SARA VOICE AGENT - FLUXION
## Specification Documento | Lifetime License Model

**Versione:** 1.0 Production Spec  
**Data:** 28 January 2026  
**Business Model:** Lifetime License (Zero Recurring Costs)  
**Target:** PMI Italiane (1-15 dipendenti)

---

## EXECUTIVE SUMMARY

**SARA** è un voice agent enterprise per prenotazioni automatiche offline-first.
- **Modello:** Desktop app Tauri + React, distribuita come **one-time license**
- **Prezzo:** €199-499 (pagamento unico lifetime)
- **Installazione:** Click-and-play, 5 minuti
- **Funzionamento:** 100% offline (Groq API opzionale come fallback)

**Verticali:** Salone bellezza, palestre, cliniche mediche, officine auto

---

## PRICING & BUSINESS MODEL (LIFETIME LICENSE)

### Tier Pricing

```
SARA Basic - €199/lifetime
├─ Voice agent core (STT + TTS + NLU)
├─ Up to 3 verticali
├─ Single location
├─ Basic CRM (contacts only)
├─ Community support (Discord)
└─ Free updates forever

SARA Professional - €399/lifetime
├─ All in Basic +
├─ All 4 verticali (salone, palestra, medical, auto)
├─ Multi-location support (up to 5 branches)
├─ Advanced CRM (history, analytics)
├─ Priority email support
├─ Custom branding (logo in UI)
└─ Free updates forever

SARA Enterprise - €799/lifetime (custom)
├─ All in Professional +
├─ Unlimited locations
├─ Custom verticali development
├─ White-label option
├─ Dedicated onboarding (2h call)
├─ Priority support (phone + email)
└─ Free updates forever

∞ Add-ons (Paid Once):
├─ Extra verticale: €50
├─ Custom integrations (API/Zapier): €100
├─ Advanced analytics: €30
└─ Offline speech models upgrade: €20
```

### Revenue Model (Fluxion)

```
Per Customer Acquisition:

Customer Type          Entry Point        Conversion    LTV (Lifetime)
┌────────────────────┬─────────────────┬────────────┬───────────┐
│ Salone (avg)       │ €199            │ 40%        │ €199      │
│ Palestra (avg)     │ €299            │ 35%        │ €299      │
│ Clinica medica     │ €399            │ 45%        │ €399      │
│ Officina auto      │ €249            │ 30%        │ €249      │
└────────────────────┴─────────────────┴────────────┴───────────┘

Customer Acquisition:
├─ Marketing budget: €20/customer (Google Ads, FB, LinkedIn)
├─ Target: 5.000 PMI first year
├─ Revenue: 5.000 × €299 avg = €1.495.000
├─ COGS/delivery: €100k (cloud infra minimal, mostly local)
├─ Profit margin: 93%
└─ Year 1 projection: €1.3M profit
```

### Why Lifetime Model Works for Fluxion

```
ADVANTAGES:
1. ✅ Product-market fit: PMI italiane ODIANO abbonamenti ricorrenti
   - Hanno margini 15-25%, ogni €30/mese è critico
   - Preferiscono "buy once, use forever"

2. ✅ No subscription infrastructure needed
   - Zero SaaS complexity (no billing, no churn, no renewal emails)
   - Zero support for subscription management
   - Reduced ongoing costs

3. ✅ Competitive advantage
   - Competitor medio: €30-99/month = €360-1188/year
   - Fluxion lifetime: €199-799 one-time = HUGE win

4. ✅ Updates = Free (builds loyalty)
   - Customers upgrade forever ("free updates" messaging)
   - No churn (product improves, not degrades)

5. ✅ Scalability to 50k+ PMI
   - Each license sold = no ongoing cost
   - Pure profit scaling (COGS = ~€100 server per 1000 customers)

CHALLENGES:
1. ❌ Requires strong product (bugs = permanent reputation damage)
2. ❌ Long sales cycle (customer hesitant on big one-time purchase)
3. ❌ Support costs deferred (must handle well)
```

---

## TECHNICAL ARCHITECTURE (LIFETIME COMPATIBLE)

### Distribution Model

```
Fluxion Desktop App (Tauri 2.x)
│
├─ Installer (.exe/.dmg/.deb)
│  ├─ Download size: ~120MB (Whisper + Coqui models bundled)
│  ├─ Installation: 5min (unpack models)
│  ├─ License activation: Email or serial key
│  └─ First time setup: 2min (vertical selection, DB init)
│
├─ LOCAL OPERATION (100% offline)
│  ├─ SQLite database (local file)
│  ├─ Whisper STT (local)
│  ├─ Coqui TTS (local)
│  ├─ UmBERTo NLU (local)
│  └─ State machine (in-process)
│
└─ OPTIONAL CLOUD (Groq fallback)
   ├─ Only if Whisper fails (network goes down)
   ├─ API key stored locally (optional)
   └─ Zero ongoing cost if unused
```

### License Activation (No Phone-Home)

```python
# Fluxion License Manager
class LicenseManager:
    def __init__(self):
        self.license_file = "~/.fluxion/sara/license.dat"
    
    def generate_key(self, customer_name: str, tier: str) -> str:
        """
        Crea chiave offline (client-side)
        - No server needed
        - Baseato su: username + machine_id + timestamp
        """
        import hashlib
        
        # Generate machine fingerprint
        machine_id = hashlib.sha256(
            f"{socket.gethostname()}{uuid.getnode()}".encode()
        ).hexdigest()[:16]
        
        # Crea chiave (pattern: FLUXION-XXXX-XXXX-XXXX-XXXX)
        key_data = f"{customer_name}:{tier}:{machine_id}:{datetime.now().year}"
        license_key = self._encode_license(key_data)
        
        return license_key
    
    def validate_license(self) -> bool:
        """
        Valida offline (nessuna connessione necessaria)
        """
        if not os.path.exists(self.license_file):
            return False  # No license → trial mode
        
        with open(self.license_file, 'r') as f:
            license_data = json.load(f)
        
        # Check: scadenza, tier, machine_id
        if datetime.now() > license_data.get('expiry'):
            return False  # Scaduto
        
        if license_data.get('machine_id') != self._get_machine_id():
            return False  # Installato su altro computer
        
        return True  # License valida
    
    def register_license(self, license_key: str):
        """
        User: digita il license key al primo avvio
        Salva localmente (no cloud sync needed)
        """
        validated = self._verify_key_format(license_key)
        
        if validated:
            license_data = {
                'key': license_key,
                'activated_at': datetime.now().isoformat(),
                'tier': self._extract_tier_from_key(license_key),
                'machine_id': self._get_machine_id(),
                'expiry': datetime(2099, 12, 31)  # Lifetime = far future
            }
            
            os.makedirs(os.path.dirname(self.license_file), exist_ok=True)
            with open(self.license_file, 'w') as f:
                json.dump(license_data, f)
            
            return True
        else:
            raise ValueError("Invalid license key")
    
    def trial_mode(self):
        """
        Se no license: trial mode (14 giorni)
        - Full features
        - "Expired" message every 3rd call
        - Redirect to purchase page
        """
        pass
```

**Advantages:**
- ✅ No backend needed (offline activation)
- ✅ No license verification calls (no tracking)
- ✅ No internet required to use Sara
- ✅ GDPR compliant (zero data transmission)

---

## REVENUE & COST STRUCTURE (LIFETIME)

### Year 1 Financial Model

```
ACQUISITION:
├─ Target customers: 5.000 PMI
├─ Avg ticket: €299 (Professional tier)
├─ Total revenue: €1.495.000
│
COGS:
├─ Cloud infrastructure (minimal): €50.000
│  ├─ Groq fallback servers: €2.000/month × 12
│  ├─ CDN for updates: €3.000/month × 12
│  └─ Database backups: €1.000/month × 12
│
├─ Support & operations: €60.000
│  ├─ Support team (1 FTE): €30.000
│  ├─ Community management: €15.000
│  └─ Bug fixes & patches: €15.000
│
├─ Development (post-launch): €80.000
│  ├─ New features & verticals: €40.000
│  ├─ ML model updates: €30.000
│  └─ Security patches: €10.000
│
└─ Total COGS: €190.000

OPERATING EXPENSES:
├─ Sales & Marketing: €200.000
│  ├─ Google Ads: €80.000
│  ├─ LinkedIn/Twitter: €40.000
│  ├─ Content marketing: €50.000
│  └─ Events/tradeshows: €30.000
│
├─ Salaries: €300.000
│  ├─ CTO (you): €100.000
│  ├─ 1 Sales: €80.000
│  ├─ 1 Support: €60.000
│  └─ 1 DevOps: €60.000
│
└─ Other (office, legal, etc): €60.000

TOTAL OPERATING EXPENSES: €560.000

PROFIT (Year 1):
├─ Revenue: €1.495.000
├─ COGS: €190.000
├─ OpEx: €560.000
└─ Net Profit: €745.000 (50% margin)
```

### Customer Lifetime Value (CLV)

```
Per Customer:

Initial Payment: €299 (Professional tier)
├─ Cost to acquire: €20 (marketing)
├─ Cost to deliver: €2 (infra/support amortized)
├─ Cost to service (lifetime): €5 (support, updates)
└─ Profit per customer: €272

Total CLV per customer: €272
├─ Recurring support cost: €0 (post year 1)
├─ Updates: Free forever (built into product)
└─ 5-year CLV: €272 (same as year 1)

ROI on €20 acquisition cost:
├─ Payback period: < 1 month
├─ CLV:CAC ratio: 13.6:1 (excellent, target is 3:1+)
└─ Year 1 revenue from customer: €299
```

### Unit Economics (Comparison vs SaaS)

```
FLUXION (Lifetime License):
├─ Avg ticket: €299
├─ Customer acquisition cost: €20
├─ Payback period: < 1 month
├─ Margin: 90%
├─ No churn risk
└─ Scaling cost: ~€100 per 1000 customers

COMPETITOR (SaaS €50/month):
├─ Avg ticket: €50/month
├─ Customer acquisition cost: €80 (2-month payback)
├─ Payback period: 2 months
├─ Margin: 60%
├─ Churn rate: 5% per month (customer loses confidence)
└─ Scaling cost: proportional to revenue

Year 5 Comparison (10.000 customers):
┌──────────────────┬──────────────┬─────────────────┐
│ Metric           │ Fluxion      │ Competitor      │
├──────────────────┼──────────────┼─────────────────┤
│ Cumulative Rev   │ €2.99M       │ €30M (no churn) │
│ Cumulative Cost  │ €950k        │ €12M            │
│ Net Profit       │ €2.04M       │ €18M            │
│ Margin           │ 68%          │ 60%             │
│ Scaling effort   │ Minimal      │ High (ops)      │
└──────────────────┴──────────────┴─────────────────┘

💡 Fluxion advantage: Simpler, more profit per customer early on.
   SaaS advantage: Exponential growth if retention high (unlikely).
```

---

## PRODUCT ROADMAP (LIFETIME COMPATIBLE)

### Phase 1: MVP (Weeks 1-6)
**Release:** €199 (Basic tier)
```
├─ Core voice agent (STT + TTS + NLU)
├─ 2 verticals: Salone, Palestra
├─ Basic state machine (slot filling)
├─ SQLite local DB
├─ Windows + Mac support
└─ Community support (Discord only)
```

### Phase 2: v1.0 (Weeks 7-14)
**Release:** €299 (Professional tier)
```
├─ All 4 verticals (add Medical + Auto)
├─ Advanced state machine (3-level correction logic)
├─ Multi-location support
├─ CRM integration (history, notes)
├─ Analytics dashboard (basic)
├─ Email support tier added
└─ Linux support
```

### Phase 3: v2.0 (Months 5-6)
**Release:** €499 (Professional +) / €799 (Enterprise)
```
├─ Advanced features:
│  ├─ Custom verticali builder (no-code)
│  ├─ API for integrations (Booking.com, WP, etc)
│  ├─ Advanced NLU (few-shot learning)
│  ├─ Multi-language support
│  ├─ White-label option
│  └─ Zapier integration
│
├─ Deployment:
│  ├─ Docker support (for tech-savvy SMBs)
│  ├─ Cloud SaaS version (optional, separate product)
│  └─ Kiosk mode (Raspberry Pi support)
│
└─ Pricing: Existing customers upgrade free
            (lifetime license = free v2.0 access)
```

### Phase 4+: Recurring (Maintenance & Minor Releases)
**Annual Releases**
```
├─ ML model improvements (Whisper, Coqui updates)
├─ New verticali (auto-repair shops, B&Bs, etc)
├─ Performance optimizations
├─ Security patches
└─ All included in lifetime license
```

---

## DISTRIBUTION & GO-TO-MARKET

### Channel Strategy

```
1. DIRECT SALES (40% revenue)
├─ Fluxion website: www.fluxion.it/sara
├─ Target: Salone & palestra owners
├─ Marketing: Google Ads (€1 CPC), Facebook (€0.50 CPC)
├─ Landing page: "Prenotazioni automatiche a vita"
├─ Conversion: 5-8% (typical for B2B SaaS)
└─ Sales cycle: 1-3 giorni (low-touch, self-serve)

2. RESELLER PARTNERSHIPS (35% revenue)
├─ Partner: Software house locali (Northover, etc)
├─ Margin: 20% for reseller, 80% for Fluxion
├─ Target: Implementare Sara nel loro portfolio
├─ Training: 1 webinar per reseller partner
└─ Support: Fluxion handles customer, reseller gets commission

3. INTEGRATION MARKETPLACES (15% revenue)
├─ Booking.com marketplace
├─ Software aggregators (Gartner, Capterra listings)
├─ Italian SMB portals
└─ Free listing (organic only)

4. WORD-OF-MOUTH (10% revenue)
├─ Existing Fluxion customers → referral bonus
├─ €50 referral fee per new customer
└─ Community momentum (Discord, Twitter)
```

### Customer Onboarding

```
Day 0: Purchase
├─ Download link emailed
├─ License key generated (automatic)
├─ Installation guide (5 min video)

Day 1: Activation
├─ Customer downloads & installs (120MB, 5min)
├─ Enters license key → unlocked
├─ Vertical selection (salone? palestra? etc)
├─ Database initialization

Days 1-3: First Use
├─ Auto-generated demo data (5 bookings)
├─ Interactive tutorial (voice agent demo)
├─ FAQ section (video tutorials)
├─ Optional: 15min onboarding call (€0, voluntary)

Days 3-7: Going Live
├─ Customer imports existing clients into CRM
├─ Sets up opening hours + availability
├─ Tests voice agent with friends
├─ Goes live with real calls

Support:
├─ Discord community (free tier)
├─ Email support (24h response, €299+ tiers)
├─ YouTube tutorials (self-serve)
├─ No phone support (keep costs low)
```

---

## COMPETITIVE POSITIONING

### Fluxion Sara vs Competitors

```
┌─────────────────┬──────────────┬────────────┬──────────────┬───────────┐
│ Feature         │ Sara Fluxion │ Voicebots  │ Voicetech.ai │ Easybot   │
├─────────────────┼──────────────┼────────────┼──────────────┼───────────┤
│ Pricing Model   │ Lifetime €199│ €299/mo    │ €1.200+/mo   │ €200/mo   │
│ Offline Mode    │ ✅ 100%      │ ❌ Cloud   │ ❌ Cloud     │ ❌ Cloud  │
│ Italian Tuned   │ ✅ UmBERTo   │ ⚠️ Generic │ ⚠️ Generic   │ ⚠️ Generic│
│ Setup Time      │ 5 min        │ 2 days     │ 1+ week      │ 1-2 days  │
│ Multi-location  │ ✅ (€399)    │ ❌         │ ✅ (+cost)   │ ⚠️ Limited│
│ CRM Integration │ ✅ Built-in  │ ⚠️ API     │ ✅ Full      │ Basic     │
│ Customization   │ ✅ (code)    │ ❌ None    │ ✅ Enterprise│ ❌        │
│ Support         │ Discord+mail │ Phone+chat │ Dedicated    │ Email     │
│ Data Privacy    │ ✅ GDPR local│ ❌ Cloud   │ ⚠️ Unclear   │ ❌ Cloud  │
│ Updates         │ ✅ Free      │ ❌ €/mo    │ ❌ €/mo      │ ❌ €/mo   │
└─────────────────┴──────────────┴────────────┴──────────────┴───────────┘

Positioning: "La soluzione SMB italiana. Paghi una volta, usi per sempre."
```

---

## IMPLEMENTATION TIMELINE (LIFETIME MODEL)

```
WEEK 1-2: Core Voice Pipeline
├─ Whisper STT (download, integrate)
├─ Coqui TTS (Carla voice)
├─ Silero VAD
└─ Basic NLU (UmBERTo)

WEEK 3-4: UI & State Machine
├─ Tauri React UI
├─ Recording interface
├─ Conversation display
├─ State machine logic

WEEK 5-6: Database & Vertical 1
├─ SQLite schema (booking, clients, history)
├─ Salone vertical (intents, slots, FAQ)
├─ License manager (offline activation)
└─ Windows/Mac builds

WEEK 7-8: Vertical 2 + Testing
├─ Palestra vertical
├─ Voice test suite (100+ Italian utterances)
├─ Performance optimization (latency < 4s)
├─ Beta testing with 10 SMBs

WEEK 9-10: Launch (€199 Basic tier)
├─ Website live (landing page + pricing)
├─ Marketing campaign (Google Ads, LinkedIn)
├─ Discord community setup
├─ Support team ready (1 person)

WEEK 11-14: v1.0 (€299 Professional)
├─ Medical + Auto verticals
├─ Multi-location support
├─ Advanced analytics
├─ Email support tier
└─ Release date: ~8 weeks post-MVP

TOTAL: 14 weeks (3.5 months) to v1.0

Cost breakdown:
├─ Development: €50k (your time as CTO)
├─ Infrastructure (first 3 months): €8k
├─ Marketing (launch): €20k
└─ Total: €78k
```

---

## CUSTOMER SUCCESS METRICS

### Target Metrics (Year 1)

```
ACQUISITION:
├─ Total customers: 5.000 SMBs
├─ Monthly growth: Month 1: 100, Month 6: 500/mo, Month 12: 600/mo
├─ Customer acquisition cost (CAC): €20
├─ Payback period: 14 days (€299 ÷ €20 CAC)

RETENTION & SATISFACTION:
├─ Churn rate: < 2% (lifetime license, no recurring)
├─ NPS (Net Promoter Score): > 60 (target)
├─ Customer satisfaction (CSAT): > 4.2/5
├─ Support ticket response time: < 24h

PRODUCT METRICS:
├─ Voice task completion rate: > 82%
├─ Average turns per booking: 4-5 (vs competitor 6-8)
├─ Voice STT WER (Italian): 9-11%
├─ End-to-end latency: 3-4 seconds (target < 3s)

REVENUE METRICS:
├─ Year 1 revenue: €1.495M
├─ Gross margin: 87%
├─ Net margin (after OpEx): 50%
├─ ARR per customer: €299 (one-time only)
└─ CLV: €272 (very high, low acquisition cost)
```

---

## FAQ FOR LIFETIME LICENSING

### Customer Questions

**Q: Che succede se il software smette di funzionare dopo 5 anni?**
A: Lifetime license = sei proprietario del software. Continua a funzionare offline per sempre. Se vuoi support/updates, il team continua a rilasciare versioni gratuite.

**Q: E se cambio computer?**
A: Possono usare lo stesso license key su max 2 computer (tuo + backup). Se serve 3+, paghi €50 per expanded license.

**Q: Cosa succede se Fluxion chiude?**
A: Il software continua a funzionare (è tutto locale). Se vuoi sorgente, chiedi via support (risorse permettendo).

**Q: Come ricevo gli aggiornamenti?**
A: Quando rilasciamo nuove versioni (ogni 3 mesi), ricevi email con download link. Installi sopra la versione precedente (mantieni licenza).

**Q: Posso rivendere la mia licenza a qualcuno?**
A: No, è nominale (linked al tuo machine_id). Se no longer need, contatta support per deactivate (non rifondo €).

---

## CONCLUSION

**Sara per Fluxion = Prodotto Lifetime su misura per PMI italiane**

✅ Modello di business semplice (no subscription complexity)
✅ Altissima profittabilità (87% gross margin)
✅ Zero churn risk (lifetime = forever)
✅ Competitore advantage (nessuno fa lifetime voice agent)
✅ Scalabilità massima (local-first = server costs minimal)

**Year 1 target: 5.000 customers, €1.3M profit**

---

**Documento:** SARA Specification v1.0  
**Status:** Production Ready  
**Ultimo aggiornamento:** 28 Jan 2026, 16:39 CET  
**Versione stack:** Tauri 2.x + React 19 + Python 3.11 + SQLite  
**Modello:** Lifetime License (Zero Recurring Costs)
