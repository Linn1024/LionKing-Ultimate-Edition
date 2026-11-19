"""Exercise launch cues with MD music and sibling effects on a complete route."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_bounce_owner_history import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    public=ROOT/'build/pride-lizard-launch-work/player';base=ROOT/'build/pride-bounce-owner-work/player';bp=base/'build-report.json';build=bound(bp)
    assert digest(base/'player.exe')==build['binary_sha256']
    route=public/'launch-route/report.json';assert bound(route)['result']=='PASS'
    out=base/'bounce-music-mix';out.mkdir();config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    siblings=['audio.music.pride_lands','audio.effects.world.lizard_launch',
        'audio.effects.simba.ledge_grab','audio.effects.world.leaves',
        'audio.effects.world.pickup_arrival','audio.effects.world.defeat_puff']
    tape=ROOT/'engine/tapes/allbugsF.read.tape'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    commands={};checks={};runs={}
    for mode in ('aot','lle'):
        for name in ('siblings','bounce'):
            label=name+'-'+mode;folder=out/label;folder.mkdir();profile=folder/'resources.ini'
            ids=siblings+(['audio.effects.simba.bounce'] if name=='bounce' else [])
            profile.write_text('schema = 1\ngame = snes\n'+''.join(node+' = md\n' for node in ids))
            env=dict(clean,TLK_LIZARD_LAUNCH_TRACE=str(folder/'launch.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'))
            command=list(map(str,[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc',
                '--md-rom',ROOT/'Lion King, The (World).md','--config',config,'--resource-profile',profile,
                '--input-polled',tape,'--frames',5000,'--no-pace','--no-audio','--no-record',
                '--hash-at',','.join(map(str,range(1,5001))),'--wav',folder/'audio.wav','--wav-seconds',100,
                '--dump-window',folder/'window.png','--dump-scene',folder/'scene.json']))
            if mode=='lle':command+=['--lle']
            commands[label]=command
            with (folder/'run.log').open('wb') as log:
                subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=350)
            rows=re.findall(pattern,(folder/'run.log').read_text())
            with (folder/'launch.csv').open() as stream:events=list(csv.DictReader(stream))
            with (folder/'driver.csv').open() as stream:driver=list(csv.DictReader(stream))
            checks[label+'/all_fields']=len(rows)==5000
            checks[label+'/two_launches']=len(events)==2 and all(r['timer']=='20' for r in events)
            checks[label+'/source_specific_entries']=sum(int(r['emitted']) for r in events)==2
            checks[label+'/pride_and_boss_music']={137,134}<=set(int(r['value']) for r in driver if r['selector']=='1')
            checks[label+'/next_main_level']=json.loads((folder/'scene.json').read_text())['level']==1
            count=sum(r['selector']=='2' and r['value']=='123' for r in driver)
            runs[label]=dict(rows=rows,events=events,pcm=wav_data(folder/'audio.wav'),client=pixels(folder/'window.png'),fm123=count)
            print(label,'launches',events,'FM123',count,flush=True)
    for mode in ('aot','lle'):
        a,b=runs['siblings-'+mode],runs['bounce-'+mode]
        checks[mode+'/every_sibling_guest_field_preserved']=a['rows']==b['rows']
        checks[mode+'/sibling_client_preserved']=a['client']==b['client']
        checks[mode+'/six_additional_fm123']=b['fm123']==a['fm123']+6
        checks[mode+'/audible_with_music']=a['pcm']!=b['pcm']
    for name in ('siblings','bounce'):
        a,b=runs[name+'-aot'],runs[name+'-lle']
        checks[name+'/every_mode_guest_field']=a['rows']==b['rows']
        checks[name+'/whole_mode_pcm']=a['pcm']==b['pcm']
        checks[name+'/actual_mode_client']=a['client']==b['client']
    paths=[Path(__file__),bp,route,tape]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        launch_events={n:r['events'] for n,r in runs.items()},fm123_counts={n:r['fm123'] for n,r in runs.items()},
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
        maintained_bounce_candidate=True,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'music/source combination checks',flush=True);assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
