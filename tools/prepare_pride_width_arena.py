"""Continue the verified upper route with ordinary rightward input and a wait."""
import json
from pathlib import Path
import struct

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-rng-player3';parent=base/'width-arena-approach2'
    rp=parent/'report.json';report=bound(rp);assert report['result']=='PASS'
    source=parent/'route.polled.tape';assert digest(source)==report['selected_tape_sha256']
    values=list(struct.unpack('<'+'H'*(source.stat().st_size//2),source.read_bytes()))
    values+=[0x100]*60+[0]*160
    out=base/'width-arena-input';out.mkdir();tape=out/'route.polled.tape'
    tape.write_bytes(struct.pack('<'+'H'*len(values),*values))
    result=dict(result='PREPARED',original_source='https://tasvideos.org/10612S',author='ShgofcTAS',
        selected_tape_sha256=digest(tape),appended_controls=[dict(buttons='Right',polls=60),dict(buttons='neutral',polls=160)],
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in (Path(__file__),rp,source)},
        ordinary_controller_inputs_only=True,guest_mutated=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
