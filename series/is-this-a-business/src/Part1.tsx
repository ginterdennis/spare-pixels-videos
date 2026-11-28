import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import T from './part1.json';
import {C, clamp01, easeInOut, easeOut, FPS, lerp, tw, BG_FILE} from './theme';
import {along, Building, JONAS_PATH, LV, MACHINE_X, pathFrom, stairsAt, Walker} from './Building';
import {Basket, JONAS, Look, Person} from './Person';
import {BasementRoom, Clock, FLOOR_Y, JONAS_LAUNDRY, NEIGHBOUR_LAUNDRY, Note, Washer} from './Props';
import {Cap, Captions, Counter, Em, EndCard, LabelFont, SeriesPill, Tag} from './UI';

const ZX = MACHINE_X;
const ZY = LV[5] - 60;
const Z = 3.4;

const inS = (t: number, s: number[]) => t >= s[0] && t < s[1];

const CAPS: Cap[] = [
  {at: 0, until: T.s2[0] - 0.08, lines: ['How one load of laundry', <>became <Em>640 stairs.</Em></>]},
  {at: T.s2[0] + 0.1, until: T.s3[0] - 0.05, lines: ["It's taken.", <Em>No idea for how long.</Em>]},
  {at: T.s3[0] + 0.12, until: T.s4[0] - 0.05, lines: ['He tries again', <Em>an hour later.</Em>]},
  {at: T.s4[0] + 0.1, until: T.clock4[0] - 0.1, lines: ["Done. But someone's", <><Em>wet laundry</Em> is still in it.</>]},
  {at: T.clock4[0], until: T.s5[0] - 0.05, lines: ['He waits 20 minutes.', <Em>Nobody comes.</Em>]},
  {at: T.s5[0] + 0.12, until: T.s6[0] - 0.05, lines: ['Back up. Back down.', <Em>80 stairs each way.</Em>]},
  {at: T.s6[0] + 0.1, until: T.s7[0] - 0.05, lines: ['Still there.', <Em>So he moves it out.</Em>]},
  {at: T.s7[0] + 0.12, until: T.s8[0] - 0.05, lines: ['His load is done.', <Em>{"He's 10 minutes late."}</Em>]},
  {at: T.s8[0] + 0.1, until: T.s9[0] - 0.05, lines: ['Someone moved HIS laundry.', <Em>{"Now he's the problem."}</Em>]},
  {at: T.s9[0] + 0.1, until: T.crowd9 - 0.08, lines: ['4 trips. 640 stairs.', <Em>For one load.</Em>]},
  {at: T.crowd9, until: T.card - 0.05, lines: ['Now picture 10 flats.', <Em>One machine.</Em>]},
];

export const NEIGHBOURS: {look: Look; lv: number; side: 'L' | 'R'; off: number; spd: number; basket: string[]}[] = [
  {look: {hoodie: C.pink, pants: C.ink, hair: '#C8692E', skin: C.skin, shoes: C.white, hairStyle: 'bun'}, lv: 0, side: 'R', off: 0.1, spd: 0.55, basket: NEIGHBOUR_LAUNDRY},
  {look: {hoodie: C.teal, pants: '#6B5A4A', hair: C.hair, skin: C.skin2, shoes: C.ink, hairStyle: 'short'}, lv: 1, side: 'L', off: 0.45, spd: 0.62, basket: [C.white, C.sky, C.navy]},
  {look: {hoodie: C.coral, pants: C.navy, hair: '#E7C36A', skin: C.skin, shoes: C.white, hairStyle: 'long'}, lv: 1, side: 'R', off: 0.8, spd: 0.5, basket: [C.lilac, C.white, C.pink]},
  {look: {hoodie: C.lilac, pants: C.ink, hair: C.hair, skin: C.skin3, shoes: C.white, hairStyle: 'curly'}, lv: 2, side: 'L', off: 0.25, spd: 0.58, basket: [C.gold, C.teal, C.white]},
  {look: {hoodie: C.sky, pants: '#4E4A6B', hair: '#8E8E8E', skin: C.skin, shoes: C.ink, hairStyle: 'bald'}, lv: 2, side: 'R', off: 0.6, spd: 0.47, basket: [C.navy, C.white, C.sky]},
  {look: {hoodie: C.green, pants: C.ink, hair: C.hair, skin: C.skin2, shoes: C.white, hairStyle: 'cap', cap: C.navy}, lv: 3, side: 'L', off: 0.05, spd: 0.6, basket: [C.coral, C.white, C.gold]},
  {look: {hoodie: C.navy, pants: '#7A6A58', hair: '#C8692E', skin: C.skin, shoes: C.white, hairStyle: 'short'}, lv: 3, side: 'R', off: 0.7, spd: 0.52, basket: [C.white, C.white, C.sky]},
  {look: {hoodie: C.white, pants: C.teal, hair: C.hair, skin: C.skin3, shoes: C.ink, hairStyle: 'bun'}, lv: 4, side: 'L', off: 0.35, spd: 0.66, basket: [C.pink, C.gold, C.lilac]},
  {look: {hoodie: C.goldDark, pants: C.ink, hair: '#E7C36A', skin: C.skin, shoes: C.white, hairStyle: 'curly'}, lv: 4, side: 'R', off: 0.9, spd: 0.6, basket: [C.teal, C.white, C.navy]},
];
const NB_PATHS = NEIGHBOURS.map((n) => pathFrom(n.lv, n.side));

