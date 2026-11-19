"""Publish verified Graveyard music ownership, retaining native gameplay and the all-MD launcher."""
from pathlib import Path
template=Path(__file__).with_name('publish_pride402.py')
s=template.read_text().replace('build/pride398/build-report.json','build/graveyard659/build-report.json').replace('build/pride401-ui/report.json','build/graveyard669-skull-qualified/report.json')
s=s.replace("previous=ROOT/'dist/installed-preview390';out=ROOT/'dist/installed-preview398'", "previous=ROOT/'dist/installed-preview652';out=ROOT/'dist/installed-preview659'")
s=s.replace('build/pride402-publication','build/graveyard670-publication').replace("before.count('dist/installed-preview390')","before.count('dist/installed-preview652')").replace("before.replace('dist/installed-preview390','dist/installed-preview398')","before.replace('dist/installed-preview652','dist/installed-preview659')")
s=s.replace("info['available_md_preset_scope']=", "info['graveyard_music_ownership_scope']=")
a=s.index("'Resource editor MD/F7 drafts every");b=s.index("\n(out/'package.json')",a)
s=s[:a]+repr('Graveyard selected MD music now suppresses only verified native music voices at DSP output, including death-bank music; original SPC queue remains active, native sound effects independent. Removes confirmed native/MD death-song overlap. Hyena artwork is mapped MD; sequence/timing/AI and Graveyard death presentation remain native. An unsuccessful query-height prototype was reverted and is not shipped.')+s[b:]
s=s.replace('Preview398: Resources > MD (or F7 in the SDL editor) drafts all available MD','Preview659: Play Elephant Graveyard MD.cmd retains all supported MD choices.')
s=s.replace('choices. Unsupported choices remain SNES. Edit individual nodes, then Apply.','Fixed native music overlapping the selected MD death cue; native sound effects preserved. No Setup needed.')
s=s.replace("for p in (ROOT/folder).rglob('*') if p.is_file()}", "for p in (ROOT/folder).rglob('*') if p.is_file() and p.name!='last_session.rec'}")
s=s.replace('paths=[Path(__file__),build,proof,launcher]', 'paths=[Path(__file__),template,build,proof,launcher]')
exec(compile(s,str(template),'exec'))
