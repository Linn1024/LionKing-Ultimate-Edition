"""Distinguish live operand execution from a changed countdown trajectory."""
import csv
import json
from pathlib import Path
import re
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
base=ROOT/'build/pride-hyena-entrance139';source=base/'fights140/report.json';r=bound(source)
assert r['result']=='PASS'
reference=ROOT/'build/pride-hyena-entrance128/report.json';assert bound(reference)['result']=='ORIGINAL_ENTRANCE_ABI_OBSERVED'
out=base/'fights144-qualification';out.mkdir()
actual=list(csv.DictReader((source.parent/'entrance-aot/entrance.csv').open()))
original=[r for r in csv.DictReader((reference.parent/'contexts.csv').open()) if r['caller']=='c14480']
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
rows=lambda name:re.findall(pattern,(source.parent/name/'run.log').read_text())
a,b=rows('native'),rows('entrance-aot')
checks={k:v for k,v in r['checks'].items() if k!='selected_choice_changes_actual_gameplay'}
checks['selected_operand_causes_actual_guest_state_differences']=sum(x[2]!=y[2] for x,y in zip(a,b))==152
checks['all4320_pictures_remain_native_on_this_route']=len(a)==len(b)==4320 and all(x[1]==y[1] for x,y in zip(a,b))
checks['all85_entrance_timers_and_camera_positions_remain_native_on_this_route']=len(actual)==len(original)==85 and [(r['field'],r['timer'],r['camera_x']) for r in actual]==[(r['field'],r['timer'],r['camera_x']) for r in original]
paths=[Path(__file__),source,reference,source.parent/'entrance-aot/entrance.csv',reference.parent/'contexts.csv']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
    correction='The original140 check name inferred changed gameplay from different full WRAM hashes. That is too broad: the operand changes guest scratch, but all85 observed entrance timers/cameras and4320 pictures remain native on this route. Original report and outputs retained. Native preservation, actual hook operands and selected mode/media parity remain valid. A route with a live countdown difference is still needed.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),flush=True)
