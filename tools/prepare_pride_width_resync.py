"""Shorten an ordinary held-left pause after both routes reach the same ledge."""
import json
from pathlib import Path
import struct

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-rng-player2'
    rp=base/'width-controls2/report.json';report=bound(rp)
    source=ROOT/report['cases']['wait-6']['tape'];assert digest(source)==report['cases']['wait-6']['tape_sha256']
    values=list(struct.unpack('<'+'H'*(source.stat().st_size//2),source.read_bytes()))
    assert values[1210:1216]==[0x200]*6
    del values[1210:1216]
    out=ROOT/'build/pride-rng-player3/width-resync';out.mkdir()
    tape=out/'route.polled.tape';tape.write_bytes(struct.pack('<'+'H'*len(values),*values))
    provenance=dict(original_source='https://tasvideos.org/10612S',author='ShgofcTAS',
        parent_tape=source.relative_to(ROOT).as_posix(),parent_sha256=digest(source),tape_sha256=digest(tape),
        edits=[dict(poll_index=1210,removed_polls=6,removed_buttons='Left')],
        ordinary_poweron_controller_inputs_only=True,guest_mutated=False,loaded_states=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in (Path(__file__),rp,source)})
    (out/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    print(tape,flush=True)


if __name__=='__main__':main()
