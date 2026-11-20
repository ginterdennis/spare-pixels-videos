import React, {useLayoutEffect, useMemo, useRef} from 'react';
import {H, W} from './theme';

/** The "phone screen": a grid of NX x NY pixels. At zoom 1 it is 720 px wide on the stage. */
export const NX = 380;
export const NY = 463;
export const P0 = 720 / NX;
export const ZMAX = 450;
export const FX = 540; // focal point on the stage
export const FY = 905;
export const CU = 190.5; // screen-pixel coordinate held at the focal point (pixel 190,231 centre)
export const CV = 231.5;

export type Mode = 'yellow' | 'sunset';
type RGB = [number, number, number];

const YELLOW: RGB = [255, 230, 0];
const BAYER4 = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5].map((v) => (v + 0.5) / 16);
const bayer = (u: number, v: number) => BAYER4[(v % 4) * 4 + (u % 4)];
const hash = (x: number, y: number) => {
  let h = (x * 374761393 + y * 668265263) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
};
const mix = (a: RGB, b: RGB, k: number): RGB => [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k];
const ramp = (stops: [number, RGB][], s: number): RGB => {
  for (let i = 1; i < stops.length; i++) {
    if (s <= stops[i][0]) {
      const [s0, c0] = stops[i - 1];
      const [s1, c1] = stops[i];
      return mix(c0, c1, (s - s0) / (s1 - s0));
    }
  }
  return stops[stops.length - 1][1];
};
const smooth = (x: number, a: number, b: number) => {
  const k = Math.min(1, Math.max(0, (x - a) / (b - a)));
  return k * k * (3 - 2 * k);
};

const SKY: [number, RGB][] = [
  [0, [14, 10, 44]],
  [0.3, [52, 22, 104]],
  [0.55, [138, 36, 128]],
  [0.75, [226, 70, 106]],
  [0.9, [255, 128, 72]],
  [1, [255, 178, 88]],
];
const SEA: [number, RGB][] = [
  [0, [70, 30, 96]],
  [0.25, [38, 20, 78]],
  [1, [8, 7, 26]],
];

/** Original pixel-art synthwave sunset. Pixel (190,231) — the one we zoom into — is pure screen yellow. */
function sunsetPixel(u: number, v: number): RGB {
  const HZ = 300;
  const sunCx = 190.5, sunCy = 236, sunR = 64;
  const dx = u + 0.5 - sunCx, dy = v + 0.5 - sunCy;
  const d = Math.hypot(dx, dy);
  if (v < HZ) {
    const cuts = [[257, 260], [268, 272], [280, 285], [292, 298]];
    const cut = cuts.some(([a, b]) => v >= a && v < b);
    if (d < sunR && !cut) {
      const k = Math.max(0, (v - 236) / 62);
      const band = Math.floor(k * 5 + bayer(u, v) - 0.5) / 5;
      return mix(YELLOW, [255, 96, 70], Math.max(0, Math.min(1, band)));
    }
    // mountains on both sides, kept away from the sun
    const ridge = 16 + 12 * Math.sin(u * 0.045) + 8 * Math.sin(u * 0.11 + 1.3) + 5 * Math.sin(u * 0.27 + 0.7);
    const edge = smooth(Math.abs(u - 190), 72, 150);
    const top = HZ - Math.max(0, ridge) * edge;
    if (v >= top && edge > 0.02) {
      return v < top + 1.5 ? [92, 40, 112] : [34, 16, 62];
    }
    const s = v / HZ;
    const sb = Math.floor(s * 16 + bayer(u, v) - 0.5) / 16;
    let c = ramp(SKY, Math.max(0, Math.min(1, sb)));
    // warm halo around the sun
    if (d < sunR * 1.7) {
      const g = (1 - (d - sunR) / (sunR * 0.7)) * 0.4;
      const gq = Math.floor(g * 4 + bayer(u, v)) / 4;
      c = mix(c, [255, 160, 96], Math.max(0, Math.min(0.45, gq)));
    }
    if (s < 0.5 && hash(u, v) > 0.9925) {
      c = mix(c, [235, 230, 255], 0.85);
    }
    return c;
  }
  const s = (v - HZ) / (NY - HZ);
  if (v < HZ + 2) return [255, 150, 92];
  const sb = Math.floor(s * 8 + bayer(u, v) - 0.5) / 8;
  let c = ramp(SEA, Math.max(0, Math.min(1, sb)));
  const w = sunR * (0.95 - 0.55 * s);
  const row = v - HZ;
  if (Math.abs(u + 0.5 - sunCx) < w && row % 6 < 2 + (s < 0.3 ? 1 : 0) && hash(Math.floor(u / 5), v) > 0.28) {
    c = mix([255, 214, 70], [255, 96, 96], s);
  }
  return c;
}

