"""Use the actual fully initialized Graveyard WRAM, not the Pride graphics reconstruction."""
from pathlib import Path
template=Path(__file__).with_name('audit_graveyard518_vulture_pairs.py')
s=template.read_text().replace('build/graveyard518-vulture-pairs','build/graveyard520-vulture-pairs')
s=s.replace('s=pride_snes_graphics(s0)', "s=bytearray(s0);s.extend(bytes(0x400000-len(s)));s[0x3e0000:]=(ROOT/'build/graveyard519-wram/wram.bin').read_bytes()")
s=s.replace("paths=[Path(__file__),ROOT/'tools/pride_sprite_catalog.py'", "paths=[Path(__file__),template,ROOT/'build/graveyard519-wram/report.json',ROOT/'build/graveyard519-wram/wram.bin',ROOT/'tools/pride_sprite_catalog.py'")
s=s.replace('using original ROM plus existing Pride WRAM reconstruction. Any other RAM-backed native bank remains unqualified.', 'using original ROM plus hash-verified fully initialized Graveyard WRAM. Temporal mappings and actual draw ownership remain separate.')
exec(compile(s,str(template),'exec'))
