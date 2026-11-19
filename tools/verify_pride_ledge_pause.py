"""Pause the actual resource tree during the ledge cue and resume exactly."""
from pathlib import Path

original=Path(__file__).with_name('verify_pride_arrival_pause.py')
source=original.read_text().replace("ROOT/'build/pride-arrival-work/player'","ROOT/'build/pride-ledge-work/player'")
source=source.replace('from summarize_pride_practice import bound','from pride_ledge_history import bound')
source=source.replace('arrival-audio','ledge-audio').replace('arrival-aot','ledge-aot').replace('arrival-pause','ledge-pause2')
source=source.replace('audio.effects.world.pickup_arrival','audio.effects.simba.ledge_grab')
source=source.replace('TLK_PICKUP_ARRIVAL_TRACE','TLK_LEDGE_GRAB_TRACE').replace('arrival.csv','ledge.csv')
source=source.replace('1676','1477').replace('2000','4500').replace('2001','4501')
source=source.replace("'--wav-seconds',60","'--wav-seconds',100")
source=source.replace('paths=[Path(__file__),bp,',"paths=[Path(__file__),original,ROOT/'tools/pride_ledge_history.py',bp,")
exec(compile(source,str(original),'exec'))
