#!/usr/bin/env python3
"""列出手写小字能放的空白带（与标题左边对齐），供执行者按构图挑位置。
用法：note_space.py <report.json> <layers目录> <小字文字> [字号=52]
输出每个空白带的 y 范围（像素与归一化），以及放在带内居中时可写进 text.json 的 xy。"""
import json
import sys
from pathlib import Path
import importlib.util
from PIL import Image, ImageFont

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('compose', ROOT / 'scripts/compose_interaction_cover.py')
compose = importlib.util.module_from_spec(spec); spec.loader.exec_module(compose)
report = json.loads(Path(sys.argv[1]).read_text())
fg = Image.open(Path(sys.argv[2]) / 'foreground.png').getchannel('A')
text = sys.argv[3]
size = int(sys.argv[4]) if len(sys.argv) > 4 else 52
profile = json.loads((ROOT / 'references/interaction-profile.json').read_text())
font = ImageFont.truetype(str(compose.font_file(profile['note'])), size)  # same lookup as the compositor
w, h = report['size']
x0 = min(b[0] for b in report['title_boxes'])
title_top = report['title_boxes'][0][1]
note_w = int(font.getlength(text)) + 10
note_h = size + 12
band = fg.crop((x0, 0, min(w, x0 + note_w), title_top - 16))
runs, start = [], None
for y in range(band.height + 1):
    empty = y < band.height and band.crop((0, y, band.width, y + 1)).getextrema()[1] <= 2
    if empty and start is None:
        start = y
    if not empty and start is not None:
        if y - start >= note_h:
            runs.append((start, y))
        start = None
print(f'title_left x={x0}, note width={note_w}px, title top y={title_top}')
if x0 + note_w > round(.95 * w):
    print('小字太宽，缩小字号或缩短文字')
for a, b in runs:
    top = max(round(.035 * h), a + (b - a - note_h) // 2)
    print(f'空白带 y {a}-{b} ({a/h:.3f}-{b/h:.3f})  建议 "xy": ["title_left", {top/h:.3f}]')
if not runs:
    print('没有足够空白：缩小字号、缩短文字，或不放小字')
