"""MiMo 预设音色 TTS（mimo-v2.5-tts，预设音色如「白桦」）。
用法：
    from tts_lib import synth
    wav_bytes = synth("要读的文本", voice="白桦", style="风格描述（可空）")
messages 格式：[{role:user, content:风格描述}, {role:assistant, content:要读的文本}]。
需要环境变量 MIMO_API_KEY，见 ../mimo_common.py。
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from mimo_common import get_key, post_tts, get_endpoint, MimoKeyError  # noqa: F401

MODEL = "mimo-v2.5-tts"

# 默认风格示例（来自张居正片；自己换成合适的）。读音提示放在风格里，很管用。
STYLE = ("沉稳、略带沙哑的中年男声，像深夜给朋友讲一段压在心里很久的历史旧事，自己也被这个故事打动。"
         "边想边说，语速有快有慢，句与句之间自然换气，句尾自然下落；不要朗诵腔，不要播音腔，不要每句都用力演。整段音色保持一致。"
         "读音务必准确：（在这里列出专名/多音字读法，例如：张居正的正读zhèng；万历的历读lì）")


def synth(text, voice="白桦", style=STYLE, timeout=600):
    payload = {"model": MODEL,
               "messages": [{"role": "user", "content": style}, {"role": "assistant", "content": text}],
               "audio": {"format": "wav", "voice": voice}}
    return post_tts(payload, timeout=timeout)
