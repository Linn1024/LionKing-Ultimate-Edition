"""Complete the currently supported mixture on the fresh reload repair."""
from pathlib import Path

original=Path(__file__).with_name('verify_pride_owned_audio_mixed_completion.py')
source=original.read_text()
changes={
    '"base=ROOT/\'build/pride-bounce-owner-work/player\'"':'"base=ROOT/\'build/pride-scene-template-work/player\'"',
    'from pride_bounce_owner_history import bound':'from pride_scene_template_history import bound',
    'paths=[Path(__file__),original,ROOT/':
        'paths=[Path(__file__),original,Path(__file__).with_name(\'verify_pride_owned_audio_mixed_completion.py\'),ROOT/',
}
for before,after in changes.items():
    assert source.count(before)==1,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))
