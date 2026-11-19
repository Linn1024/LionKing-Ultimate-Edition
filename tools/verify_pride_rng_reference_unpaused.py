"""Remove the original movie's later Start press from the ordinary boss route."""
import json
from pathlib import Path
import struct

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest

previous_verifier=Path(__file__).with_name('verify_pride_rng_reference_route.py')
namespace={'__file__':str(Path(__file__).resolve()),'__name__':'prepare_only'}
exec(compile(previous_verifier.read_text(),str(previous_verifier),'exec'),namespace)
controller_original=ROOT/'build/pride-ground-gap/native/derived.polled.tape'
assert digest(controller_original)=='216040df88f794e740f4a551a11ffdee8762754e9e04f93d419d7b706f7bf1c4'
values=list(struct.unpack('<'+'H'*(controller_original.stat().st_size//2),controller_original.read_bytes()))
assert [i for i,x in enumerate(values) if i>1000 and x&0x1000]==[3535]
before=values[3535];values[3535]&=~0x1000
folder=ROOT/'build/pride-rng-player2/controller-unpaused2';folder.mkdir()
tape=folder/'route.polled.tape';tape.write_bytes(struct.pack('<'+'H'*len(values),*values))
provenance=folder/'provenance.json'
provenance.write_text(json.dumps(dict(original_tape=controller_original.relative_to(ROOT).as_posix(),
    original_sha256=digest(controller_original),tape_sha256=digest(tape),
    edits=[dict(poll_index=3535,before=before,after=values[3535],button='Start')],
    original_source='https://tasvideos.org/10612S',author='ShgofcTAS',
    ordinary_controller_inputs_only=True,loaded_states=False,guest_edits=False),indent=2)+'\n')
source=namespace['source']
source=source.replace("base/'completion-reference'", "base/'completion-reference-unpaused2'")
old="tape=ROOT/'build/pride-ground-gap/native/derived.polled.tape';assert digest(tape)=='216040df88f794e740f4a551a11ffdee8762754e9e04f93d419d7b706f7bf1c4';previous['frames']=5500"
assert old in source
source=source.replace(old,"tape=ROOT/'build/pride-rng-player2/controller-unpaused2/route.polled.tape';previous['frames']=6000")
source=source.replace('sources=[Path(__file__),original_verifier,bp]',
    'sources=[Path(__file__),original_verifier,previous_verifier,controller_original,provenance,bp]')
original_verifier=namespace['original_verifier']
exec(compile(source,str(original_verifier),'exec'))
