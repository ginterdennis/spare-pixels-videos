import React from 'react';
import {C, FONT, OW} from './theme';
import {ClothesPile} from './Person';

export const NEIGHBOUR_LAUNDRY = [C.pink, C.lilac, C.coral, C.pink, C.sky];
export const JONAS_LAUNDRY = [C.gold, C.navy, C.white, C.goldDark, C.teal];

export type WasherState = 'running' | 'done' | 'idle';

/** Front-loading washing machine. Local origin = centre of its feet on the floor. 330 x 410 at s = 1. */
export const Washer: React.FC<{
  x: number; y: number; s?: number; t: number; state: WasherState;
  drum?: string[]; // clothes visible through the door
  display?: string;
  pile?: string[] | null; // clothes heaped on top
  pileK?: number; // 0..1 grow-in of the pile
  sensor?: number; // 0..1 sensor box on top (part 2)
  sensorBlink?: boolean;
  qr?: number; // 0..1 QR sticker
  sock?: boolean;
  ow?: number;
}> = ({x, y, s = 1, t, state, drum = [], display, pile = null, pileK = 1, sensor = 0, sensorBlink = false, qr = 0, sock = false, ow = OW}) => {
  const sw = ow / s;
  const run = state === 'running';
  const shake = run ? 3.2 * Math.sin(t * 47) + 1.6 * Math.sin(t * 71) : 0;
  const tilt = run ? 0.5 * Math.sin(t * 39) : 0;
  const rot = run ? t * 520 : 0;
  const disp = display ?? (run ? 'RUN' : state === 'done' ? 'END' : '- -');
  const drumR = 98;
  return (
    <g transform={`translate(${x},${y}) scale(${s})`}>
      {run && (
        <g stroke={C.ink} strokeWidth={sw * 0.9} strokeLinecap="round" fill="none" opacity={0.7 + 0.3 * Math.sin(t * 30)}>
          <path d="M -200 -330 q -14 30 0 60" />
          <path d="M -224 -310 q -10 20 0 40" />
          <path d="M 200 -330 q 14 30 0 60" />
          <path d="M 224 -310 q 10 20 0 40" />
        </g>
      )}
      <g transform={`translate(${shake},0) rotate(${tilt},0,0)`}>
        {/* feet */}
        <rect x={-150} y={-14} width={40} height={16} rx={5} fill={C.ink} />
        <rect x={110} y={-14} width={40} height={16} rx={5} fill={C.ink} />
        {/* body */}
        <rect x={-165} y={-420} width={330} height={410} rx={28} fill={C.machine} stroke={C.ink} strokeWidth={sw} />
        <path d={`M -165 -345 L 165 -345`} stroke={C.ink} strokeWidth={sw * 0.8} />
        {/* panel */}
        <rect x={-142} y={-404} width={78} height={42} rx={10} fill={C.metal} stroke={C.ink} strokeWidth={sw * 0.8} />
        <circle cx={-20} cy={-383} r={20} fill={C.white} stroke={C.ink} strokeWidth={sw * 0.8} />
        <path d={`M -20 -383 L ${-20 + 13 * Math.cos(run ? t * 2 : -0.8)} ${-383 + 13 * Math.sin(run ? t * 2 : -0.8)}`} stroke={C.ink} strokeWidth={sw * 0.8} strokeLinecap="round" />
        <rect x={22} y={-402} width={124} height={40} rx={8} fill={C.ink} />
        <text x={84} y={-372} textAnchor="middle" fontFamily={FONT.pixel} fontWeight={700} fontSize={25} fill={state === 'done' ? C.gold : run ? C.tealLight : '#8C93B8'}>{disp}</text>
        {/* door */}
        <circle cx={0} cy={-178} r={128} fill={C.metal} stroke={C.ink} strokeWidth={sw} />
        <circle cx={0} cy={-178} r={drumR + 4} fill={C.ink} />
        <clipPath id={`glass-${x}-${y}`}>
          <circle cx={0} cy={-178} r={drumR} />
        </clipPath>
        <g clipPath={`url(#glass-${x}-${y})`}>
          <rect x={-drumR} y={-178 - drumR} width={drumR * 2} height={drumR * 2} fill={state === 'idle' && drum.length === 0 ? '#5E6A88' : '#4A587D'} />
          {drum.length > 0 && (
            run ? (
              <g transform={`rotate(${rot},0,-178)`}>
                {drum.map((c, i) => {
                  const a = (i / drum.length) * Math.PI * 2;
                  return <circle key={i} cx={52 * Math.cos(a)} cy={-178 + 52 * Math.sin(a)} r={40} fill={c} stroke={C.ink} strokeWidth={sw * 0.8} />;
                })}
              </g>
            ) : (
              <g>
                {drum.map((c, i) => {
                  const cx = -70 + (140 * i) / Math.max(1, drum.length - 1);
                  const cy = -178 + 52 - ((i * 37) % 3) * 22;
                  return <ellipse key={i} cx={cx} cy={cy} rx={52} ry={44} fill={c} stroke={C.ink} strokeWidth={sw * 0.8} />;
                })}
                {drum.map((c, i) => i < 3 ? <ellipse key={`u${i}`} cx={-40 + 45 * i} cy={-178 - 8 - (i % 2) * 14} rx={42} ry={36} fill={drum[(i + 2) % drum.length]} stroke={C.ink} strokeWidth={sw * 0.8} /> : null)}
              </g>
            )
          )}
          {/* glass shine */}
          <path d={`M -62 -238 A 82 82 0 0 1 22 -258`} stroke="#FFFFFF" strokeOpacity={0.55} strokeWidth={14} fill="none" strokeLinecap="round" />
          {run && <rect x={-drumR} y={-178 + 10} width={drumR * 2} height={drumR} fill={C.sky} opacity={0.35} />}
        </g>
        <circle cx={0} cy={-178} r={drumR + 4} fill="none" stroke={C.ink} strokeWidth={sw} />
        <rect x={112} y={-200} width={18} height={44} rx={6} fill={C.metal} stroke={C.ink} strokeWidth={sw * 0.8} />
        {/* wet sock hanging out of the door seal */}
        {sock && (
          <path d="M 40 -88 q 6 40 -4 70 q -6 18 18 18 q 24 0 18 -22 q -6 -30 -4 -62 Z" fill={C.pink} stroke={C.ink} strokeWidth={sw * 0.9} strokeLinejoin="round" />
        )}
        {/* QR sticker (part 2) */}
        {qr > 0 && (
          <g opacity={qr} transform={`translate(-138,-318) scale(${0.6 + 0.4 * qr})`}>
            <rect x={0} y={0} width={70} height={70} rx={6} fill={C.white} stroke={C.ink} strokeWidth={sw * 0.8} />
            {[[8, 8], [44, 8], [8, 44]].map(([qx, qy], i) => (
              <g key={i}><rect x={qx} y={qy} width={18} height={18} fill={C.ink} /><rect x={qx + 4} y={qy + 4} width={10} height={10} fill={C.white} /><rect x={qx + 6} y={qy + 6} width={6} height={6} fill={C.ink} /></g>
            ))}
            {[[32, 12], [36, 30], [30, 40], [46, 36], [52, 48], [40, 52], [56, 58], [32, 58], [46, 30]].map(([qx, qy], i) => <rect key={`d${i}`} x={qx} y={qy} width={6} height={6} fill={C.ink} />)}
          </g>
        )}
      </g>
      {/* sensor box on top (part 2) */}
      {sensor > 0 && (
        <g transform={`translate(${shake + 70},${-420 - 4}) scale(${sensor})`}>
          <rect x={-44} y={-44} width={88} height={46} rx={12} fill={C.gold} stroke={C.ink} strokeWidth={sw} />
          <circle cx={22} cy={-21} r={8} fill={sensorBlink ? C.green : C.ink} stroke={C.ink} strokeWidth={sw * 0.6} />
          <rect x={-30} y={-28} width={30} height={14} rx={4} fill={C.ink} opacity={0.75} />
        </g>
      )}
      {/* clothes heaped on top */}
      {pile && pileK > 0 && (
        <g transform={`translate(${-40 + shake},-420) scale(${pileK})`}>
          <ClothesPile colors={pile} w={210} h={46} sw={sw} seed={3} />
        </g>
      )}
    </g>
  );
};

