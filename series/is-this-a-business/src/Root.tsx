import React from 'react';
import {Composition} from 'remotion';
import {Part1} from './Part1';
import {Part2} from './Part2';
import {Part3} from './Part3';
import {Part4} from './Part4';
import {Part5} from './Part5';
import {Case2P1} from './Case2P1';
import T1 from './part1.json';
import T2 from './part2.json';
import T3 from './part3.json';
import T4 from './part4.json';
import T5 from './part5.json';
import TC2 from './c2p1.json';

export const Root: React.FC = () => (
  <>
    <Composition id="Part1" component={Part1} durationInFrames={Math.round(T1.end * 30)} fps={30} width={1080} height={1920} />
    <Composition id="Part1UI" component={Part1} defaultProps={{uiOnly: true}} durationInFrames={Math.round(T1.end * 30)} fps={30} width={1080} height={1920} />
    <Composition id="Part2" component={Part2} durationInFrames={Math.round(T2.end * 30)} fps={30} width={1080} height={1920} />
    <Composition id="Part3" component={Part3} durationInFrames={Math.round(T3.end * 30)} fps={30} width={1080} height={1920} />
    <Composition id="Part4" component={Part4} durationInFrames={Math.round(T4.end * 30)} fps={30} width={1080} height={1920} />
    <Composition id="Part5" component={Part5} durationInFrames={Math.round(T5.end * 30)} fps={30} width={1080} height={1920} />
    <Composition id="Case2Part1" component={Case2P1} durationInFrames={Math.round(TC2.end * 30)} fps={30} width={1080} height={1920} />
  </>
);
