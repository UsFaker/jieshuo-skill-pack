#!/usr/bin/env python3
"""稿子 AI 味扫描（v2：加入叙述者口吻、小句节奏、时长估算，基准来自 11 条抖音参考）。用法：python3 ai_scan.py 稿子.md [--names 商鞅,秦孝公,...]
支持 `0:12` 时间戳行、编号行、纯文本；自动去掉【大字：…】。"""
import re,sys,collections
args=sys.argv[1:]; names=[]
if '--names' in args:
    i=args.index('--names'); names=args[i+1].split(','); args=args[:i]+args[i+2:]
raw=open(args[0]).read()
lines=[]
for l in raw.splitlines():
    if l.lstrip().startswith('#') or l.lstrip().startswith('- ') or not l.strip(): continue
    l=re.sub(r'【大字：.*?】','',l); l=re.sub(r'^\d+\.\s*','',l); l=re.sub(r'`[\d:.]+`','',l).strip()
    if l: lines.append(l)
text=''.join(lines)
BAN={"结构标签":r"第[一二三四五六七八九十\d]+个(爽点|点|阶段)|接下来我们看|下面我们来看",
 "比喻预告":r"用今天的话说|放到今天|换成今天|这等于|相当于今天",
 "场面后解释":r"这一步[，,]?就是|这就是最|这说明了",
 "空洞预告":r"答案可能|真正的反转|扎心|细思极恐|你品",
 "抽象标签句":r"被.{1,4}反噬|只认.{1,4}不认|一个.{2,14}的(男人|女人|人)[。！]?$",
 "AI套话":r"值得一提的是|不得不说|某种意义上|让我们|总而言之|综上|毋庸置疑|不可否认"}
LIMIT={"规则":2,"制度":2,"体制":1,"系统":2,"公司":1,"企业":1,"KPI":1,"老板":1,"业绩":1,"打工人":1,"硬生生":1,"其实":3,"真正":2,"本质":1}
print("== 禁用句式（出现即改）")
for k,p in BAN.items():
    hits=[l for l in lines if re.search(p,l)]
    for h in hits: print(f"  [{k}] {h}")
print("== 限量词（实际/上限）")
for w,lim in LIMIT.items():
    c=text.count(w)
    if c: print(f"  {w}: {c}/{lim}" + ("  <-- 超了" if c>lim else ""))
q=[l for l in lines if '？' in l or '?' in l]
addr=[l for l in lines if re.search(r'大家(?!族|庭)|你们|观众|评论区|朋友们|各位|你(?!的老师)',l)]
voice=[l for l in lines if re.search(r'我觉得|我看|在我看来|说白了|注意|这叫什么|你想想|你记住|你看|说实话|讲真|未必|大错特错|太浅了|要我说|换你|你猜',l)]
print(f"== 问句 {len(q)} 个（每个问句下一句要答上；抽象二选一要删）")
for l in q: print("  ?",l)
print(f"== 对观众说话 {len(addr)} 处（抖音参考每条 5–25 处；建议 4–10 处，每处都要带具体内容）")
for l in addr: print("  >",l)
print(f"== 叙述者口吻 {len(voice)} 处（判断 / 提醒 / 吐槽；参考视频每分钟 1–3 处，0 处就是在念编年史）")
for l in voice: print("  *",l)
import statistics as _st
_cl=[len(re.sub(r'[^\u4e00-\u9fff0-9A-Za-z]','',x)) for x in re.split(r'[。！？?!，,、；;：:]',text)]
_cl=[x for x in _cl if x]
_ch=len(re.sub(r'[^\u4e00-\u9fff0-9A-Za-z]','',text))
print(f"== 节奏：{_ch} 字，按 5.3 字/秒约 {_ch/5.3/60:.1f} 分钟；小句平均 {_st.mean(_cl):.1f} 字，中位 {_st.median(_cl):.0f}，6 字以内占 {sum(x<=6 for x in _cl)/len(_cl)*100:.0f}%（参考视频：平均 8.4–12 字，6 字以内占 15–39%；6 字以内超过 50% 听起来像发电报）")
# 重复实词：2-4 字 n-gram
clean=re.sub(r'[^\u4e00-\u9fffA-Za-z]','',text)
for n in names: clean=clean.replace(n,'')
stop=set("一个他的了是在这就也不都没有我们他们自己可是但是因为所以然后已经还是什么时候这个那个一样".split())
cnt=collections.Counter()
for n in (2,3,4):
    for i in range(len(clean)-n+1):
        g=clean[i:i+n]
        if any(ch in "的了是在和也就都着把被给" for ch in (g[0],g[-1])): continue
        cnt[g]+=1
top=[(g,c) for g,c in cnt.most_common(400) if c>=4 and g not in stop]
seen=[]
for g,c in top:
    if any(g in s and c<=cs for s,cs in seen): continue
    seen.append((g,c))
print("== 重复词（≥4 次，人名已排除；主题词要换说法）")
print("  "+"、".join(f"{g}×{c}" for g,c in seen[:30]))
# 主角名第一次出现
if names:
    first=names[0]; pos=text.find(first)
    print(f"== 主角「{first}」第一次出现在第 {pos} 个字（约 {pos/5:.0f} 秒）；前 15 秒内要有身份标签+成就+下场")