function buildImage(mode: Mode) {
  const rgb = new Uint8ClampedArray(NX * NY * 3);
  const rgba = new Uint8ClampedArray(NX * NY * 4);
  for (let v = 0; v < NY; v++) {
    for (let u = 0; u < NX; u++) {
      const c = mode === 'yellow' ? YELLOW : sunsetPixel(u, v);
      const i = v * NX + u;
      rgb[i * 3] = c[0]; rgb[i * 3 + 1] = c[1]; rgb[i * 3 + 2] = c[2];
      rgba[i * 4] = c[0]; rgba[i * 4 + 1] = c[1]; rgba[i * 4 + 2] = c[2]; rgba[i * 4 + 3] = 255;
    }
  }
  return {rgb, rgba};
}

// subpixel emitter colours when off / fully on
const OFF: RGB[] = [[46, 12, 20], [10, 36, 20], [12, 18, 50]];
const FULL: RGB[] = [[255, 52, 64], [52, 255, 110], [60, 110, 255]];
const Q = 24; // brightness levels, so stripes can be batched into a few paths
const css = (c: RGB, a = 1) => `rgba(${c[0] | 0},${c[1] | 0},${c[2] | 0},${a})`;
const LEVEL_COLORS = [0, 1, 2].map((k) => Array.from({length: Q + 1}, (_, l) => css(mix(OFF[k], FULL[k], l / Q))));

export const stripeAlpha = (pitch: number) => {
  const k = Math.min(1, Math.max(0, (pitch - 6) / 22));
  return k * k * (3 - 2 * k);
};

