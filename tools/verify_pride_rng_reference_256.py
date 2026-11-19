"""Check the same ordinary unpaused completion controls on the256-pixel display."""
from pathlib import Path

previous_verifier=Path(__file__).with_name('verify_pride_rng_reference_route.py')
namespace={'__file__':str(Path(__file__).resolve()),'__name__':'prepare_only'}
exec(compile(previous_verifier.read_text(),str(previous_verifier),'exec'),namespace)
source=namespace['source']
source=source.replace("base/'completion-reference'", "base/'completion-reference-unpaused256'")
source=source.replace('for width in (320,):','for width in (256,):')
old="tape=ROOT/'build/pride-ground-gap/native/derived.polled.tape';assert digest(tape)=='216040df88f794e740f4a551a11ffdee8762754e9e04f93d419d7b706f7bf1c4';previous['frames']=5500"
assert old in source
source=source.replace(old,"tape=ROOT/'build/pride-rng-player2/controller-unpaused2/route.polled.tape';previous['frames']=6000")
source=source.replace('sources=[Path(__file__),original_verifier,bp]',
    "sources=[Path(__file__),original_verifier,previous_verifier,ROOT/'build/pride-rng-player2/controller-unpaused2/provenance.json',bp]")
original_verifier=namespace['original_verifier']
exec(compile(source,str(original_verifier),'exec'))
