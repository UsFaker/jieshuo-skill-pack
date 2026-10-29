# [示例] 商鞅 v7 整片剪辑管线的参考实现。路径和素材名写死为当时的项目（/workspace/shangyang/...），换项目时照着改；用法和顺序见 pipeline_examples/README.md。
import numpy as np, subprocess, json, soundfile as sf, sys
R='/workspace/shangyang'; F=R+'/v7/full'; W=F+'/work'; SR=48000
P=json.load(open(F+'/plan_full.json')); S=P['shots']; LS={int(k):v for k,v in P['LS'].items()}; TOT=P['total']; N=int(TOT*SR)
L=json.load(open(F+'/tts/lines77.json')); SEC={x['id']:x['sec'] for x in L}
def dec(f,ss=0,t=None,ch=2,af=None):
    cmd=['ffmpeg','-v','error','-ss',str(ss)]+(['-t',str(t)] if t else [])+['-i',f]+(['-af',af] if af else [])+['-ac',str(ch),'-ar',str(SR),'-f','f32le','-']
    x=np.frombuffer(subprocess.run(cmd,capture_output=True).stdout,np.float32); return x.reshape(-1,ch)
def lufs(x):
    sf.write('/tmp/_lf.wav',x,SR); o=subprocess.run(['ffmpeg','-hide_banner','-i','/tmp/_lf.wav','-af','loudnorm=print_format=json','-f','null','-'],capture_output=True,text=True).stderr
    s=o[o.rfind('{'):]; return float(json.loads(s[:s.find('}')+1])['input_i'])
def fade(x,fi,fo):
    n=len(x); a=np.ones(n,np.float32); i=min(n,int(fi*SR)); o=min(n,int(fo*SR))
    if i: a[:i]=np.linspace(0,1,i)
    if o: a[n-o:]=np.minimum(a[n-o:],np.linspace(1,0,o))
    return x*a[:,None]
vo=dec(F+'/vo_raw_full.wav',ch=1)[:N]; vo=np.pad(vo,((0,N-len(vo)),(0,0))); VOI=lufs(vo); print('VO I',VOI)
# BGM: 按段落换曲, 3s 交叉淡化
secstart={s:min(LS[i] for i in LS if SEC[i]==s) for s in set(SEC.values())}
plan=[(1,'Darkest_Child',6.0),(4,'Prelude_and_Action',2.0),(5,'Heroic_Age',4.0),(6,'Crusade',10.0),(7,'Five_Armies',8.0),(8,'Darkest_Child',150.0)]
bg=np.zeros((N,2),np.float32); XF=3.0
for k,(s,name,ss) in enumerate(plan):
    a=0.0 if k==0 else secstart[s]-XF/2; b=TOT if k==len(plan)-1 else secstart[plan[k+1][0]]+XF/2
    x=dec(f'{R}/audio/bgm/{name}.mp3',ss,b-a+0.5)[:int((b-a)*SR)]
    if len(x)<int((b-a)*SR): x=np.pad(x,((0,int((b-a)*SR)-len(x)),(0,0)))
    x=fade(x,2.5 if k==0 else XF,3.5 if k==len(plan)-1 else XF); x=x*10**((VOI-14-lufs(x))/20)
    i0=int(a*SR); bg[i0:i0+len(x)]+=x[:N-i0]
C_=[]
def shot(line,asset):
    c=[(k,s) for k,s in enumerate(S) if s['line']==line and s['asset']==asset]; assert c,(line,asset); return c[0]
def cue(line,asset,fid,ss,rel,desc,fi=0.1,fo=0.25,af=None,off=0.04,dur=None,pre=0.06):
    k,s=shot(line,asset); at=s['t0']+off; end=S[k+1]['t0']+0.02 if k+1<len(S) else TOT
    end=min(end-pre,TOT) if dur is None else min(at+dur,end-pre)
    C_.append(dict(at=round(at,3),fid=fid,ss=ss,dur=round(end-at,3),rel=rel,desc=f'L{line} {asset} {desc}',fi=fi,fo=min(fo,(end-at)/2),af=af))
