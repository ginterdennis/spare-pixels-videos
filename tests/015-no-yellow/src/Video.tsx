import React from 'react';
import {AbsoluteFill, Easing, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, easeInOut, easeOut, lerp, T, tw} from './theme';
import {CU, CV, FX, FY, NX, NY, P0, PixelWorld, ZMAX} from './PixelWorld';
import {Cyan, Gold, Green, Headline, HeadEntry, Hud, Pink, Red, Reticle, StripeLabels, Sub, SubEntry} from './UI';
import {EyeScene} from './EyeScene';
import {Cards, CtaSwatches} from './Cards';

const HEADS: HeadEntry[] = [
  {at: -1, lines: ['Your phone has', <><Pink>zero</Pink> <Gold>yellow</Gold> lights.</>]},
  {at: T.pixelHeadline, lines: ['Every pixel is', <Cyan>3 tiny lights.</Cyan>]},
  {at: T.rgHeadline, lines: [<>Only <Red>red</Red> + <Green>green</Green></>, 'are switched on.']},
  {at: T.eyeStart, lines: ['So why do you', <Gold>see yellow?</Gold>]},
  {at: T.eyeHead2, lines: ["Your eye can't", <Gold>tell them apart.</Gold>]},
  {at: T.cardsHead, lines: ['Every colour is', <Cyan>the same trick.</Cyan>]},
  {at: T.outStart, lines: [<Gold>Just 3 lights.</Gold>, 'Your brain paints', 'everything else.']},
  {at: T.cta, lines: [<>Comment <Gold>a colour.</Gold></>, "I'll zoom into it."]},
  {at: T.loop - 0.05, lines: ['Your phone has', <><Pink>zero</Pink> <Gold>yellow</Gold> lights.</>]},
];

const SUBS: SubEntry[] = [
  {at: T.hookSub, until: T.pixelHeadline, text: "Let's zoom in."},
  {at: T.noYellowSub, until: T.worldOut + 0.1, text: 'Not one yellow light.'},
  {at: T.brainSub, until: T.eyeEnd + 0.1, text: 'Your brain makes up the yellow.'},
];

const zoomIn = Easing.bezier(0.62, 0, 0.18, 1);
const zoomOut = Easing.bezier(0.55, 0, 0.25, 1);
export const zoomAt = (t: number) => {
  if (t < T.zoomStart) return 1;
  if (t < T.zoomEnd) return Math.exp(Math.log(ZMAX) * zoomIn((t - T.zoomStart) / (T.zoomEnd - T.zoomStart)));
  if (t < T.outStart) return ZMAX;
  if (t < T.outEnd) return Math.exp(Math.log(ZMAX) * (1 - zoomOut((t - T.outStart) / (T.outEnd - T.outStart))));
  return 1;
};

/** A light sheen sweeping across the yellow screen in the first second, so the hook moves immediately. */
const Sheen: React.FC<{t: number}> = ({t}) => {
  const k = tw(t, 0.12, 0.85, easeInOut);
  if (k <= 0 || k >= 1) return null;
  return (
    <div style={{position: 'absolute', left: FX - CU * P0, top: FY - CV * P0, width: NX * P0, height: NY * P0, borderRadius: 38, overflow: 'hidden'}}>
      <div style={{position: 'absolute', top: -200, left: lerp(-500, 900, k), width: 260, height: NY * P0 + 400, rotate: '18deg',
        background: 'linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.55) 50%, rgba(255,255,255,0) 100%)'}} />
    </div>
  );
};

