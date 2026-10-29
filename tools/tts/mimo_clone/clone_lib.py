"""MiMo 声音复刻（mimo-v2.5-tts-voiceclone）。
参考音频放在 audio.voice 字段，格式 "data:audio/wav;base64,..."（或 audio/mpeg），base64 后不超过 10MB。
messages：[{role:user, content:风格描述（建议留空，空的更自然）}, {role:assistant, content:要读的文本}]。
需要环境变量 MIMO_API_KEY（见 ../mimo_common.py）。
"""
import base64, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from mimo_common import post_tts, get_key, MimoKeyError  # noqa: F401

MODEL = "mimo-v2.5-tts-voiceclone"
_cache = {}


def ref_data_uri(ref):
    if ref not in _cache:
        raw = open(ref, "rb").read()
        mime = "audio/mpeg" if ref.lower().endswith(".mp3") else "audio/wav"
        b64 = base64.b64encode(raw).decode()
        if len(b64) > 10 * 1024 * 1024:
            raise ValueError(f"参考音频 base64 后 {len(b64)/1e6:.1f}MB，超过 10MB 上限，请截短（建议 15–30 秒有人声的片段）")
        _cache[ref] = f"data:{mime};base64," + b64
    return _cache[ref]


def synth_clone(text, ref, style=""):
    payload = {"model": MODEL,
               "messages": [{"role": "user", "content": style}, {"role": "assistant", "content": text}],
               "audio": {"format": "wav", "voice": ref_data_uri(ref)}}
    return post_tts(payload)
