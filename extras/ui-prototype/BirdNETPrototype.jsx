/**
 * BirdNET Remix — UI Prototype
 * Scale: 4× (160×128 → 640×512)
 * Reference: initial_design/07-ui-specification.md
 *
 * REVIEW NOTES:
 * - CONFIG screen: character-cycling input mocked as static "entering..." state per spec
 * - Spectrogram: uses Option B (confidence-band bars) per 06-software-design.md recommendation
 * - Button A long-press (boot→config) simulated at 2s per prompt (spec says 3s for C)
 * - Button C long-press shutdown simulated at 2s (spec says ≥3s — shortened for prototype UX)
 * - DIM timeout shortened to 15s for prototype review (spec: 60s)
 * - Auto-return from DETECTION shortened to 30s (matches spec) with visible countdown bar
 * - History scroll: Button A = scroll up, Button C = scroll down (per 07 history button hints)
 * - REVIEW: Idle screen status bar placement — spec shows battery bottom-right in 06 but
 *   top status bar in 07. Implemented top status bar (07 takes precedence).
 * - REVIEW: CONFIG screen layout not fully specified in 07-ui-specification.md — layout
 *   improvised as 4-step wizard with step indicator. Needs designer sign-off.
 * - REVIEW: Shutdown screen — spec says "screen goes black" after ~3s. Implemented as
 *   fade to black then reset to BOOT for prototype looping purposes.
 */

import { useState, useEffect, useRef, useCallback } from "react";

// ─── Palette ────────────────────────────────────────────────────────────────
const C = {
  bg:         "#0D1B0E",
  primary:    "#F0ECD8",
  secondary:  "#8BA888",
  accent:     "#E8C84A",
  confFill:   "#4CAF50",
  confBg:     "#1E3320",
  specLow:    "#1A3A5C",
  specHigh:   "#F0A030",
  batGood:    "#66BB6A",
  batLow:     "#FFA726",
  batCrit:    "#EF5350",
  divider:    "#2A4A2A",
  btnHint:    "#567856",
};

// ─── Mock Data ───────────────────────────────────────────────────────────────
const DETECTIONS = [
  { common: "Great Tit",               scientific: "Parus major",            conf: 87, time: "14:23" },
  { common: "Blue Tit",                scientific: "Cyanistes caeruleus",    conf: 92, time: "14:18" },
  { common: "Robin",                   scientific: "Erithacus rubecula",     conf: 78, time: "13:55" },
  { common: "Song Thrush",             scientific: "Turdus philomelos",      conf: 83, time: "13:41" },
  { common: "Chaffinch",               scientific: "Fringilla coelebs",      conf: 71, time: "13:30" },
  { common: "Blackbird",               scientific: "Turdus merula",          conf: 95, time: "13:12" },
  { common: "Wren",                    scientific: "Troglodytes troglodytes",conf: 66, time: "12:58" },
  { common: "Great Spotted Woodpecker",scientific: "Dendrocopos major",      conf: 74, time: "12:43" },
];

const CONFIG_STEPS = ["Wi-Fi SSID", "Password", "BirdWeather Token", "Timezone"];

// ─── Helpers ─────────────────────────────────────────────────────────────────
const px = (n) => `${n * 4}px`; // scale 1× spec px → 4× prototype px

function batColor(pct) {
  if (pct <= 20) return C.batCrit;
  if (pct <= 40) return C.batLow;
  return C.batGood;
}

function useNow() {
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);
  return now;
}

function fmtTime(d) {
  return d.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false });
}
function fmtHHMM(d) {
  return d.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", hour12: false });
}
function fmtDate(d) {
  return d.toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
}
function fmtDateParts(d) {
  return {
    weekday: d.toLocaleDateString("en-GB", { weekday: "long" }),
    date: d.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" }),
  };
}

// ─── Sub-components ──────────────────────────────────────────────────────────

// Status bar — 14px tall in spec → 56px scaled
function StatusBar({ now, battery, wifi }) {
  const batPct = battery;
  const segs = Math.round(batPct / 20); // 0–5 segments
  const bc = batColor(batPct);
  return (
    <div style={{
      height: px(14), background: C.bg,
      borderBottom: `1px solid ${C.divider}`,
      display: "flex", alignItems: "center",
      padding: `0 ${px(4)}`, gap: px(4),
      fontFamily: "'Share Tech Mono', 'Courier New', monospace",
      fontSize: px(7), color: C.secondary,
      flexShrink: 0,
    }}>
      {/* Wi-Fi icon */}
      <span style={{ color: wifi ? C.secondary : C.btnHint, fontSize: px(8) }}>
        {wifi ? "▲" : "△"}
      </span>
      {/* Battery */}
      <span style={{ color: bc }}>
        {"["}
        {"█".repeat(segs)}{"░".repeat(5 - segs)}
        {"]"} {batPct}%
      </span>
      <span style={{ flex: 1 }} />
      {/* Time */}
      <span style={{ color: C.primary, fontSize: px(7) }}>{fmtHHMM(now)}</span>
    </div>
  );
}

