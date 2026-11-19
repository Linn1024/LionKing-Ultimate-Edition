"""Read-only output-filter echo and Continue-boundary diagnostics on candidate62."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


OBSERVER=r'''
#include "common_rtl.h"
#include "tlk_audio.h"
#include "snes/snes.h"
#include "snes/apu.h"
#include "snes/dsp.h"
extern Snes *g_snes;
extern int __real_TlkNativeAudioOwnerMusicMute(unsigned,int,int);
static struct {unsigned long long calls,filtered,echo_nonzero;} stats[8192][3];
static FILE *trace;
static void FinishMusicStats(void) {
    const char *path=getenv("TLK_MUSIC_OUTPUT_STATS");if(!path)return;
    FILE *f=fopen(path,"w");if(!f)exit(96);
    fputs("field,scene,calls,filtered,echo_nonzero\n",f);
    const unsigned scenes[]={0xc00387,0xc0080d,0xc0057b};
    for(unsigned i=0;i<8192;i++)for(unsigned j=0;j<3;j++)if(stats[i][j].calls)
        fprintf(f,"%u,%u,%llu,%llu,%llu\n",i,scenes[j],stats[i][j].calls,stats[i][j].filtered,stats[i][j].echo_nonzero);
    fclose(f);if(trace)fclose(trace);
}
int __wrap_TlkNativeAudioOwnerMusicMute(unsigned ch,int l,int r) {
    int result=__real_TlkNativeAudioOwnerMusicMute(ch,l,r);
    unsigned field=(unsigned)snes_frame_counter+1;
    unsigned scene=g_ram[0xdf]|(unsigned)g_ram[0xe0]<<8|(unsigned)g_ram[0xe1]<<16;
    int selected=TlkAudioNativeMusicSelected();
    static int installed;if(!installed){atexit(FinishMusicStats);installed=1;}
    unsigned context=scene==0xc00387?0:scene==0xc0080d?1:scene==0xc0057b?2:3;
    if(field<8192 && context<3 && selected) {
        stats[field][context].calls++;stats[field][context].filtered+=result;
        stats[field][context].echo_nonzero+=!!(l || r);
    }
    static unsigned lastfield[8];static int lastresult[8],lastselected[8];
    if(ch<8 && field>=4545 && field<=4549 &&
       (lastfield[ch]!=field || lastresult[ch]!=result || lastselected[ch]!=selected)) {
        const char *path=getenv("TLK_MUSIC_OUTPUT_EDGE");
        if(path && !trace){trace=fopen(path,"w");if(!trace)exit(96);
            fputs("field,scene,channel,muted,selected,echo_l,echo_r,sample_write,apu_clock,srcn,gain,sample,volume_l,volume_r\n",trace);}
        if(trace && g_snes && g_snes->apu && g_snes->apu->dsp) {
            Dsp *d=g_snes->apu->dsp;DspChannel *c=d->channel+ch;
            fprintf(trace,"%u,%u,%u,%d,%d,%d,%d,%u,%llu,%u,%u,%d,%d,%d\n",field,scene,ch,result,selected,l,r,
                d->sampleWrite,(unsigned long long)g_snes->apu->portClock,c->srcn,c->gain,c->sampleOut,c->volumeL,c->volumeR);fflush(trace);
        }
        lastfield[ch]=field;lastresult[ch]=result;lastselected[ch]=selected;
    }
    return result;
}
'''


def main():
    base=ROOT/'build/pride-music-output62';bp=base/'build-report.json';prior=bound(bp)
    out=ROOT/'build/pride-music-observer63';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
    source=out/'observer.c';source.write_text(OBSERVER);cmd=prior['compiles']['owner'].copy()
    for flag,value in [('-c',source),('-o',out/'observer.obj'),('-MT',out/'observer.obj'),('-MF',out/'observer.d')]:cmd[cmd.index(flag)+1]=str(value)
    with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    inputs=argv('link '+(base/'link.rsp').read_text())[1:];inputs.extend([(out/'observer.obj').as_posix(),'-Wl,--wrap=TlkNativeAudioOwnerMusicMute'])
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    for name in ('genesis_plus_gx_libretro.dll','save-contract.json'):shutil.copyfile(base/name,out/name)
    linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
    assert len(linked)==323 and sum(prior['link_inputs_sha256'].get(p)==sha for p,sha in linked.items())==322
    paths=[Path(__file__),bp,source,rsp]
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compile=cmd,link_inputs_sha256=linked,
                unchanged_candidate_inputs=322,read_only_return_preserving_wrapper=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
