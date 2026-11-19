"""Accepted menu ownership survives the original global effects Off action."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_menu_output83_owner.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-menu-output83-owner-component'","ROOT/'build/pride-menu-enable86-owner-component'")
anchor='word(0x1ff96,0);CHECK(!TlkNativeAudioOwnerMute(7,62,0));word(0x1ff96,1);'
assert source.count(anchor)==1
source=source.replace(anchor,'word(0x1ff96,0);CHECK(TlkNativeAudioOwnerMute(7,62,0));word(0x1ff96,1);')
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))
