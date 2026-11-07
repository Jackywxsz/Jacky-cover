#!/usr/bin/env python3
"""给透明前景加白色贴纸描边和浅投影。用法：sticker_edge.py <in.png> <out.png> [描边px] [--bleed left|right]
左、右、上加宽画布让描边完整；底边是身体收口（合成时渐隐进黑区），不加描边。
主体碰到左/右/上边缘说明生图时被裁切，直接报错；只有人物身体（肩、手臂）被左右边切到、
要贴着封面边缘出画时，才用 --bleed 指定那一侧：那一侧不加描边，合成时贴住封面边缘。"""
import sys
from pathlib import Path
from PIL import Image, ImageFilter
from PIL.PngImagePlugin import PngInfo

args = sys.argv[1:]
bleed = set()
while '--bleed' in args:
    i = args.index('--bleed'); bleed.add(args[i+1]); del args[i:i+2]
if not bleed <= {'left', 'right'}:
    sys.exit('--bleed 只能是 left 或 right')
src, out = args[0], args[1]
width = int(args[2]) if len(args) > 2 else 14
if Path(out).exists():
    sys.exit(f'已存在，不覆盖：{out}')
im = Image.open(src).convert('RGBA')
a = im.getchannel('A')
w, h = im.size
for name, box in [('left', (0, 0, 2, h)), ('right', (w-2, 0, w, h)), ('top', (0, 0, w, 2))]:
    rows = a.crop(box).point(lambda v: 1 if v > 40 else 0).histogram()[1] // 2
    if rows > 10 and name not in bleed:  # a few pixels of a flying prop grazing the edge is tolerated
        sys.exit(f'CROPPED {name}: {src}')
pad = width * 3
canvas = Image.new('RGBA', (w + pad * 2, h + pad * 2))
canvas.alpha_composite(im, (pad, pad))
alpha = canvas.getchannel('A').point(lambda v: 255 if v > 40 else 0)
# Extend the bottom cut downward so no outline forms along it.
alpha.paste(alpha.crop((0, pad + h - 1, w + pad * 2, pad + h)).resize((w + pad * 2, pad + 1)), (0, pad + h - 1))
# Same for a side the body bleeds off.
if 'left' in bleed:
    alpha.paste(alpha.crop((pad, 0, pad + 1, h + pad * 2)).resize((pad + 1, h + pad * 2)), (0, 0))
if 'right' in bleed:
    alpha.paste(alpha.crop((pad + w - 1, 0, pad + w, h + pad * 2)).resize((pad + 1, h + pad * 2)), (pad + w - 1, 0))
edge = alpha.filter(ImageFilter.MaxFilter(width * 2 + 1)).filter(ImageFilter.GaussianBlur(1))
shadow = edge.filter(ImageFilter.GaussianBlur(width)).point(lambda v: v * 35 // 100)
result = Image.new('RGBA', canvas.size)
result.alpha_composite(Image.merge('RGBA', [Image.new('L', canvas.size, 0)] * 3 + [shadow]), (0, width // 2))
result.alpha_composite(Image.merge('RGBA', [Image.new('L', canvas.size, 255)] * 3 + [edge]))
result.alpha_composite(canvas)
meta = PngInfo()
meta.add_text('jacky_cover_bleed', ','.join(sorted(bleed)))  # read by compose_interaction_cover.py
result.crop((pad if 'left' in bleed else 0, 0, pad + w if 'right' in bleed else w + pad * 2, pad + h)).save(out, pnginfo=meta)
