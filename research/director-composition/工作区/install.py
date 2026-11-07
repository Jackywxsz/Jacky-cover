from pathlib import Path
import json,hashlib,shutil,subprocess,re
root=Path('skills/jacky-cover')
p=Path('research/director-composition');work=p/'工作区';stage=work/'proposed'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
before=json.loads((work/'preinstall-hashes.json').read_text())
changed=['SKILL.md','references/visual-system.md','references/pose-library.md']
added=['references/scene-direction.md','references/gbro-license.txt']
for n,h in before.items():
 assert sha(root/n)==h, 'Concurrent change: '+n
for n in added:assert not (root/n).exists(),'New file already exists: '+n
# Verify all relative document/asset links in the proposed source against the proposed or existing tree.
links=[]
for n in changed+added:
 if not n.endswith('.md'):continue
 content=(stage/n).read_text()
 for target in re.findall(r'\]\(([^)]+)\)',content):
  if '://' in target or target.startswith('#'):continue
  target=target.split('#')[0]
  local=(Path(n).parent/target)
  assert (stage/local).exists() or (root/local).exists(),f'Broken reference: {n} -> {target}'
  links.append({'from':n,'to':target})
for n in changed+added:
 (root/n).parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(stage/n,root/n)
 assert sha(root/n)==sha(stage/n)
for n,h in before.items():
 if n not in changed:assert sha(root/n)==h,'Unexpected runtime/asset change: '+n
assert Path('skills/jacky-cover').resolve()==root
v=subprocess.run(['python3','<LOCAL_CODEX>/skills/.system/skill-creator/scripts/quick_validate.py',str(root)],capture_output=True,text=True)
(work/'skill-validation.txt').write_text(v.stdout+v.stderr)
assert v.returncode==0,v.stdout+v.stderr
report={'status':'passed','active_source':str(root),'modified':{n:sha(root/n) for n in changed},'added':{n:sha(root/n) for n in added},'unchanged':{n:h for n,h in before.items() if n not in changed},'relative_links':links,'skill_structure_validation':v.stdout.strip(),'behavior_walkthrough':'行为走查.md','new_image_calls':0,'new_services':0,'new_active_skill_entries':0,'visual_generation_validation':'not performed; future generated output still needs user review'}
(work/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(work/'验收记录.md').write_text('''# 导演构图Skill安装验收

已安装到唯一源 skills/jacky-cover；Codex入口仍为原符号链接。修改3份文档，新增导演参考与来源许可；修改前文档保存在本项目工作区/before，未生成第二套可发现Skill。

已通过官方quick_validate（Skill is valid!）、所有修改文档的本地引用目标检查、安装后字节校验；配置、合成脚本、固定纸蓝底、黑蒙版及两张原始身份照hash保持不变。新导演参考由主入口与动作库可达，并接到视觉验收。

完成6种输入情境的文档走查，覆盖报告、Bot军团、只改字、外部风格冲突、语义信息不足和生图语义失败。详见行为走查.md。旧动作库中带“本轮”字样的过时示例已改为历史命题说明。

本轮无生图、无外部发布、无新增服务；未重复运行图像合成回归（脚本和模板未变）。文档检查不等于图片质量通过，导演稿需在下次实际生成后对照无字图、成图和缩略图验收。当前报告封面仍待用户认可。

回退范围仅为本次3份改动文档与2份新增参考：用before中原文档恢复，移出新增scene-direction.md及gbro-license.txt；不触碰品牌资产、配置、脚本或现有成图。执行回退前先检查后续修改，避免覆盖其他任务。
''')
(p/'manifest.json').write_text(json.dumps({'status':'skill_update_complete','active_skill':str(root/'SKILL.md'),'scope':'导演构图方法吸收','research':'输出版本/研究与吸收说明.md','sources':'输入资料/sources.json','evidence':'工作区/verification.json','accepted_brand_assets_unchanged':True,'new_image_calls':0,'image_quality_claim':'not tested by this documentation update'},ensure_ascii=False,indent=2)+'\n')
print(v.stdout.strip());print('PASS: 3 documents updated, 2 references added; links checked; fixed assets and runtime unchanged.')
