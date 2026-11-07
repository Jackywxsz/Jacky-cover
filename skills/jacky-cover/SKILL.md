---
name: jacky-cover
description: 制作 Jacky 真人与芽仔同框的 3:4 视频封面。默认纸蓝风：生图出透明 3D 抠图（Jacky 半身 + 芽仔手办推进的隐喻场景），加白色贴纸边贴到固定纸蓝底上，下方渐变黑蒙版 + 普惠体白橙两行标题 + 霞鹜文楷手写小字。可选暗调整图风（gbro 式一次生成整张）。用于 Jacky Cover、JK Cover、Jacky 封面。
---

# Jacky Cover

默认**纸蓝风**。用户明确要深色/暗调整图时才用[暗调整图风](references/composition.md)：同样定隐喻，照 composition.md 写提示词，用第 3 节命令生成一张 3:4 整图（标题由模型画进图），不加白边、不合成，直接按第 5 节检查（排版项改为“标题逐字正确、在上方三分之一”）。

**运行约定**：所有命令都在 `skills/jacky-cover/` 目录下运行；`<项目>` = `../../experiments/covers/<日期>-<主题>/`（先 `mkdir -p`）。生图依赖本机已安装并登录的 `codex` CLI。

```
选题 → 给 2–3 个风格方案并推荐一个 → 用户选定 → 写提示词 → 生成一张透明方图 → 加白边 → 合成(无小字) → 定小字位置 → 合成成品 → 检查
```

固定不变的：纸蓝底、黑蒙版、标题字体与排法、Jacky 身份、芽仔造型。每期变化的：隐喻场景、动作、小字位置。模板、标题、蒙版的数值唯一来源是 `references/interaction-profile.json`，本文不重复写数字。

## 1. 选题与风格方案（先和用户对好再生图）

读文案和素材，结合主题给用户 2–3 个风格方案，推荐其中一个并说理由，**用户选定后才写提示词、生图**。每个方案写清：

`[风格] Jacky 在做什么（动作参考 Kxx）→ 芽仔在推进什么 → 观众看懂什么`

- 风格从 [scene-types.md](references/scene-types.md) 的风格库里选（如微观世界、身后窗口、举设备……），内容需要时也可以提新的。用不用和前几期一样的风格由用户定；[cover-log.md](references/cover-log.md) 只作记录，方案里可以顺带提一句最近用过什么。
- 动作从 [pose-library.md](references/pose-library.md) 选最贴近的一张，写进方案。
- 芽仔默认是微观世界的主角；Jacky 和它所在的物件有真实的手部接触。
- 标题两行逐字保留：第一行短、第二行长，橙色重点词在第二行（用户另有指定按用户的）。小字是一句补充，如“Bot军团配置全公开”；用户没给就自己写一句贴合内容的。
- 用户已指定风格和动作时直接照用户的，不再出方案。

## 2. 写提示词

照 scene-types.md：一句事件 → Jacky 表情、站姿、两只手 → 芽仔在哪做什么 → 主物件上有什么（数量写死）→ 遮挡关系 → 末尾原文附固定段。存为 `<项目>/prompt-v1.txt`。

## 3. 生成与加白边

参考图顺序：`assets/jacky-reference-front.jpg`、`assets/jacky-reference-side.jpg`、`../jacky-illustration/assets/ip/yazai-paper-blue-anchor-v1.png`、选定的动作参考 `assets/poses/Kxx.png`，可选用户素材（最多两张）。每轮只生成一张（Codex 内置 image_gen，约 10 分钟，要后台运行或把命令超时设到 600000ms，否则会被默认 2 分钟超时打断）：

```sh
scripts/codex_imagegen.sh <项目>/foreground-v1.png <项目>/prompt-v1.txt assets/jacky-reference-front.jpg assets/jacky-reference-side.jpg ../jacky-illustration/assets/ip/yazai-paper-blue-anchor-v1.png assets/poses/K01.png
scripts/sticker_edge.py <项目>/foreground-v1.png <项目>/foreground-v1-edge.png
```

`sticker_edge.py` 若报 `CROPPED`，说明人或物件被画面边缘切了，这张作废，按第 5 节重新生成。

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

先看草稿的半身切口：报告 `scene.body_cut_detected` 为 true、且草稿里切口露在外面没被物件挡住，就在 text.json 加 `"hide_cut_behind_title": true`，换个文件名重新出草稿再量空白（这个开关会移动场景位置）。

再看草稿和空白带，按构图选小字位置：

- 场景偏下或俯视：放左上空白。
- 场景偏上（如身后窗口），场景和标题之间有空：放在中间，读起来像标题的引子。
- 两处都行时选离隐喻核心更近、更平衡的那处；放不下就把字号调小（不低于 profile 的 note.min_size）或缩短文字，仍不行就不放。

把 `"note":{"text":"…","xy":["title_left",y],"size":52}` 加进 text.json，再合成成品（输出、报告、图层目录都不能已存在）：

```sh
python3 scripts/compose_interaction_cover.py --scene <项目>/foreground-v1-edge.png --text <项目>/text.json --output <项目>/cover-v1.png --report <项目>/cover-v1.json --layers-dir <项目>/layers-v1
```

标题由脚本自动排：两行左对齐、整块水平居中；第二行铺满左右安全宽度，第一行大一号，4 个字以内大两号；底部边距是左右边距的两倍。小字与标题左边对齐，颜色按背景亮度自动选。只改文字时只重跑合成，不重新生图。

## 5. 检查与交付

看成品原图和 270×360 缩略图，在 `<项目>/check.md` 逐条写：

- **本人**：脸型、五官、发型对照原照；黑圆领短袖；表情自然亲和。
- **身体与手臂**：头、胸、肩、胯朝向一致，没有上下身扭开；伸出的手臂看得出是从对应肩膀自然连出来的，不是正面躯干侧面硬接一条胳膊；手指数对，和物件真实接触。被物件自然遮挡一部分没问题。
- **芽仔**：双叶、黑色无五官面罩加单侧反光、红臂带、胸钮、大头短身圆靴；3D 手办；全图只有一个。
- **一眼看懂**：遮住标题能说出芽仔在推进什么；主场景在上 2/3，不沉进黑区；数量与文案一致。
- **半身切口**：切口不能裸露成一条硬线。优先在构思时让主物件挡在他身前；挡不住就用第 4 节的 `hide_cut_behind_title`。
- **排版**：白边完整、没有被切；标题逐字正确；小字不压画面、与标题左对齐。

不合格就针对问题改提示词、用同一组原照重新生成一张（输出名递增 v2、v3）；**禁止把生成的图再上传去修改**。只把自检通过的那张交给用户，不给多个版本让用户挑。同一选题最多 3 轮，仍不行就停下说明缺口。交付成品路径和 check.md；自检和用户验收分开写，用户认可前不当范例。

交付后在 `references/cover-log.md` 末尾追加一行本期记录。用户认可的新风格，追加到 scene-types.md 的风格库，并附上通过的提示词。

## 素材规则

- 人物身份只来自 front / side 原照。`assets/poses/` 的动作参考只管姿势，不作身份来源；其他生成图（封面、前景）都不能作为参考输入。
- 固定模板（纸蓝底、蒙版）要换，必须出新版本资产，不改旧 PNG。
- 验证记录：仓库根目录下 `experiments/cover-paper3d/`（流程定稿测试）和 `experiments/covers/`（按流程实跑的每一期）。

维护：`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`。
