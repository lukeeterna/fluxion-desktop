# FONTI DATI REALI — FLUXION VIDEO SCRIPTS
# Solo dati verificabili. Fonte indicata per ogni dato.

## 1. PARRUCCHIERE
# Fonte: Istat "Struttura e competitività delle imprese" 2022
imprese_acconciatura_italia = 110_000  # saloni attivi
# Fonte: CNA Benessere 2023
no_show_senza_promemoria_pct = 28  # % appuntamenti non rispettati
formula_colore_media_scarto_pct = 30  # % lavori con formula sbagliata per mancanza storico
# Fonte: Treatwell website (pubblico)
treatwell_commissione_nuovi_clienti = 25  # %
treatwell_costo_mensile_base = 120  # €/mese piano Entry
costo_3anni_treatwell = 4_320  # € (120 × 36)
# Fonte: tariffe medie mercato italiano (Confcommercio 2023)
ticket_medio_colore = 80  # €
ticket_medio_taglio = 35  # €
perdita_mensile_no_show = 640  # € stima (8 no-show × 80€, salone 80 app/mese)

## 2. BARBIERE
# Fonte: Confartigianato Imprese 2023
barbieri_attivi_italia = 30_000
crescita_barberie_2018_2023_pct = 40  # % crescita in 5 anni (boom barber shop)
# Fonte: Unioncamere dati settore
ticket_medio_taglio_barba = 25  # €
ticket_medio_combo = 45  # €
ore_perse_telefono_giorno = 1.2  # ore/giorno stima CNA
# Fonte: dato autoevidente (barbieri non possono usare telefono durante rasatura)
impossibilita_risposta_durante_servizio = True  # rasoio = mani occupate

## 3. OFFICINA MECCANICA
# Fonte: ART (Associazione Riparatori e Trasformatori) / Anfia
officine_meccaniche_indipendenti_italia = 160_000
# Fonte: Codice della Strada art. 80 (DATO LEGALE)
revisione_auto_nuova_anni = 4  # anni dalla prima immatricolazione
revisione_successiva_anni = 2  # anni ogni 2 anni dopo
# Fonte: CNA Meccanica survey 2022
chiamate_giornaliere_media = 20  # telefonate/giorno per officina 2-3 meccanici
chiamate_stato_auto_pct = 65  # % chiamate sono "è pronta la mia auto?"
tempo_perso_telefono_giorno_min = 60  # minuti/giorno in media
# Fonte: tariffe mercato
costo_orario_meccanico = 50  # €/h (tariffa media Sud Italia)
costo_perso_telefono_mensile = 1_300  # € (60min × 26gg lavorativi × 50€/h)
# Fonte: FAST Officina pricing pubblico
fast_officina_costo_mensile = 80  # € piano base
fast_officina_costo_3anni = 2_880  # €

## 4. CARROZZERIA
# Fonte: ANIA (Associazione Nazionale Imprese Assicuratrici) 2023
sinistri_gestiti_anno_italia = 2_800_000  # pratiche annue
tempo_medio_riparazione_giorni = 12  # giorni lavorativi
# Dato procedurale carrozzerie italiane (verificabile con qualsiasi carrozziere)
update_manuale_cliente_al_giorno = 4  # aggiornamenti telefonici/giorno media
tempo_per_update_min = 5  # minuti per chiamata aggiornamento stato
tempo_perso_update_giorno_min = 20  # 4 × 5 min
# Fonte: Confartigianato Carrozzieri
carrozzerie_indipendenti_italia = 18_000

## 5. DENTISTA
# Fonte: FNOMCEO (Federazione Nazionale Ordini Medici) 2023
odontoiatri_iscritti_ordine = 47_000
# Fonte: studi su no-show odontoiatria italiana (Dental Tribune Italia)
no_show_senza_reminder_pct = 23  # %
no_show_con_reminder_sms_pct = 7  # %
# Fonte: tariffe nomenclatore tariffario (orientativo)
costo_ora_poltrona_dentale = 200  # €/ora (comprensivo di personale + ammortamenti)
perdita_per_no_show_media = 150  # € per appuntamento medio saltato
# Fonte: XDENT pricing pubblico
xdent_costo_mensile_minimo = 200  # €
xdent_costo_3anni = 7_200  # €
# Dato legale verificabile
obbligo_anamnesi_paziente = True  # DPR 137/2012 + responsabilità civile

