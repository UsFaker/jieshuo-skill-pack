// usage: node render.mjs scene.json out_prefix [--still t] [--clip] [--fps 30]
import { loadChromium, chromePath, CHROME_ARGS } from './_pw.mjs';
const chromium = await loadChromium();
import fs from 'fs'; import path from 'path'; import { execSync } from 'child_process';
const [,, scenePath, out, ...rest] = process.argv;
const arg=(k,d)=>{const i=rest.indexOf(k);return i>=0?rest[i+1]:d;};
fs.mkdirSync(path.dirname(path.resolve(out)),{recursive:true});
const scene=JSON.parse(fs.readFileSync(scenePath,'utf8'));
const dir=path.dirname(new URL(import.meta.url).pathname);  // 套件目录（kit.html 所在）
const b=await chromium.launch({executablePath:chromePath(),args:CHROME_ARGS});
const pg=await b.newPage({viewport:{width:1920,height:1080}});
pg.on('console',m=>console.log('[page]',m.text()));
await pg.goto('file://'+dir+'/kit.html');
await pg.evaluate(async s=>await window.BT.load(s), scene);
const el=await pg.$('#stage');
if(rest.includes('--still')){
  const t=+arg('--still', scene.still ?? 2.5);
  await pg.evaluate(t=>window.BT.seek(t),t); await pg.waitForTimeout(50);
  await el.screenshot({path:out+'.png'});
  execSync(`ffmpeg -v error -y -i ${out}.png -q:v 2 ${out}.jpg && rm ${out}.png`);
  console.log(JSON.stringify(await pg.evaluate(()=>window.BT.report())));
}
if(rest.includes('--clip')){
  const fps=+arg('--fps',30), dur=scene.dur||3.5, n=Math.round(dur*fps);
  const fd=out+'_frames'; fs.mkdirSync(fd,{recursive:true});
  for(let i=0;i<n;i++){await pg.evaluate(t=>window.BT.seek(t),i/fps); await el.screenshot({path:`${fd}/${String(i).padStart(4,'0')}.png`});}
  execSync(`ffmpeg -v error -y -framerate ${fps} -i ${fd}/%04d.png -c:v libx264 -pix_fmt yuv420p -crf 17 -preset medium ${out}.mp4`);
  fs.rmSync(fd,{recursive:true});
}
await b.close();
