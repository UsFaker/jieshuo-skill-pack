"""把挑好的各句 wav 拼成整条配音，句间插入设定的停顿（不加速、不压缩停顿）。
每句先去掉头尾静音，句内超过 0.32 秒的长静音裁到 0.32 秒（只裁生成时多出来的，不动我们设的句间停顿）。
句间停顿：默认 0.42 秒；换段 1.0 秒；问句 0.75 秒（可选）；--big 里指定的关键句 1.2–1.4 秒；最后一句后 1.4 秒。
"""
import json, subprocess
import numpy as np, soundfile as sf

SR = 48000


def load(f):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32).copy()


def clean(x, thr_db=-45, cap=0.32):
    hop = int(SR * 0.01); n = len(x) // hop
    db = 20 * np.log10(np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(n)]))
    sil = db < thr_db; nz = np.where(~sil)[0]; a = max(0, nz[0] - 3); b = min(n, nz[-1] + 1 + 6)
    out = []; i = a
    while i < b:
        j = i
        while j < b and sil[j] == sil[i]: j += 1
        seg = x[i * hop:j * hop]
        if sil[i] and (j - i) * 0.01 > cap: k = int(cap * SR); seg = np.concatenate([seg[:k // 2], seg[-k // 2:]])
        out.append(seg); i = j
    y = np.concatenate(out); f = int(SR * 0.01); y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f); return y


def parse_big(s):
    """'4:1.2,8:1.4' → {4:1.2, 8:1.4}"""
    return {int(k): float(v) for k, v in (p.split(":") for p in s.split(",") if p)} if s else {}


def build(lines_path, selected, out_wav, out_timing, big=None, default_gap=0.42, sec_gap=1.0, q_gap=None, end_gap=1.4, upto=None, lead=0.3):
    L = json.load(open(lines_path, encoding="utf8")); X = {x["id"]: x for x in L}
    sel = json.load(open(selected)) if isinstance(selected, str) else selected   # {line_id(str): wav}
    big = big or {}
    ids = sorted(X)
    if upto: ids = [i for i in ids if i <= upto]

    def gap(i):
        if i in big: return big[i]
        nxt = X.get(i + 1)
        if nxt and nxt["sec"] != X[i]["sec"]: return sec_gap
        if q_gap and X[i]["text"].rstrip().endswith(("？", "?")): return q_gap
        return default_gap
    parts = [np.zeros(int(SR * lead), np.float32)]; t = lead; tim = []
    for i in ids:
        y = clean(load(sel[str(i)]))
        tim.append({"id": i, "sec": X[i]["sec"], "start": round(t, 3), "end": round(t + len(y) / SR, 3), "text": X[i]["text"], "take": sel[str(i)]})
        parts.append(y); t += len(y) / SR
        g = gap(i) if i != ids[-1] else end_gap; parts.append(np.zeros(int(SR * g), np.float32)); t += g
    v = np.concatenate(parts); sf.write(out_wav, v, SR); json.dump(tim, open(out_timing, "w"), ensure_ascii=False, indent=1)
    chars = sum(len([c for c in X[i]["text"] if c.isalnum()]) for i in ids); sp = sum(x["end"] - x["start"] for x in tim)
    print("dur", round(len(v) / SR, 2), "speech", round(sp, 1), "cps_speech", round(chars / sp, 2), "cps_overall", round(chars / (len(v) / SR), 2))
    return tim
