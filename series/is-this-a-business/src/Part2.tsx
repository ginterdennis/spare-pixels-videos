import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import T from './part2.json';
import {C, easeInOut, easeOut, FPS, lerp, tw} from './theme';
import {Building, LV, MACHINE_X, stairsAt, Walker} from './Building';
import {Basket, JONAS, Person} from './Person';
import {BasementRoom, FLOOR_Y, JONAS_LAUNDRY, NEIGHBOUR_LAUNDRY, Washer} from './Props';
import {CouchFront, FlatRoom, Phone, ScanBeam, SensorBubble} from './Scenes2';
import {Cap, Captions, Counter, Em, EndCard, SeriesPill, Tag} from './UI';

const ZX = MACHINE_X;
const ZY = LV[5] - 60;
const Z = 3.4;
const inS = (t: number, s: number[]) => t >= s[0] && t < s[1];

const CAPS: Cap[] = [
  {at: 0, until: T.stop - 0.05, lines: ['A €10 box on the washer.', <Em>It feels the shaking.</Em>]},
  {at: T.stop + 0.05, until: T.c1[1] - 0.05, lines: ['Shaking stops?', <Em>The load is done.</Em>]},
  {at: T.s3[0] + 0.1, until: T.free3 - 0.05, lines: ['Before Jonas goes down,', <Em>he checks his phone.</Em>]},
  {at: T.free3, until: T.s3[1] - 0.05, lines: ['Free?', <Em>Now he goes.</Em>]},
  {at: T.s5[0] + 0.1, until: T.phone5, lines: ['He loads it', <Em>and scans the sticker.</Em>]},
  {at: T.phone5 + 0.05, until: T.s5[1] - 0.05, lines: ['Now the app knows', <Em>this load is his.</Em>]},
  {at: T.s6[0] + 0.1, until: T.s6[1] - 0.05, lines: ['Back upstairs.', <Em>No waiting around.</Em>]},
  {at: T.s7[0] + 0.1, until: T.nudge7 - 0.05, lines: ['Done?', <Em>His phone buzzes.</Em>]},
  {at: T.nudge7, until: T.s7[1] - 0.05, lines: ['Too slow?', <Em>It nudges him again.</Em>]},
  {at: T.s8[0] + 0.1, until: T.card - 0.05, lines: ['2 trips. 320 stairs.', <Em>Half. And zero waiting.</Em>]},
];

const zoomAt = (t: number) => {
  const zin = (end: number) => lerp(1, Z, tw(t, end - T.zoomIn, T.zoomIn, easeInOut));
  const zout = (start: number) => lerp(Z, 1, tw(t, start, T.zoomOut, easeOut));
  if (inS(t, T.s4)) return zin(T.s4[1]);
  if (inS(t, T.s6)) return zout(T.s6[0]);
  if (inS(t, T.s8)) return zout(T.s8[0]);
  if (t >= T.card) return lerp(1, Z, tw(t, T.cardOut, T.end - T.cardOut, easeInOut));
  return 1;
};

const jonasOverview = (t: number) => {
  const down = (a: number[], base: number, basket: string[] | null) => {
    const u = tw(t, a[0], a[1] - a[0]);
    const mv = t >= a[0] && t < a[1];
    return {w: {u, look: JONAS, basket, moving: mv} as Walker, stairs: base + stairsAt(u), moving: mv};
  };
  const up = (a: number[], base: number, basket: string[] | null) => {
    const u = 1 - tw(t, a[0], a[1] - a[0]);
    const mv = t >= a[0] && t < a[1];
    return {w: {u, look: JONAS, basket, rev: true, moving: mv} as Walker, stairs: base + 80 - stairsAt(u), moving: mv};
  };
  if (inS(t, T.s4)) return down(T.down4, 0, JONAS_LAUNDRY);
  if (inS(t, T.s6)) return up(T.up6, 80, []);
  if (t < T.up8[0]) return down(T.down8, 160, []);
  const r = up(T.up8, 240, JONAS_LAUNDRY);
  if (t >= T.up8[1]) { r.w.moving = false; r.w.face = 1; }
  return r;
};

