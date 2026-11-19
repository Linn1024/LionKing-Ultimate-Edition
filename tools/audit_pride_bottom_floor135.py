"""Locate bottom floor-query coverage; does not prove natural fall reachability."""
import ctypes as C
import json
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

def main():
    out=ROOT/'build/pride-bottom-floor135';out.mkdir()
    reference=ROOT/'build/pride-enemy-gates96/report.json';r=bound(reference)
    assert r['result']=='ENEMY_GATES_AND_PROBE_DIFFERENCE_QUALIFIED'
    frames=ROOT/'build/pride-hyena-recovery/snes/normal/frames.json'
    first=json.loads(frames.read_text())[0]
    snapshot=frames.parent/f'hl_wram_{first["field"]}.bin'
    assert digest(snapshot)==r['source_sha256'][snapshot.relative_to(ROOT).as_posix()]
    ram=snapshot.read_bytes();word=lambda at:struct.unpack_from('<H',ram,at)[0]
    assert len(ram)==0x20000 and (word(0xd0),word(0xd4))==(200,80)
    source=Path(__file__).with_name('pride_bottom_floor_oracle135.c');runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c'
    command=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc','-I'+str(ROOT/'engine/snesrecomp/runner/src/snes'),str(source),str(runtime),'-o',str(out/'oracle.dll')]
    subprocess.run(command,check=True)
    rompath=ROOT/'Lion King, The (USA).sfc'
    rom=read_rom(rompath.name,'457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    oracle=C.CDLL(str(out/'oracle.dll'));oracle.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    assert oracle.terrain_native_init(C.create_string_buffer(rom),len(rom))
    oracle.bottom_floor135.argtypes=[C.c_void_p,C.c_uint,C.c_uint,C.c_uint,C.POINTER(C.c_uint)]
    data=C.create_string_buffer(ram);total=0;columns=[]
    with (out/'queries.jsonl').open('w') as log:
        for x in range(1600):
            hits=[]
            for y in range(1248,1280):
                raw=(C.c_uint*5)();assert oracle.bottom_floor135(data,len(ram),x,y,raw),(x,y)
                log.write(json.dumps(dict(x=x,y=y,carry=raw[0],raw_delta=raw[1],tag=raw[2],flags=raw[3]),separators=(',',':'))+'\n')
                if raw[0]:hits.append(y)
                total+=1
            columns.append(dict(x=x,blocking_y=hits))
    gaps=[c['x'] for c in columns if not c['blocking_y']]
    (out/'columns.json').write_text(json.dumps(columns,separators=(',',':'))+'\n')
    checks=dict(all51200_original_queries_returned=total==51200,actual_snapshot_bound=True,original_map1600x1280=True)
    paths=[Path(__file__),source,ROOT/'tools/pride_terrain_native_oracle.c',runtime,reference,frames,snapshot,rompath]
    report=dict(result='BOTTOM_FLOOR_QUERY_DOMAIN_CAPTURED',checks=checks,fixtures=total,columns_without_any_hit=gaps,
        hit_columns=1600-len(gaps),query_y=[1248,1279],scope='Original native C0C4A7 floor queries on a bound actual normal-fight full RAM snapshot. Enumerates bottom32 rows in pixels at every map X. Raw carry/delta only; no player sweep, MD equivalence, floor barrier, natural reachability or fall transition claim.',
        production_changed=False,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],checks,'hit columns',report['hit_columns'],'gap columns',gaps[:24],flush=True)
if __name__=='__main__':main()
