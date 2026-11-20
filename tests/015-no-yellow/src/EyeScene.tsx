import React from 'react';
import {backOut, C, easeInOut, easeOut, FONT, lerp, T, tw} from './theme';

const PANEL_X = 80;
const PANEL_W = 860;
const PANEL_H = 330;
// relative L / M / S cone response to 580 nm light (approximate; same for the matched red + green mix)
const CONES = [
  {h: 0.92, c: 'rgb(255,90,106)'},
  {h: 0.62, c: 'rgb(90,255,143)'},
  {h: 0.03, c: 'rgb(90,140,255)'},
];
const SPECTRUM =
  'linear-gradient(90deg, #6a1fd6 0%, #2f5bff 22%, #18c8ff 34%, #2cff6a 44%, #b8ff2a 56%, #ffe600 62.5%, #ff8a1a 72%, #ff2a2a 84%, #8a0010 100%)';

const Label: React.FC<{x: number; y: number; children: React.ReactNode; color?: string}> = ({x, y, children, color = C.muted}) => (
  <div style={{position: 'absolute', left: x, top: y, fontFamily: FONT.display, fontWeight: 700, fontSize: 23, letterSpacing: '0.2em', color, whiteSpace: 'nowrap'}}>{children}</div>
);

const Panel: React.FC<{t: number; top: number; kind: 'real' | 'screen'; inAt: number; fillAt: number}> = ({t, top, kind, inAt, fillAt}) => {
  const k = tw(t, inAt, 0.45, easeOut);
  const beam = tw(t, inAt + 0.15, 0.45, easeInOut);
  const same = tw(t, T.same, 0.5, easeOut);
  const id = `clip-${kind}`;
  const flow = -(t - inAt) * 260;
  return (
    <div style={{position: 'absolute', left: PANEL_X, top, width: PANEL_W, height: PANEL_H, opacity: k, translate: `0px ${lerp(40, 0, k)}px`,
      borderRadius: 36, background: 'rgba(255,255,255,0.035)', border: '2px solid rgba(255,255,255,0.08)'}}>
      <Label x={40} y={34}>{kind === 'real' ? 'REAL YELLOW LIGHT' : 'YOUR SCREEN'}</Label>
      <Label x={560} y={34}>EYE SENSORS</Label>

      {/* source */}
      {kind === 'real' ? (
        <>
          <div style={{position: 'absolute', left: 44, top: 176, width: 250, height: 30, borderRadius: 8, background: SPECTRUM, opacity: 0.35}} />
          <div style={{position: 'absolute', left: 44 + 250 * 0.6 - 14, top: 170, width: 28, height: 42, borderRadius: 8, background: '#ffe600',
            boxShadow: '0 0 26px 6px rgba(255,230,0,0.65)'}} />
          <div style={{position: 'absolute', left: 44 + 250 * 0.6, top: 124, translate: '-50% 0px', fontFamily: FONT.mono, fontWeight: 700, fontSize: 26, color: C.gold}}>580 nm</div>
          <Label x={44} y={236} color="rgba(150,156,185,0.8)">ONE WAVELENGTH</Label>
        </>
      ) : (
        <>
          {[0, 1].map((i) => (
            <div key={i} style={{position: 'absolute', left: 120 + i * 58, top: 128, width: 40, height: 118, borderRadius: 12,
              background: i === 0 ? C.red : C.green, boxShadow: `0 0 28px 6px ${i === 0 ? 'rgba(255,52,64,0.6)' : 'rgba(52,255,110,0.55)'}`}} />
          ))}
          <div style={{position: 'absolute', left: 236, top: 128, width: 40, height: 118, borderRadius: 12, background: 'rgb(12,18,50)'}} />
          <Label x={44} y={268} color="rgba(150,156,185,0.8)">RED + GREEN, NO YELLOW</Label>
        </>
      )}

      {/* light beams */}
      <svg width={PANEL_W} height={PANEL_H} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
        <defs>
          <clipPath id={id}>
            <rect x={0} y={0} width={lerp(300, 540, beam)} height={PANEL_H} />
          </clipPath>
        </defs>
        <g clipPath={`url(#${id})`} style={{filter: 'drop-shadow(0 0 10px rgba(255,255,255,0.35))'}}>
          {kind === 'real' ? (
            <path d="M 300 191 L 500 191" stroke="#ffe600" strokeWidth={12} strokeLinecap="round" strokeDasharray="30 16" strokeDashoffset={flow} fill="none" />
          ) : (
            <>
              <path d="M 290 165 C 380 165, 420 191, 500 191" stroke="rgb(255,52,64)" strokeWidth={11} strokeLinecap="round" strokeDasharray="30 16" strokeDashoffset={flow} fill="none" />
              <path d="M 290 220 C 380 220, 420 191, 500 191" stroke="rgb(52,255,110)" strokeWidth={11} strokeLinecap="round" strokeDasharray="30 16" strokeDashoffset={flow + 15} fill="none" />
            </>
          )}
        </g>
      </svg>

      {/* cone bars */}
      {CONES.map((c, i) => {
        const f = tw(t, fillAt + i * 0.1, 0.7, easeOut);
        const x = 560 + i * 96;
        return (
          <React.Fragment key={i}>
            <div style={{position: 'absolute', left: x, top: 92, width: 62, height: 180, borderRadius: 16, background: 'rgba(255,255,255,0.07)', overflow: 'hidden'}}>
              <div style={{position: 'absolute', left: 0, bottom: 0, width: 62, height: Math.max(6, 180 * c.h * f), borderRadius: 16, background: c.c,
                boxShadow: `0 0 24px ${c.c}`}} />
            </div>
            <div style={{position: 'absolute', left: x + 31 - 11, top: 288, width: 22, height: 22, borderRadius: 11, background: c.c, opacity: 0.9}} />
          </React.Fragment>
        );
      })}
      {/* "same" outline */}
      <div style={{position: 'absolute', left: 538, top: 74, width: 296, height: 252, borderRadius: 24, border: `4px dashed ${C.gold}`, opacity: same,
        scale: String(lerp(1.15, 1, same))}} />
    </div>
  );
};