/** Overview zoom: 1 = whole house; Z = close on the washer. */
const zoomAt = (t: number) => {
  const zin = (end: number) => lerp(1, Z, tw(t, end - T.zoomIn, T.zoomIn, easeInOut));
  const zout = (start: number) => lerp(Z, 1, tw(t, start, T.zoomOut, easeOut));
  if (inS(t, T.s1)) return zin(T.s1[1]);
  if (inS(t, T.s3)) return t < T.up3[0] ? zout(T.s3[0]) : zin(T.s3[1]);
  if (inS(t, T.s5)) return t < T.up5[0] ? zout(T.s5[0]) : zin(T.s5[1]);
  if (inS(t, T.s7)) return t < T.up7[0] ? zout(T.s7[0]) : zin(T.s7[1]);
  if (t >= T.s9[0]) return zout(T.s9[0]);
  return 1;
};

/** Jonas on the overview: path fraction, direction, basket, visibility. */
const jonasOverview = (t: number): {w: Walker; stairs: number; moving: boolean} => {
  const down = (a: number[], base: number, basket: string[] | null) => {
    const u = lerp(0, 1, tw(t, a[0], a[1] - a[0]));
    return {w: {u, look: JONAS, basket, moving: t >= a[0] && t < a[1]} as Walker, stairs: base + stairsAt(u), moving: t >= a[0] && t < a[1]};
  };
  const up = (a: number[], base: number, basket: string[] | null) => {
    const u = 1 - tw(t, a[0], a[1] - a[0]);
    return {w: {u, look: JONAS, basket, rev: true, moving: t >= a[0] && t < a[1]} as Walker, stairs: base + 80 - stairsAt(u), moving: t >= a[0] && t < a[1]};
  };
  if (inS(t, T.s1)) {
    const u = lerp(0.03, 1, tw(t, T.walk1[0], T.walk1[1] - T.walk1[0], (x) => 1 - Math.pow(1 - x, 1.5)));
    return {w: {u, look: JONAS, basket: JONAS_LAUNDRY, moving: t < T.walk1[1]}, stairs: stairsAt(u), moving: t < T.walk1[1]};
  }
  if (inS(t, T.s3)) {
    if (t < T.tag3) return up(T.up3, 80, JONAS_LAUNDRY);
    const r = down(T.down3, 160, JONAS_LAUNDRY);
    if (t < T.down3[0]) r.w.visible = false;
    return r;
  }
  if (inS(t, T.s5)) {
    if (t < T.tag5) return up(T.up5, 240, JONAS_LAUNDRY);
    const r = down(T.down5, 320, JONAS_LAUNDRY);
    if (t < T.down5[0]) r.w.visible = false;
    return r;
  }
  if (inS(t, T.s7)) {
    if (t < T.tag7) return up(T.up7, 400, []);
    const r = down(T.down7, 480, []);
    if (t < T.down7[0]) r.w.visible = false;
    return r;
  }
  // s9: back up with his (wet) laundry
  const r = up(T.up9, 560, JONAS_LAUNDRY);
  if (t >= T.up9[1]) {
    r.w.moving = false;
    r.w.face = 1;
  }
  return r;
};

const stairsForCloseUp = (t: number) => (inS(t, T.s2) ? 80 : inS(t, T.s4) ? 240 : inS(t, T.s6) ? 400 : 560);

