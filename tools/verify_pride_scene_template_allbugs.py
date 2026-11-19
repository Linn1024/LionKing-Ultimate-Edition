"""Verify the native 60648-field route and observer neutrality on the repair."""
from pathlib import Path

original=Path(__file__).with_name('verify_pride_rng_allbugs.py')
source=original.read_text()
changes={
    "ROOT/'build/pride-rng-player2'":"ROOT/'build/pride-scene-template-work/player'",
    "out=base/'allbugs2'":"out=base/'allbugs-standalone'",
    'from summarize_pride_practice import bound':'from pride_scene_template_history import bound',
    'sources=[Path(__file__),bp,':'sources=[Path(__file__),original,bp,',
    "        if mode=='lle':cmd+=['--lle']":
        "        if frames==3000:cmd+=['--hash-at',','.join(map(str,range(1,3001)))]\n        if mode=='lle':cmd+=['--lle']",
    "    checks['pilot_full_frame_wram_neutral']=pilot_control==pilot_observed":
        """    checks['pilot_full_frame_wram_neutral']=pilot_control==pilot_observed
    rows=lambda name:re.findall(r'frame=(\\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',(out/name/'run.log').read_text())
    checks['pilot_every_frame_full_wram_neutral']=len(rows('pilot-control'))==3000 and rows('pilot-control')==rows('pilot-observed')""",
}
for before,after in changes.items():
    assert source.count(before)==1,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))
