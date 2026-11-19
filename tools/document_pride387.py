"""Record the current installed-data change without rewriting historical proof."""
from audit_scenes import ROOT
notice='''CURRENT387: Public382 moves all8000 Pride contact cells and fixed Can't Wait
palette recipes into Setup's scene-v2 package. Installed playback loads those
tables; outdated explicit data requests Setup before play. Native gameplay,
independent sources and public372 artwork are retained. Default installation
and launchers upgraded, existing assets/settings retained. Read
docs/pride-prepared-contact.md (relative to project root).
Evidence: pride380 direct prepared-data/Setup checks, pride381 ordinary route
through victory/bonus to level1, pride383 real Windows boss view/error check,
pride384 scoped qualification, pride385 publication, pride386 helper links.
No cold polled replay claim:383's harness restarted its tape at poll0 after
loading3750. No save/game correction was justified. Full first-level goal OPEN.
Public382 SHA256:
c8393231f7e42a9afdbaabbb56b6e66c865a8bcf326f1a54b50a8968b6d0416e.

User priority: playable walkthrough and differences visible in ordinary play;
no instrument-only timing/one-frame transition refinements, no repeated
unrelated test matrices. Older notes below are historical and may be superseded.

'''
for name in ('docs/HANDOFF.md','docs/pride-lands-status.md','docs/background-audit.md','docs/launchers.md','README.md'):
    path=ROOT/name;text=path.read_text(encoding='utf-8')
    if not text.startswith('CURRENT387:'):path.write_text(notice+text,encoding='utf-8')
path=ROOT/'engine/docs/devlog.md';text=path.read_text(encoding='utf-8')
if '## Prepared Pride contact tables377..387' not in text:path.write_text(text+'\n\n## Prepared Pride contact tables377..387\n\n'+notice+'See root docs/pride-prepared-contact.md for scope, excluded harness claim and retained failed reports.\nFramework submodules untouched; other ROM-based preparation remains open.\n',encoding='utf-8')
print('Recorded public382, focused evidence and remaining preparation scope.')
