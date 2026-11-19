"""Select the verified battle-cue package without touching installed game data."""
import json,shutil
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
build=ROOT/'build/pride-battle319/build-report.json';b=bound(build)
package=ROOT/'dist/installed-preview319/package-report.json';bound(package)
proof=ROOT/'build/pride-battle320/report.json';assert bound(proof)['result']=='PASS'
launch=ROOT/'build/pride-battle323-launcher/last-launch.log';assert 'native_hud_assets=loaded' in launch.read_text()
out=ROOT/'build/pride-battle324-publication';out.mkdir(exist_ok=True)
archive=ROOT/'build/pride-battle324-baseline';archive.mkdir(exist_ok=True);records={}
for name in ('scripts/RunInstalledPreview.ps1','tools/pride_arena_history.py','docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-hyena-entrance.md','engine/docs/devlog.md','README.md','docs/launchers.md'):
    p=ROOT/name;q=archive/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(archive/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
history=ROOT/'tools/pride_arena_history.py';text=history.read_text();anchor="    folders.append('pride-battle315-baseline')";assert text.count(anchor)==1
history.write_text(text.replace(anchor,anchor+"\n    folders.append('pride-battle324-baseline')"))
protected={p.relative_to(ROOT).as_posix():digest(p) for folder in ('game-data','settings') for p in (ROOT/folder).rglob('*') if p.is_file()}
launcher=ROOT/'scripts/RunInstalledPreview.ps1';assert 'dist/installed-preview307' in launcher.read_text()
assert digest(package.parent/'LionKing.exe')==b['binary_sha256']
launcher.write_text((build.parent/'RunInstalledPreview.publish.ps1').read_text())
checks=dict(verified_package_selected='dist/installed-preview319' in launcher.read_text(),installed_data_and_settings_preserved=all(digest(ROOT/name)==sha for name,sha in protected.items()),candidate_installed_launch_passed=True)
paths=[Path(__file__),build,package,proof,launch,archive/'report.json',launcher,history]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,published=True,full_first_level_complete=False,protected_sha256=protected,scope='Only launcher executable selection changed; no Setup or asset re-extraction needed. Current audio schema3 rejects older development audio histories.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PUBLISHED',b['binary_sha256'],checks)
