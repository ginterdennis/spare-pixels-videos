import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import T from './c2p1.json';
import {backOut, C, easeInOut, easeOut, FONT, FPS, lerp, OW, tw} from './theme';
import {along, Building, DOOR_L, DOOR_R, LV, SA, SB, Walker} from './Building';
import {JONAS, Look, Person} from './Person';
import {FLOOR_Y} from './Props';
import {NEIGHBOURS} from './Part1';
import {Cap, Captions, Counter, Em, EndCard, LabelFont, SeriesPill, Tag} from './UI';

// Case 2, Part 1 "The parcel": the app says DELIVERED, the doormat is empty. The photo shows another
// door. Every neighbour passed it on: 7 flats, 160 stairs. Flat 7 was 4B, right next door, since Tuesday.
// Same house and cast as case 1 (laundry). Voiced (A+).
const inS = (t: number, s: number[]) => t >= s[0] && t < s[1];
type Pt = {x: number; y: number};
type Stop = {fl: number; side: 'L' | 'R'; text: string};
const idx = (fl: number) => 4 - fl; // floor number -> LV index
const doorX = (side: 'L' | 'R') => (side === 'L' ? DOOR_L + 46 : DOOR_R - 46);

/** Walking route between two flat doors over the stair flights. */
const route = (a: {fl: number; side: 'L' | 'R'}, b: {fl: number; side: 'L' | 'R'}): Pt[] => {
  const ia = idx(a.fl), ib = idx(b.fl);
  const pts: Pt[] = [{x: doorX(a.side), y: LV[ia]}];
  if (ia < ib) {
    for (let k = ia; k < ib; k++) {
      pts.push({x: k % 2 === 0 ? SA : SB, y: LV[k]});
      pts.push({x: k % 2 === 0 ? SB : SA, y: LV[k + 1]});
    }
  } else if (ia > ib) {
    for (let k = ia - 1; k >= ib; k--) {
      pts.push({x: k % 2 === 0 ? SB : SA, y: LV[k + 1]});
      pts.push({x: k % 2 === 0 ? SA : SB, y: LV[k]});
    }
  }
  pts.push({x: doorX(b.side), y: LV[ib]});
  return pts;
};

const HOME = {fl: 4, side: 'L' as const};
const STOPS: Stop[] = [
  {fl: 2, side: 'L', text: 'Gave it to 3B!'},
  {fl: 3, side: 'R', text: '1A signed for it.'},
  {fl: 1, side: 'L', text: '0B took it.'},
  {fl: 0, side: 'R', text: 'Gave it to 2B.'},
  {fl: 2, side: 'R', text: 'Try 3A?'},
  {fl: 3, side: 'L', text: '4B, I think.'},
  {fl: 4, side: 'R', text: ''}, // flat 7: right next door (scene D)
];
const LEGS = STOPS.map((s, i) => route(i === 0 ? HOME : STOPS[i - 1], s));
const LEG_STAIRS = STOPS.map((s, i) => 16 * Math.abs((i === 0 ? HOME.fl : STOPS[i - 1].fl) - s.fl)); // 32,16,32,16,32,16
const lookAt = (fl: number, side: 'L' | 'R'): Look => (fl === 4 && side === 'L' ? JONAS : NEIGHBOURS.find((n) => n.lv === idx(fl) && n.side === side)!.look);
// leg i: walk from T.legs[i][0] to T.legs[i][1]; the neighbour's bubble pops on arrival
const legAt = (t: number) => {
  for (let i = LEGS.length - 1; i >= 0; i--) if (t >= T.legs[i][0]) return i;
  return -1;
};
const stairsAt = (t: number) => {
  let s = 0;
  T.legs.forEach((l: number[], i: number) => {
    s += LEG_STAIRS[i] * tw(t, l[0], l[1] - l[0]);
  });
  return Math.round(s);
};
const flatsAt = (t: number) => {
  let n = 0;
  T.legs.forEach((l: number[]) => {
    if (t >= l[1]) n++;
  });
  return n;
};

