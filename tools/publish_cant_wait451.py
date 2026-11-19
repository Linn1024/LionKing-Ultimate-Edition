"""Publish independent ostrich colors alongside the existing monkey choice."""
from pathlib import Path
template=Path(__file__).with_name('publish_cant_wait443.py')
s=template.read_text().replace('build/cant-wait440/build-report.json','build/cant-wait448/build-report.json').replace('build/cant-wait442-ui/report.json','build/cant-wait450-ui/report.json')
s=s.replace("previous=ROOT/'dist/installed-preview418';out=ROOT/'dist/installed-preview440'","previous=ROOT/'dist/installed-preview440';out=ROOT/'dist/installed-preview448'")
s=s.replace('build/cant-wait443-publication','build/cant-wait451-publication').replace("before.count('dist/installed-preview418')","before.count('dist/installed-preview440')").replace("before.replace('dist/installed-preview418','dist/installed-preview440')","before.replace('dist/installed-preview440','dist/installed-preview448')")
s=s.replace('cant_wait_monkey_palette_scope','cant_wait_animal_palette_scope').replace('Independent original MD monkey colors in the second level, 29 reviewed shared poses, both coat palettes, current live scene palette and original native/flash guards. Live Apply; artwork and gameplay unchanged.','Independent original MD monkey and ostrich colors:29/12 reviewed shared poses, live scene palette, physical draw/actor ownership and native/flash guards. Live Apply; artwork and gameplay unchanged.')
s=s.replace('Preview440: Resources > Graphics > Sprites > Animals > Monkeys > Palette','Preview448: Resources > Graphics > Sprites > Animals > Ostriches > Palette').replace('build/cant-wait441-monkeys/report.json','build/cant-wait449-ostrich/report.json')
exec(compile(s,str(template),'exec'))
