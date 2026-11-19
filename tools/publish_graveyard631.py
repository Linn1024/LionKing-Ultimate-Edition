"""Publish qualified independent Graveyard vulture gameplay, upgrading native prepared data and retaining choices."""
from pathlib import Path
template=Path(__file__).with_name('publish_pride395.py')
s=template.read_text().replace('build/pride390/build-report.json','build/graveyard621/build-report.json')
s=s.replace("proofs=[ROOT/'build/pride391/report.json',ROOT/'build/pride392-route/report.json',ROOT/'build/pride394-qualification/report.json']", "proofs=[ROOT/'build/graveyard630-gameplay-qualified/report.json']")
s=s.replace('build/pride389-cmake','build/graveyard619-helper').replace("previous=ROOT/'dist/installed-preview382';out=ROOT/'dist/installed-preview390'", "previous=ROOT/'dist/installed-preview609';out=ROOT/'dist/installed-preview621'")
s=s.replace('build/pride395-publication','build/graveyard631-publication').replace("before.count('dist/installed-preview382')","before.count('dist/installed-preview609')").replace("before.replace('dist/installed-preview382','dist/installed-preview390')","before.replace('dist/installed-preview609','dist/installed-preview621')")
s=s.replace('build/pride391/data','build/graveyard627-setup/data')
s=s.replace("info['required_sprite_assets_version']=2", "info['required_sprite_assets_version']=2;info['required_sprite_policy_sha256']=(helper.parent/'sprites.assets').read_bytes()[88:120].hex()")
s=s.replace("info['prepared_pride_gameplay_scope']='Sprite-v2 includes both default start positions, lizard reactivation flags,836 pose hitboxes and14 roar tokens/fire delay. Installed playback imports these tables; gameplay algorithms, artwork and source choices unchanged.'", "info['graveyard_gameplay_scope']='Independent patrolling-vulture health (MD difficulty+1) and four original MD pose collision rectangles, prepared during Setup. Appropriate level restart.840 prepared pose records preserve all prior836. Other native rules retained; broader AI parity and a full MD-gameplay walkthrough are not claimed.'")
s=s.replace('Preview390 loads Pride start/reactivation/hitbox/roar tables from Setup.', 'Preview621: Gameplay > Level layouts > Elephant Graveyard offers independent Patrolling vulture health and Vulture contact boxes. Choose MD and Apply; this restarts the level.')
s=s.replace("for p in (ROOT/folder).rglob('*') if p.is_file()}", "for p in (ROOT/folder).rglob('*') if p.is_file() and p.name!='last_session.rec'}")
s=s.replace('paths=[Path(__file__),build,helper,','paths=[Path(__file__),template,build,helper,')
exec(compile(s,str(template),'exec'))
