"""Record original confirmed-menu actors and VDP submissions without guest edits.

Run with .tools/python32/python.exe. Research artifacts remain under build/.
"""
import ctypes as C
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT,MdLab,png
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='build/pride-final-menu-yes-original')
    parser.add_argument('--confirm',type=int,nargs='+',default=[124,130]);args=parser.parse_args()
    out=ROOT/args.output;out.mkdir()
    source=ROOT/'build/pride-continue-transition-reference/report.json'
    reference=bound(source)
    origin=ROOT/'build/pride-final-input-reference/prefatal.state'
    raw=origin.read_bytes();blob=C.create_string_buffer(raw)
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t]
    game.core.retro_unserialize.restype=C.c_bool
    cases={};checks={}
    try:
        for confirm in args.confirm:
            folder=out/str(confirm);folder.mkdir()
            assert game.core.retro_unserialize(blob,len(raw))
            rows=[];same=True
            old_frames={r['age']:r for r in reference['cases'].get(str(confirm),{}).get('video_frames',[])}
            with (source.parent/str(confirm)/'video.bin').open('rb') if old_frames else (folder/'unused.bin').open('wb+') as old:
                with (folder/'work_ram.bin').open('wb') as ramfile, (folder/'vram.bin').open('wb') as vramfile, (folder/'video.bin').open('wb') as video:
                    for age in range(max(352,confirm+228)):
                        game.step(128 if age==0 else (256 if age==confirm else 0));game.samples.clear()
                        if age<118:continue
                        ram=bytes(game.work_ram);reg=bytes(game.reg);vram=bytes(game.vram)
                        sprites=[];index=0;seen=set();sat=(reg[5]&0x7e)<<9
                        while index not in seen and len(sprites)<80:
                            seen.add(index);at=(sat+index*8)&65535
                            words=[vram[at+n]|vram[at+n+1]<<8 for n in range(0,8,2)]
                            sprites.append(dict(index=index,words=words));index=words[1]&127
                            if not index:break
                        rows.append(dict(age=age,ram_offset=ramfile.tell(),vram_offset=vramfile.tell(),
                            sprites=sprites,registers=list(reg),cram=bytes(game.cram).hex(),
                            vsram=bytes(game.vsram).hex(),video_sha256=hashlib.sha256(game.image[0]).hexdigest(),
                            video_offset=video.tell(),video_bytes=len(game.image[0]),pitch=game.image[3],format=game.image[4]))
                        ramfile.write(ram);vramfile.write(vram)
                        video.write(game.image[0])
                        if age in old_frames:
                            frame=old_frames[age];old.seek(frame['offset'])
                            same &= old.read(frame['bytes'])==game.image[0]
                        if age in (124,130,160,200,240,260,280,300,315,320,330,340,350,351):
                            png(folder/f'{age}.png',*game.image)
            if old_frames:checks[str(confirm)+'_matches_prior_full_video']=same
            cases[str(confirm)]=rows
            print('Captured YES',confirm,'through',rows[-1]['age'],'prior video comparison',bool(old_frames),same,flush=True)
    finally:game.close()
    paths=[Path(__file__),source,origin,ROOT/'tools/md_lab.py',ROOT/'Lion King, The (World).md']
    report=dict(result='CAPTURED' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,
        guest_or_rom_edits=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    assert all(checks.values())


if __name__=='__main__':main()
