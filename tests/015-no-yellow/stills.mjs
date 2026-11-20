// Render several stills from the bundle with one browser. Usage: node stills.mjs 0 4.5 9.8 ...
import {openBrowser, renderStill, selectComposition} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';

const serveUrl = path.resolve('build');
const browserExecutable = '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
fs.mkdirSync('stills', {recursive: true});
const browser = await openBrowser('chrome', {browserExecutable});
const composition = await selectComposition({serveUrl, id: 'NoYellow', puppeteerInstance: browser, browserExecutable});
for (const s of process.argv.slice(2)) {
  const frame = Math.round(parseFloat(s) * 30);
  const t0 = Date.now();
  await renderStill({serveUrl, composition, frame, output: `stills/t${s}.png`, puppeteerInstance: browser, browserExecutable, imageFormat: 'png'});
  console.log(`t=${s}s frame ${frame}: ${Date.now() - t0} ms`);
}
await browser.close({silent: true});