const Overview: React.FC<{t: number}> = ({t}) => {
  const j = jonasOverview(t);
  let machine: {state: 'running' | 'done' | 'idle'; drum: string[]} = {state: 'idle', drum: []};
  if (inS(t, T.s6)) machine = {state: 'running', drum: JONAS_LAUNDRY};
  if (t >= T.s8[0]) machine = {state: 'done', drum: t < T.up8[0] - 0.1 ? JONAS_LAUNDRY : []};
  if (t >= T.cardOut) machine = {state: 'running', drum: NEIGHBOUR_LAUNDRY};
  const z = zoomAt(t);
  const walkers = t >= T.cardOut ? [] : [j.w];
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(${ZX},${ZY}) scale(${z}) translate(${-ZX},${-ZY})`}>
        <Building t={t} walkers={walkers} machine={machine} />
      </g>
    </svg>
  );
};

/** Opening basement scene (also the loop target). */
const SensorScene: React.FC<{t: number}> = ({t}) => {
  const running = t < T.stop;
  const settle = t >= T.end - 0.01 ? 1 : 1;
  const blink = Math.floor(t * 4) % 2 === 0;
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(700,900) scale(${settle}) translate(-700,-900)`}>
        <BasementRoom t={t}>
          <Washer x={700} y={FLOOR_Y} t={t} state={running ? 'running' : 'done'} drum={NEIGHBOUR_LAUNDRY} sensor={1} sensorBlink={running ? blink : true} qr={1} />
          <SensorBubble t={t} amp={running ? 1 : Math.max(0, 1 - (t - T.stop) / 0.25)} label={running ? 'SHAKING = RUNNING' : 'STILL = DONE'} color={running ? C.gold : C.green} k={1} />
          <Person x={250} y={FLOOR_Y} face={1} pose="idle" look={{hoodie: C.pink, pants: C.ink, hair: '#C8692E', skin: C.skin, shoes: C.white, hairStyle: 'bun'}} expr={running ? 'neutral' : 'happy'} />
        </BasementRoom>
      </g>
    </svg>
  );
};

const Flat: React.FC<{t: number; s0: number}> = ({t, s0}) => {
  const settle = 1 + 0.12 * (1 - tw(t, s0, 0.35, easeOut));
  let expr: 'neutral' | 'happy' | 'shock' = 'neutral';
  if (inS(t, T.s3) && t >= T.free3) expr = 'happy';
  if (inS(t, T.s7)) expr = t < T.done7 + 0.1 ? 'neutral' : t < T.nudge7 ? 'happy' : 'shock';
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(540,960) scale(${settle}) translate(-540,-960)`}>
        <FlatRoom t={t}>
          <Person x={250} y={FLOOR_Y} face={1} sit pose="phone" expr={expr} blink={Math.abs(((t * 0.7) % 3) - 1.5) < 0.04} />
          <CouchFront />
        </FlatRoom>
      </g>
    </svg>
  );
};

const LoadScene: React.FC<{t: number}> = ({t}) => {
  const settle = 1 + 0.18 * (1 - tw(t, T.s5[0], 0.35, easeOut));
  const loaded = t >= T.load5 + 0.3;
  const scanning = t >= T.scan5[0] - 0.15;
  const running = t >= T.start5;
  const pose = t < T.load5 ? 'carry' : t < T.load5 + 0.45 ? 'reach' : scanning ? 'phone' : 'idle';
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(700,900) scale(${settle}) translate(-700,-900)`}>
        <BasementRoom t={t}>
          <Washer x={700} y={FLOOR_Y} t={t} state={running ? 'running' : 'idle'} drum={loaded ? JONAS_LAUNDRY : []} display={running ? '1:50' : undefined} sensor={1} sensorBlink={running && Math.floor(t * 4) % 2 === 0} qr={1} />
          {t >= T.load5 && (
            <g transform={`translate(196,${FLOOR_Y - 58})`}>
              <Basket clothes={t < T.load5 + 0.3 ? JONAS_LAUNDRY : []} sw={6} />
            </g>
          )}
          <Person x={430} y={FLOOR_Y} face={1} pose={pose} poseK={pose === 'reach' ? 0.5 - 0.5 * Math.cos((t - T.load5) * 14) : 1} basket={t < T.load5 ? JONAS_LAUNDRY : null} expr={running ? 'happy' : 'neutral'} holding={pose === 'reach' ? C.gold : null} />
          <ScanBeam t={t} at={T.scan5[0]} dur={T.scan5[1] - T.scan5[0]} from={{x: 532, y: 700}} to={{x: 597, y: 877}} />
        </BasementRoom>
      </g>
    </svg>
  );
};

