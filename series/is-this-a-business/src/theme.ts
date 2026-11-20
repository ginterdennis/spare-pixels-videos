import {loadFont} from '@remotion/fonts';
import {Easing, staticFile} from 'remotion';

export const W = 1080;
export const H = 1920;
export const FPS = 30;

// "Is this a business?" series palette: warm paper, navy ink (spare.pixels navy), gold accent.
export const C = {
  paper: '#F3ECE0',
  ink: '#1C2140',
  navy: '#283163',
  wall: '#E9DFCE',
  wallDark: '#DCCFB9',
  basement: '#D8CCB6',
  floor: '#C9B99D',
  floorLine: '#B5A385',
  earth: '#BFA88A',
  stair: '#D9C8AA',
  gold: '#FFC94D',
  goldDark: '#E8A92A',
  teal: '#2F8F89',
  tealLight: '#A6D5CE',
  coral: '#EF6A57',
  pink: '#F28DB2',
  lilac: '#B79BE0',
  sky: '#8FC1E3',
  white: '#FBF8F2',
  skin: '#F2C29B',
  skin2: '#C98B62',
  skin3: '#8D5A3B',
  hair: '#3A2A22',
  glass: '#A9CBE0',
  machine: '#F8F6F0',
  metal: '#D7DBE2',
  green: '#3FA36A',
};

export const FONT = {sans: 'Inter', pixel: 'Silkscreen', script: 'Pacifico', mono: 'JBMono'};

const fontFiles: [string, string, string][] = [
  ['Inter', 'Inter-Black.ttf', '900'],
  ['Inter', 'Inter-ExtraBold.ttf', '800'],
  ['Inter', 'Inter-Bold.ttf', '700'],
  ['Silkscreen', 'Silkscreen.ttf', '400'],
  ['Silkscreen', 'Silkscreen-Bold.ttf', '700'],
  ['Pacifico', 'Pacifico.ttf', '400'],
  ['JBMono', 'JBMono-Bold.ttf', '700'],
];
for (const [family, file, weight] of fontFiles) loadFont({family, url: staticFile(file), weight});

export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);
export const backOut = Easing.out(Easing.back(1.7));

export const clamp01 = (x: number) => Math.min(1, Math.max(0, x));
/** 0..1 progress of a tween starting at `start`, lasting `dur` seconds. */
export const tw = (t: number, start: number, dur: number, ease: (x: number) => number = (x) => x) => ease(clamp01((t - start) / dur));
export const lerp = (a: number, b: number, k: number) => a + (b - a) * k;
export const win = (t: number, a: number, b: number, dIn = 0.2, dOut = 0.2) => Math.min(tw(t, a, dIn, easeOut), 1 - tw(t, b - dOut, dOut, easeInOut));

/** Outline width used everywhere (screen px). */
export const OW = 6;
