"""Reject an otherwise supported MD choice when the MD ROM is unavailable."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_soft_tree.py')
source=original_verifier.read_text()
source=source.replace("out=base/'windows'/args.case","out=base/'missing-md'/args.case")
source=source.replace("ROOT/'Lion King, The (World).md','--resource-profile'", "out/'missing.md','--resource-profile'")
begin=source.index('                baseline=profile.read_bytes()')
end=source.index('                proc.wait(timeout=180);',begin)
source=source[:begin]+'''                baseline=profile.read_bytes();setchoice('graphics.sprites.simba.cub.palette',2)
                key(0x71);row=snap('missing-rom-rejected')
                checks['missing_rom_rejected']=row['modal']==1 and row['dirty']==1 and choice(row,'graphics.sprites.simba.cub.palette')[2]==0
                checks['profile_not_published']=profile.read_bytes()==baseline
                checks['guest_still_paused']=row['field']==1500
                key(0x1b);key(0x72);checks['draft_reverted']=latest(trace)['dirty']==0
                key(0x7b)
''' + source[end:]
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original_verifier,')
exec(compile(source,str(original_verifier),'exec'))
