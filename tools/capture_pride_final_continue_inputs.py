"""Exercise original-style Continue edge handling in the isolated scene controller."""
import csv
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import pixels


def pad(name,age):
    if name=='early-tap':return 0x8200 if age==89 else 0
    if name=='early-release':return 0x8200 if 70<=age<=110 else 0
    if name=='held-through':return 0x8200 if 70<=age<=150 else 0
    if name.startswith('edge-'):return 0x8000 if age==int(name.split('-')[1]) else 0
    if name=='after-fade':return 0x200 if 122<=age<=127 else (0x8000 if 130<=age<=133 else 0)
    return 0


def main():
    base=ROOT/'build/pride-final-input-probe2';out=base/'continue';out.mkdir()
    build=bound(base/'build-report.json');binary=base/'player.exe';assert digest(binary)==build['binary_sha256']
    fixture_path=ROOT/'build/pride-final-continue-fixture/report.json';fixture=bound(fixture_path)
    state=fixture_path.parent/'prefatal.state';identity=digest(state);fatal=fixture['fatal_field']
    original=(fixture_path.parent/'neutral-after-final.tape').read_bytes()
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    commands=[];observations={};checks={}
    for name in ('neutral','early-tap','early-release','held-through','edge-123','edge-124','after-fade'):
        folder=out/name;folder.mkdir();end=800 if name=='after-fade' else 180
        suffix=[pad(name,n) for n in range(1,end+1)]
        tape=folder/'input.tape';tape.write_bytes(original[:fatal*2]+struct.pack('<'+'H'*len(suffix),*suffix))
        env=dict(clean,TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),TLK_FINAL_INPUT_LOG=str(folder/'input.csv'),
            TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',TLK_FINAL_SCENE_PRESENT='1',
            TLK_AUDIO_EVENTS=str(folder/'audio-events.csv'))
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--config',config,'--load',state,'--input',tape,'--lle','--frames',fatal+end,
             '--no-pace','--no-audio','--no-record','--dump-window',folder/'window.png','--dump-scene',folder/'scene.json',
             '--wav',folder/'audio.wav','--wav-seconds',120]
        commands.append(list(map(str,cmd)))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(commands[-1],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
        rows=list(csv.DictReader((folder/'input.csv').open()));events=list(csv.DictReader((folder/'points.csv').open()))
        accepted=[int(r['field'])-fatal for r in events if r['pc']=='c08dc8']
        decisions=[dict(age=int(r['age']),pad=r['pad5a'],choice=int(r['choice']),credits=int(r['credits'])) for r in rows if r['kind']=='decision']
        scene=json.loads((folder/'scene.json').read_text())
        observations[name]=dict(accepted=accepted,decisions=decisions,final=scene['latched_gameplay'])
        checks[name+'/no_decision_before_124']=all(r['age']>=124 for r in decisions)
        print(name,'accepted',accepted,'first decisions',decisions[:2],'final',scene['latched_gameplay'],flush=True)
    checks['source_snapshot_unchanged']=digest(state)==identity
    paths=[Path(__file__),base/'build-report.json',binary,fixture_path,state]
    report=dict(result='OBSERVED' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
        public_player_changed=False,interpreter_native_art_only=True,input_fidelity_requires_comparison=True,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],'Continue input captures',flush=True)
    assert all(checks.values()),checks


if __name__=='__main__':main()
