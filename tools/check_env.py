#!/usr/bin/env python3
"""检查整合包需要的环境：python.包、ffmpeg、node、chrome、playwright-core、MIMO_API_KEY。用法：python3 tools/check_env.py"""
import importlib, os, shutil, subprocess, sys
ok = True
def row(name, good, hint=""):
    global ok; ok &= bool(good); print(("[ok]  " if good else "[缺]  ") + name + ("" if good else "  → " + hint))
for m, pipname in [("numpy","numpy"),("soundfile","soundfile"),("librosa","librosa"),("pypinyin","pypinyin"),("faster_whisper","faster-whisper"),
                   ("resemblyzer","resemblyzer"),("parselmouth","praat-parselmouth"),("PIL","pillow"),("cv2","opencv-python-headless"),("rembg","rembg[cpu]")]:
    try: importlib.import_module(m); row("python: " + m, True)
    except Exception: row("python: " + m, False, f"pip install {pipname}")
for b, hint in [("ffmpeg","安装 ffmpeg（需 libx264）"),("ffprobe","随 ffmpeg 一起装")]:
    row(b, shutil.which(b), hint)
node = shutil.which("node"); v = subprocess.run([node, "-v"], capture_output=True, text=True).stdout.strip() if node else ""
row(f"node {v}", node, "安装 Node.js 22（HyperFrames 需要 22；大字套件 18+ 即可）")
chrome = os.environ.get("CHROME_PATH") or next((shutil.which(c) for c in ["google-chrome","google-chrome-stable","chromium","chromium-browser"] if shutil.which(c)), None)
row("chrome: " + str(chrome), chrome, "安装 google-chrome 或设置 CHROME_PATH")
kit = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bigtext-kit")
r = subprocess.run([node or "node", "-e", "import('./_pw.mjs').then(m=>m.loadChromium()).then(()=>process.exit(0))"], cwd=kit, capture_output=True, text=True) if node else None
row("playwright-core", r is not None and r.returncode == 0, "cd tools/bigtext-kit && npm i playwright-core（或设 PLAYWRIGHT_CORE / LEMO_OPUSCAR_DIR）")
print(("[ok]  " if os.environ.get("MIMO_API_KEY") or os.environ.get("MIMO_API_KEY_FILE") else "[提示] ") + "MIMO_API_KEY " + ("已设置" if os.environ.get("MIMO_API_KEY") or os.environ.get("MIMO_API_KEY_FILE") else "未设置（只在配音时需要：export MIMO_API_KEY=...）"))
sys.exit(0 if ok else 1)
