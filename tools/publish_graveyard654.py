"""Publish the all-available-MD Graveyard launcher and its scoped practice-menu guard fix."""
from pathlib import Path
template=Path(__file__).with_name('publish_pride402.py')
s=template.read_text().replace('build/pride398/build-report.json','build/graveyard652/build-report.json').replace('build/pride401-ui/report.json','build/graveyard653-md-launcher/report.json')
s=s.replace("previous=ROOT/'dist/installed-preview390';out=ROOT/'dist/installed-preview398'", "previous=ROOT/'dist/installed-preview644';out=ROOT/'dist/installed-preview652'")
s=s.replace('build/pride402-publication','build/graveyard654-publication').replace("before.count('dist/installed-preview390')","before.count('dist/installed-preview644')").replace("before.replace('dist/installed-preview390','dist/installed-preview398')","before.replace('dist/installed-preview644','dist/installed-preview652')")
s=s.replace("info['available_md_preset_scope']=", "info['graveyard_md_launcher_scope']=")
a=s.index("'Resource editor MD/F7 drafts every");b=s.index("\n(out/'package.json')",a)
s=s[:a]+repr('Play Elephant Graveyard MD.cmd starts our port at Graveyard with every currently ready MD choice selected, using the real Available MD profile and separate settings/graveyard-md. Unsupported choices explicitly SNES. Title navigation adapter skips the direct later-level Options shortcut, retaining native Options input rather than exiting120. Existing native controls preserved; other linked code retained.')+s[b:]
s=s.replace('Preview398: Resources > MD (or F7 in the SDL editor) drafts all available MD','Preview652: Play Elephant Graveyard MD.cmd selects all available MD sources')
s=s.replace('choices. Unsupported choices remain SNES. Edit individual nodes, then Apply.','and starts Graveyard directly. Separate settings/graveyard-md; existing mix choices preserved.')
s=s.replace("for p in (ROOT/folder).rglob('*') if p.is_file()}", "for p in (ROOT/folder).rglob('*') if p.is_file() and p.name!='last_session.rec'}")
s=s.replace('paths=[Path(__file__),build,proof,launcher]', "paths=[Path(__file__),template,build,proof,launcher,ROOT/'Play Elephant Graveyard MD.cmd',ROOT/'profiles/graveyard-md.ini']")
exec(compile(s,str(template),'exec'))
