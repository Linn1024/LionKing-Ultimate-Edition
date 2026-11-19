"""Use the earlier ordinary level-entry save so Simba can reach the skull middle before contact."""
from pathlib import Path
template=Path(__file__).with_name('check_graveyard660_skull_audio.py')
s=template.read_text().replace('build/graveyard660-skull-audio','build/graveyard661-skull-entry').replace("for name in ('death','skull'):","for name in ('skull',):")
s=s.replace("else '2350'", "else '13950'").replace("str(reference.parent/'entry.state')", "str(ROOT/'build/graveyard511-checkpoint/entry.state')")
a=s.index('stems=list(');b=s.index('paths=[',a)
s=s[:a]+"checks=dict(observed_opening_skull=True)\n"+s[b:]
s=s.replace('paths=[Path(__file__),reference,build,',"paths=[Path(__file__),template,ROOT/'build/graveyard511-checkpoint/report.json',reference,build,")
exec(compile(s,str(template),'exec'))
