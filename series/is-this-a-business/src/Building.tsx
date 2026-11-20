import React from 'react';
import {C, FONT, OW} from './theme';
import {Look, Person} from './Person';
import {Washer} from './Props';

// Cross-section of the house: floors 4..0 and the basement (-1).
export const BX0 = 110;
export const BX1 = 910;
export const ROOF = 352;
export const LV = [492, 622, 752, 882, 1012, 1162]; // floor lines: 4, 3, 2, 1, 0, -1
export const LABELS = ['4', '3', '2', '1', '0', '-1'];
export const SA = 330; // stair x (left end)
export const SB = 650; // stair x (right end)
export const STEPS_PER_FLIGHT = 16;
export const MACHINE_X = 842;
export const DOOR_L = 196;
export const DOOR_R = 824;
export const PS = 0.16; // person scale in the overview

type Pt = {x: number; y: number};

/** Path from a flat door on level `lv` down to the washer. */
export const pathFrom = (lv: number, side: 'L' | 'R' = 'L'): Pt[] => {
  const pts: Pt[] = [{x: side === 'L' ? DOOR_L : DOOR_R, y: LV[lv]}];
  for (let k = lv; k < 5; k++) {
    const xs = k % 2 === 0 ? SA : SB;
    const xe = k % 2 === 0 ? SB : SA;
    pts.push({x: xs, y: LV[k]});
    pts.push({x: xe, y: LV[k + 1]});
  }
  pts.push({x: MACHINE_X - 82, y: LV[5]});
  return pts;
};
export const JONAS_PATH = pathFrom(0, 'L');

const lens = (p: Pt[]) => {
  const L = [0];
  for (let i = 1; i < p.length; i++) L.push(L[i - 1] + Math.hypot(p[i].x - p[i - 1].x, p[i].y - p[i - 1].y));
  return L;
};

/** Position, facing and distance walked at fraction u (0..1) along a path. */
export const along = (p: Pt[], u: number) => {
  const L = lens(p);
  const total = L[L.length - 1];
  const d = Math.min(total, Math.max(0, u * total));
  let i = 1;
  while (i < p.length - 1 && L[i] < d) i++;
  const seg = L[i] - L[i - 1] || 1;
  const k = (d - L[i - 1]) / seg;
  const x = p[i - 1].x + (p[i].x - p[i - 1].x) * k;
  const y = p[i - 1].y + (p[i].y - p[i - 1].y) * k;
  const face: 1 | -1 = p[i].x >= p[i - 1].x ? 1 : -1;
  return {x, y, face, dist: d, total};
};

/** Stairs climbed/descended so far on JONAS_PATH at fraction u (16 per flight, only on the stair segments). */
export const stairsAt = (u: number) => {
  const a = along(JONAS_PATH, u);
  return Math.round(((a.y - LV[0]) / (LV[5] - LV[0])) * 5 * STEPS_PER_FLIGHT);
};

const Flight: React.FC<{x0: number; y0: number; x1: number; y1: number}> = ({x0, y0, x1, y1}) => {
  const n = 8;
  const run = (x1 - x0) / n;
  const rise = (y1 - y0) / n;
  let d = `M ${x0} ${y0}`;
  for (let i = 0; i < n; i++) {
    d += ` L ${x0 + run * (i + 1)} ${y0 + rise * i} L ${x0 + run * (i + 1)} ${y0 + rise * (i + 1)}`;
  }
  const under = `${d} L ${x1} ${y1 + 16} L ${x0} ${y0 + 16} Z`;
  return (
    <g>
      <path d={under} fill={C.stair} stroke={C.ink} strokeWidth={OW * 0.6} strokeLinejoin="round" />
    </g>
  );
};

const Door: React.FC<{x: number; y: number; label: string; hi?: boolean}> = ({x, y, label, hi}) => (
  <g>
    <rect x={x - 26} y={y - 88} width={52} height={88} rx={4} fill={hi ? C.gold : C.wallDark} stroke={C.ink} strokeWidth={OW * 0.6} />
    <circle cx={x + 14} cy={y - 42} r={3.5} fill={C.ink} />
    <text x={x} y={y - 98} textAnchor="middle" fontFamily={FONT.pixel} fontWeight={700} fontSize={17} fill={C.ink} opacity={0.7}>{label}</text>
  </g>
);

