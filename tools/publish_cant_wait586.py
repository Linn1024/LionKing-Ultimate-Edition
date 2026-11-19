"""Publish qualified second-level sounds without reinstalling assets or replacing user settings."""
from pathlib import Path
template=Path(__file__).with_name('publish_pride402.py')
s=template.read_text().replace('build/pride398/build-report.json','build/cant-wait579/build-report.json').replace('build/pride401-ui/report.json','build/cant-wait581-audio-ui/report.json')
s=s.replace("previous=ROOT/'dist/installed-preview390';out=ROOT/'dist/installed-preview398'", "previous=ROOT/'dist/installed-preview536';out=ROOT/'dist/installed-preview579'")
s=s.replace('build/pride402-publication','build/cant-wait586-publication').replace("before.count('dist/installed-preview390')","before.count('dist/installed-preview536')").replace("before.replace('dist/installed-preview390','dist/installed-preview398')","before.replace('dist/installed-preview536','dist/installed-preview579')")
s=s.replace("info['available_md_preset_scope']=", "info['cant_wait_sound_scope']=")
a=s.index("'Resource editor MD/F7 drafts every");b=s.index("\n(out/'package.json')",a)
s=s[:a]+repr('Independent CW rhino/monkey/ostrich/flying-creature/extra-life/bonus effects, shared roar/hurt/checkpoint/Continue choices and existing level music. Native gameplay retained by user direction; prepared graphics/data unchanged.')+s[b:]
s=s.replace('Preview398: Resources > MD (or F7 in the SDL editor) drafts all available MD', 'Preview579: Direct second level: Play Cant Wait Mix.cmd. Resources > Audio >')
s=s.replace('choices. Unsupported choices remain SNES. Edit individual nodes, then Apply.', 'Sound effects > World effects > Can\'t Wait to Be King. Choose SNES/MD, then Apply.')
# Preserve the template's Python string literal when inserting the apostrophe.
s=s.replace("Can\'t Wait to Be King", "Can\\'t Wait to Be King")
s=s.replace("proof=ROOT/", "proofs=[ROOT/'build'/name/'report.json' for name in ('cant-wait573-route-audio','cant-wait574-native-control','cant-wait575-current-save','cant-wait580-continue-audio','cant-wait581-audio-ui','cant-wait584-pause')]\nfor p in proofs:assert bound(p)['result']=='PASS'\nproof=ROOT/",1)
s=s.replace("for p in (ROOT/folder).rglob('*') if p.is_file()}","for p in (ROOT/folder).rglob('*') if p.is_file() and p.name!='last_session.rec'}")
s=s.replace("ps=str(Path(os.environ", "settings=publication/'candidate-settings';settings.mkdir(exist_ok=True)\n(settings/'resources.ini').write_text((ROOT/'build/cant-wait573-route-audio/resources.ini').read_text()+'audio.music.cant_wait_to_be_king = md\\n')\nps=str(Path(os.environ")
s=s.replace("'-Frames','1'", "'-PracticeLevel','1','-Frames','1600','-SceneCapture',str(publication/'scene.json'),'-WindowCapture',str(publication/'window.png')")
s=s.replace("assert 'native_hud_assets=loaded'", "assert json.loads((publication/'scene.json').read_text())['level']==1\nassert 'Saved resource profile loaded' in (publication/'candidate-settings/last-launch.log').read_text()\nassert 'native_hud_assets=loaded'")
s=s.replace('paths=[Path(__file__),build,proof,launcher]', 'paths=[Path(__file__),template,build,*proofs,launcher]')
s=s.replace('full_first_level_complete=False', 'second_level_practical_goal_complete=True')
exec(compile(s,str(template),'exec'))
