"""Verify original MD checkpoint interaction SAT geometry and texture indices.

Read-only power-on replay. This verifies uploaded sprite data, not final OBJ/BG
occlusion or cross-version interaction behavior. Run with embedded32-bit Python.
"""
import ctypes as C
import hashlib
import json
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT,png
from pride_sprite_catalog import md_frame


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def match(rom,vram,sprites,pose,start):
    pieces=md_frame(rom,pose)
    if start+len(pieces)>len(sprites):return None
    first=sprites[start]
    dx,dy,w,h,_=pieces[0]
    flipx=bool(first['attr']&0x800)
    flipy=bool(first['attr']&0x1000)
    cx=first['x']+dx+w if flipx else first['x']-dx
    cy=first['y']+dy+h if flipy else first['y']-dy
    checked=0
    for n,(dx,dy,w,h,texture) in enumerate(pieces):
        sprite=sprites[start+n];attr=sprite['attr']
        if bool(attr&0x800)!=flipx or bool(attr&0x1000)!=flipy:return None
        expected=(cx-dx-w if flipx else cx+dx,cy-dy-h if flipy else cy+dy,w,h)
        if (sprite['x'],sprite['y'],sprite['w'],sprite['h'])!=expected:return None
        for y in range(h):
            for x in range(w):
                a=(((attr&0x7ff)+(x//8)*(h//8)+y//8)*32+(y&7)*4+(x&7)//2)&65535
                b=texture+((x//8)*(h//8)+y//8)*32+(y&7)*4+(x&7)//2
                shift=0 if x&1 else 4
                if (vram[a^1]>>shift)&15 != (rom[b]>>shift)&15:return None
                checked+=1
    return dict(pose=pose,first_slot=first['slot'],origin=[cx,cy],pieces=len(pieces),
                palette_banks=[s['attr']>>13&3 for s in sprites[start:start+len(pieces)]],
                texture_indices=checked)


def main():
    out=ROOT/'build/pride-checkpoint-player/original-md-display'
    out.mkdir(exist_ok=True)
    report_path=out/'report.json';report_path.write_text('{"result":"RUNNING"}\n')
    sources=[Path(__file__),ROOT/'tools/md_lab.py',ROOT/'tools/pride_sprite_catalog.py',
             ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',
             ROOT/'.tools/genesis-plus-gx/core/vdp_render.c',ROOT/'Lion King, The (World).md',
             ROOT/'build/md-next-levels-replay/frames.json',
             ROOT/'build/pride-checkpoint-player/original-md-interaction/report.json']
    identities={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sources}
    assert digest(sources[3])=='a6c45bbaf55010698fac6b8f0289428b54dc57dbdea12188472255358dea028a'
    assert digest(sources[5])=='e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5'
    rom=sources[5].read_bytes();inputs=json.loads(sources[6].read_text())
    cpu=json.loads(sources[7].read_text());assert cpu['result']=='AUDITED'
    game=MdLab();cache=(C.c_ubyte*1024).in_dll(game.core,'sat')
    sat_base=C.c_uint16.in_dll(game.core,'satb')
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    rows=[];controls=[]
    try:
        with (out/'sat.bin').open('wb') as data:
            data.write(b'MDOSAT01')
            for frame in range(1,3601):
                game.step(inputs[frame-1]['pad'])
                if frame%100==1:
                    control=ROOT/f'build/md-next-levels-replay/{frame:05d}-wram.bin'
                    if control.exists():
                        assert bytes(game.work_ram)==control.read_bytes(),frame
                        controls.append(control)
                if 3500<=frame<=3600:
                    vram=bytes(game.vram);sat=bytes(cache);base=sat_base.value
                    assert base==((game.reg[5]&(0x7e if game.reg[12]&1 else 0x7f))<<9)
                    sprites=[];index=0;visited=set()
                    for _ in range(80 if game.reg[12]&1 else 64):
                        assert index not in visited;visited.add(index)
                        y,link=struct.unpack_from('<HH',sat,index*8)
                        attr,x=struct.unpack_from('<HH',vram,base+index*8+4)
                        shape=link>>8&15
                        sprites.append(dict(slot=index,x=(x&511)-128,y=(y&511)-128,
                                            w=((shape>>2&3)+1)*8,h=((shape&3)+1)*8,attr=attr))
                        index=link&127
                        if not index:break
                    matches=[]
                    for pose in (0x973b6,0x977c6,0x977fe):
                        for start in range(len(sprites)):
                            result=match(rom,vram,sprites,pose,start)
                            if result:matches.append(result)
                    rows.append(dict(frame=frame,sprites=sprites,matches=matches,
                        cpu_checkpoint_poses=[r for r in cpu['observations'] if r['frame']==frame]))
                    data.write(struct.pack('<III',frame,frame-3500,base)+bytes(game.reg)+bytes(game.cram)+sat+vram)
                    if frame in (3544,3546,3550,3552,3554):png(out/f'{frame}.png',*game.image)
                game.samples.clear()
    finally:game.close()
    assert len(rows)==101
    matches=[m for r in rows for m in r['matches']]
    assert {m['pose'] for m in matches}=={0x973b6,0x977c6,0x977fe}
    assert all(set(m['palette_banks'])=={0} for m in matches)
    for name,sha in identities.items():assert digest(ROOT/name)==sha,name
    sources.extend(controls)
    (out/'fields.json').write_text(json.dumps(rows,indent=2)+'\n')
    artifacts=[p for p in out.iterdir() if p.name!='report.json']
    report=dict(result='PASS',scope=__doc__,ordinary_power_on=True,loaded_states=False,guest_edits=False,
        captured_fields=len(rows),matched_fields=sum(bool(r['matches']) for r in rows),
        texture_indices=sum(m['texture_indices'] for m in matches),
        pose_matched_fields={str(p):[r['frame'] for r in rows if any(m['pose']==p for m in r['matches'])]
                            for p in (0x973b6,0x977c6,0x977fe)},
        original_palette_bank0_verified=True,prefix_full_ram_controls=len(controls),
        final_window_or_cross_version_timing_verified=False,full_first_level_fidelity_complete=False,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sources},
        artifacts_sha256={p.name:digest(p) for p in artifacts})
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    print('Original MD interaction SAT geometry/VRAM indices PASS: '+str(report['pose_matched_fields']),flush=True)


if __name__=='__main__':main()