export type Walker = {u: number; look: Look; basket: string[] | null; path?: Pt[]; visible?: boolean; moving?: boolean; rev?: boolean; face?: 1 | -1; opacity?: number; expr?: 'neutral' | 'tired' | 'annoyed' | 'happy'};

/** The whole house in cross-section, with walkers on the stairs. */
export const Building: React.FC<{t: number; walkers: Walker[]; machine?: {state: 'running' | 'done' | 'idle'; drum: string[]; pile?: string[] | null}; hiDoor?: boolean; machineGlow?: number}> = ({t, walkers, machine, hiDoor = true, machineGlow = 0}) => (
  <g>
    {/* ground and earth */}
    <rect x={0} y={LV[4]} width={1080} height={1920 - LV[4]} fill={C.earth} />
    <line x1={0} y1={LV[4]} x2={1080} y2={LV[4]} stroke={C.ink} strokeWidth={OW} />
    {[[40, 1080], [70, 1130], [990, 1060], [1030, 1150], [60, 1250], [1010, 1240]].map(([x, y], i) => <circle key={i} cx={x} cy={y} r={7} fill={C.ink} opacity={0.18} />)}
    {/* rooms */}
    {LV.map((y, i) => {
      const top = i === 0 ? ROOF : LV[i - 1] + 14;
      return <rect key={i} x={BX0} y={top} width={BX1 - BX0} height={y - top} fill={i === 5 ? C.basement : C.wall} />;
    })}
    {/* slabs */}
    {LV.map((y, i) =>
      i === 5 ? (
        <rect key={`s${i}`} x={BX0} y={y} width={BX1 - BX0} height={14} fill={C.navy} />
      ) : (
        <g key={`s${i}`}>
          <rect x={BX0} y={y} width={SA + 4 - BX0} height={14} fill={C.navy} />
          <rect x={SB - 4} y={y} width={BX1 - SB + 4} height={14} fill={C.navy} />
        </g>
      ),
    )}
    <rect x={BX0 - 10} y={ROOF - 16} width={BX1 - BX0 + 20} height={18} rx={4} fill={C.navy} stroke={C.ink} strokeWidth={OW * 0.6} />
    <rect x={720} y={ROOF - 70} width={40} height={56} fill={C.wallDark} stroke={C.ink} strokeWidth={OW * 0.6} />
    {/* stairs */}
    {[0, 1, 2, 3, 4].map((k) => {
      const xs = k % 2 === 0 ? SA : SB;
      const xe = k % 2 === 0 ? SB : SA;
      return <Flight key={k} x0={xs} y0={LV[k]} x1={xe} y1={LV[k + 1]} />;
    })}
    {/* doors: 2 flats per floor */}
    {[0, 1, 2, 3, 4].map((i) => (
      <g key={`d${i}`}>
        <Door x={DOOR_L} y={LV[i]} label={`${LABELS[i]}A`} hi={hiDoor && i === 0} />
        <Door x={DOOR_R} y={LV[i]} label={`${LABELS[i]}B`} />
      </g>
    ))}
    {/* outer walls */}
    <rect x={BX0} y={ROOF} width={BX1 - BX0} height={LV[5] + 14 - ROOF} fill="none" stroke={C.ink} strokeWidth={OW} />
    {/* floor labels */}
    {LV.map((y, i) => (
      <text key={`l${i}`} x={BX0 - 18} y={y - 40} textAnchor="end" fontFamily={FONT.pixel} fontWeight={700} fontSize={30} fill={C.ink}>{LABELS[i]}</text>
    ))}
    {/* the one washer */}
    {machineGlow > 0 && <circle cx={MACHINE_X} cy={LV[5] - 62} r={92} fill={C.gold} opacity={0.35 * machineGlow} />}
    {machine && <Washer x={MACHINE_X} y={LV[5]} s={0.3} t={t} state={machine.state} drum={machine.drum} pile={machine.pile ?? null} ow={OW * 0.7} />}
    {/* walkers */}
    {walkers.map((w, i) => {
      if (w.visible === false) return null;
      const a = along(w.path ?? JONAS_PATH, w.u);
      return (
        <Person key={i} x={a.x} y={a.y} s={PS} face={w.moving === false ? (w.face ?? 1) : w.rev ? ((-a.face) as 1 | -1) : a.face} walk={w.moving === false ? null : a.dist / 26} opacity={w.opacity ?? 1} pose={w.basket ? 'carry' : 'idle'} basket={w.basket} look={w.look} expr={w.expr ?? 'neutral'} ow={3.4} />
      );
    })}
  </g>
);
