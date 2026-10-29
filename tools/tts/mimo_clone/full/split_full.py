#!/usr/bin/env python3
"""把 gen_sec.py 生成的各段 take 按句切开并打分。结果追加进 split_res.json（已处理的跳过，可断点续跑）。
用法：python split_full.py --lines lines.json --ref ref.wav --secs 1,2,3 --whole whole --split split --res split_res.json
输出 split/S{sec}_t{k}_L{句id}.wav。
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, ".."))   # 引用上一级的 syn / emb / splitlib 等模块
import argparse, glob, json
import emb as E
from splitlib import split_take
from asrutil import get_model

ap = argparse.ArgumentParser()
ap.add_argument("--lines", default="lines.json"); ap.add_argument("--ref", required=True); ap.add_argument("--secs", required=True)
ap.add_argument("--whole", default="whole"); ap.add_argument("--split", default="split"); ap.add_argument("--res", default="split_res.json")
a = ap.parse_args(); E.set_ref(a.ref)
L = json.load(open(a.lines, encoding="utf8")); m = get_model()
out = json.load(open(a.res)) if os.path.exists(a.res) else {}
for s in a.secs.split(","):
    LL = [x for x in L if str(x["sec"]) == s]
    for f in sorted(glob.glob(f"{a.whole}/S{s}_t?.wav")):
        if f in out: continue
        r = split_take(f, LL, f"{a.split}/S{s}_{os.path.basename(f)[-6:-4]}", m); r["sec"] = s; out[f] = r
        print(f, "cer", r["cer"], "ok", r["ok"], "f0all", r["f0all"], "sim", r["simall"], "f0/l", [o["f0"] for o in r["lines"]], "sim/l", [o["sim"] for o in r["lines"]], flush=True)
        json.dump(out, open(a.res, "w"), ensure_ascii=False, indent=1)
