"""Publish separately selectable HUD components with existing installed data."""
from pathlib import Path
template=Path(__file__).with_name('publish_pride402.py')
s=template.read_text().replace('build/pride398/build-report.json','build/pride418/build-report.json').replace('build/pride401-ui/report.json','build/pride423-hud-ui/report.json')
s=s.replace("previous=ROOT/'dist/installed-preview390';out=ROOT/'dist/installed-preview398'","previous=ROOT/'dist/installed-preview398';out=ROOT/'dist/installed-preview418'")
s=s.replace("'build/pride402-publication'","'build/pride424-publication'")
s=s.replace("before.count('dist/installed-preview390')","before.count('dist/installed-preview398')").replace("before.replace('dist/installed-preview390','dist/installed-preview398')","before.replace('dist/installed-preview398','dist/installed-preview418')")
s=s.replace("info['available_md_preset_scope']='Resource editor MD/F7 drafts every currently available MD choice with inherited branches, explicit SNES overrides for unavailable leaves, individual overrides and ordinary Apply/restart. Existing settings/data unchanged until user applies.'", "info['independent_hud_scope']='Pride Lands roar meter, health meter and lives artwork can be selected independently; existing whole-HUD source remains their inherited parent. Live Apply; shared HUD palette remains independent.'")
s=s.replace("Preview398: Resources > MD (or F7 in the SDL editor) drafts all available MD\\nchoices. Unsupported choices remain SNES. Edit individual nodes, then Apply.","Preview418: Resources > Graphics > HUD > Meters and lives now contains\\nRoar meter, Health meter and Lives display. Choose each independently, then Apply.")
s=s.replace('paths=[Path(__file__),build,proof,launcher]',"render_proof=ROOT/'build/pride421-hud-play/report.json';assert bound(render_proof)['result']=='PASS'\npaths=[Path(__file__),template,build,proof,render_proof,launcher]")
exec(compile(s,str(template),'exec'))
