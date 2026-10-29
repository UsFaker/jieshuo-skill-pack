"""韵律特征（音高起伏、停顿、有声时长等），用来比较各 take 是否像「说话」而不是「朗诵」。需要 praat-parselmouth。"""
import numpy as np


def feats(snd):
    p = snd.to_pitch_ac(time_step=0.01, pitch_floor=60, pitch_ceiling=300, octave_jump_cost=0.6, voicing_threshold=0.5)
    f = p.selected_array["frequency"]; v = f > 0
    st = 12 * np.log2(f[v] / 100) if v.any() else np.array([0.])
    I = snd.to_intensity(time_step=0.01).values[0]
    runs = []; c = 0
    for x in v:
        if x: c += 1
        else:
            if c: runs.append(c); c = 0
    if c: runs.append(c)
    d = np.abs(np.diff(st)) if len(st) > 1 else np.array([0.])
    q = np.percentile(st, [25, 75]) if len(st) > 3 else [0, 0]
    return dict(st_iqr=float(q[1] - q[0]), hi=float(np.mean(st > np.median(st) + 6)), st_med=float(np.median(st)), st_std=float(np.std(st)),
                st_rng=float(np.percentile(st, 95) - np.percentile(st, 5)),
                swing=float(np.mean(d[d < 4])) if (d < 4).any() else 0,
                int_pk=float(np.percentile(I, 98) - np.median(I[I > np.percentile(I, 30)])),
                longest_voiced=max(runs) / 100 if runs else 0, voiced=v.sum() / 100)
