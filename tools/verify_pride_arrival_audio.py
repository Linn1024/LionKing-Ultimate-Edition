"""Verify independent collection/arrival sounds and complete native control."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-arrival-work/player';bp=base/'build-report.json';build=bound(bp)
    assert digest(base/'player.exe')==build['binary_sha256']
    out=base/'arrival-audio';out.mkdir();config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    choices={'native':'','arrival':'audio.effects.world.pickup_arrival = md\n',
        'collection':'audio.effects.world.life_bug = md\n',
        'both':'audio.effects.world.life_bug = md\naudio.effects.world.pickup_arrival = md\n',
        'unrelated':'audio.effects.world.hyena_hurt = md\n'}
    profiles={}
    for name,text in choices.items():
        profiles[name]=out/f'{name}.ini';profiles[name].write_text('schema = 1\ngame = snes\n'+text)
    tape=ROOT/'engine/tapes/allbugsF.read.tape'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    commands={};checks={};runs={}
    for mode in ('aot','lle'):
        for name in choices:
            label=f'{name}-{mode}';folder=out/label;folder.mkdir()
            env=dict(clean,TLK_PICKUP_ARRIVAL_TRACE=str(folder/'arrival.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'))
            command=[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                '--resource-profile',profiles[name],'--config',config,'--input-polled',tape,'--frames',2000,
                '--no-pace','--no-audio','--no-record','--hash-at',','.join(map(str,range(1,2001))),
                '--wav',folder/'audio.wav','--wav-seconds',60,'--dump-window',folder/'window.png']
            if mode=='lle':command+=['--lle']
            commands[label]=list(map(str,command))
            with (folder/'run.log').open('wb') as log:
                subprocess.run(commands[label],env=env,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
            rows=re.findall(pattern,(folder/'run.log').read_text())
            arrivals=list(csv.DictReader((folder/'arrival.csv').open()))
            emitted=sum(int(r['emitted']) for r in arrivals)
            driver=list(csv.DictReader((folder/'driver.csv').open()))
            fm112=[r for r in driver if r['selector']=='2' and r['value']=='112']
            expected_arrivals=2 if name in ('arrival','both') else 0
            expected_fm=expected_arrivals+(2 if name in ('collection','both') else 0)
            checks[label+'/all_fields']=len(rows)==2000
            checks[label+'/two_original_initializations']=len(arrivals)==2 and all(r['timer']=='36' for r in arrivals)
            checks[label+'/source_specific_emission']=emitted==expected_arrivals and len(fm112)==expected_fm
            runs[label]=dict(rows=rows,arrivals=arrivals,driver=driver,pcm=wav_data(folder/'audio.wav'),pixels=pixels(folder/'window.png'))
            print(label,'arrivals',emitted,'FM112',len(fm112),flush=True)
    for name in choices:
        a,b=runs[name+'-aot'],runs[name+'-lle']
        checks[name+'/aot_lle_all_fields']=a['rows']==b['rows']
        checks[name+'/aot_lle_entire_pcm']=a['pcm']==b['pcm']
        checks[name+'/aot_lle_entire_client']=a['pixels']==b['pixels']
    for mode in ('aot','lle'):
        native=runs['native-'+mode];arrival=runs['arrival-'+mode];collection=runs['collection-'+mode];both=runs['both-'+mode]
        checks[mode+'/arrival_preserves_every_native_guest_field']=native['rows']==arrival['rows']
        checks[mode+'/arrival_preserves_collection_guest_fields']=collection['rows']==both['rows']
        checks[mode+'/all_sound_choices_preserve_client']=all(runs[name+'-'+mode]['pixels']==native['pixels'] for name in choices)
        checks[mode+'/arrival_audible']=arrival['pcm']!=native['pcm'] and both['pcm']!=collection['pcm']
        checks[mode+'/unrelated_choice_preserves_pcm']=runs['unrelated-'+mode]['pcm']==native['pcm']
    # Direct previous-player native control, with the same normal power-on tape.
    folder=out/'previous-native';folder.mkdir();command=list(commands['native-aot']);command[0]=str(ROOT/'build/pride-flight-player/player.exe')
    for flag,name in (('--wav','audio.wav'),('--dump-window','window.png')):command[command.index(flag)+1]=str(folder/name)
    commands['previous-native']=command
    with (folder/'run.log').open('wb') as log:
        subprocess.run(command,env=clean,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
    checks['previous_native_all_guest_fields']=re.findall(pattern,(folder/'run.log').read_text())==runs['native-aot']['rows']
    checks['previous_native_entire_pcm']=wav_data(folder/'audio.wav')==runs['native-aot']['pcm']
    checks['previous_native_entire_client']=pixels(folder/'window.png')==runs['native-aot']['pixels']
    paths=[Path(__file__),bp,tape,ROOT/'engine/runner/tlk_pickup_audio.c',ROOT/'engine/runner/tlk_audio.c',
        ROOT/'engine/runner/tlk_resources.c',ROOT/'build/pride-flight-player/player.exe',ROOT/'build/pride-arrival-tail/report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        arrival_events={name:r['arrivals'] for name,r in runs.items()},compared_fields=10000,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
        cold_saves_and_pause_verified=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'checks',flush=True);assert all(checks.values())


if __name__=='__main__':main()
