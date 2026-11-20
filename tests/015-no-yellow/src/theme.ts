import {loadFont} from '@remotion/fonts';
import {Easing, staticFile} from 'remotion';
import timing from './timing.json';

export const T = timing;
export const W = 1080;
export const H = 1920;

// spare.pixels house palette (kit.py)
export const C = {
  bgTop: 'rgb(14,16,32)',
  bgBot: 'rgb(6,7,16)',
  white: 'rgb(246,246,250)',
  gold: 'rgb(255,211,107)',
  pink: 'rgb(255,79,176)',
  cyan: 'rgb(90,200,255)',
  muted: 'rgb(150,156,185)',
  // subpixel emitters
  red: 'rgb(255,52,64)',
  green: 'rgb(52,255,110)',
  blue: 'rgb(60,110,255)',
  yellow: 'rgb(255,230,0)',
};

export const FONT = {
  display: 'Inter',
  pixel: 'Silkscreen',
  mono: 'JBMono',
};

const fontFiles: [string, string, string][] = [
  ['Inter', 'Inter-Black.ttf', '900'],
  ['Inter', 'Inter-ExtraBold.ttf', '800'],
  ['Inter', 'Inter-Bold.ttf', '700'],
  ['Inter', 'Inter-SemiBold.ttf', '600'],
  ['Silkscreen', 'Silkscreen.ttf', '400'],
  ['Silkscreen', 'Silkscreen-Bold.ttf', '700'],
  ['JBMono', 'JBMono-Bold.ttf', '700'],
];
for (const [family, file, weight] of fontFiles) {
  loadFont({family, url: staticFile(file), weight});
}

// Easings
export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);
export const backOut = Easing.out(Easing.back(1.6));

/** 0..1 progress of a tween starting at `start` seconds, lasting `dur` seconds. */
export const tw = (t: number, start: number, dur: number, ease: (x: number) => number = (x) => x) =>
  ease(Math.min(1, Math.max(0, (t - start) / dur)));

/** Fade-in at `a`, fade-out at `b` (each `d` seconds). */
export const window01 = (t: number, a: number, b: number, d = 0.25) =>
  Math.min(tw(t, a, d, easeOut), 1 - tw(t, b, d, easeInOut));

export const lerp = (a: number, b: number, k: number) => a + (b - a) * k;
