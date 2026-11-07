from pathlib import Path
import importlib.util,json
src=Path('skills/jacky-cover/scripts/compose_interaction_cover.py')
spec=importlib.util.spec_from_file_location('cover',src);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
v=Path(__file__).resolve().parent;p=v.parents[1];t=v/'template'
m.build_template(root=t)
im,report,layers=m.render(v/'foreground-corrected.png',json.loads((v/'text.json').read_text()),root=t)
out=p/'输出版本/v4修正版'
m.save_result(im,report,layers,out/'告别写报告-Opus55接管比赛.png',out/'render-report.json',out/'layers')
assert report['title_line_gap_px']==38
assert report['title_font_sizes']==[177,109]
print(json.dumps({'gap_px':report['title_line_gap_px'],'title':report['title_runs'],'scene':report['scene'],'note':report['note']},ensure_ascii=False,indent=2))
