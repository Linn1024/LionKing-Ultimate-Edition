"""Exercise a normal 320-wide start, final menu and incoming Continue canvas."""
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
    base=ROOT/'build/pride-final-wide';out=base/'lifecycle';out.mkdir();commands={};checks={}
    build=base/'build-report.json';bound(build)
    source=ROOT/'build/pride-final-combined/lifecycle/report.json';prior=bound(source)
    profile=out/'resources.ini'
    profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n'
        'gameplay.levels.pride_lands.health_death = md\ngraphics.scenery = md\n')
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    env.update(TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',TLK_FINAL_SCENE_PRESENT='1',
        TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',TLK_CONTINUE_TRANSITION='1')
    template=prior['commands']['prior-revival-to-final-menu'].copy()
    i=template.index('--save-at');del template[i:i+3]
    template[0]=str(base/'player.exe');template[template.index('--resource-profile')+1]=str(profile)
    def run(name,field,load=None,save=None):
        folder=out/name;folder.mkdir();cmd=template.copy();cmd[cmd.index('--frames')+1]=str(field)
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:
            cmd[cmd.index(flag)+1]=str(folder/file)
        if load:cmd+=['--load',str(load/'saved.state')]
        if save:cmd+=['--save-at',str(save),str(folder/'saved.state')]
        with (folder/'run.log').open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        commands[name]=cmd;return folder
    start=run('ordinary-start-menu',3920,save=3800)
    menu=run('cold-menu',3920,load=start)
    checks['ordinary320_menu']=pixels(start/'window.png')[:2]==(640,448)
    checks['main_v3_record']=int.from_bytes((start/'saved.state').read_bytes()[8:12],'little')==3
    checks['main_final_menu_cold_client']=pixels(menu/'window.png')==pixels(start/'window.png')
    checks['main_final_menu_cold_guest']=hashes(menu/'run.log')==hashes(start/'run.log')
    incoming=run('incoming',4800,load=start,save=4800)
    data=(incoming/'saved.state').read_bytes();sidebytes=int.from_bytes(data[40:44],'little')
    sides=data[-sidebytes:];level=sides[3*64*224*4:]
    checks['incoming_level_sides_retained']=any(level)
    for field in (4801,5300):
        direct=run('direct'+str(field),field,load=start)
        resumed=run('cold'+str(field),field,load=incoming)
        checks[str(field)+'_cold_guest']=hashes(direct/'run.log')==hashes(resumed/'run.log')
        checks[str(field)+'_cold_client']=pixels(direct/'window.png')==pixels(resumed/'window.png')
        audio=pcm(resumed/'audio.wav');checks[str(field)+'_cold_pcm']=bool(audio) and pcm(direct/'audio.wav')[-len(audio):]==audio
        if field==5300:
            guest=json.loads((direct/'scene.json').read_text())['latched_gameplay']
            checks['continue_playable_pride']=guest['descriptor']==0x387 and guest['health']>0 and guest['lives']==2
    paths=[Path(__file__),source,build]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
