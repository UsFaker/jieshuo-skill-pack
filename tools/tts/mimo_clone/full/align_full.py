#!/usr/bin/env python3
"""给拼好的整条配音做逐字对齐（剪辑「按句切镜头」和字幕用）：每句在其时间窗内重新转写，与稿子逐字拼音对齐，
对不上的字用前后已对上的字插值。输出 align_full.json：LS/LE（每句起止）、CH（每字起止）、gaps（静音段）、total、bad（对齐率<0.9 的句）。
用法：python align_full.py --lines lines.json --wav vo_raw_full.wav --timing vo_timing_full.json --out align_full.json
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, ".."))   # 引用上一级的 syn / emb / splitlib 等模块
import argparse, difflib, json, warnings
import numpy as np, soundfile as sf, librosa
warnings.filterwarnings("ignore")
from pypinyin import lazy_pinyin
from asrutil import get_model
from textutil import fixnum

ap = argparse.ArgumentParser()
ap.add_argument("--lines", default="lines.json"); ap.add_argument("--wav", default="vo_raw_full.wav")
ap.add_argument("--timing", default="vo_timing_full.json"); ap.add_argument("--out", default="align_full.json")
a = ap.parse_args()
L = {x["id"]: x for x in json.load(open(a.lines, encoding="utf8"))}; tim = json.load(open(a.timing))
v, sr = sf.read(a.wav); v = v if v.ndim == 1 else v[:, 0]
y = librosa.resample(v.astype(np.float32), orig_sr=sr, target_sr=16000)
hop = int(sr * 0.01); n = len(v) // hop
db = 20 * np.log10(np.sqrt(np.add.reduceat(v[:n * hop] ** 2, np.arange(0, n * hop, hop)) / hop + 1e-12)); sil = db < -45
gaps = []; i = 0
while i < n:
    j = i
    while j < n and sil[j] == sil[i]: j += 1
    if sil[i] and j - i >= 6: gaps.append((round(i * 0.01, 3), round(j * 0.01, 3)))
    i = j
m = get_model(); CH = {}; bad = []
for x in tim:
    i = x["id"]; t0 = max(0, x["start"] - 0.15); t1 = x["end"] + 0.15
    s, _ = m.transcribe(y[int(t0 * 16000):int(t1 * 16000)], language="zh", beam_size=5, word_timestamps=True, condition_on_previous_text=False, initial_prompt=L[i]["tts"])
    ch = []
    for sg in s:
        for w in sg.words:
            cs = [c for c in fixnum(w.word) if c.isalnum()]
            for k, c in enumerate(cs):
                d = (w.end - w.start) / len(cs); ch.append((c, t0 + w.start + k * d, t0 + w.start + (k + 1) * d))
    ref = [c for c in L[i]["tts"] if c.isalnum()]
    rp = [lazy_pinyin(c)[0] for c in ref]; hp = [lazy_pinyin(c[0])[0] for c in ch]
    sm = difflib.SequenceMatcher(None, rp, hp, autojunk=False); r2h = {}
    for p, q, nn in sm.get_matching_blocks():
        for k in range(nn): r2h[p + k] = q + k
    T = [None] * len(ref)
    for k in range(len(ref)):
        if k in r2h: T[k] = [ch[r2h[k]][1], ch[r2h[k]][2]]
    known = [k for k in range(len(ref)) if T[k]]
    for k in range(len(ref)):
        if T[k] is None:
            lo = max([q for q in known if q < k], default=None); hi = min([q for q in known if q > k], default=None)
            if lo is None: T[k] = [x["start"], x["start"] + 0.15]
            elif hi is None: T[k] = [T[lo][1] + (k - lo - 1) * 0.17, T[lo][1] + (k - lo) * 0.17]
            else:
                f = (k - lo) / (hi - lo); tt = T[lo][1] + (T[hi][0] - T[lo][1]) * f; T[k] = [tt, tt + 0.17]
    for t in T: t[0] = round(min(max(t[0], x["start"]), x["end"]), 3); t[1] = round(min(max(t[1], x["start"]), x["end"]), 3)
    CH[i] = T; q = len(r2h) / max(1, len(ref))
    if q < 0.9: bad.append((i, round(q, 2)))
    print(i, len(r2h), len(ref), flush=True)
json.dump(dict(LS={x["id"]: x["start"] for x in tim}, LE={x["id"]: x["end"] for x in tim}, CH=CH, gaps=gaps, total=len(v) / sr, bad=bad), open(a.out, "w"))
print("bad", bad)
