"""Close the reviewed first-level delivery milestone and hand off later levels."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
review=ROOT/'build/pride432-completion-review/report.json';r=bound(review);assert r['result']=='REVIEWED'
assert len(r['reports'])==16 and all(v['result']=='PASS' for v in r['reports'].values()) and all(r['installed'].values())
p=ROOT/'docs/HANDOFF.md';s=p.read_text()
s=s.replace('Current431, 2026-11-10. The first-level fidelity goal remains OPEN. Public418 is', 'Current434, 2026-11-10. The first-level delivery milestone is COMPLETE following\nthe user-directed practical review; remaining-level development is next. Public418 is')
start=s.index('## Remaining first-level work');end=s.index('## Subsystem reading map',start)
s=s[:start]+'''## First-level review and active next work

Read [the delivery review](pride-delivery-review.md).432 revalidates16 retained
reports and all15 installed identities; no game tests are repeated. Walkthrough,
independent supported choices, installer resources, basic saves/retry, menu/audio
and visual defect evidence satisfy the practical first-level milestone. The user
explicitly directed moving on rather than endlessly searching hypothetical gaps.

This is not universal original-MD behavior certification. Generic unsupported MD
movement/combat/enemy choices stay explicit SNES, useful hybrid emulation stays,
and the whole runtime still consumes original data. Concrete reported first-level
defects can be fixed later. Do not keep the milestone open solely for arbitrary
untested cases, unseen falls, action-pointer differences or one-frame transitions.

Proceed through every remaining level and the ending, starting with Can't Wait
to Be King's animal artwork/ownership. Its prepared scenery, dynamic palette,
background scroll/wrap, shared cub art and music already exist. Do not repeat
those implementations or their entire old test suites. Read
[the remaining-level plan](remaining-levels-plan.md) and the scene-specific docs.

''' + s[end:]
s=s.replace('Source archive417 preserves the preceding HUD sources;430 preserves handoff425\nand the earlier hurt-selection notes. HUD aggregate425 remains valid; current\nread-only fatal investigation is `build/pride431-bindings/report.json`.\nAll411/414,419..424 and426 runs are terminal. Public418 is unchanged.', 'Source archive417 preserves the preceding HUD sources;430 preserves handoff425\nand earlier hurt-selection notes;433 preserves the preceding431 open-goal docs.\nCurrent delivery review is `build/pride434-delivery/report.json`, backed by432.\nAll retained runs are terminal. Public418 is unchanged.')
s=s.replace('After this first-level goal is actually complete, create the explicitly requested\nnext goal for every remaining level through the ending. Do not create it early\nor mark the current goal complete because only its routes pass.', 'The first-level review is complete. Create/resume the explicitly requested next\ngoal for every remaining level through the ending. Keep the practical stopping\nrule: implement confirmed missing features and address visible/playable defects.')
p.write_text(s)
p=ROOT/'docs/pride-lands-status.md';s=p.read_text().replace('Current431,','Current434,')
s=s.replace('independent SNES/MD choices. The broader first-level fidelity goal remains OPEN.', 'independent SNES/MD choices. The first-level delivery milestone is COMPLETE\nunder the user-directed practical review432/434; full original-MD behavior is\nnot universally certified. See [delivery review](pride-delivery-review.md).')
start=s.index('## Practical next work');end=s.index('## Useful subsystem documents',start)
s=s[:start]+'''## Practical next work

Continue [remaining levels through the ending](remaining-levels-plan.md), starting
with concrete missing animal artwork in Can't Wait to Be King. Preserve honest
unsupported MD choices and the completed first-level behavior. Reopen only a
specific confirmed issue, rather than restarting the entire first-level search.
Basic save/retry and inherited baseline gates need no unrelated repetition.

''' + s[end:];p.write_text(s)
p=ROOT/'docs/next-levels-status.md';s=p.read_text();p.write_text('''CURRENT434: The practical first-level delivery review is complete; later levels
are the next active development goal. Read docs/remaining-levels-plan.md and
docs/pride-delivery-review.md (project root). Public418 remains selected.
Start with Can't Wait animal artwork/ownership; its prepared foreground,
three-region background scroll/wrap, dynamic palette, shared cub artwork and
music already exist. Implement concrete missing features and visible/playable
defects; do not resume hypothetical first-level fidelity searches.
Older entries below retain their historical scopes and are superseded where
the current handoff or scene implementation says otherwise.

''' + s)
p=ROOT/'engine/docs/devlog.md';p.write_text(p.read_text()+'''\n\n## Practical first-level delivery review432..434\n\nUser directed moving to later levels rather than speculative difference searches.\n432 inspects16 bound reports (all PASS), their actual requirement-specific checks,\nand15 current installed identities (all match), without new game runs. Review\ncovers original baseline/observer, walkthrough, supported independent choices,\nmenu/audio, prepared resources, save/retry and visible presentation. First-level\ndelivery milestone complete with honest unsupported MD/hybrid limits; no universal\noriginal-MD or whole-ROM independence claim. Public418 unchanged.433 preserves\npreceding docs. Next: remaining levels/ending, beginning with Can't Wait animal\nartwork. See root docs/pride-delivery-review.md and remaining-levels-plan.md.\n''')
paths=[Path(__file__),review,*[ROOT/name for name in ('docs/HANDOFF.md','docs/pride-lands-status.md','docs/next-levels-status.md','docs/pride-delivery-review.md','docs/remaining-levels-plan.md','engine/docs/devlog.md','tools/pride_arena_history.py')]]
out=ROOT/'build/pride434-delivery';out.mkdir(exist_ok=True)
(out/'report.json').write_text(json.dumps(dict(result='FIRST_LEVEL_DELIVERY_COMPLETE',runtime_changed=False,user_priority='Concrete playable/visible requirements; move to later levels instead of speculative indefinite parity checks.',requirements_review='docs/pride-delivery-review.md',next_plan='docs/remaining-levels-plan.md',universal_original_md_equivalence=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('FIRST_LEVEL_DELIVERY_COMPLETE',flush=True)
