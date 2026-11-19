"""Record published foreground and persistent player-facing priorities."""
from pathlib import Path
from audit_scenes import ROOT

notice='''CURRENT376: Public372 adds prepared MD foreground artwork in Can't Wait to
Be King (12391/12400 cells, nine native fallbacks), with independent palette
and scenery choices. Native collision/gameplay remain unchanged. Setup uses
the native scene preparer; default data and launchers are upgraded, settings
preserved. See docs/cant-wait-prepared-foreground.md (relative to project root).
Evidence: build/cant-wait373/report.json, cant-wait374-window/report.json and
cant-wait375-publication/report.json. Actual Windows view inspected. Full
first-level scope remains OPEN. Public372 SHA256:
6aab89332f2fc5b99373cb2de9a4804e61cd17ca1ca29ddc4e374bcd3b780537.
Earlier entries below describe historical releases and may be superseded.

User priority: check visible art, controls/combat and walkthrough progression.
Do not pursue instrument-only timing or one-frame transition differences.
Keep checks focused on affected code; no repeated unrelated test matrices.

'''
for name in ('docs/HANDOFF.md','docs/cant-wait-live-background.md','docs/next-levels-status.md','docs/background-audit.md','docs/pride-lands-status.md','docs/launchers.md','README.md'):
    path=ROOT/name; text=path.read_text(encoding='utf-8')
    if not text.startswith('CURRENT376:'): path.write_text(notice+text,encoding='utf-8')
path=ROOT/'engine/docs/devlog.md'
text=path.read_text(encoding='utf-8')
if '## Prepared second-level foreground (public372)' not in text:
    path.write_text(text+'\n\n## Prepared second-level foreground (public372)\n\n'+notice+'See engine/tools/prepare_scene_assets.c and engine/cmake/TlkSceneAssets.cmake.\nNo framework submodule changes; renderer/art preparation only.\n',encoding='utf-8')
print('Recorded public372 and player-facing priorities.')
