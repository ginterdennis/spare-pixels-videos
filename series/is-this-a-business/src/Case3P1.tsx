import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import T from './c3p1.json';
import {backOut, C, easeInOut, easeOut, FONT, FPS, lerp, OW, tw, BG_FILE, nc, HARD_SHADOW, LOOK} from './theme';
import {JONAS, Look, Person} from './Person';
import {Clock, FLOOR_Y} from './Props';
import {Landing} from './Case2P1';
import {Cap, Captions, Counter, Em, EndCard, LabelFont, SeriesPill, Tag} from './UI';

// Case 3 "Locked out": Saturday 23:10, Jonas takes the trash out in his socks, the door falls shut behind him,
// keys inside. The locksmith wants €120, Saturday night doubles it. 70 minutes in the stairwell, the phone dies.
// The door wasn't even locked, it just fell shut: €240. Idea: the kiosk downstairs keeps your spare key, €2 a month.
// Prices: ADAC (June 2026) simple opening by day 80-150 euros, night/weekend 150-250 euros, surcharges 50-100 %.
const inS = (t: number, s: number[]) => t >= s[0] && t < s[1];
const easeIn = (x: number) => x * x;

const SOCKS: Look = {...JONAS, shoes: nc('#C9CFDA', '#ECE8FF')};
const LOCKSMITH: Look = {hoodie: nc('#46557A', '#5B4BB0'), pants: C.ink, hair: C.hair, skin: C.skin2, shoes: C.ink, hairStyle: 'cap', cap: C.coral};
const KIOSK: Look = {hoodie: C.lilac, pants: C.navy, hair: '#2B1D16', skin: C.skin3, shoes: C.ink, hairStyle: 'short'};
const BAG = nc('#3D4257', '#2E2752');

const billAt = (t: number) => {
  if (t < T.q1) return 0;
  if (t < T.q2) return Math.round(lerp(0, 120, tw(t, T.q1, 0.35, easeOut)));
  return t < T.dbl ? 120 : Math.round(lerp(120, 240, tw(t, T.dbl, 0.35, easeOut)));
};

const CAPS: Cap[] = [
  {at: 0, until: T.reveal - 0.05, lines: ['How one door click', <Em>became €240.</Em>]},
  {at: T.reveal, until: T.sA[1] - 0.05, lines: ['Locked out.', <Em>Keys inside.</Em>]},
  {at: T.sB[0] + 0.1, until: T.q2 - 0.05, lines: ['The locksmith', <Em>wants €120.</Em>]},
  {at: T.q2, until: T.sB[1] - 0.05, lines: ['Saturday night?', <Em>Double.</Em>]},
  {at: T.sC[0] + 0.1, until: T.die - 0.05, lines: ['He waits in his socks.', <Em>70 minutes.</Em>]},
  {at: T.die, until: T.sC[1] - 0.05, lines: ['His phone', <Em>dies.</Em>]},
  {at: T.open, until: T.bill - 0.05, lines: ["The door wasn't", <Em>even locked.</Em>]},
  {at: T.bill, until: T.sD[1] - 0.05, lines: ['It just fell shut.', <Em>€240, please.</Em>]},
  {at: T.sE[0] + 0.1, until: T.rcpt - 0.05, lines: ['Idea: the kiosk downstairs', <Em>keeps your spare key.</Em>]},
  {at: T.rcpt, until: T.ask - 0.05, lines: ['€2 a month.', <Em>One lockout = 10 years.</Em>]},
];

/** A house key (local origin = ring centre), hanging down. */
const Key: React.FC<{x: number; y: number; s?: number; rot?: number; col?: string}> = ({x, y, s = 1, rot = 0, col = C.gold}) => (
  <g transform={`translate(${x},${y}) rotate(${rot}) scale(${s})`}>
    <circle cx={0} cy={0} r={17} fill="none" stroke={C.ink} strokeWidth={13} />
    <circle cx={0} cy={0} r={17} fill="none" stroke={col} strokeWidth={7} />
    <path d="M -9 16 L 9 16 L 9 72 L 18 72 L 18 82 L 9 82 L 9 92 L 18 92 L 18 102 L -9 102 Z" fill={col} stroke={C.ink} strokeWidth={4} strokeLinejoin="round" />
  </g>
);