/** Wall clock with a fast-turning minute hand. */
export const Clock: React.FC<{x: number; y: number; r?: number; minutes: number; ow?: number}> = ({x, y, r = 56, minutes, ow = OW}) => {
  const am = (minutes / 60) * Math.PI * 2 - Math.PI / 2;
  const ah = ((minutes / 60 + 9) / 12) * Math.PI * 2 - Math.PI / 2;
  return (
    <g transform={`translate(${x},${y})`}>
      <circle r={r} fill={C.white} stroke={C.ink} strokeWidth={ow} />
      {Array.from({length: 12}, (_, i) => {
        const a = (i / 12) * Math.PI * 2;
        return <line key={i} x1={Math.cos(a) * (r - 10)} y1={Math.sin(a) * (r - 10)} x2={Math.cos(a) * (r - 18)} y2={Math.sin(a) * (r - 18)} stroke={C.ink} strokeWidth={i % 3 === 0 ? 5 : 3} strokeLinecap="round" />;
      })}
      <line x1={0} y1={0} x2={Math.cos(ah) * r * 0.45} y2={Math.sin(ah) * r * 0.45} stroke={C.ink} strokeWidth={7} strokeLinecap="round" />
      <line x1={0} y1={0} x2={Math.cos(am) * r * 0.7} y2={Math.sin(am) * r * 0.7} stroke={C.coral} strokeWidth={5} strokeLinecap="round" />
      <circle r={6} fill={C.ink} />
    </g>
  );
};

