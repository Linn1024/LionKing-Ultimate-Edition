"""Prepare a dedicated all-available-MD Graveyard profile through the installed resource editor."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait581_audio_ui.py')
s=template.read_text().replace('build/cant-wait573-route-audio/report.json','build/graveyard601-native-music/report.json').replace('build/cant-wait579/build-report.json','build/graveyard644/build-report.json').replace('build/cant-wait581-audio-ui','build/graveyard650-md-preset').replace("r['commands']['route']","r['commands']['play']")
s=s.replace("cmd[0]=str(build.parent/'player.exe')", "cmd[0]=str(ROOT/'dist/installed-preview644/LionKing.exe')")
s=s.replace('i=cmd.index(flag);del cmd[i:i+n]', 'if flag in cmd:\n        i=cmd.index(flag);del cmd[i:i+n]')
s=s.replace("cmd+=['--menu-at'", "cmd[cmd.index('--sprite-assets')+1]=str(ROOT/'build/graveyard619-helper/sprites.assets')\ncmd+=['--menu-at'")
a=s.index('        key(0x24)');b=s.index('    finally:',a)
s=s[:a]+'''        key(0x76);draft=wait(lambda r:r['modal'] and choices(r)['game'][1]==2);snapshots['draft']=draft
        capture_client(hwnd,out/'md-options.png');key(0x1b);key(0x71)
        restarted=wait(lambda r:not r['menu'] and r['field']<1600);snapshots['restart']=restarted
        after=wait(lambda r:not r['menu'] and r['field']>=1580 and r['descriptor']==0xc003eb and r['health']>0 and r['macro_index']==r['macro_length']);snapshots['after']=after
        capture_client(hwnd,out/'gameplay.png');c=choices(after)
        supported=('display.viewport','graphics.scenery.foreground','graphics.scenery.background','graphics.scenery.palettes','graphics.sprites.simba.cub.frames','graphics.sprites.enemies.hyenas.frames','graphics.sprites.enemies.vultures.frames','graphics.sprites.bones.palette','graphics.hud.frames','audio.music.elephant_graveyard.track','audio.music.elephant_graveyard.death','audio.effects.world.graveyard.vulture','audio.effects.world.graveyard.bone_platform','audio.effects.world.graveyard.pillar','gameplay.levels.elephant_graveyard.vulture_health','gameplay.levels.elephant_graveyard.vulture_bounds')
        checks['all_reviewed_md_choices']=all(c[n][4]==2 for n in supported)
        checks['unsupported_choices_native']=all(c[n][4]==1 for n in ('gameplay.simba.movement','gameplay.simba.combat','gameplay.levels.other','audio.voices'))
        checks['md_root_persisted']='game = md' in (out/'resources.ini').read_text()
        checks['playable_graveyard']=after['level']==2 and after['health']>0
''' +s[b:]
s=s.replace("paths=[Path(__file__),reference,build]", "assert all(checks.values()),checks\nprofile=ROOT/'profiles/graveyard-md.ini';assert not profile.exists();profile.write_bytes((out/'resources.ini').read_bytes())\npaths=[Path(__file__),template,reference,build,profile]")
exec(compile(s,str(template),'exec'))
