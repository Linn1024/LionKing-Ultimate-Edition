"""Read-only live floor-contact ABI and detached original-CPU preparation audit.

Never activates grounding in the player. Live observations are ordinary LLE
routes; the separately labeled detached calls operate only on copied WRAM.
"""
import argparse
import ctypes as C
import csv
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from verify_windows import hashes

OUT=ROOT/'build/pride-default-grounding'
BASE=ROOT/'build/pride-default-actor'
ABI=('a','x','y','stack','direct_page','db','p','emulation')


def build():
    original=json.loads((BASE/'build-report.json').read_text())
    for name,sha in original['source_sha256'].items():assert digest(ROOT/name)==sha,name
    for host in ('probe','sdl'):
        for name,sha in original['runs'][host]['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    owner=(ROOT/'tools/pride_default_actor_owner.c').read_text()
    anchor='static void owner_init(void) {';assert owner.count(anchor)==1
    owner=owner.replace(anchor,'#include "pride_default_grounding_observer.h"\n'+anchor)
    anchor='interp_bridge_add_pre_opcode_hook(points[i],owner_hook);'
    assert owner.count(anchor)==1;owner=owner.replace(anchor,anchor+'\n    grounding_init();')
    (OUT/'observed-owner.c').write_text(owner)
    restore=(ROOT/'tools/pride_default_actor_restore.c').read_text().replace('"pride_default_actor_owner.c"','"observed-owner.c"')
    (OUT/'observed-restore.c').write_text(restore)
    probe=(ROOT/'tools/pride_default_actor_probe.c').read_text().replace('"pride_default_actor_restore.c"','"observed-restore.c"')
    clone=OUT/'observed-probe.c';clone.write_text(probe)
    folder=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe'
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=folder));runs={}
    for host in ('probe','sdl'):
        entry=next(r for r in db if 'tlk_scene_prepared_'+host+'.dir/' in r.get('output','') and r['file'].endswith('pride_scene_render_probe.c'))
        obj=OUT/('observed-'+host+'.obj');command=argv(entry['command'])
        for flag,value in (('-c',clone.as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):
            command[command.index(flag)+1]=value
        command+=['-I'+str(ROOT/'tools'),'-DTLK_PRIVATE_COMPILED_HOOKS=1','-DTLK_FORCE_SCENE_PRESENTATION=1']
        with (OUT/(host+'-compile.log')).open('wb') as log:
            subprocess.run(command,cwd=folder,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        response=argv('response '+(BASE/(host+'.rsp')).read_text())[1:]
        old=(BASE/('private-'+host+'-host.obj')).as_posix();assert response.count(old)==1
        response[response.index(old)]=obj.as_posix()
        rsp=OUT/(host+'.rsp');rsp.write_text(subprocess.list2cmdline(response))
        link=subprocess.check_output([ninja,'-t','commands','tlk_scene_prepared_'+host+'.exe'],cwd=folder,text=True).splitlines()[-1]
        command=argv(link.split('&&',1)[1].rsplit('&&',1)[0].strip())
        command[next(n for n,a in enumerate(command) if a.startswith('@'))]='@'+rsp.as_posix()
        binary=OUT/('observed-'+host+'.exe');command[command.index('-o')+1]=binary.as_posix()
        for n,a in enumerate(command):
            if a.startswith('-Wl,--out-implib,'):command[n]='-Wl,--out-implib,'+(OUT/(host+'.dll.a')).as_posix()
        with (OUT/(host+'-link.log')).open('wb') as log:
            subprocess.run(command,cwd=folder,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        inputs={}
        for a in response:
            if a.lower().endswith(('.obj','.a')):
                p=Path(a);p=p if p.is_absolute() else folder/p
                inputs[str(p.resolve().relative_to(ROOT)).replace('\\','/')]=digest(p)
        runs[host]=dict(binary_sha256=digest(binary),link_inputs_sha256=inputs)
    core=ROOT/'engine/snesrecomp/runner/src/snes';compiler=Path('C:/mingw32/bin/gcc.exe')
    runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c'
    command=[str(compiler),'-shared','-O2','-I'+str(core),str(ROOT/'tools/pride_default_grounding_oracle.c'),str(runtime),'-o',str(OUT/'original-grounding.dll')]
    with (OUT/'oracle-build.log').open('wb') as log:
        subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    sources=[Path(__file__),ROOT/'tools/pride_default_grounding_observer.h',ROOT/'tools/pride_default_grounding_oracle.c',
        ROOT/'tools/pride_terrain_native_oracle.c',core/'interp816.c',runtime,core/'interp816.h',core/'saveload.h',compiler,
        BASE/'build-report.json',OUT/'observed-owner.c',OUT/'observed-restore.c',clone]
    identities={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sources if p.is_relative_to(ROOT)}
    (OUT/'build-report.json').write_text(json.dumps(dict(result='BUILT',source_sha256=identities,runs=runs,
        compiler_sha256=digest(compiler),oracle_sha256=digest(OUT/'original-grounding.dll')),indent=2)+'\n')
    revisions=OUT/'source-revisions';revisions.mkdir(exist_ok=True)
    (revisions/(digest(Path(__file__))+'.py')).write_bytes(Path(__file__).read_bytes())
    print('Read-only observer hosts and original grounding oracle built',flush=True)


def run(width,graphics,host,observed,frames):
    name=f'{width}-{graphics}-{host}-{frames}-'+('observed' if observed else 'control')
    out=OUT/name;out.mkdir(exist_ok=True)
    reference=BASE/f'default/{width}-{graphics}-lle'
    env=os.environ.copy()
    for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE','TLK_SCENE_RENDER_PROBE'):env[key]=str(out)
    for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE','TLK_SCENE_RESTORE_ENABLE',
                'TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO','TLK_SCENE_RENDER_ENABLE'):env[key]='1'
    for key in ('TLK_NATIVE_BANK_RECORD','TLK_WATCH','TLK_TRAP_PC','TLK_TRAP_FROM'):env.pop(key,None)
    env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md')
    binary=OUT/f'observed-{host}.exe' if observed else BASE/f'default-actor-{host}.exe'
    command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
        '--resource-profile',reference/'resources.ini','--input',reference/'default-neutral.tape','--frames',frames,'--lle']
    if host=='sdl':
        config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\nwidescreen_hud = in place\n')
        command+=['--config',config,'--no-pace','--no-audio','--no-record','--dump-window',out/'window.png','--wav',out/'audio.wav','--wav-seconds','100']
    else:command+=['--wide',width,'--ram-log',out/'route.ram','--wide-png',out/'picture.png']
    with (out/'run.log').open('wb') as log:
        p=subprocess.run(list(map(str,command)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
    assert p.returncode==0,(name,p.returncode)
    report=dict(result='CAPTURED',binary_sha256=digest(binary),guest=hashes(out/'run.log'),
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (reference/'resources.ini',reference/'default-neutral.tape',OUT/'build-report.json')},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!='report.json'})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(name+' captured',flush=True)


def verify():
    # The configured 32-bit interpreter DLL uses MinGW's support DLLs.
    dll_directory=os.add_dll_directory('C:/mingw32/bin')
    library=C.CDLL(str(OUT/'original-grounding.dll'))
    library.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    rom_path=ROOT/'Lion King, The (USA).sfc';md_path=ROOT/'Lion King, The (World).md'
    assert digest(rom_path)=='457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712'
    assert digest(md_path)=='e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5'
    rom=rom_path.read_bytes();assert library.terrain_native_init(rom,len(rom))
    library.grounding_snapshot_run.argtypes=[C.c_void_p,C.c_uint,C.POINTER(C.c_uint),C.c_void_p,C.POINTER(C.c_uint),C.c_void_p,C.c_void_p]
    def invoke(data,abi):
        output=C.create_string_buffer(0x20000);reads=C.create_string_buffer(0x20000);writes=C.create_string_buffer(0x20000);result=(C.c_uint*11)()
        assert library.grounding_snapshot_run(data,len(data),(C.c_uint*8)(*abi),output,result,reads,writes),list(result)
        return output.raw,list(result),reads.raw,writes.raw
    build=json.loads((OUT/'build-report.json').read_text())
    predecessor=json.loads((BASE/'build-report.json').read_text())
    for name,sha in predecessor['source_sha256'].items():assert digest(ROOT/name)==sha,name
    for name,sha in predecessor['production_sha256'].items():assert digest(ROOT/name)==sha,name
    cases={};window_pixels=0
    for width,graphics in ((256,'native'),(320,'all')):
        for host,frames in (('probe',2085),('sdl',2053),('sdl',2076)):
            prefix=f'{width}-{graphics}-{host}-{frames}'
            observed=OUT/(prefix+'-observed');control=OUT/(prefix+'-control')
            a=json.loads((observed/'report.json').read_text());b=json.loads((control/'report.json').read_text())
            for folder,record,is_observer in ((observed,a,True),(control,b,False)):
                binary=OUT/f'observed-{host}.exe' if is_observer else BASE/f'default-actor-{host}.exe'
                assert record['binary_sha256']==digest(binary)
                expected=build['runs'][host]['binary_sha256'] if is_observer else predecessor['runs'][host]['binary_sha256']
                assert record['binary_sha256']==expected
                for name,sha in record['source_sha256'].items():assert digest(ROOT/name)==sha,name
                for name,sha in record['artifacts_sha256'].items():assert digest(folder/name)==sha,(folder,name)
            assert a['guest']==b['guest'],prefix
            for name in ('render-owned.rgb','owner-fields.csv','owner-events.csv','post-ready.csv','prepared-fonts.bin','restore-fields.csv','normal-wram.bin'):
                if (control/name).exists():assert digest(observed/name)==digest(control/name),(prefix,name)
            if host=='sdl':
                for name in ('window.png','audio.wav'):assert digest(observed/name)==digest(control/name),(prefix,name)
                from verify_windows import pixels
                w,h,client=pixels(observed/'window.png');assert (w,h)==(width*2,448)
                window_pixels+=w*h
            elif (control/'route.ram').exists():assert digest(observed/'route.ram')==digest(control/'route.ram')
            events=list(csv.DictReader((observed/'grounding.csv').open()))
            calls=[]
            for entry in (r for r in events if r['event']=='entry'):
                returned=next(r for r in events if r['event']=='return' and r['call']==entry['call'])
                before=(observed/f'ground-{int(entry["call"]):03}-entry.bin').read_bytes()
                after=(observed/f'ground-{int(entry["call"]):03}-return.bin').read_bytes()
                abi=[int(entry[k],16 if k not in ('emulation',) else 10) for k in ABI]
                actual,result,reads,writes=invoke(before,abi)
                assert actual==after,(prefix,'original full RAM return')
                expected=[int(returned[k],16 if k!='emulation' else 10) for k in ABI]
                assert result[:8]==expected,(prefix,result,expected)
                assert int(entry['actor_y'])==(1248 if not calls else 1255) and int(returned['actor_y'])==1255
                calls.append(dict(instructions=result[8],invalid_bus_accesses=result[9],cpu=result[:8],
                    changed_offsets=[n for n,(x,y) in enumerate(zip(before,after)) if x!=y],
                    read_offsets=[n for n,x in enumerate(reads) if x],write_offsets=[n for n,x in enumerate(writes) if x]))
            experiments=[]
            if frames>=2076:
                assert len(calls)==2
                for label in ('before-idle','after-idle'):
                    row=next(r for r in events if r['event']==label)
                    data=bytearray((observed/f'ground-{int(row["call"]):03}-{label}.bin').read_bytes())
                    # Detached call ABI only: select the live actor and a safe,
                    # artificial long-return frame. No live guest is written.
                    player=int(row['player'],16);struct.pack_into('<H',data,0x68,player)
                    data[0x1ff1:0x1ff4]=bytes.fromhex('ff3fc0')
                    fixture=bytes(data);abi=[0,0,0,0x1ff0,0,0x7e,0x10,0]
                    after,result,reads,writes=invoke(fixture,abi)
                    x,y=struct.unpack_from('<HH',after,player+8)
                    again,second,_,_=invoke(after,abi)
                    assert (x,y)==(64,1255) and struct.unpack_from('<HH',again,player+8)==(x,y)
                    assert result[3:8]==[0x1ff3,0,0x7e,0x10,0]
                    experiments.append(dict(label=label,age=int(row['age']),detached_abi_fixture=True,
                        output_xy=[x,y],instructions=result[8],idempotent_actor_position=True,
                        changed_offsets=[n for n,(x,y) in enumerate(zip(fixture,after)) if x!=y],
                        write_offsets=[n for n,x in enumerate(writes) if x]))
            else:assert not calls
            cases[prefix]=dict(live_original_calls=calls,detached_preparation=experiments,observer_control_exact=True,
                actual_windows=host=='sdl',artifacts_sha256={str(p.relative_to(OUT)).replace('\\','/'):digest(p)
                    for folder in (observed,control) for p in folder.iterdir() if p.is_file()})
            print(prefix+' read-only control/original CPU checks PASS',flush=True)
    retained={}
    for name,sha in build['source_sha256'].items():
        if name=='tools/audit_pride_default_grounding.py' and digest(ROOT/name)!=sha:
            # Capture-driving source is immutable evidence even when its
            # post-capture verifier is corrected. Do not relabel old captures
            # as executions of the new verifier/driver revision.
            saved=OUT/'source-revisions'/(sha+'.py');assert digest(saved)==sha
            retained[name]=dict(sha256=sha,snapshot=str(saved.relative_to(ROOT)).replace('\\','/'))
        else:assert digest(ROOT/name)==sha,name
    assert digest(OUT/'original-grounding.dll')==build['oracle_sha256']
    for host,record in build['runs'].items():
        assert digest(OUT/f'observed-{host}.exe')==record['binary_sha256']
        for name,sha in record['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    report=dict(result='SOURCE_ABI_VERIFIED_INTEGRATION_OPEN',scope=__doc__,cases=cases,
        compared_window_pixels=window_pixels,actual_window_clients=8,live_original_calls=sum(len(c['live_original_calls']) for c in cases.values()),
        live_guest_mutated=False,production_behavior_enabled=False,compiled_grounding_observation_verified=False,
        earlier_actor_reset_verified=False,gameplay_initialization_profiles_verified=False,
        full_first_level_fidelity_complete=False,build_source_sha256=build['source_sha256'],retained_build_source_versions=retained,
        verifier_sha256=digest(Path(__file__)),rom_sha256={'snes':digest(rom_path),'md':digest(md_path)},
        build_report_sha256=digest(OUT/'build-report.json'))
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    dll_directory.close()
    print('Original live floor-contact ABI and detached pre-fade readiness PASS; integration remains open',flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify-only',action='store_true');args=parser.parse_args()
    OUT.mkdir(exist_ok=True)
    if args.verify_only:verify();return
    build()
    for width,graphics in ((256,'native'),(320,'all')):
        for host,frames in (('probe',2085),('sdl',2053),('sdl',2076)):
            for observed in (False,True):run(width,graphics,host,observed,frames)
    subprocess.run([str(ROOT/'.tools/python32/python.exe'),str(Path(__file__).resolve()),'--verify-only'],cwd=ROOT,check=True,timeout=120)


if __name__=='__main__':main()
