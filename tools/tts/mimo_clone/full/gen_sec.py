#!/usr/bin/env python3
"""长稿按段落（sec）分别一次性生成，每段多条 take。整段一次生成音色最一致，所以不要把一段拆小。
用法：python gen_sec.py --lines lines.json --ref ref.wav --n 4 --secs 1,2,3,4,5,6,7,8 --out whole [--k0 0]
输出 whole/S{sec}_t{k}.wav。已存在的跳过，可断点续跑。--k0 从第几条 take 开始补。
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, ".."))   # 引用上一级的 syn / emb / splitlib 等模块
import argparse, json
from syn import syn

ap = argparse.ArgumentParser()
ap.add_argument("--lines", default="lines.json"); ap.add_argument("--ref", required=True)
ap.add_argument("--n", type=int, default=3); ap.add_argument("--secs", required=True, help="段落编号，逗号分隔，要和 lines.json 的 sec 一致")
ap.add_argument("--k0", type=int, default=0); ap.add_argument("--out", default="whole"); ap.add_argument("--style", default="")
a = ap.parse_args()
L = json.load(open(a.lines, encoding="utf8")); os.makedirs(a.out, exist_ok=True)
for k in range(a.k0, a.n):
    for s in a.secs.split(","):
        f = f"{a.out}/S{s}_t{k}.wav"
        if os.path.exists(f) and os.path.getsize(f) > 5000: continue
        txt = "".join(x["tts"] for x in L if str(x["sec"]) == s)
        open(f, "wb").write(syn(txt, a.ref, a.style)); print(f, flush=True)
print("ALLDONE")
