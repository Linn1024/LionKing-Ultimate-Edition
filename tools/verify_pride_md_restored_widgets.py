"""Compare ordinary original-MD revival HUD uploads with original CPU fonts.

Source widget semantics, source geometry and indices only. Does not certify
private presenter layout, final occlusion, other maxima or other life contexts.
"""
import hashlib
import json
from pathlib import Path
import struct
from audit_scenes import ROOT


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def sprite_indices(vram,sprite):
    assert not sprite['attr']&0x1800
    attr=sprite['attr'];w=sprite['width'];h=sprite['height']
    return bytes((vram[((((attr&0x7ff)+(x//8)*(h//8)+y//8)*32+(y&7)*4+(x&7)//2)&65535)^1]
                  >>(0 if x&1 else 4))&15 for y in range(h) for x in range(w))


def source_indices(raw,w,h):
    return bytes((raw[(x//8*(h//8)+y//8)*32+(y&7)*4+(x&7)//2]>>(0 if x&1 else 4))&15
                 for y in range(h) for x in range(w))


def main():
    out=ROOT/'build/pride-checkpoint-player/md-restored-widgets';out.mkdir(exist_ok=True)
    parent=ROOT/'build/pride-scene-sat-full';capture_path=parent/'report.json'
    capture=json.loads(capture_path.read_text());assert capture['result']=='PASS'
    for name,sha in capture['source_sha256'].items():assert digest(ROOT/name)==sha,name
    for name,sha in capture['artifacts_sha256'].items():assert digest(parent/name)==sha,name
    records={r['age']:r for r in json.loads((parent/'fields.json').read_text())}
    source=ROOT/'build/pride-hud/original-meter-reference.bin'
    raw=source.read_bytes();assert len(raw)==225*710
    fonts={struct.unpack_from('<3H',raw,at):raw[at+6:at+710] for at in range(0,len(raw),710)}
    assert len(fonts)==225
    counters_path=ROOT/'build/pride-checkpoint-player/md-restored-widget-counters/report.json'
    counters_report=json.loads(counters_path.read_text())
    assert counters_report['result']=='PASS' and not counters_report['guest_edits'] and not counters_report['loaded_states']
    for name,sha in counters_report['source_sha256'].items():assert digest(ROOT/name)==sha,name
    counters={r['age']:r for r in counters_report['fields']}
    snes_path=ROOT/'Lion King, The (USA).sfc';md_path=ROOT/'Lion King, The (World).md'
    md=md_path.read_bytes()
    native_ram_path=ROOT/'build/pride-scene-owner-headless/native-scheduled/normal-wram.bin'
    native_ram=native_ram_path.read_bytes()
    native_maximum,roar_maximum,lives=(struct.unpack_from('<H',native_ram,a)[0] for a in (0x1ffac,0x1ffae,0x1ffaa))
    assert (native_maximum,roar_maximum,lives)==(6,24,7)
    data=(parent/'sat.bin').read_bytes();size=66732
    assert data[:8]==b'MDOSAT01' and len(data)==8+361*size
    observations=[];compared=0
    for age in range(273,347):
        record=data[8+age*size:8+(age+1)*size]
        assert struct.unpack_from('<II',record)==(4755+age,age)
        vram=record[1196:];sprites=records[age]['sprites']
        assert records[age]['health']==native_maximum
        assert counters[age]['roar_max']==roar_maximum and counters[age]['roar']==0
        for kind,first,maximum,current,origin in ((0,0,roar_maximum,counters[age]['roar'],16),
                                                 (1,5,native_maximum,native_maximum,320-32-native_maximum*4)):
            font=fonts[kind,maximum,current]
            for n,(dx,w,offset) in enumerate(((5,8,0),(8,32,64),(40,32,320))):
                sprite=sprites[first+n]
                assert (sprite['x'],sprite['y'],sprite['width'],sprite['height'])==(origin+dx,16,w,16),(age,kind,n)
                assert sprite['palette']==0 and sprite['priority']==1
                actual=sprite_indices(vram,sprite)
                expected=source_indices(font[offset:],w,16)
                if actual!=expected:
                    matches=[key for key,font_data in fonts.items() if key[0]==kind and
                             actual==source_indices(font_data[offset:],w,16)]
                    raise AssertionError((age,kind,n,'font mismatch; original CPU candidates',matches))
                compared+=len(actual)
        portrait,digit=sprites[3:5]
        assert (portrait['x'],portrait['y'],portrait['width'],portrait['height'])==(22,194,24,24)
        assert (digit['x'],digit['y'],digit['width'],digit['height'])==(48,200,16,16)
        assert all(s['palette']==0 and s['priority']==1 for s in (portrait,digit))
        actual=sprite_indices(vram,portrait)
        assert actual==source_indices(md[0x8f1f8:],24,24),(age,'portrait')
        compared+=len(actual)
        actual=sprite_indices(vram,digit)
        candidates=[n for n in range(10) if actual==source_indices(md[0x8f438+n*128:],16,16)]
        assert candidates==[lives],(age,'life digit',candidates,lives)
        compared+=len(actual)
        observations.append(dict(age=age,health=[native_maximum,native_maximum],
            roar=[roar_maximum,counters[age]['roar']],displayed_life_digit=lives,
            roar_origin=[16,16],health_origin=[320-32-native_maximum*4,16],
            portrait_origin=[22,194],digit_origin=[48,200]))
    sources=[Path(__file__),capture_path,parent/'fields.json',parent/'sat.bin',source,
             ROOT/'tools/pride_hud_audit.py',ROOT/'build/md-lab/game.state',
             ROOT/'build/pride-checkpoint-player/md-restored-widget-oracle.log',
             md_path,snes_path,native_ram_path,counters_path,
             ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    result=dict(result='PASS',scope=__doc__,original_uploaded_fields=len(observations),
        original_uploaded_texture_indices=compared,original_cpu_oracle_cases=225,
        restored_health_maximum_and_current=6,restored_roar_maximum=24,restored_roar_current=0,
        native_canonical_roar_current=24,private_full_roar_source_semantics_divergence_open=True,
        displayed_life_digit_matches_native_counter=7,observations=observations,
        actual_windows_or_private_presenter_verified=False,full_first_level_fidelity_complete=False,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sources})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(str(compared)+' original MD HUD upload indices/geometry exact on74 fields; health6, roar0 of24, life digit7. Private full-roar divergence OPEN',flush=True)


if __name__=='__main__':main()
