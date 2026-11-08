# 纸蓝封面：3D 抠图前景怎么写

生图出一张**透明背景的方图**：Jacky 真人半身 + 芽仔 3D 手办 + 立体物件组成的图解场景。之后由脚本加白色贴纸边，贴到纸蓝底上，再合成黑蒙版和标题。
写法借 [gbro-cover-design](https://github.com/pyang5166/gbro-cover-design)（许可见 `research/retired-from-v7/references/gbro-license.txt`）：人物姿势具体、主体元素详细、谁遮挡谁写清楚。

## 画面怎么想：直观、抓眼、一眼看懂

目标：在缩略图里 1 秒看懂这期讲什么，并且想点进来。**先直观，后隐喻。**

1. **先找最直观的那一幕**：能把这期的东西直接演出来，就不绕弯——工具真的在干活、成果真的冒出来、前后真的不一样。观点太抽象、直接画不出来时才用隐喻，而且用大家一看就懂的物件（跑道、钥匙、拼图、开关……）。
2. **一个钩子**：每张找一个让人多看一眼的点，按内容挑一个就够，不要堆：
   - 冲出来：成果或角色从屏幕、窗口里冲出画面；
   - 前后对比：一边灰的、乱的、旧的，一边亮的、整齐的、做好的；
   - 大小反差：手掌上的微缩世界，或者一大堆活被小小的芽仔搞定；
   - 结果看得见：曲线冲高、清单打满勾、作品排成一面墙。
3. **芽仔干最关键的那件事**：由它推、拉、举、搬、点亮、连接，动作幅度大、方向清楚；个头不要小到缩略图里认不出它和它在干嘛。Jacky 托着、端着、指着或展示它所在的物件。
4. **少而清楚**：一个主物件，周围小元素不超过三组；只有关键那一步或结果用橙色，其余灰、白、浅色，视线自然落到重点上。面板类一律画成苹果风圆角窗口（红黄绿三点、3D 倾斜、干净 UI），不画灰色平板。
5. **只写一个瞬间**：先一句事件，再写物件放在 Jacky 手托 / 手指的哪里、芽仔动作、物件上有什么、遮挡关系。Jacky 的身体照动作参考，不在提示词里重新描述他的站姿和手臂。不写坐标，不堆禁词。

## 风格库（给用户出方案时从这里选）

每期结合主题从这里挑 2–3 个给用户，推荐一个；内容需要时也可以提新风格。用户认可的新风格、用户给的新参考，在这里追加一行，并在下方示例补一条通过的提示词。动作参考见 [pose-library.md](pose-library.md)。

| 风格 | 用在 | Jacky（动作参考） | 芽仔 |
|---|---|---|---|
| A 微缩片场 | 管团队、编排、搭建 | 双手悬在微缩场景上方操控，或一手往里放东西（K02） | 在场景中央指挥一群不同造型的小机器人 |
| B 举设备 | AI 替你干活、新工具、成果 | 双手端电脑朝镜头（K04），或单手推手机（K03） | 站在键盘或屏幕边，把结果从屏幕里推出来 |
| C 身后窗口 | 教程、步骤、流程、架构 | 站在前面右侧，侧身指向窗口里的关键一步（K05） | 从窗口下沿走出来，推动关键那一步 |
| D 微观世界（托在掌上） | 一个小系统在运转、看清内部、一件事的全过程 | 单手平托微缩场景，低头看（K01），或另一手指着其中一处（K06） | 在掌上的场景里推进关键一步 |

新构思时可以换的维度：主物件（设备、窗口、模型、机关、书/卷轴、地图、拼图、开关……）、Jacky 的参与方式（托、举、推、指、摆放、观察、拉开、按下）、机位（平视、俯视、近景手部、纵深）、比例（巨人看微缩、等大同框、物件冲向镜头）、芽仔的动作（推、拉、搬、连接、点亮、修理、指挥）。

用户给了 logo、产品形象，作为 image 5、6 上传，写清“image 5 shown on …”，不用通用图标代替，不虚构功能和数字。

**用户给了截图、要放在屏幕或面板上**：不让模型照着截图重画（会画错内容、溢出边框）。屏幕留成纯洋红，生成后用 `scripts/place_screen.py` 把真截图按透视贴进去。在提示词里这样写那块屏幕，截图不上传给模型：

```
The screen of the [laptop / phone / window] is ONE flat solid pure magenta (#FF00FF) area with no reflection, glare, gradient, icon or UI on it; all four corners of the screen stay visible. Yazai may stand in front of a small part of the screen or point at it, but never covers a corner.
```

芽仔和截图的互动写成它站在屏幕前、指着或推着屏幕上某个位置（如“指着屏幕右上部分”），不写截图里的具体文字。

## 固定段（每次原文附在提示词末尾）

```
Identity: images 1 and 2 are original photos of the SAME real man; keep his exact face shape, eyes, eyebrows, nose, lips, ears, short spiky black undercut hair, skin tone and age; no glasses. He wears a plain BLACK CREW-NECK SHORT-SLEEVE T-shirt. Natural, warm, approachable expression, not exaggerated. Photorealistic skin, both arms complete, five fingers per hand.
Body (image 4): image 4 is this man's body for this picture. Keep his body exactly as in image 4 — same pose, same arm and hand positions, same body proportions, shoulder width and head-to-body ratio; do not slim, shrink, stretch or re-pose him. Objects described above go where his hands already hold or point. Ignore image 4's background and any props in it unless stated above; check his face against images 1 and 2.
Yazai (image 3) is a small physical collectible figure (vinyl toy, about the height of a coffee mug unless stated) with exactly this design: big round white helmet, two green sprout leaves on top, featureless glossy black visor with ONE soft reflection on one side, gray round ear covers, red arm bands, white/blue/red chest buttons, short body, short legs, round boots. Only one Yazai; other small characters must look clearly different (e.g. small gray round robots).
Look: photorealistic, cinematic soft studio key light, crisp detail; Yazai and props are real 3D physical objects with real shadows and reflections. Any screen or panel is a premium Apple-style window: rounded corners, a thin light frame, red/yellow/green traffic-light dots at top-left, clean minimal UI with soft depth, slightly tilted in 3D perspective — never a plain gray board. No readable words anywhere.
Framing: SQUARE 1:1 image. The man is framed as in image 4 (cut at the waist by the bottom edge) and as large as possible: from just below the top margin down to the bottom edge, on the right part of the square. The metaphor scene with Yazai sits where his hands hold or point (usually the left and upper part), at least as large as his upper body. Keep a wide EMPTY transparent margin on the left, right and top (at least one tenth of the width): his head, shoulders, hands and every object stay well away from those edges.
Cut-out: fully transparent background (real alpha) around the man and the objects; NO room, NO wall, NO desk surface, NO floor, NO backdrop, NO text, NO title, NO dark gradient. Only the man and the described objects exist.
```

## 示例（2026-11-07 测试通过的提示词，学具体程度，不照抄内容）

### A 微缩片场 · “一个人 / 管好一支AI团队”

```
One moment: the man leans over a miniature 3D office diorama like a giant and gently places a tiny robot into it, while Yazai leads the little AI team at work.
The man (images 1 and 2): calm focused slight smile, leaning in from the right; his right hand places a small gray robot figure at a desk, his left hand rests on the edge of the diorama base.
The diorama: a compact square wooden base about as wide as his shoulders, low glass partitions, five tiny desks with glowing blue mini monitors, five small gray round robot figures working; a small Apple-style whiteboard window with a three-node flow chart.
Yazai figure (image 3): standing on a tiny round podium in the center of the diorama, one arm pointing at the whiteboard, handing an orange task card to a robot.
Overlap: the diorama is in front of his torso; his face and both hands stay visible.
```

### B 举设备 · “告别写报告 / Opus 5.5接管比赛”

```
One moment: the man holds an open laptop toward the viewer; Yazai, standing on the keyboard, pushes a finished glowing presentation card out of the screen while crumpled paper drafts tumble away beside it.
The man (images 1 and 2): warm relaxed smile at camera, on the right, standing upright and facing the camera squarely. His two hands hold the left and right sides of the laptop base at chest height, laptop tilted toward the viewer.
Yazai figure (image 3): standing on the keyboard, both hands pushing a large white Apple-style slide window (simple orange bar chart rising) half out of the screen toward the upper-left; three crumpled paper balls falling from the laptop's left edge.
Overlap: the laptop covers his chest; his face and both hands stay visible.
```

### C 身后窗口 · “5步搭好 / 你的AI工作流”

```
One moment: a large Apple-style app window floats behind him on the left showing a five-step workflow; the man points at it while Yazai steps out of the window and pushes step 3 into place.
The man (images 1 and 2): standing in front on the right, three-quarter turned toward the window, his right index finger (viewer left) pointing at step 3; left arm relaxed; friendly natural smile at camera.
The window: tilted in 3D toward the viewer, about as tall as his upper body, upper-left and center. Inside, a clean UI with exactly FIVE rounded step cards in a rising diagonal joined by a thin line, each with a simple icon (note, gear, chat bubble, chart, flag); cards 1-2 orange with a check mark, card 3 half orange, cards 4-5 light gray.
Yazai figure (image 3): standing on the window's bottom edge as if stepping out of it, both hands pushing card 3 upward into the line.
Overlap: the window is behind him; his pointing hand is in front of its right edge; face fully visible.
```

数量要写死（如“exactly FIVE”），否则模型常少画一两个。
