import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import T from './part4.json';
import {backOut, C, easeInOut, easeOut, FONT, FPS, lerp, OW, tw} from './theme';
import {along, Building, JONAS_PATH, LV, MACHINE_X, pathFrom, Walker} from './Building';
import {JONAS, Person} from './Person';
import {BasementRoom, FLOOR_Y, JONAS_LAUNDRY, NEIGHBOUR_LAUNDRY, Washer} from './Props';
import {NEIGHBOURS} from './Part1';
import {CouchFront, FlatRoom, Phone} from './Scenes2';
import {Cap, Captions, Counter, Em, EndCard, LabelFont, SeriesPill, Tag} from './UI';

// Part 4 "Jonas builds it": the box works, but the basement has no Wi-Fi. A second chip at the basement
// door passes the message upstairs. First ping goes to the neighbour who voted NO. Voiced (A+).
const inS = (t: number, s: number[]) => t >= s[0] && t < s[1];
const PINK = NEIGHBOURS[0]; // 4B, whose laundry Jonas moved in Part 1
const NOVOTER = NEIGHBOURS[5]; // 1A, "NO. I just knock." in Part 3
const PINK_PATH = pathFrom(PINK.lv, PINK.side);
const ZX = MACHINE_X;
const ZY = LV[5] - 60;
const Z = 3.4;

