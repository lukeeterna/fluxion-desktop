import React from "react";
import {
  AbsoluteFill,
  Audio,
  CalculateMetadataFunction,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";
// Series, Sequence unused (TransitionSeries used instead)
import { TransitionSeries, linearTiming, springTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";

// Shared colors (Fluxion dark theme)
export const C = {
  bg:      "#020617", sidebar: "#0f172a", card:  "#1e293b",
  card2:   "#334155", t1:     "#f1f5f9", t2:    "#94a3b8",
  t3:      "#475569", cyan:   "#22d3ee", cyanDk:"#0891b2",
  green:   "#10b981", yellow: "#f59e0b", red:   "#ef4444",
  violet:  "#8b5cf6", rose:   "#f43f5e", blue:  "#3b82f6",
  teal:    "#14b8a6",
} as const;

// Inline F-lettermark logo (cyan rounded square + white F)
const FluxionLogo: React.FC<{ size?: number }> = ({ size = 36 }) => (
  <svg width={size} height={size} viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="80" height="80" rx="16" fill="#06B6D4"/>
    <text x="40" y="57" fontFamily="system-ui,-apple-system,sans-serif" fontSize="52" fontWeight="800" fill="white" textAnchor="middle">F</text>
  </svg>
);

const SCENES = [
  "01-intro","02-setup","03-dashboard","04-clienti",
  "05-calendario","06-sara","07-verticali","08-fatture","09-outro",
] as const;

// ── calculateMetadata: durations driven by audio files ───────────────────────
export const calculateTutorialMetadata: CalculateMetadataFunction<{}> = async () => {
  const FPS = 30;
  const PADDING_S = 1.0; // extra seconds after each audio clip

  // We can't dynamically measure audio duration in this macOS version,
  // so use pre-measured values (seconds). Run: ffprobe -v quiet -print_format json -show_format <file>
  const durations: Record<string, number> = {
    "01-intro":     9.2,
    "02-setup":     10.8,
    "03-dashboard": 10.1,
    "04-clienti":   10.5,
    "05-calendario":11.3,
    "06-sara":      14.6,
    "07-verticali": 13.2,
    "08-fatture":    9.8,
    "09-outro":     13.9,
  };

  const sceneDurations = SCENES.map(id =>
    Math.ceil((durations[id] + PADDING_S) * FPS)
  );

  const TRANSITION_FRAMES = 15; // 0.5s fade between scenes
  const totalFrames = sceneDurations.reduce((sum, d) => sum + d, 0)
    - TRANSITION_FRAMES * (SCENES.length - 1);

  return {
    durationInFrames: totalFrames,
    props: {},
    metadata: { sceneDurations, TRANSITION_FRAMES },
  };
};

// ── Helpers ──────────────────────────────────────────────────────────────────
const fi = (frame: number, from: number, to: number, inF = 10, extrapolateRight = "clamp" as const) =>
  interpolate(frame, [from, from + inF], [0, 1], { extrapolateRight, extrapolateLeft: "clamp" });

const Card: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{ background: C.card, border: `1px solid ${C.card2}`, borderRadius: 8, padding: 14, ...style }}>
    {children}
  </div>
);

const FadeIn: React.FC<{ from?: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ from = 0, children, style }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [from, from + 12], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const y = interpolate(frame, [from, from + 12], [14, 0], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  return <div style={{ opacity, transform: `translateY(${y}px)`, ...style }}>{children}</div>;
};

// ── Sidebar navigation ────────────────────────────────────────────────────────
const NAV = ["Dashboard","Calendario","Clienti","Servizi","Operatori","Fatture","Cassa","Fornitori","Voice Agent","Impostazioni"];

const AppLayout: React.FC<{ active: string; children: React.ReactNode }> = ({ active, children }) => (
  <AbsoluteFill style={{ background: C.bg, fontFamily: "'Inter','Helvetica',sans-serif", display: "flex", flexDirection: "column" }}>
    {/* Header */}
    <div style={{ height: 54, background: "#0a1228", borderBottom: `1px solid ${C.card2}`, display: "flex", alignItems: "center", flexShrink: 0 }}>
      <div style={{ width: 222, display: "flex", alignItems: "center", gap: 10, paddingLeft: 14 }}>
        <FluxionLogo size={26} />
        <span style={{ color: C.cyan, fontWeight: 800, fontSize: 15, letterSpacing: -0.5 }}>FLUXION</span>
      </div>
      <div style={{ flex: 1, paddingLeft: 14 }}>
        <span style={{ color: C.t1, fontWeight: 700, fontSize: 14 }}>{active}</span>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 10, paddingRight: 14 }}>
        <div style={{ background: C.card, borderRadius: 6, padding: "3px 10px", fontSize: 11, color: C.t3 }}>⌘K</div>
        <div style={{ width: 28, height: 28, borderRadius: 14, background: C.cyanDk, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 700, color: C.t1 }}>MR</div>
      </div>
    </div>
    {/* Body */}
    <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
      <div style={{ width: 222, background: C.sidebar, borderRight: `1px solid ${C.card2}`, paddingTop: 8, flexShrink: 0 }}>
        {NAV.map(n => (
          <div key={n} style={{ margin: "1px 8px", padding: "8px 12px", borderRadius: 6, background: n === active ? C.cyanDk : "transparent", color: n === active ? C.t1 : C.t2, fontSize: 13, fontWeight: n === active ? 700 : 400 }}>{n}</div>
        ))}
      </div>
      <div style={{ flex: 1, overflow: "hidden", padding: 14 }}>{children}</div>
    </div>
  </AbsoluteFill>
);

