# 大字 kit（照参考爆款《张居正》的花字体系做，商鞅片全片在用）
- `kit.html`、`kit.css`、`kit.js`：模板。场景用 JSON 描述，每帧调用 `BT.seek(t)`，输出结果是确定的。
- `render.mjs`：
  - 出静帧：`node render.mjs scenes/X.json out/X --still 3.0`
  - 出片段：`node render.mjs scenes/X.json out/X --clip [--fps 30]`
  - 用的是系统 Chrome 和 playwright-core，查找方式见下面「运行环境」。
- `make_scenes.py`：重新生成 8 个样例场景（`scenes/*.json`）。参考爆款对照图 `对比.jpg`、`对比2.jpg` 已做好，对比图脚本需要参考帧，没打进包。
- `render_ov.mjs` / `render_ov3.mjs`：出透明叠层 PNG 序列（`node render_ov3.mjs plan.json 0 N`，环境变量 `OUTDIR` 指定输出目录），再用 ffmpeg overlay 叠到视频上。
- `assets/matte/`：用 rembg 抠出的前景人物或物体，用于「字压在人物身后」。木杆的遮罩是手工做的。
- `assets/bg/`：占位背景，AI 生成，16:9，1920×1080。

## 预设（preset）
| preset | 对应参考 | 字体 | 默认颜色 | 默认入场 |
|---|---|---|---|---|
| SONG_RED | A 宋体重磅红 | 思源宋体 Heavy | 红 | blurSettle（模糊落定，0.32s） |
| SONG_WHITE | B 宋体白 | 思源宋体 Heavy | 白 | blurSettle |
| BRUSH | C 毛笔红白相间 | 庞门正道粗书体 | 白（逐字可指定红） | brushSlam（砸入回弹 + 白光扫过） |
| HEI / HEI_SANS | D 粗黑白/黄 | 优设标题黑 / 思源黑 Heavy | 白（可 y: 黄） | zoomPunch（冲撞放大 + 背景震动） |
| EPIC | G 黄油体红厚影 | 站酷庆科黄油体 | 红 | blurSettle |
| BANGSHU | H 榜书白 | 仓耳周珂正大榜书 | 白 | inkDrop（逐字落下 + 拖影） |

几种用法不另设预设，在场景里用参数实现：
- **E 竖排侧栏**：`vertical:true, stagger:0.09`，任意预设都能加。
- **F 人物身后巨字**：`behind:true` 加 `matte`。
- **双行错位**：两条 item，第二条 t0 晚 0.5–0.8 秒，并错开 x/y。
- **旧词变灰**：`dimAt`。

文字写法：`"w:商|r:鞅"`、`"r1.3:117|w:年后"`。冒号前的字母是颜色（w 白 / r 红 / y 黄），后面的数字是相对字号。

自动安全区：字会被限制在左右各 96px、上 60px、下 170px（字幕区）以内，不会被挤出画面。

字幕：底部 50px 粗宋白字，带黑描边。用 `[关键词]` 标红。


## 运行环境（render*.mjs）
- 路径都是**相对套件目录**的：场景 JSON 里 `"bg": "assets/bg/portrait.jpg"`、`"matte": "assets/matte/gate_pole.png"`；也可以写绝对路径。
- Chrome：默认找 `/usr/bin/google-chrome`、`google-chrome-stable`、`chromium` 等；找不到就 `export CHROME_PATH=/path/to/chrome`。
- playwright-core（只要 `playwright-core` 这个包，不用下载它自带的浏览器），按顺序找：
  1. 环境变量 `PLAYWRIGHT_CORE`（指向 `node_modules/playwright-core` 目录）
  2. 环境变量 `LEMO_OPUSCAR_DIR`（lemo-opuscar 项目目录，用它的 `node_modules`）
  3. 套件目录或当前目录向上的 `node_modules/playwright-core`
  4. `npm root -g` 全局目录
  最省事：`cd tools/bigtext-kit && npm i playwright-core`。
- 出一张静帧试试：`node render.mjs scenes/01_商鞅.json out/01_商鞅 --still 3.0` → `out/01_商鞅.jpg`。
- 字体都在 `fonts/`，授权见 `fonts/LICENSES.md`；`kit.css` 用相对路径引用，整个目录不要拆开。
