#!/usr/bin/env python3
"""Fixed-background cover compositor. No generative face edits or scene cropping."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat

ROOT = Path(__file__).resolve().parents[1]
PROFILE = 'references/interaction-profile.json'
BASE = 'assets/covers/paper-blue-interaction-v4.png'
MASK = 'assets/covers/black-gradient-v7.png'
MANIFEST = 'assets/covers/template-manifest-v7.json'


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
    g = p['black_gradient']
    require(g['interpolation']=='smoothstep' and 0<=g['start_y']<g['end_y']<=1
            and 0<g['max_alpha']<1, 'Invalid continuous gradient')
    return p, raw


def rgb(value):
    return tuple(bytes.fromhex(value.lstrip('#')))


def alpha_rows(p):
    h = p['size'][1]
    g = p['black_gradient']
    values=[]
    for row in range(h):
        t=max(0,min(1,(row/(h-1)-g['start_y'])/(g['end_y']-g['start_y'])))
        values.append(round(255*g['max_alpha']*t*t*(3-2*t)))
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


def shown(path):
    # Reports never carry local machine paths: repo files are repo-relative, others keep only the file name.
    path = Path(path).resolve()
    repo = ROOT.parents[1]
    return str(path.relative_to(repo)) if path.is_relative_to(repo) else path.name


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


def place_scene(path, p, anchor_cut=False):
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
    # Detect an exposed torso cut; only when the caller asks (nothing in the scene hides it)
    # is the cut anchored low behind the title shadow.
    # Detected by shape: the lowest rows of the subject form a wide flat opaque cut.
    # Faint generator haze is ignored when locating the real lower edge.
    solid = a.point(lambda v: 255 if v > 40 else 0).getbbox()
    def opaque_width(dy):
        return a.crop((solid[0], solid[3]-dy, solid[2], solid[3]-dy+1)).point(lambda v: 1 if v > 200 else 0).histogram()[1]
    # A torso cut keeps nearly vertical sides down to the edge; rounded objects narrow toward their bottom.
    near, higher = opaque_width(20), opaque_width(40)
    body_cut = near >= 0.15*(solid[2]-solid[0]) and near >= 0.85*higher
    anchored = body_cut and anchor_cut
    if anchored:
        y1 = round(h*p['body_cut_anchor_y'])
    scale = min((x1-x0)/subject.width, (y1-y0)/subject.height)
    size = (max(1, round(subject.width*scale)), max(1, round(subject.height*scale)))
    resized = subject.resize(size, Image.Resampling.LANCZOS)
    xy = (x0+((x1-x0)-size[0])//2, y1-size[1] if anchored else y0)
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
                   'bottom_dissolve_y': [fade_start,fade_end], 'body_cut_detected': body_cut, 'body_cut_anchored': anchored,
                   'transform': 'uniform whole-scene fit; bottom alpha dissolve into title shadow; no RGB/face edits'}



def render(scene_path, text, font=None, note_font=None, root=ROOT):
    p, base, mask, manifest = load_template(root)
    scene_path = Path(scene_path).expanduser().resolve()
    scene, placement = place_scene(scene_path, p, anchor_cut=text.get('hide_cut_behind_title', False))
    lines = text.get('lines', [])
    require(len(lines)==2, 'Exactly two title lines are required')
    for line in lines:
        require(isinstance(line.get('text'),str) and line['text'].strip(), 'Empty title line')
        require('\n' not in line['text'], 'Title line contains newline')
        emphasis = line.get('emphasis')
        require(not emphasis or line['text'].count(emphasis)==1, 'Emphasis must occur exactly once')
    fp = font_file(p['title'], font)
    w,h = p['size']
    t = p['title']
    left, right = round(w*t['left']), round(w*t['right'])
    def fill_size(s):
        # Largest size whose real advance width fits the safe width.
        size=t['max_auto_size']
        while size>=t['min_size'] and ImageFont.truetype(str(fp),size).getlength(s)>right-left:
            size-=1
        require(size>=t['min_size'],'Title too long; do not squeeze glyphs')
        return size
    # Line 2 (usually longer) fills the safe width; line 1 is one step larger (two when it is short), never wider than the safe width.
    line2_size=fill_size(lines[1]['text'])
    line1_units=sum(1 if ord(ch)>0x2e80 else .5 for ch in lines[0]['text'] if not ch.isspace())
    line1_ratio=t['line1_ratio_short'] if line1_units<=t['short_line1_units'] else t['line1_ratio']
    sizes=[]
    for row, line in enumerate(lines):
        if 'size' in line:
            require(isinstance(line['size'],int) and t['min_size']<=line['size']<=t['max_override_size'], 'Requested title size outside range')
            require(ImageFont.truetype(str(fp),line['size']).getlength(line['text'])<=right-left,'Requested title size overflows; do not stretch or silently reflow')
            sizes.append(line['size'])
        elif row==0:
            sizes.append(min(fill_size(line['text']),round(line2_size*line1_ratio)))
        else:
            sizes.append(line2_size)
    def ink_boxes(sizes):
        probe=ImageDraw.Draw(Image.new('L',(1,1)))
        return [probe.textbbox((0,0),line['text'],font=ImageFont.truetype(str(fp),s),anchor='ls') for line,s in zip(lines,sizes)]
    region_top=round(h*t['region_top'])+t['top_pad']
    def block_metrics(sizes):
        widths=[ImageFont.truetype(str(fp),s).getlength(line['text']) for line,s in zip(lines,sizes)]
        side=round((w-max(widths))/2)
        # Bottom margin is a fixed multiple of the side margin, so the block sits in proportion to its width.
        return widths, side, h-round(side*t['bottom_margin_ratio'])
    # Auto-sized lines shrink together until the block fits the bottom-third safe area.
    while True:
        boxes=ink_boxes(sizes)
        widths, block_x, bottom = block_metrics(sizes)
        if sum(b[3]-b[1] for b in boxes)+t['line_gap']<=bottom-region_top: break
        auto=[i for i,line in enumerate(lines) if 'size' not in line and sizes[i]>t['min_size']]
        require(auto,'Title block too tall for the title region')
        for i in auto: sizes[i]-=1
    ink=Image.new('RGBA',(w,h))
    draw=ImageDraw.Draw(ink)
    title_boxes=[]
    title_runs=[]
    # Stack from the bottom safe line upward: line 2 sits on `bottom`, line 1 sits line_gap above it.
    baselines=[0,0]
    baselines[1]=bottom-boxes[1][3]
    baselines[0]=baselines[1]+boxes[1][1]-t['line_gap']-boxes[0][3]
    # Lines share one left edge (block_x); the block as a whole is centered horizontally.
    for row, line in enumerate(lines):
        ft=ImageFont.truetype(str(fp),sizes[row])
        x=block_x
        baseline=baselines[row]
        box=draw.textbbox((x,baseline),line['text'],font=ft,anchor='ls')
        require(box[0]>=left-1 and box[2]<=right+1 and box[3]<=bottom+1 and box[1]>=region_top-1, 'Title overflow')
        if title_boxes:
            require(box[1]>=title_boxes[-1][3]+t['min_line_gap'],'Title lines collide')
        e=line.get('emphasis')
        if e:
            before,after=line['text'].split(e)
            for fragment,offset,color in [(before,0,'white'),(e,ft.getlength(before),'orange'),(after,ft.getlength(before+e),'white')]:
                if fragment: draw.text((x+offset,baseline),fragment,font=ft,fill=p['colors'][color],anchor='ls')
        else:
            draw.text((x,baseline),line['text'],font=ft,fill=p['colors']['white'],anchor='ls')
        title_boxes.append(list(box))
        title_runs.append({'text':line['text'],'emphasis':line.get('emphasis'),'size':sizes[row],'bbox':list(box)})
    title_sizes=sizes
    size=max(sizes)
    pre_mask=Image.alpha_composite(base,scene)
    under_text=Image.alpha_composite(pre_mask,mask)
    note_info=None
    if text.get('note'):
        note=text['note'];nf=font_file(p['note'],note_font)
        ns=note.get('size',34)
        require(p['note']['min_size']<=ns<=p['note']['max_size'],'Handwritten note size outside profile')
        require(isinstance(note.get('text'),str) and note['text'].strip() and '\n' not in note['text'],'Invalid note')
        xy=note.get('xy');require(isinstance(xy,list) and len(xy)==2,'Note needs normalized xy')
        ft_note=ImageFont.truetype(str(nf),ns)
        # x may be "title_left" to align the note with the title block's left edge.
        nx=min(b[0] for b in title_boxes) if xy[0]=='title_left' else round(xy[0]*w)
        pos=(nx,round(xy[1]*h))
        nb=draw.textbbox(pos,note['text'],font=ft_note,anchor='lt')
        require(nb[0]>=round(.05*w) and nb[2]<=round(.95*w) and nb[1]>=0 and nb[3]<title_boxes[0][1]-16,'Note outside safe gap')
        # Ignore only <=2/255 invisible alpha dust from the generated cutout; preserve all source pixels.
        require(scene.getchannel('A').crop(nb).getextrema()[1]<=2,'Note overlaps foreground; choose actual negative space')
        # Dark ink on light paper; white once the note sits over the darkening gradient.
        lum=ImageStat.Stat(under_text.convert('L').crop(nb)).mean[0]
        note_color=p['colors']['ink'] if lum>=140 else p['colors']['white']
        draw.text(pos,note['text'],font=ft_note,fill=note_color,anchor='lt')
        note_info={'font_file':shown(nf),'font_sha256':digest(nf.read_bytes()),'family_style':ft_note.getname(),'size':ns,'bbox':list(nb),'color':note_color}
    final=Image.alpha_composite(under_text,ink)
    report={'template_id':p['template_id'],'size':[w,h],'profile_sha256':manifest['profile_sha256'],
            'template_files':manifest['files'],'scene_file':shown(scene_path),'scene_sha256':digest(scene_path.read_bytes()),
            'scene':placement,'black_gradient':p['black_gradient'],
            'alpha_8bit_samples':[mask.getpixel((0,round(y*(h-1))))[3] for y in p['black_gradient']['sample_y']],
            'font_file':shown(fp),'font_sha256':digest(fp.read_bytes()),'font_family_style':ft.getname(),
            'font_size':size,'title_font_sizes':title_sizes,'title_runs':title_runs,'title_boxes':title_boxes,'title_region_bbox':[0,round(h*p['title']['region_top']),w,h],'title_line_gap_px':title_boxes[1][1]-title_boxes[0][3],'note':note_info,
            'self_check':'technical_checks_passed_visual_review_required','user_acceptance':'not_claimed',
            'visual_review_required':['original-photo likeness and skin','body orientation consistent and arms connected','Yazai identity as 3D figure','semantic relationship','overall reference family and phone thumbnail']}
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
