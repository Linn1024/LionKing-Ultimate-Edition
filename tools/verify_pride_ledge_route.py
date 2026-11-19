"""Complete the ordinary cue-using Pride route and verify the later handoff."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_arrival_route.py')
source=original_verifier.read_text().replace("ROOT/'build/pride-arrival-work/player'","ROOT/'build/pride-ledge-work/player'")
source=source.replace('from summarize_pride_practice import bound','from pride_ledge_history import bound')
source=source.replace('audio.effects.world.pickup_arrival','audio.effects.simba.ledge_grab')
source=source.replace('TLK_PICKUP_ARRIVAL_TRACE','TLK_LEDGE_GRAB_TRACE').replace('arrival','ledge')
source=source.replace("len(events)==2 and all(r['timer']=='36' for r in events)","len(events)==5 and {r['entry'] for r in events}=={'c351a8','c3537a'}")
source=source.replace('(2 if selected else 0)','(5 if selected else 0)').replace("r['value']=='112'","r['value']=='94'")
source=source.replace('two_original_entries','five_original_entries').replace('first_2000_fields','first_4500_fields')
source=source.replace('both_cues_exercised_before_next_main_level','both_ledge_directions_exercised_before_next_main_level')
source=source.replace('paths=[Path(__file__),bp,',"paths=[Path(__file__),original_verifier,ROOT/'tools/pride_ledge_history.py',bp,")
exec(compile(source,str(original_verifier),'exec'))
