"""Verify dry music removal and native gameplay on the current Difficult route."""
from concurrent.futures import ThreadPoolExecutor
import csv
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-music-output61';bp=base/'build-report.json';build=bound(bp)
    source=ROOT/'build/pride-music-transport59/verification/report.json';prior=bound(source)
    assert prior['result']=='PASS';out=base/'verification';out.mkdir();checks={};commands={};observations={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    def run(name):
        folder=out/name;folder.mkdir();cmd=prior['commands'][name].copy();cmd[0]=str(base/'player.exe')
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            (folder/file).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/file)
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        commands[name]=cmd
        env=dict(clean,TLK_MUSIC_OUTPUT_STATS=str(folder/'output.csv'),TLK_MUSIC_OWNER_TRACE=str(folder/'owner.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'))
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        print(name,'exit',rc,flush=True);return name,(folder,rc)
    cases=[choice+'-'+mode for choice in ('native','music') for mode in ('aot','lle')]
    with ThreadPoolExecutor(max_workers=3) as pool:runs=dict(pool.map(run,cases))
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    def hashes(folder):return re.findall(pattern,(folder/'run.log').read_text())
    reference=hashes(source.parent/'public-native')
    for name,(folder,rc) in runs.items():
        selected=name.startswith('music');dual=source.parent/name
        checks[name+'_exit']=rc==0
        checks[name+'_all4600_picture_full_wram_native']=len(hashes(folder))==4600 and hashes(folder)==reference
        for file in ('scene.json','window.png'):checks[name+'_'+file+'_native']=digest(folder/file)==digest(dual/file)
        checks[name+'_pcm_choice']=((digest(folder/'audio.wav')!=digest(dual/'audio.wav')) if selected else (digest(folder/'audio.wav')==digest(dual/'audio.wav')))
        rows=[{k:int(v) for k,v in r.items()} for r in csv.DictReader((folder/'output.csv').open())]
        totals={key:sum(r[key] for r in rows) for key in rows[0] if key!='field'}
        checks[name+'_no_unhandled_echo_samples']=totals['echo_blocked']==0
        checks[name+'_all_audible_voices_classified']=totals['unknown']==0
        checks[name+'_actual_music_and_fx_samples']=totals['audible_music']>0 and totals['audible_fx']>0
        checks[name+'_selected_music_filter_used']=totals['muted']>0 if selected else totals['muted']==0
        observations[name]=dict(first_field=rows[0]['field'],last_field=rows[-1]['field'],sample_totals=totals)
    for choice in ('native','music'):
        a=runs[choice+'-aot'][0];b=runs[choice+'-lle'][0]
        for file in ('audio.wav','owner.csv','output.csv','driver.csv'):checks[choice+'_'+file+'_mode_parity']=digest(a/file)==digest(b/file)
    checks['binary_exact']=digest(base/'player.exe')==build['binary_sha256']
    paths=[Path(__file__),bp,source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                private_output_filter=True,whole_first_level_or_lifecycle_proven=False,
                echo_nonzero_cases_not_implemented=True,current_resume_not_implemented=True,
                public_preview_unchanged=True,full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)
    print(json.dumps(observations,indent=2),flush=True)


if __name__=='__main__':main()
