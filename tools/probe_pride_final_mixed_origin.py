"""Reproduce selected graphics loss at the private native256 final-life capture."""
import json
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from capture_pride_difficulty_start import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels


def main():
    base=ROOT/'build/pride-title-fade2';bound(base/'build-report.json')
    out=ROOT/'build/pride-final-mixed-origin-probe';out.mkdir()
    reference=ROOT/'build/pride-title-fade2/verification/report.json';bound(reference)
    template=json.loads(reference.read_text())['commands'][0]
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ngraphics.scenery.palettes = md\n')
    cfg=out/'host.ini';cfg.write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    active=dict(clean,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
        TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',TLK_CONTINUE_TRANSITION='1')
    commands={}
    for name,env in [('selected-control',clean),('selected-final',active)]:
        folder=out/name;folder.mkdir();cmd=template.copy();cmd[0]=str(base/'player.exe')
        for flag,value in [('--resource-profile',profile),('--config',cfg),('--frames',3894),
            ('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:
            cmd[cmd.index(flag)+1]=str(value)
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        commands[name]=cmd
    left=pixels(out/'selected-control/window.png');right=pixels(out/'selected-final/window.png')
    changed=sum(a!=b for a,b in zip(left[2],right[2]))
    paths=[Path(__file__),base/'build-report.json',reference,ROOT/'build/pride-final-continue-fixture/prefatal.state']
    report=dict(result='REPRODUCED' if changed else 'NOT_REPRODUCED',changed_client_pixels=changed,
        client_shape=left[:2],commands=commands,
        guest_hashes={name:hashes(out/name/'run.log') for name in commands},
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],changed,'client pixels',flush=True)


if __name__=='__main__':main()
