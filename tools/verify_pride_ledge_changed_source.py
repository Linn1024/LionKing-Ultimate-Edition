"""Changing ledge audio on a mid-chime cold load must discard the old MD tail."""
from pathlib import Path

original=Path(__file__).with_name('verify_pride_arrival_changed_source.py')
source=original.read_text().replace("ROOT/'build/pride-arrival-work/player'","ROOT/'build/pride-ledge-work/player'")
source=source.replace('from summarize_pride_practice import bound','from pride_ledge_history import bound')
source=source.replace('arrival-saves','ledge-saves').replace('arrival-audio','ledge-audio').replace('arrival-changed-source','ledge-changed-source')
source=source.replace('TLK_PICKUP_ARRIVAL_TRACE','TLK_LEDGE_GRAB_TRACE').replace('arrival.csv','ledge.csv')
source=source.replace('1676','1477').replace("'--frames',2000","'--frames',4500")
source=source.replace('import os','import os\nimport re')
source=source.replace('from verify_windows import hashes,pixels',"""from verify_windows import hashes,pixels
def continued_rows(path):
    return re.findall(r'frame=(\\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',path.read_text())
""")
source=source.replace("'--load',state,'--frames',4500,","'--load',state,'--frames',4500,'--hash-at',','.join(map(str,range(1,4501))),")
source=source.replace("hashes(folder/'run.log')==hashes(reference/'run.log')",
    "continued_rows(folder/'run.log')==continued_rows(reference/'run.log')[1477:]")
source=source.replace('changed_audio_profile_drops_foreign_tail=True if',
    'remaining_guest_fields_checked=3023,changed_audio_profile_drops_foreign_tail=True if')
source=source.replace("len(entries)==1 and entries[0]['emitted']=='0'","len(entries)==4 and all(r['emitted']=='0' for r in entries)")
source=source.replace("r['value']=='112'","r['value']=='94'").replace('no_foreign_fm112','no_foreign_fm94')
source=source.replace('sources=[Path(__file__),bp,',"sources=[Path(__file__),original,ROOT/'tools/pride_ledge_history.py',bp,")
exec(compile(source,str(original),'exec'))
