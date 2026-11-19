"""Publish the focused caption correction without rerunning unrelated suites."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
base=ROOT/'build/pride-caption268';bp=base/'build-report.json';b=bound(bp)
proofs=[ROOT/'build'/name/'report.json' for name in ('pride-caption269','pride-caption270-clamp','pride-caption271-window')]
for p in proofs:
    r=bound(p);assert r['result']=='PASS' and all(r['checks'].values()),p
assert digest(base/'player.exe')==b['binary_sha256']
previous=ROOT/'dist/installed-preview260';old=previous/'package-report.json';bound(old)
out=ROOT/'dist/installed-preview268';out.mkdir()
for p in previous.rglob('*'):
    if not p.is_file() or p.name in ('package-report.json','package.json','README.txt','LionKing.exe'):continue
    q=out/p.relative_to(previous);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
shutil.copy2(base/'player.exe',out/'LionKing.exe')
info=json.loads((previous/'package.json').read_text());info['player_sha256']=b['binary_sha256'];info['caption_centering']='Pride opening titles remain horizontally viewport-centred with SNES falling letters or MD artwork; source-specific height, falling offsets and duration retained.'
(out/'package.json').write_text(json.dumps(info,indent=2)+'\n')
(out/'README.txt').write_text((previous/'README.txt').read_text().replace('preview260','preview268')+'\nPride opening level captions stay horizontally centred, including falling letters.\n')
launcher=ROOT/'scripts/RunInstalledPreview.ps1';before=launcher.read_text();assert before.count('dist/installed-preview260')==1
protected_paths=[ROOT/'game-data/install.json',previous/'LionKing.exe']+[p for p in (ROOT/'settings').rglob('*') if p.is_file()]
protected={p.relative_to(ROOT).as_posix():digest(p) for p in protected_paths}
paths=[Path(__file__),bp,*proofs,old]
(out/'package-report.json').write_text(json.dumps(dict(result='PACKAGED',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
launcher.write_text(before.replace('dist/installed-preview260','dist/installed-preview268'))
reportout=ROOT/'build/pride-caption272-publication';reportout.mkdir()
checks=dict(packaged_binary_matches_focused_windows_build=digest(out/'LionKing.exe')==b['binary_sha256'],launcher_selects268='dist/installed-preview268' in launcher.read_text(),installed_data_settings_and_previous_binary_preserved=all(digest(ROOT/p)==sha for p,sha in protected.items()))
paths += [launcher,out/'package-report.json']
(reportout/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,published=True,full_first_level_complete=False,
    scope='Presentation-only caption fix published after targeted opening snapshots/guest preservation and one real Windows view. No unrelated broad regressions, installer/settings rewrite or asset-format changes.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PUBLISHED',b['binary_sha256'],flush=True)