export const Part2: React.FC = () => {
  const t = useCurrentFrame() / FPS;
  let scene: React.ReactNode;
  let stairs = 0;
  let moving = false;
  if (inS(t, T.c1)) scene = <SensorScene t={t} />;
  else if (inS(t, T.s3)) scene = <Flat t={t} s0={T.s3[0]} />;
  else if (inS(t, T.s5)) { scene = <LoadScene t={t} />; stairs = 80; }
  else if (inS(t, T.s7)) { scene = <Flat t={t} s0={T.s7[0]} />; stairs = 160; }
  else {
    scene = <Overview t={t} />;
    const j = jonasOverview(t);
    stairs = j.stairs;
    moving = j.moving;
  }
  if (t >= T.cardOut) stairs = Math.round(lerp(320, 0, tw(t, T.cardOut, 0.35, easeInOut)));
  const totalPop = Math.max(0, 1 - Math.abs(t - T.total8 - 0.1) / 0.35);
  const bump = (moving ? 0.25 * Math.abs(Math.sin(t * 26)) : 0) + 0.9 * totalPop;
  const cuts = [T.s3[0], T.s4[0], T.s5[0], T.s6[0], T.s7[0], T.s8[0]];
  const flash = Math.max(0, ...cuts.map((c) => 1 - Math.abs(t - c) / 0.07)) * 0.35;
  const status = inS(t, T.s3)
    ? t < T.free3
      ? {label: 'BUSY', sub: 'done in ~25 min', color: C.goldDark, progress: 0.78}
      : {label: 'FREE', sub: 'Go now!', color: C.green, progress: 1}
    : inS(t, T.s5)
      ? {label: 'YOURS', sub: 'Done in ~1 h 50', color: C.teal, progress: 0.04}
      : {label: 'DONE', sub: 'Your laundry is ready', color: C.green, progress: 1};
  return (
    <AbsoluteFill style={{backgroundColor: C.paper}}>
      <Img src={staticFile('paper.png')} style={{position: 'absolute', width: 1080, height: 1920}} />
      {scene}
      <Phone t={t} at={T.s3[0] + 0.2} until={T.s3[1] - 0.05} status={status} statusAt={T.free3} />
      <Phone t={t} at={T.phone5} until={T.s5[1] - 0.05} status={status} />
      <Phone t={t} at={T.s7[0] + 0.05} until={T.s7[1] - 0.05} status={status} banners={[{title: 'Your laundry is done!', sub: 'Washer · just now', at: T.done7}, {title: 'Someone is waiting', sub: 'Washer · 10 min later', at: T.nudge7}]} />
      <AbsoluteFill style={{backgroundColor: C.white, opacity: flash}} />
      <SeriesPill part={2} />
      <Counter value={stairs} bump={bump} color={t >= T.total8 && t < T.cardOut ? C.teal : C.ink} sub="PART 1: 640" />
      <Tag t={t} at={T.free3} until={T.s3[1] - 0.1} text="25 MIN LATER" y={330} />
      <Captions t={t} caps={CAPS} />
      <EndCard t={t} at={T.card} out={T.cardOut} next={3} lines={['Would 10 flats pay', <span style={{color: C.gold}}>€1 a month for it?</span>]} />
    </AbsoluteFill>
  );
};
