"""Cold-load before/after both arrival entries and during the original chime tail."""
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
from verify_windows import hashes,pixels


def main():
    base=ROOT/'build/pride-arrival-work/player';bp=base/'build-report.json';build=bound(bp)
    reference_path=base/'arrival-audio/report.json';reference=bound(reference_path);assert reference['result']=='PASS'
    out=base/'arrival-saves';out.mkdir();config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\naudio.effects.world.pickup_arrival = md\n')
    tape=ROOT/'engine/tapes/allbugsF.read.tape';clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    continuous=base/'arrival-audio/arrival-aot';whole=wav_data(continuous/'audio.wav');checks={};commands={}
    def run(label,mode,end,inputs,state=None,save=None):
        folder=out/label;folder.mkdir()
        env=dict(clean,TLK_PICKUP_ARRIVAL_TRACE=str(folder/'arrival.csv'))
        command=[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
            '--resource-profile',profile,'--config',config,'--input-polled',inputs,'--frames',end,
            '--no-pace','--no-audio','--no-record','--wav',folder/'audio.wav','--wav-seconds',60,
            '--dump-window',folder/'window.png']
        if mode=='lle':command+=['--lle']
        if state:command+=['--load',state]
        if save:command+=['--save-at',end,save]
        commands[label]=list(map(str,command))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(commands[label],env=env,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        events=list(csv.DictReader((folder/'arrival.csv').open())) if (folder/'arrival.csv').exists() else []
        return folder,wav_data(folder/'audio.wav'),sum(int(r['emitted']) for r in events)
    # Labels in the trace are the last completed audio field. Use clear margins
    # before/after the guest entry, plus a point inside its measured39-field tail.
    first=int(reference['arrival_events']['arrival-aot'][0]['last_audio_frame'])
    second=int(reference['arrival_events']['arrival-aot'][1]['last_audio_frame'])
    for point in (first-1,first+3,first+20,second-1,second+3):
        for saved_mode in ('aot','lle'):
            label=f'{point}-{saved_mode}';state=out/f'{label}.state'
            saved,prefix,emitted=run(label+'-save',saved_mode,point,tape,save=state)
            checks[label+'/prefix_pcm_exact']=whole[:len(prefix)]==prefix
            used=int(re.search(r'tape_words_used=(\d+)',(saved/'run.log').read_text()).group(1))
            suffix=out/f'{label}.polled.tape';suffix.write_bytes(tape.read_bytes()[used*2:])
            # Every completed run is terminal before lossless compression.
            subprocess.run(['compact.exe','/C','/F','/I','/Q','/EXE:LZX',str(state)],stdout=subprocess.DEVNULL,check=True)
            subprocess.run(['compact.exe','/C','/F','/S:'+str(saved),'/I','/Q','/EXE:LZX'],stdout=subprocess.DEVNULL,check=True)
            for loaded_mode in ('aot','lle'):
                folder,tail,count=run(label+'-load-'+loaded_mode,loaded_mode,2000,suffix,state=state)
                key=label+'/'+loaded_mode
                checks[key+'/complete_remaining_pcm']=tail==whole[len(prefix):]
                checks[key+'/guest_hashes']=hashes(folder/'run.log')==hashes(continuous/'run.log')
                checks[key+'/actual_client']=pixels(folder/'window.png')==pixels(continuous/'window.png')
                checks[key+'/no_lost_or_repeated_entry']=count==2-emitted
                subprocess.run(['compact.exe','/C','/F','/S:'+str(folder),'/I','/Q','/EXE:LZX'],stdout=subprocess.DEVNULL,check=True)
            print(label,'failed:',[k for k,v in checks.items() if not v],flush=True)
    paths=[Path(__file__),bp,reference_path,profile,tape]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        entry_relative_points=[first-1,first+3,first+20,second-1,second+3],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
        new_process_mode_combinations=20,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],len(checks),'save checks',flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
