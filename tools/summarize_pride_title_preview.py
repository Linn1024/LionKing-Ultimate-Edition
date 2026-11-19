"""Bind the promoted caption/HUD preview; full Pride fidelity remains open."""
from pathlib import Path

original=Path(__file__).with_name('summarize_pride_popup_preview.py')
source=original.read_text()
changes={
    "base=ROOT/'build/pride-popup-work'":"base=ROOT/'build/pride-title-work'",
    'from pride_popup_preview_history import bound':'from pride_title_preview_history import bound',
    "base/'native-gates/play-report.json'":"base/'native-gates3/play-report.json'",
    "ROOT/'tools/pride_popup_preview_history.py'":"ROOT/'tools/pride_title_preview_history.py'",
    'paths=[Path(__file__),component_path,':'paths=[Path(__file__),original,component_path,',
    'pickup_arrival_artwork_palette_position_verified=True,':
        'caption_artwork_palette_position_duration_verified=True,native_wide_hud_priority_repaired=True,owned_health_death_caption_context_verified=False,',
    "ROOT/'build/pride-popup-preview-latest.json'":"ROOT/'build/pride-title-preview-latest.json'",
    'Verified popup preview promoted':'Verified caption preview promoted',
}
for before,after in changes.items():
    assert source.count(before)==1,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))
