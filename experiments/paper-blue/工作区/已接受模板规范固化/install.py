from pathlib import Path
import hashlib,json,shutil
root=Path('skills/jacky-cover')
project=Path('experiments/paper-blue')
stage=project/'工作区/已接受模板规范固化'
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=json.loads((stage/'preinstall-hashes.json').read_text())
for name,h in prior.items():
    assert hashfile(root/name)==h, f'Concurrent change: {name}'
profile=json.loads((root/'references/interaction-profile.json').read_text())
assert profile['template_id']=='jacky-paper-blue-interaction-v7'
assert profile['title']['region_top']==2/3
assert profile['black_gradient']['start_y']==.45
assert profile['black_gradient']['end_y']==.89
assert profile['black_gradient']['max_alpha']==.94
assert hashfile(root/profile['background']['asset'])==profile['background']['sha256']
assert hashfile(root/'assets/covers/black-gradient-v7.png')=='be25df27385227c654b5108f5e680a0a5f5dcf5fcf816793774fe9c92b9ef8f4'
unchanged=['references/interaction-profile.json','scripts/compose_interaction_cover.py','assets/covers/black-gradient-v7.png',profile['background']['asset']]
before={name:hashfile(root/name) for name in unchanged}
for name in prior:
    shutil.copy2(stage/'proposed'/name,root/name)
    assert hashfile(root/name)==hashfile(stage/'proposed'/name)
assert before=={name:hashfile(root/name) for name in unchanged}
assert (Path('skills/jacky-cover')).resolve()==root
m=json.loads((project/'manifest.final.json').read_text())
shutil.copy2(project/'manifest.final.json',stage/'manifest.before.json')
m.update(status='user_accepted_v7_preferences_documented',user_acceptance={'status':'accepted','scope':'当前右侧封面；不代表未来所有生成均已验收','evidence':'用户：这一张我先保存了；把这几次调整的偏好跟要求写进 Skill','date':'2026-11-07'},visual_limitations=['未来新生成人物、芽仔比例与内容隐喻仍须逐次独立验收'],preference_consolidation={'report':'工作区/已接受模板规范固化/验收记录.md','template_changed':False,'renderer_changed':False,'new_image_calls':0})
(project/'manifest.final.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
(stage/'verification.json').write_text(json.dumps({'status':'passed','installed_documents':{name:hashfile(root/name) for name in prior},'unchanged_runtime_and_assets':before,'single_skill_source':str(root),'user_accepted_image':m['current_trial'],'new_image_calls':0},ensure_ascii=False,indent=2)+'\n')
(stage/'验收记录.md').write_text('''# Jacky Cover｜固化已接受模板偏好

用户已接受当前右侧封面，原图保留在输出版本/右侧标题收紧与上部提亮/如何发挥-GrokBot最强实力.png。

本次仅更新真实 Skill 的 SKILL.md 与 references/visual-system.md：明确固定底图、底部1/3标题区、安全边距、v7连续黑蒙版、真实字体与颜色；明确标题按指定断行与内容长短选逐行字号，不固定200/110px或45px行距。小字放上部实际清晰留白。人物原照重生成、芽仔比例及身份验收规则继续生效。

已核对配置值、底图/蒙版hash、唯一入口符号链接以及安装后文档字节；配置、合成器、图像资产均未改动。本次无新生图，无新增排版系统，未重复运行此前已通过的13项图像测试。备份位于本目录before/，不处于技能发现目录，无第二个活动入口。

后续执行：读取真实Skill与visual-system → 用interaction-profile.json定位固定资产 → 按文案分行并写text.json（短行需放大时显式size）→ 唯一合成脚本 → 检查报告、全图与缩略图。既有图文局部调整复用已接受前景；生成新动作仍回原始身份照片。

完成边界：当前封面接受与本次规范固化已完成；未宣称未来生成的人脸保真、肢体或隐喻自动通过。详细机器核对见verification.json。
''')
print('PASS: installed 2 documents; runtime and template assets unchanged; acceptance recorded.')
