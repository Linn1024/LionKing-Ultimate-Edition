"""Verify installer-produced menu images using a reader linked without decoders."""
import ctypes as C
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-final-art-installed';out=base/'verification4';out.mkdir()
    source=ROOT/'build/pride-final-menu-ram-audit/report.json';old=bound(source)
    original=ROOT/'build/pride-final-menu-art-original/report.json';bound(original)
    prep=C.CDLL(str(base/'prepare.dll'));reader=C.CDLL(str(base/'reader.dll'))
    prep.TlkFinalArtPrepare.argtypes=[C.c_void_p,C.c_size_t,C.POINTER(C.c_uint32),C.c_uint,C.POINTER(C.c_void_p),C.POINTER(C.c_size_t)]
    reader.TlkFinalArtLoad.argtypes=[C.c_void_p,C.c_size_t];reader.TlkFinalArtLoad.restype=C.c_void_p
    reader.TlkFinalArtFree.argtypes=[C.c_void_p]
    reader.TlkFinalArtBounds.argtypes=[C.c_void_p,C.c_uint32,*([C.POINTER(C.c_int)]*4)]
    reader.TlkFinalArtPixel.argtypes=[C.c_void_p,C.c_uint32,C.c_int,C.c_int]
    reader.TlkFinalArtColor.argtypes=[C.c_void_p,C.c_uint,C.c_uint,C.POINTER(C.c_uint16)]
    frames=sorted(int(f,16) for f in old['matched_frame_metadata']);ids=(C.c_uint32*len(frames))(*frames)
    rom=(ROOT/'Lion King, The (World).md').read_bytes();buffer=C.create_string_buffer(rom)
    ptr=C.c_void_p();size=C.c_size_t();checks={}
    assert prep.TlkFinalArtPrepare(buffer,len(rom),ids,len(frames),C.byref(ptr),C.byref(size))
    record=C.string_at(ptr,size.value);free=C.CDLL('msvcrt.dll').free;free.argtypes=[C.c_void_p];free(ptr)
    (out/'menu-assets.bin').write_bytes(record)
    installed=C.create_string_buffer(record);art=reader.TlkFinalArtLoad(installed,len(record));assert art
    # Loading must own its data. Neither ROM nor package memory remains needed.
    C.memset(buffer,0,len(rom));C.memset(installed,0,len(record))
    memory=(original.parent/'continue/120/work_ram.bin').read_bytes();memory=bytes(memory[i^1] for i in range(len(memory)))
    count=0
    try:
        for address in frames:
            pieces=old['matched_frame_metadata'][hex(address)]
            left=min(p['x'] for p in pieces);top=min(p['y'] for p in pieces)
            right=max(p['x']+p['width'] for p in pieces);bottom=max(p['y']+p['height'] for p in pieces)
            expected=[0]*((right-left)*(bottom-top))
            for p in reversed(pieces):
                pixel_source=int(p['source'],16);w=p['width'];h=p['height'];data=memory if pixel_source>=0xff0000 else rom
                offset=pixel_source&65535 if pixel_source>=0xff0000 else pixel_source
                for y in range(h):
                    for x in range(w):
                        at=offset+((x//8)*(h//8)+y//8)*32+(y&7)*4+(x&7)//2
                        index=data[at]>>(0 if x&1 else 4)&15
                        if index:expected[(p['y']-top+y)*(right-left)+p['x']-left+x]=index
            values=[C.c_int() for _ in range(4)]
            checks[hex(address)+'_bounds']=bool(reader.TlkFinalArtBounds(art,address,*map(C.byref,values))) and [v.value for v in values]==[left,top,right-left,bottom-top]
            actual=[reader.TlkFinalArtPixel(art,address,x,y) for y in range(top,bottom) for x in range(left,right)]
            checks[hex(address)+'_original_pixels']=actual==expected;count+=len(actual)
        raw=struct.unpack('<64H',(original.parent/'continue/120/cram.bin').read_bytes())
        palette=[]
        for bank in range(4):
            for i in range(16):
                value=C.c_uint16();assert reader.TlkFinalArtColor(art,bank,i,C.byref(value));palette.append(value.value)
        mapped=[]
        for c in raw:
            mapped.append(sum((((c>>s&7)*4+((c>>s&7)>>2)))<<(s//3*5) for s in (0,3,6)))
        checks['original_palette']=palette==mapped
        checks['missing_frame_requests_unavailable']=reader.TlkFinalArtPixel(art,0,0,0)==-1
    finally:reader.TlkFinalArtFree(art)
    variants={}
    for name,offset,value in [('version',8,2),('count',20,257),('source',24,0),('reserved',88,1),('width',252,513)]:
        data=bytearray(record);struct.pack_into('<I',data,offset,value)
        if name=='width':data[56:88]=hashlib.sha256(data[112:]).digest()
        variants[name]=bytes(data)
    data=bytearray(record);data[-1]^=1;variants['checksum']=bytes(data);variants['truncated']=record[:-1]
    for name,data in variants.items():
        b=C.create_string_buffer(data);candidate=reader.TlkFinalArtLoad(b,len(data))
        checks[name+'_rejects']=not candidate
        if candidate:reader.TlkFinalArtFree(candidate)
    symbols=subprocess.check_output(['C:/mingw32/bin/nm.exe',str(base/'reader.dll')],text=True)
    checks['reader_has_no_rom_decoder_or_preparer']='TlkMdDecompress' not in symbols and 'TlkFinalArtPrepare' not in symbols
    spec=importlib.util.spec_from_file_location('lz',ROOT/'engine/tools/re/decompress.py');lz=importlib.util.module_from_spec(spec);spec.loader.exec_module(lz)
    decoded,used=lz.decompress(rom,0x299a6e)
    checks['bank_size']=len(decoded)==27872 and used==14636
    for case in ('continue','game-over'):
        for age in (90,96,97,100,118,120,124,125,140,141,160,180,200,220):
            raw=(original.parent/case/str(age)/'work_ram.bin').read_bytes();raw=bytes(raw[i^1] for i in range(len(raw)))
            matches=decoded==raw[0x190:0x190+len(decoded)]
            checks[case+str(age)+('_original_bank' if age>=97 else '_before_bank_complete')]=matches if age>=97 else not matches
    paths=[Path(__file__),source,original,*[ROOT/'engine/runner'/n for n in
        ('tlk_final_art.c','tlk_final_art.h','tlk_final_art_internal.h','tlk_final_art_prepare.c','tlk_final_art_prepare.h','tlk_md_assets.c')]]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,frame_pixels_compared=count,
        installer_record_bytes=len(record),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
        binary_sha256={name:digest(base/name) for name in ('reader.dll','prepare.dll')})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
