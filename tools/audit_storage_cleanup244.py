"""Aggregate lossless space recovery and validate current project bindings."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
out=ROOT/'build/storage-cleanup244';checks={};reports={};rows=[]
for name in ('rgb','other'):
    p=out/name/'report.json';r=bound(p);reports[name]=r
    journal=[json.loads(line) for line in (p.parent/'files.jsonl').read_text().splitlines()]
    checks[name+'_complete_and_all_bytes_verified']=r['result']=='PASS' and len(journal)==r['candidate_count']==r['verified_files'] and all(x['bytes_unchanged'] and x['sha256_before']==x['sha256_after'] and x['exit']==0 for x in journal)
    checks[name+'_all_paths_under_build']=all((ROOT/x['path']).resolve().is_relative_to((ROOT/'build').resolve()) for x in journal)
    rows+=journal
pilot=json.loads((out/'pilot.json').read_text());checks['pilot_bytes_unchanged']=pilot['bytes_unchanged'] and pilot['exit']==0
checks['no_duplicate_processed_paths']=len({x['path'] for x in rows}|{pilot['path']})==len(rows)+1
for name in ('pride-menu243-bindings/report.json','pride-hyena-entrance139/bindings/report.json'):
    r=bound(ROOT/'build'/name);checks[name+'_still_bound']=r['result']=='PASS'
for folder,published in (('pride-menu226-integrated',False),('pride-hyena-entrance139',True)):
    p=ROOT/'build'/folder/'build-report.json';r=bound(p)
    checks[folder+'_binary_exact']=digest(p.parent/'player.exe')==r['binary_sha256']
    checks[folder+'_all324_inputs_exact']=len(r['link_inputs_sha256'])==324 and all(digest(ROOT/q)==sha for q,sha in r['link_inputs_sha256'].items())
    if published:checks['public139_exact']=digest(ROOT/'dist/installed-preview139/LionKing.exe')==r['binary_sha256']
checks['framework_submodules_clean']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
saved=sum(r['allocated_before']-r['allocated_after'] for r in rows)+pilot['allocated_before']-pilot['allocated_after']
paths=[Path(__file__),ROOT/'tools/compact_research_storage.py',ROOT/'tools/pride_arena_history.py',ROOT/'docs/HANDOFF.md',ROOT/'docs/pride-lands-status.md',ROOT/'docs/storage-maintenance.md']
artifacts=[out/'pilot.json',out/'retention-audit.json',*[out/n/p for n in ('rgb','other') for p in ('report.json','inventory.json','files.jsonl')]]
result=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,processed_files=len(rows)+1,
    allocated_saved_bytes=saved,allocated_saved_GB=round(saved/10**9,2),allocated_saved_GiB=round(saved/2**30,2),
    current_free_bytes=shutil.disk_usage(ROOT).free,file_deletions=0,
    scope='Lossless transparent Windows compression of ignored build research files. Every processed file verified before/after. Current staged/public bytes, all link inputs and immediate evidence bindings preserved; no new gameplay/release claim. Retention candidates audited, none deleted.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in artifacts})
(out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','artifacts_sha256')}),flush=True)
