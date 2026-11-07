#!/usr/bin/env python3

import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_DIR / "scripts" / "validate_run.py"


VALID_ANALYSIS = """# Analysis

- 素材检查：已查源稿旁与对应项目，只有逐字稿
- 证据模式：transcript-derived
- 主主题：文科生通过公开 AI 输出获得企业 AI 落地岗机会
- 主产品：无
- 承载界面：内容衍生的编辑型证据面板
- 辅助品牌：无
- 一眼主语：公开作品让文科生被企业看见
- 主证据：AI 作品集成果画廊
- 辅助证据：被看见信号与公开输出反馈
- 可牺牲信息：完整履历和解释段落
- 标题提炼依据：逐字稿中的文科生、三万粉和企业 AI 落地岗
- 最近封面对照：最近一张为托腮人物、左上标题和下方大斜窗
- 目标人物动作：右下开放指向作品集，禁止托腮与抱臂
- 身份锚点来源：原始照片
"""

VALID_PLAN = """# Cover plan

- 标题断行：账号变作品集
- 强调词：作品集
- 构图：由 Oil Cover 根据 3:4 规则决定
- 屏幕裁切：一个浏览器物件，保留 80%-95%，至少一边被画布裁切
- 人物层级：人物及互动手完整位于所有面板和卡片前景
- 人物空间关系：人物跨过一个面板边缘，面板在躯干后延续，并由局部接触阴影建立前后景
- 参考输入：Oil Cover gallery 风格参考 + 逐字稿 + 2 张 Jacky 身份锚点
- 连续封面差异：动作、人物比例、标题结构、证据几何与视觉钩子均不同
- 副标题：文科生靠3万粉拿下AI落地岗
- 内容分工：主标结论，副标背景，面板作品
- 面板可视化：一组连贯作品预览
- 人物裁切：上半身，不露裤腰
"""

VALID_PROMPT = """Use case: ads-marketing.
Asset type: Xiaohongshu exact 3:4 portrait cover.
Input images: Image 1 is the Oil Cover style reference; Images 2 and 3 are Jacky identity references. Evidence mode is transcript-derived.
Primary request: Create one complete Oil Cover editorial cover with one integrated Jacky portrait.
Content attribution: main topic is transcript-derived; main product is none; host interface is a content-derived editorial evidence panel; supporting brands are none.
Title text: primary title "账号变作品集"; optional short subtitle "文科生靠3万粉拿下AI落地岗". The primary title fills 90%-96% of the safe width.
Composition: title block stays within 10%-42% of canvas height; screen stays below it with Oil Cover hierarchy.
Portrait integration guard: generate Jacky as an integrated part of the same scene, not as a pasted cutout. The entire Jacky figure stays in foreground above every screen, panel, card and window layer. One panel plane continues behind the lower-right torso or shoulder, and the torso visibly crosses that edge with no floating gap; use a narrow localized contact shadow. Default to no hand contact with any panel edge, card, window or screen. If a pointing gesture is essential, use only the inner-side hand nearest the panel, keep a clearly visible air gap between every finger and the panel, and keep the complete hand and forearm in foreground. Never grip, hold, pinch, rest on, hook around or wrap fingers around a panel edge. The natural half-body crop meets the bottom canvas edge.
Mandatory visible background: full-canvas clean #E7DBC4 base, visible fine grid, a soft pastel blue atmosphere derived from #0138C4 glowing gently from the edges or corners, very light grain; no neon or acid hues.
Colour system: #0138C4 is limited to one keyword and small aligned marks; panels stay warm white or light neutral.
Screen crop plan: one visible browser object only; show 80%-95%; clip at least one edge by the canvas.
Screenshot distillation plan: evidence mode is transcript-derived; use one primary evidence object occupying 65%-80% of the screen content area, plus at most one supporting evidence line or one short chip; remove dense text and fake product branding.
Visual communication plan: one-glance subject is the portfolio creating the job opportunity; the same primary evidence object occupies 65%-80% of the screen content area; only one short supporting line or chip remains.
Screen refinement plan: enlarge the primary portfolio evidence; preserve window chrome and red-yellow-green controls; remove irrelevant paths and dense copy.
Shadow plan: one clean light graphite screen shadow and soft contact shadow.
Text style: modern PingFang SC / SF Pro CJK hierarchy; deep graphite main text; restrained serif accent where useful.
Title decoration: one thin #0138C4 underline and cursor mark aligned with the highlighted job phrase.
Decoration: only content-related status marks aligned to the Oil Cover grid.
Jacky brand patch: #E7DBC4 paper base; restrained #0138C4; natural relaxed Jacky at lower right with a thin white keyline, wearing a fitted but not compression-tight plain black crew-neck short-sleeve T-shirt in matte cotton; no blazer, jacket, overshirt, cardigan, polo or button-down shirt.
Avoid: full screenshot copy, dense tiny text, fake UI, extra person, avatar or face inside the panel, large saturated blue panel, watermark, low-resolution artifacts.
"""