const CAPS: Cap[] = [
  {at: 0, until: T.reveal - 0.05, lines: ['How one parcel', <Em>visited 7 flats.</Em>]},
  {at: T.reveal, until: T.sA[1] - 0.05, lines: ['"Delivered."', <Em>Where?</Em>]},
  {at: T.sB[0] + 0.1, until: T.legs[0][1] - 0.05, lines: ['The photo shows', <Em>the wrong door.</Em>]},
  {at: T.legs[0][1], until: T.sB[1] - 0.05, lines: ['That neighbour', <Em>passed it on.</Em>]},
  {at: T.sC[0] + 0.1, until: T.next2 - 0.05, lines: ['So did', <Em>the next one.</Em>]},
  {at: T.next2, until: T.stairsLine - 0.05, lines: ['And the next.', <Em>And the next.</Em>]},
  {at: T.stairsLine, until: T.flat7 - 0.05, lines: ['160 stairs', <Em>later...</Em>]},
  {at: T.flat7, until: T.since - 0.05, lines: ['Flat 7 was', <Em>right next door.</Em>]},
  {at: T.since, until: T.sD[1] - 0.05, lines: ['"Oh, that\'s yours?', <Em>{"It's been here since Tuesday.\""}</Em>]},
  {at: T.sE[0] + 0.1, until: T.ask - 0.05, lines: ['Now picture', <Em>December.</Em>]},
  {at: T.ask, until: T.card - 0.05, lines: ['Where does YOUR', <Em>parcel end up?</Em>]},
];

/** Cardboard parcel (local origin = bottom centre). */
const Parcel: React.FC<{x: number; y: number; s?: number; rot?: number}> = ({x, y, s = 1, rot = 0}) => (
  <g transform={`translate(${x},${y}) rotate(${rot}) scale(${s})`}>
    <rect x={-80} y={-110} width={160} height={110} rx={6} fill="#C9935A" stroke={C.ink} strokeWidth={OW} />
    <rect x={-80} y={-110} width={160} height={26} fill="#B98249" stroke={C.ink} strokeWidth={OW * 0.8} />
    <rect x={-14} y={-110} width={28} height={110} fill="#E8C690" opacity={0.85} />
    <rect x={22} y={-66} width={46} height={34} rx={3} fill={C.white} stroke={C.ink} strokeWidth={3} />
  </g>
);

/** Floor-4 landing close-up: 4A (Jonas, gold door) left, 4B right. `openA`/`openB` 0..1 door swing. */
export const Landing: React.FC<{t: number; openA: number; openB: number; children?: React.ReactNode; matEmpty?: number; insideA?: React.ReactNode}> = ({t, openA, openB, children, matEmpty = 0, insideA}) => {
  const door = (x: number, label: string, open: number, col: string, inside?: React.ReactNode) => (
    <g>
      <text x={x + 130} y={570} textAnchor="middle" fontFamily={FONT.sans} fontWeight={900} fontSize={44} fill={C.ink}>{label}</text>
      <rect x={x} y={600} width={260} height={FLOOR_Y - 600} fill={C.ink} />
      <rect x={x + 20} y={640} width={220} height={FLOOR_Y - 640} fill="#F5E6C8" opacity={0.25} />
      {inside}
      {/* door leaf swings open towards the viewer (narrower = more open) */}
      <g transform={`translate(${x},0) scale(${lerp(1, 0.18, open)},1)`}>
        <rect x={0} y={600} width={260} height={FLOOR_Y - 600} fill={col} stroke={C.ink} strokeWidth={OW} />
        <rect x={30} y={640} width={200} height={190} rx={8} fill="none" stroke={C.ink} strokeWidth={4} opacity={0.4} />
        <rect x={30} y={860} width={200} height={240} rx={8} fill="none" stroke={C.ink} strokeWidth={4} opacity={0.4} />
        <circle cx={222} cy={880} r={13} fill={C.metal} stroke={C.ink} strokeWidth={4} />
      </g>
      <rect x={x - 12} y={588} width={284} height={FLOOR_Y - 588} fill="none" stroke={C.ink} strokeWidth={OW * 1.3} />
    </g>
  );
  return (
    <g>
      <rect x={0} y={0} width={1080} height={FLOOR_Y} fill={C.wall} />
      {/* ceiling lamp */}
      <line x1={540} y1={300} x2={540} y2={380} stroke={C.ink} strokeWidth={4} />
      <path d="M 490 420 L 590 420 L 570 380 L 510 380 Z" fill={C.gold} stroke={C.ink} strokeWidth={5} strokeLinejoin="round" />
      {door(150, '4A', openA, C.gold, insideA)}
      {door(680, '4B', openB, C.wallDark)}
      {/* floor + doormats */}
      <rect x={0} y={FLOOR_Y} width={1080} height={1920 - FLOOR_Y} fill={C.floor} />
      <line x1={0} y1={FLOOR_Y} x2={1080} y2={FLOOR_Y} stroke={C.ink} strokeWidth={OW} />
      {[1230, 1320, 1440, 1600, 1800].map((y) => <line key={y} x1={0} y1={y} x2={1080} y2={y} stroke={C.floorLine} strokeWidth={3} />)}
      <rect x={160} y={FLOOR_Y + 16} width={240} height={46} rx={10} fill={C.coral} stroke={C.ink} strokeWidth={5} />
      <rect x={690} y={FLOOR_Y + 16} width={240} height={46} rx={10} fill={C.teal} stroke={C.ink} strokeWidth={5} />
      {matEmpty > 0 && (
        <rect x={210} y={FLOOR_Y - 96} width={150} height={104} rx={6} fill="none" stroke={C.ink} strokeWidth={5} strokeDasharray="16 12" opacity={matEmpty * (0.6 + 0.4 * Math.sin(t * 10))} />
      )}
      {children}
    </g>
  );
};