/** Keys on the hook inside flat 4A (visible while the door is open). */
const InsideKeys: React.FC<{t: number}> = ({t}) => (
  <g>
    <rect x={208} y={756} width={96} height={20} rx={6} fill={nc('#8C6239', '#6B3FA0')} stroke={C.ink} strokeWidth={4} />
    <circle cx={256} cy={766} r={5} fill={C.metal} />
    <Key x={256} y={800} s={0.85} rot={4 * Math.sin(t * 6)} />
    <circle cx={256} cy={790} r={40} fill={C.gold} opacity={0.18 + 0.1 * Math.sin(t * 8)} />
  </g>
);

/** Rubber stamp. */
const Stamp: React.FC<{x: number; y: number; k: number; text: string; w: number; rot?: number; size?: number}> = ({x, y, k, text, w, rot = -9, size = 60}) =>
  k > 0 ? (
    <g transform={`translate(${x},${y}) rotate(${rot}) scale(${lerp(2.2, 1, k)})`} opacity={Math.min(1, k * 2)}>
      <rect x={-w / 2} y={-50} width={w} height={92} rx={12} fill={C.white} stroke={C.coral} strokeWidth={9} />
      <text x={0} y={22} textAnchor="middle" fontFamily={FONT.sans} fontWeight={900} fontSize={size} fill={C.coral}>{text}</text>
    </g>
  ) : null;

/** Trash bag standing on the floor (local origin = bottom centre). */
const Bag: React.FC<{x: number; y: number; s?: number}> = ({x, y, s = 1}) => (
  <g transform={`translate(${x},${y}) scale(${s})`}>
    <path d="M -62 0 Q -78 -70 -40 -112 L -14 -128 L -22 -150 L 22 -150 L 14 -128 L 40 -112 Q 78 -70 62 0 Z" fill={BAG} stroke={C.ink} strokeWidth={OW} strokeLinejoin="round" />
    <path d="M -30 -96 Q -40 -60 -34 -24" stroke={C.white} strokeWidth={6} fill="none" opacity={0.25} strokeLinecap="round" />
  </g>
);

/** Scene A (and the loop tail): the floor-4 landing, the door falls shut. */
const SceneA: React.FC<{t: number}> = ({t}) => {
  const openA = 0.8 * (1 - tw(t, -0.15, T.slam + 0.15, easeIn));
  const push = lerp(1.0, 1.08, tw(t, -0.5, 4.4, easeInOut));
  const shake = t > T.slam && t < T.slam + 0.3 ? 9 * Math.sin((t - T.slam) * 70) * (1 - (t - T.slam) / 0.3) : 0;
  const jx = lerp(330, 590, tw(t, -0.6, 1.1, easeOut));
  const walking = t < 0.45;
  const turned = t > T.slam + 0.25;
  const stamp = tw(t, T.reveal, 0.22, backOut);
  const xk = tw(t, T.xray, 0.35, backOut);
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(${shake},0) translate(360,900) scale(${push}) translate(-360,-900)`}>
        <Landing t={t} openA={openA} openB={0} insideA={<InsideKeys t={t} />}>
          {t >= T.slam + 0.1 && <Bag x={jx + 120} y={lerp(FLOOR_Y - 190, FLOOR_Y, tw(t, T.slam + 0.1, 0.22, easeIn))} s={0.8} />}
          <Person x={jx} y={FLOOR_Y} s={0.92} face={turned ? -1 : 1} look={SOCKS} walk={walking ? t * 9 + 20 : null} holding={t < T.slam + 0.1 ? BAG : null} expr={t >= T.reveal - 0.4 ? 'shock' : t > T.slam ? 'neutral' : 'happy'} />
          {xk > 0 && (
            <g transform={`translate(256,820) scale(${lerp(0.3, 1, xk)})`} opacity={Math.min(1, xk * 1.5)}>
              <circle r={104} fill={nc('#2A2F4F', '#1A1336')} stroke={C.coral} strokeWidth={9} strokeDasharray="22 12" />
              <rect x={-52} y={-60} width={104} height={22} rx={6} fill={nc('#8C6239', '#6B3FA0')} stroke={C.ink} strokeWidth={4} />
              <Key x={0} y={-26} s={1.1} rot={5 * Math.sin(t * 5)} />
            </g>
          )}
          <Stamp x={300} y={1010} k={stamp} text="LOCKED OUT" w={450} />
        </Landing>
      </g>
    </svg>
  );
};

/** Scene B: the call. Landing in the background, the phone big in front. */
const SceneB: React.FC<{t: number}> = ({t}) => {
  const settle = lerp(1.1, 1.02, tw(t, T.sB[0], 0.5, easeOut));
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(560,900) scale(${settle}) translate(-560,-900)`}>
        <Landing t={t} openA={0} openB={0}>
          <Bag x={740} y={FLOOR_Y} s={0.8} />
          <Person x={600} y={FLOOR_Y} s={0.92} face={-1} look={SOCKS} pose="phone" expr={t >= T.q2 ? 'shock' : 'tired'} />
        </Landing>
      </g>
      <rect x={0} y={0} width={1080} height={1920} fill={C.shade} opacity={(LOOK === 'neon' ? 2.4 : 1) * 0.18 * tw(t, T.sB[0], 0.3)} />
    </svg>
  );
};