LEGACY_INVALID_PROMPT = """Create one complete 3:4 cover. Keep the full strength of an Oil Cover.
Put an information panel in the lower half with AI 作品集, 被看见 and 公开输出.
Use #E7DBC4 and #0138C4. Put Jacky at the lower right.
"""


def replace_field(prompt, field, value):
    """Replace one fixture field without carrying conflicting old prose."""
    lines = prompt.splitlines()
    return "\n".join(field + " " + value if line.startswith(field) else line
                     for line in lines) + "\n"


class ValidateRunTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.analysis = self.root / "analysis.md"
        self.plan = self.root / "cover_plan.md"
        self.prompt = self.root / "cover_3x4.prompt.md"
        self.analysis.write_text(VALID_ANALYSIS)
        self.plan.write_text(VALID_PLAN)
        for name in ("gallery.png", "jacky-reference-front.jpg", "jacky-reference-side.jpg", "screen-evidence.png"):
            (self.root / name).touch()

    def tearDown(self):
        self.tempdir.cleanup()

    def run_validator(self, prompt_text, evidence_mode="transcript-derived", extra_args=None, extra_refs=None, include_gallery=True):
        self.prompt.write_text(prompt_text)
        refs = [
            self.root / "jacky-reference-front.jpg",
            self.root / "jacky-reference-side.jpg",
        ]
        if include_gallery:
            refs.insert(0, self.root / "gallery.png")
        if evidence_mode == "real-screen":
            refs.append(self.root / "screen-evidence.png")
        refs.extend(extra_refs or [])
        return subprocess.run(
            [
                "python3",
                str(VALIDATOR),
                "--prompt",
                str(self.prompt),
                "--analysis",
                str(self.analysis),
                "--plan",
                str(self.plan),
                "--aspect",
                "3x4",
                "--refs",
                *map(str, refs),
                *(extra_args or []),
            ],
            capture_output=True,
            text=True,
        )

    def test_rejects_legacy_prompt_that_only_mentions_oil_cover(self):
        result = self.run_validator(LEGACY_INVALID_PROMPT)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing Oil Cover prompt field", result.stdout)

    def test_accepts_complete_oil_prompt_with_small_jacky_patch(self):
        result = self.run_validator(VALID_PROMPT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Jacky Cover preflight passed", result.stdout)

    def test_accepts_user_wardrobe_and_nonoverlapping_layout(self):
        self.plan.write_text(VALID_PLAN + "\n用户覆盖：人物在面板旁，不交叠；衣着按指定参考")
        prompt = replace_field(VALID_PROMPT, "Portrait integration guard:",
                               "Keep the person beside the panel, with natural anatomy.")
        prompt = replace_field(prompt, "Jacky brand patch:",
                               "Use the user-specified wardrobe and preserve identity.")
        result = self.run_validator(prompt)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("Structural check only", result.stdout)

    def test_user_title_is_not_blocked_by_new_jacky_length_quota(self):
        self.analysis.write_text(VALID_ANALYSIS + "\n标题覆盖：用户指定")
        prompt = VALID_PROMPT.replace('primary title "账号变作品集"',
                                     'primary title "告别写报告 Opus5.5接管比赛"')
        result = self.run_validator(prompt)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_coherent_gallery_not_rejected_by_literal_density_recipe(self):
        prompt = VALID_PROMPT.replace(
            "one primary evidence object occupying 65%-80% of the screen content area, plus at most one supporting evidence line or one short chip",
            "a coherent portfolio gallery with a clear primary example; delete repetitive prose",
        )
        result = self.run_validator(prompt)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_user_requested_hand_pose_is_not_an_aesthetic_gate(self):
        self.plan.write_text(VALID_PLAN + "\n用户覆盖：手自然扶面板；须目检手指结构和遮挡")
        prompt = replace_field(VALID_PROMPT, "Portrait integration guard:",
                               "The inner-side hand may rest on the panel edge.")
        result = self.run_validator(prompt)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_natural_repeated_pose_does_not_require_three_changes(self):
        self.plan.write_text(VALID_PLAN + "\n连续封面差异数：1；沿用自然直立姿态")
        result = self.run_validator(VALID_PROMPT)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_documented_portrait_example_passes_structure_check(self):
        visual = (SKILL_DIR / "references" / "visual-system.md").read_text()
        guard = next(line for line in visual.splitlines()
                     if line.startswith("Portrait integration guard:"))
        prompt = replace_field(VALID_PROMPT, "Portrait integration guard:",
                               guard.split(":", 1)[1])
        result = self.run_validator(prompt)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_accepts_complete_panel_without_forced_crop(self):
        self.analysis.write_text(VALID_ANALYSIS.replace("transcript-derived", "real-screen"))
        self.plan.write_text(VALID_PLAN.replace(
            "一个浏览器物件，保留 80%-95%，至少一边被画布裁切",
            "用户指定完整面板，内部布局和内容不拆分，无额外容器"))
        prompt = replace_field(VALID_PROMPT, "Screen crop plan:",
                               "Show the entire supplied panel with all internal content.")
        prompt = replace_field(prompt, "Screenshot distillation plan:",
                               "Preserve the full panel; do not extract or rearrange elements.")
        prompt = replace_field(prompt, "Avoid:", "Duplicate containers and evidence occlusion.")
        prompt = prompt.replace("Evidence mode is transcript-derived.",
                                "Image 4 is real-screen evidence.")
        result = self.run_validator(prompt, evidence_mode="real-screen",
            extra_args=["--evidence-refs", str(self.root / "screen-evidence.png")])
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_user_style_reference_can_replace_gallery(self):
        reference = self.root / "user-style.png"
        reference.touch()
        prompt = replace_field(VALID_PROMPT, "Input images:",
            "Images 1 and 2: original identity photos; Image 3: user style reference.")
        result = self.run_validator(prompt, include_gallery=False, extra_refs=[reference])
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_local_edit_with_original_identity_and_evidence(self):
        target = self.root / "selected-cover.png"
        target.touch()
        self.analysis.write_text(VALID_ANALYSIS.replace("transcript-derived", "real-screen"))
        self.plan.write_text(VALID_PLAN + "\n本轮要改：一个错字\n必须保留：人物、面板、布局\n尚未确认：修字结果")
        prompt = replace_field(VALID_PROMPT, "Use case:", "text-localization.")
        prompt = replace_field(prompt, "Input images:",
            "Images 1 and 2: original identity photos; Image 3: panel evidence; Image 4: edit target.")
        prompt = replace_field(prompt, "Primary request:",
            "Correct only the specified title character in Image 4. Preserve portrait, panel and layout.")
        result = self.run_validator(prompt, evidence_mode="real-screen",
            include_gallery=False, extra_refs=[target],
            extra_args=["--evidence-refs", str(self.root / "screen-evidence.png")])
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_real_screen_mode_requires_a_content_evidence_reference(self):
        self.analysis.write_text(VALID_ANALYSIS.replace("transcript-derived", "real-screen"))
        real_screen_prompt = VALID_PROMPT.replace("transcript-derived", "real-screen").replace(
            "65%-80%", "55%-75%"
        )
        result = self.run_validator(real_screen_prompt)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("real-screen evidence mode requires", result.stdout)

    def test_logo_alone_cannot_satisfy_real_evidence(self):
        self.analysis.write_text(VALID_ANALYSIS.replace("transcript-derived", "real-screen"))
        logo = self.root / "claude.png"
        logo.touch()
        result = self.run_validator(VALID_PROMPT.replace("65%-80%", "55%-75%"),
                                    extra_refs=[logo], extra_args=["--logo-refs", str(logo)])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("explicit --evidence-refs", result.stdout)

    def test_accepts_explicit_real_evidence(self):
        self.analysis.write_text(VALID_ANALYSIS.replace("transcript-derived", "real-screen"))
        result = self.run_validator(VALID_PROMPT.replace("65%-80%", "55%-75%"),
            evidence_mode="real-screen",
            extra_args=["--evidence-refs", str(self.root / "screen-evidence.png")])
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_declared_evidence_must_actually_be_uploaded(self):
        self.analysis.write_text(VALID_ANALYSIS.replace("transcript-derived", "real-screen"))
        result = self.run_validator(VALID_PROMPT.replace("65%-80%", "55%-75%"),
            extra_args=["--evidence-refs", str(self.root / "screen-evidence.png")])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("evidence references must be included", result.stdout)

    def test_reference_budget(self):
        extras = [self.root / f"extra-{i}.png" for i in range(3)]
        for p in extras:
            p.touch()
        result = self.run_validator(VALID_PROMPT, extra_refs=extras)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exceeds host limit", result.stdout)

    def test_duplicate_identity_photo_rejected(self):
        photo = str(self.root / "jacky-reference-front.jpg")
        result = self.run_validator(VALID_PROMPT,
                                   extra_args=["--identity-refs", photo, photo])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("two distinct", result.stdout)

    def test_role_overlap_rejected(self):
        self.analysis.write_text(VALID_ANALYSIS.replace("transcript-derived", "real-screen"))
        photo = str(self.root / "jacky-reference-front.jpg")
        result = self.run_validator(VALID_PROMPT.replace("65%-80%", "55%-75%"),
                                   extra_args=["--evidence-refs", photo])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("roles must be separate", result.stdout)

    def test_missing_subtitle_decision_rejected(self):
        self.plan.write_text(VALID_PLAN.replace("- 副标题：文科生靠3万粉拿下AI落地岗\n", ""))
        result = self.run_validator(VALID_PROMPT)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing cover plan field: 副标题", result.stdout)

    def test_missing_source_inventory_rejected(self):
        self.analysis.write_text(VALID_ANALYSIS.replace("素材检查", "忽略素材"))
        result = self.run_validator(VALID_PROMPT)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing Oil Cover analysis field: 素材检查", result.stdout)

    def test_missing_reference_file_rejected(self):
        missing = self.root / "absent.png"
        result = self.run_validator(VALID_PROMPT, extra_refs=[missing])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reference file does not exist", result.stdout)

    def test_missing_identity_photo_rejected(self):
        (self.root / "jacky-reference-side.jpg").unlink()
        result = self.run_validator(VALID_PROMPT)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reference file does not exist", result.stdout)

    def test_conflicting_evidence_modes_rejected(self):
        self.analysis.write_text(VALID_ANALYSIS + "\n证据模式：real-screen")
        result = self.run_validator(VALID_PROMPT)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("choose exactly one evidence mode", result.stdout)

    def test_gallery_cannot_be_identity_reference(self):
        result = self.run_validator(VALID_PROMPT, extra_args=[
            "--identity-refs", str(self.root / "gallery.png"),
            str(self.root / "jacky-reference-front.jpg")])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("style reference cannot also be identity", result.stdout)

    def test_prompt_field_order(self):
        prompt = VALID_PROMPT.replace("Use case: ads-marketing.\n", "")
        prompt += "Use case: ads-marketing.\n"
        result = self.run_validator(prompt)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("out of order", result.stdout)


if __name__ == "__main__":
    unittest.main()
