"""Combined sound walkthrough with explicit supported leaf choices."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait567_route_audio.py')
s=template.read_text().replace('build/cant-wait565/build-report.json','build/cant-wait572/build-report.json').replace('build/cant-wait567-route-audio','build/cant-wait573-route-audio')
leaves=['audio.effects.simba.roar','audio.effects.simba.hurt','audio.effects.world.checkpoint','audio.effects.world.continue_token']+['audio.effects.world.cant_wait.'+x for x in ('rhino','monkey_contacts','monkey_reaction','ostrich_steps','ostrich_jump','flying_takeoff','extra_life','bonus')]
s=s.replace('audio.effects = md\\n', ''.join(x+' = md\\n' for x in leaves)).replace(",('2','112')",'')
s=s.replace("native_music_no_md_track=", "profile_loaded='Saved resource profile loaded' in (out/'run.log').read_text(),native_music_no_md_track=")
exec(compile(s,str(template),'exec'))
