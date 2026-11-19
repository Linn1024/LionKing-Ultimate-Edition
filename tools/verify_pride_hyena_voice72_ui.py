"""Real pause/source/restart UI for the hyena voice; encounter playback is separate."""
from pathlib import Path
original=Path(__file__).with_name('verify_pride_music_ui65.py')
source=original.read_text().replace("ROOT/'build/pride-music-output65'","ROOT/'build/pride-hyena-voice72'")
source=source.replace("base/'windows-ui'","base/'voice-ui'")
source=source.replace("node='audio.music.pride_lands'","node='audio.effects.world.hyena_hurt'")
source=source.replace("r['field']>=1200 and r['descriptor']==0xc00387","r['field']>=2200 and r['descriptor']==0xc00387")
anchor="checks[label+'_actual_driver_selection']=(137 in tracks) if choice==2 else (137 not in tracks)"
assert source.count(anchor)==1
source=source.replace(anchor,"checks[label+'_no_hyena_voice_outside_encounter']=not any(r['selector']=='19' and r['value']=='4' for r in drivers()[count:])")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original,')
exec(compile(source,str(original),'exec'))
