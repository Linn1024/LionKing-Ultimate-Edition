"""Build an original-entry plus per-field lifetime observer, without guest edits."""
from pathlib import Path

original=Path(__file__).with_name('build_pride_player_allbugs.py')
source=original.read_text().replace("base = ROOT / 'build/pride-player'","base = ROOT / 'build/pride-arrival-work/player'")
source=source.replace("out = base / 'allbugs-observer'","out = base / 'contact-audio-lifetime'")
source=source.replace('from build_pride_rng_allbugs import OBSERVER',"""OBSERVER=(ROOT/'tools/native_cub_contact_audio_observer.c').read_text()
needle='return PrideObservedRunFrame(inputs);'
assert OBSERVER.count(needle)==1
OBSERVER=OBSERVER.replace(needle,'_Bool result=PrideObservedRunFrame(inputs); ContactAudioAfterFrame(); return result;')
OBSERVER=(ROOT/'tools/native_cub_contact_audio_lifetime.c').read_text()+'\\n'+OBSERVER
""")
source=source.replace('paths = [Path(__file__),',
    "paths = [Path(__file__), original, ROOT/'tools/native_cub_contact_audio_observer.c', ROOT/'tools/native_cub_contact_audio_lifetime.c',")
exec(compile(source,str(original),'exec'))
