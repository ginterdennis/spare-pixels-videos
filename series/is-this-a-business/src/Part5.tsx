import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import T from './part5.json';
import {backOut, C, easeInOut, easeOut, FONT, FPS, lerp, OW, tw, BG_FILE} from './theme';
import {Building, DOOR_L, DOOR_R, LV, Walker} from './Building';
import {JONAS, Look, Person} from './Person';
import {BasementRoom, FLOOR_Y, JONAS_LAUNDRY, Note, Washer} from './Props';
import {NEIGHBOURS} from './Part1';
import {Phone} from './Scenes2';
import {Cap, Captions, Counter, Em, EndCard, LabelFont, SeriesPill, Tag} from './UI';

// Part 5 "The landlord found out" (finale of case 1): a notice on the washer says the box must go by
// Friday. No box = 640 stairs again. Jonas shows the landlord one number: angry notes since the box = 0.
// The landlord owns 12 houses and orders a box for every one. Voiced (A+).
const inS = (t: number, s: number[]) => t >= s[0] && t < s[1];
export const LANDLORD: Look = {hoodie: '#8A6A4A', pants: '#55586E', hair: '#C9C9C9', skin: C.skin, shoes: C.ink, hairStyle: 'bald', landlord: true};

const CAPS: Cap[] = [
  {at: 0, until: T.stamp - 0.05, lines: ['The landlord', <Em>found the box.</Em>]},
  {at: T.stamp, until: T.sA[1] - 0.05, lines: ['"Remove it', <Em>by Friday."</Em>]},
  {at: T.sB[0] + 0.1, until: T.panic - 0.05, lines: ['No box =', <Em>640 stairs again.</Em>]},
  {at: T.panic, until: T.sB[1] - 0.05, lines: ['The whole house', <Em>panics.</Em>]},
  {at: T.sC[0] + 0.1, until: T.zero - 0.05, lines: ['Jonas showed him', <Em>one number.</Em>]},
  {at: T.zero, until: T.sC[1] - 0.05, lines: ['Angry washer notes', <Em c={C.green}>since the box: 0.</Em>]},
  {at: T.sD[0] + 0.1, until: T.grid0 - 0.05, lines: ['He owns', <Em>12 houses.</Em>]},
  {at: T.grid0, until: T.sD[1] - 0.05, lines: ['12 houses × 10 flats × €1', <Em c={C.green}>= €120 a month.</Em>]},
  {at: T.sE[0] + 0.1, until: T.ask - 0.05, lines: ['From 640 stairs', <Em>to 12 customers.</Em>]},
  {at: T.ask, until: T.card - 0.05, lines: ['Would YOUR landlord', <Em>say YES or NO?</Em>]},
];

/** The landlord's notice, taped on the washer. `k` pop-in, `stampK` BY FRIDAY stamp, `crossK` crossed out. */
const Notice: React.FC<{t: number; k: number; stampK: number; crossK: number}> = ({t, k, stampK, crossK}) => {
  const cx = 770, cy = 905;
  return (
    <g transform={`translate(${cx},${cy}) rotate(-4) scale(${lerp(1.25, 1, k)})`} opacity={Math.min(1, k * 3)}>
      <rect x={-150} y={-160} width={300} height={320} fill={C.white} stroke={C.ink} strokeWidth={OW * 0.8} />
      <rect x={-50} y={-178} width={100} height={30} fill={C.tealLight} opacity={0.9} transform="rotate(-3)" />
      <text x={0} y={-96} textAnchor="middle" fontFamily={FONT.sans} fontWeight={900} fontSize={50} fill={C.coral}>NOTICE</text>
      <line x1={-110} y1={-76} x2={110} y2={-76} stroke={C.ink} strokeWidth={4} />
      <text x={0} y={-30} textAnchor="middle" fontFamily={FONT.sans} fontWeight={800} fontSize={34} fill={C.ink}>Remove this</text>
      <text x={0} y={12} textAnchor="middle" fontFamily={FONT.sans} fontWeight={800} fontSize={34} fill={C.ink}>device.</text>
      <text x={110} y={58} textAnchor="end" fontFamily={FONT.script} fontSize={28} fill={C.navy}>the landlord</text>
      {stampK > 0 && (
        <g transform={`translate(0,112) rotate(-7) scale(0.92) scale(${lerp(2.2, 1, stampK)})`} opacity={Math.min(1, stampK * 2)}>
          <rect x={-128} y={-40} width={256} height={74} rx={10} fill="none" stroke={C.coral} strokeWidth={8} />
          <text x={0} y={16} textAnchor="middle" fontFamily={FONT.sans} fontWeight={900} fontSize={46} fill={C.coral}>BY FRIDAY!</text>
        </g>
      )}
      {crossK > 0 && (
        <g stroke={C.ink} strokeWidth={14} strokeLinecap="round" opacity={0.85}>
          <line x1={-130} y1={-140} x2={lerp(-130, 130, crossK)} y2={lerp(-140, 140, crossK)} />
          {crossK > 0.5 && <line x1={130} y1={-140} x2={lerp(130, -130, (crossK - 0.5) * 2)} y2={lerp(-140, 140, (crossK - 0.5) * 2)} />}
        </g>
      )}
    </g>
  );
};

/** Basement close-up: running washer, the box, the notice. Used for scene A (and the loop) and E. */
const Basement: React.FC<{t: number; end?: boolean}> = ({t, end = false}) => {
  const t0 = end ? T.sE[0] : 0;
  const push = end ? lerp(1.12, 1.0, tw(t, t0, 0.5, easeOut)) : lerp(1.0, 1.08, tw(t, -0.5, 4.0, easeInOut));
  const k = end ? 1 : tw(t, -0.25, 0.4, backOut);
  const stampK = end ? 1 : tw(t, T.stamp, 0.22, backOut);
  const crossK = end ? tw(t, T.cross, 0.45, easeInOut) : 0;
  const noteK = end ? tw(t, T.note, 0.3, backOut) : 0;
  const expr = end ? (t > T.note ? 'happy' : 'neutral') : t < T.stamp ? 'neutral' : 'shock';
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(760,900) scale(${push}) translate(-760,-900)`}>
        <BasementRoom t={t}>
          <Washer x={770} y={FLOOR_Y} t={t} state="running" drum={JONAS_LAUNDRY} sensor={1} sensorBlink={Math.floor(t * 4) % 2 === 0} qr={1} display="0:42" />
          <Notice t={t} k={k} stampK={stampK} crossK={crossK} />
          {noteK > 0 && <Note x={790} y={1000} text="Make me 12." k={noteK} rot={6} size={40} />}
          <Person x={350} y={FLOOR_Y} face={1} pose={end ? (t > T.note + 0.3 ? 'wave' : 'idle') : 'carry'} poseK={t} basket={end ? null : JONAS_LAUNDRY} expr={expr} />
        </BasementRoom>
      </g>
    </svg>
  );
};

/** Speech bubble next to a flat door (overview). */
const DoorBubble: React.FC<{lv: number; side: 'L' | 'R'; text: string; k: number; o: number}> = ({lv, side, text, k, o}) => {
  const w = Math.max(150, text.length * 17 + 44);
  const y = LV[lv] - 128;
  const x = side === 'L' ? DOOR_L + 40 : DOOR_R - 40 - w;
  const tailX = side === 'L' ? x + 26 : x + w - 26;
  return (
    <g opacity={o} transform={`translate(${tailX},${y + 60}) scale(${lerp(0.4, 1, k)}) translate(${-tailX},${-(y + 60)})`}>
      <path d={`M ${tailX - 12} ${y + 56} L ${side === 'L' ? tailX - 26 : tailX + 26} ${y + 84} L ${tailX + 12} ${y + 56} Z`} fill={C.white} stroke={C.ink} strokeWidth={4} strokeLinejoin="round" />
      <rect x={x} y={y - 4} width={w} height={66} rx={16} fill={C.white} stroke={C.coral} strokeWidth={6} />
      <text x={x + w / 2} y={y + 40} textAnchor="middle" fontFamily={FONT.sans} fontWeight={800} fontSize={30} fill={C.ink}>{text}</text>
    </g>
  );
};

const lookAt = (lv: number, side: 'L' | 'R'): Look => (lv === 0 && side === 'L' ? JONAS : NEIGHBOURS.find((n) => n.lv === lv && n.side === side)!.look);
const PANIC: {lv: number; side: 'L' | 'R'; text: string}[] = [
  {lv: 0, side: 'R', text: 'NOT the stairs!'},
  {lv: 2, side: 'L', text: 'Noooo!'},
  {lv: 1, side: 'R', text: 'My €1!'},
  {lv: 3, side: 'L', text: 'Told you.'},
  {lv: 4, side: 'R', text: '640 again?!'},
  {lv: 2, side: 'R', text: 'My socks!'},
];

/** Scene B: overview, the stairs counter rolls back to 640, every door opens. */
const SceneB: React.FC<{t: number}> = ({t}) => {
  const settle = lerp(1.1, 1, tw(t, T.sB[0], 0.4, easeOut));
  const walkers: Walker[] = [];
  const bubbles: React.ReactNode[] = [];
  PANIC.forEach((p, i) => {
    const a = T.nb0 + i * T.nbGap;
    if (t < a) return;
    const pk = tw(t, a, 0.3, backOut);
    walkers.push({u: 0, path: [{x: p.side === 'L' ? DOOR_L + 46 : DOOR_R - 46, y: LV[p.lv]}, {x: 0, y: LV[p.lv]}], look: lookAt(p.lv, p.side), basket: null, moving: false, face: p.side === 'L' ? 1 : -1, opacity: Math.min(1, pk * 1.4), expr: 'annoyed'});
    bubbles.push(<DoorBubble key={i} lv={p.lv} side={p.side} text={p.text} k={pk} o={1} />);
  });
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(540,760) scale(${settle}) translate(-540,-760)`}>
        <Building t={t} walkers={walkers} machine={{state: 'idle', drum: []}} hiDoor={false} />
        {bubbles}
      </g>
    </svg>
  );
};

