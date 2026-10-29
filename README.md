# 解说片 skill 整合包（jieshuo-skill-pack）

AI 解说视频制作 skill（`SKILL.md`）加上它用到的工具、脚本和资料，复制到别的机器、别的 Agent 就能用。

> 解压后得到 `jieshuo-skill-pack/`。下面用 `$PACK` 指这个目录。

## 一、目录说明
```
jieshuo-skill-pack/
├─ SKILL.md                      skill 原文（最新版；末尾加了一节「路径 → 包内位置」对照表）
├─ README.md                     本文件
├─ requirements.txt              Python 依赖
├─ tools/
│  ├─ check_env.py               环境自检：python 包、ffmpeg、node、chrome、playwright-core、MIMO_API_KEY
│  ├─ bigtext-kit/               大字/花字套件（对应原机器 /workspace/tools/bigtext-kit）
│  │   ├─ fonts/                 字体（免费商用，授权见 fonts/LICENSES.md）
│  │   ├─ scenes/                8 个示例场景 JSON
│  │   ├─ assets/bg, assets/matte  示例用的背景图和抠像（场景里的路径是 assets/... 相对路径）
│  │   ├─ kit.html/css/js        模板；render.mjs 出静帧/片段；render_ov*.mjs 出透明叠层
│  │   └─ _pw.mjs                自动查找 playwright-core 和 Chrome
│  └─ tts/
│     ├─ mimo_common.py          读 MIMO_API_KEY，发请求
│     ├─ mimo_tts/               预设音色（如「白桦」）：tts_lib.py、gen_vo.py
│     └─ mimo_clone/             声音复刻：clone_lib/syn（合成）、gen_whole/whole_split/build_w/score_c
│         └─ full/               整片版本：gen_sec/split_full/select_full/build_vo_full/align_full
│         └─ refs/               默认复刻音频参考：V1_full.wav
├─ research/script_corpus_text/  写稿资料（只有文本，对应原机器 /workspace/research/script_corpus）
│  ├─ 写稿指南.md  douyin_分析.md  标题主题拆解.md  语料索引.md  逐句分析.md  ref_zhangjuzheng.md
│  ├─ ai_scan.py                 稿子 AI 味扫描      transcribe.py  faster-whisper 转写
│  └─ corpus/ text/ tx/ subs/ dy/   各来源的转写文本和字幕（无音视频）
├─ pipeline_examples/            商鞅片的剪辑管线参考实现（**示例**，路径写死，见其中的 README.md）
└─ examples/                     示例数据：句表 lines77_商鞅v7.json、plan、逐句对画表、稿子
```

## 二、安装
1. 系统程序：
   - ffmpeg（含 libx264、ffprobe）
   - Node.js：大字套件 18+ 即可，HyperFrames 需要 **Node 22**
   - google-chrome（或 chromium；Chrome 不在默认位置就 `export CHROME_PATH=...`）
2. Python（3.10+，建议建虚拟环境）：
   ```bash
   cd $PACK && python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
   首次用 faster-whisper 会自动下载 whisper 模型（medium 约 1.5GB）；rembg 首次会下载抠像模型。
3. 大字套件需要 playwright-core（只要这个包，不用它的浏览器）：
   ```bash
   cd $PACK/tools/bigtext-kit && npm i playwright-core
   ```
   或者 `export PLAYWRIGHT_CORE=/path/to/node_modules/playwright-core`，或 `export LEMO_OPUSCAR_DIR=/path/to/lemo-opuscar`（见下）。
4. 自检：`python3 $PACK/tools/check_env.py`

### 第三方项目（没打进包，需要自行安装）
| 项目 | 地址 | 安装 |
|---|---|---|
| lemo-opuscar（59 种代码渲染风格） | https://github.com/lemomo-ai/lemo-opuscar | `git clone https://github.com/lemomo-ai/lemo-opuscar && cd lemo-opuscar && npm install`，入口先读 README.zh-CN.md、DIRECTOR.md、各风格 STYLE.md；`export LEMO_OPUSCAR_DIR=$(pwd)` |
| HyperFrames（HTML 渲 MP4） | https://github.com/heygen-com/hyperframes | 按其 README 安装，需要 Node 22；运行时 `HYPERFRAMES_SKIP_SKILLS=1 HYPERFRAMES_NO_TELEMETRY=1`，stdin 接 `/dev/null` |

