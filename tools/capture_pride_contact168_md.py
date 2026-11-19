"""Fresh original MD power-on reference for the three longer contact protocols."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
import pride_movement_audit as movement
out=ROOT/'build/pride-contact168-md';out.mkdir()
movement.CASES.clear();movement.CASES.update(movement.ROLL_CONTACT_VARIANTS)
cases=movement.md(settle=256,fresh_ready=out,actor_slots=True)
target=out/'md.json';target.write_text(json.dumps(dict(cases=cases,settle_frames=256,fresh_md_input_boot=True,raw_slots_may_be_inactive=True,scope='Original MD fresh ordinary Start boot with owned full timing/audio checkpoint and the established three longer input protocols. No ROM/actor/RNG edits.'),indent=2)+'\n')
previous=ROOT/'build/pride-roll-contacts/md.json';old=json.loads(previous.read_text())
checks=dict(all1238_fields=sum(map(len,cases.values()))==1238,fresh_original_matches_prior_protocols=cases==old['cases'])
paths=[Path(__file__),ROOT/'tools/pride_movement_audit.py',ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',ROOT/'Lion King, The (World).md',previous]
(out/'report.json').write_text(json.dumps(dict(result='CAPTURED' if all(checks.values()) else 'DIFFERENCES',checks=checks,
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('MD capture',checks,flush=True)
