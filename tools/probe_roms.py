"""Local, read-only investigation of the two supplied ROMs."""
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.tools/pythonlibs'))


def tile4(data):
    return [[sum(((data[y*2+(p&1)+(16 if p>=2 else 0)] >> (7-x)) & 1) << p
                 for p in range(4)) for x in range(8)] for y in range(8)]


def main():
    snes = next(ROOT.glob('*.sfc')).read_bytes()
    md = (ROOT / 'Lion King, The (World).md').read_bytes()
    print('MD header:', md[0x100:0x200])
    print('SNES Simba palette:', struct.unpack_from('<16H', snes, 0x7b93))
    found = []
    for off in range(0x1aa04b, 0x1ae84b, 32):
        t = tile4(snes[off:off+32])
        chunky = bytes((row[x] << 4) | row[x+1] for row in t for x in range(0,8,2))
        if len(set(chunky)) < 5:
            continue
        hit = md.find(chunky)
        if hit >= 0:
            found.append((hex(off),hex(hit)))
    print('Exact tile matches (SNES -> MD):', found[:40], 'count',len(found))
    # Valid 16-colour CRAM runs, ranked by per-index proximity to cub Simba.
    src = struct.unpack_from('<16H', snes, 0x7b93)
    target = [((v&31)*7/31, ((v>>5)&31)*7/31, ((v>>10)&31)*7/31) for v in src]
    candidates = []
    for off in range(0,len(md)-32,2):
        vals=struct.unpack_from('>16H',md,off)
        if vals[0] != 0 or any(v&~0xeee for v in vals) or len(set(vals))<10:
            continue
        rgb=[((v>>1)&7,(v>>5)&7,(v>>9)&7) for v in vals]
        err=sum(sum((a-b)**2 for a,b in zip(c,t)) for c,t in zip(rgb[1:],target[1:]))
        candidates.append((round(err,2),hex(off),[hex(v) for v in vals]))
    print('Candidate palettes (unverified):', sorted(candidates)[:8])
    from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
    cs=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    pc=struct.unpack_from('>I',md,4)[0]
    print('Reset vector',hex(pc))
    for i in cs.disasm(md[pc:pc+0x350],pc):
        print(f'{i.address:06x}: {i.mnemonic:10} {i.op_str}')


if __name__=='__main__': main()
