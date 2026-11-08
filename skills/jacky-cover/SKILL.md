---
name: jacky-cover
description: 制作 Jacky 真人与芽仔同框的 3:4 视频封面。默认纸蓝风：生图出透明 3D 抠图（Jacky 半身 + 芽仔手办演出主题的图解场景），加白色贴纸边贴到固定纸蓝底上，下方渐变黑蒙版 + 普惠体白橙两行标题 + 霞鹜文楷手写小字。可选暗调整图风（gbro 式一次生成整张）。用于 Jacky Cover、JK Cover、Jacky 封面。
---

# Jacky Cover

默认**纸蓝风**。用户明确要深色/暗调整图时才用[暗调整图风](references/composition.md)：同样先定画面，照 composition.md 写提示词，按第 3 节的参考图要求生成一张 3:4 整图（标题由模型画进图），不加白边、不合成，直接按第 5 节检查（排版项改为“标题逐字正确、在上方三分之一”）。

**运行约定**：所有命令都在 `skills/jacky-cover/` 目录下运行；`<项目>` = `../../experiments/covers/<日期>-<主题>/`（先 `mkdir -p`）。生图工具不限（见第 3 节的要求），合成只依赖 Python + Pillow。

```
选题 → 给 2–3 个风格方案并推荐一个 → 用户选定 → 写提示词 → 生成一张透明方图 → 加白边 → 合成(无小字) → 定小字位置 → 合成成品 → 检查
```

固定不变的：纸蓝底、黑蒙版、标题字体与排法、Jacky 身份、芽仔造型。每期变化的：图解场景、动作、小字位置。模板、标题、蒙版的数值唯一来源是 `references/interaction-profile.json`，本文不重复写数字。

## 1. 选题与风格方案（先和用户对好再生图）

读文案和素材，结合主题给用户 2–3 个风格方案，推荐其中一个并说理由，**用户选定后才写提示词、生图**。每个方案写清：

`[风格] 一句话画面（直观演出来，还是隐喻）→ 钩子 → Jacky 动作 Kxx → 观众 1 秒看懂什么`

画面怎么想见 scene-types.md 的“画面怎么想”：先直观、后隐喻，每张一个钩子，芽仔干最关键的那件事。

- 风格从 [scene-types.md](references/scene-types.md) 的风格库里选（如微观世界、身后窗口、举设备……），内容需要时也可以提新的。用不用和前几期一样的风格由用户定；[cover-log.md](references/cover-log.md) 只作记录，方案里可以顺带提一句最近用过什么。
- 动作只从 [pose-library.md](references/pose-library.md) 选，人物身体照这张来，不重新设计；场景按这张动作的手势来放。
- 标题两行逐字保留：第一行短、第二行长，橙色重点词在第二行（用户另有指定按用户的）。小字是一句补充，如“Bot军团配置全公开”；用户没给就自己写一句贴合内容的。
- 用户已指定风格和动作时直接照用户的，不再出方案。

## 2. 写提示词

照 scene-types.md：一句事件 → Jacky 表情、站姿、两只手 → 芽仔在哪做什么 → 主物件上有什么（数量写死）→ 遮挡关系 → 末尾原文附固定段。存为 `<项目>/prompt-v1.txt`。

## 3. 生成与加白边

用你手上任何能“一次上传多张参考图”的生图工具，每轮只生成一张。不管用什么工具，这几条都不能省：

1. **四张参考图一次全部上传，顺序固定**（就是提示词里的 image 1–4）：
   1. `assets/jacky-reference-front.jpg`（正脸原照）
   2. `assets/jacky-reference-side.jpg`（侧脸原照）
   3. `../jacky-illustration/assets/ip/yazai-paper-blue-anchor-v1.png`（芽仔）
   4. `assets/poses/Kxx.png`（第 1 步选定的动作模板）

   用户素材（logo、截图、参考图）接在后面作 image 5、6。工具一次传不了这四张，或者只能传一张，就**停下告诉用户**，不要少传几张硬生成，也不要用文字描述代替参考图。
2. **提示词就是 `<项目>/prompt-v1.txt` 全文**，包括末尾的固定段，不改写、不删减。
3. **背景**：工具能出透明图就直接出透明 PNG。只能出纯色底时，把固定段 `Cut-out` 那行换成 `Background: one flat plain light-gray (#D9D9D9) background, no shadow on it, no gradient, no floor; nothing else in the picture.`，生成后用手上的抠图工具去掉背景，存成带透明通道的 PNG。抠完放大看头发、手指、芽仔叶子和白色物件的边缘，没被抠掉、没有灰边才算过。
4. 生成需要的时间看工具，可能长达 10 分钟，命令或任务的超时要留够。

存为 `<项目>/foreground-v1.png`，再加白边：

```sh
scripts/sticker_edge.py <项目>/foreground-v1.png <项目>/foreground-v1-edge.png
```

本机装了 `codex` CLI 时，可以用现成脚本一步生成（参数顺序就是上面的参考图顺序）：`scripts/codex_imagegen.sh <项目>/foreground-v1.png <项目>/prompt-v1.txt <image1> <image2> <image3> <image4>`。

