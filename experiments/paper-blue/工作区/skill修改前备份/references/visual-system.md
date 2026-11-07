# Jacky Cover 品牌与排版字段

将本文件用于 Oil Cover 既有 prompt 字段，不另写一套完整 prompt。以下是可被当前明确要求覆盖的品牌默认；选定一种表达后移除互斥指令，不将所有选项同时堆入提示词。标题内容和证据来自本期材料。

## 色彩与材质

- `Mandatory visible background`：全画布 `#E7DBC4` 干净暖纸底，细网格和极轻纸颗粒；柔和蓝色氛围可跟随构图，不画成额外底卡、喷雾团或霓虹。
- `Colour system`：深墨 `#1B1E24` 为主文字，`#0138C4` 用于一个语义重点、副标撕纸条和少量相关点缀，保持主次。不是只能用于微小点缀，也不把所有面板染蓝。
- 面板默认暖白、浅灰或纸色；真实截图、Logo、浏览器控制点及语义状态色保留原色，包括其中原有的蓝色。背景纸纹和蓝光不跨入脸、颈部形成白斑或色块。

## 主副标题

- `Text style` 优先有力度、紧凑、可读的粗笔触中文；质感不能损伤笔画和字形结构。主标讲一个判断，优先两行，按语义断行，不拆词、不拉伸等宽、不强制每行填满画布。深墨色主字加一个蓝色重点。
- 默认不用厚白描边和硬黑投影；用户参考确需描边时保持字间、行间底色可见，不连成白块。字形的自然动势可随参考变化，不强制全部平直或倾斜。
- 克制、清晰的场景可选阿里巴巴普惠体 Bold 级干净粗黑体；不要与粗笔触、厚贴纸风同时叠加。字形类别是视觉目标，不保证生成图使用实际字体文件。
- 副标明显小于主标，补充方法、可信依据、结果或条件；不得为排版静默删改用户文案。
- `Title decoration` 优先蓝色撕纸条配白字，纸边有自然不规则纤维，不画成光滑圆角胶囊或规则锯齿；不默认加黑色垫层。撕纸服务副标，有合适副标才使用；用户参考要求朴素排版时可直接用小号深墨副标。
- 装饰来自本期内容并保持克制；不自动补星星、箭头、下划线或多层标签。主标重点与副标条共同构成同一套强调色关系。

## 构图与安全区

- 在 `Composition` 写本期具体位置：3:4 优先上方主标、其下副标，下半部左侧证据面板、右侧自然上半身人物。用户构图参考优先；这是关系起点，不是固定坐标模板。
- 以顶部约10%留白为起点，结合 Oil Cover 上方标题区建议调整。检查文字、撕纸、描边和阴影的完整外沿均在安全区，不仅检查文字中心。左右留白、主副标间距和副标到面板的距离一起看；不能把标题顶到上沿或把人物硬压低来避让。
- 先保证主标一眼可读，再看证据可辨和人物自然。面板大小要让缩略图能看出主体；不为填满画布强行裁证据或放大人脸。
- 4:3、16:9 重新分配标题与证据的横向空间，保留层级与自然人像比例，不拉伸竖版。数字比例只作设计起点，不作为校验器门禁。
- `Screen crop plan` 与 `Screenshot distillation plan` 按完整面板/提炼重组选定。完整面板保留内部布局和内容，不能强制裁掉一边或仅露80%-95%；只沿已有边缘加适合画面的单层细描边/轻阴影，不再套窗口。提炼模式继续按 Oil Cover 去噪。

## 人物与空间

- `Jacky brand patch`：原照身份与真实年龄感，默认合身但不紧绷的纯黑圆领短袖、自然体态和从容表情。用户明确指定衣着时覆盖默认；换衣保持原照自然头颈肩，不通过比例指令另造身体。
- `Portrait integration guard`：默认右下胸像/上半身落底，不露裤腰或下半身。人物在面板前，肩膀与非关键面板边缘可以自然交叠，并用克制接触阴影衔接；位置、交叠和阴影服从当前构图，不为制造空间感遮挡证据。默认无手接触，必要手势按本轮要求，检查人体结构与前后关系。
- 若用人物描边，只沿外轮廓作细线，不进入脸和脖子，不形成粗白光环或抠图残边。人物自然感来自原照结构、连续肤色和一致光照，不来自增加轮廓装饰。
- 在 `Avoid` 写本期真正相关的禁止项：皮肤白斑、标题描边粘连、面板重复容器、证据遮挡或身份漂移等。不添加与用户指定完整截图或姿态互斥的旧句。不得凭空往截图添加人物、脸或头像；如用户指定完整原图已有此类内容，按指定用途保留，不因通用无人物规则擅删。

## 可调整的英文基底

下面只示范字段表达；按本期风格、手势和编辑范围改写。字体、装饰和几何的确定状态各写一处，不逐字强制匹配。若用户选克制字形或没有副标，替换相应句子，不能同时保留粗笔触与撕纸要求。

```text
Text style: use compact, bold, expressive Chinese brush lettering with fully legible character strokes; break the main title by meaning, preferably into two lines, without stretching characters to equal line widths. Use deep ink with one semantic emphasis in brand blue. No thick white outline or hard black drop shadow by default. Keep the exact subtitle clearly smaller.
Title decoration: set the subtitle in white on a brand-blue torn-paper strip with irregular fibrous edges, without a black backing layer. Keep the strip within the safe area and separated from the main title.
Portrait integration guard: preserve Jacky's identity and natural head-neck-shoulder anatomy from the original photos. Keep any already accepted head direction. Follow the current Composition for crop and placement, protect all primary evidence, and keep skin tone and lighting continuous. Any keyline stays outside the portrait silhouette and never crosses the face or neck.
Jacky brand patch: use warm paper #E7DBC4, deep ink #1B1E24 and brand blue #0138C4 for title emphasis, the selected subtitle treatment and restrained accents. Preserve the original colours of screenshot evidence and logos. Dress Jacky in a natural-fitting plain black crew-neck short-sleeve T-shirt unless the user specifies otherwise.
```

原图逐字验主副标、看头颈肩和皮肤，再用等比例缩略图检查阅读顺序、安全区及证据可辨性。参考构图被采用不代表整张图已获用户认可；本轮编辑还须对照未要求改变的部分。