export const EyeScene: React.FC<{t: number}> = ({t}) => {
  const vis = Math.min(tw(t, T.eyeStart, 0.3, easeOut), 1 - tw(t, T.eyeEnd, 0.3, easeInOut));
  if (vis <= 0) return null;
  const st = tw(t, T.same, 0.45, backOut);
  const ring = tw(t, T.same, 0.7, easeOut);
  return (
    <div style={{position: 'absolute', inset: 0, opacity: vis, translate: `0px ${lerp(0, -40, tw(t, T.eyeEnd, 0.3, easeInOut))}px`}}>
      <Panel t={t} top={500} kind="real" inAt={T.p1In} fillAt={T.p1Fill} />
      <Panel t={t} top={1000} kind="screen" inAt={T.p2In} fillAt={T.p2Fill} />
      {st > 0 ? (
        <div style={{position: 'absolute', left: 540, top: 914, translate: '-50% -50%', scale: String(lerp(1.8, 1, Math.min(1, st))), rotate: `${lerp(-12, -3, Math.min(1, st))}deg`,
          opacity: Math.min(1, st * 1.5), display: 'flex', alignItems: 'center', gap: 18}}>
          <div style={{width: 80, height: 80, borderRadius: 40, background: C.gold, color: 'rgb(10,12,26)', fontFamily: FONT.display, fontWeight: 900, fontSize: 64,
            lineHeight: '78px', textAlign: 'center', boxShadow: `0 0 ${40 * (1 - ring) + 10}px rgba(255,211,107,0.8)`}}>=</div>
          <div style={{padding: '10px 26px 14px', borderRadius: 16, border: `3px solid ${C.gold}`, background: 'rgba(10,12,26,0.92)', fontFamily: FONT.pixel, fontWeight: 700,
            fontSize: 44, color: C.gold, whiteSpace: 'nowrap'}}>SAME SIGNAL</div>
        </div>
      ) : null}
    </div>
  );
};
