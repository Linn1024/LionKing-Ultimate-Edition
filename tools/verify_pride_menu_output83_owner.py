"""Real menu ownership chain plus existing bounce/music lifetime component checks."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

EXTRA=r'''
    file=fopen(argv[2],"rb");CHECK(file);CHECK(fread(ram,1,65536,file)==65536);fclose(file);
    const unsigned callers[]={0xc46849,0xc468a2,0xc467cf,0xc46804,0xc46a56,0xc469db};
    const unsigned kinds[]={1,1,2,2,3,4};
    const char *ids[]={"audio.effects.title_cursor","audio.effects.title_cursor","audio.effects.title_selection","audio.effects.title_selection","audio.effects.options_adjustment","audio.effects.options_exit"};
    for(unsigned row=0;row<6;row++) {
        TlkNativeAudioOwnerReset();memset(g_ram,0,sizeof g_ram);
        unsigned kind=kinds[row],program=(kind==1 || kind==4)?5:6;
        cpu=(CpuState){0};cpu.D=0x1f00;cpu.DB=0x7e;cpu.m_flag=1;cpu.S=0x2ce;
        word(0x1f15,0x8000|program);word(0x1f6d,0);word(0x1ff96,1);
        address(0xdf,0xc005ab);address(cpu.S+17,callers[row]-1);
        uint8_t before[131072];memcpy(before,g_ram,sizeof before);CpuState old=cpu;
        SemAccepted(&cpu,0xc21c90);
        CHECK(!memcmp(before,g_ram,sizeof before));CHECK(!memcmp(&old,&cpu,sizeof old));
        CHECK(SemKind(atomic_load(&s_sem_queue[0]))==kind);
        cpu.m_flag=0;cpu.Y=0x230;word(0x1f6f,program<<8|2);SemTransfer(&cpu,0xc2212e);
        CHECK(SemKind(atomic_load(&s_sem_ring[44]))==kind);
        ram[8]=program;ram[0x230]=2;ram[0x231]=program;
        unsigned stream=program==5?0x38a2:0x38ba;ram[0x294]=stream;ram[0x295]=stream>>8;
        CHECK(ram[stream-13]==program && ram[stream-12]==1);
        TlkNativeAudioOwnerSpc(0x1bcb,0,0,0,ram);TlkNativeAudioOwnerSpc(0x1be3,0,0,44,ram);
        CHECK(SemKind(s_sem_pending)==kind);
        TlkNativeAudioOwnerSpc(0xfc9,0,8,0,ram);CHECK(SemKind(s_sem_software[8])==kind);
        CHECK(!s_sem_pending);
        TlkNativeAudioOwnerSpc(0xd34,8,7,0,ram);TlkNativeAudioOwnerLatchKon(128);TlkNativeAudioOwnerCommit(7);
        only_id=ids[row];CHECK(TlkNativeAudioOwnerMute(7,62,0));CHECK(!TlkNativeAudioOwnerMute(6,62,0));
        CHECK(!TlkNativeAudioOwnerMute(7,62,1));only_id="unselected";CHECK(!TlkNativeAudioOwnerMute(7,62,0));only_id=ids[row];
        ready=0;CHECK(!TlkNativeAudioOwnerMute(7,62,0));ready=1;
        word(0x1ff9e,1);CHECK(!TlkNativeAudioOwnerMute(7,62,0));word(0x1ff9e,0);
        word(0x1ff96,0);CHECK(!TlkNativeAudioOwnerMute(7,62,0));word(0x1ff96,1);
        address(0xdf,0xc105ab);CHECK(!TlkNativeAudioOwnerMute(7,62,0));address(0xdf,0xc005ab);
        CHECK(TlkNativeAudioOwnerSave(saved,896));CHECK(!memcmp(saved,"SEMOWN03",8));
        TlkNativeAudioOwnerReset();CHECK(TlkNativeAudioOwnerLoad(saved,896));CHECK(TlkNativeAudioOwnerMute(7,62,0));
        CHECK(TlkNativeAudioOwnerSave(again,896));CHECK(!memcmp(saved,again,896));
        memcpy(invalid,saved,896);SemPut32(invalid+768,0x50000001);CHECK(!TlkNativeAudioOwnerValidate(invalid,896));
        memcpy(invalid,saved,896);SemPut32(invalid+768,0x10000000);CHECK(!TlkNativeAudioOwnerValidate(invalid,896));
        TlkNativeAudioOwnerSpc(0xd34,9,7,0,ram);CHECK(TlkNativeAudioOwnerMute(7,62,0));
        TlkNativeAudioOwnerLatchKon(128);TlkNativeAudioOwnerCommit(7);CHECK(!TlkNativeAudioOwnerMute(7,62,0));
        only_id=NULL;
    }
'''


def main():
    original=ROOT/'build/pride-music-output65/component/report.json';r=bound(original)
    assert r['result']=='PASS';template=original.parent/'component.c'
    text=template.read_text().replace('CHECK(argc==2)','CHECK(argc==3)')
    text=text.replace('int TlkMdSoundReady(void) { return 1; }','static int ready=1;\nint TlkMdSoundReady(void) { return ready; }')
    text=text.replace('int TlkResourcesUseMd(const char *id) { return 1; }','static const char *only_id;\nint TlkResourcesUseMd(const char *id) { return !only_id || !strcmp(id,only_id); }')
    anchor='    printf("PASS %u maintained ownership checks'
    assert text.count(anchor)==1;text=text.replace(anchor,EXTRA+'\n'+anchor)
    out=ROOT/'build/pride-menu-output83-owner-component';out.mkdir();source=out/'component.c';source.write_text(text)
    cmd=r['command'].copy()
    cmd=[str(source) if x==str(template) else str(out/'component.exe') if x==str(original.parent/'component.exe') else x for x in cmd]
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    fixture=Path(r['command'][0]) # Compiler command does not contain runtime arguments.
    fixture=ROOT/'build/pride-lizard-launch-work/player/spc-voice-owner-audit/native/aram_1400.bin'
    menu=ROOT/'build/pride-menu-spc82/native/dispatch-592-5.aram'
    run=subprocess.run([str(out/'component.exe'),str(fixture),str(menu)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    (out/'run.log').write_text(run.stdout)
    paths=[Path(__file__),original,template,source,fixture,menu,ROOT/'engine/runner/tlk_native_audio_owner.c']
    report=dict(result='PASS' if run.returncode==0 else 'FAIL',output=run.stdout,command=cmd,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],run.stdout,flush=True)
    assert run.returncode==0


if __name__=='__main__':main()
