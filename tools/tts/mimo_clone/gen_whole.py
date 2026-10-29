#!/usr/bin/env python3
"""把整篇（或一个段落）稿子一次性生成多条 take——同一次调用音色最一致。
用法：
  python gen_whole.py --lines lines.json --ref ref.wav --n 4 --out whole            # 全稿一次
  python gen_whole.py --lines lines.json --ref ref.wav --n 4 --out whole --sec 1     # 只生成第 1 段
输出 whole/W_t{k}.wav（全稿）或 whole/S{sec}_t{k}.wav（单段）。已存在的文件会跳过，可以断点续跑。
每次调用建议不超过约 400 字；更长的稿子用 full/gen_sec.py 按段落生成。
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from syn import syn

ap = argparse.ArgumentParser()
ap.add_argument("--lines", default="lines.json"); ap.add_argument("--ref", required=True)
ap.add_argument("--n", type=int, default=3); ap.add_argument("--out", default="whole")
ap.add_argument("--sec", help="只生成这个段落（lines.json 里的 sec 值）"); ap.add_argument("--style", default="")
a = ap.parse_args()
L = json.load(open(a.lines, encoding="utf8"))
if a.sec is not None: L = [x for x in L if str(x["sec"]) == a.sec]
txt = "".join(x["tts"] for x in L); print(txt)
os.makedirs(a.out, exist_ok=True)
tag = "W" if a.sec is None else f"S{a.sec}"
for k in range(a.n):
    f = f"{a.out}/{tag}_t{k}.wav"
    if os.path.exists(f) and os.path.getsize(f) > 5000: continue
    open(f, "wb").write(syn(txt, a.ref, a.style)); print(f, flush=True)
print("ALLDONE")
