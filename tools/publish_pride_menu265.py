"""Select the packaged menu update after its focused installed-window smoke."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

base=ROOT/'build/pride-menu260-help';build=base/'build-report.json';b=bound(build)
package=ROOT/'dist/installed-preview260/package-report.json';bound(package)
smoke=ROOT/'build/pride-menu264-package/report.json';r=bound(smoke);assert r['result']=='PASS' and all(r['checks'].values())
assert b['changes_only_help_string'] and digest(package.parent/'LionKing.exe')==b['binary_sha256']
launcher=ROOT/'scripts/RunInstalledPreview.ps1';before=launcher.read_text();assert before.count('dist/installed-preview139')==1
after=before.replace('dist/installed-preview139','dist/installed-preview260')
candidate=base/'RunInstalledPreviewCandidate.ps1';assert candidate.read_text()==after.replace('$projectRoot = Split-Path $PSScriptRoot -Parent',"$projectRoot = '"+str(ROOT)+"'")
protected_paths=[ROOT/'game-data/install.json',ROOT/'dist/PrepareSpriteAssets.exe',ROOT/'dist/installed-preview139/LionKing.exe']
protected_paths += [p for p in (ROOT/'settings').rglob('*') if p.is_file()]
protected={p.relative_to(ROOT).as_posix():digest(p) for p in protected_paths}
archive=ROOT/'build/pride-menu265-publish-baseline';archive.mkdir();records={}
for name in ('scripts/RunInstalledPreview.ps1','tools/pride_arena_history.py','README.md','docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-final-menu-source.md','docs/pride-menu-current-checks.md','docs/background-audit.md','docs/launchers.md','engine/docs/devlog.md'):
    p=ROOT/name;q=archive/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    records[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(archive/'report.json').write_text(json.dumps(dict(historical_sources=records),indent=2)+'\n')
history=ROOT/'tools/pride_arena_history.py';text=history.read_text();anchor="    folders.append('pride-menu259-baseline')";assert text.count(anchor)==1
history.write_text(text.replace(anchor,anchor+"\n    folders.append('pride-menu265-publish-baseline')"))
launcher.write_text(after)
out=ROOT/'build/pride-menu265-publication';out.mkdir()
checks=dict(new_package_selected=launcher.read_text()==after,only_launcher_package_path_changed=after.replace('dist/installed-preview260','dist/installed-preview139')==before,
    install_helpers_old_binary_and_user_settings_preserved=all(digest(ROOT/p)==sha for p,sha in protected.items()))
paths=[Path(__file__),build,package,smoke,candidate,launcher,history,archive/'report.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,published=True,full_first_level_complete=False,
    player_sha256=b['binary_sha256'],protected_sha256=protected,
    scope='Root Play launchers now select260. Verified226 menu/resource gameplay and media plus exact260 help-string-only rebuild and focused installed Windows smoke; no unrelated broad tests repeated. Current user settings/install retained, older139 binary retained.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PUBLISHED',b['binary_sha256'],checks,flush=True)
