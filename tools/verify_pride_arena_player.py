"""Exercise the maintained arena repair across widths and independent sources."""
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
from verify_windows import hashes,pixels
from verify_pride_audio_state import wav_data


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--resume',action='store_true');args=parser.parse_args()
    base=ROOT/'build/pride-arena-work';out=base/'player-check';out.mkdir(exist_ok=args.resume)
    assert not (out/'report.json').exists()
    binary=base/'tlk_pride_player.exe';build=json.loads((base/'build-report.json').read_text())
    assert digest(binary)==build['binary_sha256']
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    previous=ROOT/'build/pride-title-work/player/native-engine/tlk_pride_player.exe'
    assert digest(previous)=='fdc9df37db7c912f39c0c6484441e057f066259564655e03f67f28a39fa17f9e'
    tape=ROOT/'build/pride-checkpoint-revival/snes/revival.polled.tape'
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    native='schema = 1\ngame = snes\ngameplay.levels.pride_lands.health_death = md\n'
    profile=out/'preceding.ini';profile.write_text(native+'display.viewport = md\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    commands=[];checks={};observations={}
    def run(exe,folder,profile,field,extra=(),env=None):
        cmd=[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--config',config,'--resource-profile',profile,'--input-polled',tape,'--frames',field,
             '--no-pace','--no-audio','--no-record','--dump-window',folder/'window.png','--dump-scene',folder/'scene.json',*extra]
        commands.append(list(map(str,cmd)))
        if not (args.resume and (folder/'scene.json').exists() and 'wram_sha256=' in (folder/'run.log').read_text()):
            with (folder/'run.log').open('wb') as log:
                subprocess.run(commands[-1],cwd=ROOT,env=env or clean,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
        text=(folder/'run.log').read_text()
        assert 'Saved resource profile loaded' in text and 'Profile rejected' not in text
        return json.loads((folder/'scene.json').read_text())
    old=out/'preceding';old.mkdir(exist_ok=args.resume);state=old/'arena-4400.state'
    scene=run(previous,old,profile,4400,['--save-at',4400,state])
    checks['preceding_public_save_in_arena']=scene['latched_gameplay']['descriptor']==0x80d and scene['latched_gameplay']['health']==1
    identity=digest(state)
    template=(ROOT/'build/pride-scene-template-work/player/owned-regression/mixed.ini').read_text()
    template=template.replace('gameplay.levels.pride_lands.start = md','gameplay.levels.pride_lands.start = snes')
    cases=[(256,'snes','snes','aot'),(320,'snes','md','aot'),(256,'md','snes','aot'),(320,'md','md','aot'),(320,'md','md','lle')]
    for width,graphics,audio,mode in cases:
        name=f'{width}-{graphics}-{audio}-{mode}';folder=out/name;folder.mkdir(exist_ok=args.resume)
        settings=template if graphics=='md' else native
        settings+=f'\ndisplay.viewport = {"md" if width==320 else "snes"}\naudio.music.pride_health_death = {audio}\ngraphics.titles.pride_lands = {graphics}\n'
        profile=folder/'resources.ini';profile.write_text(settings)
        env=dict(clean,TLK_PRIDE_DIAGNOSTICS=str(folder))
        extra=['--load',state,'--wav',folder/'audio.wav','--wav-seconds','120']+(['--lle'] if mode=='lle' else [])
        scene=run(binary,folder,profile,4778,extra,env)
        game=scene['latched_gameplay'];events=list(csv.DictReader((folder/'owner-events.csv').open()))
        rows=list(csv.DictReader((folder/'owner-fields.csv').open()))
        checks[name+'/owned_arena_entry']=any(r['event']=='begin' and r['field']=='4430' for r in events)
        checks[name+'/normal_345']=any(r['event']=='normal' and r['field']=='4775' and r['age']=='345' for r in events)
        checks[name+'/health_270']=all(int(r['native_health'])==0 for r in rows if int(r['age'])<270) and any(r['age']=='270' and r['native_health']=='6' for r in rows)
        checks[name+'/checkpoint_return']=game['player']==[1200,111] and game['health']==6 and game['lives']==7
        checks[name+'/actual_width']=pixels(folder/'window.png')[0:2]==(width*2,448)
        evidence=list(folder.rglob('scenery-evidence.json'));assert len(evidence)==1,evidence
        scenery=json.loads(evidence[0].read_text())
        checks[name+'/arena_background_recipe']=scenery['latched_gameplay']['descriptor']==0x80d and scenery['stage_detected']
        observations[name]=dict(gameplay=game,hashes=hashes(folder/'run.log'),scenery_camera=scenery['camera'])
        print(name,'arena revival/checkpoint capture',flush=True)
    a=out/'320-md-md-aot';b=out/'320-md-md-lle'
    checks['both_modes_same_view']=pixels(a/'window.png')==pixels(b/'window.png')
    checks['both_modes_same_audio']=wav_data(a/'audio.wav')==wav_data(b/'audio.wav')
    checks['both_modes_same_gameplay']=hashes(a/'run.log')==hashes(b/'run.log')
    checks['old_save_unchanged']=digest(state)==identity
    checks['previous_binary_unchanged']=digest(previous)=='fdc9df37db7c912f39c0c6484441e057f066259564655e03f67f28a39fa17f9e'
    paths=[Path(__file__),base/'build-report.json',binary,previous,tape]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},
        full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'maintained arena checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()
