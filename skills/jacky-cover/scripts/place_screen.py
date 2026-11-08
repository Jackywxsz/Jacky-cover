#!/usr/bin/env python3
"""把真实截图贴进生成图里留成洋红色的屏幕。用法：place_screen.py <前景.png> <截图> <输出.png> [--fit contain|cover]
生成时屏幕画成纯洋红（#FF00FF）、四个角都露出来；脚本找到洋红区域的四个角，把截图按透视贴进去。
只替换洋红像素，所以挡在屏幕前的芽仔、手、物件保持在上层。截图内容逐像素来自原图，不经模型重画。
报告（JSON）打到标准输出；洋红太少、四角找不准时直接报错，换一张重新生成。"""
import json
import sys
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter

FULL, SOFT = 140, 90  # key score: >=FULL fully replaced, SOFT..FULL partially


def key_score(rgb):
    r, g, b = rgb.split()
    return ImageChops.subtract(ImageChops.darker(r, b), g)  # magenta-ness: min(R,B) - G


def corners(mask):
    # Extreme points of the screen area: works for a flat screen seen in perspective.
    w = mask.width
    pts = [(i % w, i // w) for i, v in enumerate(mask.getdata()) if v]
    tl = min(pts, key=lambda p: p[0] + p[1]); br = max(pts, key=lambda p: p[0] + p[1])
    tr = max(pts, key=lambda p: p[0] - p[1]); bl = min(pts, key=lambda p: p[0] - p[1])
    return [tl, tr, br, bl], len(pts)


def quad_area(q):
    return abs(sum(q[i][0]*q[(i+1) % 4][1] - q[(i+1) % 4][0]*q[i][1] for i in range(4))) / 2


def solve(a, b):
    n = len(b); m = [row[:] + [v] for row, v in zip(a, b)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(m[r][c])); m[c], m[p] = m[p], m[c]
        for r in range(n):
            if r != c:
                f = m[r][c] / m[c][c]
                m[r] = [x - f*y for x, y in zip(m[r], m[c])]
    return [m[i][n] / m[i][i] for i in range(n)]


def perspective(dst, src):
    # Coefficients mapping output (dst) points back to input (src) points, as Image.transform wants.
    a, b = [], []
    for (x, y), (u, v) in zip(dst, src):
        a += [[x, y, 1, 0, 0, 0, -u*x, -u*y], [0, 0, 0, x, y, 1, -v*x, -v*y]]; b += [u, v]
    return solve(a, b)


def main(argv):
    fit = 'contain'
    if '--fit' in argv:
        i = argv.index('--fit'); fit = argv[i+1]; del argv[i:i+2]
    if fit not in ('contain', 'cover') or len(argv) != 3:
        sys.exit(__doc__)
    fg_path, shot_path, out = argv
    if Path(out).exists():
        sys.exit(f'已存在，不覆盖：{out}')
    fg = Image.open(fg_path).convert('RGBA')
    score = key_score(fg.convert('RGB'))
    hard = score.point(lambda v: 255 if v >= FULL else 0).filter(ImageFilter.MinFilter(5))
    q, n = corners(hard) if hard.getbbox() else ([], 0)
    if n < 0.01 * fg.width * fg.height:
        sys.exit('没找到洋红屏幕：生成时屏幕要画成纯洋红（#FF00FF）')
    coverage = n / max(1, quad_area(q))
    if coverage < 0.55:
        sys.exit(f'洋红区域不像一块平的四边形屏幕（覆盖率 {coverage:.2f}），可能角被挡住或屏幕弯曲：重新生成，四个角都露出来')
    # Screen proportions from the quad's average edge lengths.
    d = lambda p, r: ((p[0]-r[0])**2 + (p[1]-r[1])**2) ** .5
    sw = (d(q[0], q[1]) + d(q[3], q[2])) / 2; sh = (d(q[0], q[3]) + d(q[1], q[2])) / 2
    shot = Image.open(shot_path).convert('RGB')
    W = 2000; H = max(1, round(W * sh / sw))
    s = (max if fit == 'cover' else min)(W / shot.width, H / shot.height)
    scaled = shot.resize((max(1, round(shot.width*s)), max(1, round(shot.height*s))), Image.Resampling.LANCZOS)
    canvas = Image.new('RGB', (W, H), shot.getpixel((0, 0)))  # contain: pad with the screenshot's edge color
    canvas.paste(scaled, ((W - scaled.width)//2, (H - scaled.height)//2))
    # Grow the quad by 2px so the magenta fringe along the frame is covered too.
    cx = sum(p[0] for p in q)/4; cy = sum(p[1] for p in q)/4
    grow = lambda p: (p[0] + 2*(1 if p[0] > cx else -1), p[1] + 2*(1 if p[1] > cy else -1))
    dst = [grow(p) for p in q]
    coeffs = perspective(dst, [(0, 0), (W, 0), (W, H), (0, H)])
    warped = canvas.convert('RGBA').transform(fg.size, Image.Transform.PERSPECTIVE, coeffs, Image.Resampling.BICUBIC, fillcolor=(0, 0, 0, 0))
    replace = score.point(lambda v: 255 if v >= FULL else 0 if v < SOFT else round(255*(v-SOFT)/(FULL-SOFT)))
    replace = ImageChops.multiply(replace, warped.getchannel('A'))
    rgb = Image.composite(warped.convert('RGB'), fg.convert('RGB'), replace)
    # Despill the thin ring around the screen (antialiased edges of hands / Yazai / frame).
    ring = ImageChops.subtract(replace.point(lambda v: 255 if v else 0).filter(ImageFilter.MaxFilter(9)), replace.point(lambda v: 255 if v >= 250 else 0))
    r, g, b = rgb.split()
    spill = key_score(rgb)
    clean = Image.merge('RGB', [ImageChops.subtract(r, spill), g, ImageChops.subtract(b, spill)])
    rgb = Image.composite(clean, rgb, ring)
    left = key_score(rgb).point(lambda v: 1 if v >= SOFT else 0).histogram()[1]
    rgb.putalpha(fg.getchannel('A'))
    rgb.save(out)
    print(json.dumps({'corners': q, 'key_pixels': n, 'coverage': round(coverage, 3), 'fit': fit, 'magenta_left_px': left}, ensure_ascii=False))


if __name__ == '__main__':
    main(sys.argv[1:])
