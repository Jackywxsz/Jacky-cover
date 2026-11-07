#!/usr/bin/env python3
"""Verify bundled asset bytes; this does NOT validate image anatomy or design."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'ASSET_MANIFEST.json').read_text())
for item in manifest['assets']:
 p=ROOT/item['path']
 assert p.is_file(),f'Missing {item["path"]}'
 assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],f'Changed {item["path"]}'
print(f'PASS: {len(manifest["assets"])} assets verified; visual/user acceptance not assessed.')
