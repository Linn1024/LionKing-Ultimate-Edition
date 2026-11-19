"""Link a consumer-only observer without changing verified runtime objects."""
import csv
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from verify_pride_live_error_ui import environment


def main():
    base=ROOT/'build/pride-restart';out=base/'sync-trace';out.mkdir(exist_ok=True)
    report_path=base/'final/windows/native-aot/report.json';report=json.loads(report_path.read_text())
    build_path=base/'build-report.json';build=json.loads(build_path.read_text())
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    for name,sha in build['runs']['sdl']['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe'
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd))
    target='tlk_scene_prepared_sdl'
    suffix='CMakeFiles/'+target+'.dir/C_/TEMP2/lionKing/tools/pride_scene_render_probe.c.obj'
    row=next(r for r in db if r.get('output','').replace('\\','/')==suffix)
    obj=out/'observer.obj';command=argv(row['command'])
    for flag,value in (('-c',(ROOT/'tools/pride_restart_sync_trace.c').as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):
        command[command.index(flag)+1]=value
    subprocess.run(command,cwd=cwd,check=True,timeout=60)
    raw=subprocess.check_output([ninja,'-t','commands',target+'.exe'],cwd=cwd,text=True).splitlines()[-1]
    command=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip());i=next(n for n,a in enumerate(command) if a.startswith('@'))
    response=argv('response '+(base/'sdl.rsp').read_text())[1:]+[obj.as_posix()]
    rsp=out/'sdl.rsp';rsp.write_text(subprocess.list2cmdline(response));command[i]='@'+rsp.as_posix()
    binary=out/'audio-observer.exe';command[command.index('-o')+1]=binary.as_posix()
    for n,a in enumerate(command):
        if a.startswith('-Wl,--out-implib,'):command[n]='-Wl,--out-implib,'+(out/'observer.dll.a').as_posix()
    command+=['-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRenderAudio,--wrap=RtlRunFrame']
    subprocess.run(command,cwd=cwd,check=True,timeout=90)
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    boot=out/'tlk_practice_boot.state';commands={}
    for name,source in (('seed','selection'),('baseline','baseline'),('before','before')):
        folder=out/name;folder.mkdir(exist_ok=True);command=list(report['commands'][source]);command[0]=str(binary)
        command[command.index('--config')+1]=str(config)
        for flag,filename in (('--dump-window','window.png'),('--dump-png','guest.png'),('--wav','audio.wav')):
            command[command.index(flag)+1]=str(folder/filename)
        if name=='before':command[command.index('--load-at')+2]=str(boot)
        env=environment(folder);env['TLK_RESTART_AUDIO_TRACE']=str(folder/'consumer.csv');commands[name]=command
        with (folder/'run.log').open('wb') as log:
            r=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
        assert not r.returncode,(name,r.returncode)
    def rows(name):
        with (out/name/'consumer.csv').open() as f:return list(csv.DictReader(f))
    a,b=rows('baseline'),rows('before');assert len(a)==3000 and len(b)==4500
    b=b[-len(a):];differences=[dict(field=x['field'],changes={k:[x[k],y[k]] for k in x if x[k]!=y[k]}) for x,y in zip(a,b) if x!=y]
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (Path(__file__),ROOT/'tools/pride_restart_sync_trace.c',build_path,report_path,ROOT/'tools/pride_restart_audio_trace.c')}
    result=dict(result='OBSERVED',differences=len(differences),first=differences[:12],source_sha256=sources,
        binary_sha256=digest(binary),commands=commands,
        artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print('Consumer differences:',len(differences),differences[:4],flush=True)


if __name__=='__main__':main()
