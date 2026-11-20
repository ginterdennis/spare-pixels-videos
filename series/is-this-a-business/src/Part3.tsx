import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import T from './part3.json';
import {backOut, C, easeInOut, easeOut, FONT, FPS, lerp, OW, tw} from './theme';
import {Building, DOOR_L, DOOR_R, LV, Walker} from './Building';
import {JONAS, Look, Person} from './Person';
import {FLOOR_Y} from './Props';
import {NEIGHBOURS} from './Part1';
import {Cap, Captions, Counter, Em, EndCard, SeriesPill} from './UI';

const inS = (t: number, s: number[]) => t >= s[0] && t < s[1];
const lookAt = (lv: number, side: 'L' | 'R'): Look => (lv === 0 && side === 'L' ? JONAS : NEIGHBOURS.find((n) => n.lv === lv && n.side === side)!.look);

type Vote = {lv: number; side: 'L' | 'R'; text: string; v: 'yes' | 'no' | 'sock'};
const VOTES: Vote[] = [
  {lv: 0, side: 'R', text: 'YES. Finally!', v: 'yes'},
  {lv: 3, side: 'L', text: 'NO. I just knock.', v: 'no'},
  {lv: 2, side: 'R', text: 'YES! No more wet socks.', v: 'yes'},
  {lv: 4, side: 'L', text: 'Can it find my lost sock?', v: 'sock'},
  {lv: 1, side: 'L', text: 'YES.', v: 'yes'},
  {lv: 2, side: 'L', text: "NO. I wash at my mum's.", v: 'no'},
  {lv: 3, side: 'R', text: 'YES, take my €1.', v: 'yes'},
  {lv: 4, side: 'R', text: 'YES. Add a dryer too.', v: 'yes'},
  {lv: 1, side: 'R', text: 'YES!', v: 'yes'},
  {lv: 0, side: 'L', text: 'Obviously YES.', v: 'yes'},
];
const voteAt = (i: number) => T.vote0 + i * T.voteGap;
const tally = (t: number) => {
  let yes = 0, no = 0, sock = 0;
  VOTES.forEach((v, i) => {
    if (t >= voteAt(i) + 0.15) {
      if (v.v === 'yes') yes++;
      else if (v.v === 'no') no++;
      else sock++;
    }
  });
  return {yes, no, sock};
};

const CAPS: Cap[] = [
  {at: 0, until: T.s1[1] - 0.05, lines: ['Would 10 flats pay', <Em>€1 a month for this?</Em>]},
  {at: T.s2[0] + 0.1, until: T.rMonth - 0.05, lines: ['The parts:', <Em>about €10.</Em>]},
  {at: T.rMonth, until: T.s2[1] - 0.05, lines: ['€1 × 10 flats = €10 a month.', <Em>Paid off in month one.</Em>]},
  {at: T.s3[0] + 0.1, until: voteAt(4) - 0.05, lines: ['So Jonas asks', <Em>the whole house.</Em>]},
  {at: voteAt(4), until: voteAt(8) - 0.05, lines: ['Not everyone', <Em>is convinced.</Em>]},
  {at: voteAt(8), until: T.s3[1] - 0.05, lines: ['7 yes. 2 no.', <Em>1 wants his sock back.</Em>]},
  {at: T.s4[0] + 0.1, until: T.card - 0.05, lines: ['So... is this a business?', <Em>Would YOU pay €1?</Em>]},
];

/** Tally marks: groups of five, the fifth crossing the four. */
const Tally: React.FC<{x: number; y: number; n: number; k: number}> = ({x, y, n, k}) => {
  const marks: React.ReactNode[] = [];
  const shown = Math.floor(n * k + 1e-6);
  for (let i = 0; i < shown; i++) {
    const g = Math.floor(i / 5), j = i % 5;
    const gx = x + g * 120;
    if (j < 4) marks.push(<line key={i} x1={gx + j * 22} y1={y} x2={gx + j * 22 + 4} y2={y + 70} stroke={C.ink} strokeWidth={7} strokeLinecap="round" />);
    else marks.push(<line key={i} x1={gx - 10} y1={y + 50} x2={gx + 82} y2={y + 14} stroke={C.coral} strokeWidth={7} strokeLinecap="round" />);
  }
  return <g>{marks}</g>;
};

