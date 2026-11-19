"""Actual independent vulture gameplay leaf Apply and appropriate level restart."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait581_audio_ui.py')
s=template.read_text().replace('build/cant-wait573-route-audio/report.json','build/graveyard601-native-music/report.json').replace('build/cant-wait579/build-report.json','build/graveyard621/build-report.json').replace('build/cant-wait581-audio-ui','build/graveyard625-ui').replace("r['commands']['route']","r['commands']['play']")
s=s.replace('audio.effects.world.cant_wait.ostrich_steps','gameplay.levels.elephant_graveyard.vulture_health').replace('audio.effects.world.cant_wait.ostrich_jump','gameplay.levels.elephant_graveyard.vulture_bounds')
s=s.replace('i=cmd.index(flag);del cmd[i:i+n]', 'if flag in cmd:\n        i=cmd.index(flag);del cmd[i:i+n]')
s=s.replace("cmd+=['--menu-at'", "cmd[cmd.index('--sprite-assets')+1]=str(ROOT/'build/graveyard619-helper/sprites.assets')\ncmd+=['--menu-at'")
s=s.replace("r['field']>=1900", "r['field']>=1580").replace('0xc003b9','0xc003eb').replace("after['level']==1","after['level']==2")
s=s.replace('range(210)','range(300)').replace('paths=[Path(__file__),reference,build]','paths=[Path(__file__),template,reference,build]')
exec(compile(s,str(template),'exec'))
