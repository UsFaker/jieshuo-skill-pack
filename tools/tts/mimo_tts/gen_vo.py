#!/usr/bin/env python3
"""用 MiMo 预设音色按块批量配音，每块多出几条 take，供之后挑选。
用法：
  python gen_vo.py --lines lines.json --style-file style.txt --out takes --takes 3 [--voice 白桦] [--max-chars 150] [--workers 6]
lines.json：[{id, sec, text, tts, (可选) breath}, ...]，朗读文本用 tts 字段。
分块规则：同一段落(sec)内累计不超过 max-chars 个字；前一句 breath>0 时另起一块。
输出 takes/c{块号}_t{take号}.wav，同时写 chunks.json（每块包含的句 id）。
"""
import argparse, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tts_lib import synth, STYLE

ap = argparse.ArgumentParser()
ap.add_argument("--lines", required=True); ap.add_argument("--style-file")
ap.add_argument("--out", default="takes"); ap.add_argument("--takes", type=int, default=3)
ap.add_argument("--voice", default="白桦"); ap.add_argument("--max-chars", type=int, default=150)
ap.add_argument("--workers", type=int, default=6)
a = ap.parse_args()
style = open(a.style_file, encoding="utf8").read().strip() if a.style_file else STYLE
L = json.load(open(a.lines, encoding="utf8"))
ch, cur = [], []
for x in L:
    if cur and (x["sec"] != cur[-1]["sec"] or sum(len(y["tts"]) for y in cur) + len(x["tts"]) > a.max_chars or cur[-1].get("breath", 0) > 0):
        ch.append(cur); cur = []
    cur.append(x)
if cur: ch.append(cur)
json.dump([[y["id"] for y in c] for c in ch], open("chunks.json", "w"))
print(len(ch), "chunks", [len("".join(y["tts"] for y in c)) for c in ch])
os.makedirs(a.out, exist_ok=True)

def run(arg):
    i, k = arg; out = f"{a.out}/c{i:02d}_t{k}.wav"
    if os.path.exists(out): return out
    text = "".join(y["tts"] for y in ch[i])
    for n in range(5):
        try:
            open(out, "wb").write(synth(text, voice=a.voice, style=style)); return out
        except Exception as e:
            if "MIMO_API_KEY" in str(e) or "API Key" in str(e): raise
            print("fail", out, e, flush=True); time.sleep(5 + 5 * n)

with ThreadPoolExecutor(a.workers) as ex:
    for r in ex.map(run, [(i, k) for i in range(len(ch)) for k in range(a.takes)]): print("ok", r, flush=True)
print("ALLDONE")