const Overview: React.FC<{t: number}> = ({t}) => {
  const j = jonasOverview(t);
  const crowdK = tw(t, T.crowd9, 0.35, easeOut) * (1 - tw(t, T.cardOut, 0.35, easeInOut));
  const walkers: Walker[] = [];
  if (crowdK > 0) {
    NEIGHBOURS.forEach((n, i) => {
      const ph = ((t - T.crowd9) * n.spd * 0.9 + n.off) % 2;
      const u = ph < 1 ? ph : 2 - ph;
      walkers.push({u, look: n.look, basket: n.basket, path: NB_PATHS[i], rev: ph >= 1, opacity: crowdK});
    });
  }
  // loop hand-off: at the very end Jonas stands where frame 0 has him
  if (t >= T.cardOut) {
    const k = tw(t, T.cardOut, 0.4, easeInOut);
    walkers.push({u: 0.03 * k, look: JONAS, basket: JONAS_LAUNDRY, moving: false, face: 1});
  } else walkers.push(j.w);
  let machine: {state: 'running' | 'done' | 'idle'; drum: string[]; pile?: string[] | null} = {state: 'running', drum: NEIGHBOUR_LAUNDRY};
  if (t >= T.s3[0] + 0.9) machine = {state: 'done', drum: NEIGHBOUR_LAUNDRY};
  if (t >= T.s6[0]) machine = {state: 'running', drum: JONAS_LAUNDRY, pile: NEIGHBOUR_LAUNDRY};
  if (t >= T.s7[0] + 1.0) machine = {state: 'done', drum: JONAS_LAUNDRY, pile: null};
  if (t >= T.s9[0]) machine = {state: 'running', drum: NEIGHBOUR_LAUNDRY, pile: null};
  if (t >= T.cardOut) machine = {state: 'running', drum: NEIGHBOUR_LAUNDRY};
  const z = zoomAt(t);
  const lblK = t < T.s1[1] ? 1 - tw(t, 1.9, 0.3) : 0;
  const jPos = along(JONAS_PATH, j.w.u);
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(${ZX},${ZY}) scale(${z}) translate(${-ZX},${-ZY})`}>
        <Building t={t} walkers={walkers} machine={machine} />
        {lblK > 0 && (
          <g opacity={lblK}>
            <Label x={jPos.x} y={jPos.y - 128} text="JONAS" bg={C.gold} />
            <Label x={MACHINE_X} y={LV[5] - 150} text="WASHER" bg={C.white} />
          </g>
        )}
      </g>
    </svg>
  );
};

const Label: React.FC<{x: number; y: number; text: string; bg: string}> = ({x, y, text, bg}) => {
  const w = text.length * 19 + 26;
  return (
    <g transform={`translate(${x},${y})`}>
      <rect x={-w / 2} y={-22} width={w} height={40} rx={10} fill={bg} stroke={C.ink} strokeWidth={4} />
      <path d="M -8 18 L 0 30 L 8 18 Z" fill={C.ink} />
      <text x={0} y={8} textAnchor="middle" fontFamily="Silkscreen" fontWeight={700} fontSize={22} fill={C.ink}>{text}</text>
    </g>
  );
};

/** Jonas in the basement close-ups. */
const CloseUp: React.FC<{t: number}> = ({t}) => {
  const s0 = inS(t, T.s2) ? T.s2[0] : inS(t, T.s4) ? T.s4[0] : inS(t, T.s6) ? T.s6[0] : T.s8[0];
  // settle from the overview zoom
  const settle = 1 + 0.18 * (1 - tw(t, s0, 0.35, easeOut));
  let jx = 300, face: 1 | -1 = 1, walk: number | null = null, pose: 'carry' | 'idle' | 'reach' | 'hips' = 'carry';
  let expr: 'neutral' | 'tired' | 'shock' | 'annoyed' | 'happy' = 'neutral';
  let basket: string[] | null = JONAS_LAUNDRY;
  let floorBasket: string[] | null = null;
  let poseK = 1, sweat = 0, tap = 0;
  let holding: string | null = null;
  let washer: React.ComponentProps<typeof Washer> = {x: 700, y: FLOOR_Y, t, state: 'running', drum: NEIGHBOUR_LAUNDRY};
  let clock: number | null = null;
  let note = 0;
  const leave = (at: number) => {
    if (t >= at - 0.12) face = -1;
    if (t >= at) {
      const d = (t - at) * 820;
      jx = jx - d;
      walk = d / 42;
    }
  };
  if (inS(t, T.s2)) {
    expr = t < s0 + 0.9 ? 'shock' : 'tired';
    sweat = tw(t, s0 + 0.5, 0.4);
    leave(T.leave2);
  } else if (inS(t, T.s4)) {
    washer = {...washer, state: 'done', sock: true};
    expr = 'annoyed';
    clock = 20 * tw(t, T.clock4[0], T.clock4[1] - T.clock4[0], easeInOut);
    if (t >= T.clock4[0]) { tap = (t - T.clock4[0]) * 18; expr = 'tired'; }
    leave(T.leave4);
  } else if (inS(t, T.s6)) {
    jx = 430;
    washer = {...washer, state: t < T.start6 ? 'done' : 'running', sock: t < T.move6[0] + 0.3, drum: t < T.move6[0] + 0.45 ? NEIGHBOUR_LAUNDRY : t < T.load6 ? [] : JONAS_LAUNDRY, pile: NEIGHBOUR_LAUNDRY, pileK: tw(t, T.move6[0] + 0.2, 0.6, easeOut), display: t < T.start6 ? 'END' : '1:50'};
    expr = t < T.move6[0] ? 'annoyed' : 'neutral';
    if (t >= T.move6[0] - 0.15 && t < T.leave6 - 0.1) {
      pose = 'reach';
      const cyc = (t - T.move6[0]) * 2.6;
      poseK = 0.5 - 0.5 * Math.cos(cyc * Math.PI * 2);
      basket = null;
      floorBasket = t < T.load6 ? JONAS_LAUNDRY : [];
      jx = 430;
      if (t >= T.move6[0] && t < T.load6) holding = t < T.move6[0] + 0.45 ? C.pink : C.gold;
    }
    if (t >= T.leave6 - 0.1) basket = [];
    if (t >= T.start6) expr = 'happy';
    leave(T.leave6);
  } else {
    // s8: someone else's load is running, his is dumped on top with a note
    washer = {...washer, state: 'running', drum: NEIGHBOUR_LAUNDRY, pile: JONAS_LAUNDRY, pileK: 1};
    basket = [];
    expr = t < s0 + 0.25 ? 'neutral' : 'shock';
    sweat = tw(t, s0 + 0.6, 0.3);
    note = tw(t, T.note8, 0.35, easeOut);
  }
  return (
    <svg width={1080} height={1920} style={{position: 'absolute'}}>
      <g transform={`translate(700,900) scale(${settle}) translate(-700,-900)`}>
        <BasementRoom t={t}>
          {clock !== null && <Clock x={480} y={560} minutes={clock} />}
          <Washer {...washer} />
          {note > 0 && <Note x={660} y={655} text="was in my way!" k={note} rot={-5} />}
          {floorBasket && (
            <g transform={`translate(196,${FLOOR_Y - 58})`}>
              <Basket clothes={floorBasket} sw={6} />
            </g>
          )}
          <Person x={jx} y={FLOOR_Y} face={face} walk={walk} pose={pose} poseK={poseK} expr={expr} basket={basket} sweat={sweat} tap={tap} holding={holding} />
        </BasementRoom>
      </g>
    </svg>
  );
};

/** uiOnly: captions, counter, pill, tags, end card and cut flashes on a transparent background,
 *  for compositing over other picture sources (028: the same story rendered in Blender). */
export const Part1: React.FC<{uiOnly?: boolean}> = ({uiOnly = false}) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const closeUp = inS(t, T.s2) || inS(t, T.s4) || inS(t, T.s6) || inS(t, T.s8);
  let stairs: number;
  let moving = false;
  if (closeUp) stairs = stairsForCloseUp(t);
  else {
    const j = jonasOverview(t);
    stairs = j.stairs;
    moving = j.moving && j.w.visible !== false;
  }
  if (t >= T.cardOut) stairs = Math.round(lerp(640, 0, tw(t, T.cardOut, 0.35, easeInOut)));
  const totalPop = Math.max(0, 1 - Math.abs(t - T.total9 - 0.1) / 0.35);
  const bump = (moving ? 0.25 * Math.abs(Math.sin(t * 26)) : 0) + 0.9 * totalPop;
  const counterColor = t >= T.total9 && t < T.cardOut ? C.coral : C.ink;
  // tiny white flash on each cut
  const cuts = [T.s2[0], T.s3[0], T.s4[0], T.s5[0], T.s6[0], T.s7[0], T.s8[0], T.s9[0]];
  const flash = Math.max(0, ...cuts.map((c) => 1 - Math.abs(t - c) / 0.07)) * 0.35;
  return (
    <LabelFont.Provider value={uiOnly ? 'sans' : 'pixel'}>
    <AbsoluteFill style={{backgroundColor: uiOnly ? 'transparent' : C.paper}}>
      {!uiOnly && <Img src={staticFile(BG_FILE)} style={{position: 'absolute', width: 1080, height: 1920}} />}
      {!uiOnly && (closeUp ? <CloseUp t={t} /> : <Overview t={t} />)}
      <AbsoluteFill style={{backgroundColor: C.white, opacity: flash}} />
      <SeriesPill part={1} />
      <Counter value={stairs} bump={bump} color={counterColor} />
      <Tag t={t} at={T.tag3} until={T.s3[1] - 0.1} text="1 HOUR LATER" />
      <Tag t={t} at={T.tag5} until={T.s5[1] - 0.1} text="40 MIN LATER" />
      <Tag t={t} at={T.tag7} until={T.s7[1] - 0.1} text="2 HOURS LATER" />
      <Captions t={t} caps={CAPS} />
      <EndCard t={t} at={T.card} out={T.cardOut} next={2} lines={['Could a tiny sensor', 'end the stair trips?']} />
    </AbsoluteFill>
    </LabelFont.Provider>
  );
};
