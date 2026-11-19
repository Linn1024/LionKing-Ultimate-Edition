"""Test the original MD hyena walking query at the Graveyard skull, preserving the audio fix."""
from pathlib import Path
template=Path(__file__).with_name('build_graveyard635.py')
s=template.read_text().replace("base=ROOT/'build/graveyard621'", "base=ROOT/'build/graveyard659'").replace("out=ROOT/'build/graveyard635'", "out=ROOT/'build/graveyard665'")
s=s.replace("('audio',b['compiles']['audio'],out/'game/tlk_audio.c')", "('probe',b['compiles']['probe'],ROOT/'engine/runner/tlk_hyena_probe.c')")
s=s.replace("'engine/runner/tlk_audio.c',", "'engine/runner/tlk_hyena_probe.c',")
exec(compile(s,str(template),'exec'))