const CAPS: Cap[] = [
  {at: 0, until: T.sA[1] - 0.05, lines: ['Jonas built it.', <Em>Day one: silence.</Em>]},
  {at: T.sB[0] + 0.1, until: T.busy + 0.15, lines: ['The app said FREE.', <Em>It wasn't.</Em>]},
  {at: T.busy + 0.25, until: T.sB[1] - 0.05, lines: ['160 stairs', <Em>for nothing.</Em>]},
  {at: T.sC[0] + 0.1, until: T.concrete - 0.05, lines: ['Floor by floor,', <Em>the Wi-Fi dies.</Em>]},
  {at: T.concrete, until: T.sC[1] - 0.05, lines: ['Concrete eats it.', <Em>Basement: zero bars.</Em>]},
  {at: T.sD[0] + 0.1, until: T.bars - 0.3, lines: ['The fix: a second €6 chip', <Em>at the basement door.</Em>]},
  {at: T.bars - 0.2, until: T.sD[1] - 0.05, lines: ['It passes the message', <Em>upstairs.</Em>]},
  {at: T.sE[0] + 0.1, until: T.card - 0.05, lines: ['First ping goes to...', <Em>the guy who voted NO.</Em>]},
];

/** Wi-Fi bars HUD, top right (replaces the stairs counter in scenes C and D). */
const WifiMeter: React.FC<{bars: number; bump: number; op?: number}> = ({bars, bump, op = 1}) => (
  <div style={{position: 'absolute', right: 52, top: 192, textAlign: 'right', opacity: op}}>
    <div style={{fontFamily: FONT.sans, fontWeight: 900, fontSize: 28, color: C.ink, letterSpacing: 2}}>WI-FI</div>
    <div style={{display: 'flex', gap: 10, alignItems: 'flex-end', justifyContent: 'flex-end', height: 96, marginTop: 6, transform: `scale(${1 + 0.14 * bump})`, transformOrigin: '100% 100%'}}>
      {[0, 1, 2, 3].map((i) => {
        const on = bars > i + 0.001;
        return <div key={i} style={{width: 26, height: 30 + i * 21, borderRadius: 6, border: `5px solid ${C.ink}`, background: on ? (bars >= 3.5 ? C.green : C.goldDark) : 'transparent', opacity: on ? 1 : 0.35}} />;
      })}
    </div>
    {bars < 0.5 && <div style={{fontFamily: FONT.sans, fontWeight: 900, fontSize: 26, color: C.coral, marginTop: 6, letterSpacing: 1}}>NO SIGNAL</div>}
  </div>
);

/** Little radio waves above a box: `k` 0..1 grow-in; crossed out when `dead`. */
const Waves: React.FC<{x: number; y: number; t: number; s?: number; dead?: boolean; col?: string; up?: boolean}> = ({x, y, t, s = 1, dead = false, col = C.teal}) => (
  <g transform={`translate(${x},${y}) scale(${s})`}>
    {[0, 1, 2].map((i) => {
      const ph = ((t * 1.6 + i / 3) % 1);
      const r = 18 + ph * 70;
      return <path key={i} d={`M ${-r * 0.8} ${-r * 0.6} A ${r} ${r} 0 0 1 ${r * 0.8} ${-r * 0.6}`} fill="none" stroke={dead ? C.wallDark : col} strokeWidth={8} strokeLinecap="round" opacity={dead ? 0.8 : 1 - ph} />;
    })}
    {dead && (
      <g stroke={C.coral} strokeWidth={10} strokeLinecap="round">
        <line x1={-30} y1={-86} x2={30} y2={-26} />
        <line x1={30} y1={-86} x2={-30} y2={-26} />
      </g>
    )}
  </g>
);

/** Scene A: basement close-up. Jonas presses the box onto the running washer. Also the loop target. */
const SceneA: React.FC<{t: number}> = ({t}) => {
  const push = lerp(1.0, 1.07, tw(t, -0.5, 3.6, easeInOut));
  const pressing = t < 1.25;
  const pose = pressing ? 'reach' : 'phone';
  const dead = t >= T.nosig;
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(760,900) scale(${push}) translate(-760,-900)`}>
        <BasementRoom t={t}>
          <Washer x={770} y={FLOOR_Y} t={t} state="running" drum={JONAS_LAUNDRY} sensor={1} sensorBlink={Math.floor(t * 4) % 2 === 0} qr={1} display="1:50" />
          <Waves x={840} y={FLOOR_Y - 480} t={t} s={0.9} dead={dead} col={C.gold} />
          <Person x={500} y={FLOOR_Y} face={1} pose={pose} poseK={pressing ? 0.85 + 0.15 * Math.sin(t * 9) : 1} expr={dead ? 'shock' : 'happy'} />
        </BasementRoom>
      </g>
    </svg>
  );
};

const zoomB = (t: number) => {
  const zin = lerp(1, Z, tw(t, T.busy - T.zoomIn, T.zoomIn, easeInOut));
  const zout = lerp(Z, 1, tw(t, T.up[0] - 0.15, T.zoomOut, easeOut));
  return t < T.up[0] - 0.15 ? zin : zout;
};

const pinkWalk = (t: number) => {
  if (t < T.up[0]) {
    const u = tw(t, T.down[0], T.down[1] - T.down[0]);
    const a = along(PINK_PATH, u);
    return {u, rev: false, moving: t >= T.down[0] && t < T.down[1], y: a.y, base: 0};
  }
  const u = 1 - tw(t, T.up[0], T.up[1] - T.up[0]);
  const a = along(PINK_PATH, u);
  return {u, rev: true, moving: t < T.up[1], y: a.y, base: 80};
};
const stairsOfY = (y: number) => Math.round(((y - LV[0]) / (LV[5] - LV[0])) * 80);
const wastedAt = (t: number) => {
  if (t < T.sB[0]) return 0;
  const w = pinkWalk(t);
  const s = stairsOfY(w.y);
  return w.base === 0 ? s : 160 - s;
};

/** Scene B: the app said FREE. 4B walks all the way down, the washer is running, she walks back up. */
const SceneB: React.FC<{t: number}> = ({t}) => {
  const w = pinkWalk(t);
  const z = zoomB(t);
  const walker: Walker = {u: w.u, look: PINK.look, basket: NEIGHBOUR_LAUNDRY, path: PINK_PATH, moving: w.moving, rev: w.rev, face: -1, expr: t >= T.busy ? 'annoyed' : 'neutral'};
  const bk = tw(t, T.busy, 0.3, backOut);
  const bo = 1 - tw(t, T.up[0] - 0.2, 0.2);
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(${ZX},${ZY}) scale(${z}) translate(${-ZX},${-ZY})`}>
        <Building t={t} walkers={[walker]} machine={{state: 'running', drum: JONAS_LAUNDRY}} hiDoor={false} />
      </g>
      {t >= T.busy && bo > 0 && (
        <g opacity={bo} transform={`translate(430,640) scale(${lerp(0.4, 1, bk)}) translate(-430,-640)`}>
          <rect x={250} y={560} width={360} height={120} rx={26} fill={C.white} stroke={C.coral} strokeWidth={8} />
          <path d="M 520 676 L 586 742 L 560 676 Z" fill={C.white} stroke={C.ink} strokeWidth={5} strokeLinejoin="round" />
          <rect x={516} y={668} width={50} height={14} fill={C.white} />
          <text x={430} y={642} textAnchor="middle" fontFamily={FONT.sans} fontWeight={900} fontSize={58} fill={C.ink}>BUSY?!</text>
        </g>
      )}
    </svg>
  );
};

