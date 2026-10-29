# [示例] 商鞅 v7 整片剪辑管线的参考实现。路径和素材名写死为当时的项目（/workspace/shangyang/...），换项目时照着改；用法和顺序见 pipeline_examples/README.md。
import sys,subprocess,json,os
R='/workspace/shangyang/v7/full/'; sys.path.insert(0,R+'edit'); from brain_full import path
P=json.load(open(R+'plan_full.json')); S=P['shots']; FPS=24
TRN={'cut':('fade',0.042),'fade':('fade',0.30),'fadeblack':('fadeblack',0.45)}
VAR=['dissolve','smoothleft','circleopen','wipeleft','fade','slideleft','fade']
vi=0
for k,s in enumerate(S):
    n,o=TRN[s['tr']] if k else ('fade',0)
    if s['tr']=='fade' and k:
        n=VAR[vi%len(VAR)]; vi+=1
    s['xn']=n; s['xo']=o
    s['xo']=round(round(o*FPS)/FPS,5)
def cdur(p): return float(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=duration','-of','csv=p=0',p]).split()[0])
# groups: boundary only at 'cut' transitions
groups=[];cur=[]
for k,s in enumerate(S):
    if cur and s['tr']=='cut' and len(cur)>=18: groups.append(cur);cur=[]
    cur.append(k)
groups.append(cur)
json.dump(groups,open(R+'work/groups.json','w'))
def render(gi):
    idx=groups[gi]; sh=[S[k] for k in idx]; f_start=sh[0]['f0']; f_end=S[idx[-1]+1]['f0'] if idx[-1]+1<len(S) else round(P['total']*FPS)
    ins=[];ch=[]
    for j,s in enumerate(sh):
        o=sh[j+1]['xo'] if j<len(sh)-1 else 0
        dur=(s['f1']-s['f0'])/FPS+o+0.12
        p=path(s['asset']); avail=cdur(p)-s['ss']-0.05; spd=min(1.0,max(0.8,avail/dur)) if avail<dur else 1.0
        s['spd']=spd; ins+=['-i',p]
        f=f"[{j}:v:0]trim=start={s['ss']}:duration={dur*spd+0.2},setpts=PTS-STARTPTS"
        if spd<0.999: f+=f",setpts=PTS/{spd},minterpolate=fps={FPS}:mi_mode=blend"
        f+=f",fps={FPS},tpad=stop_mode=clone:stop_duration=2,scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,setsar=1,format=yuv420p"
        if s.get('asset')=='B1' and s['line']==2:
            d=s['dur']; f+=f",geq=lum='lum(X,Y)*(1-0.30*clip((T-0.5)/{d-0.5},0,1))':cb='cb(X,Y)-14*clip((T-0.5)/{d-0.5},0,1)':cr='cr(X,Y)+22*clip((T-0.5)/{d-0.5},0,1)',fps={FPS}"
        f+=f",trim=duration={dur},setpts=PTS-STARTPTS,fps={FPS}[v{j}]"
        ch.append(f)
    cur='v0'
    for j in range(1,len(sh)):
        off=(sh[j]['f0']-f_start)/FPS
        ch.append(f"[{cur}][v{j}]xfade=transition={sh[j]['xn']}:duration={sh[j]['xo']}:offset={off},fps={FPS}[x{j}]"); cur=f'x{j}'
    n=f_end-f_start
    ch.append(f"[{cur}]curves=all='0/0 0.25/0.22 0.75/0.78 1/1',eq=saturation=0.95,vignette=PI/7,trim=end_frame={n},setpts=PTS-STARTPTS[out]")
    out=R+f'work/base_g{gi:02d}.mp4'
    cmd=['ffmpeg','-v','error','-y']+ins+['-filter_complex',';'.join(ch),'-map','[out]','-r',str(FPS),'-frames:v',str(n),'-c:v','libx264','-preset','veryfast','-crf','10','-pix_fmt','yuv420p',out]
    subprocess.run(cmd,check=True); print('group',gi,'frames',n,'shots',len(sh),'slow',[(s['asset'],round(s['spd'],2)) for s in sh if s['spd']<0.999],flush=True)
if __name__=='__main__':
    if sys.argv[1]=='list': print(len(groups)); sys.exit()
    render(int(sys.argv[1]))
