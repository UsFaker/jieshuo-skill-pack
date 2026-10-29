# [示例] 商鞅 v7 整片剪辑管线的参考实现。路径和素材名写死为当时的项目（/workspace/shangyang/...），换项目时照着改；用法和顺序见 pipeline_examples/README.md。
import sys,json,subprocess
out=sys.argv[1]; crf=sys.argv[2]; extra=sys.argv[3:]
W='/workspace/shangyang/v7/full/work'; B=json.load(open(f'{W}/bigtext.json'))
inp=['-i',f'{W}/work_base.mp4']
for k,b in enumerate(B): inp+=['-framerate','30','-i',f"{W}/bt/{k:02d}/%04d.png"]
inp+=['-i',f'{W}/master.wav']
fc=[];cur='0:v'
for k,b in enumerate(B):
    fc.append(f"[{k+1}:v]format=rgba,setpts=PTS-STARTPTS+{b['t0']}/TB[o{k}]")
    fc.append(f"[{cur}][o{k}]overlay=eof_action=pass:enable='between(t,{b['t0']},{b['t0']+b['dur']})'[t{k}]"); cur=f't{k}'
fc.append(f"[{cur}]subtitles={W}/subs.ass:fontsdir=/workspace/shangyang/bigtext/fonts[outv]")
cmd=['ffmpeg','-v','error','-stats','-y']+inp+['-filter_complex',';'.join(fc),'-map','[outv]','-map',f'{len(B)+1}:a','-c:v','libx264','-preset','slow','-crf',crf]+extra+['-profile:v','high','-pix_fmt','yuv420p','-r','24','-g','48','-movflags','+faststart','-c:a','aac','-b:a','256k','-ar','48000','-shortest',out]
subprocess.run(cmd,check=True)
