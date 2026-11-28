import React from 'react';
import {Img, staticFile} from 'remotion';
import {backOut, BRAND, C, easeInOut, easeOut, FONT, lerp, LOOK, tw} from './theme';

const NEON = LOOK === 'neon';

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
              background: NEON ? 'rgba(14,10,28,0.94)' : C.white,
              border: NEON ? `3px solid #3A2C6E` : `6px solid ${C.ink}`,
              borderRadius: NEON ? 24 : 20,
              boxShadow: NEON ? '0 0 32px rgba(176,92,255,0.32), inset 0 0 0 1px rgba(176,92,255,0.25)' : `9px 9px 0 ${C.ink}`,
              padding: '20px 34px 24px',
              fontFamily: FONT.sans,
              fontWeight: 800,
              fontSize: 52,
              lineHeight: '64px',
              letterSpacing: '-0.015em',
              color: NEON ? BRAND.starlight : C.ink,
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

/** Font for the small labels (pill, tags, counter label, card kicker). Default: the series' original
 *  pixel font. 028 and later Blender versions use Inter Black (no pixel looks, user rule 22 Nov). */
export const LabelFont = React.createContext<'pixel' | 'sans'>('pixel');
const useLF = () => (NEON ? {fontFamily: FONT.mono, fontWeight: 700, letterSpacing: '0.08em'} : React.useContext(LabelFont) === 'sans' ? {fontFamily: FONT.sans, fontWeight: 900} : {fontFamily: FONT.pixel, fontWeight: 700});
/** Same choice for SVG text: {family, weight}. Part 4+ (2D) also uses 'sans'. */
export const useLabelSvg = () => (NEON ? {family: FONT.mono, weight: 700} : React.useContext(LabelFont) === 'sans' ? {family: FONT.sans, weight: 900} : {family: FONT.pixel, weight: 700});

/** Series pill + part pill, top left. Neon look: the brand icon (watermark) starts the row. */
export const SeriesPill: React.FC<{part: number; op?: number; label?: string}> = ({part, op = 1, label}) => {
  const lf = useLF();
  if (NEON) {
    const pill = (c: string): React.CSSProperties => ({...lf, fontSize: 27, padding: '9px 18px 10px', borderRadius: 999, color: c, background: `${c}22`, border: `3px solid ${c}`, whiteSpace: 'nowrap'});
    return (
      <div style={{position: 'absolute', left: 48, top: 196, display: 'flex', alignItems: 'center', gap: 12, opacity: op}}>
        <Img src={staticFile('sh-icon.svg')} style={{width: 76, height: 76}} />
        <div style={pill(BRAND.mint)}>IS THIS A BUSINESS?</div>
        <div style={pill(BRAND.cyan)}>{label ?? `PART ${part}`}</div>
      </div>
    );
  }
  return (
    <div style={{position: 'absolute', left: 56, top: 200, display: 'flex', gap: 12, opacity: op}}>
      <div style={{background: C.navy, color: C.paper, ...lf, fontSize: 30, padding: '10px 18px 12px', borderRadius: 999, border: `5px solid ${C.ink}`}}>IS THIS A BUSINESS?</div>
      <div style={{background: C.gold, color: C.ink, ...lf, fontSize: 30, padding: '10px 18px 12px', borderRadius: 999, border: `5px solid ${C.ink}`}}>{label ?? `PART ${part}`}</div>
    </div>
  );
};

/** Small time-jump tag ("1 HOUR LATER"). */
export const Tag: React.FC<{t: number; at: number; until: number; text: string; x?: number; y?: number}> = ({t, at, until, text, x = 56, y = 290}) => {
  if (t < at || t > until + 0.2) return null;
  const k = tw(t, at, 0.3, backOut);
  const o = 1 - tw(t, until, 0.18);
  return (
    <div style={{position: 'absolute', left: x, top: y, opacity: o, transform: `scale(${k})`, transformOrigin: '0% 50%'}}>
      <div style={NEON
        ? {background: BRAND.night, color: BRAND.starlight, ...useLF(), fontSize: 28, padding: '8px 18px 10px', borderRadius: 14, border: `3px solid ${BRAND.sunPink}`, boxShadow: '0 0 22px rgba(255,90,223,0.35)', rotate: '-3deg'}
        : {background: C.white, color: C.ink, ...useLF(), fontSize: 30, padding: '8px 18px 10px', borderRadius: 14, border: `5px solid ${C.ink}`, boxShadow: `6px 6px 0 ${C.ink}`, rotate: '-3deg'}}>{text}</div>
    </div>
  );
};

