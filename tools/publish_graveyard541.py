"""Publish prepared vulture choices and live bone colors after focused qualification."""
from pathlib import Path
template=Path(__file__).with_name('publish_pride395.py')
s=template.read_text().replace('build/pride390/build-report.json','build/graveyard536/build-report.json')
s=s.replace("proofs=[ROOT/'build/pride391/report.json',ROOT/'build/pride392-route/report.json',ROOT/'build/pride394-qualification/report.json']", "proofs=[ROOT/'build'/name/'report.json' for name in ('graveyard531-vultures','graveyard532-ui','graveyard538-setup','graveyard539-ui','graveyard540-bones-qualified','graveyard516-route')]")
s=s.replace('build/pride389-cmake','build/graveyard529-helper').replace("previous=ROOT/'dist/installed-preview382';out=ROOT/'dist/installed-preview390'", "previous=ROOT/'dist/installed-preview503';out=ROOT/'dist/installed-preview536'")
s=s.replace('build/pride395-publication','build/graveyard541-publication').replace("before.count('dist/installed-preview382')","before.count('dist/installed-preview503')").replace("before.replace('dist/installed-preview382','dist/installed-preview390')","before.replace('dist/installed-preview503','dist/installed-preview536')")
s=s.replace('build/pride391/data','build/graveyard538-setup/data')
s=s.replace("info['required_sprite_assets_version']=2", "info['required_sprite_assets_version']=2;info['required_sprite_policy_sha256']=(helper.parent/'sprites.assets').read_bytes()[88:120].hex()")
s=s.replace("info['prepared_pride_gameplay_scope']='Sprite-v2 includes both default start positions, lizard reactivation flags,836 pose hitboxes and14 roar tokens/fire delay. Installed playback imports these tables; gameplay algorithms, artwork and source choices unchanged.'", "info['graveyard_vulture_bone_scope']='46 original MD vulture animation-phase images with independent scene-specific colors, five verified native owners and preserved flashes; independent four moving-bone-platform colors with native shared drawings/motion. Existing art/gameplay payloads retained except newly prepared original native vulture palette5. Native timing/gameplay/effects retained.'")
s=s.replace('Preview390 loads Pride start/reactivation/hitbox/roar tables from Setup.', 'Preview536 adds Vultures frames/palette and Bone platforms palette; live Apply in Graveyard.')
s=s.replace("for p in (ROOT/folder).rglob('*') if p.is_file()}", "for p in (ROOT/folder).rglob('*') if p.is_file() and p.name!='last_session.rec'}")
s=s.replace('paths=[Path(__file__),build,helper,','paths=[Path(__file__),template,build,helper,')
exec(compile(s,str(template),'exec'))
