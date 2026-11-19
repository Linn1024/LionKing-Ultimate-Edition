"""Verify installed title payload playback, real windows, cold loads and ownership."""
import argparse
import csv
import json
import os
from pathlib import Path
import struct
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='verification');parser.add_argument('--player',default='build/pride-title-native15');args=parser.parse_args()
    base=ROOT/args.player;build=base/'build-report.json';bound(build)
    source=ROOT/'build/pride-game-over13/verification2/report.json';old=bound(source)
    lifecycle=ROOT/'build/pride-game-over13/lifecycle2/report.json';life=bound(lifecycle)
    manifest=ROOT/'build/pride-title-native-installed/setup-verification/Game data & native loads/install.json';info=json.loads(manifest.read_text())
    native=manifest.parent/info['native_final_assets']['file'];out=base/args.output;out.mkdir();checks={};commands={};timings={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_FINAL_MD_ART']='1'
    def run(width,label,age,case='none',load=None,save=False,lle=False,native_art=False,old_player=False,tape=None,native_control=False):
        folder=out/f'{width}-{label}';folder.mkdir()
        template=life['commands'][f'{width}-native-control2600'] if native_control else old['commands'][f'{width}-{case}-'+('title700' if case=='none' else '150')]
        cmd=template.copy()
        if '--save-at' in cmd:
            i=cmd.index('--save-at');del cmd[i:i+3]
        if not old_player:cmd[0]=str(base/'player.exe');cmd[cmd.index('--final-native-assets')+1]=str(native)
        for flag,value in [('--config',out/'host.ini'),('--frames',4444+age),('--dump-window',folder/'window.png'),
                           ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        if load:cmd[cmd.index('--load')+1]=str(load)
        if tape:cmd[cmd.index('--input')+1]=str(tape)
        if save:cmd+=['--save-at',str(4444+age),str(folder/'saved.state')]
        if lle:cmd+=['--lle']
        actual=dict(env,TLK_CONTINUE_EXIT_LOG=str(folder/'exit.csv'))
        if native_art or native_control:actual.pop('TLK_FINAL_MD_ART')
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=actual,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[f'{width}-{label}']=cmd;print(width,label,r.returncode,flush=True);return folder,r.returncode
    def same(prefix,a,b,skip=0):
        if not (a/'window.png').exists():
            checks[prefix+'_client']=checks[prefix+'_guest']=checks[prefix+'_pcm']=False;return
        checks[prefix+'_client']=pixels(a/'window.png')==pixels(b/'window.png')
        checks[prefix+'_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        checks[prefix+'_pcm']=pcm(a/'audio.wav')==pcm(b/'audio.wav')[skip:]
    for width in (256,320):
        frames={}
        for age in (342,366,400,432,434,435,437,700):
            folder,code=run(width,str(age),age,save=age in (366,400,432,434));frames[age]=folder;checks[f'{width}_{age}_exit']=code==0
        same(f'{width}_preparation_not_early',frames[342],source.parent/f'{width}-none-342')
        for saved,target in ((366,435),(400,435),(432,435),(434,435),(434,700)):
            folder,code=run(width,f'cold{saved}to{target}',target,load=frames[saved]/'saved.state')
            checks[f'{width}_cold{saved}to{target}_exit']=code==0
            same(f'{width}_cold{saved}to{target}',folder,frames[target],len(pcm(frames[saved]/'audio.wav')))
        for age in (435,700):
            folder,code=run(width,f'lle{age}',age,lle=True);checks[f'{width}_lle{age}_exit']=code==0;same(f'{width}_lle{age}',folder,frames[age])
        for age,previous in ((435,463),(437,465)):
            folder,code=run(width,f'previous{previous}',previous,old_player=True);checks[f'{width}_previous{previous}_exit']=code==0
            checks[f'{width}_title_picture{age}_matches_previous{previous}']=pixels(frames[age]/'window.png')==pixels(folder/'window.png')
        folder,code=run(width,'native-art700',700,native_art=True);checks[f'{width}_native_art_exit']=code==0;same(f'{width}_art_independence',folder,frames[700])
        pressed,code=run(width,'input-title700',700,case='a140');checks[f'{width}_input_title_exit']=code==0
        for name,folder,expected in [('timeout',frames[700],435),('button',pressed,251)]:
            rows=list(csv.reader((folder/'exit.csv').open()));copies=[r for r in rows if r[0]=='title_fast']
            first=next(int(r[1]) for r in rows if r[0]=='frame' and r[2]=='c005ab' and int(r[5])>0)
            checks[f'{width}_{name}_all_ten_copies']=len(copies)==10 and {int(r[5]) for r in copies}==set(range(10,20))
            checks[f'{width}_{name}_first_picture']=first==expected
            timings[f'{width}-{name}']=dict(first_picture=first,previous=expected+28,original=370 if name=='timeout' else 186,remaining_fields=65)
        tape=Path(life['commands'][f'{width}-new-game2000'][life['commands'][f'{width}-new-game2000'].index('--input')+1])
        live,code=run(width,'new-game2000',2000,tape=tape,save=True);checks[f'{width}_new_game_exit']=code==0
        scene=json.loads((live/'scene.json').read_text());guest=scene['latched_gameplay'];checks[f'{width}_new_game_is_pride']=scene['level']==0 and guest['descriptor']==0x387 and guest['health']==4
        data=(live/'saved.state').read_bytes();at=96+struct.unpack_from('<I',data,20)[0]
        checks[f'{width}_new_game_owner_retired']=struct.unpack_from('<I',data,at+100)[0]==struct.unpack_from('<I',data,at+112)[0]==0
        checks[f'{width}_new_game_counters_preserved']=all(guest[k]==life['observations'][str(width)]['native_control'][k] for k in ('health','lives','checkpoint','player'))
        cold,code=run(width,'cold-new-game2000',2000,load=frames[400]/'saved.state',tape=tape);checks[f'{width}_cold_new_game_exit']=code==0;same(f'{width}_cold_new_game',cold,live,len(pcm(frames[400]/'audio.wav')))
        control,code=run(width,'native-control2600',2600,native_control=True);checks[f'{width}_native_control_exit']=code==0
        same(f'{width}_native_final_unmodified',control,lifecycle.parent/f'{width}-native-control2600')
        rejected,code=run(width,'old-v1-save',435,load=source.parent/f'{width}-none-330/saved.state')
        checks[f'{width}_old_package_save_rejects']=code==8 and b'loaded_state=' not in (rejected/'run.log').read_bytes()
    paths=[Path(__file__),build,source,lifecycle,manifest,native,ROOT/'engine/runner/pride/final/pride_final_runtime.inc']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,timing=timings,
        scope='Installed title decoding only; sound upload and native intro/input remain open',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True);assert all(checks.values())

if __name__=='__main__':main()
