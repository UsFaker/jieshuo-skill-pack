"""说话人相似度（Resemblyzer）和音高（librosa pyin）。
参考音频路径：环境变量 CLONE_REF，或调用 set_ref(path)。脚本里的 --ref 参数会自动调用 set_ref。
"""
import os, warnings
import numpy as np, soundfile as sf, librosa
warnings.filterwarnings("ignore")
from resemblyzer import VoiceEncoder, preprocess_wav

_enc = VoiceEncoder()
_ref = {"path": os.environ.get("CLONE_REF"), "emb": None}


def load16(f):
    x, sr = sf.read(f); x = x if x.ndim == 1 else x[:, 0]
    return librosa.resample(x.astype(np.float32), orig_sr=sr, target_sr=16000) if sr != 16000 else x.astype(np.float32)


def emb(y):
    return _enc.embed_utterance(preprocess_wav(y, source_sr=16000))


def f0med(y):
    f0, v, _ = librosa.pyin(y, fmin=70, fmax=400, sr=16000); f0 = f0[~np.isnan(f0)]
    return float(np.median(f0)) if len(f0) else 0.0


def set_ref(path):
    _ref["path"] = path; _ref["emb"] = None


def ref_emb():
    """参考音频的说话人向量（懒加载）。"""
    if _ref["emb"] is None:
        if not _ref["path"]:
            raise RuntimeError("没有指定参考音频：用 --ref 或 export CLONE_REF=参考.wav")
        _ref["emb"] = emb(load16(_ref["path"]))
    return _ref["emb"]


def sim(y):
    return float(emb(y) @ ref_emb())