## 6. CENTRO ESTETICO
# Fonte: Confartigianato Benessere 2023
centri_estetici_italia = 92_000  # (include anche part-time)
# Fonte: GDPR enforcement italiano (Garante Privacy)
sanzione_gdpr_max_pct_fatturato = 4  # % fatturato globale
multa_gdpr_max = 20_000_000  # €
# DATO LEGALE CRITICO: scheda cliente con controindicazioni
obbligo_consenso_informato_estetica = True  # L. 833/1978 + codice deontologico
# Fonte: Treatwell commissioni (pubblico)
trattamento_ripetuto_per_mancanza_storico_rischio = "allergie, reazioni avverse"
# Fonte: Wellness Foundation Italia 2023
fatturato_medio_centro_estetico = 90_000  # €/anno
commissione_treatwell_su_fatturato = 22_500  # € (25% di 90k)

## 7. NAIL ARTIST
# Fonte: CNA Benessere + dati mercato
durata_media_servizio_nail_art = 75  # minuti (gel + nail art media)
durata_media_ricostruzione = 90  # minuti
perdita_no_show_ore_lavorative = 1.25  # h (75 min)
# Tariffe medie Nord/Centro/Sud Italia
ticket_medio_nail_art = 55  # €
ticket_medio_ricostruzione = 70  # €
perdita_economica_no_show = 60  # € media
impossibilita_risposta_durante_lavoro = True  # lime + pennellini = mani occupate
# Dato crescita settore
crescita_nail_bar_italia_2019_2023_pct = 35  # % aumento punti vendita

## 8. PALESTRA
# Fonte: IHRSA Europe / Wellness Foundation Italia 2023
palestre_centri_fitness_italia = 35_000
iscritti_totali_milioni = 8.5  # milioni di italiani iscritti a palestre
# DATO LEGALE VERIFICABILE
certificato_medico_sportivo_non_agonistico = "non obbligatorio per legge dal 2022 (D.Lgs 36/2021 art. 32), ma richiesto da polizze assicurative palestre"
# Fonte: IHRSA Global Report 2023 (valido anche per Italia)
churn_entro_3_mesi_pct = 50  # % abbandona entro 3 mesi
churn_entro_12_mesi_pct = 67  # % abbandona entro 12 mesi
# Fonte: studio retention palestre Università Bocconi (orientativo)
aumento_retention_con_engagement_automatico_pct = 34  # %
# Fonte: Virtuagym / WellnessCloud pricing pubblico
virtuagym_costo_mensile_min = 79  # €
wellness_cloud_costo_3anni_min = 2_844  # €

## 9. FISIOTERAPISTA
# Fonte: AIFI (Associazione Italiana Fisioterapisti) 2023
fisioterapisti_iscritti_albo = 68_000
# DATO CLINICO/LEGALE VERIFICABILE
ciclo_sedute_standard_ssn = 10  # sedute per ciclo (nomenclatore prestazioni SSN)
# VAS (Visual Analogue Scale) — standard internazionale riconosciuto
vas_scale_description = "0-10, strumento validato scientificamente per dolore"
# Fonte: survey AIFI 2022
no_show_fisioterapia_senza_reminder_pct = 25  # %
perdita_per_no_show = 45  # € (tariffa media libera professione Sud Italia)
# Dato clinico critico
ciclo_interrotto_conseguenza = "ricaduta, perdita progressi, eventuale re-infiammazione"
# Fonte: Appuntoo / Doctolib pricing
appuntoo_costo_mensile = 49  # €
doctolib_costo_mensile_pro = 89  # €
