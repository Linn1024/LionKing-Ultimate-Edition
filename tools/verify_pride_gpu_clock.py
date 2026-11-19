"""Derive visible MD pose clocks from actual SAT geometry and VRAM indices."""
import csv
import hashlib
import json
from pathlib import Path
import struct
from audit_scenes import ROOT
from pride_sprite_catalog import md_frame


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-gpu-clock';out.mkdir(exist_ok=True)
    source=ROOT/'build/pride-scene-sat-full';capture=json.loads((source/'report.json').read_text());assert capture['result']=='PASS'
    rom=(ROOT/'Lion King, The (World).md').read_bytes()
    rows={r['age']:r for r in json.loads((source/'fields.json').read_text())}
    death={int(r['age']):r for r in csv.DictReader((ROOT/'build/pride-death-controller/original-fields.csv').open()) if r['case']=='0'}
    revival={int(r['age']):r for r in csv.DictReader((ROOT/'build/pride-revival-scene/original-revival.csv').open()) if r['case']=='0'}
    size=66732;data=(source/'sat.bin').read_bytes();assert data[:8]==b'MDOSAT01' and len(data)==8+361*size
    checked=0;result=[]
    def verify(age,pose,cx,cy,first):
        nonlocal checked
        record=data[8+age*size:8+(age+1)*size];assert struct.unpack_from('<II',record)==(4755+age,age)
        vram=record[1196:];sprites=rows[age]['sprites'];pieces=md_frame(rom,pose);assert pieces
        for n,(dx,dy,w,h,texture) in enumerate(pieces):
            s=sprites[first+n];attr=s['attr'];flipx=bool(attr&0x800);flipy=bool(attr&0x1000)
            expected=(cx-dx-w if flipx else cx+dx,cy-dy-h if flipy else cy+dy,w,h)
            assert (s['x'],s['y'],s['width'],s['height'])==expected,(age,hex(pose),n,'geometry',s,expected)
            for y in range(h):
                for x in range(w):
                    # Compare unflipped texture indices; hardware flips are
                    # checked in the geometry transform above, not baked in.
                    a=((attr&0x7ff)+(x//8)*(h//8)+y//8)*32+(y&7)*4+(x&7)//2
                    b=texture+((x//8)*(h//8)+y//8)*32+(y&7)*4+(x&7)//2
                    actual=vram[a^1]>>(0 if x&1 else 4)&15
                    expected=rom[b]>>(0 if x&1 else 4)&15
                    assert actual==expected,(age,hex(pose),n,x,y,actual,expected)
                    checked+=1
        return len(pieces)
    assert rows[0]['linked']>len(md_frame(rom,int(death[0]['md_pose'])))
    for age in range(1,249):
        logical=min(age-(1 if age<=24 else 2),224);position=min(max(age-2,0),224);r=death[logical];p=death[position];pose=int(r['md_pose'])
        cx=int(p['x'])-int(p['camera_x']);cy=int(p['y'])-int(p['camera_y'])
        count=verify(age,pose,cx,cy,0);assert rows[age]['linked']==count
        result.append(dict(age=age,phase='death',cpu_reference_age=logical,position_cpu_age=position,md_pose=pose,snes_pose=int(r['snes_pose'])))
    for age in range(273,347):
        logical=age-2;r=revival[logical];pose=int(r['md_pose']);row=rows[age]
        cx=row['hero'][0]-row['camera'][0];cy=row['hero'][1]-row['camera'][1]
        count=verify(age,pose,cx,cy,8)
        # The separate static checkpoint head follows the other world object.
        verify(age,0x973b6,128,96,9+count)
        result.append(dict(age=age,phase='revival',cpu_reference_age=logical,md_pose=pose,snes_pose=int(r['snes_pose'])))
    (out/'visible-poses.json').write_text(json.dumps(result,indent=2)+'\n')
    report=dict(result='PASS',scope=__doc__,death_fields=248,revival_fields=74,
        compared_texture_indices=checked,death_prelude_pose_delay_fields=1,death_main_pose_delay_fields=2,
        death_position_gpu_delay_fields=2,revival_gpu_delay_fields=2,
        preceding_gameplay_retained_at_death0=True,static_checkpoint_head_separate=True,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in
            (Path(__file__),source/'report.json',source/'fields.json',source/'sat.bin',
             ROOT/'build/pride-death-controller/original-fields.csv',ROOT/'build/pride-revival-scene/original-revival.csv',
             ROOT/'Lion King, The (World).md',out/'visible-poses.json')},
        full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Original MD visible clocks:248 death/74 revival fields, SAT geometry and',checked,'VRAM indices exact PASS',flush=True)


if __name__=='__main__':main()