// ── SCENE 01 — Intro ──────────────────────────────────────────────────────────
const Scene01Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const logoS  = spring({ frame, fps, config: { damping: 12, stiffness: 100 } });
  const textO  = fi(frame, 14, 24, 12);
  const subO   = fi(frame, 24, 36, 12);
  const chipsO = fi(frame, 36, 48, 12);
  const chips  = ["✂ Saloni","🏋 Palestre","🏥 Cliniche","🔧 Officine","🦷 Odontoiatria","💆 Estetica"];

  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 35%,#0c1a3a 0%,#020617 70%)", fontFamily: "'Inter','Helvetica',sans-serif", alignItems: "center", justifyContent: "center", flexDirection: "column" }}>
      {/* Grid background */}
      <div style={{ position: "absolute", inset: 0, backgroundImage: `linear-gradient(${C.card2}18 1px,transparent 1px),linear-gradient(90deg,${C.card2}18 1px,transparent 1px)`, backgroundSize: "60px 60px" }} />
      {/* Glow */}
      <div style={{ position: "absolute", width: 360, height: 360, borderRadius: 180, background: `radial-gradient(circle,${C.cyan}14 0%,transparent 70%)`, top: "5%", left: "50%", transform: "translateX(-50%)" }} />

      <div style={{ transform: `scale(${logoS})`, zIndex: 1, marginBottom: 14 }}>
        <div style={{ filter: "drop-shadow(0 0 24px #22d3ee99)" }}><FluxionLogo size={100} /></div>
      </div>
      <div style={{ opacity: textO, zIndex: 1, textAlign: "center" }}>
        <div style={{ fontSize: 76, fontWeight: 900, letterSpacing: -3, background: `linear-gradient(90deg,${C.cyan},${C.teal})`, WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", lineHeight: 1 }}>FLUXION</div>
      </div>
      <div style={{ opacity: subO, marginTop: 14, zIndex: 1 }}>
        <p style={{ color: C.t2, fontSize: 22, margin: 0, textAlign: "center" }}>Il gestionale desktop che lavora per te</p>
      </div>
      <div style={{ opacity: chipsO, display: "flex", gap: 10, marginTop: 36, flexWrap: "wrap", justifyContent: "center", zIndex: 1, maxWidth: 720 }}>
        {chips.map(c => <div key={c} style={{ background: C.card, border: `1px solid ${C.card2}`, borderRadius: 20, padding: "6px 16px", fontSize: 13, fontWeight: 600, color: C.t1 }}>{c}</div>)}
      </div>
    </AbsoluteFill>
  );
};

// ── SCENE 02 — Setup ─────────────────────────────────────────────────────────
const Scene02Setup: React.FC = () => {
  const frame = useCurrentFrame();
  const verticals = [
    { label: "✂  Salone / Barbiere",  desc: "Parrucchieri, barbieri, saloni di bellezza", selected: true },
    { label: "🏋  Palestra / Fitness", desc: "Centri fitness, crossfit, personal trainer",  selected: false },
    { label: "🏥  Studio Medico",      desc: "Fisioterapia, odontoiatria, estetica",         selected: false },
    { label: "🔧  Officina",           desc: "Auto, moto, cicli, elettronica",               selected: false },
  ];
  const dlgO = fi(frame, 4, 14, 12);

  return (
    <AbsoluteFill style={{ background: "#05101f", fontFamily: "'Inter','Helvetica',sans-serif", alignItems: "center", justifyContent: "center" }}>
      <div style={{ opacity: dlgO, width: 660, background: C.card, border: `1px solid ${C.card2}`, borderRadius: 14 }}>
        {/* Modal header */}
        <div style={{ background: "#141e38", borderRadius: "14px 14px 0 0", padding: "16px 22px", borderBottom: `1px solid ${C.card2}` }}>
          <div style={{ color: C.t1, fontWeight: 700, fontSize: 17 }}>Configurazione iniziale</div>
          {/* Steps */}
          <div style={{ display: "flex", gap: 0, marginTop: 10 }}>
            {["Benvenuto","Verticale","Attività","Orari","Fine"].map((s,i) => (
              <div key={s} style={{ flex: 1, textAlign: "center", fontSize: 11, fontWeight: i <= 1 ? 700 : 400, color: i <= 1 ? C.cyan : C.t3 }}>{s}</div>
            ))}
          </div>
          {/* Progress */}
          <div style={{ height: 4, background: C.card2, borderRadius: 2, marginTop: 6 }}>
            <div style={{ width: "40%", height: 4, background: C.cyan, borderRadius: 2 }} />
          </div>
        </div>
        {/* Content */}
        <div style={{ padding: "20px 22px" }}>
          <div style={{ color: C.t1, fontWeight: 700, fontSize: 15, marginBottom: 4 }}>Scegli il settore della tua attività</div>
          <div style={{ color: C.t2, fontSize: 12, marginBottom: 16 }}>Puoi cambiarlo in qualsiasi momento dalle Impostazioni</div>
          {verticals.map((v, i) => (
            <FadeIn key={v.label} from={6 + i * 5}>
              <div style={{ display: "flex", alignItems: "center", padding: "12px 14px", borderRadius: 8, marginBottom: 8, background: v.selected ? C.cyanDk : C.sidebar, border: `2px solid ${v.selected ? C.cyan : C.card2}` }}>
                <div style={{ flex: 1 }}>
                  <div style={{ color: v.selected ? C.t1 : C.t2, fontSize: 14, fontWeight: v.selected ? 700 : 400 }}>{v.label}</div>
                  <div style={{ color: C.t2, fontSize: 11, marginTop: 2 }}>{v.desc}</div>
                </div>
                {v.selected && <div style={{ color: C.cyan, fontSize: 18, fontWeight: 700 }}>✓</div>}
              </div>
            </FadeIn>
          ))}
          <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 16 }}>
            <div style={{ background: C.cyanDk, color: C.t1, borderRadius: 8, padding: "10px 22px", fontSize: 14, fontWeight: 700 }}>Continua →</div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ── SCENE 03 — Dashboard ─────────────────────────────────────────────────────
