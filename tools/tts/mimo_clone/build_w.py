#!/usr/bin/env python3
"""用 whole_split.py 切好的某一条 take（如 W_t2）拼出整条配音。
用法：python build_w.py --lines lines.json --split-dir whole/split --take W_t2 --out vo_raw.wav --timing vo_timing.json --big 4:1.2
  --take    用哪条 take 的全部句子；想逐句混选就自己写 selected.json（{"句id": "wav路径"}）后用 --selected
  --big     关键句后的停顿，格式 句id:秒,句id:秒；换段自动 1.0 秒，其余 0.42 秒，最后一句后 1.4 秒
  --upto N  只拼前 N 句（出开头样片用）
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from buildlib import build, parse_big

ap = argparse.ArgumentParser()
ap.add_argument("--lines", default="lines.json"); ap.add_argument("--split-dir", default="whole/split"); ap.add_argument("--take", default="W_t0")
ap.add_argument("--selected"); ap.add_argument("--out", default="vo_raw.wav"); ap.add_argument("--timing", default="vo_timing.json")
ap.add_argument("--big", default=""); ap.add_argument("--upto", type=int); ap.add_argument("--question-gap", type=float)
a = ap.parse_args()
L = json.load(open(a.lines, encoding="utf8"))
sel = json.load(open(a.selected)) if a.selected else {str(x["id"]): f"{a.split_dir}/{a.take}_L{x['id']}.wav" for x in L}
json.dump(sel, open("selected.json", "w"), indent=1)
build(a.lines, sel, a.out, a.timing, big=parse_big(a.big), q_gap=a.question_gap, upto=a.upto)
