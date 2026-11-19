"""Prepare current full-MD menu input while retaining every original gameplay read."""
import argparse,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,default=ROOT/'build/full-genesis-tas-current/input.tape');a=ap.parse_args()
 original=(ROOT/'build/remaining1025-genesis-tas/genesis-gameplay.polled.tape').read_bytes()
 prior=(ROOT/'build/fidelity3357-neutral-menu-phase/input.tape').read_bytes()
 assert sha(original)=='6acbbc75c29f8a70b22c1f72dece7a403c88384d063bfe5b656405138caa9dd3'
 assert sha(prior)=='6d01c0521e43dedb316c3af910e51c44207d4730d2a3868166251e575d848b99' and prior==bytes(2)+original
 gameplay=original[918*2:];assert len(gameplay)//2==51990
 # The animated MD opening needs189 extra menu reads. One further ordinary
 # neutral read before Start preserves the original inherited video-clock
 # phase:5677..79 proves the1108 boot changes the later vulture/Timon pattern,
 # while1109 restores the original setup and avoids the extra Stampede hit.
 # Keep this entirely in the menu translation; every gameplay read is original.
 prefix=bytes(2)+prior[:501*2]+bytes(189*2)+prior[501*2:919*2];assert len(prefix)//2==1109
 result=prefix+gameplay;assert result==bytes(2)+prior[:501*2]+bytes(189*2)+prior[501*2:]
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(result)
 report=dict(result='PREPARED_CURRENT_FULL_MD_MENU_PREFIX',boot_prefix_polls=1109,original_gameplay_polls=51990,total_polls=len(result)//2,original_sha256=sha(original),original_gameplay_sha256=sha(gameplay),input_sha256=sha(result),scope='Original gameplay51990 reads unchanged, ordered and byte-exact. Add189 neutral reads before the existing first title Down for the animated MD opening, plus one ordinary neutral menu read before initial Start. Existing normal Options A/A and all game inputs retained; no cheat/debug/guest/RNG/clock forcing. Current5677 observes1108 boot incoming d5e087, three real RNG steps ahead of original1afc3a;5678 menu-only1109 restores original Toss incoming1afc3a. At Stampedeclock2710 hero158/182,HP2,lives9 equals original; actual paced Windows5679 viewed and own guest/picture endpoints exact. This fixes replay startup, not game code; later levels and final ending TAS remain unverified on this route.')
 a.output.with_suffix('.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