/** Stairs counter, top right. Bumps when the number changes. Neon look: mono label in haze, the number in
 *  JetBrains Mono with the eclipse gradient (a non-default colour, e.g. C.coral for "too much", stays solid). */
export const Counter: React.FC<{value: number; bump: number; label?: string; op?: number; color?: string; sub?: string; prefix?: string}> = ({value, bump, label = 'STAIRS', op = 1, color = C.ink, sub, prefix = ''}) => {
  const lf = useLF();
  const solid = NEON && color !== C.ink;
  const num: React.CSSProperties = NEON
    ? {fontFamily: FONT.mono, fontWeight: 700, fontSize: 88, lineHeight: '92px', letterSpacing: '-0.02em',
       ...(solid ? {color} : {backgroundImage: BRAND.gradient, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent'}),
       filter: `drop-shadow(0 0 14px ${solid ? color + '88' : 'rgba(176,92,255,0.55)'})`}
    : {fontFamily: FONT.sans, fontWeight: 900, fontSize: 92, lineHeight: '92px', color, letterSpacing: '-0.03em'};
  return (
    <div style={{position: 'absolute', right: 52, top: 192, textAlign: 'right', opacity: op}}>
      <div style={{...lf, fontSize: NEON ? 26 : 28, color: NEON ? BRAND.haze : C.ink, letterSpacing: NEON ? '0.2em' : 2}}>{label}</div>
      <div style={{...num, transform: `scale(${1 + 0.12 * bump})`, transformOrigin: '100% 50%', fontVariantNumeric: 'tabular-nums'}}>{prefix}{Math.round(value).toLocaleString('en-US')}</div>
      {sub && <div style={{...lf, fontSize: 26, color: C.coral, marginTop: 4, letterSpacing: NEON ? '0.12em' : 1}}>{sub}</div>}
    </div>
  );
};

/** End card: "NEXT · PART n" + the question. Slides up from below. */
export const EndCard: React.FC<{t: number; at: number; out: number; next: number; lines: React.ReactNode[]; sub?: string; kicker?: string}> = ({t, at, out, next, lines, sub = '', kicker}) => {   // no like/share/follow asks (user, 27 Nov)
  if (t < at) return null;
  const k = tw(t, at, 0.5, easeOut);
  const ko = tw(t, out, 0.4, easeInOut);
  return (
    <div style={{position: 'absolute', left: 70, width: 870, top: lerp(1920, 1040, k) + ko * 900, opacity: 1 - ko}}>
      <div style={NEON
        ? {background: 'rgba(14,10,28,0.96)', border: '3px solid #3A2C6E', borderRadius: 28, boxShadow: '0 0 48px rgba(176,92,255,0.35), inset 0 0 0 1px rgba(34,230,255,0.25)', padding: '28px 40px 34px'}
        : {background: C.navy, border: `6px solid ${C.ink}`, borderRadius: 26, boxShadow: `10px 10px 0 ${C.ink}`, padding: '28px 40px 34px'}}>
        <div style={{...useLF(), fontSize: NEON ? 28 : 32, color: NEON ? BRAND.cyan : C.gold, letterSpacing: NEON ? '0.2em' : 2}}>{kicker ?? `NEXT · PART ${next}`}</div>
        <div style={{fontFamily: NEON ? FONT.display : FONT.sans, fontWeight: NEON ? 800 : 900, fontSize: NEON ? 54 : 64, lineHeight: NEON ? '66px' : '74px', color: NEON ? BRAND.starlight : C.paper, marginTop: 14, letterSpacing: NEON ? '-0.01em' : '-0.02em', textTransform: NEON ? 'uppercase' : undefined}}>
          {lines.map((l, i) => <div key={i}>{l}</div>)}
        </div>
        {sub && <div style={{fontFamily: FONT.sans, fontWeight: 700, fontSize: 36, color: NEON ? BRAND.haze : C.tealLight, marginTop: 18}}>{sub}</div>}
      </div>
    </div>
  );
};
