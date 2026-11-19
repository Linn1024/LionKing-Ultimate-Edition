"""Publish focused Graveyard HUD/hyena choices; retain active full-level goal."""
from pathlib import Path
template=Path(__file__).with_name('publish_pride402.py')
s=template.read_text().replace('build/pride398/build-report.json','build/graveyard503/build-report.json').replace('build/pride401-ui/report.json','build/graveyard512-ui/report.json')
s=s.replace("previous=ROOT/'dist/installed-preview390';out=ROOT/'dist/installed-preview398'", "previous=ROOT/'dist/installed-preview482';out=ROOT/'dist/installed-preview503'")
s=s.replace('build/pride402-publication','build/graveyard514-publication').replace("before.count('dist/installed-preview390')","before.count('dist/installed-preview482')").replace("before.replace('dist/installed-preview390','dist/installed-preview398')","before.replace('dist/installed-preview482','dist/installed-preview503')")
s=s.replace("info['available_md_preset_scope']='Resource editor MD/F7 drafts every currently available MD choice with inherited branches, explicit SNES overrides for unavailable leaves, individual overrides and ordinary Apply/restart. Existing settings/data unchanged until user applies.'", "info['graveyard_hud_hyena_scope']='Live roar/health/lives HUD and independently selected hyena frames/palette in owned Elephant Graveyard actors. Existing reviewed pose pairs and prepared scene-specific MD colors; native animation/gameplay/audio retained. Full Graveyard goal remains active.'")
s=s.replace('Preview398: Resources > MD (or F7 in the SDL editor) drafts all available MD\\nchoices. Unsupported choices remain SNES. Edit individual nodes, then Apply.', 'Preview503: Elephant Graveyard supports shared HUD and independent hyena art/colors.\\nF12 Resources: choose Hyenas and Meters and lives, then Apply. Full-level goal active.')
s=s.replace("previous=ROOT/'dist/installed-preview482'", "proofs=[ROOT/'build'/name/'report.json' for name in ('graveyard494-hud','graveyard504-hyenas')]\nfor p in proofs:assert bound(p)['result']=='PASS'\nprevious=ROOT/'dist/installed-preview482'")
s=s.replace('paths=[Path(__file__),build,proof,launcher]', 'paths=[Path(__file__),template,build,proof,*proofs,launcher]')
# A concurrently played game appends this recording; publication never writes it.
# Continue protecting all installed assets and actual settings/profile files.
s=s.replace("for p in (ROOT/folder).rglob('*') if p.is_file()}", "for p in (ROOT/folder).rglob('*') if p.is_file() and p.name!='last_session.rec'}")
exec(compile(s,str(template),'exec'))
