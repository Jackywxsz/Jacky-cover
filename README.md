# Jacky Cover — 开发中 / 待接手优化

**这是未完成开发的交接仓库，不是已验收发布版。最新 Opus 5.5 v5 封面已被用户明确否定。**

本仓库保留当前 Skill 全量文件、完整品牌素材/原照/动作参考、依赖的 Jacky Illustration、旧版备份和本次迭代证据，供后续开发者接手。没有发布 release，没有把失败图提升为新模板。

先读 [HANDOFF.md](HANDOFF.md)，再读 [当前 Skill](skills/jacky-cover/SKILL.md)。

## 目录

- `skills/jacky-cover/`：唯一当前 Cover 实现，完整素材、规范、合成脚本、13项测试。
- `skills/jacky-illustration/`：本次交接时的完整依赖快照；芽仔锚点、纸片隐喻方法、示例与上游许可。不是另一套 Cover 默认。
- `experiments/paper-blue/`：纸蓝模板、主副标题、蒙版和 Grok Bot 的迭代过程、原始输入及分层输出。
- `experiments/opus55/`：当前未完成选题，v1–v5、无蒙版前景、prompt、手臂错位排查和用户否定状态。
- `research/director-composition/`：吸收 gbro 构图方法的来源、许可与历史修改记录。
- `archive/`：7份旧 Skill 快照，从原备份解包保存，不自动加载或覆盖当前实现。
- `tools/`：校验素材与复现合成；不调用任何生图服务。
- `ASSET_MANIFEST.json`：全包图片、字体的 SHA256 清单。

## 复现现有合成（不是重新生图）

需要 Python 3.10+。从仓库根目录运行：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python tools/verify_assets.py
.venv/bin/python -m unittest discover -s skills/jacky-cover/tests -v
.venv/bin/python tools/replay_opus55.py --output output/opus55-v5-replay
```

脚本使用仓库内真实字体和项目模板，无需原电脑目录。输出含封面、无字图层、蒙版、缩略图及报告；已有输出目录不可覆盖。重放的是**用户拒绝的 v5**，只用来验证文件/字体/合成链路齐全，不证明构图、人体或隐喻合格。

新图片生成需要宿主提供图像生成能力；仓库没有附带 API 凭据，也没有声称可以离线自动重新生成真人。实际原照、芽仔、动作参考与 prompt 都已保留。

## 素材与使用

这是私人开发交接，包含用户明确要求保留的真人原照和第三方动作参考，不应把整个仓库当作统一开源授权。已有上游许可原样保留，见 [素材说明](ASSETS.md)。历史文本中的本机路径已改为仓库路径或占位符；图片/字体字节保持原样，见素材清单。历史安装脚本只作证据，不要直接执行；可复现入口以 `tools/` 为准。
