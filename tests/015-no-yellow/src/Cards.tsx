import React from 'react';
import {backOut, C, easeInOut, easeOut, FONT, lerp, T, tw} from './theme';

type Card = {name: string; swatch: string; nameColor: string; rgb: [number, number, number]; cap: string; sub?: string; frame?: boolean};
const CARDS: Card[] = [
  {name: 'WHITE', swatch: 'rgb(255,255,255)', nameColor: 'rgb(255,255,255)', rgb: [100, 100, 100], cap: 'all 3 on'},
  {name: 'BLACK', swatch: 'rgb(0,0,0)', nameColor: 'rgb(150,156,185)', rgb: [0, 0, 0], cap: 'all 3 off'},
  {name: 'BROWN', swatch: 'rgb(140,69,0)', nameColor: 'rgb(214,124,52)', rgb: [55, 27, 0], cap: 'just dark orange', sub: 'next to something brighter', frame: true},
  {name: 'MAGENTA', swatch: 'rgb(255,0,255)', nameColor: 'rgb(255,80,236)', rgb: [100, 0, 100], cap: 'not in the rainbow', sub: 'no wavelength. your brain invents it'},
];
const OFF = [[46, 12, 20], [10, 36, 20], [12, 18, 50]];
const FULL = [[255, 52, 64], [52, 255, 110], [60, 110, 255]];
const VALUE_COL = ['rgb(255,96,108)', 'rgb(90,245,140)', 'rgb(110,150,255)'];

const CardView: React.FC<{t: number; card: Card; start: number; end: number; idx: number}> = ({t, card, start, end, idx}) => {
  const inK = tw(t, start, 0.32, easeOut);
  const outK = tw(t, end - 0.2, 0.2, easeInOut);
  if (inK <= 0 || outK >= 1) return null;
  const dx = lerp(140, 0, inK) + lerp(0, -140, outK);
  const op = Math.min(inK, 1 - outK);
  const sw = tw(t, start + 0.05, 0.45, backOut);
  return (
    <div style={{position: 'absolute', inset: 0, opacity: op, translate: `${dx}px 0px`}}>
      <div style={{position: 'absolute', top: 470, width: 1080, textAlign: 'center', fontFamily: FONT.display, fontWeight: 900, fontSize: 124,
        letterSpacing: '-0.02em', color: card.nameColor, textShadow: '0 8px 40px rgba(0,0,0,0.6)'}}>{card.name}</div>
      {/* swatch */}
      <div style={{position: 'absolute', left: 120, top: 690, width: 340, height: 340, borderRadius: 40, background: card.swatch, scale: String(sw),
        border: card.frame ? '22px solid rgb(246,246,250)' : card.name === 'BLACK' ? '3px solid rgba(150,156,185,0.5)' : 'none',
        boxSizing: 'border-box', boxShadow: card.name === 'WHITE' ? '0 0 70px rgba(255,255,255,0.35)' : card.name === 'MAGENTA' ? '0 0 70px rgba(255,0,255,0.4)' : '0 20px 60px rgba(0,0,0,0.5)'}} />
      {/* the pixel: 3 emitters */}
      {[0, 1, 2].map((k) => {
        const on = tw(t, start + 0.18 + k * 0.08, 0.3, easeOut) * (card.rgb[k] / 100);
        const c = OFF[k].map((o, j) => Math.round(o + (FULL[k][j] - o) * on));
        const col = `rgb(${c[0]},${c[1]},${c[2]})`;
        return (
          <React.Fragment key={k}>
            <div style={{position: 'absolute', left: 540 + k * 124, top: 690, width: 104, height: 340, borderRadius: 28, background: col,
              boxShadow: on > 0.05 ? `0 0 ${50 * on}px ${8 * on}px rgba(${FULL[k].join(',')},${0.7 * on})` : 'none'}} />
            <div style={{position: 'absolute', left: 540 + k * 124 + 52, top: 1052, translate: '-50% 0px', fontFamily: FONT.mono, fontWeight: 700, fontSize: 34,
              color: card.rgb[k] > 0 ? VALUE_COL[k] : 'rgba(150,156,185,0.6)'}}>{card.rgb[k]}%</div>
          </React.Fragment>
        );
      })}
      <div style={{position: 'absolute', top: 1128, width: 1080, textAlign: 'center', fontFamily: FONT.display, fontWeight: 800, fontSize: 58, color: C.white}}>{card.cap}</div>
      {card.sub ? (
        <div style={{position: 'absolute', top: 1206, width: 1080, textAlign: 'center', fontFamily: FONT.display, fontWeight: 700, fontSize: 36, color: C.muted,
          opacity: tw(t, start + 0.35, 0.3, easeOut)}}>{card.sub}</div>
      ) : null}
      {/* progress */}
      <div style={{position: 'absolute', top: 1300, width: 1080, display: 'flex', justifyContent: 'center', gap: 16}}>
        {CARDS.map((_, i) => (
          <div key={i} style={{width: 22, height: 22, borderRadius: 5, background: i === idx ? C.gold : 'rgba(150,156,185,0.3)'}} />
        ))}
      </div>
    </div>
  );
};

export const Cards: React.FC<{t: number}> = ({t}) => {
  if (t < T.cards[0] - 0.1 || t > T.cardsEnd + 0.1) return null;
  return (
    <>
      {CARDS.map((card, i) => (
        <CardView key={card.name} t={t} card={card} idx={i} start={T.cards[i]} end={i === CARDS.length - 1 ? T.cardsEnd : T.cards[i] + T.cardDur + 0.05} />
      ))}
    </>
  );
};

const CTA_COLS = ['rgb(255,79,176)', 'rgb(90,200,255)', 'rgb(150,100,255)', 'rgb(255,138,61)', 'rgb(61,255,176)', 'rgb(255,61,90)'];

export const CtaSwatches: React.FC<{t: number}> = ({t}) => {
  if (t < T.cta) return null;
  return (
    <div style={{position: 'absolute', top: 1418, width: 1080, display: 'flex', justifyContent: 'center', gap: 26, opacity: 1 - tw(t, T.loop - 0.1, 0.3, easeInOut)}}>
      {CTA_COLS.map((c, i) => {
        const k = tw(t, T.cta + 0.25 + i * 0.07, 0.4, backOut);
        const bob = Math.max(0, Math.sin((t - T.cta) * Math.PI * 2 * 0.9 - i * 0.7)) * 22;
        return (
          <div key={i} style={{width: 96, height: 96, borderRadius: 22, background: c, scale: String(Math.max(0, k)), translate: `0px ${-bob}px`,
            boxShadow: `0 0 30px ${c}`}} />
        );
      })}
    </div>
  );
};
