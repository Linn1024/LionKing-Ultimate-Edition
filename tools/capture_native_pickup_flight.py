"""Sample executed native pickup flight lifetimes from the active actor list.

Original LLE on an ordinary tape, without guest edits. Sparse post-frame RAM
samples are lifetime evidence, not per-instruction execution or timing parity.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess

from audit_scenes import ROOT,read_rom


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',default='build/native-pickup-flight')
    parser.add_argument('--reuse',action='store_true',help='Parse retained raw captures after a failed analysis; never rerun or replace them.')
    parser.add_argument('--raw-from',type=Path,help='Analyze retained captures into a fresh output directory.')
    args=parser.parse_args();out=(ROOT/args.out).resolve()
    assert out.is_relative_to(ROOT/'build')
    if args.reuse:assert out.is_dir() and not (out/'report.json').exists()
    else:out.mkdir()
    rom=ROOT/'Lion King, The (USA).sfc'
    read_rom(rom.name,'457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    exe=ROOT/'engine/build-win/tlk_headless.exe';tape=ROOT/'engine/tapes/allbugsF.read.tape'
    frames=list(range(900,4001,4))
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    env.update(TLK_WRAM_DUMP=','.join(map(str,frames)),TLK_WRAM_DIR=str(out))
    command=list(map(str,[exe,'--rom',rom,'--input-polled',tape,'--frames',4000,'--lle']))
    raw=(ROOT/args.raw_from).resolve() if args.raw_from else out
    assert raw.is_relative_to(ROOT/'build')
    if not args.reuse and not args.raw_from:
        with (out/'run.log').open('wb') as stream:
            subprocess.run(command,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=300)
    rows=[]
    for field in frames:
        ram=(raw/f'hl_wram_{field}.bin').read_bytes()
        w=lambda at:struct.unpack_from('<H',ram,at)[0]
        addr=lambda at:int.from_bytes(ram[at:at+3],'little')
        if w(0x1ff9e) or addr(0xdf) not in (0xc00387,0xc0080d):continue
        at=w(0x76);previous=0;seen=set()
        while at:
            assert 0x8000<=at<=0xff80 and at not in seen and len(seen)<80 and w(at)==previous,(field,at)
            seen.add(at);action=addr(at+0x30)
            if action in (0xc55247,0xc55413):
                draw=w(at+12);assert 0x8000<=draw<=0xffe0
                rows.append(dict(field=field,actor=at,action=hex(action),pose=hex(addr(draw+10)),
                    flags=hex(w(draw+8)),fixed=bool(w(draw+8)&0x4000),palette=w(draw+8)>>1&7,
                    x=w(at+8),y=w(at+10),descriptor=hex(addr(at+4))))
            previous,at=at,w(at+2)
    metadata_path=ROOT/'tools/pride_npc_pairs.json'
    metadata={int(r['snes'],16):r for r in json.loads(metadata_path.read_text())['pairs'] if r['role']=='pickup'}
    fixed=[r for r in rows if r['fixed']]
    missing=sorted({r['pose'] for r in fixed if int(r['pose'],16) not in metadata})
    paths=[Path(__file__),exe,tape,metadata_path,raw/'run.log']
    if raw!=out:paths += sorted(raw.glob('hl_wram_*.bin'))
    report=dict(result='OBSERVED' if fixed else 'NO_FLIGHT_OBSERVED',observations=rows,
        fixed_active_flight_samples=len(fixed),poses=sorted({r['pose'] for r in fixed}),
        actions=sorted({r['action'] for r in fixed}),unreviewed_flight_poses=missing,
        ordinary_input_no_guest_edits=True,active_list_checked=True,sampling_interval=4,
        production_mappings_unchanged=True,all_flight_types_verified=False,command=command,
        rom_sha256=digest(rom),retained_raw_captures_reanalyzed=args.reuse,
        retained_capture_directory=raw.relative_to(ROOT).as_posix(),
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(fixed),'active fixed-flight samples; poses',report['poses'],flush=True)


if __name__=='__main__':main()
