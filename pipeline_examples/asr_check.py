# [示例] 商鞅 v7 整片剪辑管线的参考实现。路径和素材名写死为当时的项目（/workspace/shangyang/...），换项目时照着改；用法和顺序见 pipeline_examples/README.md。
import json,re,difflib,numpy as np,soundfile as sf,librosa,sys
sys.path.insert(0,'..'); from split_full_util import fixnum
from faster_whisper import WhisperModel
from pypinyin import lazy_pinyin
F='/workspace/shangyang/v7/full'; P=json.load(open(F+'/plan_full.json'))
v,sr=sf.read(F+'/work/master.wav'); v=v if v.ndim==1 else v.mean(1)
a=librosa.resample(v.astype(np.float32),orig_sr=sr,target_sr=16000)
m=WhisperModel('medium',device='cpu',compute_type='float32',cpu_threads=8)
sg,_=m.transcribe(a,language='zh',beam_size=5,word_timestamps=True,condition_on_previous_text=False,vad_filter=False)
ch=[]
for s in sg:
    for w in s.words:
        cs=[c for c in fixnum(w.word) if c.isalnum()]
        for k,c in enumerate(cs):
            d=(w.end-w.start)/len(cs); ch.append((c,w.start+k*d+0.1))   # whisper 词时间戳约早0.1s
sub=[];own=[]
for (a0,b0,t,i) in P['subs']:
    for c in re.sub(r'[\[\]]','',t):
        if c.isalnum(): sub.append(c); own.append(a0)
# 字幕里用显示文本(数字为汉字?) 用pinyin对齐
sp=[lazy_pinyin(c)[0] for c in sub]; hp=[lazy_pinyin(c[0])[0] for c in ch]
sm=difflib.SequenceMatcher(None,sp,hp,autojunk=False); off=[];seen=set()
for p,q,n in sm.get_matching_blocks():
    for k in range(n):
        # 只取字幕起点第一个字
        if own[p+k] not in seen and (p+k==0 or own[p+k-1]!=own[p+k]):
            seen.add(own[p+k]); off.append(ch[q+k][1]-own[p+k])
off=np.array(off); print('n',len(off),'median',np.median(off),'|off| median',np.median(abs(off)),'p90',np.percentile(abs(off),90),'frac<=0.2',(abs(off)<=0.2).mean())
txt=''.join(c for c,_ in ch); json.dump(dict(off=list(map(float,off)),asr=txt),open(F+'/qa/asr_check.json','w'),ensure_ascii=False)
