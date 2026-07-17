#!/usr/bin/env node
/*
 * Render slideshow sinh nhật -> MP4 1920x1080. Scalable (chunked) cho album lớn.
 * B1: Playwright mở index.html?static, chụp từng slide -> video/frames/fNNN.png
 * B2: mỗi frame -> clip Ken Burns (zoompan) D giây
 * B3: xfade-join theo CỤM (chunk) -> rồi xfade-join các cụm -> video (crossfade, scale tốt)
 * B4: ghép nhạc nền + fade out
 *
 * Chạy:
 *   node tools/render_birthday_video.mjs --seconds 5 --xfade 0.7 --music music.mp3
 *   node tools/render_birthday_video.mjs --skip-shoot --motion none
 */
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { mkdirSync, rmSync, existsSync, readdirSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const BDIR = path.join(ROOT, 'Shopee-birthday');
const VID = path.join(BDIR, 'video');
const FRAMES = path.join(VID, 'frames');
const FINFRAMES = path.join(VID, 'finale');
const CLIPS = path.join(VID, 'clips');
const INDEX = path.join(BDIR, 'index.html');

function arg(name, def) {
  const i = process.argv.indexOf('--' + name);
  if (i < 0) return def;
  const v = process.argv[i + 1];
  return (v && !v.startsWith('--')) ? v : true;
}
const D = parseFloat(arg('seconds', '5'));
const X = parseFloat(arg('xfade', '0.7'));
const FPS = parseInt(arg('fps', '30'));
const MUSIC = arg('music', '');
const MOTION = arg('motion', 'gentle');
const CHUNK = parseInt(arg('chunk', '12'));
const CONC = parseInt(arg('concurrency', '4'));
const OUT = path.join(VID, arg('out', 'sinh-nhat-shopee.mp4'));
const SKIP_SHOOT = process.argv.includes('--skip-shoot');
const DFRAMES = Math.round(D * FPS);

function sh(args, { quiet = true } = {}) {
  return new Promise((res, rej) => {
    const p = spawn('ffmpeg', ['-hide_banner', '-loglevel', quiet ? 'error' : 'warning', '-stats', ...args],
      { stdio: quiet ? 'ignore' : 'inherit' });
    p.on('exit', c => c === 0 ? res() : rej(new Error('ffmpeg exit ' + c)));
    p.on('error', rej);
  });
}

async function pool(items, n, fn) {
  const q = [...items.keys()]; let done = 0;
  async function worker() {
    while (q.length) { const i = q.shift(); await fn(items[i], i); process.stdout.write(`\r  ${++done}/${items.length}`); }
  }
  await Promise.all(Array.from({ length: Math.min(n, items.length) }, worker));
  console.log('');
}

async function shoot() {
  if (!existsSync(INDEX)) throw new Error('Chưa có ' + INDEX);
  rmSync(FRAMES, { recursive: true, force: true }); mkdirSync(FRAMES, { recursive: true });
  const browser = await chromium.launch();
  // deviceScaleFactor 2 -> chụp 3840x2160 (chi tiết thật) -> encode xuống 1080 cho nét
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2 });
  await page.goto(pathToFileURL(INDEX).href + '?static', { waitUntil: 'networkidle' });
  await page.waitForFunction('typeof window.__count === "number"', null, { timeout: 15000 });
  await page.evaluate(() => document.fonts.ready);
  const n = await page.evaluate(() => window.__count);
  console.log(`Chụp ${n} slide...`);
  for (let i = 0; i < n; i++) {
    await page.evaluate(i => window.__goto(i), i);
    await page.waitForTimeout(160);
    await page.screenshot({ path: path.join(FRAMES, 'f' + String(i).padStart(3, '0') + '.png'), clip: { x: 0, y: 0, width: 1920, height: 1080 } });
    process.stdout.write(`\r  ${i + 1}/${n}`);
  }
  console.log('\n✓ frames'); await browser.close();
}

// Quay slide cuối CÓ pháo hoa (bước dt cố định -> mượt, tất định) -> FINFRAMES
async function shootFinale(durSec) {
  rmSync(FINFRAMES, { recursive: true, force: true }); mkdirSync(FINFRAMES, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2 });
  await page.goto(pathToFileURL(INDEX).href + '?static', { waitUntil: 'networkidle' });
  await page.waitForFunction('typeof window.__count === "number"', null, { timeout: 15000 });
  await page.evaluate(() => document.fonts.ready);
  const n = await page.evaluate(() => window.__count);
  await page.evaluate(i => window.__goto(i), n - 1);           // tới slide cuối
  await page.waitForTimeout(200);
  const nf = Math.round(durSec * FPS), step = 1000 / FPS;
  console.log(`Chụp pháo hoa finale: ${nf} frame...`);
  for (let f = 0; f < nf; f++) {
    await page.evaluate(dt => window.__fwStepFixed(dt), step);
    await page.screenshot({ path: path.join(FINFRAMES, 'f' + String(f).padStart(4, '0') + '.png'), clip: { x: 0, y: 0, width: 1920, height: 1080 } });
    if (f % 30 === 0) process.stdout.write(`\r  ${f}/${nf}`);
  }
  console.log(`\r  ${nf}/${nf}`); await browser.close();
}

