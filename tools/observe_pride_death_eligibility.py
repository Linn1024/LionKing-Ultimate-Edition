"""Observe actual death entry guards with an isolated copy of the current host.

Changes only diagnostic output; existing game objects and the public player stay
unchanged. Captures are research artifacts under build/.
"""
import json
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv, digest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--allow-arena',action='store_true')
    args=parser.parse_args()
    out=ROOT/('build/pride-arena-revival-probe2' if args.allow_arena else 'build/pride-death-entry-observer2');out.mkdir()
    build=ROOT/'build/pride-title-work/player'
    public=build/'native-engine/tlk_pride_player.exe';identity=digest(public)
    source=out/'pride';shutil.copytree(ROOT/'engine/runner/pride',source)
    owner=source/'pride_repeat_owner.c';text=owner.read_text()
    if args.allow_arena:
        guard='ol(0xdf)==0xc00387'
        assert text.count(guard)==1
        text=text.replace(guard,'(ol(0xdf)==0xc00387 || ol(0xdf)==0xc0080d)')
    anchor='        if(!PrideRepeatEligible())return;'
    assert text.count(anchor)==1
    text=text.replace(anchor,'''        fprintf(stderr,"death_entry field=%u eligible=%d level=%u cub=%u health=%u skip=%u final=%u lives=%u descriptor=%06x state=%06x checkpoint=%u/%u\\n",
            (unsigned)snes_frame_counter+1,PrideRepeatEligible(),ow(0x1ff9e),ow(0x2000),ow(0x2004),ow(0xa6ba),ow(0x1ff90),ow(0x1ffaa),ol(0xdf),ol(0xb243),ow(0x1ffa4),ow(0x1ffa6));
'''+anchor)
    owner.write_text(text)
    probe=source/'pride_practice_probe.c';text=probe.read_text()
    anchor='    practice_frame_complete();'
    assert text.count(anchor)==1
    text=text.replace(anchor,anchor+'''
    static unsigned diagnostic_state=~0u,diagnostic_health=~0u;
    if(ow(0x2004)!=diagnostic_health || ol(0xb243)!=diagnostic_state) {
        diagnostic_health=ow(0x2004);diagnostic_state=ol(0xb243);
        if(snes_frame_counter>4000)fprintf(stderr,"actor_transition field=%u health=%u state=%06x lives=%u xy=%u/%u\\n",
            (unsigned)snes_frame_counter,diagnostic_health,diagnostic_state,ow(0x1ffaa),ow(0xb21b),ow(0xb21d));
    }
''')
    probe.write_text(text)
    ninja='C:/mingw32/bin/ninja.exe'
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=build))
    entry=next(r for r in db if r.get('file','').endswith('/pride/tlk_pride_host.c'))
    command=argv(entry['command']);obj=out/'observer.obj'
    for flag,value in [('-c',source/'tlk_pride_host.c'),('-o',obj),('-MF',out/'observer.d'),('-MT',obj)]:
        command[command.index(flag)+1]=str(value)
    with (out/'compile.log').open('wb') as log:
        subprocess.run(command,cwd=build,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
    lines=(build/'build.ninja').read_text().splitlines()
    start=next(n for n,s in enumerate(lines) if s.startswith('build native-engine/tlk_pride_player.exe:'))
    objects=lines[start].split(': ',1)[1].split(' ',1)[1].split(' |')[0].split()
    assert objects.count(entry['output'])==1
    objects[objects.index(entry['output'])]=obj.as_posix()
    libraries=next(s.split(' = ',1)[1] for s in lines[start+1:] if s.startswith('  LINK_LIBRARIES ='))
    link_args=objects+argv('link '+libraries)[1:]
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(link_args))
    binary=out/'observer.exe'
    link=['C:/mingw32/bin/g++.exe','-O3','-static',
          '-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine',
          '@'+str(rsp),'-o',str(binary)]
    with (out/'link.log').open('wb') as log:
        subprocess.run(link,cwd=build,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    shutil.copyfile(build/'native-engine/genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
    results={}
    for name,tape in [('checkpoint-early','build/pride-checkpoint-revival/snes/revival.polled.tape'),
                      ('checkpoint-reviewed','build/pride-health-death-native/neutral-tail.polled.tape')]:
        folder=out/name;folder.mkdir()
        profile=folder/'resources.ini';profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\ngameplay.levels.pride_lands.health_death = md\n')
        config=folder/'host.ini';config.write_text('opengl=0\nscale=3\n')
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--config',config,'--resource-profile',profile,'--input-polled',ROOT/tape,
             '--frames','5400','--no-pace','--no-audio','--no-record','--dump-window',folder/'window.png',
             '--dump-scene',folder/'scene.json']
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
        if args.allow_arena:
            env['TLK_PRIDE_DIAGNOSTICS']=str(folder)
            cmd+=['--save-at','4440',folder/'during.state']
        with (folder/'run.log').open('wb') as log:
            subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
        log_text=(folder/'run.log').read_text()
        assert 'Saved resource profile loaded' in log_text and 'Profile rejected' not in log_text
        results[name]=[s for s in log_text.splitlines() if s.startswith(('death_entry ','actor_transition '))]
        print(name,results[name],flush=True)
        if args.allow_arena:break
    assert digest(public)==identity
    paths=[Path(__file__),ROOT/'engine/runner/pride/pride_repeat_owner.c',ROOT/'engine/runner/pride/tlk_pride_host.c',public]
    report=dict(result='OBSERVED',public_player_unchanged=True,arena_guard_enabled=args.allow_arena,observations=results,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