/** Ground-floor hallway: mailboxes, entrance door. */
const Hallway: React.FC<{children?: React.ReactNode}> = ({children}) => (
  <g>
    <rect x={0} y={0} width={1080} height={FLOOR_Y} fill={C.wall} />
    {[0, 1].map((r) => [0, 1, 2, 3, 4].map((c) => <rect key={`${r}${c}`} x={60 + c * 56} y={420 + r * 66} width={50} height={58} rx={4} fill={C.metal} stroke={C.ink} strokeWidth={OW * 0.6} />))}
    {/* entrance door with glass */}
    <rect x={700} y={430} width={300} height={FLOOR_Y - 430} fill={C.navy} stroke={C.ink} strokeWidth={OW} />
    <rect x={740} y={480} width={220} height={300} rx={8} fill="#BFDDEA" stroke={C.ink} strokeWidth={OW * 0.8} />
    <circle cx={730} cy={850} r={11} fill={C.gold} stroke={C.ink} strokeWidth={4} />
    <rect x={0} y={FLOOR_Y} width={1080} height={1920 - FLOOR_Y} fill={C.floor} />
    <line x1={0} y1={FLOOR_Y} x2={1080} y2={FLOOR_Y} stroke={C.ink} strokeWidth={OW} />
    {[1230, 1320, 1440, 1600, 1800].map((y) => <line key={y} x1={0} y1={y} x2={1080} y2={y} stroke={C.floorLine} strokeWidth={3} />)}
    {children}
  </g>
);

