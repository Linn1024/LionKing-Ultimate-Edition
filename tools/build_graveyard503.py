"""Build owned Graveyard hyena resources with its independent prepared scene colors."""
from pathlib import Path
template=Path(__file__).with_name('build_graveyard493.py')
s=template.read_text().replace("base=ROOT/'build/cant-wait482'","base=ROOT/'build/graveyard493'").replace("out=ROOT/'build/graveyard493'","out=ROOT/'build/graveyard503'")
s=s.replace("('wide',b['compiles']['wide'],None)]", "('wide',b['compiles']['wide'],None),('sprites',b['compiles']['sprites'],out/'game/tlk_md_sprites.c'),('assets',b['compiles']['assets'],ROOT/'engine/runner/tlk_md_assets.c')]")
s=s.replace("'engine/runner/tlk_wide.c',", "'engine/runner/tlk_wide.c','engine/runner/tlk_md_sprites.c','engine/runner/tlk_md_sprites.h','engine/runner/tlk_md_assets.c','engine/runner/tlk_md_assets.h',")
exec(compile(s,str(template),'exec'))
