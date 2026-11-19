"""Correct a verifier's guessed log token using the actual prepared-file contract."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reference=ROOT/'build/graveyard632-installed/report.json';r=bound(reference);assert r['result']=='FAIL' and not r['checks']['prepared_assets_loaded'] and all(v for k,v in r['checks'].items() if k!='prepared_assets_loaded')
manifest=ROOT/'game-data/install.json';m=json.loads(manifest.read_text(encoding='utf-8-sig'));package=ROOT/'dist/installed-preview621/package.json';p=json.loads(package.read_text());assets=ROOT/'game-data'/m['sprite_assets']['file'];raw=assets.read_bytes();checks={k:v for k,v in r['checks'].items() if k!='prepared_assets_loaded'}
checks.update(correct_prepared_policy=raw[88:120].hex()==p['required_sprite_policy_sha256'],prepared_payload_verified=digest(assets)==m['sprite_assets']['sha256'],actual_native_cache_loaded='resource_cache=loaded' in (reference.parent/'settings/last-launch.log').read_text())
out=ROOT/'build/graveyard633-installed-qualified';out.mkdir();paths=[Path(__file__),reference,manifest,package,assets,ROOT/'scripts/RunInstalledPreview.ps1']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,scope='632 captured/inspected the actual installed Windows client, selected both sources and rejected obsolete data before playing. Its guessed sprite_assets=loaded log token does not exist. Validate the successful launcher policy/hash contract and actual resource_cache=loaded token, reusing that run without changing game code or replaying it.',source_sha256={x.relative_to(ROOT).as_posix():digest(x) for x in paths}),indent=2)+'\n');print(checks,flush=True)
