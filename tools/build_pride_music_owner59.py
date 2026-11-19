"""Read-only native music/FX group provenance on the no-stop experiment."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv, digest
from pride_arena_history import bound


TRACE = r'''
static unsigned music_candidate[8],music_latched[8],music_voice[8];
static FILE *music_trace;
static void MusicTrace(const char *stage,unsigned ch,unsigned slot,unsigned group,unsigned program,unsigned stream) {
    const char *path=getenv("TLK_MUSIC_OWNER_TRACE");if(!path)return;
    if(!music_trace){music_trace=fopen(path,"w");if(!music_trace)exit(96);
        fputs("field,stage,channel,slot,group,program,stream,scene,level\n",music_trace);}
    fprintf(music_trace,"%u,%s,%u,%u,%u,%u,%u,%u,%u\n",(unsigned)snes_frame_counter+1,
        stage,ch,slot,group,program,stream,SemAddress(0xdf),SemWord(g_ram,0x1ff9e));fflush(music_trace);
}
static void MusicObserve(unsigned pc,unsigned a,unsigned x,unsigned y,const uint8_t *ram) {
    if(pc==0xfd1 && x<22)MusicTrace("software",0,x,ram[0xb],ram[8],SemWord(ram,0x294));
    if(pc==0xd34 && x<8) {
        music_candidate[x]=a<22?ram[0x2e3+a]:0x100;
        MusicTrace("assign",x,a,music_candidate[x],0,0);
    }
}
'''


def main():
    base = ROOT/'build/pride-music-transport59'; bp = base/'build-report.json'; prior = bound(bp)
    out = ROOT/'build/pride-music-owner59'; out.mkdir(); cwd = ROOT/'build/pride-sprite-fresh44'
    rows = json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=cwd))
    row, = [r for r in rows if r.get('output','').endswith('/tlk_native_audio_owner.c.obj')]
    cmd = argv(row['command']); original = Path(row['file']); text = original.read_text()
    anchor = 'static void SemAccepted(CpuState *cpu,uint32_t pc) {'
    assert text.count(anchor)==1; text=text.replace(anchor,TRACE+'\n'+anchor)
    anchor='    if(s_sem_driver_valid)OwnerSpc(pc,a,x,y,ram);'
    assert text.count(anchor)==1
    text=text.replace(anchor,'    if(s_sem_driver_valid){ MusicObserve(pc,a,x,y,ram); OwnerSpc(pc,a,x,y,ram); }')
    anchor='void TlkNativeAudioOwnerLatchKon(unsigned value) {'
    assert text.count(anchor)==1
    text=text.replace(anchor,anchor+'\n    for(unsigned ch=0;ch<8;ch++)music_latched[ch]=(value&(1u<<ch))?music_candidate[ch]:0x100;')
    anchor='        s_sem_voice[ch]=s_sem_latched[ch];'
    assert text.count(anchor)==1
    text=text.replace(anchor,anchor+'\n        music_voice[ch]=music_latched[ch]; MusicTrace("keyon",ch,0,music_voice[ch],0,0);')
    anchor='    s_sem_driver_valid=0;OwnerClear();'
    assert text.count(anchor)==1
    text=text.replace(anchor,anchor+'\n    for(unsigned ch=0;ch<8;ch++)music_candidate[ch]=music_latched[ch]=music_voice[ch]=0x100; MusicTrace("reset",0,0,0x100,0,0);')
    source=out/'owner.c';source.write_text(text)
    for flag,value in [('-c',source),('-o',out/'owner.obj'),('-MT',out/'owner.obj'),('-MF',out/'owner.d')]:cmd[cmd.index(flag)+1]=str(value)
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    inputs=argv('link '+(base/'link.rsp').read_text())[1:]
    old=(cwd/row['output']).resolve()
    indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old]
    assert len(indices)==1;inputs[indices[0]]=(out/'owner.obj').as_posix()
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    for name in ('genesis_plus_gx_libretro.dll','save-contract.json'):shutil.copyfile(base/name,out/name)
    linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
    unchanged=sum(prior['link_inputs_sha256'].get(p)==sha for p,sha in linked.items())
    assert unchanged==321 and len(linked)==322
    paths=[Path(__file__),bp,original,source,rsp]
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compile=cmd,link_inputs_sha256=linked,
                unchanged_inputs_from_no_stop_experiment=unchanged,read_only_observer=True,
                public_preview_unchanged=True,dual_music_intentional=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
