#!/usr/bin/env python3
"""给切好的单句 wav 打分：字错率（拼音级）、有效语速（字/秒）、韵律特征。
用法：python score_c.py --lines lines.json --out scores.json whole/split/W_t0_L1.wav whole/split/W_t0_L2.wav ...
文件名里要有 _L{句id}_ 或 _L{句id}.wav。可断点续跑（已打分的跳过）。需要 praat-parselmouth。
"""
import argparse, difflib, json, os, re, sys
import parselmouth
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from faster_whisper.vad import get_speech_timestamps, VadOptions
from pypinyin import lazy_pinyin
from asrutil import get_model, load16
from textutil import num2cn
from prosody import feats

ap = argparse.ArgumentParser(); ap.add_argument("--lines", default="lines.json"); ap.add_argument("--out", default="scores.json"); ap.add_argument("files", nargs="+")
a = ap.parse_args()
L = {x["id"]: x for x in json.load(open(a.lines, encoding="utf8"))}
m = get_model()
R = json.load(open(a.out)) if os.path.exists(a.out) else {}
for f in a.files:
    if f in R: continue
    i = int(re.search(r"_L(\d+)[_.]", os.path.basename(f)).group(1)); y = load16(f); n = len([c for c in L[i]["text"] if c.isalnum()])
    if len(y) / 16000 > n / 1.5 + 1: R[f] = dict(id=i, cer=9, asr="TOO LONG", sp=0); continue
    ts = get_speech_timestamps(y, VadOptions(min_silence_duration_ms=120, speech_pad_ms=30, threshold=0.5)); sp = sum(t["end"] - t["start"] for t in ts) / 16000
    s, _ = m.transcribe(y, language="zh", beam_size=5, condition_on_previous_text=False)
    txt = re.sub(r"\d+", lambda q: num2cn(q.group()), "".join(z.text for z in s))
    ref = lazy_pinyin([c for c in re.sub(r"\d+", lambda q: num2cn(q.group()), L[i]["tts"]) if c.isalnum()]); hyp = lazy_pinyin([c for c in txt if c.isalnum()])
    sm = difflib.SequenceMatcher(None, ref, hyp, autojunk=False); mm = sum(q.size for q in sm.get_matching_blocks())
    cer = max(1 - mm / len(ref), (len(hyp) - len(ref)) / len(ref))
    fe = feats(parselmouth.Sound(f))
    R[f] = dict(id=i, asr=txt, cer=round(cer, 3), sp=round(n / max(sp, 0.1), 2), dur=round(len(y) / 16000, 2), **{k: round(v, 3) for k, v in fe.items()})
    print(f, R[f]["cer"], R[f]["sp"], round(fe["st_iqr"], 1), txt, flush=True)
    json.dump(R, open(a.out, "w"), ensure_ascii=False, indent=0)