const jonasWalk = (t: number) => tw(t, T.walk[0], T.walk[1] - T.walk[0]) * 0.93;
const barsOfY = (y: number) => {
  const fl = ((y - LV[0]) / (LV[5] - LV[0])) * 5; // 0 at floor 4 .. 5 in the basement
  return Math.max(0, Math.min(4, Math.ceil(4 - fl + 0.001)));
};

/** Router in Jonas's flat (4A) with signal rings that fade out floor by floor. */
const RouterRings: React.FC<{t: number}> = ({t}) => {
  const rx = 268, ry = LV[0] - 22;
  return (
    <g>
      {[0, 1, 2, 3].map((i) => {
        const ph = (t * 0.55 + i / 4) % 1;
        const r = 30 + ph * 760;
        const op = Math.max(0, 0.75 - ph * 1.15);
        return <circle key={i} cx={rx} cy={ry} r={r} fill="none" stroke={C.teal} strokeWidth={7} opacity={op} />;
      })}
      <rect x={rx - 30} y={ry - 18} width={60} height={26} rx={7} fill={C.navy} stroke={C.ink} strokeWidth={3} />
      <line x1={rx - 18} y1={ry - 18} x2={rx - 24} y2={ry - 44} stroke={C.ink} strokeWidth={4} strokeLinecap="round" />
      <line x1={rx + 18} y1={ry - 18} x2={rx + 24} y2={ry - 44} stroke={C.ink} strokeWidth={4} strokeLinecap="round" />
      <circle cx={rx + 14} cy={ry - 5} r={4} fill={C.green} />
    </g>
  );
};

