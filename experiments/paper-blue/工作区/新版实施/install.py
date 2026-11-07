from pathlib import Path
import hashlib,json,tarfile,shutil,datetime
project=Path('experiments/paper-blue')
work=project/'工作区/新版实施';stage=work/'skill';target=Path('skills/jacky-cover')
hashfile=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
expected=json.loads((work/'preinstall-hashes.json').read_text())
actual={str(f.relative_to(target)):hashfile(f) for f in target.rglob('*') if f.is_file()}
assert actual==expected,'Source drift: stop before backup/install'
backup=project/'工作区/旧版备份';backup.mkdir(exist_ok=True)
archive=backup/'jacky-cover-legacy-before-template-v1.tar.gz'
assert not archive.exists(),'Backup already exists; do not overwrite'
with tarfile.open(archive,'w:gz') as tar:tar.add(target,arcname='jacky-cover',recursive=True)
with tarfile.open(archive) as tar:
    archived={m.name.removeprefix('jacky-cover/'):hashlib.sha256(tar.extractfile(m).read()).hexdigest() for m in tar.getmembers() if m.isfile()}
assert archived==actual,'Archive verification failed'
(backup/'backup-manifest.json').write_text(json.dumps({'archive':archive.name,'archive_sha256':hashfile(archive),'files':actual},indent=2))
(backup/'恢复说明.md').write_text('''# 旧版已封存\n此压缩包是完整安装前快照，逐文件SHA256已核验。它不在Skill发现目录中，不自动加载、不作为失败回退。\n恢复仅在用户明确要求时执行：先备份届时活动版本，再解压本包到临时目录，比较manifest和当前文件，替换真实源目录。不要在skills目录中同时保留两个带SKILL.md的可发现版本。\n当前唯一入口：skills/jacky-cover/SKILL.md。Codex同名入口是符号链接。\n''')
for f in stage.rglob('*'):
    if f.is_file() and '__pycache__' not in f.parts:
        dest=target/f.relative_to(stage);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
removed=[]
for rel in ['scripts/validate_run.py','tests/test_validate_run.py']:
    path=target/rel
    if path.exists():path.unlink();removed.append(rel)
for path in (target/'tests').glob('__pycache__/test_validate_run.*.pyc'):
    removed.append(str(path.relative_to(target)));path.unlink()
installed={str(f.relative_to(stage)):hashfile(target/f.relative_to(stage)) for f in stage.rglob('*') if f.is_file() and '__pycache__' not in f.parts}
assert all(hashfile(stage/rel)==h for rel,h in installed.items())
assert all(hashfile(target/rel)==h for rel,h in expected.items() if rel.startswith('assets/jacky-reference-'))
record={'installed_at':datetime.datetime.now().isoformat(),'target':str(target),'backup':str(archive),'installed_files':installed,'removed_legacy_files':removed,'original_photos':'hashes unchanged','alias_resolves_to':str(Path('skills/jacky-cover').resolve())}
(work/'installation-report.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
print(json.dumps(record,ensure_ascii=False,indent=2))
