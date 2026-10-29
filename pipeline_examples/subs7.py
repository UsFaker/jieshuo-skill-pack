# [示例] 商鞅 v7 整片剪辑管线的参考实现。路径和素材名写死为当时的项目（/workspace/shangyang/...），换项目时照着改；用法和顺序见 pipeline_examples/README.md。
import sys,re
R='/workspace/shangyang/v7'; N=int(sys.argv[1])
# (start,end,text) 烧录字幕，按静音锚点分句；[ ]内标红
C=[(0.30,2.40,'公元前三百多年的一天'),(2.69,4.10,'秦国渭河边上'),(4.39,5.80,'跪着[七百多]个犯人'),
(6.20,8.45,'从早上审到天黑'),(8.74,9.84,'一个一个判'),(10.09,11.15,'一个一个[杀]'),
(11.52,13.30,'那天[渭河水]都染红了'),(13.60,15.60,'哭喊声传出去好几里地'),
(15.99,18.90,'坐在河边一个一个判下去的'),(19.20,20.32,'就是[商鞅]'),
(21.48,22.26,'课本里'),(22.56,24.76,'他是让秦国从西边穷国'),(24.90,27.32,'变成头号强国的大改革家'),
(27.71,29.36,'可秦国人提起他'),(29.66,32.20,'头一个想到的，是他的[狠]')]
if N==8: C+=[(32.59,33.80,'他对百姓狠'),(33.92,34.85,'对太子狠'),(35.14,36.25,'对夸他的人狠'),(36.54,37.55,'对老朋友狠'),
(37.92,38.52,'到最后'),(38.82,39.46,'这股[狠]'),(39.93,40.78,'一点不剩'),(41.08,42.70,'全落回了他自己身上')]
def fmt(t): return f'{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}'
hdr="""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Source Han Serif CN Heavy,70,&H00FFFFFF,&H000000FF,&H00000000,&H96000000,0,0,0,0,100,100,2,0,1,4.5,2,2,80,80,58,1
Style: Tag,Source Han Serif CN Heavy,64,&H00FFFFFF,&H000000FF,&H00000000,&H96000000,0,0,0,0,100,100,6,0,1,3,1,1,110,80,230,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev=''
for a,b,t in C:
    t=re.sub(r'\[(.*?)\]',lambda m:'{\\c&H0C00F2&}'+m.group(1)+'{\\c&HFFFFFF&}',t)
    ev+=f'Dialogue: 0,{fmt(a-0.04)},{fmt(b+0.06)},Sub,,0,0,0,,{t}\n'
ev+=f"Dialogue: 1,{fmt(19.70)},{fmt(21.25)},Tag,,0,0,0,,{{\\fad(200,300)}}商鞅\n"
open(f'{R}/edit/subs_{N}.ass','w').write(hdr+ev)
print(len(C),'subs; max chars',max(len(re.sub(r'[\[\]，]','',t)) for _,_,t in C))
