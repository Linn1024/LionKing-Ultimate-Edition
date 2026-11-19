"""Continue the retained ordinary controller recording through the boss encounter."""
from pathlib import Path

previous_verifier=Path(__file__).with_name('verify_pride_rng_reference_route.py')
namespace={'__file__':str(Path(__file__).resolve()),'__name__':'prepare_only'}
exec(compile(previous_verifier.read_text(),str(previous_verifier),'exec'),namespace)
source=namespace['source']
source=source.replace("base/'completion-reference'", "base/'completion-reference-long3'")
source=source.replace("previous['frames']=5500", "previous['frames']=8000")
# Windows' command line cannot hold8000 comma-separated hash fields. The prior
# same-input5500-field capture covers the prefix; this run compares3001..8000.
for old,new in (
    ("range(1,previous['frames']+1)","range(3001,previous['frames']+1)"),
    ("len(rows(a))==previous['frames']","len(rows(a))==previous['frames']-3000"),
    ('every_aot_lle_field','suffix_aot_lle_fields'),
    ('sources=[Path(__file__),original_verifier,bp]',
     'sources=[Path(__file__),original_verifier,previous_verifier,bp]')):
    assert old in source,old
    source=source.replace(old,new)
original_verifier=namespace['original_verifier']
exec(compile(source,str(original_verifier),'exec'))
