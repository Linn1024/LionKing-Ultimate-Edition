"""Build installed sprite-v2 gameplay-table loading without guest changes."""
import json,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
base=ROOT/'build/pride382';bp=base/'build-report.json';b=bound(bp)
sprite_report=ROOT/'build/pride-continue-token46/build-report.json';sb=bound(sprite_report)
out=ROOT/'build/pride390';out.mkdir(exist_ok=True);cwd=ROOT/'build/pride-sprite-fresh44'
with (out/'game-patches.log').open('wb') as log:subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/game-patches'),'--snesrecomp',str(ROOT/'engine'),'--out',str(out/'game')],stdout=log,stderr=subprocess.STDOUT,check=True)
assert (out/'game/tlk_md_sprites.c').read_bytes()==(sprite_report.parent/'game/tlk_md_sprites.c').read_bytes()
inputs=argv('link '+(base/'link.rsp').read_text())[1:];compiles=dict(b['compiles'])
rows=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=cwd))
tasks=[('resources',b['compiles']['resources'],out/'game/tlk_resources.c'),('sprites',sb['compiles']['sprites'],out/'game/tlk_md_sprites.c')]
for part in ('start_data','reactivation_data','hitbox_data','roar_data'):
    matches=[r for r in rows if r.get('output','').replace('\\','/').endswith('/runner/tlk_'+part+'.c.obj') and (cwd/r['output']).resolve().relative_to(ROOT).as_posix() in b['link_inputs_sha256']];assert len(matches)==1,part
    tasks.append((part,argv(matches[0]['command']),ROOT/'engine/runner'/('tlk_'+part+'.c')))
tasks.append(('pride_data',tasks[2][1],ROOT/'engine/runner/tlk_pride_data.c'))
for label,template,src in tasks:
    cmd=template.copy();old=(cwd/cmd[cmd.index('-o')+1]).resolve();obj=out/(label+'.obj')
    for flag,value in (('-o',obj),('-MT',obj),('-MF',out/(label+'.d')),('-c',src)):cmd[cmd.index(flag)+1]=str(value)
    with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
    if label=='pride_data':inputs.insert(0,obj.as_posix())
    else:
        indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(indices)==1,(label,old)
        inputs[indices[0]]=obj.as_posix()
    compiles[label]=cmd;print('compiled',label,flush=True)
rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
retained=sum(b['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert retained==len(b['link_inputs_sha256'])-6
names=['engine/runner/tlk_'+part+suffix for part in ('start_data','reactivation_data','hitbox_data','roar_data','pride_data') for suffix in ('.c','.h')]
names+=['engine/runner/tlk_data_record.h','engine/runner/tlk_md_sprite_assets.inc','engine/runner/tlk_md_sprite_format.inc','engine/runner/tlk_resources.c']
paths=[Path(__file__),bp,sprite_report,rsp,out/'game/tlk_resources.c',out/'game/tlk_md_sprites.c',*[ROOT/name for name in names]]
(out/'build-report.json').write_text(json.dumps(dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,inputs_retained=retained,scope='Load Pride start/reactivation/hitbox/roar tables from sprite-v2 prepared package. Algorithms, runtime state schemas and artwork mappings unchanged.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('BUILT',digest(out/'player.exe'),flush=True)
