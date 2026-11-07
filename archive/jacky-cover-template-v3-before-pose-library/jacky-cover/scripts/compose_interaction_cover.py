#!/usr/bin/env python3
"""Fixed-background cover compositor. No generative face edits or scene cropping."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PROFILE = 'references/interaction-profile.json'
BASE = 'assets/covers/paper-blue-interaction-v3.png'
MASK = 'assets/covers/black-gradient-v3.png'
MANIFEST = 'assets/covers/template-manifest-v3.json'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def png(im):
    buffer = io.BytesIO()
    im.save(buffer, format='PNG')
    return buffer.getvalue()


def profile(root=ROOT):
    raw = (root / PROFILE).read_bytes()
    p = json.loads(raw)
    require(p['size'] == [1080, 1440], 'Unsupported template size/version')
    stops = p['black_alpha_stops']
    require(stops == [[0.0, 0.0], [0.45, 0.0], [0.60, 0.08], [0.68, 0.25], [0.77, 0.85], [1.0, 0.95]],
            'Unexpected gradient profile; use a new version for a changed template')
    return p, raw


def rgb(value):
    return tuple(bytes.fromhex(value.lstrip('#')))


def alpha_rows(p):
    h = p['size'][1]
    stops = p['black_alpha_stops']
    values = []
    for row in range(h):
        y = row / (h - 1)
        for (y0, a0), (y1, a1) in zip(stops, stops[1:]):
            if y <= y1:
                values.append(round(255 * (a0 + (a1 - a0) * (y - y0) / (y1 - y0))))
                break
    return values


def make_template(p, root=ROOT):
    w, h = p['size']
    asset = root/p['background']['asset']
    require(digest(asset.read_bytes()) == p['background']['sha256'], 'Reference background changed')
    with Image.open(asset) as source:
        require(source.size == (w,h), 'Fixed background dimensions differ')
        base = source.convert('RGBA')
    alpha = Image.frombytes('L', (w, h), b''.join(bytes([v])*w for v in alpha_rows(p)))
    mask = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    mask.putalpha(alpha)
    return base, mask


def build_template(root=ROOT):
    p, raw = profile(root)
    base, mask = make_template(p, root)
    payloads = {BASE: png(base), MASK: png(mask)}
    record = {'template_id': p['template_id'], 'profile_sha256': digest(raw),
              'files': {k: digest(v) for k, v in payloads.items()}}
    payloads[MANIFEST] = (json.dumps(record, indent=2)+'\n').encode()
    # Compare every existing file before writing anything; no silent replacement.
    for rel, data in payloads.items():
        path = root / rel
        require(not path.exists() or path.read_bytes() == data,
                f'Template differs: {rel}; do not overwrite an active template')
    for rel, data in payloads.items():
        path = root / rel
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as handle:
                handle.write(data)
    return record


def load_template(root=ROOT):
    p, raw = profile(root)
    m = json.loads((root / MANIFEST).read_text())
    require(m['profile_sha256'] == digest(raw), 'Template profile/hash mismatch')
    for rel in (BASE, MASK):
        require(digest((root / rel).read_bytes()) == m['files'][rel], f'Template asset/hash mismatch: {rel}')
    base, mask = [Image.open(root / rel).convert('RGBA') for rel in (BASE, MASK)]
    require(base.size == mask.size == tuple(p['size']), 'Template dimensions differ')
    require(base.getchannel('A').getextrema() == (255, 255), 'Background must be opaque')
    require(all(c.getextrema() == (0, 0) for c in mask.split()[:3]), 'Mask must be pure black')
    expected = b''.join(bytes([v])*base.width for v in alpha_rows(p))
    require(mask.getchannel('A').tobytes() == expected, 'Actual alpha curve differs from profile')
    return p, base, mask, m


def font_file(spec, override=None):
    candidates = [Path(override).expanduser()] if override else [
        Path.home()/'Library/Fonts'/spec['filename'],
        Path('/Library/Fonts')/spec['filename'],
        ROOT/'assets/fonts'/spec['filename']]
    found = next((p for p in candidates if p.is_file()), None)
    require(found is not None, f'Missing real font: {spec["filename"]}; no substitution')
    f = ImageFont.truetype(str(found), 32)
    require(f.getname() == (spec['family'], spec['style']), f'Font identity mismatch: {f.getname()}')
    return found.resolve()


def place_scene(path, p):
    with Image.open(path) as source:
        require(source.format == 'PNG' and 'A' in source.getbands(), 'Scene must be a PNG with real alpha')
        require(not getattr(source, 'is_animated', False), 'Animated scene is unsupported')
        im = source.convert('RGBA')
    a = im.getchannel('A')
    require(a.getextrema() == (0, 255), 'Scene needs transparent background and opaque subjects')
    visible = sum(a.histogram()[1:])/(im.width*im.height)
    require(visible < 0.85, 'Scene is almost a full background; no white/chessboard substitute')
    bbox = a.getbbox()
    require(bbox is not None, 'Scene is empty')
    subject = im.crop(bbox)
    w, h = p['size']
    x0, y0, x1, y1 = [round(v*(w if i%2==0 else h)) for i,v in enumerate(p['scene_box'])]
    scale = min((x1-x0)/subject.width, (y1-y0)/subject.height)
    size = (max(1, round(subject.width*scale)), max(1, round(subject.height*scale)))
    resized = subject.resize(size, Image.Resampling.LANCZOS)
    xy = (x0+((x1-x0)-size[0])//2, y0)
    layer = Image.new('RGBA', (w,h))
    layer.alpha_composite(resized, xy)
    box = layer.getchannel('A').getbbox()
    require(box[0]>=x0 and box[1]>=y0 and box[2]<=x1 and box[3]<=y1, 'Scene exceeds fixed safe area')
    # Only dissolve the lower cutoff into the title shadow; never stretch pixels.
    fade_height = p['scene_bottom_fade_px']
    fade_end = box[3]
    fade_start = max(box[1], fade_end-fade_height)
    dissolve = Image.new('L',(w,h),255)
    dd = ImageDraw.Draw(dissolve)
    for y in range(fade_start, fade_end):
        v = (y-fade_start)/max(1,fade_end-fade_start-1)
        dd.line((0,y,w-1,y),fill=round(255*(1-v*v*(3-2*v))))
    layer.putalpha(ImageChops.multiply(layer.getchannel('A'),dissolve))
    return layer, {'source_size': list(im.size), 'source_alpha_bbox': list(bbox),
                   'placed_bbox_before_dissolve': list(box), 'placed_bbox': list(layer.getchannel('A').getbbox()),
                   'scale': scale, 'source_upscaled': scale>1,
                   'bottom_dissolve_y': [fade_start,fade_end],
                   'transform': 'uniform whole-scene fit; bottom alpha dissolve into title shadow; no RGB/face edits'}



def render(scene_path, text, font=None, note_font=None, root=ROOT):
    p, base, mask, manifest = load_template(root)
    scene_path = Path(scene_path).expanduser().resolve()
    scene, placement = place_scene(scene_path, p)
    lines = text.get('lines', [])
    require(len(lines)==2, 'Exactly two title lines are required')
    for line in lines:
        require(isinstance(line.get('text'),str) and line['text'].strip(), 'Empty title line')
        require('\n' not in line['text'], 'Title line contains newline')
        emphasis = line.get('emphasis')
        require(not emphasis or line['text'].count(emphasis)==1, 'Emphasis must occur exactly once')
    fp = font_file(p['title'], font)
    w,h = p['size']
    left, right = round(w*p['title']['left']), round(w*p['title']['right'])
    size=p['title']['max_size']
    while size>=p['title']['min_size']:
        ft=ImageFont.truetype(str(fp),size)
        if max(ft.getlength(line['text']) for line in lines)<=right-left:
            break
        size-=1
    require(size>=p['title']['min_size'],'Title too long; do not squeeze glyphs')
    ink=Image.new('RGBA',(w,h))
    draw=ImageDraw.Draw(ink)
    title_boxes=[]
    for row, line in enumerate(lines):
        y=round(p['title']['top'][row]*h)
        # One shared baseline keeps mixed-color fragments aligned.
        ascent,_=ft.getmetrics()
        baseline=y+ascent
        box=draw.textbbox((left,baseline),line['text'],font=ft,anchor='ls')
        # Convert requested visual top into a common baseline for this line.
        baseline+=y-box[1]
        box=draw.textbbox((left,baseline),line['text'],font=ft,anchor='ls')
        require(box[0]>=left-1 and box[2]<=right+1 and box[3]<=round(h*p['title']['bottom']), 'Title overflow')
        if title_boxes:
            require(box[1]>title_boxes[-1][3]+8,'Title lines collide')
        e=line.get('emphasis')
        if e:
            before,after=line['text'].split(e)
            for fragment,offset,color in [(before,0,'white'),(e,ft.getlength(before),'orange'),(after,ft.getlength(before+e),'white')]:
                if fragment: draw.text((left+offset,baseline),fragment,font=ft,fill=p['colors'][color],anchor='ls')
        else:
            draw.text((left,baseline),line['text'],font=ft,fill=p['colors']['white'],anchor='ls')
        title_boxes.append(list(box))
    note_info=None
    if text.get('note'):
        note=text['note'];nf=font_file(p['note'],note_font)
        ns=note.get('size',34)
        require(p['note']['min_size']<=ns<=p['note']['max_size'],'Handwritten note size outside profile')
        require(isinstance(note.get('text'),str) and note['text'].strip() and '\n' not in note['text'],'Invalid note')
        xy=note.get('xy');require(isinstance(xy,list) and len(xy)==2,'Note needs normalized xy')
        ft_note=ImageFont.truetype(str(nf),ns)
        pos=(round(xy[0]*w),round(xy[1]*h))
        nb=draw.textbbox(pos,note['text'],font=ft_note,anchor='lt')
        require(nb[0]>=round(.05*w) and nb[2]<=round(.95*w) and nb[1]>=0 and nb[3]<title_boxes[0][1]-16,'Note outside safe gap')
        require(scene.getchannel('A').crop(nb).getextrema()[1]==0,'Note overlaps foreground; choose actual negative space')
        draw.text(pos,note['text'],font=ft_note,fill=p['colors']['ink'],anchor='lt')
        note_info={'font_file':str(nf),'font_sha256':digest(nf.read_bytes()),'family_style':ft_note.getname(),'size':ns,'bbox':list(nb)}
    pre_mask=Image.alpha_composite(base,scene)
    under_text=Image.alpha_composite(pre_mask,mask)
    final=Image.alpha_composite(under_text,ink)
    report={'template_id':p['template_id'],'size':[w,h],'profile_sha256':manifest['profile_sha256'],
            'template_files':manifest['files'],'scene_file':str(scene_path),'scene_sha256':digest(scene_path.read_bytes()),
            'scene':placement,'alpha_stops':p['black_alpha_stops'],
            'alpha_8bit_samples':[mask.getpixel((0,round(y*(h-1))))[3] for y,_ in p['black_alpha_stops']],
            'font_file':str(fp),'font_sha256':digest(fp.read_bytes()),'font_family_style':ft.getname(),
            'font_size':size,'title_boxes':title_boxes,'note':note_info,
            'self_check':'technical_checks_passed_visual_review_required','user_acceptance':'not_claimed',
            'visual_review_required':['original-photo likeness and skin','both arms shoulder-elbow-wrist-hand before and after mask','Yazai identity AND paper-cut material','semantic relationship','overall reference family and phone thumbnail']}
    layers={'background.png':base,'foreground.png':scene,'black-mask.png':mask,'pre-mask.png':pre_mask,'text.png':ink}
    return final,report,layers


def save_result(image, report, layers, output, report_path, layers_dir=None):
    output,report_path=Path(output).resolve(),Path(report_path).resolve()
    require(output.suffix.lower()=='.png' and report_path.suffix.lower()=='.json','Output must be PNG; report must be JSON')
    payloads={output:png(image.convert('RGB')),report_path:(json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode()}
    require(output!=report_path,'Output paths collide')
    if layers_dir:
        ld=Path(layers_dir).resolve();require(not ld.exists(),'Layers directory exists; choose a new version')
        for name,im in layers.items():payloads[ld/name]=png(im)
        payloads[ld/'thumbnail.png']=png(image.resize((270,360),Image.Resampling.LANCZOS).convert('RGB'))
    require(all(not path.exists() for path in payloads),'An output exists; never overwrite')
    created=[]
    try:
        for path,data in payloads.items():
            path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('xb') as handle: handle.write(data)
            created.append(path)
    except Exception:
        for path in created:path.unlink()
        raise


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build-template',action='store_true')
    for name in ['scene','text','output','report','layers-dir','font','note-font']:ap.add_argument('--'+name)
    args=ap.parse_args()
    try:
        if args.build_template:
            require(not any([args.scene,args.text,args.output,args.report,args.layers_dir]),'Build does not accept run arguments')
            print(json.dumps(build_template(),indent=2));return 0
        require(all([args.scene,args.text,args.output,args.report]),'Require --scene --text --output --report')
        image,record,layers=render(args.scene,json.loads(Path(args.text).read_text()),args.font,args.note_font)
        save_result(image,record,layers,args.output,args.report,args.layers_dir)
        print(json.dumps(record,ensure_ascii=False,indent=2));return 0
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);return 2


if __name__=='__main__':raise SystemExit(main())
