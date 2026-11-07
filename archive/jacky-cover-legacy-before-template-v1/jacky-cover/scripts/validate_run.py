#!/usr/bin/env python3

import argparse
from pathlib import Path


OIL_PROMPT_FIELDS = (
    "Use case:",
    "Asset type:",
    "Input images:",
    "Primary request:",
    "Content attribution:",
    "Title text:",
    "Composition:",
    "Portrait integration guard:",
    "Mandatory visible background:",
    "Colour system:",
    "Screen crop plan:",
    "Screenshot distillation plan:",
    "Visual communication plan:",
    "Screen refinement plan:",
    "Shadow plan:",
    "Text style:",
    "Title decoration:",
    "Decoration:",
    "Jacky brand patch:",
    "Avoid:",
)

ANALYSIS_FIELDS = (
    "素材检查",
    "证据模式",
    "主主题",
    "主产品",
    "承载界面",
    "辅助品牌",
    "一眼主语",
    "主证据",
    "辅助证据",
    "可牺牲信息",
    "标题提炼依据",
    "最近封面对照",
    "目标人物动作",
    "身份锚点来源：原始照片",
)

PLAN_FIELDS = (
    "标题断行",
    "强调词",
    "构图",
    "屏幕裁切",
    "人物层级",
    "人物空间关系",
    "参考输入",
    "连续封面差异",
    "副标题",
    "内容分工",
    "面板可视化",
    "人物裁切",
)

ASPECT_MARKERS = {
    "3x4": "exact 3:4 portrait",
    "4x3": "exact 4:3 horizontal",
    "16x9": "exact 16:9 horizontal",
}

STYLE_REFERENCE_NAMES = {"gallery.png", "gallery-4x3.png"}


def read_text(path: Path, label: str, errors: list[str]) -> str:
    if not path.is_file():
        errors.append(f"missing {label}: {path}")
        return ""
    return path.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Jacky Cover run before ImageGen.")
    parser.add_argument("--prompt", required=True, type=Path)
    parser.add_argument("--analysis", required=True, type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--aspect", required=True, choices=sorted(ASPECT_MARKERS))
    parser.add_argument("--refs", required=True, nargs="+", type=Path)
    parser.add_argument("--identity-refs", nargs=2, type=Path)
    parser.add_argument("--evidence-refs", nargs="*", type=Path, default=[])
    parser.add_argument("--logo-refs", nargs="*", type=Path, default=[])
    parser.add_argument("--max-refs", type=int, default=5,
                        help="Reference-image budget (default 5); change only for a verified host limit")
    args = parser.parse_args()

    errors: list[str] = []
    prompt = read_text(args.prompt, "prompt", errors)
    analysis = read_text(args.analysis, "analysis", errors)
    plan = read_text(args.plan, "cover plan", errors)

    for field in OIL_PROMPT_FIELDS:
        if field not in prompt:
            errors.append(f"missing Oil Cover prompt field: {field}")

    for field in ANALYSIS_FIELDS:
        if field not in analysis:
            errors.append(f"missing Oil Cover analysis field: {field}")

    for field in PLAN_FIELDS:
        if field not in plan:
            errors.append(f"missing cover plan field: {field}")

    positions = [prompt.find(field) for field in OIL_PROMPT_FIELDS]
    if all(pos >= 0 for pos in positions) and positions != sorted(positions):
        errors.append("Oil Cover prompt fields are out of order")

    is_transcript_derived = (
        "证据模式：transcript-derived" in analysis
        or "证据模式: transcript-derived" in analysis
    )
    is_real_screen = "证据模式：real-screen" in analysis or "证据模式: real-screen" in analysis

    marker = ASPECT_MARKERS[args.aspect]
    if marker not in prompt:
        errors.append(f"prompt does not declare aspect marker: {marker}")

    # Crop, typography, colour, wardrobe and pose are user-overridable design
    # choices. Validate input structure here, not exact aesthetic wording.
    if is_real_screen == is_transcript_derived:
        errors.append("choose exactly one evidence mode: real-screen or transcript-derived")

    missing_refs = [str(path) for path in args.refs if not path.is_file()]
    for path in missing_refs:
        errors.append(f"reference file does not exist: {path}")

    refs = [path.resolve() for path in args.refs]
    if args.max_refs < 1 or len(refs) > args.max_refs:
        errors.append(f"reference count exceeds host limit: {len(refs)} > {args.max_refs}")
    if len(set(refs)) != len(refs):
        errors.append("duplicate reference files")
    styles = {path for path in refs if path.name in STYLE_REFERENCE_NAMES}

    identity = [p.resolve() for p in args.identity_refs] if args.identity_refs else [
        p for p in refs if p.name.startswith("jacky-reference-")
    ]
    evidence = {p.resolve() for p in args.evidence_refs}
    logos = {p.resolve() for p in args.logo_refs}
    if len(identity) != 2 or len(set(identity)) != 2:
        errors.append("exactly two distinct original identity references are required")
    roles = [("identity", set(identity)), ("evidence", evidence), ("logo", logos)]
    for label, paths in roles:
        if not paths.issubset(set(refs)):
            errors.append(f"{label} references must be included in --refs")
        if paths & styles:
            errors.append(f"style reference cannot also be {label} reference")
    if set(identity) & (evidence | logos) or evidence & logos:
        errors.append("identity, evidence and logo roles must be separate")
    if is_real_screen and not evidence:
        errors.append("real-screen evidence mode requires explicit --evidence-refs; logo alone is not evidence")
    if is_transcript_derived and evidence:
        errors.append("transcript-derived cannot declare real-screen evidence refs; select the correct mode")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"Jacky Cover preflight passed: {args.aspect}, {len(args.refs)} reference files")
    print("Structural check only: inspect actual output for identity, pose, text hierarchy and visual evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
