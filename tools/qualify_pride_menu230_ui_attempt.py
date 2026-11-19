"""Retain229 failed restart harness without claiming a successful source switch."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_pride_soft_tree import latest
out=ROOT/'build/pride-menu229-resource-ui';assert not (out/'attempt-report.json').exists()
r=latest(out/'tree.jsonl')
(out/'interruption-correction.json').write_text(json.dumps(dict(manual_stop_performed=False,
    clarification='The late root stop attempt found no window; the harness had already timed out and closed its child. No extra stop message was sent.'),indent=2)+'\n')
paths=[Path(__file__),ROOT/'tools/verify_pride_menu229_resource_ui.py',ROOT/'build/pride-menu226-integrated/build-report.json']
(out/'attempt-report.json').write_text(json.dumps(dict(result='FAIL',stage='restart wait after F2',
    observed=dict(field=r['field'],modal=r['modal'],help=r['help'],node=next(c for c in r['choices'] if c[0]=='graphics.pride_final_menu')),
    scope='New node reached and SNES persisted. Scripted --frames startup without load/practice skips power-on restart checkpoint; log reports no power-on state. Corrected interactive/current-cold-load replay required. Not a passing source-switch/restart gate. All processes terminal; disk critically full.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
    artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('RETAINED failed UI attempt',flush=True)
