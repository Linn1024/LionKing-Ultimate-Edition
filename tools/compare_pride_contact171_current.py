"""Compare the fresh current-player protocols while preserving raw input/state data."""
import collections
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from pride_movement_audit import ROLL_CONTACT_VARIANTS
from compare_pride_roll_originals import compare
native_path=ROOT/'build/pride-contact170-current/report.json';native=bound(native_path);assert native['result']=='CAPTURED'
md_path=ROOT/'build/pride-contact168-md/report.json';md=bound(md_path);assert md['result']=='DIFFERENCES'
out=ROOT/'build/pride-contact171-comparison';out.mkdir()
a=json.loads((native_path.parent/'snes.json').read_text())['cases'];b=json.loads((md_path.parent/'md.json').read_text())['cases']
checks={};raw_slot_differences={}
old=json.loads((ROOT/'build/pride-roll-contacts/md.json').read_text())['cases']
for name,pads in ROLL_CONTACT_VARIANTS.items():
    checks[name+'_current_actual_host_inputs_match_protocol']=all(row['pad']==(int(format(pad,'016b')[::-1],2)&0xfff) for row,pad in zip(a[name],pads)) and len(a[name])==len(pads)
    for row,pad in zip(a[name],pads):row['pad']=pad
    checks[name+'_fresh_md_defined_player_camera_and_draw_fields_match_prior']=all({k:v for k,v in x.items() if k!='raw_slots'}=={k:v for k,v in y.items() if k!='raw_slots'} for x,y in zip(b[name],old[name]))
    raw_slot_differences[name]=sum(x['raw_slots']!=y['raw_slots'] for x,y in zip(b[name],old[name]))
report=compare(a,b,False)
checks['all1238_current_player_samples_match_original_md']=report['total_fields_per_version']==1238 and all(r['result']=='MATCH' for r in report['cases'].values())
report.update(result='PASS' if all(checks.values()) else 'PARTIAL',checks=checks,fresh_md_raw_slot_different_rows=raw_slot_differences,
    scope='Current139 actual SDL player with fresh current checkpoint and exact ordinary protocol inputs vs fresh original MD. Comparison view converts verified host bit order back to SNES tape convention. All raw captures retained. Raw-slot differences from older MD are not hidden or classified as active/inactive; active-list reachability and per-branch production/mode neutrality remain separate.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in [Path(__file__),native_path,md_path,ROOT/'tools/compare_pride_roll_originals.py',ROOT/'tools/compare_pride_movement.py',ROOT/'build/pride-roll-contacts/md.json']})
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)
