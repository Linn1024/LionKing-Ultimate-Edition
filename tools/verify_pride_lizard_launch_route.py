"""Complete the ordinary route with both launch cues and inspect the handoff."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_arrival_route.py')
source=original_verifier.read_text().replace('pride-arrival-work','pride-lizard-launch-work')
source=source.replace('from summarize_pride_practice import bound','from pride_lizard_launch_history import bound')
source=source.replace('audio.effects.world.pickup_arrival','audio.effects.world.lizard_launch')
source=source.replace('TLK_PICKUP_ARRIVAL_TRACE','TLK_LIZARD_LAUNCH_TRACE').replace('arrival','launch')
source=source.replace('launch-audio/report.json','launch-audio-baselines/report.json')
source=source.replace("r['timer']=='36'","r['timer']=='20'")
source=source.replace("r['value']=='112'","r['value']=='123'")
source=source.replace('first_2000_fields','first_4500_fields')
source=source.replace('paths=[Path(__file__),bp,',"paths=[Path(__file__),original_verifier,ROOT/'tools/pride_lizard_launch_history.py',bp,")
exec(compile(source,str(original_verifier),'exec'))
