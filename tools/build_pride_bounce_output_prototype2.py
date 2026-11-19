"""Private output-filter experiment; preserve the original sound command path.

SRCN92 ownership is currently bounded to the observed bounce window. This is
research, not production capability or a general sample-ownership assertion.
"""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_lizard_launch_preview_history import bound


FILTER=r'''
#include "common_rtl.h"
#include "tlk_resources.h"
#include "tlk_md_sound.h"
static int PrototypeBounceOutputMute(Dsp *dsp,int channel) {
    if(dsp->channel[channel].srcn!=92 || dsp->channel[channel].echoEnable)return 0;
    unsigned scene=g_ram[0xdf]|(unsigned)g_ram[0xe0]<<8|(unsigned)g_ram[0xe1]<<16;
    return !g_ram[0x1ff9e] && !g_ram[0x1ff9f] && !g_ram[0x2000] && !g_ram[0x2001] &&
        (scene==0xc00387 || scene==0xc0080d) && (g_ram[0x1ff96] || g_ram[0x1ff97]) &&
        TlkMdSoundReady() && TlkResourcesUseMd("audio.effects.simba.bounce");
}
'''


def main():
    base=ROOT/'build/pride-lizard-launch-work/player';bp=base/'build-report.json';build=bound(bp)
    out=base/'bounce-output-prototype2';out.mkdir()
    rows=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=base))
    host_row,=[r for r in rows if r.get('output','').endswith('/tlk_pride_host.c.obj')]
    def core(suffix):
        row,=[r for r in rows if r.get('output','').startswith('native-engine/CMakeFiles/tlk_pride_player') and r.get('file','').replace('\\','/').endswith(suffix)]
        return row
    dsp_row=core('/dsp.c');audio_row=core('/tlk_audio.c')
    host_source=ROOT/'engine/runner/pride/tlk_pride_host.c'
    host=out/'host.c';host.write_text('#define __wrap_RtlRunFrame PrideObservedRunFrame\n#include "'+host_source.as_posix()+'"\n#undef __wrap_RtlRunFrame\n'+(ROOT/'tools/native_bounce_npc_observer4.c').read_text())
    original_dsp=Path(dsp_row['file']);text=original_dsp.read_text()
    needle='void dsp_cycle(Dsp* dsp) {';assert text.count(needle)==1
    text=text.replace(needle,FILTER+'\n'+needle)
    needle='    dsp_cycleChannel(dsp, i);';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    if(PrototypeBounceOutputMute(dsp,i))continue;')
    dsp=out/'dsp.c';dsp.write_text(text)
    original_audio=Path(audio_row['file']);text=original_audio.read_text()
    needle='            cpu->A=0;';assert text.count(needle)==1
    text=text.replace(needle,'            if(strcmp(cues[i].id,"audio.effects.simba.bounce"))cpu->A=0;')
    audio=out/'audio.c';audio.write_text(text)
    replacements={};commands={}
    for label,row,source in (('host',host_row,host),('dsp',dsp_row,dsp),('audio',audio_row,audio)):
        obj=out/(label+'.obj');command=argv(row['command'])
        for flag,value in (('-c',source.as_posix()),('-o',obj.as_posix()),('-MF',obj.as_posix()+'.d'),('-MT',obj.as_posix())):
            command[command.index(flag)+1]=value
        command+=['-I',str(Path(row['file']).parent)]
        commands[label]=command
        with (out/(label+'-compile.log')).open('wb') as log:
            subprocess.run(command,cwd=base,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        replacements[(base/row['output']).resolve()]=obj
    link_row,=[r for r in rows if r.get('output')=='native-engine/tlk_pride_player.exe']
    link=argv(link_row['command'].split('&&',1)[1].split('&&',1)[0].strip());found=set()
    for index,arg in enumerate(link):
        if arg.lower().endswith('.obj'):
            p=Path(arg);p=(p if p.is_absolute() else base/p).resolve()
            if p in replacements:link[index]=replacements[p].as_posix();found.add(p)
        if arg.startswith('-Wl,--out-implib,'):link[index]='-Wl,--out-implib,'+(out/'prototype.dll.a').as_posix()
    assert found==set(replacements),found
    binary=out/'player.exe';link[link.index('-o')+1]=binary.as_posix()
    rsp=out/'prototype.rsp';rsp.write_text(subprocess.list2cmdline(link[1:]))
    with (out/'link.log').open('wb') as log:
        subprocess.run([link[0],'@'+rsp.as_posix()],cwd=base,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    inputs=dict(build['link_inputs_sha256'])
    for old,new in replacements.items():
        assert inputs.pop(old.relative_to(ROOT).as_posix())==digest(old)
        inputs[new.relative_to(ROOT).as_posix()]=digest(new)
    for name,sha in inputs.items():assert digest(ROOT/name)==sha,name
    backend=base/'genesis_plus_gx_libretro.dll';shutil.copy2(backend,out/backend.name)
    paths=[Path(__file__),bp,host_source,original_dsp,original_audio,host,dsp,audio,rsp,
        ROOT/'tools/native_bounce_npc_observer4.c',backend]
    report=dict(result='BUILT',binary_sha256=digest(binary),link_inputs_sha256=inputs,
        replacement_object_count=3,all_other_inputs_identical=True,
        prototype_sample=92,production_or_framework_submodule_modified=False,
        full_sample_ownership_proven=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},commands=commands)
    assert digest(base/'player.exe')==build['binary_sha256']
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Private output prototype built; production unchanged; ownership scope still unproven',flush=True)


if __name__=='__main__':main()
