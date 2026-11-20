import React from 'react';
import {Composition} from 'remotion';
import {Part1} from './Part1';
import {Part2} from './Part2';
import {Part3} from './Part3';
import T1 from './part1.json';
import T2 from './part2.json';
import T3 from './part3.json';

export const Root: React.FC = () => (
  <>
    <Composition id="Part1" component={Part1} durationInFrames={Math.round(T1.end * 30)} fps={30} width={1080} height={1920} />
    <Composition id="Part2" component={Part2} durationInFrames={Math.round(T2.end * 30)} fps={30} width={1080} height={1920} />
    <Composition id="Part3" component={Part3} durationInFrames={Math.round(T3.end * 30)} fps={30} width={1080} height={1920} />
  </>
);