/** Scene C: Jonas walks down with his phone; the bars drop floor by floor. */
const SceneC: React.FC<{t: number}> = ({t}) => {
  const u = jonasWalk(t);
  const settle = lerp(1.08, 1, tw(t, T.sC[0], 0.4, easeOut));
  const walker: Walker = {u, look: JONAS, basket: null, moving: t >= T.walk[0] && t < T.walk[1], expr: t > T.concrete ? 'annoyed' : 'neutral'};
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(540,800) scale(${settle}) translate(-540,-800)`}>
        <Building t={t} walkers={[walker]} machine={{state: 'running', drum: JONAS_LAUNDRY}} hiDoor>
          <RouterRings t={t} />
          {/* the slabs light up as the signal dies in them */}
          {t >= T.concrete && [1, 2, 3, 4].map((i) => <rect key={i} x={110} y={LV[i]} width={800} height={14} fill={C.coral} opacity={0.75 * tw(t, T.concrete + 0.08 * i, 0.2) * (0.6 + 0.4 * Math.sin(t * 12 + i))} />)}
        </Building>
      </g>
    </svg>
  );
};

/** Scene D: hallway by the basement door. The relay box goes above the door; the signal hops up. */
const SceneD: React.FC<{t: number}> = ({t}) => {
  const settle = lerp(1.1, 1, tw(t, T.sD[0], 0.4, easeOut));
  const placed = t >= T.place;
  const pk = tw(t, T.place, 0.35, backOut);
  const reaching = t >= T.place - 0.7 && t < T.place + 0.35;
  const relay = t >= T.relay;
  const up = t >= T.bars - 0.4;
  const BX = 700, BY = 520; // relay box
  const sockK = tw(t, T.sock, 0.3, backOut);
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(540,900) scale(${settle}) translate(-540,-900)`}>
        <rect x={0} y={0} width={1080} height={FLOOR_Y} fill={C.wall} />
        {/* stair rail going up on the left */}
        <path d={`M 0 760 L 300 470`} stroke={C.ink} strokeWidth={10} strokeLinecap="round" />
        {[0, 1, 2, 3, 4, 5].map((i) => <line key={i} x1={20 + i * 50} y1={FLOOR_Y - 40 - i * 62} x2={20 + i * 50} y2={760 - 20 - i * 48} stroke={C.ink} strokeWidth={5} opacity={0.5} />)}
        {/* basement door, open: dark stairs down */}
        <rect x={570} y={600} width={260} height={FLOOR_Y - 600} fill={C.ink} />
        {[0, 1, 2, 3, 4].map((i) => <rect key={i} x={590 + i * 14} y={720 + i * 90} width={220 - i * 28} height={16} fill={C.navy} opacity={0.85 - i * 0.12} />)}
        <rect x={552} y={584} width={296} height={FLOOR_Y - 584} fill="none" stroke={C.ink} strokeWidth={OW * 1.4} />
        <path d={`M 830 600 L 930 640 L 930 ${FLOOR_Y + 30} L 830 ${FLOOR_Y}`} fill={C.wallDark} stroke={C.ink} strokeWidth={OW} strokeLinejoin="round" />
        <circle cx={912} cy={900} r={9} fill={C.ink} />
        {/* sign */}
        <rect x={600} y={630} width={200} height={54} rx={8} fill={C.white} stroke={C.ink} strokeWidth={4} />
        <text x={700} y={669} textAnchor="middle" fontFamily={FONT.sans} fontWeight={900} fontSize={30} fill={C.ink}>BASEMENT</text>
        {/* floor */}
        <rect x={0} y={FLOOR_Y} width={1080} height={1920 - FLOOR_Y} fill={C.floor} />
        <line x1={0} y1={FLOOR_Y} x2={1080} y2={FLOOR_Y} stroke={C.ink} strokeWidth={OW} />
        {[1230, 1320, 1440, 1600, 1800].map((y) => <line key={y} x1={0} y1={y} x2={1080} y2={y} stroke={C.floorLine} strokeWidth={3} />)}
        {/* signal from the basement climbing to the relay box */}
        {relay && [0, 1, 2, 3, 4].map((i) => {
          const ph = ((t - T.relay) * 1.3 + i / 5) % 1;
          const y = lerp(1080, BY + 40, ph);
          return <circle key={i} cx={BX} cy={y} r={14} fill={C.gold} stroke={C.ink} strokeWidth={4} opacity={Math.sin(Math.PI * ph)} />;
        })}
        {/* waves from the relay box towards upstairs */}
        {up && <Waves x={BX} y={BY - 40} t={t} s={1.6} col={C.green} />}
        {/* relay box */}
        {placed && (
          <g transform={`translate(${BX},${BY}) scale(${pk})`}>
            <rect x={-60} y={-38} width={120} height={66} rx={14} fill={C.teal} stroke={C.ink} strokeWidth={OW} />
            <circle cx={32} cy={-6} r={10} fill={relay && Math.floor(t * 5) % 2 === 0 ? C.green : C.ink} stroke={C.ink} strokeWidth={3} />
            <rect x={-42} y={-20} width={44} height={22} rx={5} fill={C.ink} opacity={0.75} />
            <text x={74} y={10} textAnchor="start" fontFamily={FONT.sans} fontWeight={900} fontSize={30} fill={C.ink}>€6</text>
          </g>
        )}
        {/* the lost sock from Part 3 */}
        <g transform={`translate(960,${FLOOR_Y - 8}) rotate(-80) scale(${1 + 0.25 * Math.max(0, 1 - Math.abs(t - T.sock - 0.2) / 0.4)})`}>
          <path d="M 0 0 q 6 40 -4 60 q -6 18 18 18 q 24 0 18 -22 q -6 -30 -4 -56 Z" fill={C.pink} stroke={C.ink} strokeWidth={5} strokeLinejoin="round" />
        </g>
        {t >= T.sock && [0, 1, 2, 3].map((i) => {
          const a = (i / 4) * Math.PI * 2 + 0.4;
          const r = 60 + 30 * sockK;
          return <line key={i} x1={960 + Math.cos(a) * (r - 22)} y1={FLOOR_Y - 30 + Math.sin(a) * (r - 22)} x2={960 + Math.cos(a) * r} y2={FLOOR_Y - 30 + Math.sin(a) * r} stroke={C.goldDark} strokeWidth={7} strokeLinecap="round" opacity={sockK} />;
        })}
        <Person x={330} y={FLOOR_Y} face={1} pose={reaching ? 'reach' : 'phone'} poseK={reaching ? 1 : 1} expr={up ? 'happy' : 'neutral'} holding={reaching ? C.teal : null} />
      </g>
    </svg>
  );
};

