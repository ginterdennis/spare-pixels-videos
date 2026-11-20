import React from 'react';
import {C, OW} from './theme';

export type Look = {
  hoodie: string;
  pants: string;
  hair: string;
  skin: string;
  shoes: string;
  hairStyle: 'short' | 'bun' | 'curly' | 'cap' | 'long' | 'bald';
  cap?: string;
};

export const JONAS: Look = {hoodie: C.gold, pants: C.navy, hair: C.hair, skin: C.skin, shoes: C.white, hairStyle: 'curly'};

export type Pose = 'idle' | 'carry' | 'hips' | 'reach' | 'phone' | 'wave' | 'shrug';
export type Expr = 'neutral' | 'tired' | 'shock' | 'annoyed' | 'happy' | 'smug';

type P = {x: number; y: number};

/** Elbow position for a two-segment arm (shoulder s, hand h, segment lengths a/b, bend side). */
const ik = (s: P, h: P, a: number, b: number, bend: 1 | -1): {e: P; h: P} => {
  let dx = h.x - s.x, dy = h.y - s.y;
  let d = Math.hypot(dx, dy);
  const max = a + b - 0.5;
  if (d > max) {
    dx *= max / d; dy *= max / d; d = max;
    h = {x: s.x + dx, y: s.y + dy};
  }
  const cosA = Math.min(1, Math.max(-1, (a * a + d * d - b * b) / (2 * a * Math.max(d, 1e-3))));
  const A = Math.acos(cosA);
  const phi = Math.atan2(dy, dx);
  return {e: {x: s.x + a * Math.cos(phi + bend * A), y: s.y + a * Math.sin(phi + bend * A)}, h};
};