export const PixelWorld: React.FC<{z: number; mode: Mode; style?: React.CSSProperties}> = ({z, mode, style}) => {
  const ref = useRef<HTMLCanvasElement>(null);
  const img = useMemo(() => buildImage(mode), [mode]);
  const off = useMemo(() => {
    const c = document.createElement('canvas');
    c.width = NX; c.height = NY;
    c.getContext('2d')!.putImageData(new ImageData(img.rgba, NX, NY), 0, 0);
    return c;
  }, [img]);

  useLayoutEffect(() => {
    const ctx = ref.current!.getContext('2d')!;
    ctx.clearRect(0, 0, W, H);
    const pitch = P0 * z;
    const sx0 = FX - CU * pitch, sy0 = FY - CV * pitch;
    const sw = NX * pitch, sh = NY * pitch;

    // bezel + emitted glow (only matters while the whole screen is in view)
    if (z < 6) {
      const bez = 20 * z, rad = 58 * z;
      ctx.save();
      ctx.shadowColor = mode === 'yellow' ? 'rgba(255,220,40,0.32)' : 'rgba(255,120,120,0.22)';
      ctx.shadowBlur = 120;
      ctx.fillStyle = '#171b36';
      ctx.beginPath();
      ctx.roundRect(sx0 - bez, sy0 - bez, sw + 2 * bez, sh + 2 * bez, rad);
      ctx.fill();
      ctx.restore();
      ctx.strokeStyle = 'rgba(255,255,255,0.10)';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.roundRect(sx0 - bez, sy0 - bez, sw + 2 * bez, sh + 2 * bez, rad);
      ctx.stroke();
    }

    const i0 = Math.max(0, Math.floor(-sx0 / pitch)), i1 = Math.min(NX - 1, Math.floor((W - sx0) / pitch));
    const j0 = Math.max(0, Math.floor(-sy0 / pitch)), j1 = Math.min(NY - 1, Math.floor((H - sy0) / pitch));
    const a = stripeAlpha(pitch);

    ctx.save();
    ctx.beginPath();
    ctx.roundRect(sx0, sy0, sw, sh, 38 * z);
    ctx.clip();

    if (a < 1) {
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(off, i0, j0, i1 - i0 + 1, j1 - j0 + 1, sx0 + i0 * pitch, sy0 + j0 * pitch, (i1 - i0 + 1) * pitch, (j1 - j0 + 1) * pitch);
    }
    if (a > 0) {
      ctx.globalAlpha = a;
      ctx.fillStyle = '#04050b';
      ctx.fillRect(sx0 + i0 * pitch, sy0 + j0 * pitch, (i1 - i0 + 1) * pitch, (j1 - j0 + 1) * pitch);
      const g = pitch * 0.05;
      const stw = (pitch - 4 * g) / 3;
      const sth = pitch - 2.6 * g;
      const round = stw > 10;
      const r = Math.min(stw * 0.3, 60);
      const big = pitch > 160;
      if (!big) {
        // batched: one path per (channel, brightness level)
        const paths: Path2D[][] = [0, 1, 2].map(() => Array.from({length: Q + 1}, () => new Path2D()));
        for (let j = j0; j <= j1; j++) {
          const y = sy0 + j * pitch + 1.3 * g;
          for (let i = i0; i <= i1; i++) {
            const x = sx0 + i * pitch + g;
            const p = (j * NX + i) * 3;
            for (let k = 0; k < 3; k++) {
              const l = Math.round((img.rgb[p + k] / 255) * Q);
              const xs = x + k * (stw + g);
              if (round) paths[k][l].roundRect(xs, y, stw, sth, r);
              else paths[k][l].rect(xs, y, stw, sth);
            }
          }
        }
        for (let k = 0; k < 3; k++) {
          for (let l = 0; l <= Q; l++) {
            ctx.fillStyle = LEVEL_COLORS[k][l];
            ctx.fill(paths[k][l]);
          }
        }
      } else {
        // close-up: each emitter glows and has a soft glassy highlight
        for (let j = j0; j <= j1; j++) {
          const y = sy0 + j * pitch + 1.3 * g;
          for (let i = i0; i <= i1; i++) {
            const x = sx0 + i * pitch + g;
            const p = (j * NX + i) * 3;
            for (let k = 0; k < 3; k++) {
              const lv = img.rgb[p + k] / 255;
              const xs = x + k * (stw + g);
              const col = mix(OFF[k], FULL[k], lv);
              ctx.save();
              if (lv > 0.05) {
                ctx.shadowColor = css(FULL[k], 0.85 * lv);
                ctx.shadowBlur = pitch * 0.12;
              }
              ctx.fillStyle = css(col);
              ctx.beginPath();
              ctx.roundRect(xs, y, stw, sth, r);
              ctx.fill();
              ctx.restore();
              // inner hot core + highlight
              const gr = ctx.createLinearGradient(xs, y, xs + stw, y);
              gr.addColorStop(0, 'rgba(255,255,255,0)');
              gr.addColorStop(0.5, `rgba(255,255,255,${0.22 * lv})`);
              gr.addColorStop(1, 'rgba(255,255,255,0)');
              ctx.fillStyle = gr;
              ctx.beginPath();
              ctx.roundRect(xs, y, stw, sth, r);
              ctx.fill();
              const hl = ctx.createLinearGradient(xs, y, xs, y + sth * 0.45);
              hl.addColorStop(0, `rgba(255,255,255,${0.10 + 0.12 * lv})`);
              hl.addColorStop(1, 'rgba(255,255,255,0)');
              ctx.fillStyle = hl;
              ctx.beginPath();
              ctx.roundRect(xs + stw * 0.12, y + sth * 0.02, stw * 0.76, sth * 0.45, r * 0.8);
              ctx.fill();
            }
          }
        }
      }
      ctx.globalAlpha = 1;
    }
    ctx.restore();
  }, [z, img, off, mode]);

  return <canvas ref={ref} width={W} height={H} style={{position: 'absolute', inset: 0, ...style}} />;
};
