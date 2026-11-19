"""Publish the live second-level monkey palette without new installed payloads."""
from pathlib import Path
template=Path(__file__).with_name('publish_pride402.py')
s=template.read_text().replace('build/pride398/build-report.json','build/cant-wait440/build-report.json').replace('build/pride401-ui/report.json','build/cant-wait442-ui/report.json')
s=s.replace("previous=ROOT/'dist/installed-preview390';out=ROOT/'dist/installed-preview398'","previous=ROOT/'dist/installed-preview418';out=ROOT/'dist/installed-preview440'")
s=s.replace("'build/pride402-publication'","'build/cant-wait443-publication'")
s=s.replace("before.count('dist/installed-preview390')","before.count('dist/installed-preview418')").replace("before.replace('dist/installed-preview390','dist/installed-preview398')","before.replace('dist/installed-preview418','dist/installed-preview440')")
s=s.replace("info['available_md_preset_scope']='Resource editor MD/F7 drafts every currently available MD choice with inherited branches, explicit SNES overrides for unavailable leaves, individual overrides and ordinary Apply/restart. Existing settings/data unchanged until user applies.'", "info['cant_wait_monkey_palette_scope']='Independent original MD monkey colors in the second level, 29 reviewed shared poses, both coat palettes, current live scene palette and original native/flash guards. Live Apply; artwork and gameplay unchanged.'")
s=s.replace("Preview398: Resources > MD (or F7 in the SDL editor) drafts all available MD\\nchoices. Unsupported choices remain SNES. Edit individual nodes, then Apply.","Preview440: Resources > Graphics > Sprites > Animals > Monkeys > Palette\\nselects MD colors live in the second level; existing scene palettes are reused.")
s=s.replace('paths=[Path(__file__),build,proof,launcher]',"render_proof=ROOT/'build/cant-wait441-monkeys/report.json';assert bound(render_proof)['result']=='PASS'\npaths=[Path(__file__),template,build,proof,render_proof,launcher]")
exec(compile(s,str(template),'exec'))