const kpis = [
  { label:"Appuntamenti oggi",  value:"12",     color:C.cyan,   sub:"↑ 3 rispetto a ieri" },
  { label:"Clienti totali",     value:"847",    color:C.green,  sub:"↑ 23 questo mese" },
  { label:"Fatturato mese",     value:"€4.280", color:C.violet, sub:"↑ 12% vs scorso" },
  { label:"Servizio top",       value:"Taglio", color:C.yellow, sub:"38% appuntamenti" },
];
const appts = [
  { t:"09:00", n:"Marco Rossi",    s:"Taglio Capelli", c:C.green  },
  { t:"10:30", n:"Giulia Ferrari", s:"Colore",         c:C.violet },
  { t:"11:00", n:"Anna Bianchi",   s:"Piega",          c:C.cyan   },
  { t:"14:00", n:"Luca Verdi",     s:"Rasatura",       c:C.yellow },
  { t:"15:30", n:"Sofia Marino",   s:"Trattamento",    c:C.rose   },
  { t:"16:00", n:"Carlo E.",       s:"Taglio + Barba", c:C.green  },
];

const Scene03Dashboard: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AppLayout active="Dashboard">
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10, marginBottom: 12 }}>
        {kpis.map((k, i) => (
          <FadeIn key={k.label} from={4 + i * 4}>
            <Card style={{ borderLeft: `3px solid ${k.color}`, padding: "12px 14px" }}>
              <div style={{ color: C.t2, fontSize: 10, marginBottom: 4 }}>{k.label}</div>
              <div style={{ color: k.color, fontSize: 24, fontWeight: 800 }}>{k.value}</div>
              <div style={{ color: C.t2, fontSize: 10, marginTop: 4 }}>{k.sub}</div>
            </Card>
          </FadeIn>
        ))}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
        <FadeIn from={20}>
          <Card style={{ padding: 0 }}>
            <div style={{ padding: "10px 14px", borderBottom: `1px solid ${C.card2}`, color: C.t1, fontWeight: 700, fontSize: 13 }}>Prossimi appuntamenti</div>
            {appts.map((a, i) => (
              <div key={a.t} style={{ display:"flex", alignItems:"center", padding:"8px 14px", background: i%2===0?"transparent":"#16243a", borderBottom:`1px solid ${C.card2}22` }}>
                <div style={{ width:3, height:24, background:a.c, borderRadius:2, marginRight:10, flexShrink:0 }} />
                <span style={{ color:C.t2, fontSize:10, fontWeight:700, width:42 }}>{a.t}</span>
                <div style={{ flex:1 }}>
                  <div style={{ color:C.t1, fontSize:12, fontWeight:600 }}>{a.n}</div>
                  <div style={{ color:C.t2, fontSize:10 }}>{a.s}</div>
                </div>
              </div>
            ))}
          </Card>
        </FadeIn>
        <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
          {[
            { title:"Clienti VIP", val:"23", color:C.yellow, sub:"↑ 5 nuovi questo mese" },
            { title:"Da incassare", val:"€ 1.240", color:C.yellow, sub:"4 fatture in attesa" },
          ].map((s, i) => (
            <FadeIn key={s.title} from={24 + i * 6}>
              <Card>
                <div style={{ color:C.t1, fontWeight:700, fontSize:13, marginBottom:6 }}>{s.title}</div>
                <div style={{ fontSize:26, fontWeight:800, color:s.color }}>{s.val}</div>
                <div style={{ color:C.t2, fontSize:10, marginTop:2 }}>{s.sub}</div>
              </Card>
            </FadeIn>
          ))}
          <FadeIn from={34}>
            <Card>
              <div style={{ color:C.t1, fontWeight:700, fontSize:13, marginBottom:10 }}>Servizi richiesti</div>
              {[["Taglio",38,C.green],["Colore",24,C.violet],["Piega",18,C.cyan]].map(([s,v,c]) => (
                <div key={s as string} style={{ marginBottom:8 }}>
                  <div style={{ display:"flex", justifyContent:"space-between", fontSize:10, color:C.t2, marginBottom:2 }}>
                    <span>{s}</span><span style={{ color:c as string }}>{v}%</span>
                  </div>
                  <div style={{ background:C.card2, borderRadius:4, height:6 }}>
                    <div style={{ width:`${v}%`, background:c as string, borderRadius:4, height:6 }} />
                  </div>
                </div>
              ))}
            </Card>
          </FadeIn>
        </div>
      </div>
    </AppLayout>
  );
};

