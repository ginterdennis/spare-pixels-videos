import React from 'react';
import {backOut, C, easeInOut, easeOut, FONT, lerp, T, tw} from './theme';
import {FX, FY, P0, ZMAX} from './PixelWorld';

// ---------- accent spans
export const Gold: React.FC<{children: React.ReactNode}> = ({children}) => <span style={{color: C.gold}}>{children}</span>;
export const Pink: React.FC<{children: React.ReactNode}> = ({children}) => <span style={{color: C.pink}}>{children}</span>;
export const Cyan: React.FC<{children: React.ReactNode}> = ({children}) => <span style={{color: C.cyan}}>{children}</span>;
export const Red: React.FC<{children: React.ReactNode}> = ({children}) => <span style={{color: 'rgb(255,84,96)'}}>{children}</span>;
export const Green: React.FC<{children: React.ReactNode}> = ({children}) => <span style={{color: 'rgb(70,240,120)'}}>{children}</span>;

const HEAD_TOP = 196;
const HEAD_SIZE = 76;
const HEAD_LH = 84;

export type HeadEntry = {at: number; lines: React.ReactNode[]};

/** Top headline. Each entry replaces the previous one: old lines lift out, new lines rise in, staggered. */
export const Headline: React.FC<{t: number; entries: HeadEntry[]}> = ({t, entries}) => {
  let idx = 0;
  for (let i = 0; i < entries.length; i++) if (entries[i].at <= t) idx = i;
  const cur = entries[idx];
  const prev = idx > 0 ? entries[idx - 1] : null;
  const outK = tw(t, cur.at, 0.18, easeInOut);
  const block = (e: HeadEntry, mode: 'in' | 'out') => (
    <div key={`${e.at}-${mode}`} style={{position: 'absolute', top: HEAD_TOP, left: 0, width: 1080}}>
      {e.lines.map((ln, li) => {
        const k = mode === 'in' ? tw(t, e.at + (e.at > 0 ? 0.13 : 0) + li * 0.07, 0.45, easeOut) : 1 - outK;
        const dy = mode === 'in' ? lerp(46, 0, k) : lerp(0, -34, outK);
        return (
          <div
            key={li}
            style={{
              height: HEAD_LH,
              lineHeight: `${HEAD_LH}px`,
              textAlign: 'center',
              fontFamily: FONT.display,
              fontWeight: 900,
              fontSize: HEAD_SIZE,
              letterSpacing: '-0.025em',
              color: C.white,
              opacity: k,
              translate: `0px ${dy}px`,
              textShadow: '0 6px 30px rgba(0,0,0,0.55)',
              whiteSpace: 'nowrap',
            }}
          >
            {ln}
          </div>
        );
      })}
    </div>
  );
  return (
    <>
      {prev && outK < 1 ? block(prev, 'out') : null}
      {block(cur, 'in')}
    </>
  );
};

export type SubEntry = {at: number; until: number; text: React.ReactNode};

export const Sub: React.FC<{t: number; entries: SubEntry[]}> = ({t, entries}) => (
  <>
    {entries.map((e) => {
      const k = Math.min(tw(t, e.at, 0.35, easeOut), 1 - tw(t, e.until - 0.2, 0.2, easeInOut));
      if (k <= 0) return null;
      return (
        <div
          key={e.at}
          style={{
            position: 'absolute', top: HEAD_TOP + 2 * HEAD_LH + 26, width: 1080, textAlign: 'center',
            fontFamily: FONT.display, fontWeight: 700, fontSize: 40, color: C.muted, opacity: k,
            translate: `0px ${lerp(18, 0, k)}px`,
          }}
        >
          {e.text}
        </div>
      );
    })}
  </>
);

// ---------- HUD (house style: small letter-spaced label, big number)
const HudBlock: React.FC<{label: string; value: string; align: 'left' | 'right'; x: number; flash?: number}> = ({label, value, align, x, flash = 0}) => (
  <div style={{position: 'absolute', top: 1404, [align]: x, textAlign: align} as React.CSSProperties}>
    <div style={{fontFamily: FONT.display, fontWeight: 700, fontSize: 22, letterSpacing: '0.24em', color: flash > 0 ? C.pink : C.muted}}>{label}</div>
    <div
      style={{
        fontFamily: FONT.display, fontWeight: 900, fontSize: 68, lineHeight: '84px', color: flash > 0 ? C.pink : C.white,
        fontVariantNumeric: 'tabular-nums', scale: String(1 + 0.32 * flash),
        transformOrigin: align === 'left' ? '0% 50%' : '100% 50%',
      }}
    >
      {value}
    </div>
  </div>
);

