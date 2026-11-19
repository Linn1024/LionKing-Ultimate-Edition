"""Remove the fixed-age default-grounding assumption; retain identical core inputs."""
import json
from pathlib import Path
import re
import shutil
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_save_identity_owned import make_contract,contract_identity
from summarize_pride_practice import bound


def main():
    parent=ROOT/'build/pride-rng-player';bp=parent/'build-report.json';base=bound(bp);out=ROOT/'build/pride-rng-player2';out.mkdir()
    cwd=ROOT/'engine/build-win';target='tlk_scene_prepared_sdl';ninja='C:/mingw32/bin/ninja.exe';response=argv('response '+(parent/'player.rsp').read_text())[1:]
    host_key=parent/'host.obj';assert response.count(host_key.as_posix())==1
    old_contract_path=parent/'save-compatibility.json';old=json.loads(old_contract_path.read_text());private=dict(old['private_context_sources_sha256'])
    window=ROOT/'engine/runner/tlk_pride_ground_window.inc'
    for p in (Path(__file__),window):private[p.relative_to(ROOT).as_posix()]=digest(p)
    inputs=dict(base['link_inputs_sha256']);backend=parent/'genesis_plus_gx_libretro.dll'
    contract=make_contract(inputs,host_key.relative_to(ROOT).as_posix(),private,digest(backend));contract['compatibility_epoch']=2;identity=contract_identity(contract)
    manifest=out/'save-compatibility.json';manifest.write_text(json.dumps(contract,indent=2)+'\n')
    original=parent/'host.i';text=original.read_text();anchor='static int grounded_service(CpuState *cpu,uint32_t pc) {';assert text.count(anchor)==1
    text=text.replace(anchor,window.read_text()+'\n'+anchor)
    anchor='if(owner_age()!=268 || owner_default_advancing || cpu->D || cpu->DB!=0x7e || cpu->PB!=0xc0 ||';assert text.count(anchor)==1
    text=text.replace(anchor,'if(!PrideDefaultGroundWindow(owner_age(),owner_default_initialized,owner_default_advancing) || cpu->D || cpu->DB!=0x7e || cpu->PB!=0xc0 ||')
    pattern=r'static const unsigned char kPrideSaveCompatibility\[32\]=\{[^}]*\};';assert len(re.findall(pattern,text))==1
    text=re.sub(pattern,'static const unsigned char kPrideSaveCompatibility[32]={'+','.join('0x'+identity[i:i+2] for i in range(0,64,2))+'};',text)
    source=out/'host.i';source.write_text(text);db=json.loads(subprocess.check_output([ninja,'-t','compdb'],cwd=cwd))
    row=next(r for r in db if r.get('output','').replace('\\','/')==f'CMakeFiles/{target}.dir/C_/TEMP2/lionKing/tools/pride_scene_render_probe.c.obj')
    host=out/'host.obj';cmd=argv(row['command'])
    for flag,value in (('-c',source.as_posix()),('-o',host.as_posix()),('-MF',host.as_posix()+'.d'),('-MT',host.as_posix())):cmd[cmd.index(flag)+1]=value
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    response[response.index(host_key.as_posix())]=host.as_posix();rsp=out/'player.rsp';rsp.write_text(subprocess.list2cmdline(response))
    raw=subprocess.check_output([ninja,'-t','commands',target+'.exe'],cwd=cwd,text=True).splitlines()[-1];cmd=argv(raw.split('&&',1)[1].rsplit('&&',1)[0].strip())
    at=next(i for i,a in enumerate(cmd) if a.startswith('@'));cmd[at]='@'+rsp.as_posix();binary=out/'player.exe';cmd[cmd.index('-o')+1]=binary.as_posix()
    for i,a in enumerate(cmd):
        if a.startswith('-Wl,--out-implib,'):cmd[i]='-Wl,--out-implib,'+(out/'player.dll.a').as_posix()
    cmd+=['-Wl,--wrap=tlk_state_save,--wrap=tlk_state_load,--wrap=RtlRunFrame,--wrap=TlkResetMachine']
    with (out/'link.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    del inputs[host_key.relative_to(ROOT).as_posix()];inputs[host.relative_to(ROOT).as_posix()]=digest(host);shutil.copy2(backend,out/backend.name)
    paths=[Path(__file__),bp,old_contract_path,original,window,source,manifest,backend,out/backend.name]
    report=dict(result='BUILT',binary_sha256=digest(binary),save_compatibility_sha256=identity,link_inputs_sha256=inputs,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},production_sha256=base['production_sha256'],
        all_nonhost_link_inputs_identical=True,public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('RNG player2 linked; nonhost core inputs identical',flush=True)


if __name__=='__main__':main()
