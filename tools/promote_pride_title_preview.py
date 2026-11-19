"""Promote the verified caption/HUD candidate, retaining the previous preview."""
from pathlib import Path

template=Path(__file__).with_name('promote_pride_popup_preview.py')
source=template.read_text()
changes={
    "base=ROOT/'build/pride-popup-work'":"base=ROOT/'build/pride-title-work'",
    'from pride_popup_history import bound':'from pride_title_history import bound',
    "component['verified_component_checks']==208":"component['verified_component_checks']==169",
    "base/'native-gates/play-report.json'":"base/'native-gates3/play-report.json'",
    "ROOT/'build/pride-scene-template-preview-latest.json'":"ROOT/'build/pride-popup-preview-latest.json'",
    "ROOT/'build/pride-scene-template-work/player/native-engine/tlk_pride_player.exe'":
        "ROOT/'build/pride-popup-work/player/native-engine/tlk_pride_player.exe'",
    "before=rb'build\\pride-scene-template-work\\player\\native-engine\\tlk_pride_player.exe'":
        "before=rb'build\\pride-popup-work\\player\\native-engine\\tlk_pride_player.exe'",
    "after=rb'build\\pride-popup-work\\player\\native-engine\\tlk_pride_player.exe'":
        "after=rb'build\\pride-title-work\\player\\native-engine\\tlk_pride_player.exe'",
    "ROOT/'tools/pride_popup_preview_history.py'":"ROOT/'tools/pride_title_preview_history.py'",
    "ROOT/'tools/pride_popup_history.py'":"ROOT/'tools/pride_title_history.py'",
    'paths=[Path(__file__),component_path,':'paths=[Path(__file__),template,component_path,',
    'archive.mkdir()':"archive.mkdir(exist_ok=True);assert not (archive/'report.json').exists()",
    "needle=\"'pride-scene-template-work/player'):\"":"needle=\"'pride-popup-work/player'):\"",
    "source.replace(needle,\"'pride-scene-template-work/player','pride-popup-work/player'):\")":
        "source.replace(needle,\"'pride-popup-work/player','pride-title-work/player'):\")",
    'Popup preview selected':'Caption preview selected',
}
for before,after in changes.items():
    assert source.count(before)==1,before
    source=source.replace(before,after)
exec(compile(source,str(template),'exec'))
