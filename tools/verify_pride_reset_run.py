"""Compare complete native fields/PCM/windows after soft reset and reinit."""
import argparse
import json
import os
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_windows import hashes,pixels


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--host',choices=('headless','sdl'),required=True);args=p.parse_args()
    base=ROOT/'build/pride-reset/views';build_path=base/'build-report.json';build=bound(build_path);binary=base/(args.host+'-reset.exe')
    assert digest(binary)==build['runs'][args.host]['binary_sha256']
    out=base/'matrix'/args.host;out.mkdir(parents=True);profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape';commands={};checks={};observations={}
    def run(kind,mode,warm):
        name=f'{kind}-{mode}-{warm}';folder=out/name;folder.mkdir()
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--resource-profile',profile,'--input',tape,'--frames',3000,'--dump-png',folder/'guest.png','--ram-log',folder/'route.ram']
        if args.host=='sdl':
            cmd=cmd[:cmd.index('--ram-log')]
            config=folder/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
            cmd+=['--config',config,'--no-pace','--no-audio','--no-record','--dump-window',folder/'window.png','--wav',folder/'audio.wav','--wav-seconds',100]
        else:cmd+=['--wide',256,'--wide-png',folder/'picture.png']
        if mode=='lle':cmd+=['--lle']
        env=os.environ.copy();env.pop('TLK_RESET_ONLY',None)
        env.update(TLK_RESET_PROBE=str(folder),TLK_RESET_KIND=kind,TLK_RESET_WARM=str(warm))
        commands[name]=list(map(str,cmd))
        with (folder/'run.log').open('wb') as log:
            r=subprocess.run(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
        assert r.returncode==0,(name,r.returncode)
        observations[name]=json.loads((folder/'boundary.json').read_text())
        print(args.host,name,'exit0',flush=True);return folder
    from verify_pride_audio_state import wav_data
    pcm=lambda folder:wav_data(folder/'audio.wav') if args.host=='sdl' else (folder/'native.pcm').read_bytes()
    controls={mode:run('none',mode,0) for mode in ('aot','lle')}
    checks['control_modes_guest']=hashes(controls['aot']/'run.log')==hashes(controls['lle']/'run.log')
    checks['control_modes_every_field']=digest(controls['aot']/'native-fields.csv')==digest(controls['lle']/'native-fields.csv')
    checks['control_modes_pcm']=pcm(controls['aot'])==pcm(controls['lle'])
    picture='window.png' if args.host=='sdl' else 'picture.png'
    checks['control_modes_picture']=pixels(controls['aot']/picture)==pixels(controls['lle']/picture)
    for kind in ('soft','init'):
        for mode in ('aot','lle'):
            for warm in (1,1211):
                folder=run(kind,mode,warm);reference=controls[mode];name=folder.name;b=observations[name]
                checks[name+'/fresh_boundary']=b['frame_after']==b['pc_after']==b['pending_after']==b['remainder_after']==0
                checks[name+'/guest']=hashes(folder/'run.log')==hashes(reference/'run.log')
                checks[name+'/every_native_field']=digest(folder/'native-fields.csv')==digest(reference/'native-fields.csv')
                checks[name+'/complete_pcm']=pcm(folder)==pcm(reference)
                checks[name+'/picture']=pixels(folder/picture)==pixels(reference/picture)
                if args.host=='headless':checks[name+'/tracked_ram']=digest(folder/'route.ram')==digest(reference/'route.ram')
    paths=(Path(__file__),build_path,tape,ROOT/'tools/verify_windows.py',ROOT/'tools/verify_pride_audio_state.py')
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,host=args.host,observations=observations,
        binary_sha256=digest(binary),commands=commands,source_sha256={str(q.relative_to(ROOT)).replace('\\','/'):digest(q) for q in paths},
        artifacts_sha256={str(q.relative_to(out)).replace('\\','/'):digest(q) for q in out.rglob('*') if q.is_file() and q.name!='report.json'},
        selected_md_audio_reset_verified=False,private_revival_reset_verified=False,public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(args.host,report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()