/** Phone call card (scene B). */
const CallCard: React.FC<{t: number}> = ({t}) => {
  if (!inS(t, [T.sB[0], T.sB[1] + 0.25])) return null;
  const k = tw(t, T.sB[0] + 0.05, 0.4, backOut);
  const o = 1 - tw(t, T.sB[1] - 0.2, 0.25);
  const secs = Math.floor(Math.max(0, t - T.sB[0]) * 7);
  const row = (at: number, l: string, r: string, opts: {big?: boolean; color?: string} = {}) => {
    const rk = tw(t, at, 0.28, backOut);
    return (
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', opacity: Math.min(1, rk * 1.5), transform: `translateX(${lerp(-40, 0, rk)}px)`, fontFamily: FONT.sans, fontWeight: opts.big ? 900 : 800, fontSize: opts.big ? 60 : 44, lineHeight: opts.big ? '78px' : '62px', color: opts.color ?? C.ink}}>
        <span>{l}</span>
        <span>{r}</span>
      </div>
    );
  };
  return (
    <div style={{position: 'absolute', left: 190, top: 330, width: 700, opacity: o, transform: `translateY(${lerp(160, 0, k)}px) scale(${lerp(0.85, 1, k)}) rotate(-2deg)`}}>
      <div style={{background: C.ink, borderRadius: 56, padding: 18, boxShadow: HARD_SHADOW}}>
        <div style={{background: C.paper, borderRadius: 42, padding: '30px 40px 40px', position: 'relative'}}>
          <div style={{position: 'absolute', right: 34, top: 24, display: 'flex', alignItems: 'center', gap: 8, fontFamily: FONT.sans, fontWeight: 900, fontSize: 30, color: C.coral}}>
            4%
            <div style={{width: 56, height: 26, border: `4px solid ${C.ink}`, borderRadius: 6, position: 'relative'}}>
              <div style={{position: 'absolute', left: 2, top: 2, width: 5, height: 14, background: C.coral, borderRadius: 2}} />
            </div>
          </div>
          <div style={{display: 'flex', alignItems: 'center', gap: 24, marginTop: 30}}>
            <div style={{width: 110, height: 110, borderRadius: 55, background: C.teal, border: `6px solid ${C.ink}`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0}}>
              <svg width={80} height={80} viewBox="-40 -30 80 80"><Key x={0} y={-6} s={0.55} rot={-35} col={C.white} /></svg>
            </div>
            <div>
              <div style={{fontFamily: FONT.sans, fontWeight: 900, fontSize: 50, lineHeight: '58px', color: C.ink}}>24/7 Locksmith</div>
              <div style={{fontFamily: FONT.sans, fontWeight: 800, fontSize: 34, color: C.teal}}>on call · 0:{String(12 + secs).padStart(2, '0')}</div>
            </div>
          </div>
          <div style={{borderTop: `4px solid ${C.wallDark}`, margin: '28px 0 12px'}} />
          {row(T.q1, 'Door opening', '€120')}
          {row(T.q2, 'Saturday night', '× 2', {color: C.coral})}
          <div style={{borderTop: `4px dashed ${C.ink}`, margin: '12px 0 8px', opacity: tw(t, T.dbl - 0.05, 0.2)}} />
          {row(T.dbl, 'TOTAL', '€240', {big: true, color: C.coral})}
        </div>
      </div>
    </div>
  );
};

