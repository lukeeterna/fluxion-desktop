/**
 * Genera file MP3 per ogni scena del tutorial usando macOS `say` (voce Alice it_IT).
 * Output: public/voiceover/scene-NN.mp3
 *
 * Usa: node --strip-types generate-audio.ts
 */
import { execSync } from "child_process";
import { existsSync, mkdirSync } from "fs";

const OUT_DIR = "./public/voiceover";
mkdirSync(OUT_DIR, { recursive: true });

const SCENES: { id: string; text: string }[] = [
  {
    id: "01-intro",
    text: "Benvenuti in FLUXION, il gestionale desktop con intelligenza artificiale per le piccole imprese italiane. Saloni, palestre, cliniche, officine: vedremo insieme tutte le funzionalità.",
  },
  {
    id: "02-setup",
    text: "La prima volta che avvii FLUXION, una procedura guidata ti aiuta a configurare la tua attività. Scegli il settore, inserisci il nome e gli orari. In meno di cinque minuti sei operativo.",
  },
  {
    id: "03-dashboard",
    text: "La dashboard è il tuo pannello di controllo. Vedi subito gli appuntamenti di oggi, i clienti totali, il fatturato del mese e i servizi più richiesti.",
  },
  {
    id: "04-clienti",
    text: "Nella sezione Clienti tieni l'anagrafica completa. Cerca per nome o telefono, aggiungi nuovi clienti in pochi secondi e visualizza lo storico completo di ogni persona.",
  },
  {
    id: "05-calendario",
    text: "Il calendario mensile visualizza tutti gli appuntamenti con un colpo d'occhio. Ogni prenotazione è colorata per tipo di servizio. Clicca su qualsiasi giorno per i dettagli o per aggiungere una nuova prenotazione.",
  },
  {
    id: "06-sara",
    text: "Sara è la tua assistente vocale con intelligenza artificiale. Risponde al telefono al posto tuo, ventiquattro ore su ventiquattro. Riconosce il cliente, verifica la disponibilità, conferma la prenotazione e invia la conferma WhatsApp in automatico.",
  },
  {
    id: "07-verticali",
    text: "FLUXION include schede specializzate per ogni settore. L'odontogramma interattivo per gli studi dentistici, le scale di valutazione clinica per la fisioterapia, e moduli personalizzati per l'estetica, le palestre e le officine.",
  },
  {
    id: "08-fatture",
    text: "La fatturazione elettronica gestisce le fatture in formato XML compatibile con il Sistema di Interscambio italiano. Crea, emetti e scarica il file in un clic.",
  },
  {
    id: "09-outro",
    text: "FLUXION: un solo acquisto, nessun abbonamento, nessuna commissione. Licenza Base a centonovantasette euro, Pro a quattrocentonovantasette, Enterprise a ottocentonovantasette. Tuo per sempre.",
  },
];

for (const scene of SCENES) {
  const aiff = `${OUT_DIR}/${scene.id}.aiff`;
  const mp3 = `${OUT_DIR}/${scene.id}.mp3`;

  if (existsSync(mp3)) {
    console.log(`⏭  Skipping ${scene.id} (already exists)`);
    continue;
  }

  console.log(`🎙  Generating ${scene.id}...`);
  execSync(`say -v Alice -o "${aiff}" "${scene.text.replace(/"/g, '\\"')}"`);
  execSync(`ffmpeg -y -i "${aiff}" -q:a 3 "${mp3}" 2>/dev/null`);
  execSync(`rm "${aiff}"`);
  console.log(`  ✓ ${mp3}`);
}

console.log("\n✅ Audio generation complete.");
