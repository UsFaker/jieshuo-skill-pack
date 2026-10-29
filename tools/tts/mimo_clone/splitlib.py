"""把一次性生成的整段配音，按句切开。
做法：整段过 faster-whisper 得字级时间戳 → 和稿子逐字（拼音）对齐 → 在相邻两句交界处找最长的静音段，从静音中点切。
返回每句的 wav 文件、音高、与参考音的相似度，以及整段的字错率（cer）。
"""
import difflib, os
import numpy as np, soundfile as sf, librosa
from pypinyin import lazy_pinyin
from asrutil import get_model
from textutil import fixnum
import emb as E


def gaps_of(v, sr, thr=-42, minlen=0.06):
    hop = int(sr * 0.01); n = len(v) // hop
    db = 20 * np.log10(np.array([np.sqrt(np.mean(v[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(n)])); sil = db < thr
    g = []; i = 0
    while i < n:
        j = i
        while j < n and sil[j] == sil[i]: j += 1
        if sil[i] and (j - i) * 0.01 >= minlen: g.append((i * 0.01, j * 0.01))
        i = j
    return g


def split_take(wav, LL, out_prefix, model=None):
    """wav：整段生成的文件；LL：这一段包含的句子（lines.json 里的元素，按顺序）；out_prefix：切出文件名前缀，如 split/S1_t0 → split/S1_t0_L3.wav"""
    m = model or get_model()
    ref = []; owner = []
    for x in LL:
        for c in x["tts"]:
            if c.isalnum(): ref.append(c); owner.append(x["id"])
    rp = [lazy_pinyin(c)[0] for c in ref]; ids = [x["id"] for x in LL]
    v, sr = sf.read(wav); v = v if v.ndim == 1 else v[:, 0]
    y = librosa.resample(v.astype(np.float32), orig_sr=sr, target_sr=16000)
    sg_, _ = m.transcribe(y, language="zh", beam_size=5, word_timestamps=True, condition_on_previous_text=False)
    ch = []; asr = ""
    for sg in sg_:
        asr += sg.text
        for w in sg.words:
            cs = [c for c in fixnum(w.word) if c.isalnum()]
            for k, c in enumerate(cs):
                d = (w.end - w.start) / len(cs); ch.append((c, w.start + k * d, w.start + (k + 1) * d))
    hp = [lazy_pinyin(c[0])[0] for c in ch]
    sm = difflib.SequenceMatcher(None, rp, hp, autojunk=False); r2h = {}
    for p, q, nn in sm.get_matching_blocks():
        for k in range(nn): r2h[p + k] = q + k
    cer = 1 - len(r2h) / max(1, len(ref)); T = {k: ch[r2h[k]] for k in r2h}; G = gaps_of(v, sr)
    bnd = []; ok = True
    for bi in range(len(ids) - 1):
        i = ids[bi]
        ks = [k for k in range(len(ref)) if owner[k] == i]; ks2 = [k for k in range(len(ref)) if owner[k] == ids[bi + 1]]
        a = [T[k][2] for k in reversed(ks) if k in T]; b = [T[k][1] for k in ks2 if k in T]
        if not a or not b: ok = False; bnd.append((0, 0)); continue
        a = a[0]; b = b[0]
        c = [g for g in G if g[1] > a - 0.3 and g[0] < b + 0.3 and g[1] - g[0] >= 0.1]
        if c: g = max(c, key=lambda q: q[1] - q[0]); bnd.append((g[0], g[1]))
        else: ok = False; bnd.append(((a + b) / 2, (a + b) / 2))
    edges = [0.0] + [(g[0] + g[1]) / 2 for g in bnd] + [len(v) / sr]
    os.makedirs(os.path.dirname(out_prefix) or ".", exist_ok=True)
    lines = []
    for bi, i in enumerate(ids):
        a, b = edges[bi], edges[bi + 1]; seg = v[int(a * sr):int(b * sr)]
        fo = f"{out_prefix}_L{i}.wav"; sf.write(fo, seg, sr)
        y16 = librosa.resample(seg.astype(np.float32), orig_sr=sr, target_sr=16000)
        lines.append(dict(i=i, file=fo, f0=round(E.f0med(y16)), sim=round(E.sim(y16), 3), dur=round(b - a, 2), a=round(a, 3), b=round(b, 3)))
    return dict(cer=round(cer, 3), dur=round(len(v) / sr, 2), ok=ok, asr=asr, lines=lines,
                f0all=round(E.f0med(y)), simall=round(E.sim(y), 3), gapw=[round(g[1] - g[0], 2) for g in bnd])
