#!/usr/bin/env python3
"""Assemble the fixed 3:4 brand cover; never generate or retouch portraits."""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
import sys

try:
    from PIL import Image, ImageChops, ImageDraw, ImageOps
except ImportError:
    raise SystemExit('ERROR: Pillow is required. No package was installed; use an available Python/Pillow runtime.')

ROOT = Path(__file__).resolve().parents[1]
MASTER_SIZE = (2160, 2880)
OUTPUT_SIZE = (1245, 1660)
SAFE = (0.08, 0.12, 0.94, 0.89)
PROTECTED = (0.52, 0.58, 0.92, 0.88)


def rect(bounds: tuple[float, ...], size: tuple[int, int]) -> tuple[int, ...]:
    return tuple(round(v * size[i % 2]) for i, v in enumerate(bounds))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def open_image(path: Path, *, alpha: bool = False) -> Image.Image:
    require(path.is_file(), f'Missing asset: {path}')
    with Image.open(path) as raw:
        require(raw.format == 'PNG', f'Expected PNG: {path}')
        require(not getattr(raw, 'is_animated', False), 'Animated PNG is not a cover layer')
        if alpha:
            require('A' in raw.getbands() or 'transparency' in raw.info,
                    f'Layer needs an actual alpha channel: {path}')
        im = ImageOps.exif_transpose(raw).convert('RGBA')
        im.load()
    return im


def validate_transparency(im: Image.Image, name: str) -> Image.Image:
    alpha = im.getchannel('A')
    low, high = alpha.getextrema()
    require(low == 0 and high > 0, f'{name} must include transparent background and visible content')
    require(alpha.getbbox() is not None, f'{name} is empty')
    return alpha


def outside(alpha: Image.Image, bounds: tuple[float, ...]) -> Image.Image:
    allowed = Image.new('L', alpha.size)
    x0, y0, x1, y1 = rect(bounds, alpha.size)
    ImageDraw.Draw(allowed).rectangle((x0, y0, x1 - 1, y1 - 1), fill=255)
    return ImageChops.multiply(alpha, ImageChops.invert(allowed))


def content_checks(im: Image.Image) -> None:
    alpha = validate_transparency(im, 'Content')
    require(im.width * 4 == im.height * 3, 'Content aspect ratio must be exactly 3:4; no stretching/cropping')
    require(not outside(alpha, SAFE).getbbox(), 'Content exceeds the fixed frame safe area')
    require(not alpha.crop(rect(PROTECTED, im.size)).getbbox(),
            'Content overlaps the portrait protected area; rearrange the content layer')
    histogram = alpha.histogram()
    visible = sum(histogram[1:]) / (im.width * im.height)
    require(visible < 0.70, 'Content is almost a full background; provide a genuine transparent artwork layer')


def max_difference(a: Image.Image, b: Image.Image, mask: Image.Image) -> int:
    diff = ImageChops.difference(a.convert('RGB'), b.convert('RGB'))
    return max(ImageChops.multiply(channel, mask).getextrema()[1] for channel in diff.split())


def png_bytes(im: Image.Image) -> bytes:
    buf = io.BytesIO()
    im.save(buf, format='PNG')
    return buf.getvalue()


