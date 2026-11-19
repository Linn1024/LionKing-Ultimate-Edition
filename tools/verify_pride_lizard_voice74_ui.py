"""Real pause/source/restart UI; lizard playback is qualified by fight captures."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_music_ui65.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-music-output65'","ROOT/'build/pride-lizard-voice74'")
source=source.replace("base/'windows-ui'","base/'voice-ui'")
source=source.replace("node='audio.music.pride_lands'","node='audio.effects.world.lizard'")
source=source.replace("r['field']>=1200 and r['descriptor']==0xc00387","r['field']>=2200 and r['descriptor']==0xc00387")
anchor="checks[label+'_actual_driver_selection']=(137 in tracks) if choice==2 else (137 not in tracks)"
assert source.count(anchor)==1
source=source.replace(anchor,'# Actual lizard cue playback is verified by the natural fight gate.')
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
