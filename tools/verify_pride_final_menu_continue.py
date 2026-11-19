"""Check installed Continue drawing with native credits and separate MD timing."""
import json
import argparse
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
    parser=argparse.ArgumentParser();parser.add_argument('--player',default='build/pride-final-menu-player9');args=parser.parse_args()
    base=ROOT/args.player;build=base/'build-report.json';bound(build)
    source=ROOT/'build/pride-final-mixed-origin-probe/report.json';old=bound(source)
    manifest=ROOT/'build/pride-final-menu-scene/installed/install.json';package=manifest.parent/json.loads(manifest.read_text())['menu_assets']['file']
    out=base/'continue';out.mkdir();checks={};commands={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    neutral=out/'neutral.tape';neutral.write_bytes(bytes(4200*2))
    golden=out/'expected'
    subprocess.run([str(ROOT/'.tools/python32/python.exe'),str(ROOT/'tools/render_pride_final_menu_fixture.py'),str(package),str(golden)],check=True,timeout=60)
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))};env['TLK_FINAL_MD_ART']='1'
    def run(width,label,age,load=None,save=False,enabled=True):
        folder=out/(str(width)+'-'+label);folder.mkdir();cmd=old['commands']['selected-final'].copy();cmd[0]=str(base/'player.exe')
        for flag,value in [('--resource-profile',out/(str(width)+'.ini')),('--config',out/'host.ini'),('--frames',3894+age),
            ('--input',neutral),
            ('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        if load:cmd[cmd.index('--load')+1]=str(load/'saved.state')
        if save:cmd+=['--save-at',str(3894+age),str(folder/'saved.state')]
        cmd+=['--final-menu-assets',str(package)]
        actual=env if enabled else {k:v for k,v in env.items() if k!='TLK_FINAL_MD_ART'}
        with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=actual,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        commands[str(width)+'-'+label]=cmd;return folder
    for width in (256,320):
        (out/(str(width)+'.ini')).write_text('schema = 1\ngame = snes\ngameplay.levels.pride_lands.final_life = md\ndisplay.viewport = '+('md' if width==320 else 'snes')+'\n')
        frames={}
        for age in (118,140,160,220):
            frames[age]=run(width,str(age),age,save=age==140)
            w,h,source_pixels=pixels(golden/(str(age)+'.png'));start=(320-width)//2;scaled=[]
            for y in range(224):
                line=[p for x in range(start,start+width) for p in (source_pixels[y*320+x],)*2];scaled.extend(line);scaled.extend(line)
            checks[str(width)+'-'+str(age)+'_installed_composition']=pixels(frames[age]/'window.png')==(width*2,448,scaled)
        restored=run(width,'cold160',160,load=frames[140])
        checks[str(width)+'_cold_client']=pixels(restored/'window.png')==pixels(frames[160]/'window.png')
        checks[str(width)+'_cold_guest']=hashes(restored/'run.log')==hashes(frames[160]/'run.log')
        checks[str(width)+'_cold_pcm']=pcm(restored/'audio.wav')==pcm(frames[160]/'audio.wav')[len(pcm(frames[140]/'audio.wav')):]
        native=run(width,'native160',160,enabled=False)
        checks[str(width)+'_independent_guest']=hashes(native/'run.log')==hashes(frames[160]/'run.log')
        checks[str(width)+'_independent_pcm']=pcm(native/'audio.wav')==pcm(frames[160]/'audio.wav')
    paths=[Path(__file__),build,source,manifest,package,ROOT/'tools/render_pride_final_menu_fixture.py']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        scope='Installed Continue composition with preserved native credit count1; original-context credit count3 remains separate gameplay work',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
