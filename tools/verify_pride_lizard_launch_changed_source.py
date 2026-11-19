"""Changing launch audio on a mid-chime cold load must discard the old MD tail."""
from pathlib import Path

original=Path(__file__).with_name('verify_pride_arrival_changed_source.py')
source=original.read_text().replace("ROOT/'build/pride-arrival-work/player'","ROOT/'build/pride-lizard-launch-work/player'")
source=source.replace('from summarize_pride_practice import bound','from pride_lizard_launch_history import bound')
source=source.replace('arrival-saves','launch-saves').replace('arrival-audio','launch-audio').replace('arrival-changed-source','launch-changed-source')
source=source.replace('TLK_PICKUP_ARRIVAL_TRACE','TLK_LIZARD_LAUNCH_TRACE').replace('arrival.csv','launch.csv')
source=source.replace('1676','2221').replace("'--frames',2000","'--frames',4500")
source=source.replace('import os','import os\nimport re')
source=source.replace('from verify_windows import hashes,pixels',"""from verify_windows import hashes,pixels
def continued_rows(path):
    return re.findall(r'frame=(\\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',path.read_text())
""")
source=source.replace("'--load',state,'--frames',4500,","'--load',state,'--frames',4500,'--hash-at',','.join(map(str,range(1,4501))),")
source=source.replace("hashes(folder/'run.log')==hashes(reference/'run.log')",
    "continued_rows(folder/'run.log')==continued_rows(reference/'run.log')[2221:]")
source=source.replace('changed_audio_profile_drops_foreign_tail=True if',
    'remaining_guest_fields_checked=2279,changed_audio_profile_drops_foreign_tail=True if')
source=source.replace("len(entries)==1 and entries[0]['emitted']=='0'","len(entries)==1 and all(r['emitted']=='0' for r in entries)")
source=source.replace("r['value']=='112'","r['value']=='123'").replace('no_foreign_fm112','no_foreign_fm123')
source=source.replace('launch-audio/report.json','launch-audio-baselines/report.json')
source=source.replace('sources=[Path(__file__),bp,',"sources=[Path(__file__),original,ROOT/'tools/pride_lizard_launch_history.py',bp,")
exec(compile(source,str(original),'exec'))
