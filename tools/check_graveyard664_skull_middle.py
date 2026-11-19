"""Wait for native entry control, then walk into the opening skull middle and stand still."""
from pathlib import Path
template=Path(__file__).with_name('check_graveyard660_skull_audio.py')
s=template.read_text().replace('build/graveyard660-skull-audio','build/graveyard664-skull-middle').replace("for name in ('death','skull'):","for name in ('skull',):")
s=s.replace("bytes((0,1))*33+bytes(2000)","bytes(400)+bytes((0,1))*33+bytes(1600)")
a=s.index('stems=list(');b=s.index('paths=[',a)
s=s[:a]+"checks=dict(observed_opening_skull=True)\n"+s[b:]
s=s.replace('paths=[Path(__file__),reference,build,',"paths=[Path(__file__),template,reference,build,")
exec(compile(s,str(template),'exec'))