/** Plain speech bubble at (x, y) = top-left. */
const Bubble: React.FC<{x: number; y: number; text: string; k: number; o?: number; tail?: 'L' | 'R'; border?: string; size?: number}> = ({x, y, text, k, o = 1, tail = 'L', border = C.ink, size = 44}) => {
  const w = Math.max(220, text.length * size * 0.56 + 60);
  const h = size * 1.9;
  const tx = tail === 'L' ? x + 50 : x + w - 50;
  return (
    <g opacity={o} transform={`translate(${tx},${y + h}) scale(${lerp(0.4, 1, k)}) translate(${-tx},${-(y + h)})`}>
      <path d={`M ${tx - 18} ${y + h - 6} L ${tail === 'L' ? tx - 34 : tx + 34} ${y + h + 44} L ${tx + 18} ${y + h - 6} Z`} fill={C.white} stroke={C.ink} strokeWidth={6} strokeLinejoin="round" />
      <rect x={x} y={y} width={w} height={h} rx={26} fill={C.white} stroke={border} strokeWidth={7} />
      <rect x={tx - 16} y={y + h - 10} width={32} height={12} fill={C.white} />
      <text x={x + w / 2} y={y + h * 0.66} textAnchor="middle" fontFamily={FONT.sans} fontWeight={900} fontSize={size} fill={C.ink}>{text}</text>
    </g>
  );
};

