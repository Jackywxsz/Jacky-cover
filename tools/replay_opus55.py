#!/usr/bin/env python3
"""Replay rejected v5 deterministically. No generation, no mutation of source assets."""
import argparse,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
if a.output.exists():p.error('Output already exists; choose a new directory')
skill=ROOT/'skills/jacky-cover'
spec=importlib.util.spec_from_file_location('cover',skill/'scripts/compose_interaction_cover.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
v=ROOT/'experiments/opus55/工作区/v5动作约束修复'
fonts=skill/'assets/fonts'
image,report,layers=m.render(v/'foreground.png',json.loads((v/'text.json').read_text()),font=fonts/'Alibaba-PuHuiTi-Bold.ttf',note_font=fonts/'字体传奇南安体-免费商用.ttf',root=v/'template')
for key in ('font_file',):
 if key in report:report[key]=str(Path(report[key]).relative_to(ROOT))
if report.get('note'):report['note']['font_file']=str(Path(report['note']['font_file']).relative_to(ROOT))
report['user_acceptance']='rejected; technical replay only'
m.save_result(image,report,layers,a.output/'cover.png',a.output/'render-report.json',a.output/'layers')
print(json.dumps({'output':str(a.output),'size':image.size,'line_gap_px':report['title_line_gap_px'],'status':'replayed_user_rejected_v5'},ensure_ascii=False))
