"""Complete the ordinary supported mixture with both new independent cues on."""
from pathlib import Path

original=Path(__file__).with_name('verify_pride_width_completion.py')
source=original.read_text().replace("base=ROOT/'build/pride-rng-player4'","base=ROOT/'build/pride-ledge-work/player'")
source=source.replace('from summarize_pride_practice import bound','from pride_ledge_history import bound')
needle="    profile=ROOT/'build/pride-rng-player2/completion-reference-unpaused256/256/resources.ini'"
assert source.count(needle)==1
source=source.replace(needle,needle+"\n    original_profile=profile\n    profile=base/'ledge-completion.ini'\n    profile.write_text(original_profile.read_text()+'\\naudio.effects.world.pickup_arrival = md\\naudio.effects.simba.ledge_grab = md\\n')")
source=source.replace("TLK_RNG_ENTRY_TRACE=str(folder/'entry.csv'))",
    "TLK_RNG_ENTRY_TRACE=str(folder/'entry.csv'),TLK_LEDGE_GRAB_TRACE=str(folder/'ledge.csv'))")
needle="        print(mode,[k for k,v in checks.items() if not v],flush=True)"
assert source.count(needle)==1
source=source.replace(needle,"        observations[mode]['ledge_events']=list(csv.DictReader((folder/'ledge.csv').open())) if (folder/'ledge.csv').exists() else []\n"+needle)
for fragment in ('width-fight1/report.json','width-fight1/best.polled.tape','width-fight-cold-end/report.json'):
    source=source.replace("base/'"+fragment+"'","ROOT/'build/pride-rng-player4/"+fragment+"'")
source=source.replace('paths=[Path(__file__),bp,',
    "paths=[Path(__file__),original,ROOT/'tools/pride_ledge_history.py',ROOT/'build/pride-ledge-baseline/report.json',bp,")
exec(compile(source,str(original),'exec'))
