"""Stage resource-selected Pride behavior with normal ROM/configuration inputs."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from summarize_pride_practice import bound
from pride_save_identity2 import make_contract,contract_identity


def main():
    parent=ROOT/'build/pride-save-identity2';base_path=parent/'build-report.json';base=bound(base_path)
    out=ROOT/'build/pride-launch';out.mkdir(exist_ok=True);assert not (out/'build-report.json').exists();cwd=ROOT/'engine/build-win';ninja='C:/mingw32/bin/ninja.exe';target='tlk_scene_prepared_sdl'
    db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd));patcher=ROOT/'engine/scripts/apply_runtime_patches.py';patches=ROOT/'engine/cmake/game-patches'
    subprocess.run([sys.executable,patcher,'--patches',patches,'--snesrecomp',ROOT/'engine','--out',out/'game'],check=True,timeout=60)
    paths=[Path(__file__),ROOT/'tools/pride_launch_dispatch.c',ROOT/'tools/pride_launch_wide.c',ROOT/'engine/runner/tlk_pride_launch.c',ROOT/'engine/runner/tlk_pride_launch.h',base_path,
           ROOT/'tools/pride_save_identity.py',ROOT/'tools/pride_save_identity2.py',*sorted(patches.glob('*.hunks'))];replacements={}
    def compile_source(label,source,suffix,extra=()):
        row=next(r for r in db if r.get('output','').replace('\\','/')==suffix);obj=out/(label+'.obj');cmd=argv(row['command'])
        for flag,value in (('-c',source.as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):cmd[cmd.index(flag)+1]=value
        cmd+=list(extra)
        with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        paths.append(source);return obj
    resource=f'CMakeFiles/{target}.dir/runner/tlk_resources.c.obj';state='C:/TEMP2/lionKing/build/pride-legacy-save/player/mixed-state.obj'
    replacements[resource]=compile_source('resources',out/'game/tlk_resources.c',resource,['-DTLK_PRIDE_DEATH_AOT_AVAILABLE=1'])
    replacements[state]=compile_source('state',out/'game/tlk_savestate.c',f'CMakeFiles/{target}.dir/runner/tlk_savestate.c.obj')
    launch=compile_source('launch',ROOT/'engine/runner/tlk_pride_launch.c',resource)
    wide_suffix=f'CMakeFiles/{target}.dir/C_/TEMP2/lionKing/tools/pride_scene_prepared_objects.c.obj';row=next(r for r in db if r.get('output','').replace('\\','/')==wide_suffix)
    wide=out/'wide.i';cmd=argv(row['command'])
    for flag,value in (('-c',(ROOT/'tools/pride_launch_wide.c').as_posix()),('-o',wide.as_posix()),('-MF',(out/'wide.d').as_posix()),('-MT','wide')):cmd[cmd.index(flag)+1]=value
    cmd[cmd.index('-c')]='-E';cmd+=['-CC','-I'+str(ROOT/'tools')]
    with (out/'wide-preprocess.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    text=wide.read_text();anchor='TlkWideDraw(uint32_t *out,int width,';at=text.index(anchor)
    while text.find(';',at)<text.find('{',at):at=text.index(anchor,at+len(anchor))
    at=text.index('{',at)+1;text=text[:at]+'\n    if(!TlkPrideHealthDeathSelected())return PrideNativeWideDraw(out,width,hud_edges);'+text[at:];wide.write_text(text)
    replacements['C:/TEMP2/lionKing/build/pride-machine-player4/wide.obj']=compile_source('wide',wide,wide_suffix)
    response=argv('response '+(parent/'a.rsp').read_text())[1:]
    for key,obj in replacements.items():assert response.count(key)==1,key;response[response.index(key)]=obj.as_posix()
    response.append(launch.as_posix());host_key=(parent/'a-host.obj').as_posix();assert response.count(host_key)==1
    link_inputs={}
    for arg in response:
        if arg.lower().endswith(('.obj','.a')):
            p=Path(arg);p=p if p.is_absolute() else cwd/p;link_inputs[p.resolve().relative_to(ROOT).as_posix()]=digest(p)
    closure_path=ROOT/'build/pride-tree-help2/build-report.json';closure=bound(closure_path);paths.append(closure_path)
    private={name:sha for name,sha in closure['source_sha256'].items() if name.startswith('tools/') and name.endswith(('.c','.h')) and 'present_probe' not in name}
    for p in (Path(__file__),ROOT/'tools/pride_launch_dispatch.c'):private[p.relative_to(ROOT).as_posix()]=digest(p)
    backend=parent/'genesis_plus_gx_libretro.dll';contract=make_contract(link_inputs,Path(host_key).relative_to(ROOT).as_posix(),private,digest(backend));contract['compatibility_epoch']=2
    identity=contract_identity(contract);manifest=out/'save-compatibility.json';manifest.write_text(json.dumps(contract,indent=2)+'\n');paths.append(manifest)
    original=parent/'a.i';text=original.read_text();paths.append(original)
    start=text.index('static unsigned restore_installed')
    prototypes='''extern void TlkPrideConfigure(const char *);
extern int TlkPrideHealthDeathSelected(void);
extern int TlkPrideProfileChanged(void);
extern char *TlkPrideSetting(const char *);
extern FILE *TlkPrideFileOpen(const char *,const char *);
extern int TlkPrideMakeDirectory(const char *);
static void PrideLaunchClearPrivate(void);
'''
    text=text[:start]+prototypes+text[start:]
    for name in ('hook','scene_hook','owner_hook','restore_hook','restore_hud_hook','restore_roar_font_hook','restore_ready_roar_hook','restore_animation_hook'):
        anchor='static void '+name+'(CpuState *cpu,uint32_t pc) {';assert text.count(anchor)==1,name
        text=text.replace(anchor,anchor+'\n    if(!TlkPrideHealthDeathSelected())return;')
    anchor='preparation_frame(uint32 inputs) {\n';assert text.count(anchor)==1;text=text.replace(anchor,anchor+'    if(!TlkPrideHealthDeathSelected())return RtlRunFrame(inputs);\n')
    for old,new in (('static int PridePracticeSave(const char *path,uint32_t field) {','static int PridePrivateSave(const char *path,uint32_t field) {'),
                    ('static int PridePracticeLoad(const char *path,uint32_t *field) {','static int PridePrivateLoad(const char *path,uint32_t *field) {')):
        assert text.count(old)==1; text=text.replace(old,new)
    anchor='                     resource_profile ? resource_profile : resource_default);';assert text.count(anchor)==1
    text=text.replace(anchor,anchor+'\n    TlkPrideConfigure(md_rom_path ? md_rom_path : md_default);')
    anchor='    restart|=TlkLeavesProfileChanged();';assert text.count(anchor)==1;text=text.replace(anchor,anchor+'\n    restart|=TlkPrideProfileChanged();')
    a=text.index('void __wrap_TlkResetMachine(void) {');b=text.index('_Bool __real_RtlRunFrame',a);cleanup=text[a:b]
    cleanup=cleanup.replace('void __wrap_TlkResetMachine(void) {','static void PrideLaunchClearPrivate(void) {').replace('    __real_TlkResetMachine();\n','')
    text+='\n'+cleanup+'\n'+(ROOT/'tools/pride_launch_dispatch.c').read_text()
    start=text.index('static unsigned restore_installed');text=text[:start]+re.sub(r'\bfopen\s*\(','TlkPrideFileOpen(',text[start:])
    text=text[:start]+re.sub(r'\bgetenv\s*\(','TlkPrideSetting(',text[start:])
    text=text.replace('_mkdir(folder)','TlkPrideMakeDirectory(folder)')
    pattern=r'static const unsigned char kPrideSaveCompatibility\[32\]=\{[^}]*\};';assert len(re.findall(pattern,text))==1
    text=re.sub(pattern,'static const unsigned char kPrideSaveCompatibility[32]={'+','.join('0x'+identity[i:i+2] for i in range(0,64,2))+'};',text)
    host_source=out/'host.i';host_source.write_text(text);host=compile_source('host',host_source,f'CMakeFiles/{target}.dir/C_/TEMP2/lionKing/tools/pride_scene_render_probe.c.obj')
    response[response.index(host_key)]=host.as_posix();rsp=out/'player.rsp';rsp.write_text(subprocess.list2cmdline(response))
    raw=subprocess.check_output([ninja,'-t','commands',target+'.exe'],cwd=cwd,text=True).splitlines()[-1];cmd=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip());index=next(i for i,a in enumerate(cmd) if a.startswith('@'));cmd[index]='@'+rsp.as_posix();binary=out/'player.exe';cmd[cmd.index('-o')+1]=binary.as_posix()
    for i,arg in enumerate(cmd):
        if arg.startswith('-Wl,--out-implib,'):cmd[i]='-Wl,--out-implib,'+(out/'player.dll.a').as_posix()
    cmd+=['-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine']
    with (out/'link.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    del link_inputs[Path(host_key).relative_to(ROOT).as_posix()];link_inputs[host.relative_to(ROOT).as_posix()]=digest(host)
    shutil.copy2(backend,out/backend.name);paths.extend([backend,out/backend.name])
    report=dict(result='BUILT',binary_sha256=digest(binary),save_compatibility_sha256=identity,link_inputs_sha256=link_inputs,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},production_sha256=base['production_sha256'],public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('Normal-configuration player linked',flush=True)


if __name__=='__main__':main()
