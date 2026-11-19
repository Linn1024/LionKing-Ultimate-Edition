"""Build all four Graveyard audit fixes, including saved presentation-only MD death movement."""
from pathlib import Path
template=Path(__file__).with_name('build_graveyard704.py')
s=template.read_text().replace('build/graveyard704','build/graveyard708')
s=s.replace("'graveyard_gameplay','hitboxes')", "'graveyard_gameplay','hitboxes','graveyard_data','sprites')")
s=s.replace("label in ('resources','audio')", "label in ('resources','audio','sprites')")
s=s.replace("('tlk_'+label+'.c')", "('tlk_md_sprites.c' if label=='sprites' else 'tlk_'+label+'.c')")
s=s.replace("'tlk_graveyard_hyena_owner.h'", "'tlk_graveyard_hyena_owner.h','tlk_wide.h','tlk_md_sprite_format.inc'")
exec(compile(s,str(template),'exec'))
