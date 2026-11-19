"""Check popup ownership using captured original actors and hostile neighbours."""
import ctypes as C
import json
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    out=ROOT/'build/pride-popup-work/guards4'
    out.mkdir()
    header=ROOT/'engine/runner/tlk_pickup_popup_role.h'
    source=out/'guard.c'
    source.write_text('#include "tlk_pickup_popup_role.h"\n'
        '__declspec(dllexport) int check(const uint8_t *r,unsigned n,unsigned d,unsigned p,int f)'
        '{return TlkPickupPopupDrawRole(r,n,d,p,f!=0);}\n')
    library=out/'guard.dll'
    subprocess.run(['C:/mingw32/bin/gcc.exe','-shared','-O2','-I'+str(header.parent),
                    str(source),'-o',str(library)],check=True)
    dll=C.CDLL(str(library));fn=dll.check
    fn.argtypes=[C.c_void_p,C.c_uint,C.c_uint,C.c_uint,C.c_int]
    paths=[Path(__file__),header]
    observations=json.loads((ROOT/'build/pride-pickup-arrival-audio/report.json').read_text())['native_sparse_active_observations']
    checks={};seen=set();example=None
    for row in observations:
        path=ROOT/f'build/native-pickup-flight/hl_wram_{row["field"]}.bin'
        ram=bytearray(path.read_bytes());actor=row['actor'];draw=struct.unpack_from('<H',ram,actor+12)[0]
        pose=int(row['pose'],16);seen.add(pose)
        def run(data=ram,n=None,d=draw,p=pose,f=1):
            buf=(C.c_ubyte*len(data)).from_buffer_copy(data)
            return bool(fn(buf,len(data) if n is None else n,d,p,f))
        checks[f'live/{row["field"]}/{actor:x}']=run()
        paths.append(path)
        if example is None:
            example=(ram,draw,pose,actor)
    assert len(seen)==12, 'Live evidence must cover the entire native popup family'
    ram,draw,pose,actor=example
    def run(data=ram,n=None,d=draw,p=pose,f=1):
        buf=(C.c_ubyte*len(data)).from_buffer_copy(data)
        return bool(fn(buf,len(data) if n is None else n,d,p,f))
    for label,offset in [('foreign_action',actor+0x30),('foreign_descriptor',actor+4),
                         ('broken_actor_owner',actor+12),('broken_position_owner',draw+4),
                         ('wrong_draw_pose',draw+10),('foreign_palette',draw+8),
                         ('another_level',0x1ff9e),('adult_simba',0x2000),('foreign_scene',0xdf),
                         ('foreign_anchor',actor+8),('foreign_height',actor+10)]:
        changed=bytearray(ram);changed[offset]^=2
        checks[label]=not run(changed)
    changed=bytearray(ram);changed[draw+9]&=~0x40
    checks['not_screen_fixed']=not run(changed)
    checks['short_buffer']=not run(n=65536)
    checks['bad_draw_pointer']=not run(d=0xffff)
    checks['unreviewed_pose']=not run(p=0xc528bc)
    checks['caller_not_fixed']=not run(f=0)
    # Actual client3 exposes latched C6FD29 while the live actor has C6FD4C.
    poses=[0xc6fd06,0xc6fd29,0xc6fd4c,0xc6fd73,0xc6fd94,0xc6fdbb,
           0xc6fde6,0xc6fe0b,0xc6fe30,0xc6fe55,0xc6fe7c,0xc6fe9d]
    changed=bytearray(ram)
    changed[draw+10:draw+13]=poses[2].to_bytes(3,'little')
    checks['latched_previous_phase_owned']=run(changed,p=poses[1])
    checks['two_phase_mismatch_rejected']=not run(changed,p=poses[0])
    checks['future_display_phase_rejected']=not run(changed,p=poses[3])
    # Palette provenance comes from actual original MD callbacks, not an image match.
    md=(ROOT/'Lion King, The (World).md').read_bytes()
    colors=struct.unpack_from('>16H',md,0x1d78aa)
    expected=[(c>>1&7)|(c>>5&7)<<3|(c>>9&7)<<6 for c in colors]
    import csv
    calls_path=ROOT/'build/pride-popup-original/calls.csv'
    calls=[r for r in csv.DictReader(calls_path.open()) if r['callback']=='190048']
    checks['original_live_md_palette']=bool(calls) and all(r['palette']=='0' and
        [int(r['colors'][i:i+4],16) for i in range(4,64,4)]==expected[1:] for r in calls)
    paths.append(calls_path)
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                native_poses_covered=len(seen),
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'ownership/palette checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
