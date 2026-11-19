"""Record final resource-independence correction and public launcher target."""
from audit_scenes import ROOT
note='''Final720 correction: selecting only Graveyard death movement now enables the
presentation renderer with native256 viewport, artwork and palette. Validate
also requires the installed death sequence/images and hyena bounds.721 passes
the death-only fresh/current-save/native-control checks and two actual Windows
captures.722 retains714 combat/audio/retry evidence because only resource
eligibility/validation changed.723 publishes720 and verifies its installed
candidate launcher;717's real all-MD gameplay client covered the same gameplay
and drawing code in708. No unrelated level walkthrough was repeated.

'''
for name in ('docs/HANDOFF.md','docs/graveyard-coverage-audit.md','docs/graveyard-resources.md','engine/docs/devlog.md'):
 p=ROOT/name;s=p.read_text();s=s.replace('Public708, 2026-11-11: the four concrete','Public720, 2026-11-11: the four concrete').replace('708 binary SHA256:307af508591feb65de8e9218b2b17d5414299fc1f56768182f52a3eb26f835cb.','720 binary SHA256:1143af80828a4dd3293719cfd3984e1789dd5da029f33a85bc68373e5c255fa3.').replace('Simba / Cub Simba / Graveyard death movement','Simba / Cub / Graveyard death movement')
 s=s.replace('Existing settings and other asset packages are preserved.','Existing settings and other asset packages are preserved.')
 s=s.replace('are updated; existing settings and other asset packages are preserved.\n','are updated; existing settings and other asset packages are preserved.\n\n'+note,1)
 s=s.replace('# Elephant Graveyard coverage fixes708','# Elephant Graveyard coverage fixes720').replace('# Current status708: Graveyard audit fixes delivered','# Current status720: Graveyard audit fixes delivered')
 p.write_text(s)
print('DOCUMENTED public720')
