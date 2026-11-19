"""Compare original pickup-arrival popup actions before enabling a new sound leaf.

Native sparse actor history and complete event trace are ordinary input runs.
MD evidence is actual original driver entry, not a sound-number similarity claim.
"""
import csv
import json
import os
from pathlib import Path
import struct
import subprocess

from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    out=ROOT/'build/pride-pickup-arrival-audio';out.mkdir()
    md_path=ROOT/'build/pride-audio-inventory/report.json';md=bound(md_path)
    assert md['result']=='ORIGINAL_PRIDE_CENSUS_CAPTURED'
    md_calls=[r for r in csv.DictReader((md_path.parent/'commands.csv').open())
        if r['level']=='1' and r['selector']=='2' and r['value']=='112' and
           r['outer_caller']=='19003e' and r['actor_state']=='18ffe6']
    assert len(md_calls)==2
    native_capture=ROOT/'build/native-pickup-flight2/report.json';bound(native_capture)
    raw_dir=ROOT/'build/native-pickup-flight';observations=[]
    for field in range(900,4001,4):
        ram=(raw_dir/f'hl_wram_{field}.bin').read_bytes()
        w=lambda at:struct.unpack_from('<H',ram,at)[0]
        address=lambda at:int.from_bytes(ram[at:at+3],'little')
        if w(0x1ff9e) or address(0xdf) not in (0xc00387,0xc0080d):continue
        actor=w(0x76);seen=set()
        while actor:
            assert 0x8000<=actor<=0xff80 and actor not in seen and len(seen)<80
            seen.add(actor)
            if address(actor+0x30)==0xc55a66:
                draw=w(actor+12)
                observations.append(dict(field=field,actor=actor,descriptor=hex(address(actor+4)),
                    action=hex(address(actor+0x30)),timer=w(actor+0x2c),pose=hex(address(draw+10)),
                    fixed=bool(w(draw+8)&0x4000),palette=w(draw+8)>>1&7,x=w(actor+8),y=w(actor+10)))
            actor=w(actor+2)
    assert observations and all(r['descriptor']=='0xc5858f' and r['fixed'] and r['palette']==0 and r['timer']<=36 for r in observations)
    intervals=[]
    for actor in sorted({r['actor'] for r in observations}):
        rows=[r for r in observations if r['actor']==actor]
        groups=[]
        for row in rows:
            if not groups or row['field']>groups[-1][-1]['field']+4:groups.append([])
            groups[-1].append(row)
        for group in groups:
            intervals.append(dict(actor=actor,first_sample=group[0]['field'],last_sample=group[-1]['field'],
                initial_sample_timer=group[0]['timer'],final_sample_timer=group[-1]['timer']))
    assert len(intervals)==2,intervals
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 1\n')
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
    tape=ROOT/'engine/tapes/allbugsF.read.tape';exe=ROOT/'build/pride-flight-player/player.exe'
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    env['TLK_AUDIO_EVENTS']=str(out/'native-events.csv')
    command=[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',out/'missing.md',
        '--config',config,'--resource-profile',profile,'--input-polled',tape,'--frames',2000,
        '--lle','--no-pace','--no-audio','--no-record']
    with (out/'run.log').open('wb') as log:
        subprocess.run(list(map(str,command)),env=env,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    events=list(csv.DictReader((out/'native-events.csv').open()))
    assert events
    for interval in intervals:
        related=[r for r in events if int(r['actor'],16)==interval['actor'] and
            interval['first_sample']-4<=int(r['frame'])<=interval['last_sample']+4]
        assert not related,(interval,related)
        interval['native_direct_or_animation_audio_calls_in_enclosing_window']=0
    snes=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    external=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    assert snes[0x55ab8:0x55abb]==bytes.fromhex('a92400')
    assert external[0x19001a:0x190020]==bytes.fromhex('337c0024002c')
    assert external[0x190034:0x19003e]==bytes.fromhex('3f3c00704eb90000228a')
    paths=[Path(__file__),md_path,native_capture,tape,exe,ROOT/'engine/runner/tlk_audio.c']
    report=dict(result='ORIGINAL_PICKUP_ARRIVAL_SOUND_DIFFERENCE_VERIFIED',native_intervals=intervals,
        native_sparse_active_observations=observations,md_driver_calls=md_calls,
        native_action='C55A66',md_action='18FFE6',both_original_initial_timers=36,
        md_only_command=dict(selector=2,value=112,caller='19003e'),
        production_mapping_for_this_caller_enabled=False,ordinary_input_no_guest_edits=True,
        full_lifetime_timing_equivalence_proven=False,command=list(map(str,command)),
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],'two ordinary arrivals: MD FM112, native silent',flush=True)


if __name__=='__main__':main()
