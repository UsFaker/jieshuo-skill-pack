import sys,json,wave,numpy as np
from faster_whisper import WhisperModel
src=sys.argv[1]; out=sys.argv[2]; model=sys.argv[3] if len(sys.argv)>3 else "medium"
prompt=sys.argv[4] if len(sys.argv)>4 else "以下是普通话的历史解说。"
w=wave.open(src); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
m=WhisperModel(model,device="cpu",compute_type="float32",cpu_threads=8)
segs,info=m.transcribe(a,language="zh",beam_size=5,vad_filter=True,word_timestamps=True,initial_prompt=prompt,condition_on_previous_text=True)
res=[]
for s in segs:
    res.append({"start":s.start,"end":s.end,"text":s.text,"words":[[w.start,w.end,w.word] for w in s.words]})
    print(f"{s.start:.1f} {s.text}",flush=True)
json.dump(res,open(out,"w"),ensure_ascii=False,indent=1)
