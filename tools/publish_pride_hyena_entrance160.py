"""Select139 after complete current gates, live countdown proof and installed replay."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
base=ROOT/'build/pride-hyena-entrance139';bp=base/'build-report.json';b=bound(bp)
proofs=[base/p/'report.json' for p in ('routes156-qualification','parent-verification','windows-ui','fights144-qualification','boundary159','package-play','native75','allbugs-verification')]
proofs += [ROOT/'build'/p/'report.json' for p in ('pride-hyena-entrance132','pride-hyena-countdown133','pride-hyena-entrance153-live-decision')]
for p in proofs:
    r=bound(p);assert r['result']=='PASS' and all(r['checks'].values()),p
assert bound(base/'native75/report.json')['route_count']==75
assert len(b['link_inputs_sha256'])==324 and b['unchanged_public118_inputs']==320
assert all(digest(ROOT/p)==sha for p,sha in b['link_inputs_sha256'].items())
assert not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
package=ROOT/'dist/installed-preview139/package-report.json';bound(package);assert digest(package.parent/'LionKing.exe')==b['binary_sha256']
launcher=ROOT/'scripts/RunInstalledPreview.ps1';history=ROOT/'tools/pride_arena_history.py';before=launcher.read_text();assert before.count('dist/installed-preview118')==1
after=before.replace('dist/installed-preview118','dist/installed-preview139');candidate=base/'RunInstalledPreviewCandidate.ps1'
assert candidate.read_text()==after.replace('$projectRoot = Split-Path $PSScriptRoot -Parent',"$projectRoot = '"+str(ROOT)+"'")
protected_paths=[ROOT/'game-data/install.json',ROOT/'dist/PrepareSpriteAssets.exe',ROOT/'dist/installed-preview118/LionKing.exe']
protected={p.relative_to(ROOT).as_posix():digest(p) for p in protected_paths}
archive=ROOT/'build/pride-hyena-entrance160-publish-baseline';archive.mkdir();rows={}
for name in ('scripts/RunInstalledPreview.ps1','tools/pride_arena_history.py','README.md','docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-hyena-entrance.md','docs/pride-hyena-probe.md','docs/resource-tree-inheritance.md','docs/launchers.md','engine/docs/devlog.md'):
    p=ROOT/name;q=archive/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);rows[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(archive/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
s=history.read_text();anchor="    folders.append('pride-hyena-entrance138-baseline')";assert s.count(anchor)==1
history.write_text(s.replace(anchor,anchor+"\n    folders.append('pride-hyena-entrance160-publish-baseline')"))
launcher.write_text(after);out=base/'publication';out.mkdir()
checks=dict(integrated139_selected=launcher.read_text()==after,only_package_selection_changed=before.replace('dist/installed-preview118','dist/installed-preview139')==after,
    installed_data_helper_and_old_public_binary_preserved=all(digest(ROOT/p)==sha for p,sha in protected.items()))
paths=[Path(__file__),bp,*proofs,package,launcher,history,candidate,archive/'report.json',*protected_paths]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,published=True,full_first_level_complete=False,
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PUBLISHED',b['binary_sha256'],checks,flush=True)