/** iOS-style banner at the top. */
const Banner: React.FC<{t: number; at: number; until: number; title: string; sub: string}> = ({t, at, until, title, sub}) => {
  if (t < at - 0.5 || t > until + 0.3) return null;
  const k = at <= 0 ? tw(t, -0.25, 0.4, backOut) : tw(t, at, 0.35, backOut);
  const o = 1 - tw(t, until, 0.25);
  return (
    <div style={{position: 'absolute', left: 60, width: 960, top: lerp(160, 300, k), opacity: o * Math.min(1, k * 2)}}>
      <div style={{background: C.white, border: `6px solid ${C.ink}`, borderRadius: 30, boxShadow: `8px 8px 0 ${C.ink}`, padding: '20px 26px', display: 'flex', gap: 22, alignItems: 'center'}}>
        <div style={{width: 84, height: 84, borderRadius: 20, background: '#C9935A', border: `5px solid ${C.ink}`, flexShrink: 0, position: 'relative'}}>
          <div style={{position: 'absolute', left: 30, top: 0, width: 16, height: 74, background: '#E8C690'}} />
        </div>
        <div>
          <div style={{fontFamily: FONT.sans, fontWeight: 900, fontSize: 44, lineHeight: '52px', color: C.ink}}>{title}</div>
          <div style={{fontFamily: FONT.sans, fontWeight: 700, fontSize: 32, lineHeight: '40px', color: C.navy, opacity: 0.75}}>{sub}</div>
        </div>
      </div>
    </div>
  );
};

