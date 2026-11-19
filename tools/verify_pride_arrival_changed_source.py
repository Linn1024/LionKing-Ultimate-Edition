"""Changing arrival audio on cold load must drop the foreign MD tail cleanly."""
import csv
import json
import os
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_windows import hashes,pixels


def main():
    base=ROOT/'build/pride-arrival-work/player';bp=base/'build-report.json';build=bound(bp)
    saves_path=base/'arrival-saves/report.json';assert bound(saves_path)['result']=='PASS'
    reference_path=base/'arrival-audio/report.json';assert bound(reference_path)['result']=='PASS'
    assert digest(base/'player.exe')==build['binary_sha256']
    out=base/'arrival-changed-source';out.mkdir()
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
    reference=base/'arrival-audio/native-aot';native=wav_data(reference/'audio.wav')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    checks={};commands={};sources=[Path(__file__),bp,saves_path,reference_path,profile]
    for saved_mode in ('aot','lle'):
        stem='1676-'+saved_mode;state=base/'arrival-saves'/f'{stem}.state'
        suffix=base/'arrival-saves'/f'{stem}.polled.tape'
        prefix=wav_data(base/'arrival-saves'/f'{stem}-save/audio.wav')
        sources += [state,suffix]
        for mode in ('aot','lle'):
            label=saved_mode+'-to-'+mode;folder=out/label;folder.mkdir()
            env=dict(clean,TLK_PICKUP_ARRIVAL_TRACE=str(folder/'arrival.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'))
            command=list(map(str,[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc',
                '--md-rom',ROOT/'Lion King, The (World).md','--config',config,'--resource-profile',profile,
                '--input-polled',suffix,'--load',state,'--frames',2000,'--no-pace','--no-audio','--no-record',
                '--wav',folder/'audio.wav','--wav-seconds',60,'--dump-window',folder/'window.png']))
            if mode=='lle':command+=['--lle']
            commands[label]=command
            with (folder/'run.log').open('wb') as log:
                subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
            entries=list(csv.DictReader((folder/'arrival.csv').open()))
            driver=list(csv.DictReader((folder/'driver.csv').open()))
            checks[label+'/remaining_native_pcm_exact']=wav_data(folder/'audio.wav')==native[len(prefix):]
            checks[label+'/native_guest_exact']=hashes(folder/'run.log')==hashes(reference/'run.log')
            checks[label+'/actual_client_exact']=pixels(folder/'window.png')==pixels(reference/'window.png')
            checks[label+'/remaining_entry_native']=len(entries)==1 and entries[0]['emitted']=='0'
            checks[label+'/no_foreign_fm112']=not any(r['selector']=='2' and r['value']=='112' for r in driver)
            print(label,'failed',[k for k,v in checks.items() if not v],flush=True)
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in sources},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
        changed_audio_profile_drops_foreign_tail=True if all(checks.values()) else False,
        full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'changed-source checks',flush=True);assert all(checks.values())


if __name__=='__main__':main()
