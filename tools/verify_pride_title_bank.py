"""Verify prepared bank5 packets against live original audio-load observations."""
import ctypes as C
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

class Packet(C.Structure):
    _fields_=[(n,C.c_uint32) for n in ('source','destination','size','command','id','directory')]

def main():
    base=ROOT/'build/pride-title-bank-installed';out=base/'verification';out.mkdir();checks={};observed={}
    source=ROOT/'build/pride-title-audio-observer/report.json';bound(source)
    dll=C.CDLL(str(base/'reader.dll'))
    dll.TlkTitleBankLoad.argtypes=[C.c_void_p,C.c_size_t];dll.TlkTitleBankLoad.restype=C.c_void_p
    dll.TlkTitleBankFree.argtypes=[C.c_void_p]
    dll.TlkTitleBankPacketAt.argtypes=[C.c_uint];dll.TlkTitleBankPacketAt.restype=C.POINTER(Packet)
    dll.TlkTitleBankPayload.argtypes=[C.c_void_p,C.c_uint,C.POINTER(C.c_size_t)];dll.TlkTitleBankPayload.restype=C.c_void_p
    raw=(base/'title-bank.assets').read_bytes();blob=C.create_string_buffer(raw);bank=dll.TlkTitleBankLoad(blob,len(raw));assert bank;C.memset(blob,0,len(raw))
    packets=[];rom=(ROOT/'Lion King, The (USA).sfc').read_bytes()
    try:
        for i in range(16):
            p=dll.TlkTitleBankPacketAt(i).contents;n=C.c_size_t();ptr=dll.TlkTitleBankPayload(bank,i,C.byref(n));assert ptr
            data=C.string_at(ptr,n.value);packets.append((p,data));checks[f'{i}_owned_length']=n.value==p.size
            if i!=1:checks[f'{i}_original_source_bytes']=data==rom[p.source&0x3fffff:(p.source&0x3fffff)+p.size]
            if i>=2:
                src=int.from_bytes(rom[0x22694+(i-2)*4:0x22697+(i-2)*4],'little')
                checks[f'{i}_original_list_entry']=src==p.source and p.command==2 and p.id==data[3] and p.directory==0x2300+p.id*4
        n=C.c_size_t(99);checks['index_bounds']=not dll.TlkTitleBankPacketAt(16) and not dll.TlkTitleBankPayload(bank,16,C.byref(n)) and n.value==0
        for width in (256,320):
            folder=source.parent/str(width);before=(folder/'before-aram.bin').read_bytes();after=(folder/'after-aram.bin').read_bytes();expected=bytearray(before);written=set()
            for i,(p,data) in enumerate(packets):
                expected[p.destination:p.destination+p.size]=data
                if p.command==2:
                    start=p.destination+3+int.from_bytes(data[4:6],'little');loop=p.destination+3+int.from_bytes(data[6:8],'little')
                    checks[f'{width}_{i}_sample_bounds']=p.destination<=start<p.destination+p.size and p.destination<=loop<p.destination+p.size
                    expected[p.directory:p.directory+4]=struct.pack('<HH',start,loop);written.add(p.id)
                    checks[f'{width}_{i}_original_directory']=after[p.directory:p.directory+4]==expected[p.directory:p.directory+4]
            checks[f'{width}_whole_owned_payload']=expected[0x25c8:0xf4fb]==after[0x25c8:0xf4fb]
            checks[f'{width}_score_original']=packets[1][1]==after[0x25f9:0x38c7]
            checks[f'{width}_unassigned_directory_preserved']=all(before[0x2300+i*4:0x2304+i*4]==after[0x2300+i*4:0x2304+i*4] for i in range(178) if i not in written)
            checks[f'{width}_observed_upper_tail_preserved']=before[0xf4fb:]==after[0xf4fb:]
            events=[json.loads(line) for line in (folder/'audio.jsonl').read_text().splitlines()];a,b=events
            checks[f'{width}_original_bank5']=a['a']==5 and a['pc']==0xc082a5 and b['pc']==0xc082bb
            checks[f'{width}_quiet_boundaries']=all(not any(r['gains']) and not any(r['keys_on']) and not r['queue_depth'] for r in events)
            checks[f'{width}_observed_upload65']=b['age']-a['age']==65
            outside=[i for i,(x,y) in enumerate(zip(expected,after)) if x!=y]
            observed[str(width)]=dict(events=events,unmodeled_aram_changed_bytes=len(outside),unmodeled_aram_addresses=[hex(i) for i in outside],
                note='Source payload/directory program verified; SPC execution/driver state, clocks and live PCM are not implemented by this reader.')
        checks['same_program_both_widths']=(source.parent/'256/after-aram.bin').read_bytes()[0x25c8:0xf4fb]==(source.parent/'320/after-aram.bin').read_bytes()[0x25c8:0xf4fb]
    finally:dll.TlkTitleBankFree(bank)
    def reject(name,data,reseal=False):
        if reseal:data[56:88]=hashlib.sha256(data[112:]).digest()
        blob=C.create_string_buffer(bytes(data));bank=dll.TlkTitleBankLoad(blob,len(data));checks[name]=not bank
        if bank:dll.TlkTitleBankFree(bank)
    for name,offset,value in [('version',8,2),('header',12,116),('count',20,15),('bank',88,12),('base',92,0x2400),
                              ('score-base',96,0x25de),('end',100,0xe870),('reserved',104,1),('source',112,0),('destination',116,0),
                              ('size',120,335),('command',124,2),('id',128,1),('directory',132,0x2300)]:
        data=bytearray(raw);struct.pack_into('<I',data,offset,value);reject(name,data,True)
    data=bytearray(raw);data[-1]^=1;reject('corruption',data)
    data=bytearray(raw);data[24]^=1;reject('source_identity',data)
    for name,data in [('truncated',bytearray(raw[:-1])),('trailing',bytearray(raw+b'\0'))]:
        struct.pack_into('<I',data,16,len(data));reject(name,data,True)
    helper=base/'cmake/tlk_prepare_final_assets.exe';repeat=out/'repeat.assets'
    r=subprocess.run([str(helper),'--snes-title-bank',str(ROOT/'Lion King, The (USA).sfc'),'--output',str(repeat)],capture_output=True)
    checks['repeat_identical']=r.returncode==0 and repeat.read_bytes()==raw
    r=subprocess.run([str(helper),'--snes-title-bank',str(ROOT/'Lion King, The (World).md'),'--output',str(repeat)],capture_output=True)
    checks['wrong_rom_preserves']=r.returncode==4 and repeat.read_bytes()==raw
    for flag,name,sha in [('--snes-rom','native','74364047aecdcb16cd10bead0bcf8538b845e5881f7bb54920c3a03fd7ef80ce'),('--md-rom','menu','f1e4e1f4fed4f19642b545e402c359d3fa6d1b457d2205f2470cbea1fc0bd075')]:
        path=out/(name+'.assets');r=subprocess.run([str(helper),flag,str(ROOT/('Lion King, The (USA).sfc' if flag=='--snes-rom' else 'Lion King, The (World).md')),'--output',str(path)],capture_output=True)
        checks[name+'_unchanged']=r.returncode==0 and digest(path)==sha
    symbols=subprocess.check_output(['C:/mingw32/bin/nm.exe',str(base/'reader.dll')],text=True)
    checks['decoder_free_reader']='TlkMdDecompress' not in symbols and 'TlkTitleBankPrepare' not in symbols
    paths=[Path(__file__),source,base/'reader.dll',base/'title-bank.assets',helper,*[ROOT/'engine/runner'/n for n in ('tlk_title_bank.c','tlk_title_bank.h','tlk_title_bank_prepare.c','tlk_title_bank_prepare.h')]]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observed,
                scope='Installer bank5 source packets/directory program only; no playback shortcut or title timing claim',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True);assert all(checks.values())

if __name__=='__main__':main()