/** Battery icon over the waiting Jonas. */
const Battery: React.FC<{t: number}> = ({t}) => {
  const pct = t < T.sC[0] + 0.8 ? 4 : t < T.sC[0] + 1.4 ? 2 : t < T.die ? 1 : 0;
  const k = tw(t, T.sC[0] + 0.25, 0.3, backOut);
  const dk = tw(t, T.die, 0.25, backOut);
  const x = 790, y = 700;
  return (
    <g transform={`translate(${x},${y}) scale(${lerp(0.5, 1, k) * (1 + 0.15 * Math.max(0, 1 - Math.abs(t - T.die - 0.12) / 0.12))})`} opacity={Math.min(1, k * 1.5)}>
      <rect x={-90} y={-44} width={170} height={88} rx={16} fill={C.white} stroke={C.ink} strokeWidth={OW * 1.2} />
      <rect x={82} y={-18} width={20} height={36} rx={5} fill={C.ink} />
      <rect x={-78} y={-32} width={Math.max(0, 146 * pct * 0.06)} height={64} rx={8} fill={C.coral} />
      <text x={-4} y={18} textAnchor="middle" fontFamily={FONT.sans} fontWeight={900} fontSize={pct > 0 ? 50 : 40} fill={pct > 0 ? C.ink : C.coral}>{pct > 0 ? `${pct}%` : 'DEAD'}</text>
      {dk > 0 && <line x1={-104} y1={56} x2={110} y2={-56} stroke={C.coral} strokeWidth={12} strokeLinecap="round" opacity={dk} />}
    </g>
  );
};

/** Scene C: waiting on the landing floor. */
const SceneC: React.FC<{t: number}> = ({t}) => {
  const settle = lerp(1.12, 1, tw(t, T.sC[0], 0.5, easeOut));
  const mins = lerp(130, 200, tw(t, T.sC[0] + 0.15, 1.9, easeInOut));
  const shiver = t > T.die ? 3 * Math.sin(t * 60) : 0;
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(540,900) scale(${settle}) translate(-540,-900)`}>
        <Landing t={t} openA={0} openB={0}>
          <Clock x={545} y={560} r={70} minutes={mins} />
          <Bag x={340} y={FLOOR_Y} s={0.8} />
          <g>
            <rect x={428} y={FLOOR_Y - 150} width={190} height={150} rx={6} fill={nc('#C9935A', '#2A2050')} stroke={C.ink} strokeWidth={OW} />
            <rect x={428} y={FLOOR_Y - 150} width={190} height={30} fill={nc('#B98249', '#3A2C6E')} stroke={C.ink} strokeWidth={OW * 0.8} />
            <rect x={510} y={FLOOR_Y - 150} width={26} height={150} fill={nc('#E8C690', '#9C7CFF')} opacity={0.85} />
          </g>
          <Person x={520 + shiver} y={FLOOR_Y} s={0.92} face={1} look={SOCKS} sit pose={t < T.die ? 'phone' : 'idle'} expr={t < T.die ? 'tired' : 'shock'} />
          <Battery t={t} />
        </Landing>
      </g>
    </svg>
  );
};

/** Scene D: the locksmith opens it in no time; the bill. */
const SceneD: React.FC<{t: number}> = ({t}) => {
  const settle = lerp(1.1, 1, tw(t, T.sD[0], 0.5, easeOut));
  const arrive = tw(t, T.sD[0], 0.8, easeOut);
  const lx = lerp(1180, 600, arrive);
  const openA = 0.85 * tw(t, T.open, 0.45, easeOut);
  const reachK = tw(t, T.sD[0] + 0.55, 0.25, easeOut) * (1 - tw(t, T.open + 0.35, 0.3));
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(540,900) scale(${settle}) translate(-540,-900)`}>
        <Landing t={t} openA={openA} openB={0} insideA={<InsideKeys t={t} />}>
          <Bag x={980} y={FLOOR_Y} s={0.8} />
          <Person x={860} y={FLOOR_Y} s={0.92} face={-1} look={SOCKS} expr={t >= T.bill ? 'annoyed' : t >= T.open ? 'shock' : 'tired'} />
          <Person x={lx} y={FLOOR_Y} s={0.92} face={-1} look={LOCKSMITH} walk={arrive < 1 ? t * 9 : null} pose={reachK > 0.05 ? 'reach' : 'idle'} poseK={0.65 * reachK} expr={t >= T.open ? 'smug' : 'neutral'} />
        </Landing>
      </g>
    </svg>
  );
};

