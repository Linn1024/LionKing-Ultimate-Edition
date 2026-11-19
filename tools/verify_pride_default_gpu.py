"""Verify original default-death/revival display geometry and uploaded textures."""
import json
from pathlib import Path
import struct
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_prepared_state import rows
from pride_sprite_catalog import md_frame


def main():
    base=ROOT/'build/pride-default-actor/original-sat';capture=json.loads((base/'report.json').read_text())
    assert capture['result']=='PASS' and not capture['guest_edits'] and not capture['loaded_states']
    for name,sha in capture['source_sha256'].items():assert digest(ROOT/name)==sha,name
    for name,sha in capture['artifacts_sha256'].items():assert digest(base/name)==sha,name
    fields={r['age']:r for r in json.loads((base/'fields.json').read_text())}
    death={int(r['age']):r for r in rows(ROOT/'build/pride-death-controller/original-fields.csv') if r['case']=='9'}
    revival={int(r['age']):r for r in rows(ROOT/'build/pride-revival-scene/original-revival.csv') if r['case']=='8'}
    rom=(ROOT/'Lion King, The (World).md').read_bytes();data=(base/'sat.bin').read_bytes();size=66732
    assert data[:8]==b'MDOSAT01' and len(data)==8+321*size
    checked=0;visible=[]
    def matches(age,pose,cx,cy):
        sprites=fields[age]['sprites'];pieces=md_frame(rom,pose);assert pieces
        vram=data[8+age*size+1196:8+(age+1)*size];result=[]
        for first in range(len(sprites)-len(pieces)+1):
            geometry=True
            for n,(dx,dy,w,h,texture) in enumerate(pieces):
                s=sprites[first+n];attr=s['attr']
                expected=(cx-dx-w if attr&0x800 else cx+dx,cy-dy-h if attr&0x1000 else cy+dy,w,h)
                if (s['x'],s['y'],s['width'],s['height'])!=expected:geometry=False;break
            if not geometry:continue
            count=0;exact=True
            for n,(dx,dy,w,h,texture) in enumerate(pieces):
                attr=sprites[first+n]['attr']
                for y in range(h):
                    for x in range(w):
                        a=((attr&0x7ff)+(x//8)*(h//8)+y//8)*32+(y&7)*4+(x&7)//2
                        b=texture+((x//8)*(h//8)+y//8)*32+(y&7)*4+(x&7)//2
                        if (vram[a^1]>>(0 if x&1 else 4)&15)!=(rom[b]>>(0 if x&1 else 4)&15):exact=False
                        count+=1
            if exact:result.append((first,count))
        return result
    for age in range(1,249):
        logical=min(age-(1 if age<=24 else 2),224);position=min(max(age-2,0),224)
        r=death[logical];p=death[position];pose=int(r['md_pose'])
        found=matches(age,pose,int(p['x'])-int(p['camera_x']),int(p['y'])-int(p['camera_y']))
        assert len(found)==1 and found[0][0]==0,(age,hex(pose),found)
        assert len(fields[age]['sprites'])==len(md_frame(rom,pose))
        checked+=found[0][1];visible.append(dict(age=age,pose=pose,phase='death',cpu_age=logical))
    for age in range(277,321):
        logical=age-(1 if age>300 else 2)
        pose=int(revival[logical]['md_pose']) if logical<=300 else fields[logical]['pose']
        row=fields[age];cx=row['hero'][0]-row['camera'][0];cy=row['hero'][1]-row['camera'][1]
        found=matches(age,pose,cx,cy);assert len(found)==1,(age,hex(pose),cx,cy,found)
        checked+=found[0][1];visible.append(dict(age=age,pose=pose,phase='revival',cpu_age=logical,first_slot=found[0][0]))
    assert fields[305]['pose']!=fields[304]['pose']
    first_second=next(r['age'] for r in visible if r['phase']=='revival' and r['pose']==fields[305]['pose'])
    assert first_second==306
    availability=[]
    for age in range(254,277):
        row=fields[age];pose=int(revival[age]['md_pose'])
        if matches(age,pose,row['hero'][0]-row['camera'][0],row['hero'][1]-row['camera'][1]):availability.append(age)
    (base/'visible-poses.json').write_text(json.dumps(visible,indent=2)+'\n')
    sources=[Path(__file__),base/'report.json',base/'fields.json',base/'sat.bin',base/'visible-poses.json',
             ROOT/'build/pride-death-controller/original-fields.csv',ROOT/'build/pride-revival-scene/original-revival.csv',
             ROOT/'tools/pride_sprite_catalog.py',ROOT/'Lion King, The (World).md']
    result=dict(result='PASS',scope=__doc__,death_fields=248,revival_and_normal_fields=44,texture_indices=checked,
        death_prefix_pose_delay=1,death_main_pose_delay=2,death_position_delay=2,
        first_next_idle_cpu_age=305,first_next_idle_gpu_age=306,normal_play_pose_delay=1,pre_color_idle_sat_ages=availability,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sources},
        full_first_level_fidelity_complete=False)
    (base/'gpu-report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Original default GPU248 death/44 revival-normal fields, '+str(checked)+' texture indices exact',flush=True)


if __name__=='__main__':main()
