"""Build gorilla frame/palette choices using installer-owned original data."""
from pathlib import Path
template=Path(__file__).with_name('build_next743.py')
s=template.read_text().replace("bp=ROOT/'build/graveyard720/build-report.json'", "bp=ROOT/'build/hakuna795/build-report.json'").replace("out=ROOT/'build/next743'", "out=ROOT/'build/hakuna802'")
s=s.replace("('resources','audio','wide','sprites','assets','pride_data','roar','lizard')", "('resources','wide','sprites','next_scene_data')")
a=s.index('db=json.loads(');b=s.index('for label,template,src,added in tasks:',a);s=s[:a]+s[b:]
s=s.replace("src=out/'game'/", "src=out/'game'/")
# next_scene_data's original compile points at the maintained runner source.
s=s.replace("'tlk_md_sprite_format.inc','tlk_lizard_audio.c'", "'tlk_md_sprite_format.inc','tlk_lizard_audio.c'")
exec(compile(s,str(template),'exec'))
