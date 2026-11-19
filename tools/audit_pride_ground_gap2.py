"""Correct original MD byte-lane decoding and the literal SNES STA opcode."""
from pathlib import Path

original_verifier=Path(__file__).with_name('audit_pride_ground_gap.py')
source=original_verifier.read_text()
source=source.replace("data['md'][0x9411]&0x20", "w('md',0x9410)&0x20")
source=source.replace('a90000a03c009700a9fcffa03e009700', 'a90000a03c009100a9fcffa03e009100')
source=source.replace("p.name!='audit.json'", "p.name!='audit2.json'")
source=source.replace("out/'audit.json'", "out/'audit2.json'")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original_verifier,')
exec(compile(source,str(original_verifier),'exec'))
