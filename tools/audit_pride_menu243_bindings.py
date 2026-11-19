"""Bind current save/restart/native75 progress and retained storage failures."""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
out=ROOT/'build/pride-menu243-bindings';out.mkdir();checks={};paths=[Path(__file__)]
for name,expected in (
    ('pride-menu232-resource-ui/attempt-report.json','FAIL'),
    ('pride-menu233-gameplay-save/report.json','PASS'),
    ('pride-menu234-resource-ui/report.json','PASS'),
    ('pride-menu235-save-guard/report.json','PASS'),
    ('pride-menu236-visible-restart/report.json','PASS'),
    ('pride-menu226-integrated/native75/report.json','PASS'),
    ('pride-menu226-integrated/allbugs-observer/build-report.json','BUILT'),
    ('pride-menu226-integrated/allbugs-verification/attempt-report.json','FAIL'),
    ('pride-menu240-md-timing/attempt-report.json','FAIL'),
    ('pride-menu241-md-timing-local/attempt-report.json','FAIL'),
    ('pride-menu231-bindings/report.json','PASS'),
    ('pride-hyena-entrance139/bindings/report.json','PASS')):
    p=ROOT/'build'/name;r=bound(p);paths.append(p);checks[name]=r['result']==expected
    if expected=='PASS':checks[name] &= all(r.get('checks',{}).values())
for folder,metadata,sha_key in (
    ('pride-menu226-integrated/allbugs-observer','binary-archive.json','original_sha256'),
    ('pride-menu241-md-timing-local/control','audio-archive.json','original_sha256')):
    p=ROOT/'build'/folder/metadata;r=json.loads(p.read_text());archive=p.parent/r['archive'];paths += [p,archive]
    sha=hashlib.sha256()
    with gzip.open(archive,'rb') as f:
        for data in iter(lambda:f.read(1024*1024),b''):sha.update(data)
    checks[folder+'_lossless_archive_exact']=sha.hexdigest()==r[sha_key] and digest(archive)==r['archive_sha256']
bp=ROOT/'build/pride-menu226-integrated/build-report.json';b=bound(bp);paths.append(bp)
checks['staged226_binary_exact']=digest(bp.parent/'player.exe')==b['binary_sha256']
checks['all324_staged_inputs_exact']=len(b['link_inputs_sha256'])==324 and all(digest(ROOT/p)==sha for p,sha in b['link_inputs_sha256'].items())
public=ROOT/'build/pride-hyena-entrance139/build-report.json';p=bound(public);paths.append(public)
checks['published139_unchanged']=digest(ROOT/'dist/installed-preview139/LionKing.exe')==p['binary_sha256'] and 'dist/installed-preview139' in (ROOT/'scripts/RunInstalledPreview.ps1').read_text()
checks['framework_submodules_clean']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
paths += [ROOT/s for s in ('docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-menu-current-checks.md',
    'docs/pride-final-menu-source.md','engine/docs/devlog.md','tools/pride_arena_history.py','tools/windows_json_pipe.py')]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
    current_staged_sha256=b['binary_sha256'],native75_complete=True,new_allbugs_complete=False,
    full_first_level_complete=False,published=False,
    scope='Bindings of current native-timing320 source switches/current gameplay save and full native75 endpoint gate. No source/width/audio/save universal matrix or All Bugs/release claim. Storage failures and exact archived bytes retained; user space request pending.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)
