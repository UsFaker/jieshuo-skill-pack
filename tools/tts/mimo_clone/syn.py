"""带重试的复刻合成。服务偶尔返回 429 或坏音频，所以失败后等 25 秒再来，最多 tries 次。"""
import time
from clone_lib import synth_clone, MimoKeyError


def syn(text, ref, style="", tries=80, wait=25):
    for k in range(tries):
        try:
            d = synth_clone(text, ref, style)
            if len(d) > 2000:
                return d
        except MimoKeyError:
            raise                      # 没设 key 不用重试，直接报错
        except Exception as e:
            print("retry", k, str(e)[:80], flush=True)
        time.sleep(wait)
    raise RuntimeError("MiMo 复刻连续失败，请检查网络、额度和限流")
