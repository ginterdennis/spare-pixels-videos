import React from 'react';
import {backOut, C, easeInOut, easeOut, FONT, lerp, OW, tw, nc, HARD_SHADOW} from './theme';
import {FLOOR_Y} from './Props';
import {useLabelSvg} from './UI';

/** Speech-bubble readout above the sensor: a live vibration trace + label. */
export const SensorBubble: React.FC<{t: number; amp: number; label: string; color: string; k: number}> = ({t, amp, label, color, k}) => {
  if (k <= 0) return null;
  const pts: string[] = [];
  for (let i = 0; i <= 120; i++) {
    const x = 30 + i * 2.5;
    const y = 74 + amp * (22 * Math.sin(i * 0.55 + t * 30) + 10 * Math.sin(i * 1.3 - t * 47));
    pts.push(`${i ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`);
  }
  return (
    <g transform={`translate(560,440) translate(210,214) scale(${lerp(0.6, 1, k)}) translate(-210,-214)`} opacity={Math.min(1, k * 1.5)}>
      <rect x={0} y={0} width={360} height={176} rx={22} fill={C.white} stroke={C.ink} strokeWidth={OW} />
      <path d="M 196 172 L 210 214 L 236 172 Z" fill={C.white} stroke={C.ink} strokeWidth={OW} strokeLinejoin="round" />
      <rect x={198} y={160} width={36} height={16} fill={C.white} />
      <rect x={22} y={26} width={316} height={96} rx={10} fill={C.ink} />
      <path d={pts.join(' ')} stroke={color} strokeWidth={5} fill="none" strokeLinejoin="round" />
      <text x={180} y={156} textAnchor="middle" fontFamily={FONT.pixel} fontWeight={700} fontSize={25} fill={C.ink}>{label}</text>
    </g>
  );
};

/** Jonas's flat on floor 4: window, picture, plant, couch. */
export const FlatRoom: React.FC<{t: number; children?: React.ReactNode}> = ({children}) => (
  <g>
    <rect x={0} y={0} width={1080} height={FLOOR_Y} fill={C.wall} />
    {/* window with rooftops */}
    <rect x={96} y={380} width={300} height={250} rx={10} fill={nc('#BFDDEA', '#26306A')} stroke={C.ink} strokeWidth={OW} />
    <path d="M 102 560 L 160 520 L 210 548 L 210 600 L 102 600 Z" fill={C.coral} opacity={0.75} />
    <path d="M 220 600 L 220 530 L 300 490 L 390 530 L 390 600 Z" fill={C.navy} opacity={0.5} />
    <rect x={102} y={590} width={288} height={34} fill={C.green} opacity={0.6} />
    <line x1={246} y1={380} x2={246} y2={630} stroke={C.ink} strokeWidth={OW} />
    <line x1={96} y1={505} x2={396} y2={505} stroke={C.ink} strokeWidth={OW} />
    <rect x={80} y={622} width={332} height={20} rx={6} fill={C.wallDark} stroke={C.ink} strokeWidth={OW * 0.8} />
    {/* picture */}
    <rect x={430} y={420} width={110} height={140} fill={C.white} stroke={C.ink} strokeWidth={OW * 0.8} />
    <circle cx={485} cy={470} r={22} fill={C.gold} />
    <path d="M 442 545 L 478 505 L 505 530 L 530 512 L 530 548 L 442 548 Z" fill={C.teal} />
    {/* floor */}
    <rect x={0} y={FLOOR_Y} width={1080} height={1920 - FLOOR_Y} fill={nc('#D3BB95', '#17112F')} />
    <line x1={0} y1={FLOOR_Y} x2={1080} y2={FLOOR_Y} stroke={C.ink} strokeWidth={OW} />
    {[1230, 1320, 1440, 1600, 1800].map((y) => <line key={y} x1={0} y1={y} x2={1080} y2={y} stroke={nc('#BDA27A', '#2B2152')} strokeWidth={3} />)}
    {/* plant */}
    <rect x={30} y={FLOOR_Y - 110} width={80} height={110} rx={8} fill={C.coral} stroke={C.ink} strokeWidth={OW} />
    {[[-30, -60], [0, -90], [30, -55], [-14, -120], [18, -128]].map(([dx, dy], i) => (
      <ellipse key={i} cx={70 + dx} cy={FLOOR_Y - 110 + dy} rx={22} ry={44} fill={C.green} stroke={C.ink} strokeWidth={OW * 0.8} transform={`rotate(${dx * 0.9},${70 + dx},${FLOOR_Y - 110 + dy})`} />
    ))}
    {/* couch */}
    <rect x={120} y={FLOOR_Y - 330} width={420} height={170} rx={36} fill={C.teal} stroke={C.ink} strokeWidth={OW} />
    {children}
  </g>
);

