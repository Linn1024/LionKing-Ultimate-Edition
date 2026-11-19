"""Walk off the low bone-platform route without jumping, to check fall-death audio."""
from pathlib import Path
template=Path(__file__).with_name('check_graveyard640_fall.py')
s=template.read_text().replace("exec(compile(s,str(template),'exec'))", "s=s.replace('build/graveyard640-fall','build/graveyard642-fall').replace(\"(out/'idle.polled.tape').write_bytes(bytes(4000))\",\"(out/'idle.polled.tape').write_bytes(bytes((0,1))*1000+bytes(2000))\")\nexec(compile(s,str(template),'exec'))")
exec(compile(s,str(template),'exec'))
