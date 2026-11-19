"""Compare real first/early loaded clients against ordinary gameplay startup."""
import argparse
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_pride_audio_state import wav_data
from verify_pride_live_error_ui import environment,read_rows
from verify_windows import hashes,pixels


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',choices=('native','md'),default='native');args=p.parse_args()
    base=ROOT/'build/pride-practice';out=base/'verified/first-loaded'/args.case;out.mkdir(parents=True,exist_ok=True)
    assert not (out/'report.json').exists(),'Use a fresh capture directory'
    name='md-lle' if args.case=='md' else 'native-aot';save='lle' if args.case=='md' else 'aot';load='aot' if args.case=='md' else 'lle'
    author=base/'verified/normal-ui'/name;author_path=author/'report.json';r=json.loads(author_path.read_text());assert r['result']=='PASS'
    state=author/'automatic-original.state';saved=r['observations']['automatic_saved_field']
    build_path=base/'build-report.json';build=json.loads(build_path.read_text());binary=base/'practice-sdl.exe'
    for path,sha in build['source_sha256'].items():assert digest(ROOT/path)==sha,path
    assert digest(binary)==build['runs']['sdl']['binary_sha256']
    profile=out/'resources.ini';profile.write_bytes((author/'resources.ini').read_bytes())
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape';commands={};checks={};pixels_checked=0
    for offset in (1,8):
        folders=[]
        for name,mode in (('control',save),('resumed',load)):
            folder=out/f'{offset}-{name}';folder.mkdir(exist_ok=True);folders.append(folder)
            config=folder/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
            cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                '--resource-profile',profile,'--config',config,'--input',tape,'--frames',saved+offset,'--no-pace',
                '--no-audio','--no-record','--dump-window',folder/'window.png','--dump-png',folder/'guest.png',
                '--wav',folder/'audio.wav','--wav-seconds',100]
            if name=='resumed':cmd+=['--load',state]
            if mode=='lle':cmd+=['--lle']
            commands[f'{offset}-{name}']=list(map(str,cmd))
            with (folder/'run.log').open('wb') as log:
                result=subprocess.run(commands[f'{offset}-{name}'],cwd=ROOT,env=environment(folder),stdout=log,stderr=subprocess.STDOUT,timeout=120)
            assert not result.returncode,(offset,name,result.returncode)
        a,b=folders
        checks[f'{offset}/guest']=hashes(a/'run.log')==hashes(b/'run.log')
        control=pixels(a/'window.png');loaded=pixels(b/'window.png')
        checks[f'{offset}/whole_client']=control==loaded;pixels_checked+=control[0]*control[1]
        rows=[row for row in read_rows(a/'practice-fields.csv') if int(row['field'])==saved+1];assert len(rows)==1
        cut=int(rows[0]['wav_frames_before_audio'])*4
        checks[f'{offset}/pcm']=wav_data(a/'audio.wav')[cut:]==wav_data(b/'audio.wav')
    paths=(Path(__file__),build_path,author_path,state,tape,ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_pride_live_error_ui.py')
    result=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,case=args.case,saved_field=saved,
        pixels_compared=pixels_checked,binary_sha256=digest(binary),source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
        commands=commands,artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(args.case,result['result'],checks,flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
