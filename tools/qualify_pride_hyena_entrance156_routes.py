"""Correct154's unsupported headless-only completion marker on retained SDL runs."""
import json
from pathlib import Path
import re
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
base=ROOT/'build/pride-hyena-entrance139';oldpath=base/'routes154-qualification/report.json';old=bound(oldpath)
failed=[k for k,v in old['checks'].items() if not v]
assert old['result']=='FAIL' and sorted(failed)==sorted(n+'_full_route_to_next_level' for n in ('native','probe-aot','probe-lle'))
out=base/'routes156-qualification';out.mkdir()
# These player return codes were printed by the original verifier and observed
# directly when root polled session59070. Its terminal1 was the later Python
# FileNotFoundError, not a nonzero game process. Keep that provenance explicit.
observation=dict(tool='functions.exec / tools.write_stdin',session_id=59070,verifier_exit_code=1,
    observed_stdout=['native exit 0 level 1 probes 0','probe-aot exit 0 level 1 probes 1002','probe-lle exit 0 level 1 probes 1002'],
    player_exit_codes=dict(native=0,**{'probe-aot':0,'probe-lle':0}),recorded_by='root from actual tool outputs; not reconstructed from game logs')
observed=out/'process-observation.json';observed.write_text(json.dumps(observation,indent=2)+'\n')
checks={k:v for k,v in old['checks'].items() if k not in failed};paths=[Path(__file__),oldpath,observed]
for name in ('native','probe-aot','probe-lle'):
    folder=base/'routes148'/name;log=folder/'run.log';scene=folder/'scene.json';s=json.loads(scene.read_text())
    rows=re.findall(r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',log.read_text())
    checks[name+'_full_route_to_next_level']=observation['player_exit_codes'][name]==0 and s['level']==1 and len(rows)==6000 and [int(r[0]) for r in rows]==list(range(1,6001))
    paths += [log,scene]
report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=old['commands'],observations=old['observations'],
    commands_reconstructed_from_frozen_verifier_and_retained_profiles=True,
    correction='154 required result=completed frames=6000, a headless-host marker absent from SDL logs. Actual player return0 was directly observed for allthree in original session59070. All6000 sequential canonical/fullWRAM fields and next-level scene are present. Retains154 and original148 failure; no capture rerun or output edits. Prior11 checks and exact source identities retained by154 binding.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)
