"""Build scripted hyena coverage, Graveyard hyena contacts and MD cub roar."""
from pathlib import Path
template=Path(__file__).with_name('build_graveyard684.py')
s=template.read_text().replace("bp=ROOT/'build/graveyard659/build-report.json'", "bp=ROOT/'build/graveyard684/build-report.json'").replace("out=ROOT/'build/graveyard684'", "out=ROOT/'build/graveyard704'")
a=s.index('tasks=[');b=s.index('for label,template,src,added in tasks:',a)
s=s[:a]+"tasks=[(label,b['compiles'][label],out/'game'/('tlk_'+label+'.c') if label in ('resources','audio') else None,False) for label in ('resources','audio','wide','hyena_audio','roar','graveyard_gameplay','hitboxes')]\n"+s[b:]
s=s.replace("'tlk_wide.c','tlk_md_sprites.c'", "'tlk_wide.c','tlk_hyena_audio.c','tlk_hitboxes.c','tlk_roar.c','tlk_graveyard_hyena_owner.h','tlk_md_sprites.c'")
exec(compile(s,str(template),'exec'))
