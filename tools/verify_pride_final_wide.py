"""Verify complete 320-wide arena final canvases and cold resumes."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    base=ROOT/'build/pride-final-wide';build=base/'build-report.json';bound(build)
    fixture=ROOT/'build/pride-final-arena-fixture/report.json';old=bound(fixture);fatal=old['fatal_field']
    out=base/'verification';out.mkdir();checks={};commands={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    active=dict(clean,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',TLK_FINAL_SCENE_PRESENT='1',
        TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',TLK_CONTINUE_TRANSITION='1')
    choices={'native':'','scenery':'graphics.scenery = md\n',
        'sprites':'graphics.sprites.simba.cub = md\ngraphics.sprites.enemies.hyenas = md\ngraphics.hud = md\n'}
    def run(case,label,age,enabled=True,save=False,restored=None,lle=False):
        folder=out/(case+'-'+label);folder.mkdir();cmd=old['commands']['old0'].copy();cmd[0]=str(base/'player.exe')
        cmd[cmd.index('--resource-profile')+1]=str(out/(case+'.ini'));cmd[cmd.index('--frames')+1]=str(fatal+age)
        cmd[cmd.index('--load')+1]=str(restored/'saved.state' if restored else ROOT/'build/pride-final-arena-fixture/prefatal-backend.state')
        if restored:
            used=int(re.search(r'tape_words_used=(\d+)',(restored/'run.log').read_text()).group(1))
            suffix=folder/'after.polled.tape';suffix.write_bytes((ROOT/'build/pride-final-arena-fixture/after.polled.tape').read_bytes()[used*2:])
            cmd[cmd.index('--input-polled')+1]=str(suffix)
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json')]:cmd[cmd.index(flag)+1]=str(folder/file)
        cmd+=['--wav',str(folder/'audio.wav'),'--wav-seconds','120']
        if save:cmd+=['--save-at',str(fatal+age),str(folder/'saved.state')]
        if lle:cmd+=['--lle']
        with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=active if enabled else clean,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        commands[case+'-'+label]=cmd;return folder
    def fade(image,age):
        loss=(((age+2)//3)*31+3)//7
        def component(c):
            v=max(0,(c>>3)-loss);return v<<3|v>>2
        return image[0],image[1],[tuple(component(c) for c in p) for p in image[2]]
    for case,extra in choices.items():
        (out/(case+'.ini')).write_text('schema = 1\ngame = snes\ndisplay.viewport = md\ngameplay.levels.pride_lands.health_death = md\n'+extra)
        control=run(case,'control',0,enabled=False)
        latched=run(case,'control1',1,enabled=False)
        frames={age:run(case,str(age),age,save=age in (0,7)) for age in (0,1,7,10,19,100,118,120,124)}
        checks[case+'_actual320_client']=pixels(frames[0]/'window.png')[:2]==(640,448)
        checks[case+'_v3_saved']=int.from_bytes((frames[0]/'saved.state').read_bytes()[8:12],'little')==3
        checks[case+'_selected_frozen_origin']=pixels(frames[0]/'window.png')==pixels(control/'window.png')
        scene=json.loads((control/'scene.json').read_text());checks[case+'_actual_arena']=scene['latched_gameplay']['descriptor']==0x80d and scene['stage_detected']
        for age in (1,7,10):checks[f'{case}_{age}_whole_fade']=pixels(frames[age]/'window.png')==fade(pixels(latched/'window.png'),age)
        checks[case+'_first_latch_guest_unchanged']=hashes(frames[1]/'run.log')==hashes(latched/'run.log')
        s0=json.loads((frames[0]/'scene.json').read_text());s1=json.loads((frames[1]/'scene.json').read_text())
        control1=json.loads((latched/'scene.json').read_text())
        checks[case+'_foreground_latches']=s1['lines'][0]['scroll'][0]==control1['lines'][0]['scroll'][0]
        checks[case+'_md_background_phase_frozen']=s1['md_background_camera']==s0['md_background_camera']
        checks[case+'_black19']=not any(any(p) for p in pixels(frames[19]/'window.png')[2])
        checks[case+'_destination100']=any(any(p) for p in pixels(frames[100]/'window.png')[2])
        checks[case+'_full_target118']=pixels(frames[118]/'window.png')==pixels(frames[120]/'window.png')
        for saved,end in [(0,1),(7,10)]:
            resumed=run(case,f'resumed{saved}-{end}',end,restored=frames[saved])
            checks[f'{case}_{saved}_saved_guest']=hashes(resumed/'run.log')==hashes(frames[end]/'run.log')
            checks[f'{case}_{saved}_saved_client']=pixels(resumed/'window.png')==pixels(frames[end]/'window.png')
            checks[f'{case}_{saved}_saved_pcm']=pcm(resumed/'audio.wav')==pcm(frames[end]/'audio.wav')[len(pcm(frames[saved]/'audio.wav')):]
        if case=='native':
            lle=run(case,'lle10',10,lle=True)
            checks['lle_guest']=hashes(lle/'run.log')==hashes(frames[10]/'run.log')
            checks['lle_client']=pixels(lle/'window.png')==pixels(frames[10]/'window.png')
            checks['lle_pcm']=pcm(lle/'audio.wav')==pcm(frames[10]/'audio.wav')
    paths=[Path(__file__),build,fixture]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),'checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
