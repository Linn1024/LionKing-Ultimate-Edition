"""Load an actual preceding-build native save with the new lizard-launch sound selected."""
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
    base=ROOT/'build/pride-lizard-launch-work/player';bp=base/'build-report.json';build=bound(bp)
    rp=base/'launch-audio-baselines/report.json';assert bound(rp)['result']=='PASS'
    old=ROOT/'build/pride-ledge-work/player/player.exe'
    archive_path=ROOT/'build/pride-lizard-launch-baseline/report.json';archive=bound(archive_path)
    assert digest(old)==archive['preview_player_sha256']
    assert digest(base/'player.exe')==build['binary_sha256']
    out=base/'previous-native-save';out.mkdir();config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    native_profile=out/'native.ini';native_profile.write_text('schema = 1\ngame = snes\n')
    selected_profile=out/'ledge.ini';selected_profile.write_text('schema = 1\ngame = snes\naudio.effects.world.lizard_launch = md\n')
    control=base/'launch-audio/launch-aot';whole=wav_data(control/'audio.wav')
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows=lambda p:re.findall(pattern,p.read_text())
    reference=rows(control/'run.log');tape=ROOT/'engine/tapes/allbugsF.read.tape';state=out/'old-native.state'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))};commands={};checks={}
    def run(label,binary,profile,end,inputs,load=None,save=None):
        folder=out/label;folder.mkdir();env=dict(clean,TLK_LIZARD_LAUNCH_TRACE=str(folder/'launch.csv'))
        command=list(map(str,[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
            '--config',config,'--resource-profile',profile,'--input-polled',inputs,'--frames',end,
            '--no-pace','--no-audio','--no-record','--hash-at',','.join(map(str,range(1,4501))),
            '--wav',folder/'audio.wav','--wav-seconds',100,'--dump-window',folder/'window.png']))
        if label=='lle':command+=['--lle']
        if load:command+=['--load',str(load)]
        if save:command+=['--save-at',str(end),str(save)]
        commands[label]=command
        with (folder/'run.log').open('wb') as log:
            subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        return folder
    author=run('old-author',old,native_profile,2219,tape,save=state);prefix=wav_data(author/'audio.wav')
    checks['old_native_prefix_pcm']=prefix==whole[:len(prefix)]
    checks['old_native_prefix_every_guest_field']=rows(author/'run.log')==reference[:2219]
    used=int(re.search(r'tape_words_used=(\d+)',(author/'run.log').read_text()).group(1))
    suffix=out/'suffix.polled.tape';suffix.write_bytes(tape.read_bytes()[used*2:])
    for mode in ('aot','lle'):
        folder=run(mode,base/'player.exe',selected_profile,4500,suffix,load=state)
        events=list(csv.DictReader((folder/'launch.csv').open()))
        checks[mode+'/whole_remaining_pcm']=wav_data(folder/'audio.wav')==whole[len(prefix):]
        checks[mode+'/every_remaining_guest_field']=rows(folder/'run.log')==reference[2219:]
        checks[mode+'/actual_client']=pixels(folder/'window.png')==pixels(control/'window.png')
        checks[mode+'/both_future_cues']=len(events)==2 and all(r['emitted']=='1' for r in events)
        print(mode,'failed',[k for k,v in checks.items() if not v],flush=True)
    paths=[Path(__file__),bp,rp,archive_path,old,tape,state,suffix,native_profile,selected_profile]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        actual_preceding_build_native_state=True,remaining_guest_fields_per_mode=2281,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
        full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'preceding-build save checks',flush=True);assert all(checks.values())


if __name__=='__main__':main()
