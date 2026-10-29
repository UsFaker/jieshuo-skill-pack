# [示例] 商鞅 v7 整片剪辑管线的参考实现。路径和素材名写死为当时的项目（/workspace/shangyang/...），换项目时照着改；用法和顺序见 pipeline_examples/README.md。
import json
F='/workspace/shangyang/v7/full'; P=json.load(open(F+'/plan_full.json')); S=P['shots']
import sys; sys.path.insert(0,F+'/edit'); from brain_full import path
L={x['id']:x for x in json.load(open(F+'/tts/lines77.json'))}
def ts(t): return f'{int(t//60)}:{t%60:05.2f}'
o=['# 商鞅 v7 整片 · 逐句对画表\n','每句：口播 → 脑内画面 → 镜头素材(绝对路径)。时间为成片时间。\n','| 句 | 时间 | 口播 | 镜头# | 素材 | 画面(脑内画面) | 转场 |','|---|---|---|---|---|---|---|']
for i in sorted(L):
    ss=[(k,s) for k,s in enumerate(S) if s['line']==i]
    for n,(k,s) in enumerate(ss):
        o.append(f"| {i if n==0 else ''} | {ts(s['t0'])}-{ts(s['t1'])} | {L[i]['text'] if n==0 else ''} | {k} | `{path(s['asset'])}` @ss={s['ss']} | {s['desc']} | {s['tr']} |")
open(F+'/逐句对画表.md','w').write('\n'.join(o)); print(len(o))