// Button hint bar — spec y:104–114 (10px) → 40px scaled
function BtnBar({ hints }) {
  return (
    <div style={{
      height: px(10), background: C.bg,
      borderTop: `1px solid ${C.divider}`,
      display: "flex", alignItems: "center", justifyContent: "space-around",
      padding: `0 ${px(4)}`,
      fontFamily: "'Share Tech Mono', 'Courier New', monospace",
      fontSize: px(7), color: C.btnHint,
      flexShrink: 0,
    }}>
      {hints.map((h, i) => <span key={i}>{h}</span>)}
    </div>
  );
}

// Confidence bar
function ConfBar({ pct }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: px(3) }}>
      <div style={{
        flex: 1, height: px(8), background: C.confBg,
        borderRadius: px(2), overflow: "hidden",
      }}>
        <div style={{
          width: `${pct}%`, height: "100%", background: C.confFill,
          transition: "width 0.3s ease",
        }} />
      </div>
      <span style={{
        fontFamily: "'Share Tech Mono', 'Courier New', monospace",
        fontSize: px(9), color: C.primary, minWidth: px(20), textAlign: "right",
      }}>{pct}%</span>
    </div>
  );
}

// Spectrogram bars (Option B: confidence-band visualiser)
function Spectrogram({ seed }) {
  const bars = Array.from({ length: 20 }, (_, i) => {
    const h = 20 + Math.abs(Math.sin((seed + i) * 0.7 + i * 0.4) * 80);
    return Math.round(h);
  });
  const maxH = px(40); // spectrogram area height ~40px spec
  return (
    <div style={{
      display: "flex", alignItems: "flex-end", gap: px(1),
      height: px(40), padding: `0 ${px(2)}`,
    }}>
      {bars.map((h, i) => {
        const ratio = h / 100;
        // interpolate specLow → specHigh
        const r = Math.round(26 + ratio * (240 - 26));
        const g = Math.round(58 + ratio * (160 - 58));
        const b = Math.round(92 + ratio * (48 - 92));
        return (
          <div key={i} style={{
            flex: 1, height: `${h}%`,
            background: `rgb(${r},${g},${b})`,
            borderRadius: `${px(1)} ${px(1)} 0 0`,
            transition: "height 0.4s ease",
          }} />
        );
      })}
    </div>
  );
}

// Listening animation dots
function ListeningAnim({ tick }) {
  const phase = tick % 3;
  return (
    <div style={{
      display: "flex", alignItems: "center", justifyContent: "center",
      gap: px(4), marginTop: px(4),
      fontFamily: "'Share Tech Mono', 'Courier New', monospace",
      fontSize: px(9),
    }}>
      <span style={{ color: C.secondary }}>≋</span>
      <span style={{ color: C.secondary }}>Listening...</span>
      {[0, 1, 2].map(i => (
        <span key={i} style={{
          color: phase === i ? C.primary : C.secondary,
          transition: "color 0.2s",
        }}>·</span>
      ))}
      <span style={{ color: C.secondary }}>≋</span>
    </div>
  );
}

// ─── Screens ─────────────────────────────────────────────────────────────────

function BootScreen() {
  const [pos, setPos] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setPos(p => (p + 5) % 110), 80);
    return () => clearInterval(t);
  }, []);
  return (
    <div style={{
      flex: 1, display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center",
      background: C.bg, gap: px(6),
    }}>
      <div style={{
        fontFamily: "'Share Tech Mono', 'Courier New', monospace",
        fontSize: px(14), color: C.accent, fontWeight: "bold",
      }}>🐦 BirdNET Remix</div>
      <div style={{
        fontFamily: "'Share Tech Mono', 'Courier New', monospace",
        fontSize: px(9), color: C.secondary,
      }}>Starting up...</div>
      {/* Indeterminate progress bar */}
      <div style={{
        width: px(100), height: px(8), background: C.confBg,
        borderRadius: px(2), overflow: "hidden", position: "relative",
      }}>
        <div style={{
          position: "absolute", left: `${pos}%`, width: "30%", height: "100%",
          background: C.accent, borderRadius: px(2),
          transform: "translateX(-50%)",
          transition: "left 0.08s linear",
        }} />
      </div>
    </div>
  );
}

