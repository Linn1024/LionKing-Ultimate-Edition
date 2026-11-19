"""Record installed rhino resource choices and the next concrete second-level work."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
reports=[ROOT/'build'/name/'report.json' for name in ('cant-wait462-rhino','cant-wait463-ui','cant-wait464-setup','cant-wait467-publication')]
for p in reports:assert bound(p)['result']=='PASS'
p=ROOT/'docs/HANDOFF.md';s=p.read_text().replace('Current454,','Current468,').replace('Public448 is\nthe current Windows player; it adds independent monkey and ostrich colors in\nCan\'t Wait to Be King. Existing scenery, cub art, audio and game logic are retained.', 'Public460 is\nthe current Windows player; it adds prepared rhino head artwork and independent\ncolors in Can\'t Wait to Be King, retaining monkey/ostrich choices and game logic.')
s=s.replace('dist/installed-preview448/LionKing.exe','dist/installed-preview460/LionKing.exe').replace('72fb01357e0f491032104b3043ad04a5a7e51dc573fea7c510efae8d00e89d13','eb23e75d306a66bfca29192bb21e7ce5d576352b47e506957f9580c19974b1ab')
s=s.replace('| Can\'t Wait animal colors448 |', '| Can\'t Wait rhino art460 | Prepared MD heads and independent palette for13 native poses/nine MD images; native timing/gameplay retained. [Details](cant-wait-rhino-art.md);462 direct-select output/data,463 actual UI/Windows,464 Setup,467 publication. |\n| Can\'t Wait animal colors448 |')
s=s.replace('reviewed monkey/ostrich color choices; next address giraffe/rhino actor art.', 'reviewed monkey/ostrich colors and rhino head frames/palette; next address giraffe\nhead ownership/art. Native giraffe frames reference bank7E work memory; decode\nfull7E/7F snapshot data and verify initialization before mapping dynamic images.')
s=s.replace('`build/cant-wait452-checkpoint/report.json`: current448 ride at7000,6329 consumed', '`build/cant-wait452-checkpoint/report.json`: dated448 ride at7000,6329 consumed')
s=s.replace('no old-development-save compatibility work is required.', 'no old-development-save compatibility work is required. Rhino462/463 use direct\nlevel2 select and a short approach after loading, with no level1 replay.',1)
s=s.replace('Current second-level aggregate is\n`build/cant-wait454-bindings/report.json`. All retained runs are terminal; public448\nis selected.', 'Current second-level aggregate is\n`build/cant-wait468-bindings/report.json`.457/465 preserve prior source/install\nidentities. All retained runs are terminal; public460 is selected.')
p.write_text(s)
p=ROOT/'docs/next-levels-status.md';p.write_text('''CURRENT468: Public460 adds installed MD rhino head images and independent
palette selection, preserving native animation/gameplay and prior animal choices.
Read docs/cant-wait-rhino-art.md (project root).462 PASS9 fast direct level-select
approach/data/native preservation;463 PASS6 actual live UI/Windows;464 actual
Setup;467 installed publication. No level1 prefix or unrelated full matrices.
Giraffe head ownership/art remains the next concrete gap; its RAM-backed source
needs full7E/7F initialization evidence. The second-level goal remains ACTIVE.
Earlier notes below preserve their historical scope.

'''+p.read_text())
p=ROOT/'engine/docs/devlog.md';p.write_text(p.read_text()+'''\n\n## Prepared Can't Wait rhino head resources455..468\n\nPublic460 adds independent live rhino frames/palette through existing NPC\ncompositor and sprite-v2 import.13 native poses/nine MD images, original equal\n16-update bounce-prefix order; native animation timing/behavior retained. Actual\nscene/draw/actor descriptor and native palette hashes guard ownership. Current\nprepared/live scene palette1 supplies MD colors; shared banks on other animals\nare untouched. All preceding prepared artwork/gameplay bytes remain exact.\n462 PASS9 direct level2 selection after loading, native/guest/data preserved and\nscoped head difference;463 PASS6 real SDL live frames/native palette independence\nand inspected Windows view.461 supplied inputs before the loading macro ended;\nfailed route retained, no game fix.464 native Setup;467 installed publication\nafter correcting inherited package sprite-policy metadata (466 rejection kept).\nDefault data/helper upgraded, settings/old assets retained. No level1 replay,\nunrelated matrix or new state schema. Giraffe RAM-backed head art is next; full\n7E/7F initialization evidence required. See root docs/cant-wait-rhino-art.md.\n''')
paths=[Path(__file__),*reports,*[ROOT/name for name in ('docs/HANDOFF.md','docs/next-levels-status.md','docs/cant-wait-rhino-art.md','engine/docs/devlog.md','engine/runner/tlk_md_sprites.c','engine/runner/tlk_md_sprites.h','engine/runner/tlk_resources.c','engine/runner/tlk_wide.c','engine/runner/tlk_cw_rhino_metadata.h','tools/cw_sprite_catalog.py','tools/cw_rhino_pairs.json','scripts/RunInstalledPreview.ps1','game-data/install.json','tools/pride_arena_history.py')]]
out=ROOT/'build/cant-wait468-bindings';out.mkdir(exist_ok=True)
(out/'report.json').write_text(json.dumps(dict(result='SECOND_LEVEL_PROGRESS',second_level_complete=False,published=True,tests_used_level_select=True,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('SECOND_LEVEL_PROGRESS; public460; next giraffe RAM-backed head',flush=True)
