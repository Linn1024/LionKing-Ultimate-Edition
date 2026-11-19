"""Verify selected native256 origin, first fade and fatal-field save continuation."""
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
    base=ROOT/'build/pride-final-mixed-origin';build=base/'build-report.json';bound(build)
    probe=ROOT/'build/pride-final-mixed-origin-probe/report.json';observed=bound(probe)
    out=base/'verification2';out.mkdir();checks={};commands={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    active=dict(clean,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
        TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',TLK_CONTINUE_TRANSITION='1')
    cfg=out/'host.ini';cfg.write_text('opengl = 0\nscale = 2\n')
    choices={'palettes':'graphics.scenery.palettes = md\n',
        'sprites':'graphics.sprites.simba.cub = md\ngraphics.sprites.enemies.other = md\ngraphics.hud = md\n',
        'scenery':'graphics.scenery = md\n','native':''}
    def run(case,label,age,old=False,enabled=True,save=False,restored=None,interpreted=False):
        folder=out/(case+'-'+label);folder.mkdir();cmd=observed['commands']['selected-final'].copy()
        cmd[0]=str(ROOT/('build/pride-title-fade2/player.exe' if old else 'build/pride-final-mixed-origin/player.exe'))
        for flag,value in [('--resource-profile',out/(case+'.ini')),('--config',cfg),('--frames',3894+age),
            ('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:
            cmd[cmd.index(flag)+1]=str(value)
        if restored:cmd[cmd.index('--load')+1]=str(restored)
        if save:cmd+=['--save-at',str(3894+age),str(folder/'saved.state')]
        if interpreted:cmd+=['--lle']
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,env=active if enabled else clean,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        commands[case+'-'+label]=cmd;return folder
    def first_fade(source):
        def component(c):
            value=max(0,(c>>3)-4);return value<<3|value>>2
        return (source[0],source[1],[tuple(component(c) for c in p) for p in source[2]])
    for case,extra in choices.items():
        (out/(case+'.ini')).write_text('schema = 1\ngame = snes\n'+extra)
        control=run(case,'control',0,old=True,enabled=False)
        old=run(case,'old',0,old=True)
        current=run(case,'current',0,save=case!='native')
        one=run(case,'one',1)
        checks[case+'_selected_origin']=pixels(current/'window.png')==pixels(control/'window.png')
        checks[case+'_guest_unchanged']=hashes(current/'run.log')==hashes(old/'run.log')
        checks[case+'_pcm_unchanged']=pcm(current/'audio.wav')==pcm(old/'audio.wav')
        checks[case+'_first_fade_from_selected']=pixels(one/'window.png')==first_fade(pixels(current/'window.png'))
        if case!='native':
            checks[case+'_visible_fix']=pixels(old/'window.png')!=pixels(current/'window.png')
            resumed=run(case,'resumed-one',1,restored=current/'saved.state')
            checks[case+'_fatal_field_save_picture']=pixels(resumed/'window.png')==pixels(one/'window.png')
            checks[case+'_fatal_field_save_guest']=hashes(resumed/'run.log')==hashes(one/'run.log')
            # Direct includes fatal field3894 plus3895; resumed starts at3895.
            checks[case+'_fatal_field_save_pcm']=pcm(resumed/'audio.wav')==pcm(one/'audio.wav')[len(pcm(current/'audio.wav')):]
        else:
            checks['native_picture_unchanged']=pixels(old/'window.png')==pixels(current/'window.png')
        if case=='palettes':
            lle=run(case,'interpreted-one',1,interpreted=True)
            checks['mixed_interpreted_guest']=hashes(lle/'run.log')==hashes(one/'run.log')
            checks['mixed_interpreted_client']=pixels(lle/'window.png')==pixels(one/'window.png')
            checks['mixed_interpreted_pcm']=pcm(lle/'audio.wav')==pcm(one/'audio.wav')
    result=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        scope=__doc__,public_player_changed=False,resource_activation_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in [Path(__file__),build,probe]},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],sum(checks.values()),'/',len(checks),'checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
