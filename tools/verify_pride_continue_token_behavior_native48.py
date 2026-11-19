"""Verify old saves and unchanged native Sun behavior with the new controls."""
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-continue-token-behavior48';build_path=base/'build-report.json';bound(build_path)
    source=ROOT/'build/pride-continue-token47/artwork-verification/report.json';prior=bound(source)
    out=base/'native-cold';out.mkdir();checks={};commands={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    baseline=Path(prior['commands']['both'][prior['commands']['both'].index('--dump-window')+1]).parent
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    expected=re.findall(pattern,(baseline/'run.log').read_text())
    for label,audio,timing,lle in [('native-aot','snes','snes',False),('native-lle','snes','snes',True),('reject-audio','md','snes',False),('reject-timing','snes','md',False)]:
        folder=out/label;folder.mkdir();cmd=prior['commands']['both'].copy();cmd[0]=str(base/'player.exe')
        for flag,name in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            p=folder/name;p.write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(p)
        with (folder/'resources.ini').open('a') as f:f.write('\naudio.effects.world.continue_token = '+audio+'\ngameplay.levels.pride_lands.continue_token_animation = '+timing+'\n')
        for flag,name in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/name)
        if lle:cmd.append('--lle')
        commands[label]=cmd
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        text=(folder/'run.log').read_text();print(label,rc,flush=True)
        if label.startswith('reject'):
            checks[label+'_before_play']=rc==8 and 'Final scene save is invalid or source choices differ' in text and 'frame_sha256=' not in text
        else:
            checks[label+'_old_save_loads']=rc==0 and 'loaded_state=' in text
            checks[label+'_all15_guest_fields']=re.findall(pattern,text)==expected and len(expected)==15
            for name in ('window.png','scene.json','audio.wav'):checks[label+'_'+name+'_preserved']=digest(folder/name)==digest(baseline/name)
    paths=[Path(__file__),source,build_path]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
