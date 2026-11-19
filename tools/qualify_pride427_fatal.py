"""Qualify displayed death poses independently of internal fatal hurt selection."""
import json
from pathlib import Path
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
capture=ROOT/'build/pride426-fatal/report.json';cap=bound(capture);assert cap['result']=='CAPTURED'
timeline=ROOT/'build/pride-death-timeline/md';ref=json.loads((timeline/'report.json').read_text())
assert digest(timeline/'samples.json')==ref['source_sha256']['samples']
rom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
prefix=[]
for i in range(33):
    at=0x7e5b2+i*4;prefix.extend([int.from_bytes(rom[at+1:at+4],'big')]*(rom[at]+1))
    if len(prefix)>=24:break
rows=json.loads((timeline/'samples.json').read_text());by={r['frame']:r for r in rows}
episodes=[]
for i,r in enumerate(rows):
    if not i or r['health'] or not rows[i-1]['health'] or r['level']!=1:continue
    f=r['frame'];action=r['words'][24]<<16|r['words'][25]
    episodes.append(dict(field=f,remaining_total_lives=r['lives'],action=hex(action),first_pose=hex(r['pose']),nonfinal_prefix_matches=r['lives']>1 and [by[f+n]['pose'] for n in range(24)]==prefix[:24]))
nonfinal=[e for e in episodes if e['remaining_total_lives']>1]
events=cap['episode'];pcs=[int(r['pc'],16) for r in events]
checks=dict(readonly_replay_matches=cap['matched_reference_fields']==86,
    observed_original_fatal_dispatch=pcs==[0x196a1c,0x196b4c,0x196cfc,0x1d6cb2,0x1d6d58],
    same_field_dispatch=all(int(r['frame'])==cap['fatal_field'] for r in events),
    hurt_body_did_not_display_new_pose=len({r['pose'] for r in events})==1,
    original_death_pose_at_field_end=next(r for r in json.loads((capture.parent/'samples.json').read_text()) if r['frame']==cap['fatal_field'])['pose']==prefix[0],
    prior_nonfinal_episodes=len(nonfinal)==8 and all(e['nonfinal_prefix_matches'] for e in nonfinal))
out=ROOT/'build/pride427-fatal-qualified';out.mkdir(exist_ok=True)
paths=[Path(__file__),capture,timeline/'report.json',timeline/'samples.json']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,episodes=episodes,runtime_changed=False,scope='One naturally reached original fatal-hit instruction trace and eight existing nonfinal original death prefixes. Directional hurt selection does not imply a visible hurt-animation gap before death in these episodes. No arbitrary airborne/final-life/fall equivalence claim; no game fix or new capability.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print(checks,episodes,flush=True)