// ── SCENE 04 — Clienti ────────────────────────────────────────────────────────
const clienti = [
  { n:"Marco Rossi",      tel:"+39 334 123 4567", data:"14 Feb 2026", fid:"★★★★☆", vip:true,  col:C.yellow },
  { n:"Giulia Ferrari",   tel:"+39 348 987 6543", data:"20 Feb 2026", fid:"★★★☆☆", vip:false, col:null },
  { n:"Anna Bianchi",     tel:"+39 320 111 2222", data:"18 Feb 2026", fid:"★★★★★", vip:true,  col:C.green },
  { n:"Luca Verdi",       tel:"+39 333 444 5555", data:" 5 Feb 2026", fid:"★★☆☆☆", vip:false, col:null },
  { n:"Sofia Marino",     tel:"+39 389 777 8888", data:"22 Feb 2026", fid:"★★★★☆", vip:true,  col:C.green },
  { n:"Carlo Esposito",   tel:"+39 366 999 0000", data:"10 Feb 2026", fid:"★★★☆☆", vip:false, col:null },
  { n:"Federica Conti",   tel:"+39 347 222 3333", data:" 8 Feb 2026", fid:"★★★★☆", vip:true,  col:C.yellow },
];

const Scene04Clienti: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AppLayout active="Clienti">
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:12 }}>
        <div style={{ color:C.t1, fontWeight:700, fontSize:17 }}>Gestione Clienti</div>
        <div style={{ background:C.cyanDk, color:C.t1, borderRadius:6, padding:"8px 18px", fontSize:12, fontWeight:700 }}>+ Nuovo Cliente</div>
      </div>
      <FadeIn from={4}>
        <div style={{ background:C.card, border:`1px solid ${C.card2}`, borderRadius:6, padding:"8px 12px", marginBottom:12, color:C.t3, fontSize:12 }}>🔍  Cerca per nome, telefono...</div>
      </FadeIn>
      <FadeIn from={8}>
        <div style={{ background:C.card2, borderRadius:"6px 6px 0 0", display:"grid", gridTemplateColumns:"2fr 1.5fr 1.5fr 1fr 0.5fr 0.8fr", padding:"8px 12px" }}>
          {["Nome Cliente","Telefono","Ultima visita","Fedeltà","VIP","Azioni"].map(h => (
            <div key={h} style={{ color:C.t2, fontSize:10, fontWeight:700 }}>{h}</div>
          ))}
        </div>
        {clienti.map((c, i) => (
          <div key={c.n} style={{ display:"grid", gridTemplateColumns:"2fr 1.5fr 1.5fr 1fr 0.5fr 0.8fr", padding:"8px 12px", background:i%2===0?C.card:"#16243a", borderBottom:`1px solid ${C.card2}33`, alignItems:"center" }}>
            <div style={{ color:C.t1, fontSize:12, fontWeight:600 }}>{c.n}</div>
            <div style={{ color:C.t2, fontSize:11 }}>{c.tel}</div>
            <div style={{ color:C.t2, fontSize:11 }}>{c.data}</div>
            <div style={{ color:C.yellow, fontSize:10 }}>{c.fid}</div>
            <div>{c.vip && <span style={{ background:c.col!, color:C.bg, borderRadius:4, padding:"1px 6px", fontSize:10, fontWeight:700 }}>VIP</span>}</div>
            <div style={{ display:"flex", gap:4 }}>
              {["✎","✕"].map((ic,j) => <div key={ic} style={{ background:C.card2, borderRadius:4, padding:"2px 6px", fontSize:11, color:j===1?C.red:C.t2 }}>{ic}</div>)}
            </div>
          </div>
        ))}
      </FadeIn>
    </AppLayout>
  );
};

