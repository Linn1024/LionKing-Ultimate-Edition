"""Verify description-only relink53 against all three qualified52 full routes."""
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
    base=ROOT/'build/pride-checkpoint-capability53';buildpath=base/'build-report.json';build=bound(buildpath)
    source=ROOT/'build/pride-checkpoint-animation52/completion/report.json';prior=bound(source);assert prior['result']=='PASS'
    out=base/'completion';out.mkdir();commands={};checks={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    def run(label):
        folder=out/label;folder.mkdir();cmd=prior['commands'][label].copy();cmd[0]=str(base/'player.exe')
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            target=folder/name;target.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(target)
        for flag,name in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/name)
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
        original=source.parent/label;checks[label+'_exit']=rc==0
        checks[label+'_all6000_guest_fields_unchanged']=len(hashes(folder))==6000 and hashes(folder)==hashes(original)
        for name in ('audio.wav','window.png','scene.json','tree.jsonl','events.csv','sun.csv'):
            checks[label+'_'+name+'_unchanged']=digest(folder/name)==digest(original/name)
        if label!='native':checks[label+'_timing_unchanged']=digest(folder/'timing.csv')==digest(original/'timing.csv')
        rows=[json.loads(line) for line in (folder/'tree.jsonl').read_text().splitlines()]
        checks[label+'_enters_next_level']=rows[-1]['field']==6000 and rows[-1]['level']==1 and rows[-1]['lives']>0
    checks['resources_description_only']=build['description_only_source_delta'] and build['unchanged_prior_inputs']==321
    checks['precise_capability_is_in_binary']=b'native game update scheduling retained' in (base/'player.exe').read_bytes()
    paths=[Path(__file__),source,buildpath]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
                no_guest_or_rom_edits=True,cross_build_save_compatibility_tested=False,full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
