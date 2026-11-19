"""Complete Pride Lands with checkpoint timing selected independently."""
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
    base=ROOT/'build/pride-checkpoint-animation52';buildpath=base/'build-report.json';build=bound(buildpath)
    source=ROOT/'build/pride-continue-token-behavior50/completion/report.json';prior=bound(source)
    out=base/'completion';out.mkdir();checks={};commands={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    def run(label):
        folder=out/label;folder.mkdir();cmd=prior['commands']['aot'].copy();cmd[0]=str(base/'player.exe')
        profile=Path(cmd[cmd.index('--resource-profile')+1]).read_text()
        profile+='\ngameplay.levels.pride_lands.checkpoint_animation = '+('snes' if label=='native' else 'md')+'\n'
        (folder/'resources.ini').write_text(profile);(folder/'host.ini').write_bytes(Path(cmd[cmd.index('--config')+1]).read_bytes())
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/name)
        if label=='lle':cmd.append('--lle')
        commands[label]=cmd
        env=dict(clean,TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'),TLK_AUDIO_EVENTS=str(folder/'events.csv'),
                 TLK_CHECKPOINT_TIMING_TRACE=str(folder/'timing.csv'),TLK_CONTINUE_TOKEN_TIMING_TRACE=str(folder/'sun.csv'))
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        print(label,rc,flush=True);return label,folder,rc
    with ThreadPoolExecutor(max_workers=3) as pool:results={label:(folder,rc) for label,folder,rc in pool.map(run,('native','aot','lle'))}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    hashes=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
    for label,(folder,rc) in results.items():
        rows=[json.loads(line) for line in (folder/'tree.jsonl').read_text().splitlines()]
        checks[label+'_exit']=rc==0
        checks[label+'_completes_pride']=rows[-1]['field']==6000 and rows[-1]['level']==1 and rows[-1]['lives']>0
        checks[label+'_checkpoint_choice']=next(c for c in rows[-1]['choices'] if c[0]=='gameplay.levels.pride_lands.checkpoint_animation')[-1]==(1 if label=='native' else 2)
        traces=list(csv.DictReader((folder/'timing.csv').open())) if (folder/'timing.csv').exists() else []
        checks[label+'_timing_source_independent']=bool(traces)==(label!='native')
    a=results['aot'][0];b=results['lle'][0];n=results['native'][0]
    checks['all6000_guest_fields_mode_parity']=len(hashes(a))==6000 and hashes(a)==hashes(b)
    checks['native_all6000_guest_fields_unchanged']=hashes(n)==hashes(source.parent/'aot')
    for name in ('audio.wav','window.png','scene.json','tree.jsonl','events.csv','timing.csv','sun.csv'):
        checks[name+'_mode_parity']=digest(a/name)==digest(b/name)
    for name in ('audio.wav','window.png','scene.json','events.csv','sun.csv'):
        original='timing.csv' if name=='sun.csv' else name
        checks['native_'+name+'_unchanged']=digest(n/name)==digest(source.parent/'aot'/original)
    checks['binary_exact']=digest(base/'player.exe')==build['binary_sha256']
    paths=[Path(__file__),buildpath,source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
                normal_poweron_no_guest_edits=True,full_first_level_fidelity_complete=False,
                cross_build_save_compatibility_tested=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