/** Invoice slip (scene D). */
const Invoice: React.FC<{t: number}> = ({t}) => {
  if (!inS(t, [T.bill, T.sD[1] + 0.25])) return null;
  const k = tw(t, T.bill, 0.4, backOut);
  const o = 1 - tw(t, T.sD[1] - 0.15, 0.25);
  const sk = tw(t, T.paid, 0.22, backOut);
  return (
    <div style={{position: 'absolute', left: 230, top: 370, width: 600, opacity: o, transform: `translateY(${lerp(140, 0, k)}px) rotate(${lerp(6, 2, k)}deg)`}}>
      <div style={{background: C.white, border: `6px solid ${C.ink}`, borderRadius: 10, boxShadow: `10px 10px 0 ${C.ink}`, padding: '26px 36px 30px', position: 'relative'}}>
        <div style={{fontFamily: FONT.sans, fontWeight: 900, fontSize: 32, color: C.navy, letterSpacing: 3}}>INVOICE</div>
        <div style={{fontFamily: FONT.sans, fontWeight: 800, fontSize: 34, color: C.ink, marginTop: 8}}>Door opening, Sat 00:20</div>
        <div style={{fontFamily: FONT.sans, fontWeight: 900, fontSize: 130, lineHeight: '140px', color: C.coral, letterSpacing: '-0.03em'}}>€240</div>
        {sk > 0 && (
          <div style={{position: 'absolute', right: 26, top: 150, transform: `rotate(-12deg) scale(${lerp(2.2, 1, sk)})`, opacity: Math.min(1, sk * 2), border: `8px solid ${C.coral}`, borderRadius: 12, padding: '4px 20px', fontFamily: FONT.sans, fontWeight: 900, fontSize: 64, color: C.coral, background: 'rgba(251,248,242,0.85)'}}>PAID</div>
        )}
      </div>
    </div>
  );
};

