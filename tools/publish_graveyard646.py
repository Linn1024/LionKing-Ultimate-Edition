"""Publish Graveyard death/retry music without changing installed assets or user choices."""
from pathlib import Path
template=Path(__file__).with_name('publish_pride402.py')
s=template.read_text().replace('build/pride398/build-report.json','build/graveyard644/build-report.json').replace('build/pride401-ui/report.json','build/graveyard645-death-qualified/report.json')
s=s.replace("previous=ROOT/'dist/installed-preview390';out=ROOT/'dist/installed-preview398'", "previous=ROOT/'dist/installed-preview621';out=ROOT/'dist/installed-preview644'")
s=s.replace('build/pride402-publication','build/graveyard646-publication').replace("before.count('dist/installed-preview390')","before.count('dist/installed-preview621')").replace("before.replace('dist/installed-preview390','dist/installed-preview398')","before.replace('dist/installed-preview621','dist/installed-preview644')")
s=s.replace("info['available_md_preset_scope']=", "info['graveyard_death_music_scope']=")
a=s.index("'Resource editor MD/F7 drafts every");b=s.index("\n(out/'package.json')",a)
s=s[:a]+repr('Graveyard music is a group with independent Level track and Health-death cue children. Existing parent MD selection inherits both: program83, shared original death430, then83 on retry. Native paths retained. Nonfinal health-death/retry, native control, independent choices, current mid-death save and real editor restart qualified; actual Graveyard fall/final-life cases not separately qualified.')+s[b:]
s=s.replace('Preview398: Resources > MD (or F7 in the SDL editor) drafts all available MD','Preview644 fixes Elephant Graveyard health-death music and retry. Existing MD')
s=s.replace('choices. Unsupported choices remain SNES. Edit individual nodes, then Apply.','music selection now inherits Level track and Health-death cue. Override either under Resources > Audio > Music > Elephant Graveyard. No Setup needed.')
s=s.replace("for p in (ROOT/folder).rglob('*') if p.is_file()}", "for p in (ROOT/folder).rglob('*') if p.is_file() and p.name!='last_session.rec'}")
s=s.replace('paths=[Path(__file__),build,proof,launcher]', 'paths=[Path(__file__),template,build,proof,launcher]')
exec(compile(s,str(template),'exec'))