/** Scene E: the neighbour who voted NO gets the first ping. */
const SceneE: React.FC<{t: number}> = ({t}) => {
  const settle = 1 + 0.12 * (1 - tw(t, T.sE[0], 0.35, easeOut));
  const expr = t < T.ping ? 'neutral' : t < T.ping + 0.9 ? 'shock' : 'happy';
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(540,960) scale(${settle}) translate(-540,-960)`}>
        <FlatRoom t={t}>
          <Person x={250} y={FLOOR_Y} face={1} sit pose="phone" look={NOVOTER.look} expr={expr} blink={Math.abs(((t * 0.7) % 3) - 1.5) < 0.04} />
          <CouchFront />
        </FlatRoom>
      </g>
    </svg>
  );
};

export const Part4: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  let scene: React.ReactNode;
  if (t < T.sA[1]) scene = <SceneA t={t} />;
  else if (inS(t, T.sB)) scene = <SceneB t={t} />;
  else if (inS(t, T.sC)) scene = <SceneC t={t} />;
  else if (inS(t, T.sD)) scene = <SceneD t={t} />;
  else if (t < T.cardOut) scene = <SceneE t={t} />;
  else scene = <SceneA t={t - T.end} />;
  const cuts = [T.sB[0], T.sC[0], T.sD[0], T.sE[0], T.cardOut];
  const flash = Math.max(0, ...cuts.map((c) => 1 - Math.abs(t - c) / 0.07)) * 0.35;
  // HUD
  let hud: React.ReactNode = null;
  if (inS(t, T.sB)) {
    const pw = pinkWalk(t);
    hud = <Counter value={wastedAt(t)} bump={pw.moving ? 0.25 * Math.abs(Math.sin(t * 26)) : 0} label="WASTED STAIRS" color={t >= T.busy ? C.coral : C.ink} sub="APP SAID: FREE" />;
  } else if (inS(t, T.sC)) {
    const a = along(JONAS_PATH, jonasWalk(t));
    const b = barsOfY(a.y);
    const bAt = (x: number) => barsOfY(along(JONAS_PATH, jonasWalk(x)).y);
    const changed = bAt(t - 0.25) !== b;
    hud = <WifiMeter bars={b} bump={changed ? 1 - ((t * 4) % 1) : 0} />;
  } else if (inS(t, T.sD)) {
    const k = tw(t, T.bars, 0.6);
    hud = <WifiMeter bars={t < T.bars ? 0 : Math.ceil(4 * k)} bump={Math.max(0, 1 - Math.abs(t - T.bars - 0.6) / 0.3)} />;
  }
  const status = t < T.ping
    ? {label: 'BUSY', sub: 'Someone is washing', color: C.goldDark, progress: 0.9}
    : {label: 'FREE', sub: 'Go now!', color: C.green, progress: 1};
  return (
    <LabelFont.Provider value="sans">
      <AbsoluteFill style={{backgroundColor: C.paper}}>
        <Img src={staticFile('paper.png')} style={{position: 'absolute', width: 1080, height: 1920}} />
        {scene}
        <Phone t={t} at={T.nosig - 0.05} until={T.sA[1] - 0.08} x={70} rot={-3} status={{label: 'NO SIGNAL', sub: 'Washer: ???', color: C.coral, progress: 0, size: 46}} />
        <Phone t={t} at={T.sE[0] + 0.1} until={T.card + 0.4} status={status} statusAt={T.ping} banners={[{title: 'The washer is FREE', sub: 'House washer · now', at: T.ping}]} />
        <AbsoluteFill style={{backgroundColor: C.white, opacity: flash}} />
        <SeriesPill part={4} />
        {hud}
        <Tag t={t} at={T.sock} until={T.sD[1] - 0.1} text="+1 LOST SOCK FOUND" x={560} y={330} />
        <Tag t={t} at={T.sE[0] + 0.2} until={T.card - 0.1} text="1A · VOTED NO" y={330} />
        <Tag t={t} at={T.sA[0] + 0.0} until={T.nosig - 0.15} text="DAY 1" y={330} />
        <Captions t={t} caps={CAPS} />
        <EndCard t={t} at={T.card} out={T.cardOut} next={5} lines={['The landlord', <span style={{color: C.gold}}>found out.</span>]} sub="Follow for Part 5" />
      </AbsoluteFill>
    </LabelFont.Provider>
  );
};
