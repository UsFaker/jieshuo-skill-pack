import json,os
import os
B=os.path.dirname(os.path.abspath(__file__))+'/'   # 套件目录；bg/matte 用相对路径 assets/bg、assets/matte，换项目时改这里或自己放图
def sc(name,bg,items,subs,matte=None,dur=3.5,still=3.0,zoomIn=True,flashAt=None):
    json.dump(dict(bg='assets/bg/'+bg+'.jpg',matte=('assets/matte/'+matte+'.png') if matte else None,items=items,subs=subs,dur=dur,still=still,zoomIn=zoomIn,flashAt=flashAt),
              open(B+f'scenes/{name}.json','w'),ensure_ascii=False,indent=1)
S=lambda t,a=0,b=9:[dict(t0=a,t1=b,text=t)]
# 1 人名：毛笔红白相间，脸侧，与眼同高
sc('01_商鞅','portrait',[dict(preset='BRUSH',text='w:商|r:鞅',size=330,x=700,y=420,t0=0.25,ls=-85)],
   S('[商鞅]，让秦国从一个被人看不起的西部穷国'))
# 2 负面词：白宋体，大红天空中心，重影
sc('02_车裂','chariots_dusk',[dict(preset='BANGSHU',text='车裂',size=300,x=960,y=290,t0=0.3,ls=10)],
   S('可他的下场，是被秦国[车裂]示众，全家被杀'))
# 3 现代梗：红宋两侧夹击 + 中间白粗黑 KPI（照 数据 KPI 效率）
sc('03_KPI','army',[dict(preset='SONG_RED',text='砍首级',size=124,x=600,y=500,t0=0.2),
                    dict(preset='SONG_RED',text='升爵位',size=124,x=1330,y=500,t0=0.75),
                    dict(preset='SONG_WHITE',text='KPI',size=190,x=960,y=690,t0=1.4,ls=4,anim='zoomPunch')],
   S('这就是最直接的[KPI]，绩效看得见，奖励马上兑现'),still=3.2)
# 4 爽点名：红宋体压在木杆后（景深压字，照 明朝第一政治家 帽子挡字）
sc('04_立木为信','gate_pole',[dict(preset='SONG_RED',text='立木为信',size=180,x=1000,y=150,t0=0.3,behind=True,ls=14)],
   S('第一个爽点，[立木为信]'),matte='gate_pole')
# 5 数字：竖排侧栏，数字红且放大（照 续命150年）
sc('05_五十金','gate_pole',[dict(preset='SONG_WHITE',text='w:赏|r1.2:五十|w:金',size=150,x=300,y=400,t0=0.2,vertical=True,stagger=0.09)],
   S('商鞅直接把赏金加到[五十金]'),zoomIn=True)
# 6 事件：巨大红宋体放在人物身后（照 独裁者）
sc('06_太子犯法','palace_prince',[dict(preset='SONG_RED',text='太子犯法',size=270,x=960,y=560,t0=0.25,behind=True,ls=6)],
   S('就在这时，[太子犯法]了'),matte='palace_prince')
# 7 金句：双行错位，白在上、红在下后入（照 反人性/反体制）
sc('07_挡在门外','inn_night',[dict(preset='SONG_WHITE',text='被自己的法',size=118,x=470,y=330,t0=0.2),
                          dict(preset='SONG_RED',text='挡在门外',size=158,x=600,y=478,t0=1.0)],
   S('商鞅，被自己定的法，挡在了门外'),still=3.0)
# 8 结尾升华：黄油体红 + 白宋第二行（照 家国担当 / 悲剧英雄）
sc('08_117年后','unify',[dict(preset='SONG_RED',text='r1.3:117|w:年后',size=170,x=960,y=165,t0=0.25,ls=6),
                       dict(preset='EPIC',text='统一天下',size=150,x=960,y=360,t0=1.1,ls=14)],
   S('商鞅死后[一百一十七年]，秦国灭掉六国，统一天下'))