/** Delivery photo card: a parcel in front of door 2A. */
const Photo: React.FC<{t: number}> = ({t}) => {
  if (t < T.photo[0] || t > T.photo[1] + 0.3) return null;
  const k = tw(t, T.photo[0], 0.4, backOut);
  const o = 1 - tw(t, T.photo[1], 0.25);
  const ring = tw(t, T.photo[0] + 0.55, 0.35, easeOut);
  return (
    <div style={{position: 'absolute', left: 190, top: 330, width: 700, opacity: o, transform: `translateY(${lerp(140, 0, k)}px) rotate(${lerp(8, -3, k)}deg) scale(${lerp(0.8, 1, k)})`}}>
      <div style={{background: C.white, border: `6px solid ${C.ink}`, borderRadius: 12, boxShadow: `10px 10px 0 ${C.ink}`, padding: '22px 22px 18px'}}>
        <svg width={644} height={600} style={{display: 'block'}}>
          <rect x={0} y={0} width={644} height={600} fill={C.wall} />
          <rect x={210} y={130} width={230} height={420} fill={C.lilac} stroke={C.ink} strokeWidth={6} />
          <circle cx={410} cy={350} r={12} fill={C.metal} stroke={C.ink} strokeWidth={4} />
          <text x={325} y={108} textAnchor="middle" fontFamily={FONT.sans} fontWeight={900} fontSize={64} fill={C.ink}>2A</text>
          <ellipse cx={325} cy={86} rx={lerp(30, 92, ring)} ry={lerp(20, 56, ring)} fill="none" stroke={C.coral} strokeWidth={9} opacity={ring} />
          <rect x={0} y={550} width={644} height={50} fill={C.floor} />
          <Parcel x={325} y={590} s={1.25} />
        </svg>
        <div style={{fontFamily: FONT.sans, fontWeight: 800, fontSize: 34, color: C.navy, marginTop: 12, textAlign: 'center'}}>Delivery photo · front door</div>
      </div>
    </div>
  );
};

/** Overview speech bubble at a flat door. */
const DoorBubble: React.FC<{fl: number; side: 'L' | 'R'; text: string; k: number; o: number}> = ({fl, side, text, k, o}) => {
  const lv = idx(fl);
  const w = Math.max(160, text.length * 17 + 48);
  const y = LV[lv] - 132;
  const x = side === 'L' ? DOOR_L + 40 : DOOR_R - 40 - w;
  const tailX = side === 'L' ? x + 26 : x + w - 26;
  return (
    <g opacity={o} transform={`translate(${tailX},${y + 60}) scale(${lerp(0.4, 1, k)}) translate(${-tailX},${-(y + 60)})`}>
      <path d={`M ${tailX - 12} ${y + 56} L ${side === 'L' ? tailX - 26 : tailX + 26} ${y + 84} L ${tailX + 12} ${y + 56} Z`} fill={C.white} stroke={C.ink} strokeWidth={4} strokeLinejoin="round" />
      <rect x={x} y={y - 4} width={w} height={66} rx={16} fill={C.white} stroke={C.ink} strokeWidth={6} />
      <text x={x + w / 2} y={y + 40} textAnchor="middle" fontFamily={FONT.sans} fontWeight={800} fontSize={31} fill={C.ink}>{text}</text>
    </g>
  );
};

/** Dotted trail of everything walked so far. */
const Trail: React.FC<{t: number; upto: number}> = ({t, upto}) => {
  const segs: React.ReactNode[] = [];
  LEGS.forEach((leg, i) => {
    const l = T.legs[i];
    const k = tw(t, l[0], l[1] - l[0]);
    if (k <= 0 || i > upto) return;
    const pts: Pt[] = [];
    const n = 40;
    for (let j = 0; j <= n; j++) pts.push(along(leg, (j / n) * k));
    segs.push(<path key={i} d={pts.map((p, j) => `${j ? 'L' : 'M'}${p.x.toFixed(1)} ${(p.y - 40).toFixed(1)}`).join(' ')} fill="none" stroke={C.coral} strokeWidth={6} strokeDasharray="4 14" strokeLinecap="round" opacity={0.85} />);
  });
  return <g>{segs}</g>;
};