// ── SCENE 05 — Calendario ─────────────────────────────────────────────────────
const Scene05Calendario: React.FC = () => {
  const DAYS = ["Lun","Mar","Mer","Gio","Ven","Sab","Dom"];
  const apptMap: Record<number,{n:string,c:string}[]> = {
    3: [{n:"Marco R.",c:C.green},{n:"Giulia F.",c:C.violet}],
    5: [{n:"Anna B.",c:C.cyan}],
    10:[{n:"Luca V.",c:C.yellow},{n:"Sofia M.",c:C.rose},{n:"+1",c:C.t3}],
    14:[{n:"Federica C.",c:C.yellow}],
    17:[{n:"Marco R.",c:C.green},{n:"Giulia F.",c:C.violet}],
    19:[{n:"Anna B.",c:C.cyan}],
    24:[{n:"Luca V.",c:C.yellow}],
    26:[{n:"Sara L.",c:C.cyan},{n:"Carlo E.",c:C.green}],
  };
  const START_DOW = 6; // Feb 1 2026 = Sunday

  return (
    <AppLayout active="Calendario">
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:10 }}>
        <div style={{ color:C.t1, fontWeight:700, fontSize:17 }}>Calendario — Febbraio 2026</div>
        <div style={{ display:"flex", gap:6 }}>
          {["‹","Oggi","›"].map(b => (
            <div key={b} style={{ background:b==="Oggi"?C.card:C.card2, border:b==="Oggi"?`1px solid ${C.cyan}`:`1px solid ${C.card2}`, color:b==="Oggi"?C.cyan:C.t1, borderRadius:6, padding:"4px 12px", fontSize:12, fontWeight:700 }}>{b}</div>
          ))}
        </div>
      </div>
      <div style={{ display:"grid", gridTemplateColumns:"repeat(7,1fr)", gap:1, flex:1 }}>
        {DAYS.map(d => <div key={d} style={{ background:C.card2, textAlign:"center", padding:"6px 0", fontSize:10, fontWeight:700, color:C.t2 }}>{d}</div>)}
        {Array.from({length:42},(_,idx) => {
          const day = idx - START_DOW + 1;
          const valid = day >= 1 && day <= 28;
          const today = day === 26;
          const apps = apptMap[day] || [];
          return (
            <div key={idx} style={{ background:today?"#0c2040":valid?C.card:C.bg, minHeight:82, padding:4, borderRight:`1px solid ${C.card2}22`, borderBottom:`1px solid ${C.card2}22` }}>
              {valid && <div style={{ fontSize:11, fontWeight:today?700:400, color:today?C.cyan:C.t2, marginBottom:2 }}>{day}</div>}
              {apps.map((a,i) => (
                <div key={i} style={{ background:a.c, borderRadius:3, padding:"1px 4px", fontSize:9, color:C.bg, fontWeight:700, marginBottom:2, overflow:"hidden", whiteSpace:"nowrap", textOverflow:"ellipsis" }}>{a.n}</div>
              ))}
            </div>
          );
        })}
      </div>
    </AppLayout>
  );
};

// ── SCENE 06 — Sara Voice Agent ───────────────────────────────────────────────
const msgs = [
  { role:"Sara",    text:"Buongiorno! Sono Sara di Valentina Style. Come posso aiutarla?" },
  { role:"Cliente", text:"Ciao, sono Marco Rossi. Vorrei prenotare un taglio per giovedì." },
  { role:"Sara",    text:"Ciao Marco! Giovedì 27 febbraio ho disponibile alle 10:00, 14:30 e 16:00. Quale preferisci?" },
  { role:"Cliente", text:"Perfetto, alle 10:00." },
  { role:"Sara",    text:"Ho prenotato per giovedì 27 alle 10:00 con Anna. Ti mando la conferma su WhatsApp. Buona giornata!" },
];

const Scene06Sara: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AppLayout active="Voice Agent">
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:10 }}>
        <div style={{ color:C.t1, fontWeight:700, fontSize:17 }}>Sara — Voice Agent AI</div>
        <div style={{ background:C.red, color:C.t1, borderRadius:6, padding:"4px 12px", fontSize:11, fontWeight:700 }}>● Chiamata in corso</div>
      </div>
      <Card style={{ flex:1, padding:0, overflow:"hidden" }}>
        {msgs.map((m, i) => {
          const isSara = m.role === "Sara";
          return (
            <FadeIn key={i} from={6 + i * 8}>
              <div style={{ display:"flex", padding:"10px 14px", background:i%2===0?"transparent":"#16243a", borderBottom:`1px solid ${C.card2}22`, gap:10, alignItems:"flex-start" }}>
                <div style={{ width:28, height:28, borderRadius:14, background:isSara?C.cyanDk:C.card2, display:"flex", alignItems:"center", justifyContent:"center", fontSize:10, fontWeight:700, color:C.t1, flexShrink:0 }}>
                  {isSara?"S":"C"}
                </div>
                <div style={{ flex:1 }}>
                  <div style={{ color:isSara?C.cyan:C.t2, fontSize:10, fontWeight:700, marginBottom:3 }}>{m.role}</div>
                  <div style={{ color:C.t1, fontSize:12, lineHeight:1.4 }}>{m.text}</div>
                </div>
              </div>
            </FadeIn>
          );
        })}
        <FadeIn from={50}>
          <div style={{ padding:"8px 14px", background:"#0a1a10", borderTop:`1px solid ${C.green}33` }}>
            <span style={{ color:C.green, fontSize:11, fontWeight:700 }}>✓ Prenotazione confermata • WhatsApp inviato automaticamente</span>
          </div>
        </FadeIn>
      </Card>
      {/* Mic button */}
      <FadeIn from={4}>
        <div style={{ display:"flex", justifyContent:"center", alignItems:"center", gap:16, marginTop:10 }}>
          <div style={{ width:48, height:48, borderRadius:24, background:C.red, display:"flex", alignItems:"center", justifyContent:"center", fontSize:20, boxShadow:`0 0 0 8px ${C.red}22` }}>🎙</div>
          <div style={{ flex:1, background:C.card, border:`1px solid ${C.card2}`, borderRadius:8, padding:"10px 14px", color:C.t3, fontSize:12 }}>Oppure scrivi un messaggio...</div>
        </div>
      </FadeIn>
    </AppLayout>
  );
};

