// 统一加载 playwright-core 和 Chrome，供 render*.mjs 使用。
// playwright-core 查找顺序：
//   1. 环境变量 PLAYWRIGHT_CORE（node_modules/playwright-core 目录，或其 index.mjs 的路径）
//   2. 环境变量 LEMO_OPUSCAR_DIR（lemo-opuscar 项目目录，用其中的 node_modules/playwright-core）
//   3. 从套件目录向上、以及从当前目录向上逐级找 node_modules/playwright-core
//   4. `npm root -g` 全局目录
// Chrome 查找顺序：环境变量 CHROME_PATH → 常见安装路径（google-chrome / chromium）。
import fs from 'fs'; import path from 'path'; import { execSync } from 'child_process'; import { pathToFileURL } from 'url';
const here = path.dirname(new URL(import.meta.url).pathname);
function entryOf(p){
  if(!p) return null;
  if(fs.existsSync(p) && fs.statSync(p).isFile()) return p;
  for (const f of ['index.mjs','index.js']) { const q=path.join(p,f); if(fs.existsSync(q)) return q; }
  return null;
}
function candidates(){
  const c=[];
  if(process.env.PLAYWRIGHT_CORE) c.push(process.env.PLAYWRIGHT_CORE);
  if(process.env.LEMO_OPUSCAR_DIR) c.push(path.join(process.env.LEMO_OPUSCAR_DIR,'node_modules/playwright-core'));
  for (const start of [here, process.cwd()]) { let d=start; for(let i=0;i<8;i++){ c.push(path.join(d,'node_modules/playwright-core')); const u=path.dirname(d); if(u===d)break; d=u; } }
  try { c.push(path.join(execSync('npm root -g',{stdio:['ignore','pipe','ignore']}).toString().trim(),'playwright-core')); } catch {}
  return c;
}
export async function loadChromium(){
  const tried=[];
  for(const c of candidates()){ const e=entryOf(c); tried.push(c); if(e){ const m=await import(pathToFileURL(e).href); return (m.chromium||m.default?.chromium); } }
  console.error('找不到 playwright-core。任选其一：\n  1) 在套件目录执行 npm i playwright-core\n  2) export PLAYWRIGHT_CORE=/path/to/node_modules/playwright-core\n  3) export LEMO_OPUSCAR_DIR=/path/to/lemo-opuscar（先在该目录 npm install）\n已找过：\n  '+tried.join('\n  '));
  process.exit(2);
}
export function chromePath(){
  const list=[process.env.CHROME_PATH,'/usr/bin/google-chrome','/usr/bin/google-chrome-stable','/usr/bin/chromium','/usr/bin/chromium-browser','/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','C:/Program Files/Google/Chrome/Application/chrome.exe'].filter(Boolean);
  for(const p of list) if(fs.existsSync(p)) return p;
  console.error('找不到 Chrome。请安装 google-chrome，或 export CHROME_PATH=/path/to/chrome'); process.exit(2);
}
export const CHROME_ARGS=['--font-render-hinting=none','--force-color-profile=srgb','--allow-file-access-from-files'];
export const KIT_DIR=here;