RV,CH_,WIND,MARCH,TORCH,FOOT,DRUM,HORSE,HERD,WALLA,WHISP,HALL='557170','235534','402710','480656','497193','352870','274223','368583','547967','634880','438384','675171'
cue(1,'A',RV,30,-20,'河水声',fi=0.8); cue(1,'A2d',CH_,2.0,-17,'木枷绳索轻响')
cue(2,'B1',CH_,9.5,-17,'锁链响',fi=0.05,dur=1.7); cue(2,'B2',WIND,12,-20,'黄昏河风',fi=0.3)
cue(3,'C1',RV,100,-14,'河水拍岸'); cue(3,'C2','764189',2.0,-27,'远处哭喊声(仅此一镜,压低)',fi=0.4,fo=0.5,af='lowpass=f=2500')
cue(4,'D',RV,200,-24,'河水低声',fi=0.5,fo=0.5)
cue(5,'E','840192',0.1,-17,'课本翻页',fi=0.02,fo=0.2,off=0.6,dur=1.3); cue(5,'E2w',WIND,30,-20,'荒村风声',fi=0.2)
cue(5,'V105',MARCH,20,-19,'大军行进脚步')
cue(6,'F',WHISP,3,-35,'低声人语(压成底噪)',fi=0.4,fo=0.8,af='lowpass=f=1200')
cue(7,'G1',WALLA,3,-35,'人群(压成底噪)',af='lowpass=f=1200'); cue(7,'G3',WIND,40,-21,'边地风'); cue(7,'V_N13',TORCH,2,-21,'宴席火把')
cue(8,'V_N18','553297',0.0,-12,'敲门',fi=0.01,fo=0.25,dur=1.6); cue(8,'V_N18',WIND,36,-20,'雪夜风',fi=0.3,fo=0.3,off=0.0)
cue(8,'V003',HERD,2.0,-18,'马群躁动',fi=0.2,fo=0.8)
cue(11,'N11',TORCH,6,-23,'病榻烛火'); cue(12,'N12',TORCH,10,-24,'烛火摇曳')
cue(17,'V011',WIND,10,-20,'荒野风'); cue(17,'V011',HORSE,5,-25,'独骑马蹄',fi=0.3)
cue(20,'V027',TORCH,14,-27,'席地对谈的灯火')
cue(22,'W22',WIND,8,-25,'城门晨风',fi=0.3); cue(24,'F24g','363089',0.5,-16,'金子倒出',fi=0.05); cue(24,'W24b',FOOT,5,-20,'汉子脚步踏尘',fi=0.1); cue(24,'W24c','363089',3.0,-21,'金子入手',fi=0.05,off=0.3,dur=1.2)
cue(27,'N27b',WHISP,8,-35,'暗处低语(底噪)',af='lowpass=f=1200')
cue(28,'V040',DRUM,0.5,-22,'战鼓',fi=0.1)
cue(32,'V055',WALLA,12,-34,'人群(底噪)',af='lowpass=f=1200')
cue(34,'N34',HALL,3,-27,'朝堂空间感')
cue(40,'N40a',WIND,20,-22,'秋叶冬雪的风'); cue(43,'V014',DRUM,3,-22,'战鼓')
cue(46,'V113',FOOT,12,-22,'迁徙脚步'); cue(46,'V065',WIND,25,-22,'山风'); cue(47,'N47',WIND,30,-26,'压抑的风')
cue(49,'N49','382616',5,-15,'火星燃起',fi=0.5,fo=0.2,off=0.1); cue(49,'V106','382616',20,-11,'书架烧成火海',fi=0.15,fo=0.5)
cue(50,'V002',MARCH,6,-22,'秦军行进'); cue(51,'N51a',TORCH,12,-26,'帐中烛火')
cue(52,'N52',HORSE,3,-21,'马蹄',fi=0.2); cue(53,'V_N13',TORCH,6,-21,'宴席火把')
cue(54,'V071',DRUM,1,-22,'战鼓'); cue(54,'V099',WIND,22,-23,'暮色风')
cue(55,'V072',WIND,26,-24,'城头风'); cue(56,'V111',WIND,9,-25,'山顶风')
cue(57,'V048',MARCH,12,-24,'车驾行进'); cue(58,'V_N05',HORSE,14,-24,'车队行进')
cue(61,'V084',HALL,8,-27,'灵堂空间感'); cue(61,'N61','803159',0.0,-16,'登基钟声',fi=0.02,fo=0.8,off=0.1,dur=3.5)
cue(63,'V087',TORCH,16,-25,'追捕火把'); cue(63,'V088',FOOT,15,-20,'狂奔脚步',fi=0.1)
cue(64,'V_N16',WIND,18,-24,'雪夜风'); cue(65,'V090',WIND,26,-18,'风雪',fi=0.3); cue(66,'V121',WIND,33,-22,'风雪')
cue(67,'N67',HALL,12,-27,'魏国朝堂')
cue(68,'V093',HORSE,8,-23,'骑兵',fi=0.2); cue(68,'V095',WIND,5,-24,'灰暗平原风')
cue(69,'V105',MARCH,26,-18,'秦军压来'); cue(70,'V003',HERD,8,-17,'马群躁动',fi=0.2,fo=0.8)
cue(70,'V096',WALLA,18,-35,'人群(底噪)',af='lowpass=f=1200'); cue(71,'V110',WIND,4,-22,'孤塔风')
cue(73,'N73a','330395',0.0,-16,'关门',fi=0.01,off=0.3,dur=1.2); cue(73,'N73b',WIND,15,-28,'死寂的风')
cue(74,'N74a',TORCH,18,-27,'烛光'); cue(74,'N74b','753282',3,-20,'手压竹简',fi=0.1,off=0.4,dur=1.6)
cue(75,'V010',MARCH,10,-20,'秦军前行'); cue(76,'N76',WIND,2,-26,'晨风'); cue(76,'V012','803159',2,-22,'钟声余韵',fi=0.02,fo=1.0,dur=3.0)
cue(77,'C1',RV,60,-20,'河水',fi=0.3); cue(77,'V099',WIND,22,-24,'收尾风',fo=1.5)
cue(78,'J78',WIND,12,-25,'高台风',fi=0.4); cue(79,'J79a',WIND,20,-27,'晨野风'); cue(79,'J79b',HORSE,15,-26,'信使上马',fi=0.2); cue(79,'J79c',MARCH,28,-20,'大军东进',fi=0.1)
cue(80,'V106','382616',40,-13,'焚书火海(回扣)',fi=0.15,fo=0.4); cue(80,'N30',WIND,16,-26,'田野风'); cue(80,'N52',HORSE,20,-23,'奔赴宴席',fi=0.15)
cue(81,'V_N16',WIND,22,-24,'雪夜风'); cue(81,'V090',WIND,30,-20,'风雪',fi=0.3)
cue(82,'J82a','803159',10,-17,'大功钟声',fi=0.02,fo=0.8,off=0.1,dur=2.0)
cue(83,'J83b',WIND,3,-22,'崖边风收尾',fi=0.8,fo=3.5,off=0.0,pre=0.0)
for b in P['bigs']:
    if b['line'] in (1,8,27,70,73,82): C_.append(dict(at=b['t0'],fid='177242',ss=0.0,dur=1.9 if b['line']==8 else 1.4,rel=-14 if b['line']==8 else -15,desc=f"L{b['line']} 大字重击",fi=0.01,fo=1.0,af=None))
sfx=np.zeros((N,2),np.float32)
for c in C_:
    x=dec(f"{R}/audio/sfx/src/fs_{c['fid']}.mp3",c['ss'],c['dur'],af=c.get('af')); assert len(x)>0,c
    if len(x)<int(c['dur']*SR*0.9): rep=int(np.ceil(c['dur']*SR/len(x))); x=np.tile(x,(rep,1))[:int(c['dur']*SR)]
    x=fade(x,c['fi'],c['fo']); I=lufs(x) if len(x)>SR*0.45 else -20
    y=x*10**((VOI+c['rel']-I)/20); pk=20*np.log10(np.abs(y).max()+1e-9)
    if pk>-4: y*=10**((-4-pk)/20)
    a=int(c['at']*SR); y=y[:N-a]; sfx[a:a+len(y)]+=y; c['end']=round(c['at']+len(y)/SR,3)
sf.write(f'{W}/vo.wav',vo,SR); sf.write(f'{W}/bgm.wav',bg,SR); sf.write(f'{W}/sfx.wav',sfx,SR)
json.dump(dict(vo_I=VOI,cues=C_),open(f'{W}/sfx_cues.json','w'),ensure_ascii=False,indent=1); print(len(C_),'cues')
