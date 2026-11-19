"""Cold-load both ledge directions and the late-boss cue without event latches."""
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
    base=ROOT/'build/pride-ledge-work/player';bp=base/'build-report.json';bound(bp)
    reference_path=base/'ledge-audio/report.json';reference=bound(reference_path);assert reference['result']=='PASS'
    out=base/'ledge-saves';out.mkdir();config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\naudio.effects.simba.ledge_grab = md\n')
    tape=ROOT/'engine/tapes/allbugsF.read.tape';clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    control=base/'ledge-audio/ledge-aot';whole=wav_data(control/'audio.wav');checks={};commands={}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
    expected_rows=rows(control)
    events=reference['ledge_events']['ledge-aot'];first=int(events[0]['last_audio_frame'])
    opposite=int(events[1]['last_audio_frame']);boss=int(events[-1]['last_audio_frame'])
    points=(first-1,first+3,first+6,opposite-1,opposite+3,boss+6)
    def run(label,mode,end,inputs,state=None,save=None):
        folder=out/label;folder.mkdir();env=dict(clean,TLK_LEDGE_GRAB_TRACE=str(folder/'ledge.csv'))
        command=list(map(str,[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc',
            '--md-rom',ROOT/'Lion King, The (World).md','--config',config,'--resource-profile',profile,
            '--input-polled',inputs,'--frames',end,'--no-pace','--no-audio','--no-record',
            '--hash-at',','.join(map(str,range(1,4501))),'--wav',folder/'audio.wav','--wav-seconds',100,
            '--dump-window',folder/'window.png']))
        if mode=='lle':command+=['--lle']
        if state:command+=['--load',str(state)]
        if save:command+=['--save-at',str(end),str(save)]
        commands[label]=command
        with (folder/'run.log').open('wb') as log:
            subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        calls=list(csv.DictReader((folder/'ledge.csv').open())) if (folder/'ledge.csv').exists() else []
        return folder,wav_data(folder/'audio.wav'),sum(int(r['emitted']) for r in calls)
    for point in points:
        for saved_mode in ('aot','lle'):
            label=f'{point}-{saved_mode}';state=out/f'{label}.state'
            saved,prefix,count=run(label+'-save',saved_mode,point,tape,save=state)
            checks[label+'/prefix_entire_pcm']=whole[:len(prefix)]==prefix
            checks[label+'/prefix_every_guest_field']=rows(saved)==expected_rows[:point]
            used=int(re.search(r'tape_words_used=(\d+)',(saved/'run.log').read_text()).group(1))
            suffix=out/f'{label}.polled.tape';suffix.write_bytes(tape.read_bytes()[used*2:])
            for mode in ('aot','lle'):
                folder,tail,remaining=run(label+'-load-'+mode,mode,4500,suffix,state=state)
                key=label+'/'+mode
                checks[key+'/whole_remaining_pcm']=tail==whole[len(prefix):]
                checks[key+'/every_remaining_guest_field']=rows(folder)==expected_rows[point:]
                checks[key+'/actual_client']=pixels(folder/'window.png')==pixels(control/'window.png')
                checks[key+'/no_lost_or_repeated_entries']=remaining==5-count
            print(label,'failed',[k for k,v in checks.items() if not v],flush=True)
    paths=[Path(__file__),bp,reference_path,profile,tape]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        save_fields=list(points),new_process_mode_combinations=24,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
        full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'cold save checks',flush=True);assert all(checks.values())


if __name__=='__main__':main()