function ConfigScreen({ step }) {
  const labels = ["SSID", "Password", "BirdWeather Token", "Timezone"];
  const mocks  = ["MyHomeNetwork", "••••••••••••", "bw_tok_XXXX", "Europe/London"];
  return (
    <div style={{
      flex: 1, display: "flex", flexDirection: "column",
      background: C.bg, padding: px(4), gap: px(4),
    }}>
      {/* Header */}
      <div style={{
        fontFamily: "'Share Tech Mono', 'Courier New', monospace",
        fontSize: px(9), color: C.accent, fontWeight: "bold",
      }}>Wi-Fi Setup ({step + 1}/{labels.length})</div>
      <div style={{ height: "1px", background: C.divider }} />
      {/* Step label */}
      <div style={{
        fontFamily: "'Share Tech Mono', 'Courier New', monospace",
        fontSize: px(9), color: C.secondary,
      }}>{labels[step]}</div>
      {/* Mock input field */}
      <div style={{
        border: `1px solid ${C.accent}`, borderRadius: px(2),
        padding: `${px(2)} ${px(3)}`,
        fontFamily: "'Share Tech Mono', 'Courier New', monospace",
        fontSize: px(9), color: C.primary,
        background: C.confBg,
      }}>
        {mocks[step]}<span style={{ color: C.accent }}>█</span>
      </div>
      <div style={{
        fontFamily: "'Share Tech Mono', 'Courier New', monospace",
        fontSize: px(7), color: C.btnHint, marginTop: "auto",
      }}>
        {/* REVIEW: CONFIG input interaction not specified — mocked as static */}
        [A]Prev char  [B]Next char  [C]Confirm
      </div>
      {/* Step dots */}
      <div style={{ display: "flex", gap: px(3), justifyContent: "center" }}>
        {labels.map((_, i) => (
          <div key={i} style={{
            width: px(5), height: px(5), borderRadius: "50%",
            background: i === step ? C.accent : C.divider,
          }} />
        ))}
      </div>
    </div>
  );
}

function IdleScreen({ now, battery, wifi, tick }) {
  const { weekday, date } = fmtDateParts(now);
  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", background: C.bg }}>
      <StatusBar now={now} battery={battery} wifi={wifi} />
      <div style={{
        flex: 1, display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
        gap: px(2),
      }}>
        {/* Clock — spec: 28px → 112px scaled */}
        <div style={{
          fontFamily: "'Share Tech Mono', 'Courier New', monospace",
          fontSize: px(28), color: C.primary, fontWeight: "bold",
          letterSpacing: px(1),
        }}>{fmtTime(now)}</div>
        {/* Date — spec: 11px → 44px scaled */}
        <div style={{
          fontFamily: "'Share Tech Mono', 'Courier New', monospace",
          fontSize: px(11), color: C.secondary,
        }}>{weekday}</div>
        <div style={{
          fontFamily: "'Share Tech Mono', 'Courier New', monospace",
          fontSize: px(11), color: C.secondary,
        }}>{date}</div>
        <ListeningAnim tick={tick} />
      </div>
      <BtnBar hints={["[A]Bright", "[B]History", "[C▶]Off"]} />
    </div>
  );
}

