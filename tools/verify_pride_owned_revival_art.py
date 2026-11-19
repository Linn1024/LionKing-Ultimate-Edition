"""Verify both ROM-owned revival decoders against independently decoded originals."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from audit_scenes import ROOT,read_rom
from pride_sprite_catalog import bitmap,snes_frame,md_frame


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-owned-revival-art';out.mkdir(exist_ok=True)
    report=out/'report.json';report.write_text('{"result":"RUNNING"}\n')
    snes=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    md=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    ref_path=ROOT/'build/pride-revival-scene/report.json';ref=json.loads(ref_path.read_text());assert ref['result']=='PASS'
    frames=ref['original_art'];assert len(frames)==13
    golden=out/'original-bitmaps.bin';pixels=0
    with golden.open('wb') as f:
        f.write(b'TLKRART1'+struct.pack('<II',1,13))
        for frame in frames:
            native=int(frame['snes'],16);external=int(frame['md'],16)
            a=bitmap(snes,snes_frame(snes,native&0x3fffff),False,with_origin=True)
            b=bitmap(md,md_frame(md,external),True,with_origin=True)
            assert a==b and hashlib.sha256(a[4]).hexdigest()==frame['indexed_sha256']
            x,y,w,h,indexes=a;f.write(struct.pack('<IiiII',native,x,y,w,h));f.write(indexes);f.write(b[4]);pixels+=w*h
    commands=[['cmake','--build','engine/build-win','--target','tlk_revival_art_test','-j','4'],
              [ROOT/'engine/build-win/tlk_revival_art_test.exe',ROOT/'Lion King, The (USA).sfc',ROOT/'Lion King, The (World).md',golden]]
    for i,cmd in enumerate(commands):
        with (out/f'run-{i}.log').open('wb') as log:
            subprocess.run(list(map(str,cmd)),cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    assert '0 failures' in (out/'run-1.log').read_text()
    result={'result':'PASS','scope':__doc__,'native_frames':13,'md_frames':13,'indexed_pixels_per_source':pixels,
        'source_buffers_detached':True,'full_source_identity_guards':True,'live_wram_not_required':True,
        'native_mixed_16_and_8_pixel_pieces':True,'native_idle_direct_rom_pieces':True,
        'production_component_enabled':False,'full_first_level_fidelity_complete':False,
        'test_sha256':digest(ROOT/'engine/build-win/tlk_revival_art_test.exe'),
        'source_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (Path(__file__),ref_path,golden,
            ROOT/'engine/runner/tlk_revival_art.c',ROOT/'engine/runner/tlk_revival_art.h',ROOT/'engine/tests/revival_art_test.c',
            ROOT/'engine/runner/tlk_death_scene.c',ROOT/'engine/CMakeLists.txt')},
        'logs_sha256':{f'run-{i}.log':digest(out/f'run-{i}.log') for i in range(2)}}
    report.write_text(json.dumps(result,indent=2)+'\n')
    print('Owned revival art: 13 independently decoded pairs,',pixels,'pixels/source, source detachment/guards PASS',flush=True)


if __name__=='__main__':main()
