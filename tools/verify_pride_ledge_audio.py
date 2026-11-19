"""Keep ledge/leaf/arrival sounds independent through both ledge directions."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_ledge_history import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-ledge-work/player';bp=base/'build-report.json';build=bound(bp)
    assert digest(base/'player.exe')==build['binary_sha256']
    evidence_path=ROOT/'build/pride-ledge-lifetimes/report.json';evidence=bound(evidence_path)
    expected=[(int(r['entry']['field'])-1,r['entry']['entry'],r['entry']['tag']) for r in evidence['all_native_contact_intervals']]
    assert len(expected)==5
    out=base/'ledge-audio';out.mkdir();config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    profiles={};choices={'native':'','ledge':'audio.effects.simba.ledge_grab = md\n',
        'leaves':'audio.effects.world.leaves = md\n',
        'both':'audio.effects.simba.ledge_grab = md\naudio.effects.world.leaves = md\n',
        'arrival':'audio.effects.world.pickup_arrival = md\n'}
    for name,text in choices.items():
        profiles[name]=out/f'{name}.ini';profiles[name].write_text('schema = 1\ngame = snes\n'+text)
    tape=ROOT/'engine/tapes/allbugsF.read.tape';clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    commands={};checks={};runs={};pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    for mode in ('aot','lle'):
        for name in choices:
            label=name+'-'+mode;folder=out/label;folder.mkdir()
            env=dict(clean,TLK_LEDGE_GRAB_TRACE=str(folder/'ledge.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'))
            command=list(map(str,[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc',
                '--md-rom',ROOT/'Lion King, The (World).md','--config',config,'--resource-profile',profiles[name],
                '--input-polled',tape,'--frames',4500,'--no-pace','--no-audio','--no-record',
                '--hash-at',','.join(map(str,range(1,4501))),'--wav',folder/'audio.wav','--wav-seconds',100,
                '--dump-window',folder/'window.png']))
            if mode=='lle':command+=['--lle']
            commands[label]=command
            with (folder/'run.log').open('wb') as log:
                subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
            events=list(csv.DictReader((folder/'ledge.csv').open())) if (folder/'ledge.csv').exists() else []
            driver=list(csv.DictReader((folder/'driver.csv').open()))
            fm94=[r for r in driver if r['selector']=='2' and r['value']=='94']
            rows=re.findall(pattern,(folder/'run.log').read_text())
            checks[label+'/all_fields']=len(rows)==4500
            checks[label+'/five_original_contact_entries']=[(int(r['last_audio_frame']),r['entry'],r['tag']) for r in events]==expected
            checks[label+'/source_specific_emission']=sum(int(r['emitted']) for r in events)==(5 if name in ('ledge','both') else 0)
            runs[label]=dict(rows=rows,events=events,driver=driver,fm94=len(fm94),pcm=wav_data(folder/'audio.wav'),client=pixels(folder/'window.png'))
            print(label,'ledge entries',len(events),'FM94',len(fm94),flush=True)
    for name in choices:
        a,b=runs[name+'-aot'],runs[name+'-lle']
        checks[name+'/every_aot_lle_guest_field']=a['rows']==b['rows']
        checks[name+'/whole_aot_lle_pcm']=a['pcm']==b['pcm']
        checks[name+'/whole_aot_lle_client']=a['client']==b['client']
    for mode in ('aot','lle'):
        native,ledge,leaves,both,arrival=[runs[n+'-'+mode] for n in choices]
        checks[mode+'/ledge_preserves_native_guest']=ledge['rows']==native['rows']
        checks[mode+'/ledge_preserves_leaf_guest']=both['rows']==leaves['rows']
        checks[mode+'/ledge_and_native_client']=ledge['client']==native['client']
        checks[mode+'/mixed_and_leaf_client']=both['client']==leaves['client']
        checks[mode+'/isolated_ledge_commands']=native['fm94']==arrival['fm94']==0 and ledge['fm94']==5
        checks[mode+'/independent_leaf_commands']=leaves['fm94']>0 and both['fm94']==leaves['fm94']+5
        checks[mode+'/ledge_audible']=ledge['pcm']!=native['pcm'] and both['pcm']!=leaves['pcm']
    # Exact preceding-player native control, including its complete PCM/window.
    previous=out/'previous-native';previous.mkdir();command=list(commands['native-aot'])
    command[0]=str(ROOT/'build/pride-arrival-work/player/player.exe')
    for flag,name in (('--wav','audio.wav'),('--dump-window','window.png')):command[command.index(flag)+1]=str(previous/name)
    commands['previous-native']=command
    with (previous/'run.log').open('wb') as log:
        subprocess.run(command,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
    checks['previous_native_every_guest_field']=re.findall(pattern,(previous/'run.log').read_text())==runs['native-aot']['rows']
    checks['previous_native_entire_pcm']=wav_data(previous/'audio.wav')==runs['native-aot']['pcm']
    checks['previous_native_entire_client']=pixels(previous/'window.png')==runs['native-aot']['client']
    paths=[Path(__file__),bp,evidence_path,tape,ROOT/'engine/runner/tlk_ledge_audio.c',ROOT/'build/pride-arrival-work/player/player.exe']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        ledge_events={name:r['events'] for name,r in runs.items()},fm94_counts={name:r['fm94'] for name,r in runs.items()},
        compared_profile_mode_fields=22500,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
        cold_saves_and_pause_verified=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'source/native-control checks',flush=True);assert all(checks.values())


if __name__=='__main__':main()