function DetectionScreen({ detection, now, battery, wifi, returnPct, specSeed }) {
  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", background: C.bg }}>
      <StatusBar now={now} battery={battery} wifi={wifi} />
      {/* Common name — spec y:15–33 (18px) → 72px */}
      <div style={{
        padding: `${px(2)} ${px(4)} 0`,
        fontFamily: "'Share Tech Mono', 'Courier New', monospace",
        fontSize: px(16), color: C.primary, fontWeight: "bold",
        overflow: "hidden", whiteSpace: "nowrap", textOverflow: "ellipsis",
        animation: "slideIn 0.2s ease-out",
      }}>{detection.common}</div>
      {/* Scientific name — spec y:34–46 (12px) → 48px */}
      <div style={{
        padding: `0 ${px(4)}`,
        fontFamily: "'Share Tech Mono', 'Courier New', monospace",
        fontSize: px(11), color: C.secondary, fontStyle: "italic",
      }}>{detection.scientific}</div>
      {/* Confidence bar — spec y:47–62 (15px) → 60px */}
      <div style={{ padding: `${px(2)} ${px(4)}` }}>
        <ConfBar pct={detection.conf} />
      </div>
      {/* Spectrogram — spec y:63–103 (40px) → 160px */}
      <div style={{
        flex: 1, background: C.bg,
        borderTop: `1px solid ${C.divider}`,
        borderBottom: `1px solid ${C.divider}`,
        overflow: "hidden",
      }}>
        <Spectrogram seed={specSeed} />
      </div>
      {/* Prototype-only: auto-return countdown bar */}
      <div style={{ height: px(3), background: C.confBg }}>
        <div style={{
          height: "100%", background: C.accent,
          width: `${returnPct}%`, transition: "width 1s linear",
        }} />
      </div>
      <BtnBar hints={["[A]Bright", "[B]History", "[C▶]Off"]} />
    </div>
  );
}

function HistoryScreen({ detections, scrollIdx, battery, wifi, now }) {
  const visible = detections.slice(scrollIdx, scrollIdx + 5);
  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", background: C.bg }}>
      {/* Header — spec y:0–14 */}
      <div style={{
        height: px(14), display: "flex", alignItems: "center",
        padding: `0 ${px(4)}`, borderBottom: `1px solid ${C.divider}`,
        gap: px(4),
      }}>
        <span style={{
          fontFamily: "'Share Tech Mono', 'Courier New', monospace",
          fontSize: px(9), color: C.accent, fontWeight: "bold", flex: 1,
        }}>Recent Detections</span>
        <span style={{
          fontFamily: "'Share Tech Mono', 'Courier New', monospace",
          fontSize: px(7), color: batColor(battery),
        }}>[{"█".repeat(Math.round(battery/20))}{"░".repeat(5-Math.round(battery/20))}]</span>
      </div>
      {/* Rows — spec: 5 rows × 14px = 70px → 280px */}
      {visible.map((d, i) => (
        <div key={i} style={{
          height: px(14), display: "flex", alignItems: "center",
          padding: `0 ${px(4)}`, gap: px(3),
          borderBottom: `1px solid ${C.divider}`,
          background: i === 0 && scrollIdx === 0 ? "#0F2210" : "transparent",
        }}>
          <span style={{
            fontFamily: "'Share Tech Mono', 'Courier New', monospace",
            fontSize: px(9),
            color: i === 0 ? C.accent : C.secondary,
            minWidth: px(22),
          }}>{d.time}</span>
          <span style={{
            fontFamily: "'Share Tech Mono', 'Courier New', monospace",
            fontSize: px(9),
            color: i === 0 ? C.accent : C.primary,
            flex: 1, overflow: "hidden", whiteSpace: "nowrap", textOverflow: "ellipsis",
          }}>{d.common}</span>
          {/* Mini conf bar */}
          <div style={{ width: px(24), height: px(5), background: C.confBg, borderRadius: px(1) }}>
            <div style={{ width: `${d.conf}%`, height: "100%", background: C.confFill, borderRadius: px(1) }} />
          </div>
          <span style={{
            fontFamily: "'Share Tech Mono', 'Courier New', monospace",
            fontSize: px(8), color: C.secondary, minWidth: px(16), textAlign: "right",
          }}>{d.conf}%</span>
        </div>
      ))}
      <div style={{ flex: 1 }} />
      <BtnBar hints={["[A]↑ Scroll", "[B]Back", "[C]↓ Scroll"]} />
    </div>
  );
}

function ShutdownScreen() {
  return (
    <div style={{
      flex: 1, display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center",
      background: C.bg, gap: px(4),
    }}>
      <div style={{
        fontFamily: "'Share Tech Mono', 'Courier New', monospace",
        fontSize: px(11), color: C.primary,
      }}>Shutting down...</div>
      <div style={{
        fontFamily: "'Share Tech Mono', 'Courier New', monospace",
        fontSize: px(9), color: C.secondary,
      }}>Saving detections database</div>
      <div style={{
        fontFamily: "'Share Tech Mono', 'Courier New', monospace",
        fontSize: px(9), color: C.secondary,
      }}>Please wait</div>
    </div>
  );
}

// ─── Main App ────────────────────────────────────────────────────────────────