// ── SCENE 07 — Verticali ──────────────────────────────────────────────────────
const Scene07Verticali: React.FC = () => {
  const frame = useCurrentFrame();
  // Odontogramma simplified
  const teeth = [
    {n:18,c:C.green},{n:17,c:C.green},{n:16,c:C.blue},{n:15,c:C.green},{n:14,c:C.cyan},{n:13,c:C.green},{n:12,c:C.violet},{n:11,c:C.blue},
    {n:21,c:C.green},{n:22,c:C.blue},{n:23,c:C.green},{n:24,c:C.red},{n:25,c:C.green},{n:26,c:C.green},{n:27,c:C.yellow},{n:28,c:C.green},
  ];
  return (
    <AppLayout active="Clienti">
      <div style={{ color:C.t1, fontWeight:700, fontSize:17, marginBottom:10 }}>Schede Verticali Specializzate</div>
      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:10 }}>
        {/* Odontogramma */}
        <FadeIn from={4}>
          <Card style={{ padding:12 }}>
            <div style={{ color:C.cyan, fontWeight:700, fontSize:13, marginBottom:8 }}>🦷 Odontoiatrica</div>
            <div style={{ fontSize:10, color:C.t2, marginBottom:8 }}>Odontogramma FDI interattivo</div>
            <div style={{ display:"flex", flexWrap:"wrap", gap:3 }}>
              {teeth.map(t => (
                <div key={t.n} style={{ width:26, height:22, background:t.c, borderRadius:4, display:"flex", alignItems:"center", justifyContent:"center", fontSize:9, fontWeight:700, color:C.bg }}>{t.n}</div>
              ))}
            </div>
            <div style={{ marginTop:8, display:"flex", gap:4, flexWrap:"wrap" }}>
              {[["Sano",C.green],["Otturato",C.blue],["Carie",C.red],["Corona",C.violet]].map(([l,c]) => (
                <div key={l as string} style={{ display:"flex", alignItems:"center", gap:3 }}>
                  <div style={{ width:8, height:8, background:c as string, borderRadius:2 }} />
                  <span style={{ fontSize:9, color:C.t2 }}>{l}</span>
                </div>
              ))}
            </div>
          </Card>
        </FadeIn>
        {/* Fisioterapia */}
        <FadeIn from={10}>
          <Card style={{ padding:12 }}>
            <div style={{ color:C.green, fontWeight:700, fontSize:13, marginBottom:8 }}>🏥 Fisioterapia</div>
            <div style={{ fontSize:10, color:C.t2, marginBottom:8 }}>Scale valutazione clinica</div>
            {[["VAS Dolore",7,10,C.red],["Oswestry",38,100,C.yellow],["SF-36",62,100,C.green]].map(([s,v,m,c]) => (
              <div key={s as string} style={{ marginBottom:8 }}>
                <div style={{ display:"flex", justifyContent:"space-between", fontSize:10, color:C.t2, marginBottom:2 }}>
                  <span>{s}</span><span style={{ color:c as string }}>{v}/{m}</span>
                </div>
                <div style={{ background:C.card2, borderRadius:4, height:6 }}>
                  <div style={{ width:`${(v as number)/(m as number)*100}%`, background:c as string, borderRadius:4, height:6 }} />
                </div>
              </div>
            ))}
            <div style={{ display:"flex", gap:4, flexWrap:"wrap", marginTop:4 }}>
              {["Lombare","Cervicale","Spalle"].map(z => (
                <div key={z} style={{ background:C.cyanDk, borderRadius:12, padding:"3px 10px", fontSize:10, fontWeight:700, color:C.t1 }}>{z}</div>
              ))}
            </div>
          </Card>
        </FadeIn>
        {/* Estetica */}
        <FadeIn from={16}>
          <Card style={{ padding:12 }}>
            <div style={{ color:C.violet, fontWeight:700, fontSize:13, marginBottom:8 }}>💆 Estetica</div>
            <div style={{ fontSize:10, color:C.t2, marginBottom:8 }}>Profilo pelle e obiettivi</div>
            <div style={{ color:C.t2, fontSize:10, marginBottom:4 }}>Tipo pelle</div>
            <div style={{ display:"flex", gap:4, marginBottom:8 }}>
              {["Secca","Mista","Grassa","Sensibile"].map((t,i) => (
                <div key={t} style={{ background:i===1?C.violet:C.card2, borderRadius:4, padding:"3px 8px", fontSize:10, color:i===1?C.t1:C.t2 }}>{t}</div>
              ))}
            </div>
            <div style={{ color:C.t2, fontSize:10, marginBottom:4 }}>Obiettivi</div>
            {["Dimagrimento","Tonificazione","Rilassamento","Anticellulite"].map((o,i) => (
              <div key={o} style={{ display:"flex", alignItems:"center", gap:6, marginBottom:4 }}>
                <div style={{ width:14, height:14, borderRadius:3, background:i<2?C.violet:C.card2, border:`1px solid ${C.card2}` }} />
                <span style={{ fontSize:10, color:C.t2 }}>{o}</span>
              </div>
            ))}
          </Card>
        </FadeIn>
      </div>
      {/* Bottom row — more verticals */}
      <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:10, marginTop:10 }}>
        {[
          { e:"✂", t:"Salone",   c:C.cyan,  f:["Listino prezzi","Storico colorazioni","Preferenze cliente"] },
          { e:"🏋", t:"Palestra", c:C.green, f:["Schede allenamento","Abbonamenti","Misurazioni"] },
          { e:"🔧", t:"Officina", c:C.yellow,f:["Storico interventi","Ricambi","Veicoli cliente"] },
        ].map((v, i) => (
          <FadeIn key={v.t} from={22 + i * 5}>
            <Card style={{ padding:10 }}>
              <div style={{ color:v.c, fontWeight:700, fontSize:12, marginBottom:6 }}>{v.e} {v.t}</div>
              {v.f.map(f => <div key={f} style={{ color:C.t2, fontSize:10, marginBottom:3 }}>• {f}</div>)}
            </Card>
          </FadeIn>
        ))}
      </div>
    </AppLayout>
  );
};

