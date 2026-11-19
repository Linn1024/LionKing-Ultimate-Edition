"""Complete Pride Lands with all new caption options in the supported mixture."""
from pathlib import Path

original=Path(__file__).with_name('verify_pride_popup_completion.py')
source=original.read_text()
changes={
    "ROOT/'build/pride-popup-work'":"ROOT/'build/pride-title-work'",
    "base/'commands4.json'":"base/'final-build3.json'",
    "ROOT/'build/pride-scene-template-work/player/launch-completion.ini'":
        "ROOT/'build/pride-popup-work/completion/resources.ini'",
    "'\\ngraphics.sprites.effects.pickup_arrival = md\\n'":"'\\ngraphics.titles.pride_lands = md\\n'",
    "ROOT/'build/pride-scene-template-work/player/native-engine/tlk_pride_player.exe'":
        "ROOT/'build/pride-popup-work/player/native-engine/tlk_pride_player.exe'",
    'paths=[Path(__file__),bp,':'paths=[Path(__file__),original,bp,',
}
for before,after in changes.items():
    assert source.count(before)==1,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))
