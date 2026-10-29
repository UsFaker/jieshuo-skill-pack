// 商鞅 大字 kit. Scene-driven, deterministic: BT.load(scene) then BT.seek(t) per frame.
(function(){
const W=1920,H=1080, SAFE={l:96,r:1824,t:60,b:H-170}; // b: keep clear of subtitle band
const COL={w:'#FFFFFF',r:'#E8000A',y:'#FCFF0E',g:'#E9D8A6',k:'#141414',d:'#B00008'};
// shadow recipes measured from the reference (soft dark drop shadow, no hard stroke)
const SH={
  soft:'drop-shadow(0 0 2px rgba(0,0,0,.55)) drop-shadow(5px 7px 9px rgba(0,0,0,.82))',
  softglow:'drop-shadow(0 0 2px rgba(0,0,0,.5)) drop-shadow(4px 6px 8px rgba(0,0,0,.8)) drop-shadow(0 0 22px rgba(120,0,0,.55))',
  heavy:'drop-shadow(0 0 3px rgba(0,0,0,.85)) drop-shadow(7px 9px 6px rgba(0,0,0,.85))',
  brush:'drop-shadow(0 0 2px rgba(0,0,0,.9)) drop-shadow(6px 8px 5px rgba(0,0,0,.9)) drop-shadow(0 0 18px rgba(0,0,0,.45))',
  epic:'drop-shadow(0 0 2px rgba(60,0,0,.9)) drop-shadow(8px 11px 7px rgba(25,0,0,.8))',
  ink:'drop-shadow(0 0 3px rgba(0,0,0,.95)) drop-shadow(3px 5px 6px rgba(0,0,0,.9)) drop-shadow(0 0 30px rgba(0,0,0,.6))',
};
// ===== presets (mirror of the reference's 8 looks) =====
const P={
  SONG_RED:   {font:'SongH',  sh:SH.softglow, def:'r', anim:'blurSettle', ls:4},   // 宋体重磅红：概念/事件/负面词（安史之乱、摸鱼文化、独裁者）
  SONG_WHITE: {font:'SongH',  sh:SH.soft,     def:'w', anim:'blurSettle', ls:4},   // 宋体白：双行第二行/中性词（反体制、乃摄也）
  BRUSH:      {font:'PMBrush',sh:SH.brush,    def:'w', anim:'brushSlam',  ls:-2},  // 毛笔红白相间：人名/金句（张居正、宰相之杰、续命60年）
  HEI:        {font:'YSHei',  sh:SH.heavy,    def:'w', anim:'zoomPunch',  ls:2},   // 粗黑白/黄：现代梗/口语（降级撤职、明朝第一政治家、踢皮球）
  HEI_SANS:   {font:'SansH',  sh:SH.heavy,    def:'w', anim:'zoomPunch',  ls:2},
  EPIC:       {font:'HuangYou',sh:SH.epic,    def:'r', anim:'blurSettle', ls:6},   // 黄油体红：亮场/结尾升华（家国担当、垂暮王朝、虽千万人吾往矣）
  BANGSHU:    {font:'Bangshu',sh:SH.ink,      def:'w', anim:'inkDrop',    ls:0},   // 榜书白：冲击单字/竖排（黑洞、徐阶）
};
let S=null, els=[];
function parseSegs(s){ // "w:商|r1.25:鞅" -> [{c,scale,txt}]
  return s.split('|').map(p=>{const m=p.match(/^([a-z])([0-9.]*):(.*)$/); return m?{c:m[1],k:m[2]?+m[2]:1,t:m[3]}:{c:null,k:1,t:p};});
}
function ease(x){x=Math.min(1,Math.max(0,x));return 1-Math.pow(1-x,3);}
function easeBack(x){x=Math.min(1,Math.max(0,x));const c1=1.9,c3=c1+1;return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2);}
function build(){
  const st=document.getElementById('stage');
  document.getElementById('bgimg').src=S.bg;
  const fg=document.getElementById('fgimg'); if(S.matte){fg.src=S.matte;fg.style.display='block';}else fg.style.display='none';
  // zoom-blur ghost copies for the radial-zoom shot transition used in the reference
  const zw=document.getElementById('zbwrap'); zw.innerHTML='';
  for(let i=1;i<=6;i++){const im=document.createElement('img');im.src=S.bg;im.className='zb';im.dataset.i=i;zw.appendChild(im);}
  const tl=document.getElementById('texts'), tl2=document.getElementById('texts2'); tl.innerHTML='';tl2.innerHTML='';
  els=S.items.map(it=>{
    const p=Object.assign({},P[it.preset],it.over||{});
    const d=document.createElement('div'); d.className='bt'+(it.vertical?' v':'');
    d.style.fontFamily=p.font; d.style.fontSize=it.size+'px'; d.style.letterSpacing=(it.ls??p.ls)+'px';
    d.style.filter=p.sh;
    const segs=parseSegs(it.text); const chars=[];
    segs.forEach(sg=>{[...sg.t].forEach(ch=>{const sp=document.createElement('span');sp.className='ch';sp.textContent=ch;
      sp.style.color=COL[sg.c||p.def]; if(sg.k!==1){sp.style.fontSize=(sg.k*100)+'%';}
      if(ch===' '){sp.style.width=(it.size*0.35)+'px';sp.style.height=(it.size*0.35)+'px';}
      d.appendChild(sp);chars.push(sp);});});
    let glint=null;
    if((it.anim||p.anim)==='brushSlam'){glint=d.cloneNode(true);glint.className='glint '+(it.vertical?'v':'');glint.style.filter='none';
      glint.querySelectorAll('.ch').forEach(c=>c.style.color='#fff');d.appendChild(glint);}
    (it.behind?tl:tl2).appendChild(d);
    return {it,p,d,chars,glint,anim:it.anim||p.anim};
  });
}
function place(e){ // centre at (x,y), then clamp into the safe area (text is never pushed out of frame)
  const d=e.d; d.style.transform='none'; d.style.left='0px'; d.style.top='0px';
  const r=d.getBoundingClientRect(); let x=e.it.x-r.width/2, y=e.it.y-r.height/2;
  const pad=24; // room for shadow
  x=Math.max(SAFE.l+pad-0,Math.min(SAFE.r-pad-r.width,x)); y=Math.max(SAFE.t,Math.min(SAFE.b-r.height,y));
  d.style.left=x+'px'; d.style.top=y+'px'; e.box={x,y,w:r.width,h:r.height};
}
function seek(t){
  const T=S.dur||3.5;
  // background: slow push-in + punch/shake on slams + radial zoom-blur in at shot start
  let sc=1+0.045*(t/T), sx=0, sy=0;
  els.forEach(e=>{const u=t-e.it.t0; if(u>=0&&u<0.2&&(e.anim==='zoomPunch'||e.anim==='brushSlam'||e.anim==='inkDrop')){const k=1-u/0.2; sc+=0.018*k; sx+=Math.sin(u*90)*9*k; sy+=Math.cos(u*77)*6*k;}});
  const bw=document.getElementById('bgwrap'), fw=document.getElementById('fgwrap');
  const tf=`translate(${sx}px,${sy}px) scale(${sc})`; bw.style.transform=tf; fw.style.transform=tf;
  const tz=S.zoomIn?Math.max(0,1-t/0.3):0; // 9-frame radial zoom-blur transition
  document.querySelectorAll('#zbwrap img').forEach(im=>{const i=+im.dataset.i; im.style.opacity=tz>0?(0.42*tz):0; im.style.transform=`scale(${1+i*0.035*tz})`;});
  document.getElementById('bgimg').style.filter=tz>0?`blur(${tz*6}px)`:'none';
  document.getElementById('flash').style.opacity=S.flashAt!=null?Math.max(0,0.55-(t-S.flashAt)*4)*(t>=S.flashAt?1:0):0;
  els.forEach(e=>{
    const it=e.it,d=e.d,u=t-it.t0;
    if(u<0||(it.t1!=null&&t>=it.t1)){d.style.visibility='hidden';return;}
    d.style.visibility='visible'; place(e);
    let s=1,b=0,o=1,rot=it.rot||0,ty=0,tx=0;
    const base=e.p.sh;
    if(e.anim==='blurSettle'){const k=ease(u/0.32); s=1.22-0.22*k; b=16*(1-k); o=Math.min(1,u/0.12);}
    else if(e.anim==='zoomPunch'){const k=u/0.24; s=k<1?1.75-0.8*easeBack(k):1; s=Math.max(s,0.94); if(k>=1)s=1; b=18*Math.max(0,1-k*1.3); o=Math.min(1,u/0.06);}
    else if(e.anim==='brushSlam'){const k=u/0.26; s=k<1?(0.3+0.78*ease(k)):(k<1.4?1.08-0.08*ease((k-1)/0.4):1); b=10*Math.max(0,1-k); o=Math.min(1,u/0.05);
      if(e.glint){const g=(u-0.28)/0.45; const pos=-30+g*160; const on=g>0&&g<1;
        const m=`linear-gradient(105deg, transparent ${pos-18}%, rgba(255,255,255,.95) ${pos}%, transparent ${pos+18}%)`;
        e.glint.style.webkitMaskImage=m; e.glint.style.maskImage=m; e.glint.style.opacity=on?0.85:0;
        e.glint.style.filter=on?'blur(1px) drop-shadow(0 0 12px rgba(255,255,255,.8))':'none';}}
    else if(e.anim==='inkDrop'){ // per-char drop with smear (黑洞 style)
      e.chars.forEach((c,i)=>{const v=(u-i*0.12)/0.28; const k=ease(v); c.style.opacity=v<=0?0:1; c.style.transform=`translateY(${(1-k)*-40}px) scaleY(${1+0.6*(1-k)})`; c.style.filter=`blur(${(1-k)*10}px)`;});
    }
    if(it.stagger){ e.chars.forEach((c,i)=>{const v=(u-i*it.stagger)/0.28; const k=ease(v); c.style.opacity=Math.max(0,Math.min(1,v*3)); c.style.transform=`scale(${1.35-0.35*k})`; c.style.filter=`blur(${(1-k)*12}px)`;}); s=1;b=0;o=1;}
    if(it.dimAt!=null&&t>=it.dimAt){const k=ease((t-it.dimAt)/0.25); o=1-0.62*k; d.style.filter=base+` grayscale(${k})`;}
    else d.style.filter=base+(b>0.05?` blur(${b}px)`:'');
    d.style.opacity=o; d.style.transform=`translate(${tx}px,${ty}px) rotate(${rot}deg) scale(${s})`;
  });
  // subtitle
  const sb=document.getElementById('sub'); const sub=(S.subs||[]).find(x=>t>=x.t0&&t<x.t1);
  if(sub){sb.innerHTML=sub.text.replace(/\[(.+?)\]/g,'<span class="hl">$1</span>');}else sb.innerHTML='';
}
window.BT={load:async(sc)=>{S=sc;build();await document.fonts.ready;await Promise.all([...document.images].map(i=>i.complete?1:new Promise(r=>{i.onload=r;i.onerror=r;})));return true;},seek,
  report:()=>els.map(e=>({text:e.it.text,box:e.box}))};
})();
