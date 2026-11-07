from pathlib import Path
import hashlib,json,shutil
p=Path(__file__).resolve().parent
root=Path('skills/jacky-cover')
expected=json.loads((p/'skill-before-hashes.json').read_text())
hashfile=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for name,h in expected.items():
    assert hashfile(root/name)==h, f'Concurrent change: {name}'
    assert hashfile(p/'skill-before'/name)==h
changes=[]
for name in expected:
    src=p/'skill-proposed'/name
    dst=root/name
    shutil.copy2(src,dst)
    assert hashfile(dst)==hashfile(src)
    changes.append({'path':str(dst),'before':expected[name],'after':hashfile(dst)})
(p/'skill-install.json').write_text(json.dumps({'changes':changes,'single_source':str(root),'backup':str(p/'skill-before')},ensure_ascii=False,indent=2)+'\n')
print('Installed 3 reviewed documents; before-hash guards passed.')
