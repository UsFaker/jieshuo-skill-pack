#!/usr/bin/env python3
"""全稿拼配音。用法：
python build_vo_full.py --lines lines.json --selected selected_full.json --out vo_raw_full.wav --timing vo_timing_full.json \\
       --big 4:1.2,8:1.4,21:1.0,31:1.2
句间停顿：默认 0.42；换段 1.0；--big 指定的关键句后 0.6–1.4（揭晓、大转折后留气口）；最后一句后 1.4。不加速、不压缩停顿。
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, ".."))   # 引用上一级的 syn / emb / splitlib 等模块
import argparse
from buildlib import build, parse_big

ap = argparse.ArgumentParser()
ap.add_argument("--lines", default="lines.json"); ap.add_argument("--selected", default="selected_full.json")
ap.add_argument("--out", default="vo_raw_full.wav"); ap.add_argument("--timing", default="vo_timing_full.json")
ap.add_argument("--big", default=""); ap.add_argument("--default-gap", type=float, default=0.42); ap.add_argument("--sec-gap", type=float, default=1.0)
a = ap.parse_args()
build(a.lines, a.selected, a.out, a.timing, big=parse_big(a.big), default_gap=a.default_gap, sec_gap=a.sec_gap)
