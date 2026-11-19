"""Inventory checkpoint interaction poses; decoded pairs are not renderer coverage."""
import hashlib
import json
from pathlib import Path
import struct

from audit_scenes import ROOT
from pride_sprite_catalog import bitmap, snes_frame, md_frame


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT/'build/pride-checkpoint-player/interaction-audit'
    out.mkdir(exist_ok=True)
    inputs = []
    rows = []
    for frame in range(3400,3741,5):
        path = ROOT/f'build/pride-checkpoint-player/collection-ram/hl_wram_{frame}.bin'
        ram = path.read_bytes()
        inputs.append(path)
        offset = 0
        while (offset := ram.find(bytes.fromhex('9a88c5'),offset,0x10000)) >= 0:
            task = offset-4
            offset += 1
            if not 0 <= task <= 0xff80:
                continue
            draw = struct.unpack_from('<H',ram,task+12)[0]
            if not 0x8000 <= draw <= 0xffe8 or struct.unpack_from('<H',ram,draw+4)[0] != task+8:
                continue
            position = struct.unpack_from('<HH',ram,task+8)
            if position != (1200,112):
                continue
            rows.append(dict(frame=frame,task=task,draw=draw,
                pose=int.from_bytes(ram[draw+10:draw+13],'little'),
                interaction=struct.unpack_from('<H',ram,task+0x2c)[0],
                timer=struct.unpack_from('<H',ram,task+0x2e)[0],
                checkpoint=list(struct.unpack_from('<HH',ram,0x1ffa4))))
    assert any(r['frame']==3655 and r['pose']==0xc2fde1 for r in rows)
    assert any(r['frame']==3660 and r['pose']==0xc2fe18 for r in rows)
    assert any(r['frame']==3665 and r['pose']==0xc2fde1 for r in rows)
    snes_path,md_path = ROOT/'Lion King, The (USA).sfc',ROOT/'Lion King, The (World).md'
    snes,md = snes_path.read_bytes(),md_path.read_bytes()
    assert digest(snes_path)=='457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712'
    assert digest(md_path)=='e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5'
    pairs = []
    for native,external in ((0x2fde1,0x977c6),(0x2fe18,0x977fe)):
        a = bitmap(snes,snes_frame(snes,native),False,with_origin=True)
        b = bitmap(md,md_frame(md,external),True,with_origin=True)
        assert a == b and a[:4] == (-58,-72,32,30)
        filename = f'{native:06x}-indexed.bin'
        (out/filename).write_bytes(a[4])
        pairs.append(dict(snes_pose=native|0xc00000,md_pose=external,bounds=list(a[:4]),
            indexed_pixels=len(a[4]),bitmap_sha256=digest(out/filename)))
    source_inputs = [Path(__file__),snes_path,md_path,ROOT/'tools/pride_sprite_catalog.py',
                     ROOT/'build/pride-checkpoint-player/collection-probe.log',*inputs]
    report = dict(result='AUDITED',scope=__doc__,ordinary_copied_ram=rows,source_pairs=pairs,
        observation_stride_fields=5,original_md_usage_or_timing_verified=False,
        physical_oam_or_final_pixels_verified=False,production_static_head_only=True,
        interaction_poses_adapted=False,full_first_level_fidelity_complete=False,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in source_inputs})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Checkpoint interaction images C2FDE1/C2FE18 found; two original source pairs exact, renderer adaptation OPEN',flush=True)


if __name__=='__main__':
    main()