/** Hallway notice board with Jonas's notice. */
const Board: React.FC<{t: number; tallyK: number}> = ({t, tallyK}) => {
  const s0 = inS(t, T.s4) ? T.s4[0] : 0;
  const settle = s0 > 0 ? 1 + 0.12 * (1 - tw(t, s0, 0.35, easeOut)) : 1;
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(540,900) scale(${settle}) translate(-540,-900)`}>
        <rect x={0} y={0} width={1080} height={FLOOR_Y} fill={C.wall} />
        {/* mailboxes */}
        {[0, 1].map((r) => [0, 1, 2, 3, 4].map((c) => <rect key={`${r}${c}`} x={36 + c * 52} y={400 + r * 62} width={46} height={54} rx={4} fill={C.metal} stroke={C.ink} strokeWidth={OW * 0.6} />))}
        {/* cork board */}
        <rect x={330} y={390} width={590} height={700} rx={14} fill="#8C6239" stroke={C.ink} strokeWidth={OW} />
        <rect x={352} y={412} width={546} height={656} rx={6} fill="#C99A5E" />
        <rect x={364} y={430} width={110} height={130} fill={C.sky} transform="rotate(-6 419 495)" stroke={C.ink} strokeWidth={OW * 0.5} />
        <rect x={800} y={950} width={86} height={100} fill={C.pink} transform="rotate(7 843 1000)" stroke={C.ink} strokeWidth={OW * 0.5} />
        {/* the notice */}
        <g transform="rotate(-2 640 750)">
          <rect x={420} y={448} width={440} height={590} fill={C.white} stroke={C.ink} strokeWidth={OW * 0.8} />
          <circle cx={640} cy={470} r={11} fill={C.coral} stroke={C.ink} strokeWidth={3} />
          <text x={640} y={540} textAnchor="middle" fontFamily={FONT.sans} fontWeight={900} fontSize={42} fill={C.ink}>LAUNDRY</text>
          <text x={640} y={588} textAnchor="middle" fontFamily={FONT.sans} fontWeight={900} fontSize={42} fill={C.ink}>SENSOR?</text>
          <rect x={596} y={612} width={88} height={46} rx={12} fill={C.gold} stroke={C.ink} strokeWidth={OW * 0.8} />
          <circle cx={662} cy={635} r={8} fill={C.green} />
          <text x={640} y={704} textAnchor="middle" fontFamily={FONT.sans} fontWeight={800} fontSize={30} fill={C.coral}>€1 a month per flat</text>
          <line x1={450} y1={738} x2={830} y2={738} stroke={C.ink} strokeWidth={4} />
          <line x1={640} y1={738} x2={640} y2={1012} stroke={C.ink} strokeWidth={4} />
          <text x={545} y={784} textAnchor="middle" fontFamily={FONT.pixel} fontWeight={700} fontSize={30} fill={C.green}>YES</text>
          <text x={735} y={784} textAnchor="middle" fontFamily={FONT.pixel} fontWeight={700} fontSize={30} fill={C.coral}>NO</text>
          <Tally x={462} y={808} n={7} k={tallyK} />
          <Tally x={676} y={808} n={2} k={tallyK} />
          {tallyK > 0.9 && (
            <g transform="translate(700,930)">
              <path d="M 0 0 q 6 40 -4 60 q -6 18 18 18 q 24 0 18 -22 q -6 -30 -4 -56 Z" fill={C.pink} stroke={C.ink} strokeWidth={4} />
              <text x={50} y={58} fontFamily={FONT.sans} fontWeight={900} fontSize={36} fill={C.ink}>1</text>
            </g>
          )}
        </g>
        {/* floor */}
        <rect x={0} y={FLOOR_Y} width={1080} height={1920 - FLOOR_Y} fill={C.floor} />
        <line x1={0} y1={FLOOR_Y} x2={1080} y2={FLOOR_Y} stroke={C.ink} strokeWidth={OW} />
        {[1230, 1320, 1440, 1600, 1800].map((y) => <line key={y} x1={0} y1={y} x2={1080} y2={y} stroke={C.floorLine} strokeWidth={3} />)}
        <Person x={150} y={FLOOR_Y} face={1} pose="reach" poseK={0.75 + 0.25 * Math.sin(t * 3)} expr="happy" />
      </g>
    </svg>
  );
};

/** Receipt card over the board. */
const Receipt: React.FC<{t: number}> = ({t}) => {
  if (!inS(t, T.s2)) return null;
  const k = tw(t, T.s2[0], 0.4, backOut);
  const o = 1 - tw(t, T.s2[1] - 0.2, 0.2);
  const row = (at: number, l: string, r: string, opts: {big?: boolean; color?: string} = {}) => {
    const rk = tw(t, at, 0.25, easeOut);
    return (
      <div style={{display: 'flex', justifyContent: 'space-between', opacity: rk, transform: `translateX(${lerp(-30, 0, rk)}px)`, fontFamily: FONT.mono, fontWeight: 700, fontSize: opts.big ? 46 : 38, lineHeight: opts.big ? '64px' : '56px', color: opts.color ?? C.ink}}>
        <span>{l}</span>
        <span>{r}</span>
      </div>
    );
  };
  return (
    <div style={{position: 'absolute', left: 120, top: 380, width: 790, opacity: o, transform: `translateY(${lerp(120, 0, k)}px) rotate(-1.5deg)`}}>
      <div style={{background: C.white, border: `6px solid ${C.ink}`, borderRadius: 10, padding: '34px 44px 40px', boxShadow: `10px 10px 0 ${C.ink}`}}>
        <div style={{fontFamily: FONT.pixel, fontWeight: 700, fontSize: 34, color: C.navy, letterSpacing: 2, marginBottom: 14}}>WHAT IT COSTS</div>
        {row(T.r1, 'Wi-Fi chip', '€6.25')}
        {row(T.r2, 'Motion sensor', '€3.40')}
        {row(T.r3, 'Cable + tape', 'have it')}
        <div style={{borderTop: `4px dashed ${C.ink}`, margin: '14px 0 10px', opacity: tw(t, T.rTotal - 0.1, 0.2)}} />
        {row(T.rTotal, 'PARTS', '~€10', {big: true})}
        {row(T.rMonth, '10 flats × €1', '€10/mo', {color: C.teal})}
        {row(T.rPaid, 'Paid off', 'month 1', {big: true, color: C.coral})}
      </div>
    </div>
  );
};

/** Speech bubble next to a flat door. */
const Bubble: React.FC<{lv: number; side: 'L' | 'R'; text: string; k: number; o: number; v: Vote['v']}> = ({lv, side, text, k, o, v}) => {
  const w = Math.max(150, text.length * 17 + 44);
  const y = LV[lv] - 128;
  const x = side === 'L' ? DOOR_L + 40 : DOOR_R - 40 - w;
  const border = v === 'yes' ? C.green : v === 'no' ? C.coral : C.lilac;
  const tailX = side === 'L' ? x + 26 : x + w - 26;
  return (
    <g opacity={o} transform={`translate(${tailX},${y + 60}) scale(${lerp(0.4, 1, k)}) translate(${-tailX},${-(y + 60)})`}>
      <path d={`M ${tailX - 12} ${y + 56} L ${side === 'L' ? tailX - 26 : tailX + 26} ${y + 84} L ${tailX + 12} ${y + 56} Z`} fill={C.white} stroke={C.ink} strokeWidth={4} strokeLinejoin="round" />
      <rect x={x} y={y - 4} width={w} height={66} rx={16} fill={C.white} stroke={border} strokeWidth={6} />
      <text x={x + w / 2} y={y + 40} textAnchor="middle" fontFamily={FONT.sans} fontWeight={800} fontSize={30} fill={C.ink}>{text}</text>
    </g>
  );
};

const Vote: React.FC<{t: number}> = ({t}) => {
  const zk = tw(t, T.s3[0], 0.35, easeOut);
  const settle = lerp(1.1, 1, zk);
  const walkers: Walker[] = [];
  const bubbles: React.ReactNode[] = [];
  VOTES.forEach((v, i) => {
    const a = voteAt(i);
    if (t < a) return;
    const pk = tw(t, a, 0.3, backOut);
    walkers.push({u: 0, path: [{x: v.side === 'L' ? DOOR_L + 46 : DOOR_R - 46, y: LV[v.lv]}, {x: 0, y: LV[v.lv]}], look: lookAt(v.lv, v.side), basket: null, moving: false, face: v.side === 'L' ? 1 : -1, opacity: Math.min(1, pk * 1.4)});
    const age = t - a;
    const o = age < 2.6 ? 1 : 1 - Math.min(1, (age - 2.6) / 0.3);
    if (o > 0) bubbles.push(<Bubble key={i} lv={v.lv} side={v.side} text={v.text} k={pk} o={o} v={v.v} />);
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

export const Part3: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  const tl = tally(t);
  const final = t >= T.s4[0];
  const yes = final ? 7 : tl.yes;
  const no = final ? 2 : tl.no;
  let scene: React.ReactNode;
  if (inS(t, T.s3)) scene = <Vote t={t} />;
  else scene = <Board t={t} tallyK={t >= T.s4[0] ? tw(t, T.s4[0] + 0.2, 0.9) * (t >= T.cardOut ? 1 - tw(t, T.cardOut, 0.3) : 1) : 0} />;
  const cuts = [T.s3[0], T.s4[0]];
  const flash = Math.max(0, ...cuts.map((c) => 1 - Math.abs(t - c) / 0.07)) * 0.35;
  const lastVote = Math.max(...VOTES.map((_, i) => (t >= voteAt(i) + 0.15 ? voteAt(i) + 0.15 : -9)));
  const bump = Math.max(0, 1 - (t - lastVote) / 0.25);
  const showCount = t < T.cardOut ? yes : Math.round(lerp(7, 0, tw(t, T.cardOut, 0.3)));
  return (
    <AbsoluteFill style={{backgroundColor: C.paper}}>
      <Img src={staticFile('paper.png')} style={{position: 'absolute', width: 1080, height: 1920}} />
      {scene}
      {inS(t, T.s2) && <AbsoluteFill style={{backgroundColor: C.ink, opacity: 0.12 * tw(t, T.s2[0], 0.3) * (1 - tw(t, T.s2[1] - 0.2, 0.2))}} />}
      <Receipt t={t} />
      <AbsoluteFill style={{backgroundColor: C.white, opacity: flash}} />
      <SeriesPill part={3} />
      <Counter value={showCount} bump={bump} label="YES VOTES" color={C.green} sub={`NO: ${t < T.cardOut ? no : 0}`} />
      <Captions t={t} caps={CAPS} />
      <EndCard t={t} at={T.card} out={T.cardOut} next={4} kicker="YOUR VOTE · PART 4" lines={['Comment YES or NO.', <span style={{color: C.gold}}>If YES wins,</span>, <span style={{color: C.gold}}>Jonas builds it.</span>]} sub="Follow for Part 4" />
    </AbsoluteFill>
  );
};
