"""Read-only checkpoint contact/animation timing from the original MD game.

Power-on controller replay plus a neutral-input branch after genuine contact.
Observe guest task state and physical SAT/VRAM independently; never edit guest.
Run with .tools/python32/python.exe.
"""
import ctypes as C
import json
from pathlib import Path
import struct
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_lab import MdLab, ROOT, png
from audit_pride_checkpoint_md_display import match
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def checkpoint(ram):
    for draw in range(0x8000, 0xffe8, 2):
        pose = (ram[draw+10] << 16) | struct.unpack_from('<H', ram, draw+12)[0]
        if pose not in (0x973b6, 0x977c6, 0x977fe):
            continue
        position = struct.unpack_from('<H', ram, draw+4)[0]
        if not 0x8008 <= position <= 0xff88:
            continue
        task = position-8
        if struct.unpack_from('<H', ram, task+12)[0] != draw:
            continue
        if struct.unpack_from('<HH', ram, position) != (656, 592):
            continue
        return dict(task=task, draw=draw, pose=pose,
                    collected=struct.unpack_from('<H', ram, task+0x2c)[0],
                    task_bytes=ram[task:task+0x50].hex())


def sprites(game, cache, base):
    vram = bytes(game.vram); sat = bytes(cache); rows=[]; index=0; visited=set()
    for _ in range(80 if game.reg[12]&1 else 64):
        assert index not in visited
        visited.add(index)
        y, link = struct.unpack_from('<HH', sat, index*8)
        attr, x = struct.unpack_from('<HH', vram, base+index*8+4)
        shape = link>>8&15
        rows.append(dict(slot=index, x=(x&511)-128, y=(y&511)-128,
                         w=((shape>>2&3)+1)*8, h=((shape&3)+1)*8, attr=attr))
        index=link&127
        if not index:
            break
    return vram, rows


def run(out, inputs, rom, neutral):
    out.mkdir(); game=MdLab(); rows=[]; controls=[]; contact=None; last=None
    cache=(C.c_ubyte*1024).in_dll(game.core, 'sat')
    sat_base=C.c_uint16.in_dll(game.core, 'satb')
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1): game.core.retro_set_controller_port_device(port,513)
    try:
        for frame in range(1, 4201):
            pad=0 if neutral and contact is not None else inputs[frame-1]['pad']
            game.step(pad); ram=bytes(game.work_ram)
            if frame%100==1 and (not neutral or contact is None):
                p=ROOT/f'build/md-next-levels-replay/{frame:05d}-wram.bin'
                if p.exists():
                    assert ram == p.read_bytes(), (frame, neutral)
                    controls.append(p)
            actor=checkpoint(ram) if frame>=3400 else None
            if actor:
                if actor['collected'] and contact is None:
                    contact=frame
                    (out/'contact-wram.bin').write_bytes(ram)
                    png(out/'contact.png', *game.image)
                vram, physical=sprites(game,cache,sat_base.value)
                displayed=[]
                for pose in (0x973b6,0x977c6,0x977fe):
                    for start in range(len(physical)):
                        found=match(rom,vram,physical,pose,start)
                        if found: displayed.append(found)
                row=dict(frame=frame,pad=pad,checkpoint=list(struct.unpack_from('<HH',ram,0xccd6)),
                         displayed=displayed,**actor)
                rows.append(row)
                signature=(actor['pose'], tuple(m['pose'] for m in displayed))
                if contact and signature != last:
                    png(out/f'{frame}.png',*game.image)
                last=signature
            game.samples.clear()
    finally: game.close()
    (out/'observations.json').write_text(json.dumps(rows,indent=2)+'\n')
    return rows,contact,controls


def runs(rows, key):
    groups=[]
    for row in rows:
        value=key(row)
        if groups and groups[-1]['value']==value and groups[-1]['last']+1==row['frame']:
            groups[-1]['last']=row['frame']; groups[-1]['fields']+=1
        else: groups.append(dict(first=row['frame'],last=row['frame'],fields=1,value=value))
    return groups


def main():
    out=ROOT/'build/md-checkpoint-timing51-reference';out.mkdir()
    prior=ROOT/'build/pride-checkpoint-player/original-md-display/report.json'
    assert bound(prior)['result']=='PASS'
    controls=ROOT/'build/md-next-levels-replay/frames.json'
    rompath=ROOT/'Lion King, The (World).md';rom=rompath.read_bytes()
    inputs=json.loads(controls.read_text());results={};sources=[]
    for mode in ('ordinary','neutral-after-contact'):
        rows,contact,checked=run(out/mode,inputs,rom,mode!='ordinary')
        sources.extend(checked)
        results[mode]=dict(contact=contact,cpu=runs(rows,lambda r:r['pose']),
                           display=runs(rows,lambda r:[m['pose'] for m in r['displayed']]),
                           control_snapshots=len(checked),observed_fields=len(rows))
        print(mode,contact,results[mode]['cpu'],flush=True)
    checks=dict(genuine_same_contact=results['ordinary']['contact']==results['neutral-after-contact']['contact']
                and results['ordinary']['contact'] is not None,
                ordinary_controls=results['ordinary']['control_snapshots']>=35,
                neutral_branch_all_three_poses=set(g['value'] for g in results['neutral-after-contact']['cpu'])
                =={0x973b6,0x977c6,0x977fe})
    paths=[Path(__file__),ROOT/'tools/md_lab.py',ROOT/'tools/audit_pride_checkpoint_md_display.py',
           ROOT/'tools/pride_sprite_catalog.py',prior,controls,rompath,
           ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',*sources]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=results,
                no_guest_or_rom_edits=True,cross_version_timing_verified=False,
                full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],checks,flush=True)


if __name__=='__main__': main()
