"""Check installed initial MD menu art through actual Windows player captures."""
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
    base=ROOT/'build/pride-final-menu-player2';build=base/'build-report.json';bound(build)
    fixture=ROOT/'build/pride-final-arena-fixture/report.json';previous=bound(fixture);fatal=previous['fatal_field']
    installed=ROOT/'build/pride-final-menu-scene/installed';manifest=installed/'install.json'
    info=json.loads(manifest.read_text());package=installed/info['menu_assets']['file'];assert digest(package)==info['menu_assets']['sha256']
    out=base/'verification';out.mkdir();checks={};commands={}
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))};env['TLK_FINAL_MD_ART']='1'
    def run(width,label,age,load=None,save=False,enabled=True,lle=False,asset=package):
        folder=out/(str(width)+'-'+label);folder.mkdir();cmd=previous['commands']['control0'].copy();cmd[0]=str(base/'player.exe')
        for flag,value in [('--resource-profile',out/(str(width)+'.ini')),('--config',out/'host.ini'),
            ('--frames',fatal+age),('--load',load/'saved.state' if load else ROOT/'build/pride-final-arena-fixture/prefatal-backend.state'),
            ('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')]:cmd[cmd.index(flag)+1]=str(value)
        if load:
            used=int(re.search(r'tape_words_used=(\d+)',(load/'run.log').read_text()).group(1));suffix=folder/'after.polled.tape'
            suffix.write_bytes((ROOT/'build/pride-final-arena-fixture/after.polled.tape').read_bytes()[used*2:]);cmd[cmd.index('--input-polled')+1]=str(suffix)
        cmd+=['--final-menu-assets',str(asset),'--wav',str(folder/'audio.wav'),'--wav-seconds','120']
        if save:cmd+=['--save-at',str(fatal+age),str(folder/'saved.state')]
        if lle:cmd+=['--lle']
        actual_env=env if enabled else {k:v for k,v in env.items() if k!='TLK_FINAL_MD_ART'}
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=actual_env,stdout=log,stderr=subprocess.STDOUT,timeout=120)
        commands[str(width)+'-'+label]=cmd;return folder,r.returncode
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    levels=[[0,32,65,98,139,172,205,238],[0,32,68,101,137,170,206,238],[0,32,65,98,139,172,205,238]]
    def reference(age,width):
        path=ROOT/f'build/pride-final-menu-art-original/game-over/{age}/window.png'
        w,h,image=pixels(path);start=(320-width)//2;result=[]
        for y in range(224):
            line=[]
            for x in range(start,start+width):
                rgb=[]
                for channel,c in enumerate(image[y*320+x]):
                    v=levels[channel].index(c);v=v*4+(v>>2);rgb.append(v<<3|v>>2)
                line.extend([tuple(rgb)]*2)
            result.extend(line);result.extend(line)
        return width*2,448,result
    for width in (256,320):
        (out/(str(width)+'.ini')).write_text('schema = 1\ngame = snes\ngameplay.levels.pride_lands.health_death = md\n'
            'gameplay.levels.pride_lands.final_life = md\ndisplay.viewport = '+('md' if width==320 else 'snes')+'\n')
        frames={}
        for age in (100,118,140,160,220):
            folder,code=run(width,str(age),age,save=age==140);frames[age]=folder
            checks[str(width)+'-'+str(age)+'_exit']=code==0
            if not code:checks[str(width)+'-'+str(age)+'_original_picture']=pixels(folder/'window.png')==reference(age,width)
        resumed,code=run(width,'cold160',160,load=frames[140]);checks[str(width)+'_cold_exit']=code==0
        if not code:
            checks[str(width)+'_cold_client']=pixels(resumed/'window.png')==pixels(frames[160]/'window.png')
            checks[str(width)+'_cold_guest']=hashes(resumed/'run.log')==hashes(frames[160]/'run.log')
            checks[str(width)+'_cold_pcm']=pcm(resumed/'audio.wav')==pcm(frames[160]/'audio.wav')[len(pcm(frames[140]/'audio.wav')):]
        native,code=run(width,'native-art',160,enabled=False);checks[str(width)+'_native_exit']=code==0
        if not code:
            checks[str(width)+'_independent_guest']=hashes(native/'run.log')==hashes(frames[160]/'run.log')
            checks[str(width)+'_independent_pcm']=pcm(native/'audio.wav')==pcm(frames[160]/'audio.wav')
            checks[str(width)+'_art_changed']=pixels(native/'window.png')!=pixels(frames[160]/'window.png')
        if width==320:
            lle,code=run(width,'lle160',160,lle=True);checks['lle_exit']=code==0
            if not code:
                checks['lle_guest']=hashes(lle/'run.log')==hashes(frames[160]/'run.log')
                checks['lle_client']=pixels(lle/'window.png')==pixels(frames[160]/'window.png')
                checks['lle_pcm']=pcm(lle/'audio.wav')==pcm(frames[160]/'audio.wav')
    for name,data in [('missing',None),('damaged',b'BAD ASSETS')]:
        path=out/(name+'.assets')
        if data is not None:path.write_bytes(data)
        _,code=run(320,name,100,asset=path);checks[name+'_requires_installation']=code==6
    paths=[Path(__file__),build,fixture,manifest,package]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        scope='Development unconfirmed-menu path; confirmed Continue exits intentionally unavailable',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
