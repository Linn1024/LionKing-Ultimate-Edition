"""Install and publish the qualified opening-skull gameplay and MD socket artwork."""
from pathlib import Path
template=Path(__file__).with_name('publish_pride395.py')
s=template.read_text().replace('build/pride390/build-report.json','build/graveyard684/build-report.json')
s=s.replace("proofs=[ROOT/'build/pride391/report.json',ROOT/'build/pride392-route/report.json',ROOT/'build/pride394-qualification/report.json']", "proofs=[ROOT/'build/graveyard688-qualified/report.json']")
s=s.replace('build/pride389-cmake','build/graveyard683-helper').replace("previous=ROOT/'dist/installed-preview382';out=ROOT/'dist/installed-preview390'", "previous=ROOT/'dist/installed-preview659';out=ROOT/'dist/installed-preview684'")
s=s.replace('build/pride395-publication','build/graveyard689-publication').replace("before.count('dist/installed-preview382')","before.count('dist/installed-preview659')").replace("before.replace('dist/installed-preview382','dist/installed-preview390')","before.replace('dist/installed-preview659','dist/installed-preview684')")
s=s.replace('build/pride391/data','build/graveyard686-setup/data')
s=s.replace("info['required_sprite_assets_version']=2", "info['required_sprite_assets_version']=2;info['required_sprite_policy_sha256']=(helper.parent/'sprites.assets').read_bytes()[88:120].hex()")
s=s.replace("info['prepared_pride_gameplay_scope']='Sprite-v2 includes both default start positions, lizard reactivation flags,836 pose hitboxes and14 roar tokens/fire delay. Installed playback imports these tables; gameplay algorithms, artwork and source choices unchanged.'", "info['graveyard_skull_scope']='11 original MD eye-socket images/colors under independent existing hyena choices. Independent installed MD floor tags for hyena turn/jump decisions; opening skull jump geometry and synchronization verified against original MD. Previous gameplay records preserved. Native sequence timing and unrelated behavior remain; MD death motion still pending.'")
s=s.replace('Preview390 loads Pride start/reactivation/hitbox/roar tables from Setup.', 'Preview684 fixes MD opening-skull hyena convergence and supplies the separate MD eye-socket artwork/colors. Hyena turns and jump approach is independently selectable under Gameplay / Level layouts / Elephant Graveyard. Current installation updated automatically; settings preserved.')
s=s.replace("for p in (ROOT/folder).rglob('*') if p.is_file()}", "for p in (ROOT/folder).rglob('*') if p.is_file() and p.name!='last_session.rec'}")
s=s.replace('paths=[Path(__file__),build,helper,','paths=[Path(__file__),template,build,helper,')
exec(compile(s,str(template),'exec'))
