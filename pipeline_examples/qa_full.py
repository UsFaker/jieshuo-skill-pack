# [示例] 商鞅 v7 整片剪辑管线的参考实现。路径和素材名写死为当时的项目（/workspace/shangyang/...），换项目时照着改；用法和顺序见 pipeline_examples/README.md。
import json,subprocess,sys,os
from PIL import Image,ImageDraw,ImageFont
F='/workspace/shangyang/v7/full'; V=sys.argv[1]; P=json.load(open(F+'/plan_full.json')); S=P['shots']
L={x['id']:x for x in json.load(open(F+'/tts/lines77.json'))}
os.makedirs(F+'/qa/frames',exist_ok=True)
font=ImageFont.truetype('/workspace/shangyang/bigtext/fonts/NotoSansSC[wght].ttf',17)
def fr(t,p): subprocess.run(['ffmpeg','-v','error','-y','-ss',f'{t:.3f}','-i',V,'-frames:v','1','-vf','scale=480:270',p],check=True)
cells=[]
for k,s in enumerate(S):
    t=(s['t0']+s['t1'])/2+0.05; p=f"{F}/qa/frames/s{k:03d}.jpg"; fr(t,p); cells.append((k,s,p))
W,H=480,270+44; per=20
for n in range(0,len(cells),per):
    ch=cells[n:n+per]; img=Image.new('RGB',(W*4,H*5),(20,20,20)); d=ImageDraw.Draw(img)
    for j,(k,s,p) in enumerate(ch):
        x,y=(j%4)*W,(j//4)*H; img.paste(Image.open(p),(x,y+44))
        d.text((x+4,y+2),f"#{k} L{s['line']} {s['asset']} {s['t0']:.1f}s",font=font,fill=(255,220,80))
        d.text((x+4,y+22),L[s['line']]['text'][:26],font=font,fill=(255,255,255))
    img.save(f"{F}/qa/sheet_{n//per+1:02d}.jpg",quality=85)
print(len(cells),'frames')
