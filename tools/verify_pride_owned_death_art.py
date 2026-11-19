"""Verify ROM-owned native/MD death pixels before the live graphics bank exists."""
import hashlib
import importlib.util
import json
import struct
import subprocess
from pathlib import Path
from audit_scenes import ROOT,read_rom
from pride_sprite_catalog import bitmap,snes_frame,md_frame


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-owned-death-art';out.mkdir(exist_ok=True)
    report_path=out/'report.json';report_path.write_text(json.dumps({'result':'RUNNING'})+'\n')
    source_hashes={str(p):digest(ROOT/p) for p in ('Lion King, The (USA).sfc','Lion King, The (World).md')}
    s=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    m=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    spec=importlib.util.spec_from_file_location('death_lz',ROOT/'engine/tools/re/decompress.py')
    lz=importlib.util.module_from_spec(spec);spec.loader.exec_module(lz)
    bank,compressed=lz.decompress(s,0xdfa78c)
    assert len(bank)==17792 and hashlib.sha256(bank).hexdigest()=='f42fc9fa3745e53e1953237e0a3b9fa78369c59511da30b2c74f02343c58c1bb'
    work=bytearray(s);work.extend(bytes(0x400000-len(work)));work[0x3f0000:0x3f0000+len(bank)]=bank
    catalog_path=ROOT/'build/pride-sprites/catalog.json';catalog=json.loads(catalog_path.read_text())
    records=catalog['cub_death_frames'];assert len(records)==20
    golden=out/'original-bitmaps.bin';pixel_count=0
    with golden.open('wb') as file:
        file.write(b'TLKDART1'+struct.pack('<II',1,20))
        for record in records:
            pose=int(record['snes'],16);md_pose=int(record['md'][0],16)
            native=bitmap(work,snes_frame(work,pose),False,with_origin=True)
            external=bitmap(m,md_frame(m,md_pose),True,with_origin=True)
            assert native==external
            x,y,width,height,indexes=native;assert (x,y)==tuple(record['origin']) and (width,height)==tuple(record['size'])
            file.write(struct.pack('<IiiII',pose,x,y,width,height));file.write(indexes);file.write(external[4]);pixel_count+=len(indexes)
    commands=[['cmake','--build','engine/build-win','--target','tlk_death_art_test','-j','4'],
              [ROOT/'engine/build-win/tlk_death_art_test.exe',ROOT/'Lion King, The (USA).sfc',ROOT/'Lion King, The (World).md',golden]]
    for i,command in enumerate(commands):
        with (out/f'run-{i}.log').open('wb') as log:
            subprocess.run(list(map(str,command)),cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    assert all(digest(ROOT/p)==sha for p,sha in source_hashes.items())
    result={'result':'PASS','scope':__doc__,'native_frames':20,'md_frames':20,'indexed_pixels_per_source':pixel_count,
            'live_bank_not_required_for_owned_art':True,'controller_age0_native_art':True,
            'source_buffers_detached':True,'rebind_clear_and_corruption_guards':True,
            'source_rom_files_unchanged':True,'compressed_bank_bytes':compressed,
            'test_sha256':digest(ROOT/'engine/build-win/tlk_death_art_test.exe'),
            'source_sha256':{'script':digest(Path(__file__)),'catalog':digest(catalog_path),'golden':digest(golden),
                             'sprites':digest(ROOT/'engine/runner/tlk_md_sprites.c'),
                             'header':digest(ROOT/'engine/runner/tlk_md_sprites.h'),'unit':digest(ROOT/'engine/tests/death_art_test.c')},
            'logs_sha256':{f'run-{i}.log':digest(out/f'run-{i}.log') for i in range(2)},
            'full_first_level_fidelity_complete':False}
    report_path.write_text(json.dumps(result,indent=2)+'\n')
    print('Private native/MD death art:20 frames,',pixel_count,'pixels/source, age0 before live bank and detached source ownership PASS',flush=True)


if __name__=='__main__':main()
