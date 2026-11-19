"""Retain the tested audio and rebuild the resource guard; final-player compiled resource bytes must match635."""
from pathlib import Path
template=Path(__file__).with_name('build_graveyard635.py')
s=template.read_text().replace("base=ROOT/'build/graveyard621'", "base=ROOT/'build/graveyard635'").replace("out=ROOT/'build/graveyard635'", "out=ROOT/'build/graveyard644'")
s=s.replace(",('audio',b['compiles']['audio'],out/'game/tlk_audio.c')",'')
exec(compile(s,str(template),'exec'))
