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
extern int PrideSemanticVoice(unsigned);
extern void PrideSemanticReset(void);
extern void PrideSemanticLatchKon(unsigned);
extern void PrideSemanticCommit(unsigned);
static int PrototypeBounceOutputMute(Dsp *dsp,int channel) {
    if(!PrideSemanticVoice(channel) || dsp->channel[channel].srcn!=92 || dsp->channel[channel].echoEnable)return 0;
    unsigned scene=g_ram[0xdf]|(unsigned)g_ram[0xe0]<<8|(unsigned)g_ram[0xe1]<<16;
    return !g_ram[0x1ff9e] && !g_ram[0x1ff9f] && !g_ram[0x2000] && !g_ram[0x2001] &&
        (scene==0xc00387 || scene==0xc0080d) && (g_ram[0x1ff96] || g_ram[0x1ff97]) &&
        TlkMdSoundReady() && TlkResourcesUseMd("audio.effects.simba.bounce");
}
'''


def main():
    base=ROOT/'build/pride-lizard-launch-work/player';bp=base/'build-report.json';build=bound(bp)
    out=base/'bounce-driver-lifecycle-prototype';out.mkdir()
    rows=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=base))
    host_row,=[r for r in rows if r.get('output','').endswith('/tlk_pride_host.c.obj')]
    def core(suffix):
        row,=[r for r in rows if r.get('output','').startswith('native-engine/CMakeFiles/tlk_pride_player') and r.get('file','').replace('\\','/').endswith(suffix)]
        return row
    dsp_row=core('/dsp.c');audio_row=core('/tlk_audio.c');spc_row=core('/spc.c')
    host_source=ROOT/'engine/runner/pride/tlk_pride_host.c'
    host=out/'host.c';host.write_text('#define __wrap_RtlRunFrame PrideObservedRunFrame\n#include "'+host_source.as_posix()+'"\n#undef __wrap_RtlRunFrame\n'+(ROOT/'tools/native_bounce_npc_observer4.c').read_text())
    ownership=ROOT/'tools/native_bounce_semantic_owner2.h'
    lifecycle=ROOT/'tools/native_bounce_driver_lifecycle.h'
    text=host.read_text().replace('_Bool __wrap_RtlRunFrame(uint32 inputs)', '_Bool NpcObservedFrame(uint32 inputs)')
    prefix='#define PrideSemanticReset PrideOriginalSemanticReset\n#define PrideSemanticSpc PrideOriginalSemanticSpc\n#define PrideSemanticVoice PrideOriginalSemanticVoice\n'
    text+='\n'+prefix+'#include "'+ownership.as_posix()+'"\n#undef PrideSemanticReset\n#undef PrideSemanticSpc\n#undef PrideSemanticVoice\n#include "'+lifecycle.as_posix()+'"\n_Bool __wrap_RtlRunFrame(uint32 inputs) { SemHooks(); SemDriverHooks(); return NpcObservedFrame(inputs); }\n'
    text+='\nvoid PrideSemanticCpu(CpuState *cpu,unsigned pc) { if(pc==0xc21c90)SemAccepted(cpu,pc); else if(pc==0xc2212e)SemTransfer(cpu,pc); else SemDriverCpu(cpu,pc); }\n'
    continuation=ROOT/'tools/native_bounce_semantic_save.h'
    text+='\n#define PrideSemanticStateLoad PrideSemanticStateLoadUnchecked\n#include "'+continuation.as_posix()+'"\n#undef PrideSemanticStateLoad\nint PrideSemanticStateLoad(const uint8_t *data,size_t size) { if(!PrideSemanticStateLoadUnchecked(data,size))return 0; SemDriverValidate(g_snes && g_snes->apu?g_snes->apu->ram:NULL);return 1; }\n'
    host.write_text(text)
    original_dsp=Path(dsp_row['file']);text=original_dsp.read_text()
    text='extern void PrideSemanticReset(void);\n'+text
    needle='void dsp_cycle(Dsp* dsp) {';assert text.count(needle)==1
    text=text.replace(needle,FILTER+'\n'+needle)
    needle='    dsp_cycleChannel(dsp, i);';assert text.count(needle)==1
    text=text.replace(needle,needle+'\n    if(PrototypeBounceOutputMute(dsp,i))continue;')
    for old,new in (
        ('void dsp_reset(Dsp* dsp) {','void dsp_reset(Dsp* dsp) {\n  PrideSemanticReset();'),
        ('    case 0x4c: {','    case 0x4c: {\n      PrideSemanticLatchKon(val);'),
        ('      dsp->channel[ch].keyOn = false;','      dsp->channel[ch].keyOn = false;\n      PrideSemanticCommit(ch);')):
        assert text.count(old)==1; text=text.replace(old,new)
    dsp=out/'dsp.c';dsp.write_text(text)
    original_audio=Path(audio_row['file']);text=original_audio.read_text()
    needle='            cpu->A=0;';assert text.count(needle)==1
    text=text.replace(needle,'            if(strcmp(cues[i].id,"audio.effects.simba.bounce"))cpu->A=0;')
    envelope=ROOT/'tools/native_bounce_audio_envelope.h'
    names=('HistorySize','SaveHistory','ValidateHistory','LoadHistory')
    prefix=''.join('#define TlkAudio'+name+' PrideBaseAudio'+name+'\n' for name in names)
    text=prefix+text+'\n#include "'+envelope.as_posix()+'"\n'
    audio=out/'audio.c';audio.write_text(text)
    original_spc=Path(spc_row['file']);text=original_spc.read_text()
    old='  uint8_t opcode = spc_readOpcode(spc);';assert text.count(old)==1
    text=text.replace(old,'  PrideSemanticSpc(spc->pc,spc->a,spc->x,spc->y,spc->apu->ram);\n'+old)
    old='#include "apu.h"';assert text.count(old)==1
    text=text.replace(old,old+'\nextern void PrideSemanticSpc(unsigned,unsigned,unsigned,unsigned,const uint8_t *);')
    spc=out/'spc.c';spc.write_text(text)
    generated=[];generated_paths=[]
    for suffix,pc in (('/bankc2_part13_v2.c',0xc21c90),('/bankc2_part14_v2.c',0xc2212e)):
        row=core(suffix);original=Path(row['file']);text=original.read_text()
        declaration='extern void PrideSemanticCpu(CpuState *,unsigned);'
        text=text.replace('#include "cpu_state.h"','#include "cpu_state.h"\n'+declaration)
        anchor=f'    cpu_trace_block(cpu, 0x{pc:06X});';assert text.count(anchor)==1
        start=text.index(anchor);at=text.index('    cpu->coprocessor_master_cycles = cpu->master_cycles;',start)
        text=text[:at]+f'    PrideSemanticCpu(cpu,0x{pc:06x});\n'+text[at:]
        extra_pcs=(0xc21ebf,0xc21e15) if pc==0xc21c90 else ()
        for extra in extra_pcs:
            anchor=f'    cpu_trace_block(cpu, 0x{extra:06X});';positions=[];start=0
            while True:
                start=text.find(anchor,start)
                if start<0:break
                positions.append(text.index('    cpu->coprocessor_master_cycles = cpu->master_cycles;',start));start+=len(anchor)
            assert positions
            for at in reversed(positions):text=text[:at]+f'    PrideSemanticCpu(cpu,0x{extra:06x});\n'+text[at:]
        previous=0xc21953 if pc==0xc21c90 else 0xc22347
        matches=[line for line in text.splitlines(keepends=True) if f'0x{previous:06X}u)' in line]
        assert len(matches)==1
        callback=0xc21955 if pc==0xc21c90 else 0xc22349
        text=text.replace(matches[0],matches[0]+f'    PrideSemanticCpu(cpu,0x{callback:06x});\n')
        copy=out/original.name;copy.write_text(text)
        generated.append((original.stem,row,copy));generated_paths.extend((original,copy))
    replacements={};commands={}
    for label,row,source in (('host',host_row,host),('dsp',dsp_row,dsp),('audio',audio_row,audio),('spc',spc_row,spc),*generated):
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
        ROOT/'tools/native_bounce_npc_observer4.c',ownership,lifecycle,continuation,envelope,original_spc,spc,backend,*generated_paths]
    report=dict(result='BUILT',binary_sha256=digest(binary),link_inputs_sha256=inputs,
        replacement_object_count=6,all_other_inputs_identical=True,
        prototype_sample=92,semantic_caller_tracking=True,save_metadata_implemented=True,production_or_framework_submodule_modified=False,
        full_sample_ownership_proven=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},commands=commands)
    assert digest(base/'player.exe')==build['binary_sha256']
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Private semantic prototype built; production unchanged; lifecycle still unverified',flush=True)


if __name__=='__main__':main()
