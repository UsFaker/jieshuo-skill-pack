#!/usr/bin/env python3
"""每个段落挑一条最好的 take（整段一条，保证同段音色一致），输出 selected_full.json（{句id: wav路径}）。
评分（越低越好）：cer×4 + 相似度低于 0.88 的句占比 + 音高极差×0.6 + 平均音高偏离目标×1.5 − (整段相似度−0.95)。
用法：python select_full.py --res split_res.json --target-f0 177 --out selected_full.json [--base-selected selected_W.json]
  --target-f0   参考音的音高中位数 Hz（用 emb.f0med 量一下参考音）
  --base-selected  已经有的前几句选择（可选），会先垫进去，再被各段结果覆盖
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, ".."))   # 引用上一级的 syn / emb / splitlib 等模块
import argparse, json, numpy as np

ap = argparse.ArgumentParser(); ap.add_argument("--res", default="split_res.json"); ap.add_argument("--target-f0", type=float, default=177)
ap.add_argument("--out", default="selected_full.json"); ap.add_argument("--base-selected"); ap.add_argument("--bad-sim", type=float, default=0.88)
a = ap.parse_args()
d = json.load(open(a.res)); rows = []
for k, v in sorted(d.items()):
    if not v["ok"]: print(k, "NOT OK cer", v["cer"]); continue
    f0 = [l["f0"] for l in v["lines"] if l["f0"]]; sims = [l["sim"] for l in v["lines"]]
    rows.append((v["sec"], k, v["cer"], v["f0all"], v["simall"], min(sims), sum(s < a.bad_sim for s in sims), len(sims), (max(f0) - min(f0)) / np.median(f0), np.std(f0) / np.mean(f0)))
for r in rows: print("S%s %-18s cer %.3f f0all %3d simall %.3f minsim %.3f bad %d/%d range %.2f cv %.3f" % r)
print("---- select"); best = {}
for r in rows:
    sec, k, cer, f0a, sa, ms, bad, n, rg, cv = r
    sc = cer * 4 + bad / n + rg * 0.6 + abs(f0a - a.target_f0) / a.target_f0 * 1.5 - (sa - 0.95)
    if sec not in best or sc < best[sec][0]: best[sec] = (sc, k)
sel = json.load(open(a.base_selected)) if a.base_selected else {}
for sec, (sc, k) in sorted(best.items()):
    v = d[k]; print(sec, k, round(sc, 3), "bad lines", [(l["i"], l["sim"], l["f0"], l["dur"]) for l in v["lines"] if l["sim"] < a.bad_sim])
    for l in v["lines"]: sel[str(l["i"])] = l["file"]
json.dump(sel, open(a.out, "w"), indent=1); print(len(sel), "lines selected")