/** Scenes B (from the walk) and C: overview of the house, Jonas hops door to door. */
const Overview: React.FC<{t: number; final?: boolean}> = ({t, final = false}) => {
  const s0 = final ? T.sE[0] : t < T.sC[0] ? T.walk0 : T.sC[0];
  const settle = lerp(1.1, 1, tw(t, s0, 0.4, easeOut));
  const i = legAt(t);
  const walkers: Walker[] = [];
  const bubbles: React.ReactNode[] = [];
  if (!final) {
    if (i < 0) {
      walkers.push({u: 0, path: [{x: doorX('L'), y: LV[0]}, {x: 0, y: LV[0]}], look: JONAS, basket: null, moving: false, face: 1});
    } else {
      const l = T.legs[i];
      const u = tw(t, l[0], l[1] - l[0], easeInOut);
      walkers.push({u, path: LEGS[i], look: JONAS, basket: null, moving: t < l[1], face: STOPS[i].side === 'L' ? -1 : 1});
    }
    STOPS.forEach((s, j) => {
      const a = T.legs[j][1];
      if (t < a || !s.text) return;
      const pk = tw(t, a, 0.3, backOut);
      const age = t - a;
      const live = j === i;
      const o = live ? 1 : Math.max(0, 1 - (age - 0.6) / 0.25);
      if (o <= 0) return;
      walkers.push({u: 0, path: [{x: s.side === 'L' ? doorX('L') - 70 : doorX('R') + 70, y: LV[idx(s.fl)]}, {x: 0, y: LV[idx(s.fl)]}], look: lookAt(s.fl, s.side), basket: null, moving: false, face: s.side === 'L' ? 1 : -1, opacity: Math.min(1, pk * 1.4) * o});
      bubbles.push(<DoorBubble key={j} fl={s.fl} side={s.side} text={s.text} k={pk} o={o} />);
    });
  }
  // December: parcels pile up at every door
  const dec = final ? tw(t, T.sE[0] + 0.3, 1.2) : 0;
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(540,760) scale(${settle}) translate(-540,-760)`}>
        <Building t={t} walkers={walkers} hiDoor />
        <Trail t={final ? T.legs[6][1] + 1 : t} upto={final ? 9 : i} />
        {bubbles}
        {final && [0, 1, 2, 3, 4].map((lv) => (['L', 'R'] as const).map((side, si) => {
          const n = 3;
          return Array.from({length: n}, (_, j) => {
            const order = lv * 6 + si * 3 + j;
            const pk = tw(dec * 2.2, order / 30, 0.08, backOut);
            if (pk <= 0) return null;
            const x = (side === 'L' ? DOOR_L + 52 : DOOR_R - 52) + (side === 'L' ? 1 : -1) * j * 38;
            return <Parcel key={`${lv}${side}${j}`} x={x} y={LV[lv] - j * 4} s={0.26 * pk} rot={(j - 1) * 6} />;
          });
        }))}
      </g>
    </svg>
  );
};

/** Scenes A and D: the floor-4 landing. */
const SceneLanding: React.FC<{t: number; twist?: boolean}> = ({t, twist = false}) => {
  if (!twist) {
    const push = lerp(1.0, 1.07, tw(t, -0.5, 3.8, easeInOut));
    const openA = tw(t, -0.4, 0.9, easeOut);
    const empty = tw(t, T.reveal - 0.2, 0.3);
    const stamp = tw(t, T.reveal, 0.22, backOut);
    return (
      <svg width={1080} height={1920} style={{position: 'absolute'}}>
        <g transform={`translate(300,900) scale(${push}) translate(-300,-900)`}>
          <Landing t={t} openA={openA} openB={0} matEmpty={empty}>
            <Person x={260} y={FLOOR_Y} s={0.92} face={1} pose="phone" expr={t >= T.reveal ? 'shock' : 'neutral'} />
            {stamp > 0 && (
              <g transform={`translate(300,1010) rotate(-9) scale(${lerp(2.2, 1, stamp)})`} opacity={Math.min(1, stamp * 2)}>
                <rect x={-200} y={-50} width={400} height={92} rx={12} fill={C.white} stroke={C.coral} strokeWidth={9} />
                <text x={0} y={22} textAnchor="middle" fontFamily={FONT.sans} fontWeight={900} fontSize={60} fill={C.coral}>DELIVERED?</text>
              </g>
            )}
          </Landing>
        </g>
      </svg>
    );
  }
  const settle = lerp(1.12, 1, tw(t, T.sD[0], 0.45, easeOut));
  const openB = tw(t, T.knock + 0.15, 0.5, easeOut);
  const pink = NEIGHBOURS[0].look;
  const bk = tw(t, T.since, 0.3, backOut);
  const hand = t >= T.handover;
  const hk = tw(t, T.handover, 0.4, easeInOut);
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(700,900) scale(${settle}) translate(-700,-900)`}>
        <Landing t={t} openA={1} openB={openB}>
          {openB > 0.3 && <Person x={830} y={FLOOR_Y} s={0.92} face={-1} pose={hand ? 'idle' : 'reach'} poseK={0.15} look={pink} expr="happy" opacity={Math.min(1, (openB - 0.3) * 3)} />}
          <Person x={lerp(430, 480, tw(t, T.sD[0], 0.6, easeOut))} y={FLOOR_Y} s={0.92} face={1} walk={t < T.sD[0] + 0.6 ? t * 9 : null} pose={hand ? 'reach' : 'idle'} poseK={0.15} expr={t >= T.knock + 0.5 ? 'shock' : 'neutral'} />
          {openB > 0.3 && <Parcel x={lerp(640, 680, hk)} y={FLOOR_Y - 150} s={0.95} />}
          {t >= T.since && (
            <g transform={`translate(820,600) scale(${lerp(0.4, 1, bk)}) translate(-820,-600)`}>
              <path d="M 800 586 L 840 646 L 850 586 Z" fill={C.white} stroke={C.ink} strokeWidth={6} strokeLinejoin="round" />
              <rect x={560} y={470} width={470} height={122} rx={26} fill={C.white} stroke={C.ink} strokeWidth={7} />
              <rect x={804} y={580} width={42} height={14} fill={C.white} />
              <text x={795} y={518} textAnchor="middle" fontFamily={FONT.sans} fontWeight={900} fontSize={40} fill={C.ink}>{"Oh, that's yours?"}</text>
              <text x={795} y={568} textAnchor="middle" fontFamily={FONT.sans} fontWeight={800} fontSize={34} fill={C.coral}>Since Tuesday!</text>
            </g>
          )}
        </Landing>
      </g>
    </svg>
  );
};