// ── SCENE 08 — Fatture ────────────────────────────────────────────────────────
const fatture = [
  { num:"0042", data:"14 Feb", cli:"Marco Rossi",    imp:"€ 25,00", stato:"Pagata", c:C.green  },
  { num:"0041", data:"13 Feb", cli:"Giulia Ferrari",  imp:"€ 70,00", stato:"Pagata", c:C.green  },
  { num:"0040", data:"12 Feb", cli:"Anna Bianchi",    imp:"€ 20,00", stato:"Emessa", c:C.cyan   },
  { num:"0039", data:"10 Feb", cli:"Luca Verdi",      imp:"€ 35,00", stato:"Emessa", c:C.cyan   },
  { num:"0038", data:" 8 Feb", cli:"Sofia Marino",    imp:"€ 55,00", stato:"Bozza",  c:C.yellow },
  { num:"0037", data:" 5 Feb", cli:"Carlo Esposito",  imp:"€ 90,00", stato:"Pagata", c:C.green  },
];

const Scene08Fatture: React.FC = () => {
  return (
    <AppLayout active="Fatture">
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:10 }}>
        <div style={{ color:C.t1, fontWeight:700, fontSize:17 }}>Fatturazione Elettronica</div>
        <div style={{ background:C.cyanDk, color:C.t1, borderRadius:6, padding:"8px 18px", fontSize:12, fontWeight:700 }}>+ Nuova Fattura</div>
      </div>
      <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:8, marginBottom:12 }}>
        {[["Tot. mese","€ 4.280",C.cyan],["Bozze","3",C.yellow],["Emesse","12",C.green],["Pagate","9",C.green]].map(([l,v,c]) => (
          <Card key={l as string} style={{ borderLeft:`3px solid ${c as string}`, padding:"10px 14px" }}>
            <div style={{ color:C.t2, fontSize:10 }}>{l}</div>
            <div style={{ color:c as string, fontSize:22, fontWeight:800 }}>{v}</div>
          </Card>
        ))}
      </div>
      <FadeIn from={6}>
        <div style={{ background:C.card2, display:"grid", gridTemplateColumns:"0.5fr 1fr 2fr 1fr 0.8fr 0.8fr", padding:"8px 12px", borderRadius:"6px 6px 0 0" }}>
          {["N°","Data","Cliente","Importo","Stato","Azioni"].map(h => <div key={h} style={{ color:C.t2, fontSize:10, fontWeight:700 }}>{h}</div>)}
        </div>
        {fatture.map((f, i) => (
          <div key={f.num} style={{ display:"grid", gridTemplateColumns:"0.5fr 1fr 2fr 1fr 0.8fr 0.8fr", padding:"8px 12px", background:i%2===0?C.card:"#16243a", borderBottom:`1px solid ${C.card2}33`, alignItems:"center" }}>
            <div style={{ color:C.t2, fontSize:11 }}>{f.num}</div>
            <div style={{ color:C.t2, fontSize:11 }}>{f.data}</div>
            <div style={{ color:C.t1, fontSize:12, fontWeight:600 }}>{f.cli}</div>
            <div style={{ color:C.t1, fontSize:12, fontWeight:700 }}>{f.imp}</div>
            <div><span style={{ background:f.stato==="Pagata"?f.c:C.card2, color:f.stato==="Pagata"?C.bg:C.t1, borderRadius:4, padding:"2px 8px", fontSize:10, fontWeight:700 }}>{f.stato}</span></div>
            <div style={{ display:"flex", gap:4 }}>
              {["⬇","✕"].map((ic,j) => <div key={ic} style={{ background:C.card2, borderRadius:4, padding:"2px 6px", fontSize:11, color:j===1?C.red:C.t2 }}>{ic}</div>)}
            </div>
          </div>
        ))}
      </FadeIn>
      <FadeIn from={12}>
        <div style={{ marginTop:10, display:"flex", alignItems:"center", gap:10 }}>
          <div style={{ background:C.card, border:`1px solid ${C.cyan}`, borderRadius:6, padding:"6px 14px", color:C.cyan, fontSize:11, fontWeight:700 }}>📄 Formato XML — SDI compatibile</div>
          <div style={{ color:C.t2, fontSize:11 }}>Download diretto per invio al Sistema di Interscambio</div>
        </div>
      </FadeIn>
    </AppLayout>
  );
};