def compose(args: argparse.Namespace) -> dict:
    base_path = ROOT / 'assets/covers/clean-window-3x4-v1.png'
    content_path = Path(args.content).expanduser().resolve()
    require(args.portrait_mode != 'cutout' or bool(args.portrait),
            'Cutout mode requires --portrait with an approved transparent cutout; no automatic substitution')
    require(args.portrait_mode != 'window' or not args.portrait,
            'Window mode uses the fixed original portrait; use cutout mode for an approved replacement')
    portrait_path = (Path(args.portrait).expanduser().resolve() if args.portrait
                     else ROOT / 'assets/ip/jacky-portrait-window-v1.png')
    inputs = {base_path.resolve(), content_path, portrait_path.resolve()}
    targets = {k: Path(v).expanduser().resolve() for k in ('output', 'master', 'thumbnail', 'report')
               if (v := getattr(args, k))}
    require(len(set(targets.values())) == len(targets), 'Output paths must be distinct')
    for path in targets.values():
        require(path not in inputs, 'An output cannot overwrite an input asset')
        require(not path.exists(), f'Output exists; choose a new version: {path}')
    for key, path in targets.items():
        require(path.suffix.lower() == ('.json' if key == 'report' else '.png'),
                f'{key} has the wrong file extension')

    base = open_image(base_path)
    require(base.size == MASTER_SIZE, 'Fixed base has an unexpected size')
    require(base.getchannel('A').getextrema() == (255, 255), 'Fixed base must be opaque')
    content = open_image(content_path, alpha=True)
    content_checks(content)
    original_content_size = content.size
    if content.size != MASTER_SIZE:
        content = content.resize(MASTER_SIZE, Image.Resampling.LANCZOS)
        # Resampling can spread boundary alpha. Validate at the actual composition resolution too.
        content_checks(content)

    portrait = open_image(portrait_path, alpha=True)
    require(portrait.size == MASTER_SIZE, 'Portrait must be a pre-positioned 2160x2880 transparent layer')
    pa = validate_transparency(portrait, 'Portrait')
    require(not outside(pa, PROTECTED).getbbox(), 'Portrait leaves the reserved area; approve a new template first')
    opaque = pa.point(lambda value: 255 if value == 255 else 0)
    require(opaque.getbbox() is not None, 'Portrait has no fully opaque pixels to verify')

    master = Image.alpha_composite(Image.alpha_composite(base, content), portrait)
    portrait_error = max_difference(master, portrait, opaque)
    require(portrait_error == 0, 'Portrait fidelity check failed')
    used = ImageChops.lighter(content.getchannel('A'), pa)
    untouched = used.point(lambda value: 255 if value == 0 else 0)
    base_error = max_difference(master, base, untouched)
    require(base_error == 0, 'Fixed background fidelity check failed')

    encoded_master = png_bytes(master)
    with Image.open(io.BytesIO(encoded_master)) as decoded:
        require(max_difference(decoded, portrait, opaque) == 0, 'Saved PNG portrait fidelity check failed')

    final = master.resize(OUTPUT_SIZE, Image.Resampling.LANCZOS).convert('RGB')
    report = {
        'template': 'clean-window-3x4-v1',
        'portrait_mode': args.portrait_mode,
        'content_source_size': list(original_content_size),
        'master_size': list(MASTER_SIZE),
        'output_size': list(OUTPUT_SIZE),
        'content_upscaled_to_master': original_content_size[0] < MASTER_SIZE[0],
        'content_upscaled_to_output': original_content_size[0] < OUTPUT_SIZE[0],
        'portrait_resampled_in_master': False,
        'portrait_opaque_pixels_verified': opaque.histogram()[255],
        'portrait_max_channel_difference': portrait_error,
        'untouched_background_max_channel_difference': base_error,
        'protected_area_clear': True,
        'visual_review_required': ['exact text and meaning', 'title in upper third',
                                   'Yazai identity, action and prominence', 'face clarity',
                                   'clean background and whitespace', '270x360 thumbnail'],
        'note': 'Master portrait opaque pixels are exact. Publication output is normally downsampled; upscaling adds no source detail.',
    }
    payloads = {'output': png_bytes(final), 'master': encoded_master,
                'thumbnail': png_bytes(final.resize((270, 360), Image.Resampling.LANCZOS)),
                'report': (json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode()}
    created = []
    try:
        for key, path in targets.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as handle:
                created.append(path)
                handle.write(payloads[key])
    except Exception:
        for path in created:
            path.unlink(missing_ok=True)
        raise
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--content', required=True, help='Full-canvas transparent 3:4 PNG of title and illustration')
    parser.add_argument('--output', required=True, help='New 1245x1660 PNG path')
    parser.add_argument('--master', help='Optional new 2160x2880 PNG path')
    parser.add_argument('--thumbnail', help='Optional new 270x360 PNG path')
    parser.add_argument('--report', help='Optional new JSON verification report')
    parser.add_argument('--portrait-mode', choices=('window', 'cutout'), default='window')
    parser.add_argument('--portrait', help='Approved cutout, pre-positioned on a transparent 2160x2880 canvas')
    args = parser.parse_args()
    try:
        report = compose(args)
    except (OSError, ValueError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
