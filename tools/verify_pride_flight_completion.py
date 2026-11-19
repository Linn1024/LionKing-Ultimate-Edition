"""Complete the ordinary supported mixture with the maintained flight renderer."""
from pathlib import Path
original=Path(__file__).with_name('verify_pride_width_completion.py')
source=original.read_text().replace("base=ROOT/'build/pride-rng-player4'","base=ROOT/'build/pride-flight-player'")
source=source.replace('from summarize_pride_practice import bound','from pride_flight_history import bound')
for fragment in ('width-fight1/report.json','width-fight1/best.polled.tape','width-fight-cold-end/report.json'):
    source=source.replace("base/'"+fragment+"'","ROOT/'build/pride-rng-player4/"+fragment+"'")
source=source.replace('paths=[Path(__file__),bp,',"paths=[Path(__file__),original,ROOT/'tools/pride_flight_history.py',ROOT/'build/pride-flight-baseline/report.json',bp,")
exec(compile(source,str(original),'exec'))
