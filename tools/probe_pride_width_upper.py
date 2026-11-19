"""Try ordinary takeoff pauses before the upper-left enemy/platform crossing."""
from pathlib import Path

original_verifier=Path(__file__).with_name('probe_pride_width_controls.py')
source=original_verifier.read_text()
source=source.replace("out=base/'width-controls'", "out=ROOT/'build/pride-rng-player3/width-upper-phases'")
source=source.replace("original=base/'controller-unpaused2/route.polled.tape'",
                      "original=ROOT/'build/pride-rng-player3/width-plan6/best.polled.tape'")
start=source.index('    cases={}')
end=source.index('    clean=',start)
source=source[:start]+'''    cases={}
    for wait in (0,8,16,24,32,40,48,64):
        cases[f'wait-{wait}']=initial+[0]*wait+[0x200]*12+[0x8200]*24+[0x200]*50
'''+source[end:]
source=source.replace('1430','1900')
source=source.replace('paths=[Path(__file__),bp,original,profile]',
    "paths=[Path(__file__),original_verifier,bp,original,profile,ROOT/'build/pride-rng-player3/width-plan6/report.json']")
exec(compile(source,str(original_verifier),'exec'))
