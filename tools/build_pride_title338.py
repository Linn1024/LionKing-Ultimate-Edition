"""Integrate blank-title DMA preparation into both compiled and LLE paths."""
import difflib,json,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
base=ROOT/'build/pride-porcupine327';bp=base/'build-report.json';b=bound(bp)
generation=ROOT/'build/pride-title337-generation';gp=generation/'generation-report.json';g=bound(gp);assert g['result']=='GENERATED'
old=ROOT/'build/pride-battle316-generation';oldg=bound(old/'generation-report.json');assert g['program_contract_sha256']==oldg['program_contract_sha256']
changed=[p.name for p in (old/'hooks').glob('*.c') if digest(p)!=digest(generation/'hooks'/p.name)]
assert set(changed)=={'bankc0_part02_v2.c','bankc0_part1e_v2.c'},changed
out=ROOT/'build/pride-title338';out.mkdir(exist_ok=True);cwd=ROOT/'build/pride-sprite-fresh44'
inputs=argv('link '+(base/'link.rsp').read_text())[1:];compiles=dict(b['compiles'])
rows=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=cwd))
tasks=[('host',b['compiles']['host'],ROOT/'engine/runner/pride/final/pride_final_host.c',Path(b['compiles']['host'][b['compiles']['host'].index('-o')+1]))]
for name in changed:
    diff=list(difflib.unified_diff((old/'hooks'/name).read_text().splitlines(),(generation/'hooks'/name).read_text().splitlines()))
    assert not any(x.startswith('-') and not x.startswith('---') for x in diff)
    (out/(name+'.diff')).write_text('\n'.join(diff)+'\n')
    matches=[r for r in rows if r.get('output','').replace('\\','/').endswith('/hooks/'+name+'.obj') and (cwd/r['output']).resolve().relative_to(ROOT).as_posix() in b['link_inputs_sha256']]
    assert len(matches)==1,(name,len(matches));r=matches[0]
    tasks.append((name[:-2],argv(r['command']),generation/'hooks'/name,(cwd/r['output']).resolve()))
for label,template,src,old_object in tasks:
    cmd=template.copy();obj=out/(label+'.obj')
    for flag,value in (('-c',src),('-o',obj),('-MT',obj),('-MF',out/(label+'.d'))):cmd[cmd.index(flag)+1]=str(value)
    if label!='host':cmd+=['-I'+str(ROOT/'engine/runner/pride')]
    with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
    indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old_object];assert len(indices)==1
    inputs[indices[0]]=obj.as_posix();compiles[label]=cmd;print('compiled',label,flush=True)
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
retained=sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert retained==321 and len(linked)==324
paths=[Path(__file__),bp,gp,old/'generation-report.json',rsp,*[ROOT/p for p in ('engine/runner/pride/final/pride_final_runtime.inc','engine/runner/pride/final/pride_final_title_dma.inc','engine/recomp/pride_final_hooks.json')]]
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,inputs_retained=retained,changed_units=changed,scope='Selected MD final exit: original DMA byte engine prepares title synchronously only under forced blank/NMI off with exact source/size/port guards. No new save state/assets. Ordinary boot/native final/YES unaffected.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('BUILT',digest(out/'player.exe'),flush=True)
