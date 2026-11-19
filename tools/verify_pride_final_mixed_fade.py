"""Verify seven-step native256 final fades and selected-media cold resumes."""
import json
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    base=ROOT/'build/pride-final-mixed-fade';build=base/'build-report.json';bound(build)
    previous=ROOT/'build/pride-final-mixed-origin/verification2/report.json';old=bound(previous)
    out=base/'verification';out.mkdir();checks={};commands={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    active=dict(clean,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
        TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',TLK_CONTINUE_TRANSITION='1')
    def run(case,label,age,legacy=False,save=False,restored=None,lle=False):
        folder=out/(case+'-'+label);folder.mkdir();cmd=old['commands'][case+'-one'].copy()
        cmd[0]=str(ROOT/('build/pride-final-mixed-origin/player.exe' if legacy else 'build/pride-final-mixed-fade/player.exe'))
        cmd[cmd.index('--frames')+1]=str(3894+age)
        for flag,name in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:
            cmd[cmd.index(flag)+1]=str(folder/name)
        if save:cmd+=['--save-at',str(3894+age),str(folder/'saved.state')]
        if restored:cmd[cmd.index('--load')+1]=str(restored)
        if lle:cmd+=['--lle']
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,env=active,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        commands[case+'-'+label]=cmd;return folder
    def faded(source,age):
        loss=(((age+2)//3)*31+3)//7
        def component(c):
            value=max(0,(c>>3)-loss);return value<<3|value>>2
        return (source[0],source[1],[tuple(component(c) for c in p) for p in source[2]])
    for case in ('native','palettes','sprites','scenery'):
        runs={age:run(case,str(age),age,save=age==7 and case!='native') for age in (0,7,10,19,118,120,124)}
        control=Path(old['commands'][case+'-control'][old['commands'][case+'-control'].index('--dump-window')+1])
        checks[case+'_selected_origin']=pixels(runs[0]/'window.png')==pixels(control)
        for age in (7,10):checks[f'{case}_{age}_whole_fade']=pixels(runs[age]/'window.png')==faded(pixels(runs[0]/'window.png'),age)
        checks[case+'_black19']=not any(any(p) for p in pixels(runs[19]/'window.png')[2])
        checks[case+'_full_target118']=pixels(runs[118]/'window.png')==pixels(runs[120]/'window.png') and any(any(p) for p in pixels(runs[118]/'window.png')[2])
        if case!='native':
            resumed=run(case,'resumed10',10,restored=runs[7]/'saved.state')
            checks[case+'_resumed_picture']=pixels(resumed/'window.png')==pixels(runs[10]/'window.png')
            checks[case+'_resumed_guest']=hashes(resumed/'run.log')==hashes(runs[10]/'run.log')
            checks[case+'_resumed_pcm']=pcm(resumed/'audio.wav')==pcm(runs[10]/'audio.wav')[len(pcm(runs[7]/'audio.wav')):]
        if case in ('native','palettes'):
            legacy=run(case,'old124',124,legacy=True)
            checks[case+'_live_menu_picture_unchanged']=pixels(legacy/'window.png')==pixels(runs[124]/'window.png')
            checks[case+'_guest_unchanged']=hashes(legacy/'run.log')==hashes(runs[124]/'run.log')
            checks[case+'_pcm_unchanged']=pcm(legacy/'audio.wav')==pcm(runs[124]/'audio.wav')
        if case=='palettes':
            legacy=run(case,'old19',19,legacy=True)
            checks['old_ghost_reproduced']=any(any(p) for p in pixels(legacy/'window.png')[2])
            lle=run(case,'lle10',10,lle=True)
            checks['mixed_lle_picture']=pixels(lle/'window.png')==pixels(runs[10]/'window.png')
            checks['mixed_lle_guest']=hashes(lle/'run.log')==hashes(runs[10]/'run.log')
            checks['mixed_lle_pcm']=pcm(lle/'audio.wav')==pcm(runs[10]/'audio.wav')
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        scope=__doc__,public_player_changed=False,resource_activation_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in [Path(__file__),build,previous]},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),'checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
