"""New-process loads at pre-key-on, audible tail and boss-bank boundaries."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_lizard_launch_preview_history import bound
from verify_pride_audio_state import wav_data,audio_offset
from verify_windows import pixels


def main():
    public=ROOT/'build/pride-lizard-launch-work/player'
    base=public/'bounce-semantic-save-prototype'
    bp=base/'build-report.json';build=bound(bp)
    assert digest(base/'player.exe')==build['binary_sha256']
    rp=public/'bounce-semantic-prototype4/verification/report.json';assert bound(rp)['result']=='PASS'
    out=base/'saves';out.mkdir();checks={};commands={};states=[]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    tape=ROOT/'engine/tapes/allbugsF.read.tape'
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    def run(label,name,mode,end,inputs,state=None,save=None):
        folder=out/label;folder.mkdir()
        env=dict(clean,TLK_SEMANTIC_OWNER_TRACE=str(folder/'ownership.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'))
        command=list(map(str,[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc',
            '--md-rom',ROOT/'Lion King, The (World).md','--config',public/'launch-audio/host.ini',
            '--resource-profile',public/f'launch-audio/{name}.ini','--input-polled',inputs,
            '--frames',end,'--no-pace','--no-audio','--no-record',
            '--hash-at',','.join(map(str,range(1,4501))),'--wav',folder/'audio.wav','--wav-seconds',100,
            '--dump-window',folder/'window.png']))
        if mode=='lle':command+=['--lle']
        if state:command+=['--load',str(state)]
        if save:command+=['--save-at',str(end),str(save)]
        commands[label]=command
        with (folder/'run.log').open('wb') as log:
            subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=400)
        rows=re.findall(pattern,(folder/'run.log').read_text())
        return folder,rows,wav_data(folder/'audio.wav')
    # Two adjacent early fields distinguish assignment from actual DSP key-on.
    cases=(('bounce','aot',1399),('bounce','aot',1400),('bounce','lle',3982),('native','aot',1400))
    for name,saved_mode,point in cases:
        label=f'{name}-{saved_mode}-{point}'
        control=public/f'bounce-semantic-prototype4/verification/{name}-aot'
        expected=re.findall(pattern,(control/'run.log').read_text());whole=wav_data(control/'audio.wav')
        state=out/(label+'.state')
        folder,rows,prefix=run(label+'-save',name,saved_mode,point,tape,save=state)
        checks[label+'/prefix_every_guest_field']=rows==expected[:point]
        checks[label+'/prefix_entire_pcm']=prefix==whole[:len(prefix)]
        raw=state.read_bytes();at=audio_offset(raw)
        checks[label+'/versioned_native_ownership']=raw[at:at+8]==b'TLKSEM01'
        states.append(dict(profile=name,mode=saved_mode,field=point,path=state.relative_to(ROOT).as_posix()))
        used=int(re.search(r'tape_words_used=(\d+)',(folder/'run.log').read_text()).group(1))
        suffix=out/(label+'.polled.tape');suffix.write_bytes(tape.read_bytes()[used*2:])
        for mode in ('aot','lle'):
            key=label+'-load-'+mode
            loaded,tail_rows,tail=run(key,name,mode,4500,suffix,state=state)
            checks[key+'/every_remaining_guest_field']=tail_rows==expected[point:]
            checks[key+'/whole_remaining_pcm']=tail==whole[len(prefix):]
            checks[key+'/actual_client']=pixels(loaded/'window.png')==pixels(control/'window.png')
        print(label,'failed',[k for k,v in checks.items() if not v],flush=True)
    sources=[Path(__file__),bp,rp,tape]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,states=states,
        new_process_load_combinations=8,prototype_only=True,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in sources},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'save checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
