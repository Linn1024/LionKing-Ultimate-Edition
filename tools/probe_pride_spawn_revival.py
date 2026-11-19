"""Capture independently selected initial position through revival.

No loaded states or guest edits manufacture this route. Timing adapters remain
excluded from the installed player; source/profile/save lifecycle is still open.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_prepared_state import rows
from verify_windows import hashes


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline',action='store_true')
    parser.add_argument('--start',choices=('snes','md'),default='md')
    parser.add_argument('--width',type=int,choices=(256,320),default=256)
    parser.add_argument('--graphics',choices=('native','frames','palette','all'),default='native')
    parser.add_argument('--execution',choices=('aot','lle'),default='lle')
    parser.add_argument('--presenter',choices=('owned','native'),default='owned')
    parser.add_argument('--sdl',action='store_true')
    parser.add_argument('--route',choices=('default','checkpoint'),default='default')
    parser.add_argument('--frames',type=int)
    parser.add_argument('--output-root',type=Path,default=Path('build/pride-spawn-revival/pilot'))
    args=parser.parse_args();args.frames=args.frames or (5400 if args.route=='checkpoint' else 3000)
    base=ROOT/('build/pride-grounded' if args.baseline else 'build/pride-spawn-revival');out=ROOT/args.output_root;out.mkdir(parents=True,exist_ok=True)
    build_path=base/'build-report.json';build=json.loads(build_path.read_text())
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    prefix='grounded' if args.baseline else 'spawn-revival'
    binary=base/f'{prefix}-{"sdl" if args.sdl else "probe"}.exe'
    assert digest(binary)==build['runs']['sdl' if args.sdl else 'probe']['binary_sha256']
    source=ROOT/('build/pride-health-death-native/neutral-tail.polled.tape' if args.route=='checkpoint' else 'build/pride-game-over-music/normal.tape')
    tape=out/('checkpoint.polled.tape' if args.route=='checkpoint' else 'default-neutral.tape')
    tape.write_bytes(source.read_bytes() if args.route=='checkpoint' else source.read_bytes()[:1669*2]+bytes(max(0,args.frames-1669)*2))
    profile=out/'resources.ini'
    settings='schema = 1\ngame = snes\ndisplay.viewport = '+('md' if args.width==320 else 'snes')+'\n'
    settings+='gameplay.levels.pride_lands.start = '+args.start+'\n'
    if args.graphics=='all':settings+='graphics.scenery = md\ngraphics.sprites.simba.cub = md\ngraphics.hud = md\ngraphics.sprites.enemies.hyenas = md\ngraphics.sprites.enemies.other = md\ngraphics.sprites.pickups = md\ngraphics.sprites.leaves = md\ngraphics.sprites.effects.defeat_puff = md\n'
    if args.graphics in ('frames','palette'):settings+='graphics.sprites.simba.cub.'+args.graphics+' = md\n'
    profile.write_text(settings+'graphics.sprites.checkpoints.frames = md\ngraphics.sprites.checkpoints.palette = md\n')
    env=os.environ.copy();env['TLK_START_TRACE']=str(out/'start.csv')
    for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE','TLK_SCENE_RENDER_PROBE'):env[key]=str(out)
    for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE',
                'TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO','TLK_SCENE_RENDER_ENABLE'):env[key]='1'
    env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_NATIVE_BANK_RECORD',None)
    env['TLK_SCENE_RENDER_ENABLE']=str(int(args.presenter=='owned'))
    command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--frames',args.frames,'--input-polled' if args.route=='checkpoint' else '--input',tape]
    if args.execution=='lle':command.append('--lle')
    if args.sdl:
        config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
        command+=['--config',config,'--no-pace','--no-audio','--no-record','--dump-window',out/'window.png',
                  '--wav',out/'audio.wav','--wav-seconds','100']
    else:command+=['--wide',args.width,'--ram-log',out/'route.ram','--wide-png',out/'picture.png']
    with (out/'run.log').open('wb') as log:
        run=subprocess.run(list(map(str,command)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
    result=dict(result='AUDITED',scope=__doc__,exit_code=run.returncode,width=args.width,graphics=args.graphics,
        execution=args.execution,start_source=args.start,baseline=args.baseline,host='sdl' if args.sdl else 'probe',frames=args.frames,
        presenter=args.presenter,
        route=args.route,loaded_states=False,guest_fixture_edits=False,
        binary_sha256=digest(binary),source_sha256={str(build_path.relative_to(ROOT)).replace('\\','/'):digest(build_path),
            'tools/probe_pride_spawn_revival.py':digest(Path(__file__)),
            str(source.relative_to(ROOT)).replace('\\','/'):digest(source)},
        guest=hashes(out/'run.log'),artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!='report.json'},
        default_actor_player_enabled=False,default_revival_save_verified=False,full_first_level_fidelity_complete=False)
    if (out/'owner-events.csv').exists():
        events=rows(out/'owner-events.csv');result['owner_event_boundaries']=[{k:r[k] for k in ('event','field','age')} for r in events if r['event'] not in ('hold_call','hold_return')]
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(args.width,args.graphics,args.execution,result['host'],'exit',run.returncode,flush=True)
    if run.returncode:raise SystemExit(run.returncode)


if __name__=='__main__':main()
