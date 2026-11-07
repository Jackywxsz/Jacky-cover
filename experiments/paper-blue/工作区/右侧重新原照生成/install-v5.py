from pathlib import Path
import hashlib,json,tarfile,shutil
p=Path('experiments/paper-blue');w=p/'工作区/右侧重新原照生成';stage=w/'skill';target=Path('skills/jacky-cover')
h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();before=json.loads((w/'preinstall-hashes.json').read_text())
assert {str(f.relative_to(target)):h(f) for f in target.rglob('*') if f.is_file()}==before,'Source drift'
archive=p/'工作区/旧版备份/jacky-cover-before-original-only-v5.tar.gz';assert not archive.exists()
with tarfile.open(archive,'w:gz') as tar:tar.add(target,arcname='jacky-cover')
with tarfile.open(archive) as tar:
 verified={m.name.removeprefix('jacky-cover/'):hashlib.sha256(tar.extractfile(m).read()).hexdigest() for m in tar.getmembers() if m.isfile()}
assert verified==before
for f in stage.rglob('*'):
 if f.is_file() and '__pycache__' not in f.parts:
  dest=target/f.relative_to(stage);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
(target/'assets/covers/template-manifest-v4.json').unlink()
installed={str(f.relative_to(stage)):h(target/f.relative_to(stage)) for f in stage.rglob('*') if f.is_file() and '__pycache__' not in f.parts}
assert all(h(stage/rel)==sha for rel,sha in installed.items())
for rel in ['assets/covers/paper-blue-interaction-v4.png','assets/covers/black-gradient-v4.png']:
 assert h(target/rel)==before[rel]
(w/'installation-report.json').write_text(json.dumps({'active_template':'v5','backup':str(archive),'backup_sha256':h(archive),'installed_files':installed,'background_and_mask':'byte-identical to v4','original_photos':'unchanged'},ensure_ascii=False,indent=2))
print('v5 installed; original-only portrait rule, proportions and exact per-line typography active; fixed background/mask unchanged.')