export default function BirdNETPrototype() {
  const now = useNow();

  // State machine
  const [screen, setScreen] = useState("BOOT"); // BOOT|CONFIG|IDLE|DETECTION|HISTORY|SHUTDOWN
  const [prevScreen, setPrevScreen] = useState("IDLE");
  const [brightness, setBrightness] = useState(1); // 1, 0.5, 0.1
  const [battery] = useState(78);
  const [wifi] = useState(true);

  // Detection cycling
  const [detIdx, setDetIdx] = useState(0);
  const [specSeed, setSpecSeed] = useState(0);

  // Timers
  const [returnSecs, setReturnSecs] = useState(30); // DETECTION → IDLE countdown
  const [animTick, setAnimTick] = useState(0);      // listening dot animation
  const [configStep, setConfigStep] = useState(0);
  const [scrollIdx, setScrollIdx] = useState(0);

  // Dim timer
  const dimTimerRef = useRef(null);
  const [dimmed, setDimmed] = useState(false);

  const resetDimTimer = useCallback(() => {
    setDimmed(false);
    if (dimTimerRef.current) clearTimeout(dimTimerRef.current);
    dimTimerRef.current = setTimeout(() => setDimmed(true), 15000);
  }, []);

  // Boot → IDLE after 3s
  useEffect(() => {
    if (screen === "BOOT") {
      const t = setTimeout(() => setScreen("IDLE"), 3000);
      return () => clearTimeout(t);
    }
  }, [screen]);

  // Shutdown → BOOT after 3s (prototype loop)
  useEffect(() => {
    if (screen === "SHUTDOWN") {
      const t = setTimeout(() => { setScreen("BOOT"); setBrightness(1); }, 3000);
      return () => clearTimeout(t);
    }
  }, [screen]);

  // Auto-cycle detections every 12s in IDLE or DETECTION
  useEffect(() => {
    if (screen !== "IDLE" && screen !== "DETECTION") return;
    const t = setInterval(() => {
      const next = (detIdx + 1) % DETECTIONS.length;
      setDetIdx(next);
      setSpecSeed(s => s + 7);
      setReturnSecs(30);
      setScreen("DETECTION");
    }, 12000);
    return () => clearInterval(t);
  }, [screen, detIdx]);

  // DETECTION → IDLE countdown
  useEffect(() => {
    if (screen !== "DETECTION") return;
    if (returnSecs <= 0) { setScreen("IDLE"); return; }
    const t = setTimeout(() => setReturnSecs(s => s - 1), 1000);
    return () => clearTimeout(t);
  }, [screen, returnSecs]);

  // Listening animation tick (0.4s per dot)
  useEffect(() => {
    const t = setInterval(() => setAnimTick(n => n + 1), 400);
    return () => clearInterval(t);
  }, []);

  // Start dim timer on mount
  useEffect(() => { resetDimTimer(); return () => clearTimeout(dimTimerRef.current); }, []);

  // ── Button handlers ──────────────────────────────────────────────────────
  const longPressRef = useRef(null);

  function handleBtnDown(btn) {
    resetDimTimer();
    if (dimmed) return; // any press wakes from dim
    longPressRef.current = setTimeout(() => {
      if (btn === "C") { setScreen("SHUTDOWN"); }
      if (btn === "A" && screen === "BOOT") { setScreen("CONFIG"); setConfigStep(0); }
    }, 2000);
  }

  function handleBtnUp(btn) {
    clearTimeout(longPressRef.current);
  }

  function handleBtnClick(btn) {
    if (dimmed) { setDimmed(false); resetDimTimer(); return; }
    resetDimTimer();

    if (btn === "A") {
      if (screen === "HISTORY") {
        setScrollIdx(i => Math.max(0, i - 1));
      } else {
        // Cycle brightness: 1 → 0.5 → 0.1 → 1
        setBrightness(b => b === 1 ? 0.5 : b === 0.5 ? 0.1 : 1);
      }
    }

    if (btn === "B") {
      if (screen === "HISTORY") {
        setScreen(prevScreen);
      } else if (screen === "IDLE" || screen === "DETECTION") {
        setPrevScreen(screen);
        setScrollIdx(0);
        setScreen("HISTORY");
      } else if (screen === "CONFIG") {
        setConfigStep(s => Math.min(s + 1, CONFIG_STEPS.length - 1));
      }
    }

    if (btn === "C") {
      if (screen === "HISTORY") {
        setScrollIdx(i => Math.min(i + 1, DETECTIONS.length - 5));
      }
      // long press handled in handleBtnDown
    }
  }

  const detection = DETECTIONS[detIdx];
  const returnPct = (returnSecs / 30) * 100;

  // ── Render ───────────────────────────────────────────────────────────────
  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
        @keyframes slideIn { from { transform: translateX(40px); opacity: 0; } to { transform: none; opacity: 1; } }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #1a1a1a; display: flex; align-items: center; justify-content: center; min-height: 100vh; }
      `}</style>

      {/* Device shell — ~750×620px */}
      <div style={{
        background: "#2a2a2a",
        borderRadius: "24px",
        padding: "24px 32px 28px",
        display: "flex", flexDirection: "column", alignItems: "center",
        gap: "16px",
        boxShadow: "0 8px 32px rgba(0,0,0,0.7), inset 0 1px 0 rgba(255,255,255,0.05)",
        userSelect: "none",
      }}>
        {/* Bezel + display */}
        <div style={{
          background: "#111",
          borderRadius: "6px",
          padding: "6px",
          boxShadow: "inset 0 2px 8px rgba(0,0,0,0.8)",
        }}>
          {/* Display — 640×512px */}
          <div style={{
            width: "640px", height: "512px",
            background: C.bg,
            overflow: "hidden",
            borderRadius: "2px",
            opacity: dimmed ? 0.1 : brightness,
            transition: "opacity 0.5s ease",
            display: "flex", flexDirection: "column",
          }}>
            {screen === "BOOT"      && <BootScreen />}
            {screen === "CONFIG"    && <ConfigScreen step={configStep} />}
            {screen === "IDLE"      && <IdleScreen now={now} battery={battery} wifi={wifi} tick={animTick} />}
            {screen === "DETECTION" && <DetectionScreen detection={detection} now={now} battery={battery} wifi={wifi} returnPct={returnPct} specSeed={specSeed} />}
            {screen === "HISTORY"   && <HistoryScreen detections={DETECTIONS} scrollIdx={scrollIdx} battery={battery} wifi={wifi} now={now} />}
            {screen === "SHUTDOWN"  && <ShutdownScreen />}
          </div>
        </div>

        {/* Status strip */}
        <div style={{
          display: "flex", gap: "16px", alignItems: "center",
          fontFamily: "'Share Tech Mono', 'Courier New', monospace",
          fontSize: "11px", color: "#888",
        }}>
          <span>STATE: <span style={{ color: C.accent }}>{screen}</span></span>
          <span>BAT: <span style={{ color: batColor(battery) }}>{battery}%</span></span>
          <span>WIFI: <span style={{ color: wifi ? C.batGood : "#888" }}>{wifi ? "●" : "○"}</span></span>
          <span>BRIGHT: <span style={{ color: C.secondary }}>{Math.round(brightness * 100)}%</span></span>
          {dimmed && <span style={{ color: C.batLow }}>⚠ DIMMED</span>}
        </div>

        {/* Buttons */}
        <div style={{ display: "flex", gap: "32px" }}>
          {["A", "B", "C"].map(btn => (
            <div key={btn} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "6px" }}>
              <button
                onMouseDown={() => handleBtnDown(btn)}
                onMouseUp={() => { handleBtnUp(btn); handleBtnClick(btn); }}
                onMouseLeave={() => handleBtnUp(btn)}
                style={{
                  width: "52px", height: "52px",
                  borderRadius: "50%",
                  background: "linear-gradient(145deg, #3a3a3a, #222)",
                  border: "2px solid #444",
                  color: C.secondary,
                  fontFamily: "'Share Tech Mono', 'Courier New', monospace",
                  fontSize: "16px", fontWeight: "bold",
                  cursor: "pointer",
                  boxShadow: "0 4px 8px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1)",
                  transition: "transform 0.1s, box-shadow 0.1s",
                }}
                onMouseEnter={e => e.currentTarget.style.transform = "scale(1.05)"}
              >{btn}</button>
              <span style={{
                fontFamily: "'Share Tech Mono', 'Courier New', monospace",
                fontSize: "10px", color: "#555",
              }}>
                {btn === "A" ? "Bright / ↑" : btn === "B" ? "History" : "Hold=Off / ↓"}
              </span>
            </div>
          ))}
        </div>

        {/* Prototype hint */}
        <div style={{
          fontFamily: "'Share Tech Mono', 'Courier New', monospace",
          fontSize: "10px", color: "#444", textAlign: "center",
        }}>
          Hold A at BOOT for CONFIG · Hold C 2s for SHUTDOWN · Auto-dim 15s · Auto-cycle 12s
        </div>
      </div>
    </>
  );
}
