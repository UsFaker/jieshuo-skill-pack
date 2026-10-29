# [示例] 商鞅 v7 整片剪辑管线的参考实现。路径和素材名写死为当时的项目（/workspace/shangyang/...），换项目时照着改；用法和顺序见 pipeline_examples/README.md。
import sys,json,re
sys.path.insert(0,'/workspace/shangyang/v7/full/edit'); from brain_full import *
R='/workspace/shangyang/v7/full/'; FPS=24
A=json.load(open(R+'align_full.json')); CH={int(k):v for k,v in A['CH'].items()}; LS={int(k):v for k,v in A['LS'].items()}; LE={int(k):v for k,v in A['LE'].items()}
G=A['gaps']; TOT=A['total']
L={x['id']:x for x in json.load(open(R+'tts/lines77.json'))}
def alnum_idx(txt): return [k for k,c in enumerate(txt) if c.isalnum()]
def gap_near(t,w=0.14):
    c=[g for g in G if g[0]-w<=t<=g[1]+w and g[1]-g[0]>=0.1]
    return min(c,key=lambda g:abs((g[0]+g[1])/2-t)) if c else None
def cut_t(i,k):
    mid=(CH[i][k-1][1]+CH[i][k][0])/2; g=gap_near(mid)
    return ((g[0]+g[1])/2 if g else mid)-0.05
def clause_bounds(i):
    t=L[i]['tts']; b=[];n=0
    for c in t:
        if c.isalnum(): n+=1
        elif c in '，。、？！；' and n and (not b or b[-1]!=n): b.append(n)
    n=len([c for c in t if c.isalnum()]); return [x for x in b if 0<x<n]
def auto_cuts(i,m):
    n=len(CH[i]); cb=clause_bounds(i); out=[]
    for j in range(1,m):
        tgt=round(j*n/m); c=[x for x in cb if abs(x-tgt)<=max(3,0.28*n) and x>(out[-1] if out else 0)]
        out.append(min(c,key=lambda x:abs(x-tgt)) if c else tgt)
    return out
shots=[]
for i in sorted(BRAIN):
    b=BRAIN[i]; sh=b['shots']; cuts=b.get('cuts') or (auto_cuts(i,len(sh)) if len(sh)>1 else [])
    ts=[LS[i]-0.08 if i>1 else 0.0]+[cut_t(i,k) for k in cuts]
    for j,(a,ss,d,tr) in enumerate(sh): shots.append(dict(line=i,asset=a,ss=ss,desc=d,tr=tr,t0=ts[j]))
for k,s in enumerate(shots):
    s['t1']=shots[k+1]['t0'] if k+1<len(shots) else TOT
# frame quantisation
for s in shots: s['f0']=round(s['t0']*FPS); 
for k,s in enumerate(shots): s['f1']=shots[k+1]['f0'] if k+1<len(shots) else round(TOT*FPS)
# 修正过短镜头
for s in shots:
    s['dur']=(s['f1']-s['f0'])/FPS
# 字幕
KEYS={1:['七百多'],2:['杀'],3:['渭河水'],4:['商鞅'],6:['狠'],8:['狠'],10:['杀了他'],16:['分土地'],24:['五十金'],27:['腰斩'],30:['奴隶'],33:['太子犯法'],37:['刺了字'],39:['割了他的鼻子'],40:['八年'],46:['边城'],49:['烧了'],54:['割给了秦国'],57:['商君'],59:['露水'],61:['秦惠文王'],64:['商君有法'],67:['不收他'],70:['车裂示众'],73:['秦人不怜'],74:['一条没废'],7:['狠'],9:['公孙鞅'],50:['公元前340年'],76:['一百一十七年'],77:['七百多人']}
KEYS.update({78:['头号功臣'],79:['统一天下'],80:['严刑连坐','太狠'],81:['作法自毙'],82:['大功','大过'],83:['绝路']})
subs=[]
for i in sorted(L):
    tt=L[i]['tts']; tx=L[i]['text']
    ps=[p for p in re.split(r'[，。、？！；]',tt) if p]; pd=[p for p in re.split(r'[，。、？！；]',tx) if p]
    assert len(ps)==len(pd),(i,ps,pd)
    n=0; seg=[]
    for p,dsp in zip(ps,pd):
        c=len([ch for ch in p if ch.isalnum()]); seg.append((n,n+c-1,dsp)); n+=c
    # 过长拆半
    out=[]
    for a,b,dsp in seg:
        if len(dsp)>17:
            h=len(dsp)//2; out.append((a,a+h-1,dsp[:h])); out.append((a+h,b,dsp[h:]))
        else: out.append((a,b,dsp))
    nch=len(CH[i])
    for a,b,dsp in out:
        g1=None if a==0 else gap_near((CH[i][a-1][1]+CH[i][a][0])/2)
        g2=None if b>=nch-1 else gap_near((CH[i][b][1]+CH[i][b+1][0])/2)
        st=LS[i] if a==0 else (g1[1] if g1 else CH[i][a][0])
        en=LE[i] if b>=nch-1 else (g2[0] if g2 else CH[i][b][1])
        for kw in KEYS.get(i,[]): 
            if kw in dsp: dsp=dsp.replace(kw,'['+kw+']',1)
        subs.append((round(st,3),round(en,3),dsp,i))
# 名字条
def find_char_t(i,sub):
    ta=''.join(c for c in L[i]['tts'] if c.isalnum()); k=ta.find(''.join(c for c in sub if c.isalnum()))
    return CH[i][k][0] if k>=0 else None
tags=[]
for (i,trig,label) in TAGS:
    t=find_char_t(i,trig); assert t is not None,(i,trig)
    tags.append(dict(line=i,label=label,t0=round(t-0.05,3)))
for k,t in enumerate(tags):
    nxt=tags[k+1]['t0'] if k+1<len(tags) else 1e9
    t['t1']=round(min(t['t0']+1.6,nxt-0.05) if True else 0,3)
    if t['label']=='商鞅': t['t1']=round(LE[4]+0.9,3)
# 大字
bigs=[]
for (i,trig,spec,pre,size,dur) in BIG:
    t=find_char_t(i,trig) if i!=1 else find_char_t(i,'七百多')
    if i==8: t=CH[8][5][0]-0.05
    bigs.append(dict(line=i,t0=round(t-0.05,3),dur=dur,text=spec,preset=pre,size=size))
json.dump(dict(total=TOT,shots=shots,subs=subs,tags=tags,bigs=bigs,LS=LS,LE=LE),open(R+'plan_full.json','w'),ensure_ascii=False,indent=1)
import collections
print('shots',len(shots),'min dur',round(min(s['dur'] for s in shots),2),[(s['line'],s['asset'],round(s['dur'],2)) for s in shots if s['dur']<1.0])
print('subs',len(subs),'max chars',max(len(re.sub(r'[\[\]]','',s[2])) for s in subs))
print('tags',[(t['label'],t['t0']) for t in tags]);print('bigs',[(b['line'],b['t0']) for b in bigs])
