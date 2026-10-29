#!/usr/bin/env python3
"""把 gen_whole.py 生成的整段 take 按句切开，并打分（字错率、音高、说话人相似度）。
用法：python whole_split.py --lines lines.json --ref ref.wav --whole whole --out whole/split --res whole_res.json
输出：whole/split/W_t{k}_L{句id}.wav；打分写入 --res。
看什么：cer<0.05；同一条 take 各句 f0 差在 15% 内；sim（对参考音）≥0.88，最低两两≥0.8；ok=False 表示某个句界没找到静音，要换 take。
"""
import argparse, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emb as E
from splitlib import split_take
from asrutil import get_model

ap = argparse.ArgumentParser()
ap.add_argument("--lines", default="lines.json"); ap.add_argument("--ref", required=True)
ap.add_argument("--whole", default="whole"); ap.add_argument("--out", default="whole/split"); ap.add_argument("--res", default="whole_res.json")
a = ap.parse_args(); E.set_ref(a.ref)
L = json.load(open(a.lines, encoding="utf8")); m = get_model(); res = {}
for f in sorted(glob.glob(f"{a.whole}/W_t?.wav")):
    if os.path.getsize(f) < 5000: continue
    r = split_take(f, L, f"{a.out}/{os.path.basename(f)[:-4]}", m); res[f] = r
    print(f, "cer", r["cer"], "ok", r["ok"], "dur", r["dur"], "f0all", r["f0all"], "sim", r["simall"],
          "f0/line", [o["f0"] for o in r["lines"]], "sim/line", [o["sim"] for o in r["lines"]], "gaps", r["gapw"], flush=True)
json.dump(res, open(a.res, "w"), ensure_ascii=False, indent=1)
