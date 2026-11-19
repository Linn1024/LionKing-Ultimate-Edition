"""Use an ordinary one-second Start release interval before resuming a paused reaction."""
from pathlib import Path
template=Path(__file__).with_name('verify_cant_wait583_pause.py')
s=template.read_text().replace('build/cant-wait583-pause','build/cant-wait584-pause').replace('2110,2111,2112','2150,2151,2152').replace("2150,True","2220,True").replace("state,2150)","state,2220)").replace('bytearray(2200*2)','bytearray(2300*2)')
exec(compile(s,str(template),'exec'))
