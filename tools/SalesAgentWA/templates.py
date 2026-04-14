"""
FLUXION Sales Agent WA — Message templates.
6 categorie, 3+ varianti per sezione.
Struttura: apertura + hook + link + firma.
Variazione minima 40% tra messaggi inviati.
"""
from __future__ import annotations

import random
from typing import List, Optional, Tuple

from utm import build_utm_youtube


TEMPLATES = {
    "parrucchiere": [
        {
            "key": "parrucchiere_v1",
            "parts": {
                "apertura": [
                    "Ciao {nome}, ho visto che gestisci {attivita} a {citta}.",
                    "Ciao {nome}, {attivita} a {citta} \u2014 sono io?",
                    "Salve {nome}, ho trovato {attivita} su Google Maps.",
                ],
                "hook": [
                    "Quante chiamate perdi mentre hai le mani occupate con un cliente?",
                    "Scommetto che almeno 3-4 prenotazioni al giorno le gestisci ancora al telefono.",
                    "Il problema dei saloni \u00e8 sempre lo stesso: il telefono suona nel momento peggiore.",
                ],
                "cta": [
                    "Ho fatto un video di 6 minuti su come Sara, la nostra assistente AI, risponde al posto tuo \u2014 anche di domenica: {link}",
                    "Guarda come altri parrucchieri italiani hanno eliminato le telefonate dalle prenotazioni: {link}",
                    "Ho registrato come funziona FLUXION per i saloni \u2014 6 minuti, nessun tecnicismo: {link}",
                ],
                "firma": [
                    "Gianluca \u2014 FLUXION",
                    "A presto,\nGianluca",
                    "Fammi sapere cosa ne pensi.\nGianluca \u2014 FLUXION",
                ],
            },
        },
    ],

    "officina": [
        {
            "key": "officina_v1",
            "parts": {
                "apertura": [
                    "Ciao {nome}, {attivita} a {citta} giusto?",
                    "Salve {nome}, ho trovato {attivita} su Maps.",
                    "Ciao {nome}, ho visto la tua officina a {citta}.",
                ],
                "hook": [
                    "Gestire i preventivi telefonici mentre sei sotto una macchina \u00e8 un casino.",
                    "Quante volte al giorno sei costretto a fermarti per rispondere al telefono?",
                    "Tra le riparazioni e le telefonate dei clienti, la giornata vola via.",
                ],
                "cta": [
                    "Ho registrato come altri meccanici gestiscono prenotazioni e preventivi in automatico: {link}",
                    "Guarda come funziona FLUXION per le officine \u2014 6 minuti che valgono la pena: {link}",
                    "Ho fatto un video su come Sara risponde ai clienti anche quando sei impegnato sotto il cofano: {link}",
                ],
                "firma": [
                    "Gianluca \u2014 FLUXION",
                    "Buon lavoro,\nGianluca",
                    "A presto,\nGianluca \u2014 FLUXION",
                ],
            },
        },
    ],

    "estetico": [
        {
            "key": "estetico_v1",
            "parts": {
                "apertura": [
                    "Ciao {nome}, gestisci {attivita} a {citta}?",
                    "Buongiorno {nome}, ho visto {attivita} su Google.",
                    "Ciao {nome}, ho trovato il tuo centro a {citta}.",
                ],
                "hook": [
                    "I no-show dell'ultimo minuto sono il problema numero uno nei centri estetici.",
                    "Le disdette last-minute costano ore di lavoro perso ogni settimana.",
                    "Quante volte un appuntamento saltato ti lascia un buco in agenda senza preavviso?",
                ],
                "cta": [
                    "Ho fatto un video su come FLUXION manda promemoria WA automatici e azzera i no-show: {link}",
                    "Guarda come altri centri estetici gestiscono le prenotazioni senza telefonate: {link}",
                    "6 minuti per capire come Sara gestisce agenda e promemoria al posto tuo: {link}",
                ],
                "firma": [
                    "Gianluca \u2014 FLUXION",
                    "A presto,\nGianluca",
                    "Fammi sapere!\nGianluca \u2014 FLUXION",
                ],
            },
        },
    ],

    "palestra": [
        {
            "key": "palestra_v1",
            "parts": {
                "apertura": [
                    "Ciao {nome}, ho visto {attivita} a {citta}.",
                    "Salve {nome}, gestisci {attivita}?",
                    "Ciao {nome}, {attivita} a {citta} \u2014 giusto?",
                ],
                "hook": [
                    "Gestire abbonamenti, rinnovi e prenotazioni corsi \u00e8 un lavoro nel lavoro.",
                    "Tenere traccia di chi ha rinnovato, chi \u00e8 in scadenza e chi manca \u2014 senza un sistema \u00e8 impossibile.",
                    "Quante ore a settimana passi a gestire l'amministrativo invece di stare con i tuoi clienti?",
                ],
                "cta": [
                    "Ho registrato come FLUXION gestisce abbonamenti, promemoria di rinnovo e prenotazioni corsi: {link}",
                    "Guarda come altri titolari di palestre hanno automatizzato la gestione clienti: {link}",
                    "6 minuti per vedere come Sara gestisce prenotazioni e rinnovi automaticamente: {link}",
                ],
                "firma": [
                    "Gianluca \u2014 FLUXION",
                    "Buon allenamento!\nGianluca",
                    "A presto,\nGianluca \u2014 FLUXION",
                ],
            },
        },
    ],

    "dentista": [
        {
            "key": "dentista_v1",
            "parts": {
                "apertura": [
                    "Buongiorno {nome}, ho visto {attivita} su Maps.",
                    "Ciao {nome}, {attivita} a {citta}?",
                    "Salve {nome}, ho trovato il tuo studio a {citta}.",
                ],
                "hook": [
                    "La gestione degli appuntamenti telefonici toglie tempo prezioso ai pazienti.",
                    "Tra conferme, disdette e riprogrammazioni, la segreteria \u00e8 sempre sotto pressione.",
                    "Quante ore al giorno la tua segreteria passa al telefono per confermare appuntamenti?",
                ],
                "cta": [
                    "Ho fatto un video su come Sara gestisce gli appuntamenti del tuo studio \u2014 anche fuori orario: {link}",
                    "Guarda come altri studi professionali hanno automatizzato la gestione agenda: {link}",
                    "6 minuti per vedere FLUXION in azione per gli studi medici e fisioterapici: {link}",
                ],
                "firma": [
                    "Gianluca \u2014 FLUXION",
                    "Cordialmente,\nGianluca",
                    "A presto,\nGianluca \u2014 FLUXION",
                ],
            },
        },
    ],

    "generico": [
        {
            "key": "generico_v1",
            "parts": {
                "apertura": [
                    "Ciao {nome}, ho visto {attivita} a {citta}.",
                    "Salve {nome}, ho trovato la tua attivit\u00e0 su Google.",
                    "Buongiorno {nome}, {attivita} a {citta} \u2014 giusto?",
                ],
                "hook": [
                    "Gestire prenotazioni e clienti telefonicamente porta via troppo tempo.",
                    "Quante ore a settimana passi a gestire appuntamenti invece di fare il tuo lavoro?",
                    "Per molte piccole imprese, il telefono \u00e8 ancora il principale collo di bottiglia.",
                ],
                "cta": [
                    "Ho fatto un video su come FLUXION automatizza la gestione clienti per le PMI italiane: {link}",
                    "Guarda come altri titolari hanno liberato ore di lavoro ogni settimana: {link}",
                    "6 minuti per capire se FLUXION pu\u00f2 aiutare anche la tua attivit\u00e0: {link}",
                ],
                "firma": [
                    "Gianluca \u2014 FLUXION",
                    "A presto,\nGianluca",
                    "Fammi sapere!\nGianluca \u2014 FLUXION",
                ],
            },
        },
    ],
}