async function encodeFinale(out) {
  await sh(['-framerate', String(FPS), '-i', path.join(FINFRAMES, 'f%04d.png'),
    '-vf', 'scale=1920:1080:flags=lanczos,setsar=1,format=yuv420p', '-r', String(FPS),
    '-c:v', 'libx264', '-crf', '11', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-fps_mode', 'cfr', '-y', out]);
}

// 1 ảnh -> clip Ken Burns D giây (silent)
function clipArgs(frame, out) {
  if (MOTION === 'none') {  // tĩnh: downscale 3840->1080 lanczos, nét tối đa
    return ['-loop', '1', '-t', String(D), '-i', frame,
      '-vf', `scale=1920:1080:flags=lanczos,setsar=1,fps=${FPS},format=yuv420p`,
      '-c:v', 'libx264', '-crf', '11', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-fps_mode', 'cfr', '-y', out];
  }
  // zoom nhẹ từ frame 3840 -> 1080: nét (downscale thật) + mượt (subpixel ở 2x)
  const zp = `[0:v]setsar=1,zoompan=z='min(zoom+0.0004,1.05)':d=${DFRAMES}:` +
    `x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=${FPS},format=yuv420p[v]`;
  return ['-i', frame, '-filter_complex', zp, '-map', '[v]', '-r', String(FPS),
    '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-fps_mode', 'cfr', '-y', out];
}

// xfade-join nhiều video (mỗi cái dur[i] giây) -> out ; trả về tổng thời lượng
async function xfadeJoin(inputs, durs, out) {
  if (inputs.length === 1) {
    await sh(['-i', inputs[0], '-c', 'copy', '-y', out]);
    return durs[0];
  }
  const args = []; inputs.forEach(f => args.push('-i', f));
  const fc = []; let cur = '[0:v]', acc = durs[0];
  for (let k = 1; k < inputs.length; k++) {
    const off = (acc - k * X).toFixed(3);
    const lbl = (k === inputs.length - 1) ? '[vout]' : `[x${k}]`;
    fc.push(`${cur}[${k}:v]xfade=transition=fade:duration=${X}:offset=${off}${lbl}`);
    cur = lbl; acc += durs[k];
  }
  args.push('-filter_complex', fc.join(';'), '-map', '[vout]',
    '-c:v', 'libx264', '-crf', '13', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-fps_mode', 'cfr', '-y', out);
  await sh(args);
  return acc - (inputs.length - 1) * X;
}

async function main() {
  if (!SKIP_SHOOT) await shoot();
  const frames = readdirSync(FRAMES).filter(f => f.endsWith('.png')).sort().map(f => path.join(FRAMES, f));
  if (!frames.length) throw new Error('Không có frame.');
  const n = frames.length;
  console.log(`Render ${n} slide (${D}s, xfade ${X}s, motion ${MOTION}${MUSIC ? ', nhạc ' + MUSIC : ''})`);

  rmSync(CLIPS, { recursive: true, force: true }); mkdirSync(CLIPS, { recursive: true });
  console.log('B2: tạo clip Ken Burns...');
  const clips = frames.map((_, i) => path.join(CLIPS, 'clip_' + String(i).padStart(3, '0') + '.mp4'));
  await pool(frames, CONC, (f, i) => sh(clipArgs(f, clips[i])));

  // Slide cuối: thay clip tĩnh bằng clip pháo hoa động
  if (!SKIP_SHOOT || !existsSync(FINFRAMES)) await shootFinale(D);
  console.log('\n  encode finale...');
  const finaleClip = path.join(CLIPS, 'clip_finale.mp4');
  await encodeFinale(finaleClip);
  clips[clips.length - 1] = finaleClip;

  const merged = path.join(CLIPS, 'merged.mp4');
  let total;
  if (clips.length <= 110) {           // xfade 1 lượt -> chỉ 2 lần encode (nét hơn)
    console.log('B3: xfade 1 lượt...');
    total = await xfadeJoin(clips, clips.map(() => D), merged);
  } else {                              // album rất lớn -> xfade theo cụm
    console.log('B3: xfade theo cụm...');
    const chunkFiles = [], chunkDurs = [];
    let ci = 0;
    for (let s = 0; s < clips.length; s += CHUNK) {
      const grp = clips.slice(s, s + CHUNK);
      const cf = path.join(CLIPS, 'chunk_' + String(ci).padStart(2, '0') + '.mp4');
      chunkDurs.push(await xfadeJoin(grp, grp.map(() => D), cf));
      chunkFiles.push(cf); process.stdout.write(`\r  cụm ${++ci}`);
    }
    console.log('');
    total = await xfadeJoin(chunkFiles, chunkDurs, merged);
  }

  console.log('B4: ghép nhạc + xuất...');
  // nhạc: 'auto' = mọi file trong Shopee-birthday/music/ (sắp theo số tự nhiên),
  // hoặc danh sách "a.mp3,b.mp3" (tương đối theo Shopee-birthday/ hoặc đường dẫn tuyệt đối)
  const nat = (a, b) => a.replace(/\d+/g, m => m.padStart(6, '0')).localeCompare(b.replace(/\d+/g, m => m.padStart(6, '0')));
  const musicDir = path.join(BDIR, 'music');
  let musicFiles = [];
  if (MUSIC === 'auto') {
    if (existsSync(musicDir))
      musicFiles = readdirSync(musicDir).filter(f => /\.(mp3|m4a|wav|aac)$/i.test(f)).sort(nat).map(f => path.join(musicDir, f));
    else
      musicFiles = readdirSync(BDIR).filter(f => /^music\d*\.mp3$/i.test(f)).sort(nat).map(f => path.join(BDIR, f));
  } else if (MUSIC) {
    musicFiles = MUSIC.split(',').map(s => s.trim()).filter(Boolean)
      .map(s => path.isAbsolute(s) ? s : path.join(BDIR, s));
  }

  let track = null;
  if (musicFiles.length > 1) {
    track = path.join(CLIPS, '_music_mix.m4a');
    const a = []; musicFiles.forEach(f => a.push('-i', f));
    a.push('-filter_complex', `${musicFiles.map((_, k) => `[${k}:a]`).join('')}concat=n=${musicFiles.length}:v=0:a=1[a]`,
      '-map', '[a]', '-c:a', 'aac', '-b:a', '192k', '-y', track);
    await sh(a);
    console.log(`  nhạc: ${musicFiles.map(f => path.basename(f)).join(' + ')}`);
  } else if (musicFiles.length === 1) {
    track = musicFiles[0];
  }

  // SFX slide cuối (pháo hoa + vỗ tay) từ Shopee-birthday/sfx/
  const sfxDir = path.join(BDIR, 'sfx');
  const sfxFiles = existsSync(sfxDir)
    ? readdirSync(sfxDir).filter(f => /\.(wav|mp3|m4a|aac)$/i.test(f)).sort().map(f => path.join(sfxDir, f)) : [];
  const finaleStart = Math.max(0, total - D + X);   // lúc slide cuối hiện rõ
  const delayMs = Math.round(finaleStart * 1000);

  if (track && sfxFiles.length) {
    const args = ['-i', merged, '-stream_loop', '-1', '-i', track];
    sfxFiles.forEach(f => args.push('-i', f));
    const fc = ['[1:a]volume=0.5[m]'];
    const mix = ['[m]'];
    sfxFiles.forEach((f, k) => {
      const vol = /applause|vo.?tay|clap/i.test(path.basename(f)) ? 0.85 : 1.0;
      fc.push(`[${2 + k}:a]adelay=${delayMs}|${delayMs},volume=${vol}[s${k}]`); mix.push(`[s${k}]`);
    });
    fc.push(`${mix.join('')}amix=inputs=${mix.length}:duration=longest:normalize=0[mx0]`);
    fc.push('[mx0]alimiter=limit=0.95[mx1]');
    fc.push(`[mx1]afade=t=out:st=${(total - 2).toFixed(2)}:d=2[aout]`);
    args.push('-filter_complex', fc.join(';'), '-map', '0:v', '-map', '[aout]',
      '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', total.toFixed(2), '-movflags', '+faststart', '-y', OUT);
    await sh(args);
    console.log(`  SFX finale: ${sfxFiles.map(f => path.basename(f)).join(' + ')} @ ${finaleStart.toFixed(1)}s`);
  } else if (track) {
    await sh(['-i', merged, '-stream_loop', '-1', '-i', track,
      '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
      '-af', `afade=t=out:st=${(total - 2).toFixed(2)}:d=2,volume=0.7`, '-shortest',
      '-movflags', '+faststart', '-y', OUT]);
  } else {
    await sh(['-i', merged, '-c', 'copy', '-movflags', '+faststart', '-y', OUT]);
  }
  console.log(`\n✅ Video (${Math.floor(total / 60)}p${Math.round(total % 60)}s): ` + path.relative(ROOT, OUT));
}
main().catch(e => { console.error('LỖI:', e.message); process.exit(1); });