## 三、环境变量
| 变量 | 必填 | 说明 |
|---|---|---|
| `MIMO_API_KEY` | 配音时必填 | MiMo 的 API Key。包里**不含任何密钥**。没设时 `synth()` 会报错并告诉你怎么设 |
| `MIMO_API_KEY_FILE` | 可选 | 不想放环境变量时，指向只含 key 的文本文件 |
| `MIMO_ENDPOINT` | 可选 | 默认 `https://api.xiaomimimo.com/v1/chat/completions` |
| `CLONE_REF` | 可选 | 复刻参考音频路径（脚本里也可用 `--ref`） |
| `WHISPER_MODEL` / `WHISPER_DEVICE` / `WHISPER_THREADS` | 可选 | 默认 `medium` / `cpu` / `8`；有 GPU 设 `WHISPER_DEVICE=cuda` |
| `PLAYWRIGHT_CORE` / `LEMO_OPUSCAR_DIR` / `CHROME_PATH` | 可选 | 大字渲染的 playwright-core 和 Chrome 位置，见 tools/bigtext-kit/README.md |
| 其他服务（如 Gemini 生图/视频） | 视用到的服务 | 同样用环境变量，不要写进脚本 |

## 四、各工具怎么用
下面的命令都在你的**项目工作目录**里跑（不是在包里），`$PACK` 换成包的实际路径。

### 1. 大字套件
```bash
cd $PACK/tools/bigtext-kit
node render.mjs scenes/01_商鞅.json out/01_商鞅 --still 3.0      # 出静帧 out/01_商鞅.jpg
node render.mjs scenes/06_太子犯法.json out/06 --clip           # 出 3.5 秒片段 mp4
```
- 场景 JSON 的 `bg`、`matte` 是相对套件目录的路径（`assets/bg/...`），也可写绝对路径。
- 用在项目里：复制一份套件到项目的 `bigtext/`，背景图和抠像放项目里，不串台。
- 六种预设、竖排/压在人物身后/双行错位/旧词变灰的写法见 `tools/bigtext-kit/README.md` 和 SKILL.md 的 4.8.1 节。
- 透明叠层：`OUTDIR=work/bt node render_ov3.mjs plan.json 0 N`，再用 ffmpeg overlay 叠到视频上（见 `pipeline_examples/final_full.py`）。

### 2. 稿子 AI 味扫描
```bash
python3 $PACK/research/script_corpus_text/ai_scan.py 稿子.md --names 商鞅,秦孝公,公子虔
```
稿子每行一句，支持 `0:12` 时间戳行、编号行，`【大字：…】` 会被忽略。输出：禁用句式、限量词、问句、对观众说话、讲述者口吻、句长节奏、时长估算。
写稿前先读 `research/script_corpus_text/写稿指南.md`、`douyin_分析.md`、`标题主题拆解.md` 和 `corpus/` 里的爆款原文。
`transcribe.py 参考.wav 输出.json [模型] [提示词]`：用 faster-whisper float32 转写参考爆款（16k 单声道 wav）。

### 3. 配音：MiMo 预设音色
```bash
export MIMO_API_KEY=...
python3 $PACK/tools/tts/mimo_tts/gen_vo.py --lines lines.json --style-file style.txt --out takes --takes 3 --voice 白桦
```
- `lines.json` 的格式见 `examples/lines77_商鞅v7.json`：`[{id, sec, text, tts, big}]`，`tts` 是真正送去朗读的文本（多音字、数字写法已处理）。
- Python 里直接用：`from tts_lib import synth; open("a.wav","wb").write(synth("文本", voice="白桦", style="风格"))`。

