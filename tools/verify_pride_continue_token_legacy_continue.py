"""Cold-load an existing ordinary Continue-menu save with the appended art nodes."""
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
    base=ROOT/'build/pride-continue-token47';out=base/'legacy-continue';out.mkdir()
    source=ROOT/'build/pride-sprite-fresh44/continue-verification/report.json';prior=bound(source);assert prior['result']=='PASS'
    build_path=base/'build-report.json';bound(build_path)
    data=ROOT/'game-data';manifest=json.loads((data/'install.json').read_text(encoding='utf-8-sig'))
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    checks={};commands={};states={}
    def run(mode):
        folder=out/mode;folder.mkdir();cmd=prior['commands']['cold-'+mode].copy();cmd[0]=str(base/'player.exe')
        cmd[cmd.index('--sprite-assets')+1]=str(data/manifest['sprite_assets']['file'])
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            p=folder/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
        with (folder/'resources.ini').open('a') as f:f.write('\ngraphics.sprites.pickups.continue_token.frames = md\ngraphics.sprites.pickups.continue_token.palette = md\n')
        for flag,name in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/name)
        commands[mode]=cmd;state=Path(cmd[cmd.index('--load')+1]);states[state.relative_to(ROOT).as_posix()]=digest(state)
        env=dict(clean,TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'))
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        print(mode,rc,flush=True);return folder,rc
    with ThreadPoolExecutor(max_workers=2) as pool:results=dict(zip(('aot','lle'),pool.map(run,('aot','lle'))))
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    for mode,(folder,rc) in results.items():
        old_cmd=prior['commands']['cold-'+mode];old=Path(old_cmd[old_cmd.index('--dump-window')+1]).parent
        log=(folder/'run.log').read_text();old_log=(old/'run.log').read_text()
        checks[mode+'_old_save_loads']=rc==0 and 'loaded_state=' in log
        fields=re.findall(pattern,log);checks[mode+'_all1500_guest_fields']=len(fields)==1500 and fields==re.findall(pattern,old_log)
        for name in ('window.png','scene.json','audio.wav'):checks[mode+'_'+name+'_preserved']=digest(folder/name)==digest(old/name)
        rows=[json.loads(r) for r in (folder/'tree.jsonl').read_text().splitlines()]
        for row in rows:row['choices']=row['choices'][:125]
        checks[mode+'_old_presentation_tree_preserved']=rows==[json.loads(r) for r in (old/'tree.jsonl').read_text().splitlines()]
        checks[mode+'_playable_after_continue']=rows[-1]['level']==0 and rows[-1]['lives']==2 and rows[-1]['health']>0
    checks['old_save_bytes_preserved']=all(digest(ROOT/p)==sha for p,sha in states.items())
    paths=[Path(__file__),source,build_path,data/'install.json',*(ROOT/p for p in states)]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
