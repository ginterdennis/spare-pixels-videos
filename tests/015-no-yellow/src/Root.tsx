import React from 'react';
import {Composition} from 'remotion';
import {NoYellow} from './Video';
import {T} from './theme';

export const Root: React.FC = () => (
  <Composition id="NoYellow" component={NoYellow} durationInFrames={Math.round(T.end * T.fps)} fps={T.fps} width={1080} height={1920} />
);
