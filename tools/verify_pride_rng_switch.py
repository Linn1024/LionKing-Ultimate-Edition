"""Use the real tree to apply independent SNES/MD entry seeds with boot restarts."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_launch_switch.py')
source=original_verifier.read_text().replace("ROOT/'build/pride-launch2'","ROOT/'build/pride-rng-player'")
source=source.replace("base/'switch'","base/'rng-switch'")
source=source.replace('gameplay.levels.pride_lands.health_death','gameplay.levels.pride_lands.random_entry')
source=source.replace("wait(owned);choose(1,'pending-snes-owned')", "wait(lambda row:row['field']>=2500);choose(1,'pending-snes')")
start=source.index("    journal=read_rows(live/'practice-fields.csv')")
end=source.index("    checks['final_native_guest_picture']",start)
source=source[:start]+"""    audio=wav_data(live/'audio.wav');md_audio=wav_data(out/'md/audio.wav');native_audio=wav_data(out/'snes/audio.wav')
    checks['complete_md_pcm_segment']=audio[-len(native_audio)-len(md_audio):-len(native_audio)]==md_audio
    checks['complete_final_native_pcm']=audio[-len(native_audio):]==native_audio
"""+source[end:]
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original_verifier,')
exec(compile(source,str(original_verifier),'exec'))
