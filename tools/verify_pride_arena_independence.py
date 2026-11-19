"""Check arena music selection and preserve the preceding default revival."""
import csv
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
    base=ROOT/'build/pride-arena-work';out=base/'independence';out.mkdir()
    binary=base/'tlk_pride_player.exe';commands=[];checks={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    def run(folder,profile,state,tape,flag,field,config,env):
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--config',config,'--resource-profile',profile,'--load',state,flag,tape,'--frames',field,
             '--no-pace','--no-audio','--no-record','--dump-window',folder/'window.png',
             '--wav',folder/'audio.wav','--wav-seconds',120]
        commands.append(list(map(str,cmd)))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(commands[-1],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        assert 'Saved resource profile loaded' in (folder/'run.log').read_text()
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    state=base/'player-check/preceding/arena-4400.state';tape=ROOT/'build/pride-checkpoint-revival/snes/revival.polled.tape'
    for choice in ('snes','md'):
        folder=out/choice;folder.mkdir();profile=folder/'resources.ini'
        profile.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\ngameplay.levels.pride_lands.health_death = md\naudio.music.pride_health_death = '+choice+'\n')
        run(folder,profile,state,tape,'--input-polled',4778,config,dict(clean,TLK_MD_SOUND_COMMANDS=str(folder/'commands.csv')))
        rows=list(csv.DictReader((folder/'commands.csv').open()))
        selected=[r for r in rows if r['selector']=='1' and r['value']=='430']
        checks[choice+'/death_music_selected_independently']=len(selected)==(1 if choice=='md' else 0)
    checks['audio_choice_preserves_gameplay']=hashes(out/'md/run.log')==hashes(out/'snes/run.log')
    checks['audio_choice_preserves_view']=pixels(out/'md/window.png')==pixels(out/'snes/window.png')
    checks['audio_choice_changes_output']=wav_data(out/'md/audio.wav')!=wav_data(out/'snes/audio.wav')
    folder=out/'default';folder.mkdir();reference=ROOT/'build/pride-title-reentry-verified/2170-md'
    state2=ROOT/'build/pride-scene-template-work/player/owned-regression/preceding-owned-2001.state'
    tape2=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape'
    run(folder,reference/'resources.ini',state2,tape2,'--input',2170,reference.parent/'host.ini',clean)
    checks['default_revival_gameplay_preserved']=hashes(folder/'run.log')==hashes(reference/'run.log')
    checks['default_revival_client_preserved']=pixels(folder/'window.png')==pixels(reference/'window.png')
    paths=[Path(__file__),base/'build-report.json',binary,state,state2,tape,tape2]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'music/default revival checks',flush=True)
    assert all(checks.values()),checks


if __name__=='__main__':main()
