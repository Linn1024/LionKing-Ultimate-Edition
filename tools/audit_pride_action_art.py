"""Exercise mapped artwork on ordinary ledge/action continuations in the preview.

Existing snapshots were authored by ordinary play. These finite paths do not
prove universal actor/effect coverage or animation-timing equivalence.
"""
import csv
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import hashes


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--resume',action='store_true');args=parser.parse_args()
    out=ROOT/'build/pride-action-art-current';out.mkdir(exist_ok=args.resume)
    assert not (out/'report.json').exists()
    binary=ROOT/'build/pride-arena-work/tlk_pride_player.exe'
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = snes\n'
        'graphics.sprites.simba.cub = md\ngraphics.sprites.enemies.hyenas = md\n'
        'graphics.sprites.enemies.other = md\ngraphics.sprites.pickups = md\n'
        'graphics.sprites.leaves = md\ngraphics.sprites.effects.defeat_puff = md\n'
        'graphics.sprites.checkpoints = md\ngraphics.sprites.effects.pickup_arrival = md\n')
    fixtures=[('first',ROOT/'build/pride-ledge-physics/snes',1472),
              ('opposite',ROOT/'build/pride-ledge-controlled/playable-opposite/snes',2165)]
    cases=('neutral','right','left','up','down','jump','right-jump','left-jump','roar','roll','reverse','late-jump')
    checks={};observations={};commands=[];sources=[Path(__file__),binary,ROOT/'engine/generated/resources/pride_sprite_map.h']
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    for fixture,origin,start in fixtures:
        state=origin/'ledge.state';identity=digest(state);sources.append(state)
        for case in cases:
            name=fixture+'-'+case;folder=out/name;folder.mkdir(exist_ok=args.resume);tape=origin/(case+'.tape');sources.append(tape)
            reference=origin/(case+('-public' if fixture=='first' else '-public-aot'))/'run.log'
            sources.append(reference)
            cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                 '--config',config,'--resource-profile',profile,'--load',state,'--input',tape,'--frames',start+120,
                 '--no-pace','--no-audio','--no-record','--dump-window',folder/'window.png','--dump-scene',folder/'scene.json']
            commands.append(list(map(str,cmd)))
            env=dict(clean,TLK_SPRITE_REPORT=str(folder/'sprites.json'),TLK_AUDIO_EVENTS=str(folder/'events.csv'))
            if not (args.resume and (folder/'scene.json').exists() and 'wram_sha256=' in (folder/'run.log').read_text()):
                with (folder/'run.log').open('wb') as log:
                    subprocess.run(commands[-1],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
            report=json.loads((folder/'sprites.json').read_text());scene=json.loads((folder/'scene.json').read_text())
            checks[name+'/gameplay_preserved']=hashes(folder/'run.log')==hashes(reference)
            checks[name+'/no_unmapped_requested_cub_art']=not report['missing_poses']
            checks[name+'/no_unmapped_requested_npc_art']=not report['missing_npc_poses']
            checks[name+'/still_pride_scene']=scene['latched_gameplay']['descriptor'] in (0x387,0x80d) and scene['level']==0
            observations[name]=dict(coverage=report,scene=scene['latched_gameplay'],audio_events=list(csv.DictReader((folder/'events.csv').open())))
            print(name,'cub',report['seen_by_role']['cub'],'missing',report['missing_poses'],report['missing_npc_poses'],flush=True)
        checks[fixture+'/original_snapshot_unchanged']=digest(state)==identity
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in set(sources)},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
        universal_artwork_or_timing_coverage_proven=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'action artwork checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