/** A limb drawn as an ink-outlined thick stroke. */
const Limb: React.FC<{pts: P[]; w: number; color: string; sw: number}> = ({pts, w, color, sw}) => {
  const d = pts.map((p, i) => `${i ? 'L' : 'M'}${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ');
  return (
    <g>
      <path d={d} stroke={C.ink} strokeWidth={w + 2 * sw} fill="none" strokeLinecap="round" strokeLinejoin="round" />
      <path d={d} stroke={color} strokeWidth={w} fill="none" strokeLinecap="round" strokeLinejoin="round" />
    </g>
  );
};

/** Clothes heaped in a basket or on a machine: overlapping outlined blobs. */
export const ClothesPile: React.FC<{colors: string[]; w: number; h: number; sw: number; seed?: number}> = ({colors, w, h, sw, seed = 1}) => {
  const n = colors.length;
  const blobs = colors.map((c, i) => {
    const r = ((Math.sin((i + 1) * 12.9898 * seed) * 43758.5453) % 1 + 1) % 1;
    const cx = -w / 2 + (w * (i + 0.5)) / n + (r - 0.5) * 18;
    const ry = h * (0.55 + 0.35 * r);
    const rx = (w / n) * 0.85 + 14;
    return <ellipse key={i} cx={cx} cy={-ry * 0.55} rx={rx} ry={ry} fill={c} stroke={C.ink} strokeWidth={sw} />;
  });
  // second row on top, smaller
  const top = colors.slice(0, Math.max(1, n - 2)).map((c, i) => {
    const m = Math.max(1, n - 2);
    const cx = -w / 2 + (w * (i + 1)) / (m + 1);
    return <ellipse key={`t${i}`} cx={cx} cy={-h * 0.95} rx={(w / m) * 0.45 + 10} ry={h * 0.42} fill={colors[(i + 2) % n]} stroke={C.ink} strokeWidth={sw} />;
  });
  return <g>{blobs}{top}</g>;
};

export const Basket: React.FC<{clothes: string[] | null; sw: number}> = ({clothes, sw}) => (
  <g>
    {clothes && clothes.length > 0 && (
      <g transform="translate(0,-44)">
        <ClothesPile colors={clothes} w={190} h={42} sw={sw} />
      </g>
    )}
    <path d="M -118 -50 L 118 -50 L 98 56 L -98 56 Z" fill={C.tealLight} stroke={C.ink} strokeWidth={sw} strokeLinejoin="round" />
    <rect x={-124} y={-60} width={248} height={22} rx={10} fill={C.teal} stroke={C.ink} strokeWidth={sw} />
    {[-70, -35, 0, 35, 70].map((x) => (
      <rect key={x} x={x - 9} y={-18} width={18} height={50} rx={9} fill={C.teal} opacity={0.55} />
    ))}
  </g>
);

export type PersonProps = {
  x: number;
  y: number;
  s?: number;
  face?: 1 | -1;
  walk?: number | null; // gait phase in radians, null = standing
  pose?: Pose;
  poseK?: number; // 0..1 blend for reach
  look?: Look;
  expr?: Expr;
  basket?: string[] | null; // clothes in the basket (null = no basket)
  sweat?: number; // 0..1
  tap?: number; // foot-tap phase
  ow?: number; // outline width in screen px
  blink?: boolean;
  opacity?: number;
  holding?: string | null; // a piece of clothing in the front hand
  sit?: boolean;
};

export const Person: React.FC<PersonProps> = ({
  x, y, s = 1, face = 1, walk = null, pose = 'idle', poseK = 1, look = JONAS, expr = 'neutral', basket = null, sweat = 0, tap = 0, ow = OW, blink = false, opacity = 1, holding = null, sit = false,
}) => {
  const sw = ow / s;
  const walking = walk !== null;
  const ph = walk ?? 0;
  const bob = (walking ? -7 * Math.abs(Math.sin(ph)) : 0) + (sit ? 64 : 0);

  // ---- legs
  const hip: P = {x: 0, y: -242 + bob};
  const legPts = (side: 1 | -1) => {
    const th = walking ? side * 0.42 * Math.sin(ph) : side * 0.06;
    const lift = walking ? Math.max(0, side * Math.cos(ph)) * 0.55 : 0;
    const tapLift = !walking && side === 1 ? Math.max(0, Math.sin(tap)) * 0.25 : 0;
    const knee = {x: hip.x + side * 6 + 112 * Math.sin(th + tapLift * 0.5), y: hip.y + 112 * Math.cos(th + tapLift * 0.5)};
    const sh = th - lift - tapLift;
    const ankle = {x: knee.x + 110 * Math.sin(sh), y: knee.y + 110 * Math.cos(sh)};
    return [hip, knee, ankle];
  };
  const shoe = (a: P, key: string) => <rect key={key} x={a.x - 24} y={a.y - 16} width={78} height={34} rx={15} fill={look.shoes} stroke={C.ink} strokeWidth={sw} />;
  const back = sit ? [hip, {x: 112, y: hip.y + 4}, {x: 116, y: -18}] : legPts(-1);
  const front = sit ? [hip, {x: 124, y: hip.y}, {x: 132, y: -18}] : legPts(1);

  // ---- arms
  const sh: P = {x: 0, y: -440 + bob};
  const swing = walking && (pose === 'idle') ? 34 * Math.sin(ph) : 0;
  let hb: P, hf: P, bb: 1 | -1 = -1, bf: 1 | -1 = -1;
  let basketAt: P | null = null;
  const k = poseK;
  switch (pose) {
    case 'carry':
      basketAt = {x: 128, y: -318 + bob};
      hb = {x: 228, y: -352 + bob}; hf = {x: 58, y: -350 + bob};
      bb = 1; bf = 1;
      break;
    case 'reach':
      hb = {x: 215 + 40 * k, y: -200 - 150 * k + bob}; hf = {x: 195 + 45 * k, y: -185 - 140 * k + bob};
      bb = 1; bf = 1;
      break;
    case 'hips':
      hb = {x: -30, y: -270}; hf = {x: 34, y: -268};
      bb = 1; bf = -1;
      break;
    case 'phone':
      hb = {x: 108, y: -452 + bob}; hf = {x: 92, y: -440 + bob};
      bb = 1; bf = 1;
      break;
    case 'wave':
      hb = {x: -10, y: -236}; hf = {x: 120 + 18 * Math.sin(k * 20), y: -650};
      bb = -1; bf = 1;
      break;
    case 'shrug':
      hb = {x: -120, y: -380}; hf = {x: 130, y: -380};
      bb = 1; bf = -1;
      break;
    default:
      hb = {x: -4 - swing, y: -228 + bob}; hf = {x: 10 + swing, y: -228 + bob};
      bb = 1; bf = -1;
  }
  const ab = ik(sh, hb, 112, 108, bb);
  const af = ik(sh, hf, 112, 108, bf);

  // ---- head + face
  const hc: P = {x: 8, y: -572 + bob};
  const eyeY = hc.y - 4;
  const ex1 = hc.x + 36, ex2 = hc.x + 62;
  const eyes = () => {
    if (blink) return <g>{[ex1, ex2].map((ex) => <path key={ex} d={`M${ex - 8} ${eyeY} L${ex + 8} ${eyeY}`} stroke={C.ink} strokeWidth={sw * 0.9} strokeLinecap="round" />)}</g>;
    const r = expr === 'shock' ? 9.5 : 7.5;
    return (
      <g>
        {[ex1, ex2].map((ex) => <circle key={ex} cx={ex} cy={eyeY} r={r} fill={C.ink} />)}
        {expr === 'tired' && [ex1, ex2].map((ex) => <path key={`l${ex}`} d={`M${ex - 11} ${eyeY - 3} L${ex + 11} ${eyeY - 3}`} stroke={C.ink} strokeWidth={sw * 0.9} strokeLinecap="round" />)}
        {expr === 'annoyed' && (
          <g>
            <path d={`M${ex1 - 12} ${eyeY - 22} L${ex1 + 10} ${eyeY - 15}`} stroke={C.ink} strokeWidth={sw * 0.9} strokeLinecap="round" />
            <path d={`M${ex2 - 10} ${eyeY - 15} L${ex2 + 12} ${eyeY - 22}`} stroke={C.ink} strokeWidth={sw * 0.9} strokeLinecap="round" />
          </g>
        )}
        {expr === 'shock' && [ex1, ex2].map((ex) => <path key={`b${ex}`} d={`M${ex - 9} ${eyeY - 24} Q${ex} ${eyeY - 31} ${ex + 9} ${eyeY - 24}`} stroke={C.ink} strokeWidth={sw * 0.8} fill="none" strokeLinecap="round" />)}
      </g>
    );
  };
  const mx = hc.x + 46, my = hc.y + 36;
  const mouth = () => {
    switch (expr) {
      case 'shock': return <ellipse cx={mx} cy={my + 2} rx={9} ry={12} fill={C.ink} />;
      case 'happy': return <path d={`M${mx - 15} ${my - 4} Q${mx} ${my + 12} ${mx + 15} ${my - 4}`} stroke={C.ink} strokeWidth={sw * 0.9} fill="none" strokeLinecap="round" />;
      case 'smug': return <path d={`M${mx - 14} ${my} Q${mx + 2} ${my + 6} ${mx + 14} ${my - 8}`} stroke={C.ink} strokeWidth={sw * 0.9} fill="none" strokeLinecap="round" />;
      case 'tired': return <path d={`M${mx - 12} ${my + 4} Q${mx} ${my - 4} ${mx + 12} ${my + 4}`} stroke={C.ink} strokeWidth={sw * 0.9} fill="none" strokeLinecap="round" />;
      case 'annoyed': return <path d={`M${mx - 13} ${my + 1} L${mx + 13} ${my + 1}`} stroke={C.ink} strokeWidth={sw * 0.9} strokeLinecap="round" />;
      default: return <path d={`M${mx - 11} ${my} Q${mx} ${my + 5} ${mx + 11} ${my}`} stroke={C.ink} strokeWidth={sw * 0.9} fill="none" strokeLinecap="round" />;
    }
  };
  const hairBack = () => {
    switch (look.hairStyle) {
      case 'bun': return <circle cx={hc.x - 54} cy={hc.y - 62} r={30} fill={look.hair} stroke={C.ink} strokeWidth={sw} />;
      case 'long': return <path d={`M${hc.x - 70} ${hc.y - 20} Q${hc.x - 92} ${hc.y + 90} ${hc.x - 40} ${hc.y + 110} L${hc.x + 10} ${hc.y + 40} Z`} fill={look.hair} stroke={C.ink} strokeWidth={sw} strokeLinejoin="round" />;
      default: return null;
    }
  };
  const hairFront = () => {
    const r = 76;
    switch (look.hairStyle) {
      case 'bald': return null;
      case 'cap':
        return (
          <g>
            <path d={`M${hc.x - r - 2} ${hc.y - 8} A ${r + 2} ${r + 2} 0 0 1 ${hc.x + r + 2} ${hc.y - 8} Z`} fill={look.cap ?? C.coral} stroke={C.ink} strokeWidth={sw} strokeLinejoin="round" />
            <path d={`M${hc.x + 30} ${hc.y - 10} L${hc.x + 122} ${hc.y - 2} Q${hc.x + 128} ${hc.y - 14} ${hc.x + 110} ${hc.y - 20} L${hc.x + 40} ${hc.y - 26} Z`} fill={look.cap ?? C.coral} stroke={C.ink} strokeWidth={sw} strokeLinejoin="round" />
          </g>
        );
      case 'curly': {
        const bumps = [[-60, -30, 28], [-40, -58, 30], [-8, -72, 30], [26, -66, 28], [52, -46, 24], [-70, 4, 22]];
        return (
          <g>
            {bumps.map(([dx, dy, rr], i) => <circle key={i} cx={hc.x + dx} cy={hc.y + dy} r={rr} fill={look.hair} stroke={C.ink} strokeWidth={sw} />)}
            {bumps.map(([dx, dy, rr], i) => <circle key={`f${i}`} cx={hc.x + dx} cy={hc.y + dy} r={rr - sw / 2} fill={look.hair} />)}
          </g>
        );
      }
      default:
        return (
          <path
            d={`M${hc.x - r + 2} ${hc.y + 6} C ${hc.x - r - 8} ${hc.y - 70}, ${hc.x - 10} ${hc.y - 104}, ${hc.x + 62} ${hc.y - 50} C ${hc.x + 40} ${hc.y - 46}, ${hc.x + 6} ${hc.y - 44}, ${hc.x - 22} ${hc.y - 30} C ${hc.x - 40} ${hc.y - 18}, ${hc.x - 46} ${hc.y}, ${hc.x - 50} ${hc.y + 12} Z`}
            fill={look.hair}
            stroke={C.ink}
            strokeWidth={sw}
            strokeLinejoin="round"
          />
        );
    }
  };

  return (
    <g transform={`translate(${x},${y}) scale(${face * s},${s})`} opacity={opacity}>
      {/* back leg + back arm */}
      <Limb pts={back} w={50} color={look.pants} sw={sw} />
      {shoe(back[2], 'sb')}
      <Limb pts={[sh, ab.e, ab.h]} w={42} color={look.hoodie} sw={sw} />
      <circle cx={ab.h.x} cy={ab.h.y} r={19} fill={look.skin} stroke={C.ink} strokeWidth={sw} />
      {/* front leg */}
      <Limb pts={front} w={50} color={look.pants} sw={sw} />
      {shoe(front[2], 'sf')}
      {/* torso */}
      <rect x={-82} y={-488 + bob} width={164} height={272} rx={48} fill={look.hoodie} stroke={C.ink} strokeWidth={sw} />
      <path d={`M${-10} ${-300 + bob} Q ${30} ${-290 + bob} ${70} ${-300 + bob}`} stroke={C.ink} strokeWidth={sw * 0.7} fill="none" strokeLinecap="round" opacity={0.55} />
      {/* neck + head */}
      <rect x={-12} y={-514 + bob} width={34} height={40} fill={look.skin} stroke={C.ink} strokeWidth={sw} />
      {hairBack()}
      <circle cx={hc.x} cy={hc.y} r={76} fill={look.skin} stroke={C.ink} strokeWidth={sw} />
      {hairFront()}
      {look.hairStyle !== 'cap' && look.hairStyle !== 'long' && (
        <g>
          <circle cx={hc.x - 30} cy={hc.y + 10} r={15} fill={look.skin} stroke={C.ink} strokeWidth={sw} />
          <path d={`M${hc.x - 26} ${hc.y + 3} q -8 7 0 14`} stroke={C.ink} strokeWidth={sw * 0.7} fill="none" strokeLinecap="round" />
        </g>
      )}
      <circle cx={hc.x + 24} cy={hc.y + 22} r={11} fill={C.coral} opacity={0.3} />
      {eyes()}
      {mouth()}
      {sweat > 0 && (
        <path d={`M${hc.x - 70} ${hc.y - 66} q -14 24 0 30 q 14 -6 0 -30 Z`} fill={C.sky} stroke={C.ink} strokeWidth={sw * 0.8} opacity={sweat} transform={`translate(0 ${10 * (1 - sweat)})`} />
      )}
      {/* basket in front of the body */}
      {basketAt && <g transform={`translate(${basketAt.x},${basketAt.y})`}><Basket clothes={basket} sw={sw} /></g>}
      {pose === 'phone' && <rect x={74} y={-512 + bob} width={50} height={86} rx={10} fill={C.ink} stroke={C.ink} strokeWidth={sw} />}
      {/* front arm */}
      <Limb pts={[sh, af.e, af.h]} w={42} color={look.hoodie} sw={sw} />
      {holding && <ellipse cx={af.h.x + 14} cy={af.h.y - 10} rx={46} ry={30} fill={holding} stroke={C.ink} strokeWidth={sw} />}
      <circle cx={af.h.x} cy={af.h.y} r={19} fill={look.skin} stroke={C.ink} strokeWidth={sw} />
    </g>
  );
};
