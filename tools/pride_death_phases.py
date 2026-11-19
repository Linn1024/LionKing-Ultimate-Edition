"""Measure native death phase ownership with each independent music source.

Uses the existing read-only interpreter cycle diagnostic. Its frame label is
the completed opcode boundary, not a fabricated cross-console synchronization.
No production adapter, guest writes, saved-state loads or ROM edits.
"""
import collections
import hashlib
import json
import os
import re
import subprocess
import struct
from pathlib import Path
from audit_scenes import ROOT
from verify_windows import hashes


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


POINTS={0xc089b7:'entry',0xc08a02:'decompress_call',0xc08a06:'decompress_return',
        0xc08a61:'centering',0xc08a8f:'wait_count',0xc08a95:'sound_begin',
        0xc08ab8:'sound_end',0xc08ac3:'display_count',0xc08acb:'animation_step',
        0xc08acf:'display_wait',0xc08ad9:'display_end',0xc08af3:'life_test',
        0xc08afe:'revival_branch',0xc08b05:'restore_health',0xc08b1f:'reload_jump',
        0xc08b22:'final_life_branch'}


def parse(path):
    text=path.read_text(errors='replace')
    events=[{'frame':int(f),'pc':int(pc,16)} for f,pc in re.findall(r'\[cyc\] f=(\d+) pc=\$([0-9A-F]+)',text)
            if int(pc,16) in POINTS]
    entries=[e['frame'] for e in events if POINTS[e['pc']]=='entry'];assert entries
    deaths=[]
    for number,start in enumerate(entries):
        stop=entries[number+1] if number+1<len(entries) else 1000000
        fields=collections.defaultdict(list)
        for e in events:
            if start<=e['frame']<stop:fields[POINTS[e['pc']]].append(e['frame'])
        assert len(fields['animation_step'])==280,fields
        # The first two calls share a diagnostic host-frame label. A blocked
        # wait and resumed opcode are not an independent video-field clock.
        assert fields['animation_step'][0]==fields['animation_step'][1]
        assert fields['animation_step'][1:]==list(range(fields['animation_step'][1],fields['animation_step'][1]+279))
        assert fields['display_end'][0]==fields['animation_step'][-1]+1
        assert len(fields['entry'])==len(fields['decompress_call'])==len(fields['display_end'])==len(fields['life_test'])==1
        assert len(fields['revival_branch'])+len(fields['final_life_branch'])==1
        deaths.append({'health_death_entry':start,'completed_opcode_fields':dict(fields),
                       'entry_to_first_call_host_labels':fields['animation_step'][0]-start,
                       'entry_to_bank_return_host_labels':fields['decompress_return'][0]-start,
                       'explicit_wait_host_labels':fields['sound_begin'][0]-fields['wait_count'][0],
                       'sound_call_host_labels':fields['sound_end'][0]-fields['sound_begin'][0],
                       'display_loop_iterations':len(fields['animation_step']),
                       'final_life':bool(fields['final_life_branch'])})
    return deaths


def main():
    out=ROOT/'build/pride-death-phases';out.mkdir(exist_ok=True)
    report_path=out/'report.json';report_path.write_text(json.dumps({'result':'RUNNING'})+'\n')
    binary=ROOT/'engine/build-win/tlk_headless.exe';identity=digest(binary)
    tape=ROOT/'build/pride-health-death-native/neutral-tail.polled.tape'
    runs={}
    profiles={'native':'','level':'audio.music.pride_lands = md\n',
              'death':'audio.music.pride_health_death = md\n',
              'both':'audio.music.pride_lands = md\naudio.music.pride_health_death = md\n'}
    for name,extra in profiles.items():
        profile=out/(name+'.ini');profile.write_text('schema = 1\ngame = snes\n'+extra)
        modes={}
        snapshots={}
        for mode in ('aot','lle'):
            folder=out/(name+'-'+mode);folder.mkdir(exist_ok=True)
            env=os.environ.copy();env['SNESRECOMP_CYC_WATCH']='C089B7-C08B22'
            env['TLK_WRAM_DIR']=str(folder)
            env['TLK_WRAM_DUMP']=','.join(map(str,range(4400,4901)))
            cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                 '--resource-profile',profile,'--frames','5400','--input-polled',tape,'--ram-log',folder/'route.ram']
            if mode=='lle':cmd.append('--lle')
            with (folder/'run.log').open('wb') as log:
                subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
            snapshots[mode]=[digest(folder/f'hl_wram_{f}.bin') for f in range(4400,4901)]
            modes[mode]={'guest':hashes(folder/'run.log'),'tracked_sha256':digest(folder/'route.ram')}
            if mode=='lle':
                deaths=parse(folder/'run.log')
                (folder/'phases.json').write_text(json.dumps(deaths,indent=2)+'\n')
        assert modes['aot']==modes['lle'],name
        assert snapshots['aot']==snapshots['lle'],('Per-field WRAM differs',name)
        for death in deaths:
            assert 4400<=death['health_death_entry']<death['completed_opcode_fields']['display_end'][0]<=4900
        if name=='native':
            original=json.loads((ROOT/'build/pride-death-timeline/native/report.json').read_text())
            assert original['headless_sha256']==identity
            assert modes['aot']['guest']==original['modes']['aot']['hashes']
            assert modes['aot']['tracked_sha256']==original['modes']['aot']['tracked_sha256']
        runs[name]={**modes['aot'],'deaths':deaths,'sampled_full_wram_equal_fields':501,
                    'sampled_wram_hashes':snapshots['lle']}
        print(name,'death phase observation and per-field AOT/LLE WRAM PASS',json.dumps([{k:v for k,v in d.items()
              if k!='completed_opcode_fields'} for d in deaths]),flush=True)
    assert digest(binary)==identity
    result={'result':'PASS','scope':__doc__,'headless_sha256':identity,'runs':runs,
            'loaded_states':False,'guest_edits':False,'production_death_source_enabled':False,
            'source_sha256':{'script':digest(Path(__file__)),'input':digest(tape)},
            'full_first_level_fidelity_complete':False}
    report_path.write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
