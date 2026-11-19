"""Verify actual Windows pixels during owned death display and revival fade."""
import array
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
from audit_scenes import ROOT
from verify_windows import pixels,hashes


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared',action='store_true');parser.add_argument('--width',type=int,choices=(256,320),default=320)
    parser.add_argument('--revival-roar',choices=('snes','md'),default='snes')
    parser.add_argument('--checkpoint',choices=('native','frames','palette','both'))
    parser.add_argument('--binary',type=Path)
    parser.add_argument('--execution',choices=('lle','aot'),default='lle')
    parser.add_argument('--output-root',type=Path)
    args=parser.parse_args();w=args.width
    suffix=('-checkpoint-'+args.checkpoint if args.checkpoint else '')+('-roar-md' if args.revival_roar=='md' else '')
    out=ROOT/args.output_root if args.output_root else ROOT/((f'build/pride-scene-prepared-windows-{w}' if args.prepared else 'build/pride-scene-render-windows')+suffix)
    out.mkdir(parents=True,exist_ok=True)
    report=out/'report.json';report.write_text('{"result":"RUNNING"}\n')
    binary=ROOT/args.binary if args.binary else ROOT/f'engine/build-win/tlk_scene_{"prepared" if args.prepared else "render"}_sdl.exe';identity=digest(binary)
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    results={}
    for profile in ('native','all'):
        phases=[('display',4500),('revival',4703)]
        if args.revival_roar=='md':phases.append(('ready',4775))
        for phase,end in phases:
            case=profile+'-'+phase;folder=out/case;folder.mkdir(exist_ok=True)
            family='scene-render-prepared' if args.prepared else 'scene-render'
            resource=ROOT/f'build/pride-{family}-sdl-{w}-5400/{profile}-owned/resources.ini'
            if args.checkpoint or args.revival_roar=='md':
                resource=folder/'resources.ini'
                settings='schema = 1\ngame = snes\ndisplay.viewport = '+('md' if w==320 else 'snes')+'\n'
                if profile=='all':settings+='graphics.scenery = md\ngraphics.sprites.simba.cub = md\ngraphics.hud = md\ngraphics.sprites.enemies.hyenas = md\ngraphics.sprites.enemies.other = md\ngraphics.sprites.pickups = md\ngraphics.sprites.leaves = md\ngraphics.sprites.effects.defeat_puff = md\n'
                if args.checkpoint:
                    settings+='graphics.sprites.checkpoints.frames = '+('md' if args.checkpoint in ('frames','both') else 'snes')+'\n'
                    settings+='graphics.sprites.checkpoints.palette = '+('md' if args.checkpoint in ('palette','both') else 'snes')+'\n'
                resource.write_text(settings)
            assert resource.is_file()
            env=os.environ.copy()
            for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE','TLK_SCENE_RENDER_PROBE'):env[key]=str(folder)
            for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE','TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RENDER_ENABLE'):env[key]='1'
            env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md')
            env['TLK_SCENE_RESTORE_ROAR_ZERO']=str(int(args.revival_roar=='md'))
            cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                 '--resource-profile',resource,'--config',config,'--frames',end,'--no-pace','--no-audio','--no-record',
                 '--input-polled',ROOT/'build/pride-health-death-native/neutral-tail.polled.tape',
                 '--save-at',end,folder/'snapshot.state','--dump-window',folder/'window.png']
            if args.execution=='lle':cmd.append('--lle')
            with (folder/'run.log').open('wb') as log:
                subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
            count=w*224;size=56+count*12;previous=None;duplicates=0;last_age=-1
            with (folder/'render-owned.rgb').open('rb') as f:
                assert f.read(16)==b'PRDRGB01'+struct.pack('<II',w,224)
                while record:=f.read(size):
                    assert len(record)==size
                    age=struct.unpack_from('<I',record)[0]
                    if age==last_age:
                        assert record==previous,'Repeated presentation changed owned pixels'
                        duplicates+=1
                    else:assert age==last_age+1
                    last_age=age;previous=record
            assert last_age==end-4430
            final=array.array('I');final.frombytes(previous[-count*4:])
            width,height,window=pixels(folder/'window.png');assert (width,height)==(w*2,448)
            for y in range(height):
                for x in range(width):
                    value=final[(y//2)*w+x//2]
                    assert window[y*width+x]==(value>>16&255,value>>8&255,value&255),(case,x,y)
            assert any(final)
            results[case]=dict(controller_age=last_age,actual_window_matches_owned_pixels=True,
                guest=hashes(folder/'run.log'),
                exact_window_pixels=width*height,identical_duplicate_presentations=duplicates,
                artifacts_sha256={p.name:digest(p) for p in sorted(folder.iterdir()) if p.is_file()})
            print(case,'actual Windows client exactly matches owned frame; duplicate presentation stable PASS',flush=True)
    assert digest(binary)==identity
    report.write_text(json.dumps(dict(result='PASS',scope=__doc__,probe_sha256=identity,runs=results,
        production_behavior_enabled=False,full_first_level_fidelity_complete=False,
        prepared_objects=args.prepared,width=w,
        execution=args.execution,
        revival_roar_source=args.revival_roar,checkpoint_sources=args.checkpoint,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in
            (Path(__file__),ROOT/'tools/pride_scene_render_wide.c',ROOT/'tools/pride_scene_prepared_objects.c',
             ROOT/'engine/runner/tlk_native_hud.c',ROOT/'engine/runner/tlk_native_hud.h',ROOT/'tools/pride_scene_render_probe.c',
             ROOT/'tools/pride_scene_render_bridge.h',ROOT/'tools/pride_scene_restore_probe.c',
             ROOT/'engine/runner/tlk_checkpoint_art.c',ROOT/'engine/runner/tlk_checkpoint_role.h',
             ROOT/'engine/runner/tlk_resources.c',ROOT/'engine/runner/tlk_revival_art.c')}),indent=2)+'\n')


if __name__=='__main__':main()