export const Hud: React.FC<{t: number; z: number; opacity: number}> = ({t, z, opacity}) => {
  const f = t - T.hudFlash;
  const flash = f > 0 && f < 0.9 ? Math.sin(Math.min(1, f / 0.9) * Math.PI) * (f < 0.45 ? 1 : 0.6) : 0;
  const shake = flash > 0 ? Math.sin(f * 90) * 8 * flash : 0;
  return (
    <div style={{position: 'absolute', inset: 0, opacity}}>
      <HudBlock label="ZOOM" value={`${Math.max(1, Math.round(z))}×`} align="left" x={118} />
      <div style={{position: 'absolute', inset: 0, translate: `${shake}px 0px`}}>
        <HudBlock label="YELLOW LIGHTS FOUND" value="0" align="right" x={150} flash={flash} />
      </div>
    </div>
  );
};

// ---------- reticle around the pixel we are about to zoom into
export const Reticle: React.FC<{t: number}> = ({t}) => {
  const k = Math.min(tw(t, T.reticle, 0.4, backOut), 1 - tw(t, T.zoomStart + 0.6, 0.5, easeInOut));
  if (k <= 0) return null;
  const s = 150 * (1 + 0.05 * Math.sin((t - T.reticle) * Math.PI * 4)) * lerp(1.6, 1, Math.min(1, k));
  const L = 40, th = 8;
  const corner = (sx: number, sy: number) => (
    <div key={`${sx}${sy}`} style={{position: 'absolute', left: FX + (sx * s) / 2 - (sx > 0 ? L : 0), top: FY + (sy * s) / 2 - (sy > 0 ? L : 0), width: L, height: L,
      borderColor: C.gold, borderStyle: 'solid', borderWidth: 0,
      [sy < 0 ? 'borderTopWidth' : 'borderBottomWidth']: th, [sx < 0 ? 'borderLeftWidth' : 'borderRightWidth']: th,
      borderRadius: 6, filter: 'drop-shadow(0 0 10px rgba(0,0,0,0.6))'} as React.CSSProperties} />
  );
  return <div style={{position: 'absolute', inset: 0, opacity: Math.min(1, k)}}>{[[-1, -1], [1, -1], [-1, 1], [1, 1]].map(([a, b]) => corner(a, b))}</div>;
};

// ---------- labels on the three subpixels of the zoomed-in pixel
const PITCH = P0 * ZMAX;
const G = PITCH * 0.05;
const STW = (PITCH - 4 * G) / 3;
const STH = PITCH - 2.6 * G;
export const stripeRect = (k: number) => ({
  x: FX - PITCH / 2 + G + k * (STW + G),
  y: FY - PITCH / 2 + 1.3 * G,
  w: STW,
  h: STH,
});

const LABELS = [
  {name: 'RED', on: true, at: T.lblR, glow: 'rgba(255,60,70,0.9)'},
  {name: 'GREEN', on: true, at: T.lblG, glow: 'rgba(60,255,120,0.9)'},
  {name: 'BLUE', on: false, at: T.lblB, glow: 'rgba(0,0,0,0)'},
];

export const StripeLabels: React.FC<{t: number; opacity: number}> = ({t, opacity}) => (
  <div style={{position: 'absolute', inset: 0, opacity}}>
    {LABELS.map((l, k) => {
      const r = stripeRect(k);
      const pop = tw(t, l.at, 0.42, backOut);
      const pop2 = tw(t, l.at + 0.12, 0.42, backOut);
      if (pop <= 0) return null;
      const pulse = Math.max(0, 1 - (t - l.at) / 0.6);
      const off = !l.on;
      const jitter = off && t - l.at < 0.5 ? Math.sin((t - l.at) * 70) * 6 * (1 - (t - l.at) / 0.5) : 0;
      return (
        <React.Fragment key={l.name}>
          {l.on ? (
            <div style={{position: 'absolute', left: r.x, top: r.y, width: r.w, height: r.h, borderRadius: Math.min(r.w * 0.3, 60),
              boxShadow: `0 0 ${60 + 80 * pulse}px ${10 + 30 * pulse}px ${l.glow}`, opacity: 0.25 + 0.75 * pulse}} />
          ) : null}
          <div style={{position: 'absolute', left: r.x + r.w / 2, top: FY - 86, translate: `calc(-50% + ${jitter}px) 0px`, scale: String(pop), textAlign: 'center'}}>
            <div style={{display: 'inline-block', padding: '10px 24px', borderRadius: 18, background: 'rgba(6,7,16,0.86)', border: '2px solid rgba(255,255,255,0.12)',
              fontFamily: FONT.display, fontWeight: 900, fontSize: 46, color: C.white, letterSpacing: '0.02em'}}>{l.name}</div>
          </div>
          <div style={{position: 'absolute', left: r.x + r.w / 2, top: FY + 12, translate: `calc(-50% + ${jitter}px) 0px`, scale: String(pop2)}}>
            <div style={{display: 'inline-block', padding: '8px 22px 12px', borderRadius: 14, background: off ? C.pink : C.gold,
              fontFamily: FONT.pixel, fontWeight: 700, fontSize: 40, color: off ? C.white : 'rgb(10,12,26)', boxShadow: '0 8px 30px rgba(0,0,0,0.45)'}}>{off ? 'OFF' : 'ON'}</div>
          </div>
        </React.Fragment>
      );
    })}
  </div>
);
