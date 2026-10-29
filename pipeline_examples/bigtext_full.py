# [示例] 商鞅 v7 整片剪辑管线的参考实现。路径和素材名写死为当时的项目（/workspace/shangyang/...），换项目时照着改；用法和顺序见 pipeline_examples/README.md。
import json,subprocess,sys,os,cv2,numpy as np
from rembg import new_session, remove
F='/workspace/shangyang/v7/full'; P=json.load(open(F+'/plan_full.json')); base=sys.argv[1]
sess=new_session('u2net_human_seg'); out=[]
def frame(t):
    p='/tmp/btf.png'; subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',base,'-frames:v','1',p]); return cv2.imread(p)
for k,b in enumerate(P['bigs']):
    t0,dur,txt,pre,size=b['t0'],b['dur'],b['text'],b['preset'],b['size']; m=None
    for t in (t0+0.3,t0+dur/2,t0+dur-0.1):
        img=frame(t); mm=np.array(remove(cv2.cvtColor(img,cv2.COLOR_BGR2RGB),session=sess,only_mask=True)).astype(np.float32)/255
        m=mm if m is None else np.maximum(m,mm)
    m=cv2.resize(m,(1920,1080))
    n=len(''.join(p.split(':')[-1] for p in txt.split('|'))); bw,bh=n*size*0.98,size*1.05
    best=None
    for cx in range(int(96+bw/2+24),int(1824-bw/2-24)+1,40):
        for cy in range(int(60+bh/2),int(780-bh/2)+1,30):   # 避开底部字幕区
            x0,y0=int(cx-bw/2),int(cy-bh/2); ov=m[y0:int(y0+bh),x0:int(x0+bw)].mean()
            sc=ov+0.00012*abs(cy-400)+0.00004*abs(cx-960)
            if best is None or sc<best[0]: best=(sc,cx,cy,ov)
    _,cx,cy,ov=best; print(k,b['line'],txt,cx,cy,round(float(ov),3),flush=True)
    out.append(dict(text=txt,name=txt,preset=pre,t0=t0,dur=dur,flash=1 if b['line']==8 else 0,x=cx,y=cy,overlap=round(float(ov),3),items=[dict(preset=pre,text=txt,size=size,x=cx,y=cy,t0=0.0)]))
json.dump(out,open(F+'/work/bigtext.json','w'),ensure_ascii=False,indent=1)
