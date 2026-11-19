"""Publish installed rhino art and the native preparer after focused level-select checks."""
from pathlib import Path
template=Path(__file__).with_name('publish_pride395.py')
s=template.read_text().replace('build/pride390/build-report.json','build/cant-wait460/build-report.json')
s=s.replace("proofs=[ROOT/'build/pride391/report.json',ROOT/'build/pride392-route/report.json',ROOT/'build/pride394-qualification/report.json']", "proofs=[ROOT/'build/cant-wait462-rhino/report.json',ROOT/'build/cant-wait463-ui/report.json',ROOT/'build/cant-wait464-setup/report.json']")
s=s.replace('build/pride389-cmake','build/cant-wait459-helper').replace("previous=ROOT/'dist/installed-preview382';out=ROOT/'dist/installed-preview390'", "previous=ROOT/'dist/installed-preview448';out=ROOT/'dist/installed-preview460'")
s=s.replace('build/pride395-publication','build/cant-wait466-publication').replace("before.count('dist/installed-preview382')","before.count('dist/installed-preview448')").replace("before.replace('dist/installed-preview382','dist/installed-preview390')","before.replace('dist/installed-preview448','dist/installed-preview460')")
s=s.replace('build/pride391/data','build/cant-wait464-setup/data')
s=s.replace("info['prepared_pride_gameplay_scope']='Sprite-v2 includes both default start positions, lizard reactivation flags,836 pose hitboxes and14 roar tokens/fire delay. Installed playback imports these tables; gameplay algorithms, artwork and source choices unchanged.'", "info['prepared_rhino_scope']='Second-level original MD head artwork for13 native poses, nine MD images, original live palette1 and independent native/MD frames/palette. Native timing/gameplay retained; old art/gameplay payloads exact.'")
s=s.replace('Preview390 loads Pride start/reactivation/hitbox/roar tables from Setup.', 'Preview460 adds Resources > Graphics > Sprites > Animals > Rhinos frames/palette.').replace('paths=[Path(__file__),build,helper,','paths=[Path(__file__),template,build,helper,')
exec(compile(s,str(template),'exec'))