const ANGRY = ['Who moved it?!', 'BUSY again!', 'Wet socks!!'];

/** Scenes C + D1: Jonas (with the phone) vs the landlord in the hallway. */
const SceneC: React.FC<{t: number}> = ({t}) => {
  const inD = t >= T.sD[0];
  const s0 = inD ? T.sD[0] : T.sC[0];
  const settle = lerp(1.1, 1, tw(t, s0, 0.4, easeOut));
  const happy = t >= T.turn;
  const whoK = tw(t, T.who, 0.3, backOut);
  const whoO = 1 - tw(t, T.phone - 0.1, 0.2);
  const ownK = tw(t, T.own, 0.3, backOut);
  const notesOut = tw(t, T.zero, 0.5, easeInOut);
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(540,900) scale(${settle}) translate(-540,-900)`}>
        <Hallway>
          {/* angry notes swirling round the landlord until the zero lands */}
          {t >= T.phone && notesOut < 1 && ANGRY.map((n, i) => {
            const nk = tw(t, T.phone + 0.15 + i * 0.25, 0.3, backOut);
            const fly = notesOut;
            const x = [565, 585, 555][i] + fly * (i % 2 ? 600 : -600);
            const y = [540, 730, 920][i] - fly * 260;
            return nk > 0 ? <Note key={i} x={x} y={y} text={n} k={nk * 0.78} rot={[-8, 6, -5][i]} size={42} /> : null;
          })}
          <Person x={820} y={FLOOR_Y} s={0.95} face={-1} pose={happy ? 'wave' : 'hips'} poseK={t} look={LANDLORD} expr={happy ? 'happy' : t >= T.zero ? 'shock' : 'annoyed'} />
          <Person x={250} y={FLOOR_Y} s={0.95} face={1} pose="phone" expr={t >= T.zero ? 'smug' : 'neutral'} />
          {t >= T.who && whoO > 0 && <Bubble x={410} y={420} text="Who said you could?!" k={whoK} o={whoO} tail="R" border={C.coral} size={46} />}
          {inD && <Bubble x={400} y={420} text="I own 12 houses." k={ownK} tail="R" border={C.green} size={52} />}
        </Hallway>
      </g>
    </svg>
  );
};

/** Scene D2: the landlord's 12 houses, each getting a box. */
const MiniHouse: React.FC<{x: number; y: number; k: number; boxK: number; t: number}> = ({x, y, k, boxK, t}) => (
  <g transform={`translate(${x},${y}) scale(${k})`}>
    <path d="M -95 -70 L 0 -140 L 95 -70 Z" fill={C.coral} stroke={C.ink} strokeWidth={6} strokeLinejoin="round" />
    <rect x={-80} y={-70} width={160} height={150} fill={C.wall} stroke={C.ink} strokeWidth={6} />
    {[[-50, -40], [10, -40], [-50, 10], [10, 10]].map(([wx, wy], i) => <rect key={i} x={wx} y={wy} width={40} height={34} rx={4} fill="#BFDDEA" stroke={C.ink} strokeWidth={4} />)}
    {boxK > 0 && (
      <g transform={`translate(52,68) scale(${boxK})`}>
        <rect x={-30} y={-22} width={60} height={34} rx={8} fill={C.gold} stroke={C.ink} strokeWidth={5} />
        <circle cx={14} cy={-5} r={6} fill={Math.floor(t * 4 + x) % 2 === 0 ? C.green : C.ink} />
      </g>
    )}
  </g>
);

const SceneD2: React.FC<{t: number}> = ({t}) => {
  const settle = lerp(1.08, 1, tw(t, T.grid0, 0.4, easeOut));
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <rect x={0} y={0} width={1080} height={1920} fill={C.paper} opacity={0.0} />
      <g transform={`translate(540,760) scale(${settle}) translate(-540,-760)`}>
        {Array.from({length: 12}, (_, i) => {
          const c = i % 3, r = Math.floor(i / 3);
          const x = 230 + c * 310;
          const y = 470 + r * 220;
          const k = tw(t, T.grid0 + i * 0.05, 0.3, backOut);
          const bk = tw(t, T.grid0 + 0.5 + i * T.gridGap, 0.25, backOut);
          return <MiniHouse key={i} x={x} y={y} k={k * 0.82} boxK={bk} t={t} />;
        })}
      </g>
    </svg>
  );
};

export const Part5: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  let scene: React.ReactNode;
  if (t < T.sA[1]) scene = <Basement t={t} />;
  else if (inS(t, T.sB)) scene = <SceneB t={t} />;
  else if (t < T.grid0) scene = <SceneC t={t} />;
  else if (t < T.sE[0]) scene = <SceneD2 t={t} />;
  else if (t < T.cardOut) scene = <Basement t={t} end />;
  else scene = <Basement t={t - T.end} />;
  const cuts = [T.sB[0], T.sC[0], T.sD[0], T.grid0, T.sE[0], T.cardOut];
  const flash = Math.max(0, ...cuts.map((c) => 1 - Math.abs(t - c) / 0.07)) * 0.35;
  let hud: React.ReactNode = null;
  if (inS(t, T.sB)) {
    const k = tw(t, T.roll[0], T.roll[1] - T.roll[0], easeInOut);
    const v = lerp(320, 640, k);
    const moving = k > 0 && k < 1;
    hud = <Counter value={v} bump={moving ? 0.2 * Math.abs(Math.sin(t * 26)) : 0} label="STAIRS PER LOAD" color={k > 0.02 ? C.coral : C.ink} sub="NO BOX" />;
  } else if (t >= T.grid0 && t < T.sE[0]) {
    const n = Math.max(0, Math.min(12, Math.floor((t - T.grid0 - 0.5) / T.gridGap) + 1));
    hud = <Counter value={n} bump={n > 0 && n < 12 ? 0.6 * (1 - (((t - T.grid0 - 0.5) / T.gridGap) % 1)) : 0} label="BOXES ORDERED" color={C.green} />;
  } else if (t >= T.sE[0] && t < T.card) {
    hud = <Counter value={320} bump={0} label="STAIRS PER LOAD" color={C.green} sub="THE BOX STAYS" />;
  }
  const phoneStatus = t < T.zero
    ? {label: '14', sub: 'angry notes last month', color: C.coral, progress: 0.9, size: 110}
    : {label: '0', sub: 'angry notes since the box', color: C.green, progress: 1, size: 130};
  return (
    <LabelFont.Provider value="sans">
      <AbsoluteFill style={{backgroundColor: C.paper}}>
        <Img src={staticFile(BG_FILE)} style={{position: 'absolute', width: 1080, height: 1920}} />
        {scene}
        <Phone t={t} at={T.phone} until={T.sC[1] - 0.08} x={70} rot={-3} status={phoneStatus} statusAt={T.zero} />
        <AbsoluteFill style={{backgroundColor: C.white, opacity: flash}} />
        <SeriesPill part={5} />
        {hud}
        <Tag t={t} at={T.sC[0] + 0.15} until={T.grid0 - 0.1} text="THE LANDLORD" x={700} y={330} />
        <Tag t={t} at={T.sE[0] + 0.15} until={T.card - 0.1} text="FRIDAY" y={330} />
        <Captions t={t} caps={CAPS} />
        <EndCard t={t} at={T.card} out={T.cardOut} next={6} kicker="CASE 1 · CLOSED" lines={['Next: a new problem.', <span style={{color: C.gold}}>Is THAT a business?</span>]} />
      </AbsoluteFill>
    </LabelFont.Provider>
  );
};
