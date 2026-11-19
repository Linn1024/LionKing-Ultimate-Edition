"""Complete the first-level route with both Sun behavior sources selected MD."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-continue-token-behavior50';build_path=base/'build-report.json';build=bound(build_path)
    source=ROOT/'build/pride-continue-token47/full-route/report.json';prior=bound(source)
    out=base/'completion';out.mkdir();checks={};commands={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    def run(mode):
        folder=out/mode;folder.mkdir();cmd=prior['commands']['aot'].copy();cmd[0]=str(base/'player.exe')
        profile=Path(cmd[cmd.index('--resource-profile')+1]).read_text()+'\naudio.effects.world.continue_token = md\ngameplay.levels.pride_lands.continue_token_animation = md\n'
        (folder/'resources.ini').write_text(profile);(folder/'host.ini').write_bytes(Path(cmd[cmd.index('--config')+1]).read_bytes())
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/name)
        if mode=='lle':cmd.append('--lle')
        commands[mode]=cmd
        env=dict(clean,TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'),TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_CONTINUE_TOKEN_TIMING_TRACE=str(folder/'timing.csv'))
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        print(mode,rc,flush=True);return mode,folder,rc
    with ThreadPoolExecutor(max_workers=2) as pool:results={mode:(folder,rc) for mode,folder,rc in pool.map(run,('aot','lle'))}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    hashes=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
    for mode,(folder,rc) in results.items():
        checks[mode+'_exit']=rc==0
        rows=[json.loads(line) for line in (folder/'tree.jsonl').read_text().splitlines()]
        checks[mode+'_completes_pride']=rows[-1]['field']==6000 and rows[-1]['level']==1 and rows[-1]['lives']>0
        checks[mode+'_both_sun_choices_md']=all(next(r for r in rows[-1]['choices'] if r[0]==name)[-1]==2 for name in ('audio.effects.world.continue_token','gameplay.levels.pride_lands.continue_token_animation'))
        checks[mode+'_timing_exercised']=(folder/'timing.csv').exists() and len((folder/'timing.csv').read_text().splitlines())>4
    a=results['aot'][0];b=results['lle'][0]
    checks['all6000_guest_fields_match']=len(hashes(a))==6000 and hashes(a)==hashes(b)
    for name in ('audio.wav','window.png','scene.json','tree.jsonl','events.csv','timing.csv'):checks[name+'_mode_parity']=digest(a/name)==digest(b/name)
    checks['binary_exact']=digest(base/'player.exe')==build['binary_sha256']
    paths=[Path(__file__),build_path,source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
                normal_poweron_no_guest_edits=True,full_first_level_fidelity_complete=False,cross_build_save_compatibility_tested=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
