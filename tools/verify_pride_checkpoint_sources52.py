"""Check checkpoint timing with all four independent artwork/palette mixtures."""
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
    base=ROOT/'build/pride-checkpoint-animation52';source=base/'animation-play/report.json';prior=bound(source)
    out=base/'source-mixtures';out.mkdir();commands={};checks={};captures={}
    template=prior['commands']['md-contact'].copy()
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    hashes=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
    def case(pair):
        frames,palette=pair;name=frames+'-'+palette;folder=out/name;folder.mkdir()
        profile=Path(template[template.index('--resource-profile')+1]).read_text()
        profile+='\ngraphics.sprites.checkpoints.frames = '+frames+'\ngraphics.sprites.checkpoints.palette = '+palette+'\n'
        for stage,end in [('seed',3280),('blink',3293)]:
            target=folder/stage;target.mkdir();cmd=template.copy();cmd[cmd.index('--frames')+1]=str(end)
            for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(target/file)
            (target/'resources.ini').write_text(profile);(target/'host.ini').write_bytes(Path(template[template.index('--config')+1]).read_bytes())
            if stage=='seed':cmd[cmd.index('--save-at')+2]=str(target/'contact.state')
            else:
                i=cmd.index('--save-at');del cmd[i:i+3]
                cmd+=['--load',str(folder/'seed/contact.state')]
                cmd[cmd.index('--input-polled')+1]=str(source.parent/'neutral.tape')
            commands[name+'/'+stage]=cmd
            env=dict(clean,TLK_CHECKPOINT_TIMING_TRACE=str(target/'timing.csv'),TLK_SOFT_TREE_LOG=str(target/'tree.jsonl'))
            with (target/'run.log').open('wb') as log:
                subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=360,creationflags=subprocess.CREATE_NO_WINDOW)
        scene=json.loads((folder/'blink/scene.json').read_text())
        choices=json.loads((folder/'blink/tree.jsonl').read_text().splitlines()[-1])['choices']
        selected=lambda name:next(c for c in choices if c[0]==name)[-1]
        checks[name+'_timing_md']=selected('gameplay.levels.pride_lands.checkpoint_animation')==2
        checks[name+'_frames_independent']=selected('graphics.sprites.checkpoints.frames')==(2 if frames=='md' else 1)
        checks[name+'_palette_independent']=selected('graphics.sprites.checkpoints.palette')==(2 if palette=='md' else 1)
        checks[name+'_same_blink_pose']=any(p['pose']==0xc2fe18 for p in scene['pieces'])
        checks[name+'_all3280_seed_guest_fields']=hashes(folder/'seed')==hashes(source.parent/'md-contact')
        for stage,reference in [('seed',source.parent/'md-contact'),('blink',source.parent/'display-3293')]:
            checks[name+'_'+stage+'_guest_endpoint']=hashes(folder/stage)[-1]==hashes(reference)[-1]
            for file in ('audio.wav','timing.csv'):checks[name+'_'+stage+'_'+file]=digest(folder/stage/file)==digest(reference/file)
        captures[name]=dict(window_sha256=digest(folder/'blink/window.png'),checkpoint_adapter=scene.get('checkpoint_adapter'))
        print(name,'completed',flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(case,[('snes','snes'),('snes','md'),('md','snes'),('md','md')]))
    paths=[Path(__file__),source,base/'build-report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,captures=captures,
                no_guest_or_rom_edits=True,cross_build_save_compatibility_tested=False,full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
