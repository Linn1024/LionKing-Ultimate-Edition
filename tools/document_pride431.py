"""Record a checked non-bug and retain the first-level scope without runtime edits."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
capture=ROOT/'build/pride426-fatal/report.json';qualified=ROOT/'build/pride428-fatal-qualified/report.json'
assert bound(capture)['result']=='CAPTURED' and bound(qualified)['result']=='PASS'
text='''

## Fatal action versus visible death426..431

Read-only original execution now follows the selected action in one naturally
reached fatal hit. At original MD field4755 the selector enters196B4C, its body
sets the directional hurt animation07E700, and the level death dispatcher runs
in the same field. No new hurt pose is displayed between those events. The
completed field instead displays the first death-stream pose02E5B8. The internal
196B4C marker remains, so comparing action-pointer bytes alone would misidentify
a visible behavior gap.

`build/pride426-fatal/report.json` preserves the full event chain, four original
images and86 end-of-field samples exactly equal to the existing original MD
reference. It replays ordinary power-on controls with a read-only CPU hook: no
guest/ROM edits, state loads or intercepted callees. The fatal-field image was
inspected. This is original-core evidence, not a new Windows player capture.

`build/pride428-fatal-qualified/report.json` passes6 checks, including all24
opening death-animation fields in each of the eight already captured nonfinal
deaths. These observed episodes all select196B4C; this does not separately
qualify the opposite direction, arbitrary airborne cases, final-life or falls.
The earlier427 qualifier incorrectly treated the post-loss counter as a pre-loss
counter; it excluded the last nonfinal episode. Its FAIL report is retained.
428 corrects only that classification, reusing the same captured observations.

There is no demonstrated visible fatal-hit animation gap to fix in these
episodes. No runtime, resource capability, package or launcher changes. Keep
the existing nonfinal/final-life controllers and avoid adding a pointer-parity
adapter for this observation. Full first-level fidelity remains open.
'''
p=ROOT/'docs/pride-hurt-selection.md';p.write_text(p.read_text()+text)
p=ROOT/'docs/HANDOFF.md';s=p.read_text().replace('Current425,','Current431,')
s=s.replace('Next select a substantive player-visible first-level fidelity gap using current', 'Fatal selector426/428 is now traced through the naturally displayed frame: the\noriginal directional hurt marker persists internally, but the death presenter\nselects the death pose in that same field. Eight existing nonfinal prefixes\nagree. No visible gap or runtime fix was established; see\n[hurt selection](pride-hurt-selection.md). Fall-boundary exploration likewise has\nno naturally established first-level pit death; do not repeat speculative sweeps.\n\nNext select a substantive player-visible first-level fidelity gap using current')
s=s.replace('Latest source archive417 preserves the416 handoff/status and preceding HUD\nsources; current HUD aggregate is `build/pride425-bindings/report.json`.\nAll411/414 and419..424 runs are terminal.', 'Source archive417 preserves the preceding HUD sources;430 preserves handoff425\nand the earlier hurt-selection notes. HUD aggregate425 remains valid; current\nread-only fatal investigation is `build/pride431-bindings/report.json`.\nAll411/414,419..424 and426 runs are terminal. Public418 is unchanged.')
p.write_text(s)
p=ROOT/'docs/pride-lands-status.md';s=p.read_text().replace('Current425,','Current431,')
s=s.replace('No new gameplay fix was needed in404..410.', 'Read-only426/428 traces one ordinary fatal hit through its displayed MD frame\nand checks eight existing nonfinal death prefixes. Different internal fatal\naction pointers do not establish a visible hurt-animation gap in these episodes;\nno adapter or gameplay correction is justified by that observation. See\n[hurt selection](pride-hurt-selection.md). Other directions/airborne/fall contexts\nremain separately scoped. Public418 is unchanged.\n\nNo new gameplay fix was needed in404..410.')
p.write_text(s)
p=ROOT/'engine/docs/devlog.md';p.write_text(p.read_text()+'''\n\n## Read-only fatal selection426..431\n\nOne ordinary original MD fatal hit reaches directional hurt then the level death\npresenter in the same field; completed frame already shows the death pose.426\nretains read-only instruction events/86 exact original samples and inspected\noriginal image.428 PASS6 checks include eight retained24-field nonfinal prefixes.\n427 excluded one episode through a pre/post-loss counter assumption; failed\nclassification retained, no game correction. No runtime changes, new capability,\nWindows player test or unrelated suites. Public418 unchanged. See root\ndocs/pride-hurt-selection.md. Full first-level goal remains OPEN.\n''')
paths=[Path(__file__),capture,qualified,ROOT/'build/pride425-bindings/report.json',*[ROOT/name for name in ('docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-hurt-selection.md','engine/docs/devlog.md','tools/pride_arena_history.py')]]
assert bound(ROOT/'build/pride425-bindings/report.json')['published']
out=ROOT/'build/pride431-bindings';out.mkdir(exist_ok=True)
(out/'report.json').write_text(json.dumps(dict(result='PROGRESS_GOAL_OPEN',runtime_changed=False,first_level_complete=False,scope='Fatal selection candidate traced to displayed death without a visible hurt-animation gap in the sampled ordinary episodes; no pointer-parity runtime adapter. Public418 retained.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PROGRESS_GOAL_OPEN; public418 unchanged',flush=True)
