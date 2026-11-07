from pathlib import Path
import hashlib,json,tarfile,shutil
p=Path('experiments/paper-blue');s=p/'工作区/动作库与自然渐变v4/skill';dest=Path('skills/jacky-cover')
h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
prev=json.loads((p/'工作区/参考底图修订v3/installation-report.json').read_text())['installed_files']
assert all(h(dest/r)==v for r,v in prev.items()),'Active Skill drift: stop'
b=p/'工作区/旧版备份/jacky-cover-template-v3-before-pose-library.tar.gz';assert not b.exists()
before={str(f.relative_to(dest)):h(f) for f in dest.rglob('*') if f.is_file()}
with tarfile.open(b,'w:gz') as tar:tar.add(dest,arcname='jacky-cover')
with tarfile.open(b) as tar:
    verified={m.name.removeprefix('jacky-cover/'):hashlib.sha256(tar.extractfile(m).read()).hexdigest() for m in tar.getmembers() if m.isfile()}
assert verified==before
for f in s.rglob('*'):
    if f.is_file() and '__pycache__' not in f.parts:
        target=dest/f.relative_to(s);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,target)
for rel in ['assets/covers/paper-blue-interaction-v3.png','assets/covers/black-gradient-v3.png','assets/covers/template-manifest-v3.json']:(dest/rel).unlink()
installed={str(f.relative_to(s)):h(dest/f.relative_to(s)) for f in s.rglob('*') if f.is_file() and '__pycache__' not in f.parts}
assert all(h(s/r)==v for r,v in installed.items())
r={'active_template':'v4','backup':str(b),'backup_sha256':h(b),'backup_files_verified':len(before),'installed_files':installed,'original_photos_unchanged':all(h(dest/r)==v for r,v in before.items() if r.startswith('assets/jacky-reference-'))}
(p/'工作区/动作库与自然渐变v4/installation-report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
print('v3 fully backed up; v4 installed as sole active template; original photos unchanged.')
