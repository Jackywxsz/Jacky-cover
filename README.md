# Jacky Cover

做 Jacky 视频封面的 Skill：Jacky 真人 + 芽仔 3D 手办组成一个隐喻场景，透明抠图加白边贴到纸蓝底上，下方渐变黑蒙版 + 普惠体两行标题 + 霞鹜文楷小字，输出 3:4 竖图。

- **当前实现**：`skills/jacky-cover/`（`main` 分支即当前版本，2026-11-07 定稿）。
- **入口**：[skills/jacky-cover/SKILL.md](skills/jacky-cover/SKILL.md)，只从这里加载规则。
- **仓库是私有的**：含 Jacky 正脸原照和以他为原型生成的动作图，不改公开、不发 release；邀请外部协作者需本人同意。

## 一期封面怎么做

```
选题 → 给 2–3 个风格方案并推荐一个 → 用户选定 → 写提示词 → 生成一张透明方图 → 加白边 → 合成草稿 → 定小字位置 → 合成成品 → 自检 → 用户验收
```

1. **先对方案**：结合主题从风格库（微观世界、身后窗口、举设备、微缩片场……，见 `references/scene-types.md`）给 2–3 个方案，每个写清 Jacky 的动作（动作库编号）、芽仔在推进什么、观众看懂什么，并推荐一个。用户选定后才生图。
2. **生图**：Codex 内置 image_gen，一次一张，约 10 分钟。参考图依次是 front / side 原照、芽仔锚点、选定的动作参考 `assets/poses/Kxx.png`（只管姿势，身份以原照为准）。
3. **合成**：`sticker_edge.py` 加白边并检查是否被裁切 → `compose_interaction_cover.py` 合成纸蓝底、蒙版、标题 → `note_space.py` 量小字空白。场景偏下时，小字放在左侧大约上 1/3 高度。
4. **检查**：每期在 `experiments/covers/<日期>-<主题>/check.md` 里分开写自检和用户验收；用户认可前不当范例。

完整步骤和命令都在 SKILL.md；所有命令在 `skills/jacky-cover/` 目录下运行。

## 目录

| 路径 | 内容 |
|---|---|
| `skills/jacky-cover/` | 当前 Skill：`SKILL.md`、脚本、测试、素材 |
| `skills/jacky-cover/assets/` | front / side 原照、纸蓝底与蒙版模板、字体、K01–K08 动作参考 |
| `skills/jacky-cover/references/` | `scene-types.md`（风格库 + 提示词固定段）、`pose-library.md`（动作库说明）、`composition.md`（可选暗调整图风）、`interaction-profile.json`（版式数值唯一来源）、`cover-log.md`（每期记录） |
| `skills/jacky-illustration/` | 依赖：芽仔锚点图等，不覆盖 Cover 规则 |
| `experiments/covers/` | 按当前流程实跑的每一期 |
| `experiments/cover-paper3d/` | 定稿流程的验证测试 |
| `experiments/` 其他、`research/`、`archive/` | 历史方案和旧 Skill 快照，只作证据，不加载、不执行 |
| `tools/` | `verify_assets.py` 校验素材哈希 |
| `ASSET_MANIFEST.json` | 全部图片、字体的 SHA256 清单；增删素材要同步 |
| `HANDOFF.md` | 开发交接记录，第一节是当前状态 |

## 安装与使用

**本机**：把 Skill 目录软链进 Agent 的 skills 目录，不要复制，因为 SKILL.md 里用到 `../jacky-illustration` 和 `../../experiments` 这类相对路径：

```sh
ln -s <仓库路径>/skills/jacky-cover ~/.claude/skills/jacky-cover
```

**云端 Agent**（如 claude.ai/code）：在 GitHub 授权里勾选本仓库即可直接使用私有仓库，默认读 `main`。生图需要已登录的 `codex` CLI；云端没有时，只能做方案、提示词和合成步骤。

**依赖**：Python 3.10+ 和 Pillow（`requirements.txt`）。字体优先读 `~/Library/Fonts`，没有就用仓库自带的。

## 校验与测试

从仓库根目录运行：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/verify_assets.py
cd skills/jacky-cover && PYTHONDONTWRITEBYTECODE=1 ../../.venv/bin/python -m unittest discover -s tests -v
```

测试只证明脚本和素材正确，不能证明人物、隐喻和审美过关；这些靠每期的自检和用户验收。

## 素材

含真人原照、生成的动作图和第三方参考，不应把整个仓库当作统一开源授权。上游许可见 [ASSETS.md](ASSETS.md)。
