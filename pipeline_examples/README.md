# 剪辑管线参考实现（示例，不是通用工具）

这些脚本是商鞅 v7 整片（83 句、6 分半）实际用的剪辑管线。**路径、素材名、句号、音效编号都写死成了那个项目**
（`/workspace/shangyang/v7/full/...`、`clips/` 里的素材 id、Freesound 音效编号等），所以它们是用来**照着学、照着改**的，不能直接在别的项目上跑。
想复用，复制一份，把顶部的 `R=`/`F=` 路径、`brain_full.py` 里的逐句画面表、`mix_full.py` 里的音效表换成自己项目的。

`examples/` 里放了这个项目的输入输出样本，改写时对照看：`lines77_商鞅v7.json`（句表格式）、`plan_full_商鞅v7.json`（plan 的结构）、`逐句对画表_商鞅v7.md`、`稿子_v7_商鞅.md`。

## 执行顺序和每个脚本做什么
| 顺序 | 脚本 | 输入 → 输出 | 要点 |
|---|---|---|---|
| 0 | `tools/tts/mimo_clone/full/align_full.py`（通用工具） | 配音 wav + 句表 → `align_full.json` | 每个字的起止时间、静音段 |
| 1 | `brain_full.py` | 手写：每句「脑内画面」→ 素材 id、源起点、转场 | **这是创作环节**：每句口播在观众脑子里是什么画面，就配什么镜头；一句里可切多个镜头（`cuts` 是第几个字切） |
| 2 | `plan_full.py` | 对齐结果 + brain → `plan_full.json` | 镜头起点吸附到字间静音；生成字幕分句、名字条、大字触发点 |
| 3 | `table_full.py` | plan → `逐句对画表.md` | 逐句对画检查表，交付前对一遍 |
| 4 | `build_base_full.py` | plan + 素材 → `work/base_gNN.mp4` | 按组渲染（并行也行），镜头间 xfade；不够长的素材最多放慢到 0.8 倍，调色 + 暗角 |
| 5 | `bigtext_full.py` | 底片 + plan → `work/bigtext.json` | 用 rembg 抠人，自动把大字摆到不挡人脸的位置（避开底部字幕区） |
| 5b | `tools/bigtext-kit/render_ov3.mjs`（`OUTDIR=work/bt node render_ov3.mjs work/bigtext.json 0 N`） | bigtext.json → 透明 PNG 序列 | 出 RGBA 叠层 |
| 6 | `subs_full.py`（依赖 `subs7.py` 里的 ASS 头） | plan → `work/subs.ass` | 烧录字幕：关键词红色，名字条 |
| 7 | `mix_full.py` | 配音 + BGM + 音效 → `vo.wav/bgm.wav/sfx.wav` | 音效逐镜头对表（`cue(句, 素材, 音效编号, 起点, 相对响度, 说明)`），人声类音效压到底噪；BGM 按段落换曲、3 秒交叉 |
| 8 | `final_full.py` | base + 叠层 + 音轨 → 成片 | `python final_full.py out.mp4 28 [extra]`：初版码率约 6Mbps，成品 CRF16 slow |
| 9 | `qa_full.py` / `asr_check.py` | 成片 → 联系表 / 字幕与声音偏移 | 抽每镜一帧排成表；整片重听写后核字幕对时（偏移中位数应在 0.2 秒内） |

## 没有放进包里的东西
- 视频素材（AI 生成的片段）、BGM、音效：体积大，且有各自的授权。商鞅片用了 Kevin MacLeod 的 BGM（CC BY，需要署名）和 Freesound 的 CC0 音效（`mix_full.py` 里的数字是 Freesound 编号）。
- 这些脚本依赖 `ffmpeg`、`opencv-python-headless`、`rembg`、`soundfile`、`numpy`、`pillow`（都在 `requirements.txt` 里）。
