"""Bind public390 table preparation and record the continuing scope."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
notice='''CURRENT396: Public390 prepares Pride start positions, lizard reactivation
flags,836 pose hitboxes and14 roar tokens/activation delay during Setup.
Installed sprite-v2 includes these tables and unchanged preceding artwork,
palettes, native death bank and map policy. Playback imports the tables instead
of running their ROM initializers. Source choices/gameplay algorithms unchanged.
Read docs/pride-prepared-gameplay.md (relative to project root).
391 verifies original/prepared tables and actual Setup;392 completes an ordinary
supported-MD route to level1 with prior guest/client/PCM preserved;393 actual
Windows play inspected;394 corrects its validator's expected rejection code
(8, not6) with only a one-field rejection rerun.395 publishes and upgrades
default assets/helper/launcher, preserving old files and settings. No save or
unrelated test matrix. Whole-runtime ROM independence is not claimed.
Public390 SHA256:
8bbf6611752f357fba04462e3bd4e0c94e05612f1bf7d0d97ddcb96fa4509be1.
First-level fidelity goal remains OPEN. Prioritize playable walkthrough and
visible gaps; do not chase instrument-only timing/one-frame transitions.
Earlier entries below describe historical releases and may be superseded.

'''
for name in ('docs/HANDOFF.md','docs/pride-lands-status.md','docs/launchers.md','README.md'):
    path=ROOT/name;text=path.read_text(encoding='utf-8')
    if not text.startswith('CURRENT396:'):path.write_text(notice+text,encoding='utf-8')
path=ROOT/'engine/docs/devlog.md';text=path.read_text(encoding='utf-8')
if '## Prepared Pride gameplay tables388..396' not in text:path.write_text(text+'\n\n## Prepared Pride gameplay tables388..396\n\n'+notice+'See root docs/pride-prepared-gameplay.md. Framework submodules untouched.\n',encoding='utf-8')
reports=[ROOT/name for name in ('build/pride389-cmake/build-report.json','build/pride390/build-report.json','build/pride391/report.json','build/pride392-route/report.json','build/pride394-qualification/report.json','build/pride395-publication/report.json','dist/installed-preview390/package-report.json')]
for p in reports:bound(p)
manifest=json.loads((ROOT/'game-data/install.json').read_text(encoding='utf-8-sig'))
assert manifest['sprite_assets']['version']==2 and manifest['scene_cache']['version']==2
launcher=(ROOT/'scripts/RunInstalledPreview.ps1').read_text();assert 'dist/installed-preview390' in launcher and 'Resolve-PreparedFile $manifest.sprite_assets 2' in launcher
out=ROOT/'build/pride396-bindings';out.mkdir(exist_ok=True)
paths=[Path(__file__),*reports,*[ROOT/name for name in ('docs/pride-prepared-gameplay.md','docs/HANDOFF.md','docs/pride-lands-status.md','docs/launchers.md','README.md','engine/docs/devlog.md','engine/CMakeLists.txt','scripts/RunInstalledPreview.ps1','game-data/install.json')]]
(out/'report.json').write_text(json.dumps(dict(result='PASS',scope='Published390 evidence bindings and current installed sprite/scene version2; full first-level goal remains open.',full_first_level_complete=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('Recorded public390 and checked current evidence/installed versions.')