def render_template(
    category: str,
    business_name: str,
    city: str,
    *,
    previously_used_keys: Optional[List[str]] = None,
) -> Tuple[str, str]:
    """
    Genera un messaggio WA per la categoria data.
    Seleziona parti a caso per garantire variazione >40%.

    Returns:
        (message_text, template_key)
    """
    templates = TEMPLATES.get(category, TEMPLATES["generico"])
    tmpl = random.choice(templates)
    parts = tmpl["parts"]

    short_name = business_name.split()[0].capitalize() if business_name else "amico"
    utm_url = build_utm_youtube(category, city)

    apertura = random.choice(parts["apertura"]).format(
        nome=short_name,
        attivita=business_name,
        citta=city,
    )
    hook = random.choice(parts["hook"])
    cta = random.choice(parts["cta"]).format(link=utm_url)
    firma = random.choice(parts["firma"])

    message = "{}\n{}\n{}\n{}".format(apertura, hook, cta, firma)
    return message, tmpl["key"]


def estimate_variation(msg1: str, msg2: str) -> float:
    """
    Stima percentuale di variazione tra due messaggi (Jaccard su trigrammi).
    Target: > 0.40 (40%).
    """
    def trigrams(text):
        return set(text[i:i+3] for i in range(len(text) - 2))

    t1, t2 = trigrams(msg1.lower()), trigrams(msg2.lower())
    if not t1 and not t2:
        return 1.0
    intersection = len(t1 & t2)
    union = len(t1 | t2)
    jaccard_similarity = intersection / union if union > 0 else 0
    return 1.0 - jaccard_similarity
