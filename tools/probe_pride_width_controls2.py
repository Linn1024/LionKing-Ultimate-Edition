"""Try ordinary takeoff timing and pauses while preserving the original jump height."""
from pathlib import Path

original_verifier=Path(__file__).with_name('probe_pride_width_controls.py')
source=original_verifier.read_text().replace("out=base/'width-controls'", "out=base/'width-controls2'")
start=source.index('    cases={}')
end=source.index('    clean=',start)
source=source[:start]+'''    cases={}
    for delay in (6,12,18):
        values=initial[:1073]+[0]*delay+initial[1073:]
        cases[f'wait-{delay}']=values
    for shift in (-12,-8,-4,4,8,12):
        values=initial.copy()
        for i in range(1045,1110):
            values[i]=(values[i]&~0x8000)|(0x8000 if 1073+shift<=i<1090+shift else 0)
        cases[f'takeoff-{shift}']=values
'''+source[end:]
source=source.replace('paths=[Path(__file__),bp,original,profile]',
                      'paths=[Path(__file__),original_verifier,bp,original,profile]')
exec(compile(source,str(original_verifier),'exec'))
