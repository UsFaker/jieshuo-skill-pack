"""faster-whisper 小工具。环境变量：WHISPER_MODEL（默认 medium）、WHISPER_DEVICE（cpu/cuda，默认 cpu）、WHISPER_THREADS（默认 8）。
配音核对一律用 float32，别用 int8，转写会差很多。"""
import os, subprocess, numpy as np

_m = {}


def load16(f):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


def get_model(name=None):
    from faster_whisper import WhisperModel
    name = name or os.environ.get("WHISPER_MODEL", "medium")
    if name not in _m:
        dev = os.environ.get("WHISPER_DEVICE", "cpu")
        _m[name] = WhisperModel(name, device=dev, compute_type="float32",
                                cpu_threads=int(os.environ.get("WHISPER_THREADS", "8")))
    return _m[name]
