"""Verify a full mixed Pride route with independent Continue-token art enabled."""
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
    base=ROOT/'build/pride-continue-token47';build_path=base/'build-report.json';build=bound(build_path)
    source=ROOT/'build/pride-sprite-fresh44/runtime-verification/report.json';prior=bound(source)
    out=base/'full-route';out.mkdir();commands={};checks={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    clean['SDL_VIDEODRIVER']='dummy'
    def run(label):
        folder=out/label;folder.mkdir();cmd=prior['commands']['full-aot'].copy();cmd[0]=str(base/'player.exe')
        cmd[cmd.index('--sprite-assets')+1]=str(ROOT/'build/pride-continue-token-assets/sprites.assets')
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            p=folder/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
        with (folder/'resources.ini').open('a') as f:
            f.write('\ngraphics.sprites.pickups.continue_token.frames = md\ngraphics.sprites.pickups.continue_token.palette = md\n')
        for flag,name in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/name)
        if label=='lle':cmd.append('--lle')
        commands[label]=cmd
        env=dict(clean,TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'),TLK_PORCUPINE_ATTACK_TRACE=str(folder/'attack.csv'),TLK_AUDIO_EVENTS=str(folder/'events.csv'))
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=900,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        print(label,rc,flush=True);return folder,rc
    with ThreadPoolExecutor(max_workers=2) as pool:results=dict(zip(('aot','lle'),pool.map(run,('aot','lle'))))
    baseline=Path(prior['commands']['full-aot'][prior['commands']['full-aot'].index('--dump-window')+1]).parent
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    hashes=lambda p:re.findall(pattern,(p/'run.log').read_text())
    expected=hashes(baseline);checks['reference_all6000_fields']=len(expected)==6000
    old_tree=[json.loads(line) for line in (baseline/'tree.jsonl').read_text().splitlines()]
    for label,(folder,rc) in results.items():
        checks[label+'_exit']=rc==0;checks[label+'_all6000_guest_fields']=hashes(folder)==expected
        for name in ('window.png','scene.json','audio.wav','attack.csv','events.csv'):
            checks[label+'_'+name+'_preserved']=digest(folder/name)==digest(baseline/name)
        tree=[json.loads(line) for line in (folder/'tree.jsonl').read_text().splitlines()]
        checks[label+'_completes_pride']=len(tree)==6000 and tree[-1]['level']==1
        for row in tree:row['choices']=row['choices'][:125]
        checks[label+'_original_tree_preserved']=tree==old_tree
    checks['binary_bound']=digest(base/'player.exe')==build['binary_sha256']
    paths=[Path(__file__),build_path,source,ROOT/'build/pride-continue-token-assets/sprites.assets']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