/** Scenes E and F: the kiosk downstairs, open 24/7, with a key board. */
const SceneE: React.FC<{t: number}> = ({t}) => {
  const settle = lerp(1.12, 1, tw(t, T.sE[0], 0.5, easeOut));
  const hk = tw(t, T.hand, 0.7, easeInOut);
  const has = t >= T.hand + 0.7;
  const hooks: React.ReactNode[] = [];
  const labels = ['4A', '4B', '3A', '3B', '2A', '2B', '1A', '1B', '0A', '0B'];
  labels.forEach((lb, i) => {
    const r = Math.floor(i / 5), c = i % 5;
    const x = 196 + c * 46, y = 620 + r * 120;
    const mine = lb === '4A';
    hooks.push(
      <g key={lb}>
        <circle cx={x} cy={y} r={5} fill={C.metal} stroke={C.ink} strokeWidth={2} />
        {!(mine && t >= T.hand) && <Key x={x} y={y + 18} s={0.42} col={mine ? C.gold : C.metal} rot={3 * Math.sin(t * 4 + i)} />}
        <rect x={x - 19} y={y + 66} width={38} height={24} rx={5} fill={mine ? C.gold : C.white} stroke={C.ink} strokeWidth={2.5} />
        <text x={x} y={y + 85} textAnchor="middle" fontFamily={FONT.sans} fontWeight={900} fontSize={17} fill={C.ink}>{lb}</text>
      </g>,
    );
  });
  // the 4A key flies from the board to Jonas's hand
  const kx = lerp(196, 640, hk), ky = lerp(638, 790, hk) - 160 * Math.sin(Math.PI * hk);
  const glow = 0.25 + 0.15 * Math.sin(t * 9);
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(540,880) scale(${settle}) translate(-540,-880)`}>
        {/* night street wall */}
        <rect x={0} y={0} width={1080} height={FLOOR_Y} fill={nc('#2B3360', '#120D26')} />
        {[[80, 380], [990, 420], [60, 1060], [1010, 980]].map(([x, y], i) => <rect key={i} x={x - 30} y={y - 16} width={60} height={32} rx={4} fill={nc('#343D72', '#1E1636')} />)}
        {/* sign */}
        <text x={540} y={404} textAnchor="middle" fontFamily={FONT.sans} fontWeight={900} fontSize={96} fill={nc(C.white, '#F2F7FF')} letterSpacing={6}>KIOSK</text>
        <rect x={800} y={330} width={190} height={74} rx={37} fill={C.gold} stroke={C.ink} strokeWidth={OW} />
        <text x={895} y={381} textAnchor="middle" fontFamily={FONT.sans} fontWeight={900} fontSize={38} fill={C.ink}>24/7</text>
        {/* awning */}
        <rect x={120} y={436} width={840} height={40} fill={C.coral} stroke={C.ink} strokeWidth={OW} />
        {Array.from({length: 10}, (_, i) => (
          <path key={i} d={`M ${120 + i * 84} 476 q 42 46 84 0`} fill={i % 2 ? C.white : C.coral} stroke={C.ink} strokeWidth={OW * 0.8} />
        ))}
        {/* lit window */}
        <rect x={140} y={522} width={800} height={500} fill={nc('#FFE7A6', '#241A4A')} stroke={C.ink} strokeWidth={OW} />
        {[640, 760, 880].map((y) => <line key={y} x1={470} y1={y} x2={930} y2={y} stroke={nc('#C9A15E', '#B05CFF')} strokeWidth={8} />)}
        {[640, 760, 880].map((y, r) => Array.from({length: 8}, (_, i) => {
          const cols = [C.teal, C.coral, C.sky, C.green, C.pink, C.gold, C.lilac, C.navy];
          return <rect key={`${r}${i}`} x={486 + i * 55} y={y - 62 + ((i + r) % 3) * 6} width={38} height={58 - ((i + r) % 3) * 6} rx={6} fill={cols[(i + r * 3) % 8]} stroke={C.ink} strokeWidth={3} />;
        }))}
        {/* key board */}
        <rect x={160} y={560} width={250} height={290} rx={10} fill={nc('#8C6239', '#6B3FA0')} stroke={C.ink} strokeWidth={OW * 0.8} />
        <text x={285} y={598} textAnchor="middle" fontFamily={FONT.sans} fontWeight={900} fontSize={26} fill={nc(C.white, '#F2F7FF')} letterSpacing={2}>SPARE KEYS</text>
        <circle cx={196} cy={650} r={34} fill={C.gold} opacity={t < T.hand ? glow : 0} />
        {hooks}
        {/* kiosk owner behind the counter */}
        <Person x={560} y={1060} s={0.86} face={1} look={KIOSK} pose={t >= T.hand - 0.3 && t < T.hand + 0.9 ? 'reach' : 'idle'} poseK={0.5} expr="happy" />
        {/* counter */}
        <rect x={140} y={960} width={800} height={200} fill={C.teal} stroke={C.ink} strokeWidth={OW} />
        <rect x={140} y={960} width={800} height={30} fill={C.tealLight} stroke={C.ink} strokeWidth={OW * 0.8} />
        {/* pavement */}
        <rect x={0} y={FLOOR_Y} width={1080} height={1920 - FLOOR_Y} fill={nc('#9C9384', '#17112F')} />
        <line x1={0} y1={FLOOR_Y} x2={1080} y2={FLOOR_Y} stroke={C.ink} strokeWidth={OW} />
        {[1240, 1360, 1540, 1780].map((y) => <line key={y} x1={0} y1={y} x2={1080} y2={y} stroke={nc('#857C6E', '#2B2152')} strokeWidth={3} />)}
        <Person x={850} y={FLOOR_Y} s={0.92} face={-1} look={JONAS} pose={has ? 'reach' : 'idle'} poseK={0.35} expr={has ? 'happy' : 'neutral'} />
        {t >= T.hand && <Key x={has ? 640 : kx} y={has ? 790 : ky} s={0.9} rot={has ? -20 : lerp(0, 340, hk)} />}
      </g>
      <rect x={0} y={0} width={1080} height={1920} fill={C.shade} opacity={(LOOK === 'neon' ? 2.4 : 1) * 0.16 * tw(t, T.rcpt, 0.3) * (1 - tw(t, T.ask, 0.3))} />
    </svg>
  );
};

/** Cost receipt (scene E). */
const Receipt: React.FC<{t: number}> = ({t}) => {
  if (!inS(t, [T.rcpt, T.ask + 0.25])) return null;
  const k = tw(t, T.rcpt, 0.4, backOut);
  const o = 1 - tw(t, T.ask - 0.1, 0.25);
  const row = (at: number, l: string, r: string, opts: {big?: boolean; color?: string} = {}) => {
    const rk = tw(t, at, 0.25, easeOut);
    return (
      <div style={{display: 'flex', justifyContent: 'space-between', opacity: rk, transform: `translateX(${lerp(-30, 0, rk)}px)`, fontFamily: FONT.mono, fontWeight: 700, fontSize: opts.big ? 48 : 38, lineHeight: opts.big ? '66px' : '58px', color: opts.color ?? C.ink}}>
        <span>{l}</span>
        <span>{r}</span>
      </div>
    );
  };
  return (
    <div style={{position: 'absolute', left: 110, top: 360, width: 830, opacity: o, transform: `translateY(${lerp(120, 0, k)}px) rotate(-1.5deg)`}}>
      <div style={{background: C.white, border: `6px solid ${C.ink}`, borderRadius: 10, padding: '32px 44px 38px', boxShadow: `10px 10px 0 ${C.ink}`}}>
        <div style={{fontFamily: FONT.sans, fontWeight: 900, fontSize: 34, color: C.navy, letterSpacing: 2, marginBottom: 12}}>WHAT IT COSTS</div>
        {row(T.rcpt + 0.05, 'Locksmith, Sat night', '€240')}
        {row(T.rcpt + 0.2, 'Kiosk keeps a key', '€2/mo', {color: C.teal})}
        <div style={{borderTop: `4px dashed ${C.ink}`, margin: '14px 0 10px', opacity: tw(t, T.rcpt + 1.65, 0.2)}} />
        {row(T.rcpt + 1.75, '1 lockout =', '10 years', {big: true, color: C.coral})}
      </div>
    </div>
  );
};

export const Case3P1: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  let scene: React.ReactNode;
  if (t < T.sB[0]) scene = <SceneA t={t} />;
  else if (t < T.sC[0]) scene = <SceneB t={t} />;
  else if (t < T.sD[0]) scene = <SceneC t={t} />;
  else if (t < T.sE[0]) scene = <SceneD t={t} />;
  else if (t < T.cardOut) scene = <SceneE t={t} />;
  else scene = <SceneA t={t - T.end} />;
  const cuts = [T.sB[0], T.sC[0], T.sD[0], T.sE[0], T.cardOut];
  const flash = Math.max(0, ...cuts.map((c) => 1 - Math.abs(t - c) / 0.07)) * 0.35;
  let hud: React.ReactNode = null;
  if (t >= T.reveal + 0.35 && t < T.sE[0]) {
    const v = billAt(t);
    const bump = [T.q1, T.dbl].some((q) => t > q && t < q + 0.4) ? 0.8 * (1 - Math.abs(t - 0.2 - (t < T.dbl ? T.q1 : T.dbl)) / 0.2) : 0;
    hud = <Counter value={v} prefix="€" bump={Math.max(0, bump)} label="THE BILL" color={v >= 240 ? C.coral : C.ink} op={tw(t, T.reveal + 0.35, 0.25)} />;
  }
  return (
    <LabelFont.Provider value="sans">
      <AbsoluteFill style={{backgroundColor: C.paper}}>
        <Img src={staticFile(BG_FILE)} style={{position: 'absolute', width: 1080, height: 1920}} />
        {scene}
        <CallCard t={t} />
        <Invoice t={t} />
        <Receipt t={t} />
        <AbsoluteFill style={{backgroundColor: C.white, opacity: flash}} />
        <SeriesPill part={1} label="CASE 3" />
        {hud}
        <Tag t={t} at={T.reveal + 0.45} until={T.sA[1] - 0.1} text="SAT · 23:10" y={300} />
        <Tag t={t} at={T.sC[0] + 0.15} until={T.sC[1] - 0.1} text="70 MINUTES LATER" y={300} />
        <Tag t={t} at={T.open + 0.1} until={T.bill - 0.05} text="NOT EVEN LOCKED" y={300} />
        <Captions t={t} caps={CAPS} />
        <EndCard t={t} at={T.card} out={T.cardOut} next={4} kicker="CASE 3 · YOUR CALL" lines={['Is this a business?', <span style={{color: C.gold}}>YES or NO?</span>]} />
      </AbsoluteFill>
    </LabelFont.Provider>
  );
};
