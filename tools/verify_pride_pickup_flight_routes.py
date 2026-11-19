"""Complete route checks for selected flight motion and unchanged native control."""
import csv
import json
import os
from pathlib import Path
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    base=ROOT/'build/pride-pickup-flight34';build=base/'build-report.json';bound(build)
    source=ROOT/'build/pride-audio-prime30/routes/report.json';old=bound(source)
    out=base/'routes';out.mkdir();checks={};commands={};observations={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    for case,enabled in [('256-snes',False),('256-md',True),('320-md',True)]:
        pair=[]
        for lle in (False,True):
            key=case+('-lle' if lle else '');folder=out/key;folder.mkdir();pair.append(folder)
            cmd=old['commands'][key].copy();cmd[0]=str(base/'player.exe')
            profile=folder/'resources.ini';profile.write_text(Path(cmd[cmd.index('--resource-profile')+1]).read_text()+
                '\ngameplay.levels.pride_lands.pickup_flight = '+('md' if enabled else 'snes')+'\n')
            for flag,value in [('--resource-profile',profile),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
            env=dict(clean,TLK_FINAL_MD_ART='1',TLK_PICKUP_FLIGHT_TRACE=str(folder/'flight.csv'))
            with (folder/'run.log').open('wb') as log:
                result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW)
            commands[key]=cmd;checks[key+'_exit']=result.returncode==0
            scene=json.loads((folder/'scene.json').read_text());checks[key+'_next_level']=scene['level']==1
            rows=list(csv.DictReader((folder/'flight.csv').open())) if (folder/'flight.csv').exists() else []
            checks[key+'_source_active']=bool(rows) if enabled else not rows
            observations[key]=dict(final_level=scene['level'],flight_calls=len(rows),arrivals=[r for r in rows if r['arrived']=='1'])
            print(key,scene['level'],len(rows),'flight calls',flush=True)
            if not enabled:
                reference=Path(old['commands'][key][old['commands'][key].index('--dump-window')+1]).parent
                checks[key+'_native_guest_preserved']=hashes(folder/'run.log')==hashes(reference/'run.log')
                checks[key+'_native_client_preserved']=pixels(folder/'window.png')==pixels(reference/'window.png')
                checks[key+'_native_pcm_preserved']=pcm(folder/'audio.wav')==pcm(reference/'audio.wav')
        a,b=pair
        checks[case+'_lle_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        checks[case+'_lle_client']=pixels(a/'window.png')==pixels(b/'window.png')
        checks[case+'_lle_pcm']=pcm(a/'audio.wav')==pcm(b/'audio.wav')
        if enabled:checks[case+'_lle_motion']= (a/'flight.csv').read_bytes()==(b/'flight.csv').read_bytes()
    paths=[Path(__file__),build,source]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()
