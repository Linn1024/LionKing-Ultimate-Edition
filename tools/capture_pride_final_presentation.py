"""Capture final-life display phases using ordinary input and real windows.

This is presentation evidence, not a final-life runtime implementation. Original
MD follows the established life-exhaustion route; the preview uses its credited
hard-mode route and neutral input after the fatal hit.
"""
import argparse
import ctypes as C
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


OFFSETS=(0,4,8,12,16,20,24,32,48,64,80,88,92,96,100,104,112,120,144,160,224,344,436)


def original(out):
    from md_lab import MdLab,png
    source=ROOT/'build/md-next-levels-replay/frames.json';inputs=json.loads(source.read_text())
    reference_path=ROOT/'build/pride-game-over-original/report.json';reference=json.loads(reference_path.read_text())
    assert reference['result']=='PASS';fatal=reference['final_life_field']
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    captures=[]
    try:
        for field in range(1,fatal+max(OFFSETS)+1):
            game.step(inputs[field-1]['pad'] if field<=4000 else (128 if field>5400 and field<=fatal else 0))
            game.samples.clear()
            if field-fatal not in OFFSETS:continue
            word=lambda at:game.work_ram[at]|game.work_ram[at+1]<<8
            png(out/f'{field-fatal:03d}.png',*game.image)
            (out/f'{field-fatal:03d}-wram.bin').write_bytes(bytes(game.work_ram))
            captures.append(dict(offset=field-fatal,field=field,health=word(0xccf6),lives=word(0xccee),level=word(0xccce)))
    finally:game.close()
    assert captures[0]['health']==0 and captures[0]['lives']==0
    return dict(fatal_field=fatal,captures=captures,ordinary_power_on=True),[source,reference_path,ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']


def preview(out):
    binary=ROOT/'build/pride-arena-work/tlk_pride_player.exe'
    source=ROOT/'build/pride-game-over-music/hard.tape';fatal=2369
    tape=out/'ordinary.tape';tape.write_bytes(source.read_bytes()[:fatal*2]+bytes((max(OFFSETS)+1)*2))
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    state=out/'prefatal.state';commands=[];captures=[]
    for field in (fatal-1,*[fatal+n for n in OFFSETS]):
        folder=out/str(field-fatal);folder.mkdir()
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--config',config,'--input',tape,'--frames',field,'--no-pace','--no-audio','--no-record',
             '--dump-window',folder/'window.png','--dump-scene',folder/'scene.json']
        if field<fatal:cmd+=['--save-at',field,state]
        else:cmd+=['--load',state]
        commands.append(list(map(str,cmd)))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(commands[-1],cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        scene=json.loads((folder/'scene.json').read_text())
        captures.append(dict(offset=field-fatal,gameplay=scene['latched_gameplay'],stage=scene['stage_detected']))
        print('Preview final offset',field-fatal,flush=True)
    assert captures[0]['gameplay']['health']==1 and captures[1]['gameplay']['health']==0 and captures[1]['gameplay']['lives']==0
    return dict(fatal_field=fatal,captures=captures,commands=commands,unmodified_prefatal_save=True),[binary,source]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',choices=('md','preview'));args=parser.parse_args()
    out=ROOT/'build/pride-final-presentation'/args.source;out.mkdir(parents=True)
    data,paths=original(out) if args.source=='md' else preview(out)
    paths += [Path(__file__),ROOT/'Lion King, The (USA).sfc',ROOT/'Lion King, The (World).md']
    report=dict(result='CAPTURED',source=args.source,**data,final_life_adapter_implemented=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(args.source,'final-life presentation captured',flush=True)


if __name__=='__main__':main()
