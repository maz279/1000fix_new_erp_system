/* Prepare deck images: top-crop variants (wide 16:10, half 6:5) + resize.
   Run with NODE_PATH=$(npm root -g) node _ppt_prep_imgs.js  */
'use strict';
const path = require('path');
const fs = require('fs');
const sharp = require('sharp');
const SRC = path.join(__dirname, 'user-guide', 'images');
const OUT = path.join(__dirname, '_ppt_imgs');
fs.mkdirSync(OUT, { recursive: true });

const WIDE = ['s-login', 's-home', 's-grid', 's-portals'];
const HALF = ['s-landing', 's-directory', 's-megamenu', 's-tellme', 's-dark', 's-bengali',
  's-record', 's-report', 's-writer', 's-dispatch', 's-console', 's-coverage', 's-journeys',
  's-mobile-nav', 'w-M02', 'w-M27', 'w-M11', 'w-M13', 'w-M15', 'w-M17', 'w-M51', 'w-M56',
  'w-M23', 'w-M26', 'w-M29'];

async function crop(name, ratio, tag, maxW) {
  const src = path.join(SRC, name + '.png');
  if (!fs.existsSync(src)) { console.log('MISSING', name); return; }
  const meta = await sharp(src).metadata();
  const targetH = Math.min(meta.height, Math.round(meta.width * ratio));
  let pipe = sharp(src).extract({ left: 0, top: 0, width: meta.width, height: targetH });
  if (meta.width > maxW) pipe = pipe.resize({ width: maxW });
  await pipe.png({ compressionLevel: 9 }).toFile(path.join(OUT, name + '-' + tag + '.png'));
}

(async () => {
  for (const n of WIDE) await crop(n, 16 / 10, 'wide', 1600);
  for (const n of HALF) await crop(n, 6 / 5, 'half', 1500);
  fs.copyFileSync(path.join(SRC, 's-mobile-home.png'), path.join(OUT, 's-mobile-home-tall.png'));
  console.log('DONE files=' + fs.readdirSync(OUT).length);
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
