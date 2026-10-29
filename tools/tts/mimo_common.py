"""MiMo TTS 公共部分：密钥、接口地址、HTTP 调用。

密钥一律从环境变量读，包里不带任何密钥：
    export MIMO_API_KEY=你的key            # 必填
    export MIMO_ENDPOINT=https://api.xiaomimimo.com/v1/chat/completions   # 可选，默认就是这个
    export MIMO_API_KEY_FILE=/path/to/key.txt   # 可选：不想把 key 放环境变量时，指向只含 key 的文件
"""
import base64, json, os, urllib.request, urllib.error
from pathlib import Path

DEFAULT_ENDPOINT = "https://api.xiaomimimo.com/v1/chat/completions"


class MimoKeyError(RuntimeError):
    pass


def get_endpoint():
    return os.environ.get("MIMO_ENDPOINT", DEFAULT_ENDPOINT)


def get_key():
    k = os.environ.get("MIMO_API_KEY", "").strip()
    if not k:
        f = os.environ.get("MIMO_API_KEY_FILE", "").strip()
        if f:
            if not Path(f).is_file():
                raise MimoKeyError(f"MIMO_API_KEY_FILE 指向的文件不存在：{f}")
            k = Path(f).read_text().strip()
    if not k:
        raise MimoKeyError(
            "没有找到 MiMo 的 API Key。请先设置环境变量：\n"
            "    export MIMO_API_KEY=你的key\n"
            "（也可以 export MIMO_API_KEY_FILE=存放key的文件路径）。key 在小米 MiMo 开放平台获取。")
    return k


def post_tts(payload, timeout=600):
    """发一次 chat/completions 请求，返回音频字节（wav）。"""
    key = get_key()
    req = urllib.request.Request(get_endpoint(), data=json.dumps(payload).encode(),
                                 headers={"api-key": key, "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"MiMo 接口返回 HTTP {e.code}：{e.read().decode(errors='ignore')[:200]}（429 是限流，稍后重试）") from None
    msg = body["choices"][0]["message"]
    a = msg.get("audio") or {}
    b64 = a.get("data") or a.get("content") or msg.get("content")
    if not b64:
        raise RuntimeError("MiMo 返回里没有音频数据：" + json.dumps(body, ensure_ascii=False)[:200])
    if "," in b64[:80]:
        b64 = b64.split(",", 1)[1]
    return base64.b64decode(b64)
