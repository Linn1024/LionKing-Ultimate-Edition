"""Preserve historical documentation and record the delivered Graveyard audit fixes."""
import json,shutil
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/graveyard718-doc-baseline';out.mkdir()
names=['docs/HANDOFF.md','docs/graveyard-coverage-audit.md','docs/graveyard-hyena-sound-audit.md','docs/graveyard-resources.md','docs/graveyard-gameplay-review.md','engine/docs/devlog.md']
rows={}
for name in names:
 p=ROOT/name;q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);rows[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
history=ROOT/'tools/pride_arena_history.py';s=history.read_text();anchor="    folders.append('graveyard706-death-baseline')";assert anchor in s;history.write_text(s.replace(anchor,anchor+"\n    folders.append('graveyard718-doc-baseline')"))
delivery='''Public708, 2026-11-11: the four concrete Graveyard audit findings are fixed.
Launch `Play Elephant Graveyard MD.cmd`. The launcher and installed preparer/data
are updated; existing settings and other asset packages are preserved.

- C58C80 scripted hyenas now share verified regular-hyena ownership for artwork,
  palette, reaction voice and selected ground decisions.709 shows changed MD
  artwork/colors at the actual late encounter;710 records its PCM4 reaction.
- New Gameplay / Level layouts / Elephant Graveyard / Hyena contact boxes uses
  the existing installer-prepared MD collision records. Same opening inputs
  leave6 health with SNES bounds and5 with MD bounds;496 adapted contacts logged.
- Gameplay / Simba / Roar now applies the existing MD14-update activation and
  original animation tokens in Graveyard as well as Pride; SNES remains20.
- New Graphics / Sprites / Simba / Cub Simba / Graveyard death movement moves
  Simba from his last live screen position toward the centre during nonfinal
  health death. Artwork, palette and music remain independently selectable.
  Native retry/final-life/fall logic is retained. Installer supplies33 death
  sequence tokens; runtime imports prepared data, without reading ROM code.

708 binary SHA256:307af508591feb65de8e9218b2b17d5414299fc1f56768182f52a3eb26f835cb.
Helper707 keeps973 images/840 collision records; sprite-v2 now includes132 bytes
of death tokens, aggregate2220548 bytes. Graveyard section TLKGYT02, view history
v5. Current mid-death save/load and retry pass; no old development-save migration.
711 confirms movement/source independence, identical selected/native guest WRAM,
current save/restore picture equality and healthy retry.712 real Windows clients
show movement and hidden death HUD.713 actual isolated Setup;714 qualification;
715 publication/default Setup;717 actual all-MD CMD, selected new leaves and
living Windows client.716's first unpaced capture raced the exiting process;
717 uses pacing for the actual capture. No product change was needed for that.

Scope: focused combat/voice/death checks, using nearby checkpoints. This does
not claim universal MD AI/animation timing or a new full-MD-gameplay walkthrough.
Ordinary MD inward leaps remain silent; do not add an invented jump roar.
For future levels, inventory actual actor descriptors, then verify each owner
at runtime across rendering, palette, audio and gameplay guards. Mapped asset
counts alone missed this scripted variant. Reuse existing nearby saves/inputs,
keep presentation choices independent and check actual Windows clients. Preserve
the per-scene background layer/scroll evidence; no background changes here.
'''
p=ROOT/'docs/HANDOFF.md';s=p.read_text();p.write_text(s.replace('# Lion King PC development handoff\n','# Lion King PC development handoff\n\n'+delivery+'\n## Earlier deliveries and audit history\n',1))
p=ROOT/'docs/graveyard-coverage-audit.md';s=p.read_text();p.write_text('# Elephant Graveyard coverage fixes708\n\n'+delivery+'\n## Original audit701 (historical findings, resolved above)\n\n'+s.split('\n',1)[1])
p=ROOT/'docs/graveyard-hyena-sound-audit.md';s=p.read_text();p.write_text(s.replace('# Graveyard hyena sound audit695\n','# Graveyard hyena sound audit695\n\nUpdate708: the omitted scripted C58C80/MD97980 ownership is fixed.710 restores\nfrom the nearby current late checkpoint and records one PCM4 reaction at17259\nfrom actorB813, confirmed C58C80 in the simultaneous actor trace.709 also\nverifies its MD artwork/colors in the actual Windows client. Public708 delivered\nthrough715/717. Earlier695 regular-hyena conclusions and intentional silent MD\nleaps remain valid. The correction below describes the pre-fix audit scope.\n',1))
p=ROOT/'docs/graveyard-resources.md';s=p.read_text();end=s.index('Opening-skull hyenas now');p.write_text('# Current status708: Graveyard audit fixes delivered\n\n'+delivery+'\n## Previous opening-skull delivery684\n\n'+s[end:])
p=ROOT/'docs/graveyard-gameplay-review.md';s=p.read_text();p.write_text(s.replace('# Elephant Graveyard gameplay review\n','# Elephant Graveyard gameplay review\n\nUpdate708: independently selectable MD hyena contact boxes now apply to both\nregular C58C74 and scripted C58C80 actors. Existing78 prepared pose pairs are\nused; no guessed artwork-sized collision rectangles.710 checks the same nearby\nopening encounter: SNES bounds retain6 health; MD bounds retain5, with496 real\nadapted contact queries. Cub MD roar also uses the existing14-update activation\nin Graveyard; source trace confirms the active adapter, SNES control bypasses it.\nScripted hyena selected ground eligibility now shares the regular descriptor\nhelper. This does not establish every MD AI sequence. The independent death\nmovement setting is presentation only: selected/native guest hashes match at\n2140, current save/restore pixels match, retry remains healthy. See\n[coverage fixes](graveyard-coverage-audit.md) for delivery and limits.\n',1))
p=ROOT/'engine/docs/devlog.md';p.write_text(p.read_text()+'''\n### Graveyard703..718: fix the four visible coverage gaps\n\n'''+delivery+'''\nImplementation: shared tlk_graveyard_hyena_owner.h guards include scripted\nC58C80 across renderer, generic sound replacement, voice and floor tags.\nHitbox adapter selects hyena family1 versus vulture2 after real owner binding.\nRoar guard adds actual cub Graveyard descriptorC003EB. Presentation caches last\nlive screen position/palette per field; installed33-token death sequence and\noriginal approach/fade draw independently of native retry logic. Current view\nhistory serializes this state. No framework submodule changes or generated game\ncode edits.703/706/718 preserve source/docs before changes. Full unrelated\nroute matrices deliberately omitted per user instruction; qualified scoped\nevidence is build/graveyard714-qualified/report.json.\n''')
print('DOCUMENTED',len(names))
