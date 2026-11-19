"""Link the independently selectable RNG entry into the reviewed development host."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_save_identity_owned import make_contract,contract_identity
from summarize_pride_practice import bound


def main():
    parent=ROOT/'build/pride-launch4';bp=parent/'build-report.json';base=bound(bp)
    out=ROOT/'build/pride-rng-player';gp=out/'generation-report.json';generation=bound(gp);assert generation['result']=='GENERATED'
    assert not (out/'build-report.json').exists();cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe';target='tlk_scene_prepared_sdl'
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd));patches=ROOT/'engine/cmake/game-patches';patcher=ROOT/'engine/scripts/apply_runtime_patches.py'
    subprocess.run([sys.executable,patcher,'--patches',patches,'--snesrecomp',ROOT/'engine','--out',out/'game'],check=True,timeout=60)
    paths=[Path(__file__),bp,gp,patcher,ROOT/'engine/CMakeLists.txt',ROOT/'engine/cmake/native_adapters.h.in',*sorted(patches.glob('*.hunks'))]
    sources=[ROOT/'engine/runner'/name for name in ('tlk_rng_entry.c','tlk_rng_entry.h','tlk_rng_runtime.c','tlk_rng_runtime.h')];paths+=sources
    def compile_source(label,path,suffix,flags=()):
        row=next(r for r in db if r.get('output','').replace('\\','/')==suffix);obj=out/(label+'.obj');cmd=argv(row['command'])
        for flag,value in (('-c',path.as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):cmd[cmd.index(flag)+1]=value
        cmd+=list(flags)
        with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        paths.append(path);return obj
    resource_row=f'CMakeFiles/{target}.dir/runner/tlk_resources.c.obj'
    replacements={parent/'resources.obj':compile_source('resources',out/'game/tlk_resources.c',resource_row,['-DTLK_PRIDE_DEATH_AOT_AVAILABLE=1','-DTLK_RNG_ENTRY_STAGED_AVAILABLE=1']),
        parent/'state.obj':compile_source('state',out/'game/tlk_savestate.c',f'CMakeFiles/{target}.dir/runner/tlk_savestate.c.obj'),
        ROOT/'build/pride-reset/fixed3/sdl-tlk_game.obj':compile_source('game',out/'game/tlk_game.c',f'CMakeFiles/{target}.dir/runner/tlk_game.c.obj',['-DTLK_RNG_ENTRY_STAGED_AVAILABLE=1'])}
    unit='bankc0_part1f_v2.c';suffix='CMakeFiles/snesrecomp_game.dir/generated/snesrecomp/'+unit+'.obj'
    replacements[cwd/suffix]=compile_source('clear',out/'generated'/unit,suffix)
    added=[compile_source('rng-entry',sources[0],resource_row),compile_source('rng-runtime',sources[2],resource_row)]
    response=argv('response '+(parent/'player.rsp').read_text())[1:]
    def resolved(arg):
        p=Path(arg);return (p if p.is_absolute() else cwd/p).resolve()
    for before,after in replacements.items():
        indices=[i for i,a in enumerate(response) if resolved(a)==before.resolve()];assert len(indices)==1,before;response[indices[0]]=after.as_posix()
    response.extend(p.as_posix() for p in added);host_key=parent/'host.obj';host_index=next(i for i,a in enumerate(response) if resolved(a)==host_key.resolve())
    inputs={resolved(a).relative_to(ROOT).as_posix():digest(resolved(a)) for a in response if a.lower().endswith(('.obj','.a'))}
    old_contract_path=parent/'save-compatibility.json';old=json.loads(old_contract_path.read_text());paths.append(old_contract_path)
    private=dict(old['private_context_sources_sha256'])
    for p in [Path(__file__),*sources]:private[p.relative_to(ROOT).as_posix()]=digest(p)
    backend=parent/'genesis_plus_gx_libretro.dll';contract=make_contract(inputs,host_key.relative_to(ROOT).as_posix(),private,digest(backend));contract['compatibility_epoch']=2
    identity=contract_identity(contract);manifest=out/'save-compatibility.json';manifest.write_text(json.dumps(contract,indent=2)+'\n');paths.append(manifest)
    original=parent/'host.i';text=original.read_text();paths.append(original)
    anchor='static unsigned restore_installed';assert text.count(anchor)==1
    text=text.replace(anchor,'extern int TlkRngRuntimeProfileChanged(void);\n'+anchor)
    anchor='    TlkPrideConfigure(md_rom_path ? md_rom_path : md_default);';assert text.count(anchor)==1
    text=text.replace(anchor,anchor+'\n    TlkRngRuntimeProfileChanged();')
    anchor='    restart|=TlkPrideProfileChanged();';assert text.count(anchor)==1
    text=text.replace(anchor,anchor+'\n    restart|=TlkRngRuntimeProfileChanged();')
    pattern=r'static const unsigned char kPrideSaveCompatibility\[32\]=\{[^}]*\};';assert len(re.findall(pattern,text))==1
    text=re.sub(pattern,'static const unsigned char kPrideSaveCompatibility[32]={'+','.join('0x'+identity[i:i+2] for i in range(0,64,2))+'};',text)
    host_source=out/'host.i';host_source.write_text(text);host=compile_source('host',host_source,f'CMakeFiles/{target}.dir/C_/TEMP2/lionKing/tools/pride_scene_render_probe.c.obj');response[host_index]=host.as_posix()
    rsp=out/'player.rsp';rsp.write_text(subprocess.list2cmdline(response));raw=subprocess.check_output([ninja,'-t','commands',target+'.exe'],cwd=cwd,text=True).splitlines()[-1]
    cmd=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip());at=next(i for i,a in enumerate(cmd) if a.startswith('@'));cmd[at]='@'+rsp.as_posix();binary=out/'player.exe';cmd[cmd.index('-o')+1]=binary.as_posix()
    for i,a in enumerate(cmd):
        if a.startswith('-Wl,--out-implib,'):cmd[i]='-Wl,--out-implib,'+(out/'player.dll.a').as_posix()
    cmd+=['-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine']
    with (out/'link.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    del inputs[host_key.relative_to(ROOT).as_posix()];inputs[host.relative_to(ROOT).as_posix()]=digest(host);shutil.copy2(backend,out/backend.name);paths.extend([backend,out/backend.name])
    report=dict(result='BUILT',binary_sha256=digest(binary),save_compatibility_sha256=identity,link_inputs_sha256=inputs,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},production_sha256=base['production_sha256'],
        resource_id=106,source_flag=0x40000000,canonical_configuration_modified=False,public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('Independent RNG scene-entry player linked',flush=True)


if __name__=='__main__':main()
