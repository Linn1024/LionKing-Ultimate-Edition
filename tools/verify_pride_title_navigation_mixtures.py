"""Exercise selected title navigation with independent MD audio and graphics."""
import csv
import json
import os
from pathlib import Path
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm

def main():
    base=ROOT/'build/pride-title-navigation23';source=base/'verification/report.json';previous=bound(source)
    out=base/'mixtures';out.mkdir();checks={};commands={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    def run(width,gfx,age,lle=False,load=None,save=False):
        label=f'{width}-{gfx}-{age}'+('-lle' if lle else '-cold' if load else '')
        folder=out/label;folder.mkdir();cmd=previous['commands'][f'{width}-idle'].copy()
        if '--save-at' in cmd:
            i=cmd.index('--save-at');del cmd[i:i+3]
        profile=out/f'{width}-{gfx}.ini'
        if not profile.exists():
            template=Path(cmd[cmd.index('--resource-profile')+1]).read_text()
            graphics=('graphics.sprites.simba.cub.frames','graphics.sprites.simba.cub.palette',
                      'graphics.scenery.foreground','graphics.scenery.background','graphics.scenery.palettes')
            profile.write_text(template+'\n'+'\n'.join(key+' = '+gfx for key in graphics)+
                               '\naudio.music.pride_lands = md\naudio.effects.simba.hurt = md\n')
        for flag,value in [('--resource-profile',profile),('--config',out/'host.ini'),('--frames',4444+age),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        if lle:cmd+=['--lle']
        if load:cmd[cmd.index('--load')+1]=str(load)
        if save:cmd+=['--save-at',str(4444+age),str(folder/'saved.state')]
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=dict(clean,TLK_FINAL_MD_ART='1',TLK_CONTINUE_EXIT_LOG=str(folder/'exit.csv')),
            stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[label]=cmd;checks[label+'_exit']=r.returncode==0;print(label,r.returncode,flush=True);return folder
    for width in (256,320):
        starts={};ends={}
        for gfx in ('snes','md'):
            starts[gfx]=run(width,gfx,1)
            ends[gfx]=run(width,gfx,700)
            alternate=run(width,gfx,700,lle=True)
            for name,fn in [('client',lambda p:pixels(p/'window.png')),('guest',lambda p:hashes(p/'run.log')),('pcm',lambda p:pcm(p/'audio.wav'))]:
                checks[f'{width}_{gfx}_normal_lle_{name}']=fn(ends[gfx])==fn(alternate)
            rows=list(csv.reader((ends[gfx]/'exit.csv').open()));copies=[r for r in rows if r[0]=='title_upload']
            checks[f'{width}_{gfx}_sixteen_packets']=len(copies)==16 and {int(r[5]) for r in copies}==set(range(16))
        checks[f'{width}_graphics_visible_at_origin']=pixels(starts['snes']/'window.png')!=pixels(starts['md']/'window.png')
        checks[f'{width}_origin_graphics_independent_guest']=hashes(starts['snes']/'run.log')==hashes(starts['md']/'run.log')
        checks[f'{width}_origin_graphics_independent_pcm']=pcm(starts['snes']/'audio.wav')==pcm(starts['md']/'audio.wav')
        checks[f'{width}_graphics_independent_guest']=hashes(ends['snes']/'run.log')==hashes(ends['md']/'run.log')
        checks[f'{width}_graphics_independent_pcm']=pcm(ends['snes']/'audio.wav')==pcm(ends['md']/'audio.wav')
        baseline=pcm(source.parent/f'{width}-idle/audio.wav')
        checks[f'{width}_md_audio_is_active']=pcm(ends['snes']/'audio.wav')[:len(baseline)]!=baseline
        saved=run(width,'md',367,save=True);cold=run(width,'md',700,load=saved/'saved.state')
        checks[f'{width}_mixed_cold_client']=pixels(cold/'window.png')==pixels(ends['md']/'window.png')
        checks[f'{width}_mixed_cold_guest']=hashes(cold/'run.log')==hashes(ends['md']/'run.log')
        checks[f'{width}_mixed_cold_pcm']=pcm(cold/'audio.wav')==pcm(ends['md']/'audio.wav')[len(pcm(saved/'audio.wav')):]
    paths=[Path(__file__),source,base/'build-report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
                scope='Supported Pride music/hurt and cub/scenery leaves in reviewed final/title path; no full source-tree or title-art completion claim',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True);assert all(checks.values())

if __name__=='__main__':main()
