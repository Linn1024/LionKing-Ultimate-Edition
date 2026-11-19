"""Build a read-only original contact-helper observer from the current graph."""
from pathlib import Path

original=Path(__file__).with_name('build_pride_player_allbugs.py')
source=original.read_text().replace("base = ROOT / 'build/pride-player'","base = ROOT / 'build/pride-arrival-work/player'")
source=source.replace("out = base / 'allbugs-observer'","out = base / 'contact-audio-observer2'")
source=source.replace('from build_pride_rng_allbugs import OBSERVER',
    "OBSERVER=(ROOT/'tools/native_cub_contact_audio_observer.c').read_text()")
source=source.replace('paths = [Path(__file__),',
    "paths = [Path(__file__), original, ROOT/'tools/native_cub_contact_audio_observer.c',")
exec(compile(source,str(original),'exec'))