`sticker_edge.py` 报 `CROPPED` 时先看切到的是什么：只是人物的肩或手臂被左/右边切到（动作模板本身是半身近景，常见），就加 `--bleed right`（或 `left`）重跑，合成时那一侧会贴住封面边缘，读起来是身体延伸出画；切到的是头、手或物件，这张作废，按第 5 节重新生成。

## 4. 合成

写 `<项目>/text.json`：

```json
{"lines":[{"text":"一个人"},{"text":"管好一支AI团队","emphasis":"AI团队"}]}
```

先不带小字合成，再量空白：

```sh
python3 scripts/compose_interaction_cover.py --scene <项目>/foreground-v1-edge.png --text <项目>/text.json --output <项目>/draft-v1.png --report <项目>/draft-v1.json --layers-dir <项目>/draft-layers-v1
python3 scripts/note_space.py <项目>/draft-v1.json <项目>/draft-layers-v1 "Bot军团配置全公开" 52
```

半身切口由脚本自动处理：检测到切口（报告 `scene.body_cut_detected`）就把场景下移，让身体沉进标题后面的黑色里，不会在纸底上淡出成灰蒙蒙的一片。只有切口已被主物件完全挡住、不想移动场景时，才在 text.json 写 `"hide_cut_behind_title": false`。

再看草稿和空白带，按构图选小字位置：

- 场景偏下或俯视：放左侧、大约上 1/3 高度（y 约 0.22–0.30），挨着人物头部左边的空白，不贴顶边。这一带放不下就先缩小字号再量，不要退到顶边。
- 场景偏上（如身后窗口），场景和标题之间有空：放在中间，读起来像标题的引子。
- 两处都行时选离画面重点更近、更平衡的那处；放不下就把字号调小（不低于 profile 的 note.min_size）或缩短文字，仍不行就不放。

把 `"note":{"text":"…","xy":["title_left",y],"size":52}` 加进 text.json，再合成成品（输出、报告、图层目录都不能已存在）：

```sh
python3 scripts/compose_interaction_cover.py --scene <项目>/foreground-v1-edge.png --text <项目>/text.json --output <项目>/cover-v1.png --report <项目>/cover-v1.json --layers-dir <项目>/layers-v1
```

标题由脚本自动排：两行左对齐、整块水平居中；第二行铺满左右安全宽度，第一行大一号，4 个字以内大两号；底部边距是左右边距的两倍。小字与标题左边对齐，颜色按背景亮度自动选。只改文字时只重跑合成，不重新生图。

## 5. 检查与交付

看成品原图和 270×360 缩略图，在 `<项目>/check.md` 逐条写：

- **本人**：把生成图和 front 原照、动作模板放在一起看（拼成一张对照图），脸型、五官、发型要认得出是他本人；脸和脖子之间不能有接缝、色差或方框；黑圆领短袖；表情自然亲和。认不出是本人就整张重新生成。
- **身体**：和选定的动作模板并排对照——姿势、肩宽、头身比、取景没被改（不变小、不变瘦、不拉长）；手指数对，和物件真实接触。被物件自然遮挡一部分没问题。
- **芽仔**：双叶、黑色无五官面罩加单侧反光、红臂带、胸钮、大头短身圆靴；3D 手办；全图只有一个。画面里没有芽仔，说明参考图或固定段没传全，查清楚再重新生成。
- **无文字**：画面里（窗口、屏幕、卡片上）没有可读的字，字只来自合成脚本排的标题和小字。
- **一眼看懂、抓眼**：看 270×360 缩略图，遮住标题也能说出这期讲什么、芽仔在干嘛；有一个让人多看一眼的钩子；橙色只落在重点上；数量与文案一致。
- **构图占满**：场景从上方安全区一直延伸到标题后的黑色里——主场景在上 2/3，上面不空一大片，身体下端沉进黑色、不在浅色纸底上淡出成灰雾。上面空太多（报告 `scene.top_gap_px` 明显大于 0）通常是人被画小了、场景铺得太宽，下一轮重新生成，不靠挪位置补。
- **排版**：白边完整、没有被切；标题逐字正确；小字不压画面、与标题左对齐。

不合格就针对问题改提示词、用同一组原照重新生成一张（输出名递增 v2、v3）；**禁止把生成的图再上传去修改**。只把自检通过的那张交给用户，不给多个版本让用户挑。同一选题最多 3 轮，仍不行就停下说明缺口。交付成品路径和 check.md；自检和用户验收分开写，用户认可前不当范例。

交付后在 `references/cover-log.md` 末尾追加一行本期记录。用户认可的新风格，追加到 scene-types.md 的风格库，并附上通过的提示词。

## 素材规则

- 人物的脸以 front / side 原照为准；身体（姿势、比例、取景）照 `assets/poses/` 里选定的那张，不用库外的动作。其他生成图（封面、前景）都不能作为参考输入。
- 脸不像时只能整张重新生成：不把原照的脸贴到生成图上，不换脸，不局部重绘或修脸。
- 固定模板（纸蓝底、蒙版）要换，必须出新版本资产，不改旧 PNG。
- 验证记录：仓库根目录下 `experiments/cover-paper3d/`（流程定稿测试）和 `experiments/covers/`（按流程实跑的每一期）。

维护：`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`。
