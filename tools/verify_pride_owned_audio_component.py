"""Run lifecycle/serialization checks against the maintained ownership module."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_pride_driver_lifecycle_component import SOURCE


def main():
    out=ROOT/'build/pride-bounce-owner-work/component';out.mkdir()
    source=out/'component.c';exe=out/'component.exe'
    start=SOURCE.index('#define PrideSemanticReset');end=SOURCE.index('static unsigned checks;',start)
    text=SOURCE[:start]+'''#include "tlk_native_audio_owner.c"
Snes *g_snes;
bool interp_bridge_add_pre_opcode_hook(uint32_t pc,InterpPreOpcodeHook hook) { return true; }
int TlkMdSoundReady(void) { return 1; }
int TlkResourcesUseMd(const char *id) { return 1; }
'''+SOURCE[end:]
    text=text.replace('unsigned snes_frame_counter','int snes_frame_counter')
    text=text.replace('uint8_t ram[65536];FILE *file=',
        'Apu *apu=calloc(1,sizeof *apu);Snes snes={0};snes.apu=apu;g_snes=&snes;uint8_t *ram=apu->ram;FILE *file=')
    text=text.replace('fread(ram,1,sizeof ram,file)==sizeof ram','fread(ram,1,65536,file)==65536')
    text=text.replace('    Apu apu={ram};Snes snes={&apu};g_snes=&snes;CpuState cpu={0};','    CpuState cpu={0};')
    replacements={'PrideSemanticVoice':'OwnerVerifiedVoice','PrideSemanticSpc':'TlkNativeAudioOwnerSpc',
        'PrideSemanticLatchKon':'TlkNativeAudioOwnerLatchKon','PrideSemanticCommit':'TlkNativeAudioOwnerCommit'}
    for a,b in replacements.items():text=text.replace(a,b)
    extra=r'''
    accept(&cpu);transfer(&cpu);play(ram);CHECK(OwnerVerifiedVoice(7));
    uint8_t saved[800],again[800],invalid[800];
    CHECK(TlkNativeAudioOwnerStateSize()==800);
    CHECK(TlkNativeAudioOwnerSave(saved,800));TlkNativeAudioOwnerReset();
    CHECK(!OwnerVerifiedVoice(7));CHECK(TlkNativeAudioOwnerLoad(saved,800));
    CHECK(OwnerVerifiedVoice(7));CHECK(TlkNativeAudioOwnerSave(again,800));CHECK(!memcmp(saved,again,800));
    for(unsigned length=0;length<800;length++)CHECK(!TlkNativeAudioOwnerLoad(saved,length));
    memcpy(invalid,saved,800);SemPut32(invalid+24,SemGet32(saved+16)+1);
    CHECK(!TlkNativeAudioOwnerLoad(invalid,800));CHECK(TlkNativeAudioOwnerSave(again,800));CHECK(!memcmp(saved,again,800));
    /* Restored unknown guest code cannot authorize muting a saved voice. */
    ram[0x600]^=1;CHECK(TlkNativeAudioOwnerLoad(saved,800));CHECK(!OwnerVerifiedVoice(7));ram[0x600]^=1;
    CHECK(TlkNativeAudioOwnerLoad(saved,800));CHECK(OwnerVerifiedVoice(7));
'''
    text=text.replace('    printf("PASS %u driver lifecycle checks',extra+'    printf("PASS %u maintained ownership checks')
    source.write_text(text)
    native=ROOT/'engine/snesrecomp/runner/src';runner=ROOT/'engine/runner'
    command=['C:/mingw32/bin/gcc.exe','-std=c11','-O2','-DTLK_NATIVE_AUDIO_OWNER_AVAILABLE=1',
        '-I',str(runner),'-I',str(native),'-I',str(native/'snes'),str(source),str(native/'sha256.c'),'-o',str(exe)]
    with (out/'compile.log').open('wb') as log:
        subprocess.run(command,check=True,stdout=log,stderr=subprocess.STDOUT)
    fixture=ROOT/'build/pride-lizard-launch-work/player/spc-voice-owner-audit/native/aram_1400.bin'
    output=subprocess.check_output([str(exe),str(fixture)],text=True);print(output,end='')
    (out/'run.log').write_text(output)
    paths=[Path(__file__),ROOT/'tools/verify_pride_driver_lifecycle_component.py',
        runner/'tlk_native_audio_owner.c',runner/'tlk_native_audio_owner.h',native/'sha256.c',source,fixture]
    report=dict(result='PASS',output=output,command=command,
        scope='maintained code identity/queue/reset/serialization plus unknown-code restore',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