export const Case2P1: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  let scene: React.ReactNode;
  if (t < T.walk0) scene = <SceneLanding t={t} />;
  else if (t < T.sD[0]) scene = <Overview t={t} />;
  else if (t < T.sE[0]) scene = <SceneLanding t={t} twist />;
  else if (t < T.cardOut) scene = <Overview t={t} final />;
  else scene = <SceneLanding t={t - T.end} />;
  const cuts = [T.walk0, T.sD[0], T.sE[0], T.cardOut];
  const flash = Math.max(0, ...cuts.map((c) => 1 - Math.abs(t - c) / 0.07)) * 0.35;
  let hud: React.ReactNode = null;
  if (t >= T.walk0 && t < T.card) {
    const n = flatsAt(t);
    const s = stairsAt(t);
    const bump = T.legs.some((l: number[]) => Math.abs(t - l[1] - 0.12) < 0.12) ? 1 : 0;
    hud = <Counter value={n} bump={bump * 0.8} label="FLATS VISITED" color={n >= 7 ? C.coral : C.ink} sub={`${s} STAIRS`} />;
  }
  return (
    <LabelFont.Provider value="sans">
      <AbsoluteFill style={{backgroundColor: C.paper}}>
        <Img src={staticFile('paper.png')} style={{position: 'absolute', width: 1080, height: 1920}} />
        {scene}
        <Banner t={t} at={0} until={T.sA[1] - 0.15} title="Your parcel was delivered" sub="Today, 14:02 · photo attached" />
        <Photo t={t} />
        <AbsoluteFill style={{backgroundColor: C.white, opacity: flash}} />
        <SeriesPill part={1} label="CASE 2 · PART 1" />
        {hud}
        <Tag t={t} at={T.sD[0] + 0.15} until={T.sD[1] - 0.1} text="FLAT 7 · NEXT DOOR" y={330} />
        <Captions t={t} caps={CAPS} />
        <EndCard t={t} at={T.card} out={T.cardOut} next={2} lines={['One box by the', <span style={{color: C.gold}}>front door?</span>]} sub="Send this to your neighbour." />
      </AbsoluteFill>
    </LabelFont.Provider>
  );
};
