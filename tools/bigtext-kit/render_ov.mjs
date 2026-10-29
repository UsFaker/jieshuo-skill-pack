// usage: node render_ov.mjs plan.json idxStart idxEnd  -> final/NN/0000.png (RGBA, transparent bg)
import { loadChromium, chromePath, CHROME_ARGS } from './_pw.mjs';
const chromium = await loadChromium();
import fs from 'fs'; import path from 'path';
const [,, planPath, a, b] = process.argv;
const plan=JSON.parse(fs.readFileSync(planPath,'utf8'));
const dir=path.dirname(new URL(import.meta.url).pathname);  // 套件目录（kit.html 所在）
const br=await chromium.launch({executablePath:chromePath(),args:CHROME_ARGS});
const pg=await br.newPage({viewport:{width:1920,height:1080}});
await pg.goto('file://'+dir+'/kit_ov.html');
for(let k=+a;k<Math.min(+b,plan.length);k++){
  const p=plan[k]; const sc={bg:'',matte:null,items:p.items,subs:[],dur:p.dur,zoomIn:false,flashAt:null};
  await pg.evaluate(async s=>await window.BT.load(s), sc);
  const fd=`${dir}/final/${String(k).padStart(2,'0')}`; fs.mkdirSync(fd,{recursive:true});
  const n=Math.round(p.dur*30);
  for(let i=0;i<n;i++){await pg.evaluate(t=>window.BT.seek(t),i/30); await pg.screenshot({path:`${fd}/${String(i).padStart(4,'0')}.png`,omitBackground:true});}
  fs.writeFileSync(`${fd}/report.json`,JSON.stringify(await pg.evaluate(()=>window.BT.report())));
  console.log('done',k,p.text,n);
}
await br.close();
