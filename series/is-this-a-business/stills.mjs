// Render stills from the bundle with one browser. Usage: node stills.mjs <CompositionId> 0 4.5 9.8 ...
import {openBrowser, renderStill, selectComposition} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';

const [id, ...times] = process.argv.slice(2);
const serveUrl = path.resolve('build');
const browserExecutable = '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
fs.mkdirSync('stills', {recursive: true});
const browser = await openBrowser('chrome', {browserExecutable});
const composition = await selectComposition({serveUrl, id, puppeteerInstance: browser, browserExecutable});
for (const s of times) {
  const frame = Math.round(parseFloat(s) * 30);
  await renderStill({serveUrl, composition, frame, output: `stills/${id}-t${s}.png`, puppeteerInstance: browser, browserExecutable, imageFormat: 'png'});
}
await browser.close({silent: true});
console.log('stills ok');
