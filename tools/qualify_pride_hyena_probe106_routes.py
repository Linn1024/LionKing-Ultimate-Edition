"""Qualify the complete103 route with actual positive probe activation."""
import csv
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

source=ROOT/'build/pride-hyena-probe103/routes99/report.json';r=bound(source)
assert r['result']=='FAIL' and [k for k,v in r['checks'].items() if not v]==['probe-aot_no_probe_on_this_route','probe-lle_no_probe_on_this_route']
out=ROOT/'build/pride-hyena-probe103/routes-qualification106';out.mkdir()
checks={k:v for k,v in r['checks'].items() if not k.endswith('_no_probe_on_this_route') or k.startswith('native_')}
rows={name:list(csv.DictReader((source.parent/name/'probes.csv').open())) for name in ('probe-aot','probe-lle')}
checks['actual109_selected_probes_both_modes']=len(rows['probe-aot'])==len(rows['probe-lle'])==109
checks['actual_probe_trace_mode_parity']=rows['probe-aot']==rows['probe-lle']
checks['all_selected_probe_heights_eight_pixels_higher']=all(int(row['selected_query_y'])==((int(row['native_query_y'])-8)&65535) for row in rows['probe-aot'])
paths=[Path(__file__),source]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
    correction='Old97 produced no selected probe trace because its real-stack guard rejected calls. The103 route expectation incorrectly carried zero activation forward; actual current output correctly has109 adjustments and every original completion/parity/native-preservation check passed.101 absence of observer output was insufficient evidence of no calls.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),flush=True)
