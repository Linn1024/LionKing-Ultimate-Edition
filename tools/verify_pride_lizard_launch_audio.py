"""Separate lizard launches, player bounce and defeat puffs on an ordinary route."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_lizard_launch_history import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-lizard-launch-work/player';bp=base/'build-report.json'
    build=bound(bp);assert digest(base/'player.exe')==build['binary_sha256']
    evidence_path=ROOT/'build/pride-lizard-launch-audio/report.json';evidence=bound(evidence_path)
    assert evidence['result']=='ORIGINAL_LIZARD_LAUNCH_SOUND_DIFFERENCE_VERIFIED'
    out=base/'launch-audio';out.mkdir();config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    choices={'native':[], 'launch':['world.lizard_launch'], 'bounce':['simba.bounce'],
        'both':['world.lizard_launch','simba.bounce'], 'puff':['world.defeat_puff']}
    profiles={}
    for name,leaves in choices.items():
        profiles[name]=out/f'{name}.ini'
        profiles[name].write_text('schema = 1\ngame = snes\n'+''.join(f'audio.effects.{leaf} = md\n' for leaf in leaves))
    tape=ROOT/'engine/tapes/allbugsF.read.tape'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    commands={};checks={};runs={};pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    for mode in ('aot','lle'):
        for name in choices:
            label=name+'-'+mode;folder=out/label;folder.mkdir()
            env=dict(clean,TLK_LIZARD_LAUNCH_TRACE=str(folder/'launch.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'))
            command=list(map(str,[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc',
                '--md-rom',ROOT/'Lion King, The (World).md','--config',config,'--resource-profile',profiles[name],
                '--input-polled',tape,'--frames',4500,'--no-pace','--no-audio','--no-record',
                '--hash-at',','.join(map(str,range(1,4501))),'--wav',folder/'audio.wav','--wav-seconds',100,
                '--dump-window',folder/'window.png']))
            if mode=='lle':command+=['--lle']
            commands[label]=command
            with (folder/'run.log').open('wb') as log:
                subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
            events=list(csv.DictReader((folder/'launch.csv').open())) if (folder/'launch.csv').exists() else []
            driver=list(csv.DictReader((folder/'driver.csv').open()))
            counts={value:sum(r['selector']=='2' and r['value']==str(value) for r in driver) for value in (123,165)}
            rows=re.findall(pattern,(folder/'run.log').read_text())
            checks[label+'/all_fields']=len(rows)==4500
            # Sparse original observations bound the entry within each preceding
            # four-field interval; do not invent exact entry times from samples.
            checks[label+'/two_original_lifetimes']=len(events)==2 and all(
                int(interval['first_sample']['field'])-5<=int(event['last_audio_frame'])<=int(interval['first_sample']['field'])
                and event['actor']==interval['first_sample']['actor'] and event['timer']=='20'
                for event,interval in zip(events,evidence['native_intervals']))
            checks[label+'/source_emission']=sum(int(r['emitted']) for r in events)==(2 if name in ('launch','both') else 0)
            runs[label]=dict(rows=rows,events=events,counts=counts,pcm=wav_data(folder/'audio.wav'),client=pixels(folder/'window.png'))
            print(label,'events',events,'FM counts',counts,flush=True)
    for name in choices:
        a,b=runs[name+'-aot'],runs[name+'-lle']
        checks[name+'/every_guest_field']=a['rows']==b['rows']
        checks[name+'/whole_pcm']=a['pcm']==b['pcm']
        checks[name+'/actual_client']=a['client']==b['client']
    for mode in ('aot','lle'):
        native,launch,bounce,both,puff=[runs[n+'-'+mode] for n in choices]
        for name in choices:
            checks[mode+'/'+name+'/native_guest']=runs[name+'-'+mode]['rows']==native['rows']
            checks[mode+'/'+name+'/native_client']=runs[name+'-'+mode]['client']==native['client']
        checks[mode+'/independent_launch']=native['counts'][123]==puff['counts'][123]==0 and launch['counts'][123]==2
        checks[mode+'/independent_bounce']=bounce['counts'][123]>0 and both['counts'][123]==bounce['counts'][123]+2
        checks[mode+'/independent_puff']=puff['counts'][165]>0 and all(r['counts'][165]==0 for r in (native,launch,bounce,both))
        checks[mode+'/audible']=launch['pcm']!=native['pcm'] and both['pcm']!=bounce['pcm']
    previous=out/'previous-native';previous.mkdir();command=list(commands['native-aot'])
    command[0]=str(ROOT/'build/pride-ledge-work/player/player.exe')
    for flag,name in (('--wav','audio.wav'),('--dump-window','window.png')):command[command.index(flag)+1]=str(previous/name)
    commands['previous-native']=command
    with (previous/'run.log').open('wb') as log:
        subprocess.run(command,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
    checks['previous_native_every_field']=re.findall(pattern,(previous/'run.log').read_text())==runs['native-aot']['rows']
    checks['previous_native_pcm']=wav_data(previous/'audio.wav')==runs['native-aot']['pcm']
    checks['previous_native_client']=pixels(previous/'window.png')==runs['native-aot']['client']
    paths=[Path(__file__),bp,evidence_path,tape,ROOT/'engine/runner/tlk_lizard_audio.c',ROOT/'build/pride-ledge-work/player/player.exe']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        events={n:r['events'] for n,r in runs.items()},command_counts={n:r['counts'] for n,r in runs.items()},
        compared_profile_mode_fields=22500,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
        cold_saves_and_pause_verified=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'checks',flush=True);assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
