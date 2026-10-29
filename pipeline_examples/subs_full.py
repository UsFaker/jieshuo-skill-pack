# [示例] 商鞅 v7 整片剪辑管线的参考实现。路径和素材名写死为当时的项目（/workspace/shangyang/...），换项目时照着改；用法和顺序见 pipeline_examples/README.md。
import re,json
F='/workspace/shangyang/v7/full'; P=json.load(open(F+'/plan_full.json'))
src=open('/workspace/shangyang/v7/edit/subs7.py').read(); hdr=src[src.index('hdr="""')+7:src.index('"""\nev')]
def fmt(t): return f'{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}'
subs=P['subs']; ev=''
for k,(a,b,t,i) in enumerate(subs):
    nb=subs[k+1][0] if k+1<len(subs) else 1e9
    e=min(b+0.06,nb-0.03,P['total']); st=max(0.0,a-0.04)
    t=re.sub(r'\[(.*?)\]',lambda m:'{\\c&H0C00F2&}'+m.group(1)+'{\\c&HFFFFFF&}',t)
    ev+=f'Dialogue: 0,{fmt(st)},{fmt(e)},Sub,,0,0,0,,{t}\n'
for t in P['tags']: ev+=f"Dialogue: 1,{fmt(t['t0'])},{fmt(t['t1'])},Tag,,0,0,0,,{{\\fad(200,300)}}{t['label']}\n"
open(F+'/work/subs.ass','w').write(hdr+ev)
print(len(subs),'subs; max chars',max(len(re.sub(r'[\[\]]','',s[2])) for s in subs))
