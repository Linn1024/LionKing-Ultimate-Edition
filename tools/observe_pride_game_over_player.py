"""Observe Game Over controls in the Windows development player."""
import argparse
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--player',default='build/pride-final-native-player11')
    parser.add_argument('--output',default='build/pride-game-over-exits-baseline');args=parser.parse_args()
    base=ROOT/args.player;build=base/'build-report.json';bound(build)
    source=ROOT/'build/pride-final-arena-fixture/report.json';fixture=bound(source);fatal=fixture['fatal_field']
    prepared=ROOT/'build/pride-final-native-installed/actual install';manifest=prepared/'install.json';info=json.loads(manifest.read_text())
    out=ROOT/args.output;out.mkdir();commands={};rows={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    (out/'resources.ini').write_text('schema = 1\ngame = snes\ngameplay.levels.pride_lands.health_death = md\ngameplay.levels.pride_lands.final_life = md\ndisplay.viewport = md\n')
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_FINAL_MD_ART']='1'
    for name,pressed,end in [('a100',100,180),('a123',123,180),('a124',124,180),('a140',140,180),('none350',None,350),('none400',None,400),('none700',None,700)]:
        folder=out/name;folder.mkdir();raw=bytearray(6000*2);struct.pack_into('<H',raw,(fatal-1)*2,0x200)
        if pressed is not None:struct.pack_into('<H',raw,(fatal+pressed-1)*2,0x8000)
        tape=folder/'input.tape';tape.write_bytes(raw)
        cmd=fixture['commands']['control0'].copy();cmd[0]=str(base/'player.exe');at=cmd.index('--input-polled');del cmd[at:at+2]
        cmd+=['--input',str(tape),'--final-menu-assets',str(prepared/info['menu_assets']['file']),
            '--final-native-assets',str(prepared/info['native_final_assets']['file']),'--wav',str(folder/'audio.wav')]
        for flag,value in [('--resource-profile',out/'resources.ini'),('--config',out/'host.ini'),('--frames',fatal+end),
            ('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json')]:cmd[cmd.index(flag)+1]=str(value)
        actual=dict(env,TLK_CONTINUE_EXIT_LOG=str(folder/'exit.csv'),TLK_FINAL_INPUT_LOG=str(folder/'input.csv'))
        with (folder/'run.log').open('wb') as log:result=subprocess.run(cmd,cwd=ROOT,env=actual,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[name]=cmd;row=dict(pressed_age=pressed,age=end,exit_code=result.returncode)
        if (folder/'window.png').exists():
            w,h,image=pixels(folder/'window.png');row['lit_pixels']=sum(c!=(0,0,0) for c in image)
            row['guest']=json.loads((folder/'scene.json').read_text())['latched_gameplay']
        rows[name]=row;print(name,row,flush=True)
    paths=[Path(__file__),build,source,manifest]
    report=dict(result='OBSERVED',rows=rows,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
