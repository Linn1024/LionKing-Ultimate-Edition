"""Play an ordinary complete route that actually uses both arrival cues."""
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
    basic_path=base/'arrival-audio/report.json';assert bound(basic_path)['result']=='PASS'
    out=base/'arrival-route';out.mkdir();config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    tape=ROOT/'engine/tapes/allbugsF.read.tape';checks={};commands={};runs={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    for label,selected,mode in (('native',False,'aot'),('arrival-aot',True,'aot'),('arrival-lle',True,'lle')):
        folder=out/label;folder.mkdir();profile=folder/'resources.ini'
        profile.write_text('schema = 1\ngame = snes\n'+('audio.effects.world.pickup_arrival = md\n' if selected else ''))
        env=dict(clean,TLK_PICKUP_ARRIVAL_TRACE=str(folder/'arrival.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'))
        command=list(map(str,[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc',
            '--md-rom',ROOT/'Lion King, The (World).md','--config',config,'--resource-profile',profile,
            '--input-polled',tape,'--frames',5000,'--no-pace','--no-audio','--no-record',
            '--hash-at',','.join(map(str,range(1,5001))),'--wav',folder/'audio.wav','--wav-seconds',100,
            '--dump-scene',folder/'scene.json','--dump-window',folder/'window.png']))
        if mode=='lle':command+=['--lle']
        commands[label]=command
        with (folder/'run.log').open('wb') as log:
            subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        rows=re.findall(pattern,(folder/'run.log').read_text());events=list(csv.DictReader((folder/'arrival.csv').open()))
        driver=list(csv.DictReader((folder/'driver.csv').open()))
        fm=[r for r in driver if r['selector']=='2' and r['value']=='112']
        checks[label+'/all_fields']=len(rows)==5000
        checks[label+'/two_original_entries']=len(events)==2 and all(r['timer']=='36' for r in events)
        checks[label+'/source_specific_commands']=sum(int(r['emitted']) for r in events)==(2 if selected else 0) and len(fm)==(2 if selected else 0)
        checks[label+'/next_main_level']=json.loads((folder/'scene.json').read_text())['level']==1
        runs[label]=dict(rows=rows,pcm=wav_data(folder/'audio.wav'),pixels=pixels(folder/'window.png'))
        print(label,'next main level reached; arrival commands',len(fm),flush=True)
    native=runs['native'];a,b=runs['arrival-aot'],runs['arrival-lle']
    checks['all_aot_lle_guest_fields']=a['rows']==b['rows']
    checks['all_native_guest_fields_preserved']=native['rows']==a['rows']
    checks['entire_aot_lle_pcm']=a['pcm']==b['pcm']
    checks['entire_actual_clients']=native['pixels']==a['pixels']==b['pixels']
    checks['arrival_is_audible']=native['pcm']!=a['pcm']
    basic=wav_data(base/'arrival-audio/native-aot/audio.wav');cut=len(basic)
    checks['native_prefix_matches_basic']=native['pcm'][:cut]==basic
    checks['entire_audio_after_first_2000_fields_native']=native['pcm'][cut:]==a['pcm'][cut:]==b['pcm'][cut:]
    paths=[Path(__file__),bp,basic_path,tape]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        compared_route_fields=5000,native_comparison_fields=5000,ordinary_poweron_no_guest_edits=True,
        both_cues_exercised_before_next_main_level=True,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
        full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'audible complete-route checks',flush=True);assert all(checks.values())


if __name__=='__main__':main()
