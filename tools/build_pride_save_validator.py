"""Observe nested save preflight without changing any load result or guest byte."""
from pathlib import Path

original_builder=Path(__file__).with_name('build_pride_rng_allbugs.py')
source=original_builder.read_text().replace("out=parent/'allbugs-observer'", "out=parent/'save-validator'")
helper=r'''
extern int TlkNativeAudioValidateHistory(const uint8_t *,size_t);
extern int TlkMdSoundValidateState(const uint8_t *,size_t);
static void PrideInspectNativeFile(const char *path) {
    const char *log_path=getenv("TLK_SAVE_VALIDATION_LOG");if(!log_path)return;
    size_t size=0;uint8_t *data=read_file(path,&size);if(!data)return;
    FILE *log=fopen(log_path,"a");if(!log)exit(96);
    unsigned view_ok=0,audio_ok=0,native_ok=0,md_ok=0,view_size=0,audio_size=0;
    uint64_t blob=size>=32?TlkGet64(data+24):0;
    size_t at=36+(size_t)blob;
    if(at<size && size-at>=4) {
        view_size=TlkGet32(data+at);at+=4;
        if(view_size<=size-at) { view_ok=TlkWideValidateHistory(data+at,view_size);at+=view_size;
            if(size-at>=4) { audio_size=TlkGet32(data+at);at+=4;
                if(audio_size<=size-at && audio_size>=128) {
                    const uint8_t *audio=data+at;
                    audio_ok=TlkAudioValidateHistory(audio,audio_size);
                    unsigned native=TlkGet32(audio+44),nested=TlkGet32(audio+40);
                    if(native<=audio_size-128) {
                        native_ok=TlkNativeAudioValidateHistory(audio+128,native);
                        if(nested<=audio_size-128-native)md_ok=!nested || TlkMdSoundValidateState(audio+128+native,nested);
                    }
                }
            }
        }
    }
    fprintf(log,"size=%u blob=%u view_size=%u view_ok=%u audio_size=%u audio_ok=%u native_ok=%u md_ok=%u end=%u\n",
            (unsigned)size,(unsigned)blob,view_size,view_ok,audio_size,audio_ok,native_ok,md_ok,(unsigned)(at+audio_size));
    fclose(log);free(data);
}
'''
anchor="    source=out/'host.i';source.write_text(text)"
assert source.count(anchor)==1
insertion="    text=text.replace('static int PrideRestartLoad(const char *path,uint32_t *field) {',"+repr(helper)+"+'\\nstatic int PrideRestartLoad(const char *path,uint32_t *field) {')\n"
insertion+="    text=text.replace('if(ok)ok=__real_tlk_state_load(temporary,&loaded);','if(ok) { PrideInspectNativeFile(temporary);ok=__real_tlk_state_load(temporary,&loaded); }')\n"
source=source.replace(anchor,insertion+anchor)
source=source.replace('paths=[Path(__file__),bp,original,source,backend,',
                      'paths=[Path(__file__),original_builder,bp,original,source,backend,')
exec(compile(source,str(original_builder),'exec'))