### 4. 配音：MiMo 声音复刻（用户给了参考录音时）
准备工作：参考录音先量一下有没有人声，只截 15–30 秒有人声的一段，存成 `ref.wav`（24k 单声道，base64 后不超过 10MB）。**包里没有任何个人录音，参考音要自己准备。**
```bash
M=$PACK/tools/tts/mimo_clone
# 4a 短稿（一次生成全稿）：生成 → 切句 → 拼接
python3 $M/gen_whole.py   --lines lines.json --ref ref.wav --n 4 --out whole
python3 $M/whole_split.py --lines lines.json --ref ref.wav --whole whole --out whole/split --res whole_res.json
python3 $M/build_w.py     --lines lines.json --split-dir whole/split --take W_t2 --out vo_raw.wav --timing vo_timing.json --big 4:1.2
# 可选：给切好的单句打分（字错率、语速、韵律）
python3 $M/score_c.py --lines lines.json --out scores.json whole/split/W_t2_L*.wav

# 4b 长稿（按段落生成，每段一次）
F=$M/full
python3 $F/gen_sec.py    --lines lines.json --ref ref.wav --n 4 --secs 1,2,3,4,5,6,7,8 --out whole
python3 $F/split_full.py --lines lines.json --ref ref.wav --secs 1,2,3,4,5,6,7,8 --whole whole --split split --res split_res.json
python3 $F/select_full.py --res split_res.json --target-f0 177 --out selected_full.json     # 每段挑最好的一条
python3 $F/build_vo_full.py --lines lines.json --selected selected_full.json --big 4:1.2,8:1.4
python3 $F/align_full.py    --lines lines.json --wav vo_raw_full.wav --timing vo_timing_full.json   # 字级时间，剪辑用
```
经验（都写在 SKILL.md 第 3 节）：
- 一整段在一次调用里生成，音色最一致，再按静音切句；不要一句一句单独生成。
- `style` 留空比写风格描述更自然。
- 用 Resemblyzer 相似度（≥0.88）、pyin 音高（各句中位数差 15% 以内）、whisper 字错率核对；服务偶尔 429 或坏音频，脚本会自动重试。
- 不加速、不压缩停顿：句间 0.42 秒，关键句后 1.2–1.4 秒（`--big`）。

### 5. 剪辑管线
见 `pipeline_examples/README.md`。这是商鞅片的**参考实现**，要改了路径和素材表才能用在新项目上。

## 五、在新机器上把 SKILL.md 装成 skill
`SKILL.md` 开头是 YAML 头（`name: AI解说视频制作`、`description: ...`），后面是正文。装法取决于 Agent：
- **Grok Bot**：把 `SKILL.md` 发给 bot，说「把这个文件存成名为 AI解说视频制作 的 skill」（bot 会用它的 skill-authoring 流程存好）；之后让 bot 把包解压到它的工作目录，并告诉它 `$PACK` 路径。
- **Claude Code**：放到 `~/.claude/skills/jieshuo-video/SKILL.md`（项目内则 `.claude/skills/jieshuo-video/SKILL.md`）。
- **Cursor**：放到 `~/.cursor/skills/jieshuo-video/SKILL.md`，或项目的 `.cursor/skills/jieshuo-video/SKILL.md`。
- **其他 Agent**：把 `SKILL.md` 全文作为系统提示 / 规则文件加载即可，并在对话里告诉它包的位置。

装好后，SKILL.md 正文里的 `/workspace/...` 路径对不上的话，让 Agent 读 SKILL.md **末尾的对照表**，或者在对话里给它这张表：

| SKILL.md 里的路径 | 包里的位置 |
|---|---|
| `/workspace/tools/bigtext-kit/` | `$PACK/tools/bigtext-kit/` |
| `/workspace/research/script_corpus/` | `$PACK/research/script_corpus_text/`（只有文本） |
| MiMo TTS / 复刻脚本 | `$PACK/tools/tts/mimo_tts/`、`$PACK/tools/tts/mimo_clone/` |
| 剪辑管线脚本 | `$PACK/pipeline_examples/`（示例） |
| `/workspace/tools/lemo-opuscar`、`/workspace/tools/hyperframes` | 不在包里，按上面第三方项目的命令安装 |

## 六、包里没有的东西
- **第三方项目**：lemo-opuscar、HyperFrames（太大，有各自许可证）。
- **音视频文件**：参考爆款的原视频/音频、你的参考录音、视频素材、BGM、音效。
- **密钥**：所有 API Key 已改为环境变量。
- **字体授权**：`tools/bigtext-kit/fonts/LICENSES.md` 里逐个写了来源和授权，商用前自己再核对一遍。
- **写稿资料的来源**：数字是 2026-10-27 从 YouTube 页面抄的，见 `语料索引.md`。
