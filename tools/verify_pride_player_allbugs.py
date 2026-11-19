"""Verify all-field observer neutrality and the complete standalone native All Bugs route."""
from pathlib import Path

original_verifier = Path(__file__).with_name('verify_pride_rng_allbugs.py')
source = original_verifier.read_text().replace("ROOT/'build/pride-rng-player2'", "ROOT/'build/pride-player'")
source = source.replace("out=base/'allbugs2'", "out=base/'allbugs-standalone'")
source = source.replace('sources=[Path(__file__),bp,', 'sources=[Path(__file__),original_verifier,bp,')
anchor = "        if mode=='lle':cmd+=['--lle']"
assert source.count(anchor) == 1
source = source.replace(anchor, "        if frames==3000:cmd+=['--hash-at',','.join(map(str,range(1,3001)))]\n" + anchor)
anchor = "    checks['pilot_full_frame_wram_neutral']=pilot_control==pilot_observed"
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '''
    rows=lambda name:re.findall(r'frame=(\\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',(out/name/'run.log').read_text())
    checks['pilot_every_frame_full_wram_neutral']=len(rows('pilot-control'))==3000 and rows('pilot-control')==rows('pilot-observed')
''')
exec(compile(source, str(original_verifier), 'exec'))
