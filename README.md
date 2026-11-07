# Jacky Cover

2026-11-07 流程定稿：Jacky 真人 + 芽仔 3D 手办的隐喻场景，透明抠图加白边贴到纸蓝底，下方渐变黑蒙版 + 普惠体两行标题 + 霞鹜文楷小字。定稿后正在用真实选题实测，单期成品是否被用户认可见各期 `check.md`。

本仓库保留当前 Skill、品牌素材与原照、依赖的 Jacky Illustration、旧版快照和迭代证据。没有发布 release。

先读 [HANDOFF.md](HANDOFF.md)，再读 [当前 Skill](skills/jacky-cover/SKILL.md)。

## 目录

- `skills/jacky-cover/`：唯一当前 Cover 实现（2026-11-07 定稿）。默认纸蓝风：Codex 生图出透明 3D 抠图 → `sticker_edge.py` 加白边 → `compose_interaction_cover.py` 合成纸蓝底、黑蒙版、普惠体标题与霞鹜文楷小字，带单元测试。可选暗调整图风（gbro 式一次生成整张）。
- `skills/jacky-illustration/`：本次交接时的完整依赖快照；芽仔锚点、纸片隐喻方法、示例与上游许可。不是另一套 Cover 默认。
- `experiments/covers/`：按定稿流程实跑的每一期（提示词、检查记录、成品）。
- `experiments/cover-paper3d/`：定稿流程的验证测试。
- `experiments/cover-gbro/`、`cover-paper/`、`cover-tests/`、`pose-library*/`：被否方案的过程记录（只提交了文字和总览图）。
- `experiments/paper-blue/`、`experiments/opus55/`：更早的纸蓝模板与 Opus v1–v5 迭代（已被否）。
- `research/director-composition/`：吸收 gbro 构图方法的来源、许可与历史修改记录。
- `archive/`：7份旧 Skill 快照，从原备份解包保存，不自动加载或覆盖当前实现。
- `tools/`：校验素材与复现合成；不调用任何生图服务。
- `ASSET_MANIFEST.json`：全包图片、字体的 SHA256 清单。

## 校验与测试

需要 Python 3.10+。从仓库根目录运行：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/verify_assets.py
.venv/bin/python -m unittest discover -s skills/jacky-cover/tests -v
```

`tools/replay_opus55.py` 只对应旧版合成脚本，当前脚本的配置字段已变，不再可用；仅作历史记录。

生图需要本机已安装并登录的 `codex` CLI（见 SKILL.md），仓库不附带任何 API 凭据。

## 素材与使用

这是私人开发交接，包含用户明确要求保留的真人原照和第三方动作参考，不应把整个仓库当作统一开源授权。已有上游许可原样保留，见 [素材说明](ASSETS.md)。历史文本中的本机路径已改为仓库路径或占位符；图片/字体字节保持原样，见素材清单。历史安装脚本只作证据，不要直接执行；可复现入口以 `tools/` 为准。
