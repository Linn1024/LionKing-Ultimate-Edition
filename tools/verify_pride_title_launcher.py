"""Check the actual promoted caption launcher and preserved installed data."""
from pathlib import Path

original=Path(__file__).with_name('verify_pride_popup_launcher.py')
source=original.read_text()
changes={
    "base=ROOT/'build/pride-popup-work'":"base=ROOT/'build/pride-title-work'",
    'from pride_popup_preview_history import bound':'from pride_title_preview_history import bound',
    "ROOT/'build/pride-scene-template-work/player/native-engine/tlk_pride_player.exe'":
        "ROOT/'build/pride-popup-work/player/native-engine/tlk_pride_player.exe'",
    "r'build\\pride-popup-work\\player\\native-engine\\tlk_pride_player.exe'":
        "r'build\\pride-title-work\\player\\native-engine\\tlk_pride_player.exe'",
    'paths=[Path(__file__),bp,':'paths=[Path(__file__),original,bp,',
}
for before,after in changes.items():
    assert source.count(before)==1,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))
