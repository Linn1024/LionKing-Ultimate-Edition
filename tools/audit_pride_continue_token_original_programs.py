"""Bind original Sun animation, descriptor and pickup-cue operands exactly."""
import json
from pathlib import Path
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-continue-token-source-audit';out.mkdir()
    snes_path=ROOT/'Lion King, The (USA).sfc';md_path=ROOT/'Lion King, The (World).md'
    s=read_rom(snes_path.name,'457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    m=read_rom(md_path.name,'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    observed=ROOT/'build/md-continue-token-original2/report.json';assert bound(observed)['result']=='PASS'
    be16=lambda a:int.from_bytes(m[a:a+2],'big');be32=lambda a:int.from_bytes(m[a:a+4],'big')
    native=[dict(duration=s[a],pose=int.from_bytes(s[a+1:a+4],'little')) for a in range(0x23e4b,0x23e5b,4)]
    external=[dict(duration=m[a],pose=int.from_bytes(m[a+1:a+4],'big')) for a in range(0x17ec12,0x17ec22,4)]
    descriptor=lambda a:dict(handler=be32(a),flags=be16(a+4),pose=be32(a+6),callback=be32(a+10))
    sun=descriptor(0x950e0);neighbor=descriptor(0x950ee)
    checks=dict(native_four_duration4=[r['duration'] for r in native]==[4]*4,
                md_four_duration5=[r['duration'] for r in external]==[5]*4,
                native_pose_family=[r['pose'] for r in native]==[0xc6f764,0xc6f79b,0xc6f7ce,0xc6f801],
                md_pose_family=[r['pose'] for r in external]==[0x18b3f8,0x18b430,0x18b468,0x18b4a0],
                native_loop=s[0x23e5b]==255 and int.from_bytes(s[0x23e5c:0x23e5f],'little')==0xc23e4b,
                md_loop=m[0x17ec22]==255 and int.from_bytes(m[0x17ec23:0x17ec26],'big')==0x17ec12,
                sun_descriptor=sun==dict(handler=0x18fd02,flags=0,pose=0x18b3f8,callback=0x18fd02),
                neighbor_is_distinct=neighbor==dict(handler=0x19c604,flags=0,pose=0xd19fc,callback=0x19c604),
                early_level_music_operand=be16(0x18fd78)==0x3f3c and be16(0x18fd7a)==15 and be16(0x18fd7c)==0x4eb9 and be32(0x18fd7e)==0x2210,
                later_level_fm_operand=be16(0x18fdb2)==0x3f3c and be16(0x18fdb4)==114 and be16(0x18fdb6)==0x4eb9 and be32(0x18fdb8)==0x228a,
                neighbor_fm94_operand=be16(0x19c6c0)==0x3f3c and be16(0x19c6c2)==94 and be32(0x19c6c6)==0x228a,
                native_event_hex13=s[0x55969]==0xf4 and int.from_bytes(s[0x5596a:0x5596c],'little')==0x13 and s[0x5596c]==0x22 and int.from_bytes(s[0x5596d:0x55970],'little')==0xc22cec)
    paths=[Path(__file__),snes_path,md_path,observed]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,native_stream=native,md_stream=external,
                sun_descriptor=sun,neighbor_descriptor=neighbor,
                native_pickup_event_hex='0x13',md_pride_music=15,md_later_level_fm=114,
                former_fm94_note_incorrect=True,pickup_contact_branch_not_yet_replayed=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)


if __name__=='__main__':main()
