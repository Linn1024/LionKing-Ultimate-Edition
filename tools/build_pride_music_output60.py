"""Private output-only Pride music filter; observe unsupported echo states."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv, digest
from pride_arena_history import bound


FILTER = r'''
#include "common_rtl.h"
extern unsigned PrivateMusicGroup(unsigned);
extern int PrivateMusicSelected(void);
typedef struct { unsigned long long cycles,music,audible_music,muted,echo_blocked,unknown,fx,audible_fx; } MusicStats;
static MusicStats music_stats[8192];
static void PrivateMusicReport(void) {
    const char *path=getenv("TLK_MUSIC_OUTPUT_STATS");if(!path)return;
    FILE *f=fopen(path,"w");if(!f)exit(96);
    fputs("field,cycles,music,audible_music,muted,echo_blocked,unknown,fx,audible_fx\n",f);
    for(unsigned i=0;i<8192;i++) {
        const MusicStats *s=music_stats+i;if(!s->cycles)continue;
        fprintf(f,"%u,%llu,%llu,%llu,%llu,%llu,%llu,%llu,%llu\n",i,s->cycles,s->music,
            s->audible_music,s->muted,s->echo_blocked,s->unknown,s->fx,s->audible_fx);
    }
    fclose(f);
}
static int PrivateMusicFilter(Dsp *dsp,unsigned ch) {
    unsigned scene=g_ram[0xdf]|(unsigned)g_ram[0xe0]<<8|(unsigned)g_ram[0xe1]<<16;
    if(g_ram[0x1ff9e] || g_ram[0x1ff9f] || (scene!=0xc00387 && scene!=0xc0080d))return 0;
    static int installed;if(!installed){atexit(PrivateMusicReport);installed=1;}
    unsigned field=(unsigned)snes_frame_counter+1;
    unsigned group=PrivateMusicGroup(ch);
    int selected=PrivateMusicSelected();
    /* Canonical synthesis and echo continue unchanged. This prototype only
     * substitutes dry output where echo contributes exactly zero. */
    int zero_echo=!dsp->echoVolumeL && !dsp->echoVolumeR;
    int mute=selected && group==0xe0 && zero_echo;
    if(field<8192) {
        MusicStats *s=music_stats+field;
        int audible=dsp->channel[ch].sampleOut && (dsp->channel[ch].volumeL || dsp->channel[ch].volumeR);
        if(!ch)s->cycles++;
        if(group==0xe0){s->music++;s->audible_music+=audible;s->muted+=mute;s->echo_blocked+=selected && !zero_echo;}
        else if(group==0){s->fx++;s->audible_fx+=audible;}
        else s->unknown+=audible;
    }
    return mute;
}
'''


def main():
    parent=ROOT/'build/pride-music-owner59';bp=parent/'build-report.json';prior=bound(bp)
    ap=ROOT/'build/pride-music-transport59/build-report.json';audio=bound(ap)
    publicpath=ROOT/'build/pride-checkpoint-capability53/build-report.json';public=bound(publicpath)
    out=ROOT/'build/pride-music-output61';out.mkdir();cwd=ROOT/'build/pride-sprite-fresh44'
    rows=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=cwd))
    dsp_row,=[r for r in rows if r.get('output','').endswith('/tlk-runtime/dsp.c.obj')
              and (cwd/r['output']).resolve().relative_to(ROOT).as_posix() in prior['link_inputs_sha256']]
    dsp_original=Path(dsp_row['file']);dsp_text=dsp_original.read_text()
    anchor='void dsp_cycle(Dsp* dsp) {';assert dsp_text.count(anchor)==1
    dsp_text=dsp_text.replace(anchor,FILTER+'\n'+anchor)
    anchor='    dsp_cycleChannel(dsp, i);';assert dsp_text.count(anchor)==1
    dsp_text=dsp_text.replace(anchor,anchor+'\n    if(PrivateMusicFilter(dsp,i))continue;')
    (out/'dsp.c').write_text(dsp_text)
    owner_original=parent/'owner.c'
    (out/'owner.c').write_text(owner_original.read_text()+'\nunsigned PrivateMusicGroup(unsigned channel) { return s_sem_driver_valid && channel<8?music_voice[channel]:256; }\n')
    audio_original=ROOT/'build/pride-music-transport59/audio.c'
    (out/'audio.c').write_text(audio_original.read_text()+'\nint PrivateMusicSelected(void) { return music_active && selected_music() && TlkMdSoundReady(); }\n')
    inputs=argv('link '+(parent/'link.rsp').read_text())[1:];compiles={}
    tasks=[('audio',audio['compile'],ROOT/'build/pride-music-transport59/audio.obj'),
           ('owner',prior['compile'],parent/'owner.obj'),
           ('dsp',argv(dsp_row['command']),(cwd/dsp_row['output']).resolve())]
    for label,template,old in tasks:
        cmd=template.copy()
        for flag,value in [('-c',out/(label+'.c')),('-o',out/(label+'.obj')),('-MT',out/(label+'.obj')),('-MF',out/(label+'.d'))]:cmd[cmd.index(flag)+1]=str(value)
        with (out/(label+'-compile.log')).open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old]
        assert len(indices)==1,(label,indices);inputs[indices[0]]=(out/(label+'.obj')).as_posix();compiles[label]=cmd
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    for name in ('genesis_plus_gx_libretro.dll','save-contract.json'):shutil.copyfile(parent/name,out/name)
    linked={(cwd/p).resolve().relative_to(ROOT).as_posix():digest(cwd/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
    unchanged=sum(public['link_inputs_sha256'].get(p)==sha for p,sha in linked.items())
    assert unchanged==319 and len(linked)==322
    paths=[Path(__file__),bp,ap,publicpath,dsp_original,owner_original,audio_original,rsp,*[out/(label+'.c') for label,_,_ in tasks]]
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,link_inputs_sha256=linked,
                unchanged_public_inputs=unchanged,output_only_prototype=True,echo_nonzero_not_filtered=True,
                ownership_resume_not_implemented=True,production_or_framework_sources_modified=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');print('BUILT',report['binary_sha256'],flush=True)


if __name__=='__main__':main()