/** Hand-written note taped to something. */
export const Note: React.FC<{x: number; y: number; text: string; rot?: number; k?: number; size?: number}> = ({x, y, text, rot = -6, k = 1, size = 34}) => (
  <g transform={`translate(${x},${y}) rotate(${rot}) scale(${k})`}>
    <rect x={-150} y={-56} width={300} height={112} fill="#FFF6C8" stroke={C.ink} strokeWidth={OW * 0.8} />
    <rect x={-40} y={-72} width={80} height={28} fill={C.tealLight} opacity={0.85} transform="rotate(4)" />
    <text x={0} y={12} textAnchor="middle" fontFamily={FONT.script} fontSize={size} fill={C.ink}>{text}</text>
  </g>
);

/** Basement room: back wall, pipes, high window, bulb, tiled floor. Floor line at FLOOR_Y. */
export const FLOOR_Y = 1160;
export const BasementRoom: React.FC<{t: number; children?: React.ReactNode; bulbOn?: boolean}> = ({t, children}) => {
  const sway = 5 * Math.sin(t * 2.1);
  return (
    <g>
      <rect x={0} y={0} width={1080} height={FLOOR_Y} fill={C.basement} />
      {/* high basement window */}
      <rect x={120} y={420} width={250} height={92} rx={8} fill="#BFD7E4" stroke={C.ink} strokeWidth={OW} />
      <line x1={245} y1={420} x2={245} y2={512} stroke={C.ink} strokeWidth={OW} />
      <path d="M 126 498 q 30 -30 60 -10 q 30 -26 60 0 q 40 -24 70 6 L 364 506 L 126 506 Z" fill={C.green} opacity={0.6} />
      {/* pipes */}
      <rect x={-10} y={372} width={1100} height={22} fill={C.metal} stroke={C.ink} strokeWidth={OW} />
      {[180, 520, 860].map((px) => <rect key={px} x={px - 10} y={362} width={20} height={42} rx={4} fill={C.wallDark} stroke={C.ink} strokeWidth={OW * 0.8} />)}
      <rect x={950} y={372} width={22} height={FLOOR_Y - 372} fill={C.metal} stroke={C.ink} strokeWidth={OW} />
      {/* bulb */}
      <g transform={`rotate(${sway},640,330)`}>
        <line x1={640} y1={330} x2={640} y2={470} stroke={C.ink} strokeWidth={4} />
        <circle cx={640} cy={490} r={22} fill="#FFE7A0" stroke={C.ink} strokeWidth={OW * 0.8} />
        <rect x={628} y={462} width={24} height={16} fill={C.metal} stroke={C.ink} strokeWidth={OW * 0.6} />
      </g>
      {/* floor */}
      <rect x={0} y={FLOOR_Y} width={1080} height={1920 - FLOOR_Y} fill={C.floor} />
      <line x1={0} y1={FLOOR_Y} x2={1080} y2={FLOOR_Y} stroke={C.ink} strokeWidth={OW} />
      {[1210, 1290, 1400, 1560, 1760].map((ly) => <line key={ly} x1={0} y1={ly} x2={1080} y2={ly} stroke={C.floorLine} strokeWidth={3} />)}
      {children}
    </g>
  );
};