// ── SCENE 09 — Outro ──────────────────────────────────────────────────────────
const Scene09Outro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const logoS  = spring({ frame, fps, config: { damping: 12, stiffness: 100 } });
  const t1O = fi(frame, 14, 24, 12);
  const t2O = fi(frame, 24, 36, 12);
  const cardsO = fi(frame, 34, 50, 14);
  const ctaO = fi(frame, 50, 64, 14);

  const pillars = [
    { icon:"📱", t:"Sara Voice AI",    d:"Prenotazioni 24/7\nautomatiche" },
    { icon:"🎯", t:"Marketing Zero",   d:"Loyalty, pacchetti\ne promozioni gratis" },
    { icon:"⚙️", t:"Gestione Totale",  d:"Calendario, schede\ne fatturazione" },
  ];

  return (
    <AbsoluteFill style={{ background:"radial-gradient(ellipse at 50% 35%,#0c1a3a 0%,#020617 70%)", fontFamily:"'Inter','Helvetica',sans-serif", alignItems:"center", justifyContent:"center", flexDirection:"column" }}>
      <div style={{ position:"absolute", inset:0, backgroundImage:`linear-gradient(${C.card2}14 1px,transparent 1px),linear-gradient(90deg,${C.card2}14 1px,transparent 1px)`, backgroundSize:"60px 60px" }} />

      <div style={{ transform:`scale(${logoS})`, zIndex:1, marginBottom:12 }}>
        <div style={{ filter:"drop-shadow(0 0 20px #22d3ee88)" }}><FluxionLogo size={72} /></div>
      </div>
      <div style={{ opacity:t1O, zIndex:1 }}>
        <div style={{ fontSize:60, fontWeight:900, letterSpacing:-2, background:`linear-gradient(90deg,${C.cyan},${C.teal})`, WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent", lineHeight:1, textAlign:"center" }}>FLUXION</div>
      </div>
      <div style={{ opacity:t2O, marginTop:8, zIndex:1 }}>
        <p style={{ color:C.t2, fontSize:18, margin:0, textAlign:"center" }}>Il gestionale che lavora per te</p>
      </div>
      <div style={{ opacity:cardsO, display:"flex", gap:14, marginTop:28, zIndex:1 }}>
        {pillars.map(p => (
          <div key={p.t} style={{ background:C.card, border:`1px solid ${C.card2}`, borderRadius:10, padding:"16px 20px", width:190, textAlign:"center" }}>
            <div style={{ fontSize:24, marginBottom:6 }}>{p.icon}</div>
            <div style={{ color:C.cyan, fontWeight:700, fontSize:13, marginBottom:4 }}>{p.t}</div>
            {p.d.split("\n").map(l => <div key={l} style={{ color:C.t2, fontSize:11 }}>{l}</div>)}
          </div>
        ))}
      </div>
      <div style={{ opacity:ctaO, marginTop:24, zIndex:1, display:"flex", flexDirection:"column", alignItems:"center", gap:10 }}>
        <div style={{ background:C.cyanDk, color:C.t1, borderRadius:24, padding:"12px 32px", fontSize:16, fontWeight:800 }}>Licenza Lifetime da soli €197</div>
        <div style={{ color:C.t3, fontSize:12 }}>Nessun abbonamento • Nessuna commissione • Tuo per sempre</div>
        <div style={{ color:C.t3, fontSize:11 }}>Base €197 &nbsp;•&nbsp; Pro €497 &nbsp;•&nbsp; Enterprise €897</div>
      </div>
    </AbsoluteFill>
  );
};

// ── Scene-audio wrapper ────────────────────────────────────────────────────────
const WithAudio: React.FC<{ id: string; children: React.ReactNode }> = ({ id, children }) => (
  <>
    <Audio src={staticFile(`voiceover/${id}.mp3`)} />
    {children}
  </>
);

// ── Main composition ───────────────────────────────────────────────────────────
// Scene durations in frames (30fps) — matches audio + 1s padding
const SCENE_FRAMES = [
  10.2, 11.8, 11.1, 11.5, 12.3, 15.6, 14.2, 10.8, 14.9
].map(s => Math.ceil(s * 30));

const TRANSITION = 12; // 0.4s fade

export const FluxionTutorial: React.FC = () => {
  const scenes: Array<{ id: string; component: React.FC; frames: number }> = [
    { id:"01-intro",      component:Scene01Intro,     frames:SCENE_FRAMES[0] },
    { id:"02-setup",      component:Scene02Setup,     frames:SCENE_FRAMES[1] },
    { id:"03-dashboard",  component:Scene03Dashboard, frames:SCENE_FRAMES[2] },
    { id:"04-clienti",    component:Scene04Clienti,   frames:SCENE_FRAMES[3] },
    { id:"05-calendario", component:Scene05Calendario,frames:SCENE_FRAMES[4] },
    { id:"06-sara",       component:Scene06Sara,      frames:SCENE_FRAMES[5] },
    { id:"07-verticali",  component:Scene07Verticali, frames:SCENE_FRAMES[6] },
    { id:"08-fatture",    component:Scene08Fatture,   frames:SCENE_FRAMES[7] },
    { id:"09-outro",      component:Scene09Outro,     frames:SCENE_FRAMES[8] },
  ];

  return (
    <AbsoluteFill>
      <TransitionSeries>
        {scenes.map((s, i) => (
          <React.Fragment key={s.id}>
            <TransitionSeries.Sequence durationInFrames={s.frames}>
              <WithAudio id={s.id}>
                <s.component />
              </WithAudio>
            </TransitionSeries.Sequence>
            {i < scenes.length - 1 && (
              <TransitionSeries.Transition
                presentation={fade()}
                timing={linearTiming({ durationInFrames: TRANSITION })}
              />
            )}
          </React.Fragment>
        ))}
      </TransitionSeries>
    </AbsoluteFill>
  );
};