/** Couch seat + armrests drawn in front of the sitter. */
export const CouchFront: React.FC = () => (
  <g>
    <rect x={130} y={FLOOR_Y - 196} width={400} height={92} rx={22} fill={nc('#3BA29B', '#1F7A66')} stroke={C.ink} strokeWidth={OW} />
    <rect x={96} y={FLOOR_Y - 250} width={72} height={200} rx={28} fill={C.teal} stroke={C.ink} strokeWidth={OW} />
    <rect x={500} y={FLOOR_Y - 250} width={72} height={200} rx={28} fill={C.teal} stroke={C.ink} strokeWidth={OW} />
    <rect x={140} y={FLOOR_Y - 56} width={24} height={56} fill={C.ink} />
    <rect x={508} y={FLOOR_Y - 56} width={24} height={56} fill={C.ink} />
  </g>
);

export type PhoneStatus = {label: string; sub: string; color: string; progress: number; size?: number};
export type Banner = {title: string; sub: string; at: number};

/** The app on Jonas's phone, shown big on the right. */
export const Phone: React.FC<{t: number; at: number; until: number; status: PhoneStatus; banners?: Banner[]; statusAt?: number; x?: number; rot?: number}> = ({t, at, until, status, banners = [], statusAt = -1, x = 590, rot = 3}) => {
  const lf = useLabelSvg();
  if (t < at || t > until + 0.25) return null;
  const k = tw(t, at, 0.4, backOut);
  const o = 1 - tw(t, until, 0.22, easeInOut);
  const sk = statusAt > 0 ? tw(t, statusAt, 0.35, backOut) : 1;
  const R = 104;
  const circ = 2 * Math.PI * R;
  return (
    <div style={{position: 'absolute', left: x, top: 400, width: 330, height: 660, opacity: o, transform: `translateY(${lerp(80, 0, k)}px) scale(${lerp(0.85, 1, k)}) rotate(${rot}deg)`, transformOrigin: '50% 100%'}}>
      <div style={{position: 'absolute', inset: 0, background: C.ink, borderRadius: 54, boxShadow: HARD_SHADOW}} />
      <div style={{position: 'absolute', left: 14, top: 14, right: 14, bottom: 14, background: C.paper, borderRadius: 42, overflow: 'hidden'}}>
        <div style={{position: 'absolute', left: 112, top: 12, width: 78, height: 22, borderRadius: 11, background: C.ink}} />
        <div style={{position: 'absolute', left: 0, right: 0, top: 70, textAlign: 'center', fontFamily: lf.family, fontWeight: lf.weight, fontSize: 22, color: C.ink, letterSpacing: 1}}>HOUSE WASHER</div>
        <svg width={302} height={300} style={{position: 'absolute', left: 0, top: 112}}>
          <circle cx={151} cy={140} r={R} fill="none" stroke={C.wallDark} strokeWidth={22} />
          <circle cx={151} cy={140} r={R} fill="none" stroke={status.color} strokeWidth={22} strokeLinecap="round" strokeDasharray={`${circ * status.progress} ${circ}`} transform="rotate(-90 151 140)" />
        </svg>
        <div style={{position: 'absolute', left: 0, right: 0, top: 206, textAlign: 'center', transform: `scale(${lerp(0.6, 1, sk)})`}}>
          <div style={{fontFamily: FONT.sans, fontWeight: 900, fontSize: status.size ?? 58, color: status.color, letterSpacing: '-0.02em', lineHeight: '60px'}}>{status.label}</div>
        </div>
        <div style={{position: 'absolute', left: 20, right: 20, top: 430, textAlign: 'center', fontFamily: FONT.sans, fontWeight: 800, fontSize: 30, lineHeight: '38px', color: C.ink}}>{status.sub}</div>
        {banners.map((b, i) => {
          if (t < b.at) return null;
          const bk = tw(t, b.at, 0.35, easeOut);
          const later = banners.slice(i + 1).some((x) => t >= x.at);
          if (later) return null;
          return (
            <div key={i} style={{position: 'absolute', left: 14, right: 14, top: lerp(-160, 52, bk), background: C.white, border: `5px solid ${C.ink}`, borderRadius: 22, padding: '12px 14px', display: 'flex', gap: 12, alignItems: 'center', boxShadow: `5px 5px 0 ${C.ink}`}}>
              <div style={{width: 46, height: 46, borderRadius: 12, background: C.gold, border: `4px solid ${C.ink}`, flexShrink: 0}} />
              <div>
                <div style={{fontFamily: FONT.sans, fontWeight: 900, fontSize: 25, lineHeight: '29px', color: C.ink}}>{b.title}</div>
                <div style={{fontFamily: FONT.sans, fontWeight: 700, fontSize: 20, lineHeight: '24px', color: C.navy, opacity: 0.75}}>{b.sub}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

/** Scan beam from the phone to the QR sticker. */
export const ScanBeam: React.FC<{t: number; at: number; dur: number; from: {x: number; y: number}; to: {x: number; y: number}}> = ({t, at, dur, from, to}) => {
  if (t < at || t > at + dur) return null;
  const k = (t - at) / dur;
  const o = Math.sin(Math.PI * k);
  return (
    <g opacity={o}>
      <path d={`M ${from.x} ${from.y} L ${to.x - 40} ${to.y - 40} L ${to.x + 40} ${to.y + 40} Z`} fill={C.gold} opacity={0.45} />
      <rect x={to.x - 46} y={to.y - 46 + 92 * ((k * 3) % 1)} width={92} height={6} fill={C.coral} />
    </g>
  );
};
