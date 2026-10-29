"""数字转汉字，用于把 ASR 结果里的阿拉伯数字和稿子里的汉字数字对齐。"""
import re
D = "零一二三四五六七八九"


def num2cn(s):
    """'1644'→一六四四（4位以上或0开头逐位读）；'117'→一百一十七式的简化读法"""
    n = int(s)
    if len(s) >= 4 or s.startswith("0"): return "".join(D[int(c)] for c in s)
    if n < 10: return D[n]
    out = ""
    if n >= 100: out += D[n // 100] + "百"; n %= 100
    if n >= 10: out += (D[n // 10] if (n // 10 > 1 or out) else "") + "十"; n %= 10
    elif out and n: out += "零"
    if n: out += D[n]
    return out


def n2c(n):
    n = int(n)
    if n < 10: return D[n]
    if n < 20: return "十" + (D[n % 10] if n % 10 else "")
    if n < 100: return D[n // 10] + "十" + (D[n % 10] if n % 10 else "")
    s = D[n // 100] + "百"; r = n % 100
    if r == 0: return s
    if r < 10: return s + "零" + D[r]
    if r < 20: return s + "一十" + (D[r % 10] if r % 10 else "")
    return s + D[r // 10] + "十" + (D[r % 10] if r % 10 else "")


def fixnum(w):
    return re.sub(r"\d+", lambda m: n2c(m.group()), w)
