"""Verify owned caption images against independent ROM decoders and live actors."""
import ctypes as C
import json
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_sprite_catalog import bitmap


def main():
    out=ROOT/'build/pride-title-work/assets2';out.mkdir()
    wrapper=out/'role.c';wrapper.write_text('#include "tlk_title_role.h"\n'
        'int title_role(const uint8_t *r,unsigned n,const uint8_t *s,unsigned z,unsigned d,unsigned p,int f)'
        '{return TlkPrideTitleDrawRole(r,n,s,z,d,p,f!=0);}\n')
    sources=[ROOT/'engine/runner'/n for n in ('tlk_title_art.c','tlk_revival_art.c','tlk_death_scene.c')]
    sha=ROOT/'engine/snesrecomp/runner/src/sha256.c'
    library=out/'art.dll';gcc='C:/mingw32/bin/gcc.exe'
    command=[gcc,'-shared','-static-libgcc','-O2','-Wl,--export-all-symbols',
             '-I'+str(ROOT/'engine/runner'),'-I'+str(sha.parent),*map(str,sources),str(sha),str(wrapper),'-o',str(library)]
    subprocess.run(command,check=True)
    lib=C.CDLL(str(library));lib.TlkRevivalArtCreatePrideTitle.restype=C.c_void_p
    lib.TlkRevivalArtCreatePrideTitle.argtypes=[C.c_void_p,C.c_uint,C.c_void_p,C.c_uint]
    lib.TlkRevivalArtPixel.argtypes=[C.c_void_p,C.c_uint,C.c_int,C.c_int,C.c_uint]
    lib.TlkRevivalArtFree.argtypes=[C.c_void_p]
    lib.title_role.argtypes=[C.c_void_p,C.c_uint,C.c_void_p,C.c_uint,C.c_uint,C.c_uint,C.c_int]
    lib.TlkTitleArtCreate.restype=C.c_void_p;lib.TlkTitleArtCreate.argtypes=lib.TlkRevivalArtCreatePrideTitle.argtypes
    lib.TlkTitleArtSample.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_uint,C.c_uint,C.c_void_p,C.c_void_p]
    lib.TlkTitleArtFree.argtypes=[C.c_void_p]
    snes_path=ROOT/'Lion King, The (USA).sfc';md_path=ROOT/'Lion King, The (World).md'
    snes=snes_path.read_bytes();md=md_path.read_bytes();sbuf=C.create_string_buffer(snes);mbuf=C.create_string_buffer(md)
    art=lib.TlkRevivalArtCreatePrideTitle(sbuf,len(snes),mbuf,len(md));assert art,'Caption decode rejected'
    palette_art=lib.TlkTitleArtCreate(sbuf,len(snes),mbuf,len(md));assert palette_art
    ram_path=ROOT/'build/native-pickup-flight/hl_wram_1000.bin';ram=bytearray(ram_path.read_bytes());p=0x17dd
    native_pieces=[]
    for i in range(13):
        x,y,source=struct.unpack_from('<3H',ram,p+27+i*6)
        native_pieces.append((x-112,y,16,16,0x280000|source))
    md_pieces=[]
    for i in range(11):
        w,h,x,y,flags,transfer,source=struct.unpack_from('>6HI',md,0x1d5dac+24+i*16)
        md_pieces.append((x-160,y-72,w,h,source))
    expected=[bitmap(snes,native_pieces,False,with_origin=True),bitmap(md,md_pieces,True,with_origin=True)]
    native_palette=struct.unpack_from('<16H',snes,0x7b93)
    md_palette=[]
    for c in struct.unpack_from('>16H',md,0x1d78aa):
        md_palette.append(sum(((c>>s&7)*4+((c>>s&7)>>2))<<(n*5) for n,s in enumerate((1,5,9))))
    cgram=(C.c_uint16*256)()
    for i,c in enumerate(native_palette):cgram[128+i]=c
    checks={};pixel_counts=[]
    for source,(x,y,w,h,data) in enumerate(expected):
        actual=bytes(lib.TlkRevivalArtPixel(art,0x7e17dd,x+i%w,y+i//w,source) for i in range(w*h))
        checks[f'{source}/independent_indexed_image']=actual==data;pixel_counts.append(sum(bool(c) for c in data))
        for palette in (0,1):
            correct=True
            for i,c in enumerate(data):
                color=C.c_uint16(0xdead)
                status=lib.TlkTitleArtSample(palette_art,x+i%w,y+i//w,source,palette,cgram,C.byref(color))
                if status!=bool(c) or (c and color.value!=(md_palette if palette else native_palette)[c]):correct=False;break
            checks[f'{source}/{palette}/independent_palette']=correct
    cgram[129]^=1;color=C.c_uint16(0xdead)
    checks['foreign_palette_fallback']=lib.TlkTitleArtSample(palette_art,0,0,1,1,cgram,C.byref(color))==-1 and color.value==0xdead
    lib.TlkRevivalArtFree(art);lib.TlkTitleArtFree(palette_art)
    scene=json.loads((ROOT/'build/pride-intro-windows/256-1000/scene.json').read_text())
    piece=next(p for p in scene['pieces'] if p['pose']==0x7e17dd);draw=piece['object'];actor=piece['position_pointer']-8
    def role(data=ram,fixed=0):
        buf=(C.c_ubyte*len(data)).from_buffer_copy(data)
        return bool(lib.title_role(buf,len(data),sbuf,len(snes),draw,0x7e17dd,fixed))
    checks['actual_caption_owned']=role()
    for label,offset in [('other_scene',0xdf),('other_level',0x1ff9e),('adult',0x2000),
        ('other_task',actor+4),('other_action',actor+0x30),('broken_owner',actor+12),
        ('broken_position',draw+4),('other_pose',draw+10),('foreign_bank',draw+8),
        ('other_string',0x17dd+31),('other_width',0x17dd+6),('other_font',0x17dd+26)]:
        changed=bytearray(ram);changed[offset]^=2;checks[label]=not role(changed)
    checks['wrong_fixed_mode']=not role(fixed=1)
    for field in range(944,981,4):
        data=(ROOT/f'build/native-pickup-flight/hl_wram_{field}.bin').read_bytes()
        checks[f'original_letter_entrance/{field}']=role(data)
    # The shared decoder refactor must preserve existing revival images.
    executable=out/'revival-test.exe';golden=ROOT/'build/pride-owned-revival-art/original-bitmaps.bin'
    test_command=[gcc,'-O2','-I'+str(ROOT/'engine/runner'),'-I'+str(sha.parent),
        str(ROOT/'engine/tests/revival_art_test.c'),str(sources[1]),str(sources[2]),str(sha),'-o',str(executable)]
    subprocess.run(test_command,check=True)
    with (out/'revival.log').open('wb') as log:
        subprocess.run([str(executable),str(snes_path),str(md_path),str(golden)],stdout=log,stderr=subprocess.STDOUT,check=True)
    checks['existing_13_revival_images_unchanged']='0 failures' in (out/'revival.log').read_text()
    paths=[Path(__file__),*sources,ROOT/'engine/runner/tlk_title_art.h',ROOT/'engine/runner/tlk_title_role.h',ram_path,snes_path,md_path,golden]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,opaque_pixels=pixel_counts,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'caption asset/ownership checks; opaque pixels',pixel_counts,flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
