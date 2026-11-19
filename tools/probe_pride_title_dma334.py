"""Repeat333 from ordinary power-on inputs instead of an obsolete checkpoint."""
from pathlib import Path
template334=Path(__file__).with_name('probe_pride_title_dma333.py')
source=template334.read_text().replace('pride-title-dma333-probe','pride-title-dma334-probe')
anchor="    cmd+=['--lle'];cmd[cmd.index('--frames')+1]='4850'"
source=source.replace(anchor,"""    cmd+=['--lle'];cmd[cmd.index('--frames')+1]='4350'
    i=cmd.index('--load');del cmd[i:i+2]
    prefix=(ROOT/'build/pride-game-over-music/normal.tape').read_bytes()[:3893*2]
    tail=(ROOT/'build/pride-final-title3/verification/no1000/input.tape').read_bytes()[3893*2:]
    tape=out/'poweron-no.tape';tape.write_bytes(prefix+tail)
    cmd[cmd.index('--input')+1]=str(tape)
""")
source=source.replace("Path(__file__),bp,reference,out/'host.i'","Path(__file__),template334,bp,reference,out/'host.i'")
source=source.replace('genuine prefatal backend checkpoint','ordinary power-on input route; no old-save compatibility work')
exec(compile(source,str(template334),'exec'))
