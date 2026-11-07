# 构图与提示词

以 [gbro-cover-design](https://github.com/pyang5166/gbro-cover-design) 为底（许可见 `research/retired-from-v7/references/gbro-license.txt`）：一次生成整张图，人物姿势具体、主体元素详细、空间关系清楚、标题和画面层次互相遮挡。
在此基础上固定四件事：人物是 Jacky；微观世界的主角是芽仔手办；标题白字配橙色重点；**版式：上方三分之一放标题（排法与纸蓝风一致：两行左对齐、整块居中，第二行铺满，第一行大一到两号），下方三分之二放人物和场景，两者互不重叠**。Identity 段、Pose 段与 scene-types.md 固定段保持逐字一致，改一处要同步另一处。

## 三种构图

| 构图 | 用在 | Jacky | 芽仔手办 |
|---|---|---|---|
| A 微缩片场 | 搭建、编排、管理团队、导演 AI | 在桌后俯身，双手伸进桌面上的微缩场景摆放或调整 | 场景主角，带着一群小角色推进任务 |
| B 举物展示 | 新工具、方法、成果、对比 | 举着设备 / 大卡片 / 文件朝镜头，近大远小 | 站在举着的物件上或从屏幕里出来，操作关键部分 |
| C 同桌协作 | AI 替你干活、接管、效率 | 坐在桌边，放松地看着芽仔干活 | 在键盘、屏幕、文件堆上忙碌，把结果推出来 |

一期只用一种；选构图看内容关系。

## 提示词模板

```
3:4 vertical cover image.
One moment: [一句事件]

The man (images 1 and 2): [表情], [身体位置], [左手…], [右手…]; half body, close to camera, on the [left/right] side.
Yazai figure (image 3): [在哪个物件上], [动作], [周围的小角色/物件].
Foreground / middle / background: [谁遮挡谁], background is [真实环境].

Title: [第一行] / [白色部分][重点词]（按固定段的标题规则画）.

[固定段]
```

## 固定段（原文照抄，放在提示词末尾）

```
Identity: images 1 and 2 are original photos of the SAME real man; keep his exact face shape, eyes, eyebrows, nose, lips, ears, short spiky black undercut hair, skin tone and age; no glasses. He wears a plain BLACK CREW-NECK SHORT-SLEEVE T-shirt. Natural, warm, approachable expression, not exaggerated. Photorealistic skin, both arms complete, five fingers per hand. Natural upright posture: head, neck, shoulders, chest and hips on one consistent axis and facing the same direction, no twist or mismatch between upper and lower body. If he reaches toward the scene, his whole torso turns toward it and he uses the arm nearer to the scene with the elbow slightly bent, the arm clearly growing out of that shoulder; never a frontal torso with an arm bolted on sideways.
Pose (image 4): a pose reference of the same man; copy only his body angle, arm and hand positions and head direction. Ignore its face, background and any props in it unless stated above; his identity always comes from images 1 and 2.
Yazai (image 3) is a small physical collectible figure (vinyl toy, about the height of a coffee mug unless stated) with exactly this design: big round white helmet, two green sprout leaves on top, featureless glossy black visor with ONE soft reflection on one side, gray round ear covers, red arm bands, white/blue/red chest buttons, short body, short legs, round boots. Only one Yazai; other small characters must look clearly different (e.g. small gray round robots).
Layout: the TOP THIRD of the image is reserved for the title on a clean dark area; the man, Yazai and the whole scene stay in the LOWER TWO-THIRDS and never touch or overlap the title.
Title rules: drawn as part of the image as one left-aligned block, the block centered horizontally, with a clear safe margin from the top edge. Line 2 (usually the longer line) fills the width between equal left and right safe margins; line 1 (shorter) is one size larger, or two sizes larger if it has four characters or fewer, and never wider than the safe width. Huge ultra-bold Chinese sans-serif (like Alibaba PuHuiTi Heavy), white, with the emphasis word in orange #F79300. Tight line gap. Exact characters only, no other text anywhere.
Look: photorealistic cinematic photo, warm dark moody environment, soft key light on face and the miniature world, shallow depth of field; high contrast so the white title reads clearly. No watermark, no logo unless provided.
```

## 示例（学具体程度，不照抄内容）

### A 微缩片场 · “一个人 / 管好一支AI团队”

```
3:4 vertical cover image.
One moment: the man arranges a miniature office on his desk where Yazai leads a small team of AI robots at work.
The man (images 1 and 2): calm focused slight smile, leaning over the desk from behind on the right; his right hand gently places a tiny gray robot figure onto a desk in the miniature office, his left hand rests on the edge of the miniature floor.
Yazai figure (image 3): standing in the center of the miniature office on a tiny podium, one arm raised pointing at a small whiteboard with a three-node flow chart, handing an orange task card to a robot; five small gray round robot figures sit at tiny desks with glowing blue mini monitors.
Foreground: the miniature office on a dark wooden desk, sharp; middle: the man's hands and face; background: blurred dark home studio with warm lamp and bookshelf.
Title (follow the title rules): line 1 "一个人" in white; line 2 "管好一支" in white followed by "AI团队" in orange.
```

### B 举物展示 · “5步搭好 / 你的AI工作流”

```
3:4 vertical cover image.
One moment: the man holds a big card toward the camera; on it, Yazai walks up a five-step path, pushing the third step into place.
The man (images 1 and 2): friendly natural smile at camera, on the right; his left hand holds a large matte card tilted toward the viewer in strong perspective, his right hand supports its lower corner.
Yazai figure (image 3): small, standing on the card, pushing a raised orange block that is step 3 of a staircase of five blocks rising across the card; steps 1-2 orange and lit, steps 4-5 plain gray.
Foreground: the card and Yazai, sharp and large; middle: the man; background: blurred dark desk setup with a monitor glow.
Title (follow the title rules): line 1 "5步搭好" in white; line 2 "你的" in white followed by "AI工作流" in orange.
```

### C 同桌协作 · “告别写报告 / Opus 5.5接管比赛”

```
3:4 vertical cover image.
One moment: the man leans back relaxed with a coffee while Yazai, standing on his laptop keyboard, finishes the report for him and pushes a finished presentation out of the screen.
The man (images 1 and 2): relaxed satisfied smile, sitting at the desk on the right, right hand holding a coffee mug, left arm resting on the desk, watching Yazai.
Yazai figure (image 3): standing on the laptop keyboard in the center, both hands pushing a large finished slide card (simple bar chart, no readable words) out of the laptop screen toward the viewer; a pile of crumpled paper drafts beside the laptop.
Foreground: laptop, Yazai and the slide card, sharp; middle: the man; background: blurred dark office at night with warm lamp.
Title (follow the title rules): line 1 "告别写报告" in white; line 2 "Opus 5.5" in white followed by "接管比赛" in orange.
```