/** Everything on screen at time t (seconds). Pure function of t so the end can cross-fade into the opening frame. */
const Scene: React.FC<{t: number}> = ({t}) => {
  const z = zoomAt(t);
  const mode = t < 20 ? 'yellow' : 'sunset';
  const worldOp = t < T.worldIn ? 1 - tw(t, T.worldOut, 0.4, easeInOut) : tw(t, T.worldIn, 0.25, easeOut);
  const arrive = 1 - tw(t, T.zoomEnd, 0.35, easeOut);
  const worldScale = t < T.worldIn ? lerp(1, 0.9, tw(t, T.worldOut, 0.4, easeInOut)) * (1 + 0.03 * (t >= T.zoomEnd ? arrive : 0)) : lerp(1.08, 1, tw(t, T.worldIn, 0.35, easeOut));
  const hudOp = t < T.worldIn ? 1 - tw(t, T.worldOut, 0.3, easeInOut) : Math.max(Math.min(tw(t, T.outStart, 0.3, easeOut), 1 - tw(t, T.cta, 0.3, easeInOut)), tw(t, T.loop + 0.1, 0.35, easeInOut));
  const labelOp = tw(t, T.lblR - 0.05, 0.1) * (1 - tw(t, T.worldOut, 0.3, easeInOut));
  const flash = Math.max(0, 1 - Math.abs(t - (T.worldIn + 0.1)) / 0.15) * 0.22 + Math.max(0, 1 - Math.abs(t - T.zoomEnd) / 0.12) * 0.12;
  const loopK = tw(t, T.loop, 0.5, Easing.bezier(0.5, 0, 0.3, 1));
  const shadeK = worldOp * Math.min(1, Math.max(0, (z - 1.15) / 0.5));
  const halo = mode === 'yellow' || loopK > 0.5 ? 'rgba(255,214,40,' : 'rgba(255,110,120,';
  const haloK = z < 3 ? 1 - (z - 1) / 2 : 0;
  return (
    <AbsoluteFill style={{background: `linear-gradient(180deg, ${C.bgTop} 0%, ${C.bgBot} 100%)`, overflow: 'hidden'}}>
      <div style={{position: 'absolute', inset: 0, background: `radial-gradient(60% 40% at 50% 47%, ${halo}${0.16 * haloK * worldOp}) 0%, rgba(0,0,0,0) 70%)`}} />
      {worldOp > 0 ? (
        <div style={{position: 'absolute', inset: 0, opacity: worldOp, scale: String(worldScale), transformOrigin: `540px ${FY}px`}}>
          <PixelWorld z={z} mode={mode} />
          {loopK > 0 ? <PixelWorld z={1} mode="yellow" style={{clipPath: `circle(${lerp(64 * P0, 1150, loopK)}px at ${FX}px ${FY}px)`}} /> : null}
        </div>
      ) : null}
      {t < T.zoomStart ? <Sheen t={t} /> : null}
      <Reticle t={t} />
      {labelOp > 0 ? <StripeLabels t={t} opacity={labelOp} /> : null}
      <EyeScene t={t} />
      <Cards t={t} />
      <CtaSwatches t={t} />
      {/* top/bottom shade so the headline and HUD always read over bright pixels */}
      <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: 520, background: 'linear-gradient(180deg, rgba(6,7,16,0.96) 0%, rgba(6,7,16,0.94) 80%, rgba(6,7,16,0) 100%)',
        opacity: shadeK}} />
      <div style={{position: 'absolute', left: 0, top: 1330, width: 1080, height: 590, background: 'linear-gradient(0deg, rgba(6,7,16,0.97) 0%, rgba(6,7,16,0.95) 86%, rgba(6,7,16,0) 100%)',
        opacity: shadeK}} />
      <Headline t={t} entries={HEADS} />
      <Sub t={t} entries={SUBS} />
      {hudOp > 0 ? <Hud t={t} z={z} opacity={hudOp} /> : null}
      <div style={{position: 'absolute', inset: 0, background: C.gold, opacity: flash, mixBlendMode: 'screen'}} />
      <div style={{position: 'absolute', inset: 0, background: 'radial-gradient(120% 80% at 50% 50%, rgba(0,0,0,0) 60%, rgba(0,0,0,0.35) 100%)'}} />
    </AbsoluteFill>
  );
};

export const NoYellow: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return <Scene t={frame / fps} />;
};
