"""Publish qualified Graveyard effects, retaining installed resources and user choices."""
from pathlib import Path
template=Path(__file__).with_name('publish_pride402.py')
s=template.read_text().replace('build/pride398/build-report.json','build/graveyard609/build-report.json').replace('build/pride401-ui/report.json','build/graveyard613-sound-delivery/report.json')
s=s.replace("previous=ROOT/'dist/installed-preview390';out=ROOT/'dist/installed-preview398'", "previous=ROOT/'dist/installed-preview579';out=ROOT/'dist/installed-preview609'")
s=s.replace('build/pride402-publication','build/graveyard615-publication').replace("before.count('dist/installed-preview390')","before.count('dist/installed-preview579')").replace("before.replace('dist/installed-preview390','dist/installed-preview398')","before.replace('dist/installed-preview579','dist/installed-preview609')")
s=s.replace("info['available_md_preset_scope']=", "info['graveyard_sound_scope']=")
a=s.index("'Resource editor MD/F7 drafts every");b=s.index("\n(out/'package.json')",a)
s=s[:a]+repr('Independent Graveyard vulture, shaking/moving/crumbling bone and pillar effects; shared Simba/hyena/pickup/arrival voices. Native gameplay retained; existing graphics and prepared packages unchanged. Audio Apply restarts level.')+s[b:]
s=s.replace('Preview398: Resources > MD (or F7 in the SDL editor) drafts all available MD','Preview609: Launch Play Elephant Graveyard Mix.cmd. Resources > Audio >')
s=s.replace('choices. Unsupported choices remain SNES. Edit individual nodes, then Apply.','Sound effects > World effects > Elephant Graveyard. Shared Simba/hyena/pickup leaves remain separate. Choose sources and Apply.')
s=s.replace("for p in (ROOT/folder).rglob('*') if p.is_file()}","for p in (ROOT/folder).rglob('*') if p.is_file() and p.name!='last_session.rec'}")
s=s.replace("ps=str(Path(os.environ", "settings=publication/'candidate-settings';settings.mkdir(exist_ok=True)\n(settings/'resources.ini').write_bytes((ROOT/'build/graveyard606-route-audio/resources.ini').read_bytes())\nps=str(Path(os.environ")
s=s.replace("'-Frames','1'", "'-PracticeLevel','2','-Frames','1600','-SceneCapture',str(publication/'scene.json'),'-WindowCapture',str(publication/'window.png')")
s=s.replace("assert 'native_hud_assets=loaded'", "assert json.loads((publication/'scene.json').read_text())['level']==2\nassert 'Saved resource profile loaded' in (publication/'candidate-settings/last-launch.log').read_text()\nassert 'native_hud_assets=loaded'")
s=s.replace('paths=[Path(__file__),build,proof,launcher]', 'paths=[Path(__file__),template,build,proof,launcher]')
s=s.replace('full_first_level_complete=False', 'graveyard_practical_sound_goal_complete=True')
exec(compile(s,str(template),'exec'))
