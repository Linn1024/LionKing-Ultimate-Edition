"""Pause the real tree two fields into the first observed launch sound."""
import json
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_arrival_pause.py')
root=Path(__file__).resolve().parents[1]
reference=json.loads((root/'build/pride-lizard-launch-work/player/launch-audio-baselines/report.json').read_text())
assert reference['result']=='PASS'
pause_field=int(reference['events']['launch-aot'][0]['last_audio_frame'])+2
source=original_verifier.read_text().replace("ROOT/'build/pride-arrival-work/player'","ROOT/'build/pride-lizard-launch-work/player'")
source=source.replace('from summarize_pride_practice import bound','from pride_lizard_launch_history import bound')
source=source.replace('arrival-audio','launch-audio').replace('arrival-aot','launch-aot').replace('arrival-pause','launch-pause')
source=source.replace('audio.effects.world.pickup_arrival','audio.effects.world.lizard_launch')
source=source.replace('TLK_PICKUP_ARRIVAL_TRACE','TLK_LIZARD_LAUNCH_TRACE').replace('arrival.csv','launch.csv')
source=source.replace('1676',str(pause_field)).replace('2000','4500').replace('2001','4501')
source=source.replace("'--wav-seconds',60","'--wav-seconds',100")
source=source.replace('launch-audio/report.json','launch-audio-baselines/report.json')
source=source.replace('paths=[Path(__file__),bp,',"paths=[Path(__file__),original_verifier,ROOT/'tools/pride_lizard_launch_history.py',bp,")
exec(compile(source,str(original_verifier),'exec'))
