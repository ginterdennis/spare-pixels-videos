import React from 'react';
import {backOut, C, easeInOut, easeOut, FONT, lerp, tw} from './theme';

export const Em: React.FC<{children: React.ReactNode; c?: string}> = ({children, c = C.coral}) => <span style={{color: c}}>{children}</span>;

export type Cap = {at: number; until: number; lines: React.ReactNode[]};

/** Caption card under the scene: white card, navy outline, hard offset shadow. Pops in, drops out. */
export const Captions: React.FC<{t: number; caps: Cap[]; top?: number}> = ({t, caps, top = 1236}) => (
  <>
    {caps.map((c, i) => {
      if (t < c.at - 0.001 || t > c.until + 0.2) return null;
      const kin = c.at <= 0 ? 1 : tw(t, c.at, 0.32, backOut);
      const kout = tw(t, c.until, 0.16, easeInOut);
      const sc = lerp(0.86, 1, kin) * lerp(1, 0.9, kout);
      const op = Math.min(1, c.at <= 0 ? 1 : tw(t, c.at, 0.12)) * (1 - kout);
      return (
        <div key={i} style={{position: 'absolute', left: 60, width: 880, top, display: 'flex', justifyContent: 'center', opacity: op}}>
          <div
            style={{
              transform: `scale(${sc}) translateY(${lerp(18, 0, kin)}px)`,
              transformOrigin: '50% 0%',
              background: C.white,
              border: `6px solid ${C.ink}`,
              borderRadius: 20,
              boxShadow: `9px 9px 0 ${C.ink}`,
              padding: '20px 34px 24px',
              fontFamily: FONT.sans,
              fontWeight: 800,
              fontSize: 52,
              lineHeight: '64px',
              letterSpacing: '-0.015em',
              color: C.ink,
              textAlign: 'center',
              maxWidth: 860,
            }}
          >
            {c.lines.map((l, li) => <div key={li}>{l}</div>)}
          </div>
        </div>
      );
    })}
  </>
);

/** Series pill + part pill, top left. */
export const SeriesPill: React.FC<{part: number; op?: number}> = ({part, op = 1}) => (
  <div style={{position: 'absolute', left: 56, top: 200, display: 'flex', gap: 12, opacity: op}}>
    <div style={{background: C.navy, color: C.paper, fontFamily: FONT.pixel, fontWeight: 700, fontSize: 30, padding: '10px 18px 12px', borderRadius: 999, border: `5px solid ${C.ink}`}}>IS THIS A BUSINESS?</div>
    <div style={{background: C.gold, color: C.ink, fontFamily: FONT.pixel, fontWeight: 700, fontSize: 30, padding: '10px 18px 12px', borderRadius: 999, border: `5px solid ${C.ink}`}}>PART {part}</div>
  </div>
);

/** Small time-jump tag ("1 HOUR LATER"). */
export const Tag: React.FC<{t: number; at: number; until: number; text: string; x?: number; y?: number}> = ({t, at, until, text, x = 56, y = 290}) => {
  if (t < at || t > until + 0.2) return null;
  const k = tw(t, at, 0.3, backOut);
  const o = 1 - tw(t, until, 0.18);
  return (
    <div style={{position: 'absolute', left: x, top: y, opacity: o, transform: `scale(${k})`, transformOrigin: '0% 50%'}}>
      <div style={{background: C.white, color: C.ink, fontFamily: FONT.pixel, fontWeight: 700, fontSize: 30, padding: '8px 18px 10px', borderRadius: 14, border: `5px solid ${C.ink}`, boxShadow: `6px 6px 0 ${C.ink}`, rotate: '-3deg'}}>{text}</div>
    </div>
  );
};

/** Stairs counter, top right. Bumps when the number changes. */
export const Counter: React.FC<{value: number; bump: number; label?: string; op?: number; color?: string; sub?: string}> = ({value, bump, label = 'STAIRS', op = 1, color = C.ink, sub}) => (
  <div style={{position: 'absolute', right: 52, top: 192, textAlign: 'right', opacity: op}}>
    <div style={{fontFamily: FONT.pixel, fontWeight: 700, fontSize: 28, color: C.ink, letterSpacing: 2}}>{label}</div>
    <div style={{fontFamily: FONT.sans, fontWeight: 900, fontSize: 92, lineHeight: '92px', color, letterSpacing: '-0.03em', transform: `scale(${1 + 0.12 * bump})`, transformOrigin: '100% 50%', fontVariantNumeric: 'tabular-nums'}}>{Math.round(value).toLocaleString('en-US')}</div>
    {sub && <div style={{fontFamily: FONT.pixel, fontWeight: 700, fontSize: 26, color: C.coral, marginTop: 4, letterSpacing: 1}}>{sub}</div>}
  </div>
);

/** End card: "NEXT · PART n" + the question. Slides up from below. */
export const EndCard: React.FC<{t: number; at: number; out: number; next: number; lines: React.ReactNode[]; sub?: string; kicker?: string}> = ({t, at, out, next, lines, sub = 'Follow so you catch it', kicker}) => {
  if (t < at) return null;
  const k = tw(t, at, 0.5, easeOut);
  const ko = tw(t, out, 0.4, easeInOut);
  return (
    <div style={{position: 'absolute', left: 70, width: 870, top: lerp(1920, 1040, k) + ko * 900, opacity: 1 - ko}}>
      <div style={{background: C.navy, border: `6px solid ${C.ink}`, borderRadius: 26, boxShadow: `10px 10px 0 ${C.ink}`, padding: '28px 40px 34px'}}>
        <div style={{fontFamily: FONT.pixel, fontWeight: 700, fontSize: 32, color: C.gold, letterSpacing: 2}}>{kicker ?? `NEXT · PART ${next}`}</div>
        <div style={{fontFamily: FONT.sans, fontWeight: 900, fontSize: 64, lineHeight: '74px', color: C.paper, marginTop: 14, letterSpacing: '-0.02em'}}>
          {lines.map((l, i) => <div key={i}>{l}</div>)}
        </div>
        <div style={{fontFamily: FONT.sans, fontWeight: 700, fontSize: 36, color: C.tealLight, marginTop: 18}}>{sub}</div>
      </div>
    </div>
  );
};
