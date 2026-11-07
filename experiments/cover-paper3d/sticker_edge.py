#!/usr/bin/env python3
"""给透明前景加白色贴纸描边和浅投影。用法：sticker_edge.py <in.png> <out.png> [描边px]
左、右、上加宽画布让描边完整；底边是身体收口（合成时渐隐进黑区），不加描边。
主体碰到左/右/上边缘说明生图时被裁切，直接报错。"""
import sys
from PIL import Image, ImageFilter

src, out = sys.argv[1], sys.argv[2]
width = int(sys.argv[3]) if len(sys.argv) > 3 else 14
im = Image.open(src).convert('RGBA')
a = im.getchannel('A')
w, h = im.size
for name, box in [('left', (0, 0, 2, h)), ('right', (w-2, 0, w, h)), ('top', (0, 0, w, 2))]:
    rows = sum(1 for v in a.crop(box).point(lambda v: 255 if v > 40 else 0).getdata() if v) // 2
    if rows > 10:  # a few pixels of a flying prop grazing the edge is tolerated
        sys.exit(f'CROPPED {name}: {src}')
pad = width * 3
canvas = Image.new('RGBA', (w + pad * 2, h + pad * 2))
canvas.alpha_composite(im, (pad, pad))
alpha = canvas.getchannel('A').point(lambda v: 255 if v > 40 else 0)
# Extend the bottom cut downward so no outline forms along it.
alpha.paste(alpha.crop((0, pad + h - 1, w + pad * 2, pad + h)).resize((w + pad * 2, pad + 1)), (0, pad + h - 1))
edge = alpha.filter(ImageFilter.MaxFilter(width * 2 + 1)).filter(ImageFilter.GaussianBlur(1))
shadow = edge.filter(ImageFilter.GaussianBlur(width)).point(lambda v: v * 35 // 100)
result = Image.new('RGBA', canvas.size)
result.alpha_composite(Image.merge('RGBA', [Image.new('L', canvas.size, 0)] * 3 + [shadow]), (0, width // 2))
result.alpha_composite(Image.merge('RGBA', [Image.new('L', canvas.size, 255)] * 3 + [edge]))
result.alpha_composite(canvas)
result.crop((0, 0, w + pad * 2, pad + h)).save(out)
