import {loadFont} from '@remotion/fonts';
import {Easing, staticFile} from 'remotion';

export const W = 1080;
export const H = 1920;
export const FPS = 30;

// "Is this a business?" series palettes.
// PAPER = the original look (warm paper, navy ink, gold accent; 022-038).
// NEON = the Sigmoid Horizon "Neon Eclipse" night version (user, 28 Nov 2026): same house and cast at night,
// light lavender line art on dark walls, brand accents (cyan, mint, sun-pink). Brand rules: brand/README.md.
const PAPER = {
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
  shade: '#1C2140',
};

const NEON: typeof PAPER = {
  paper: '#05030B',      // void
  ink: '#CFC6FF',        // line art: light lavender, reads as neon on the dark walls
  navy: '#2A1F52',
  wall: '#140E2A',
  wallDark: '#0F0A21',
  basement: '#0B0818',
  floor: '#1A1336',
  floorLine: '#33275F',
  earth: '#0E0A1C',
  stair: '#1D1540',
  gold: '#22E6FF',       // Jonas's hoodie and the series accent become horizon-cyan
  goldDark: '#12A8C4',
  teal: '#3DFFB0',       // topic-business mint
  tealLight: '#9DFFD8',
  coral: '#FF5ADF',      // sun-pink: emphasis
  pink: '#FF2FD0',
  lilac: '#B05CFF',
  sky: '#5B8CFF',
  white: '#0E0A1C',      // cards, bubbles and screens become night panels; their C.ink text and outlines stay light
  skin: '#F2C29B',
  skin2: '#C98B62',
  skin3: '#8D5A3B',
  hair: '#3A2A22',
  glass: '#26306A',
  machine: '#221B44',
  metal: '#3E3768',
  green: '#3DFFB0',
  shade: '#000000',     // full-frame dimming overlays (paper look: navy ink)
};

export type Look = 'neon' | 'paper';
/** The series look. 'neon' for every new video since 28 Nov 2026 (brand rule); 'paper' only to re-render old parts. */
export const LOOK: Look = 'neon';
export const C = LOOK === 'neon' ? NEON : PAPER;
export const C_PAPER = PAPER;
/** A colour that only exists in one scene: nc(paperHex, neonHex). Never hard-code a hex without it. */
export const nc = (paper: string, neon: string) => (LOOK === 'neon' ? neon : paper);
/** The hard offset shadow of the paper look becomes a soft violet glow in the neon look. */
export const HARD_SHADOW = LOOK === 'neon' ? '0 0 40px rgba(176,92,255,0.35)' : '10px 10px 0 rgba(28,33,64,0.35)';
/** Full-frame background image in public/. */
export const BG_FILE = LOOK === 'neon' ? 'night.png' : 'paper.png';
/** Brand colours for the UI layer (brand/tokens.json). */
export const BRAND = {
  void: '#05030B', night: '#0E0A1C', dusk: '#1E1636', starlight: '#F2F7FF', haze: '#A49DC4',
  magenta: '#FF2FD0', ultraviolet: '#B05CFF', cyan: '#22E6FF', sunPink: '#FF5ADF', mint: '#3DFFB0',
  gradient: 'linear-gradient(90deg, #FF2FD0 0%, #B05CFF 50%, #22E6FF 100%)',
};

export const FONT = {sans: 'Inter', pixel: 'Silkscreen', script: 'Pacifico', mono: 'JBMono', display: 'Unbounded'};

const fontFiles: [string, string, string][] = [
  ['Inter', 'Inter-Black.ttf', '900'],
  ['Inter', 'Inter-ExtraBold.ttf', '800'],
  ['Inter', 'Inter-Bold.ttf', '700'],
  ['Silkscreen', 'Silkscreen.ttf', '400'],
  ['Silkscreen', 'Silkscreen-Bold.ttf', '700'],
  ['Pacifico', 'Pacifico.ttf', '400'],
  ['JBMono', 'JBMono-Bold.ttf', '700'],
  ['JBMono', 'JBMono-SemiBold.ttf', '600'],
  ['Unbounded', 'Unbounded-ExtraBold.ttf', '800'],
  ['Unbounded', 'Unbounded-Black.ttf', '900'],
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
