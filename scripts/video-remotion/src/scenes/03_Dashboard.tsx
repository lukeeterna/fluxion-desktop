import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { C, Card, FadeIn, Layout, Callout } from "../components/Layout";

const kpis = [
  { label: "Appuntamenti oggi",  value: "12",     color: C.cyan,   sub: "↑ 3 rispetto a ieri" },
  { label: "Clienti totali",     value: "847",    color: C.green,  sub: "↑ 23 questo mese" },
  { label: "Fatturato mese",     value: "€4.280", color: C.violet, sub: "↑ 12% vs mese scorso" },
  { label: "Servizio top",       value: "Taglio", color: C.yellow, sub: "38% degli appuntamenti" },
];

const appts = [
  { time: "09:00", name: "Marco Rossi",    srv: "Taglio Capelli", color: C.green  },
  { time: "10:30", name: "Giulia Ferrari", srv: "Colore",         color: C.violet },
  { time: "11:00", name: "Anna Bianchi",   srv: "Piega",          color: C.cyan   },
  { time: "14:00", name: "Luca Verdi",     srv: "Rasatura",       color: C.yellow },
  { time: "15:30", name: "Sofia Marino",   srv: "Trattamento",    color: C.rose   },
  { time: "16:00", name: "Carlo E.",       srv: "Taglio + Barba", color: C.green  },
];

export const SceneDashboard: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <Layout active="/" fadeIn>
      <FadeIn from={4}>
        {/* KPI row */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10, marginBottom: 12 }}>
          {kpis.map((k, i) => (
            <FadeIn key={k.label} from={6 + i * 4}>
              <Card style={{ borderLeft: `3px solid ${k.color}`, padding: "12px 14px" }}>
                <div style={{ color: C.t2, fontSize: 11, marginBottom: 4 }}>{k.label}</div>
                <div style={{ color: k.color, fontSize: 26, fontWeight: 800, lineHeight: 1.1 }}>{k.value}</div>
                <div style={{ color: C.t2, fontSize: 10, marginTop: 4 }}>{k.sub}</div>
              </Card>
            </FadeIn>
          ))}
        </div>

        {/* Bottom row */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, height: 390 }}>
          {/* Appuntamenti */}
          <FadeIn from={20}>
            <Card style={{ height: "100%", padding: 0, overflow: "hidden" }}>
              <div style={{ padding: "12px 14px", borderBottom: `1px solid ${C.card2}` }}>
                <span style={{ color: C.t1, fontWeight: 700, fontSize: 14 }}>Prossimi appuntamenti</span>
              </div>
              {appts.map((a, i) => (
                <div key={a.time} style={{
                  display: "flex", alignItems: "center", padding: "9px 14px",
                  background: i % 2 === 0 ? "transparent" : "#16243a",
                  borderBottom: `1px solid ${C.card2}22`,
                }}>
                  <div style={{ width: 3, height: 28, background: a.color, borderRadius: 2, marginRight: 10, flexShrink: 0 }} />
                  <span style={{ color: C.t2, fontSize: 11, fontWeight: 700, width: 46 }}>{a.time}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ color: C.t1, fontSize: 13, fontWeight: 600 }}>{a.name}</div>
                    <div style={{ color: C.t2, fontSize: 11 }}>{a.srv}</div>
                  </div>
                </div>
              ))}
            </Card>
          </FadeIn>

          {/* Right column */}
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <FadeIn from={24}>
              <Card>
                <div style={{ color: C.t1, fontWeight: 700, fontSize: 14, marginBottom: 8 }}>Clienti VIP</div>
                <div style={{ fontSize: 28, fontWeight: 800, color: C.yellow }}>23</div>
                <div style={{ color: C.t2, fontSize: 11, marginTop: 2 }}>↑ 5 nuovi questo mese</div>
                <div style={{ display: "inline-block", background: C.yellow, color: C.bg, borderRadius: 4, padding: "2px 8px", fontSize: 11, fontWeight: 700, marginTop: 6 }}>★ VIP</div>
              </Card>
            </FadeIn>
            <FadeIn from={28}>
              <Card>
                <div style={{ color: C.t1, fontWeight: 700, fontSize: 14, marginBottom: 8 }}>Fatture da incassare</div>
                <div style={{ fontSize: 28, fontWeight: 800, color: C.yellow }}>€ 1.240</div>
                <div style={{ color: C.t2, fontSize: 11, marginTop: 2 }}>4 fatture in attesa</div>
              </Card>
            </FadeIn>
            <FadeIn from={32}>
              <Card style={{ flex: 1 }}>
                <div style={{ color: C.t1, fontWeight: 700, fontSize: 14, marginBottom: 10 }}>Servizi richiesti</div>
                {[["Taglio", 38, C.green], ["Colore", 24, C.violet], ["Piega", 18, C.cyan], ["Barba", 12, C.yellow]].map(([s, v, c]) => (
                  <div key={s as string} style={{ marginBottom: 8 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: C.t2, marginBottom: 3 }}>
                      <span>{s}</span><span style={{ color: c as string }}>{v}%</span>
                    </div>
                    <div style={{ background: C.card2, borderRadius: 4, height: 6 }}>
                      <div style={{ width: `${v}%`, background: c as string, borderRadius: 4, height: 6 }} />
                    </div>
                  </div>
                ))}
              </Card>
            </FadeIn>
          </div>
        </div>
      </FadeIn>

      {/* Callouts */}
      <Callout n={1} delay={8}  style={{ position: "absolute", top: 76, left: 248 }} />
      <Callout n={2} delay={22} style={{ position: "absolute", top: 202, left: 248 }} />
      <Callout n={3} delay={28} style={{ position: "absolute", top: 202, right: 16 }} />
    </Layout>
  );
};
