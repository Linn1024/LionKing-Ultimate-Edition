"""Replay a deep ordinary-input branch from power-on in reference and player."""
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-fall-lower-route';out.mkdir()
    sweep=ROOT/'build/pride-fall-native-sweep'
    research=bound(sweep/'report.json')
    template_path=ROOT/'build/pride-pickup-flight35/wide-warm/report.json'
    template=bound(template_path)['command']
    anchor_log=(sweep/'anchor2500/run.log').read_text()
    used=int(re.search(r'tape_words_used=(\d+)',anchor_log)[1])
    original=ROOT/'engine/tapes/allbugsF.read.tape'
    tape=out/'poweron.polled.tape'
    tape.write_bytes(original.read_bytes()[:used*2]+(sweep/'2500-left240.polled.tape').read_bytes())
    profile=out/'native.ini';profile.write_text('schema = 1\ngame = snes\n')
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    env['TLK_RAM_LOG_DEATH']='1'
    commands={};checks={};outputs={}
    for mode in ('reference','aot','lle'):
        folder=out/mode;folder.mkdir()
        if mode=='reference':
            cmd=list(map(str,[ROOT/'engine/build-win/tlk_headless.exe','--rom',ROOT/'Lion King, The (USA).sfc',
                             '--resource-profile',profile,'--input-polled',tape,'--frames',3200,'--lle',
                             '--ram-log',folder/'game.ram']))
        else:
            cmd=template.copy()
            replacements={'--config':config,'--resource-profile':profile,'--input-polled':tape,'--frames':3200,
                          '--dump-window':folder/'window.png','--dump-scene':folder/'scene.json','--wav':folder/'audio.wav'}
            for flag,value in replacements.items():cmd[cmd.index(flag)+1]=str(value)
            if mode=='lle':cmd.append('--lle')
        commands[mode]=cmd
        with (folder/'run.log').open('wb') as log:
            run=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
                               timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
        checks[mode+'_exit']=run.returncode==0
        text=(folder/'run.log').read_text()
        outputs[mode]={key:re.search(key+r'=([0-9a-f]{64})',text)[1] for key in ('wram_sha256','frame_sha256')}
        print(mode,outputs[mode],flush=True)
    for key in ('wram_sha256','frame_sha256'):
        checks[key+'_all_three']=len({r[key] for r in outputs.values()})==1
    branch=(sweep/'2500-left240/game.ram').read_text().splitlines()
    replay=(out/'reference/game.ram').read_text().splitlines()
    checks['uninterrupted_branch_rows']=replay[-len(branch):]==branch
    for name in ('window.png','audio.wav','scene.json'):
        checks[name+'_both_modes']=digest(out/'aot'/name)==digest(out/'lle'/name)
    paths=[Path(__file__),sweep/'report.json',template_path,original,
           ROOT/'engine/build-win/tlk_headless.exe',Path(template[0])]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,outputs=outputs,
                branch='2500-left240',ordinary_poweron_inputs=True,actor_rom_or_rng_edits=False,
                natural_fall_observed=False,max_y=research['cases']['2500-left240']['max_y'],
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),flush=True)
    assert all(checks.values())


if __name__=='__main__':main()
