/* MD1CB090: FA1CB056, ten eleven-update drawings, then FA1CB06C.
 * SNES C1AAB9 submits its single original voice program. */
static unsigned destiny_speech_active,destiny_speech_age,destiny_speech_actor;
static unsigned destiny_speech_second,destiny_speech_choice;
static void destiny_speech_clear(void) {
    destiny_speech_active=destiny_speech_age=destiny_speech_actor=destiny_speech_second=0;
}
static void destiny_speech_trace(const char *event) {
    static FILE *log;static int checked;
    if(!checked){checked=1;const char *p=getenv("TLK_DESTINY_SPEECH_TRACE");if(p)log=fopen(p,"w");
        if(log)fputs("field,event,actor,age,second\n",log);}
    if(log){fprintf(log,"%u,%s,%04x,%u,%u\n",frame,event,destiny_speech_actor,destiny_speech_age,destiny_speech_second);fflush(log);}
}
static int destiny_speech_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=2 || !destiny() || word(0x2000)!=65535 ||
       music_caller(cpu)!=0xc1aab9 || !TlkResourcesUseMd("audio.voices.mufasa_destiny") ||
       !word(0x1ff96) || !TlkMdSoundReady())return 0;
    unsigned actor=word(0x68);
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       address(actor+48)!=0xc1aa3f || address(0xb243)!=0xc1a8c8)return 0;
    cpu->A=0;destiny_speech_active=1;destiny_speech_age=destiny_speech_second=0;destiny_speech_actor=actor;
    TlkMdSoundDestinySpeechSample(0);effect_tail();destiny_speech_trace("first");return 1;
}
static void destiny_speech_frame(void) {
    if(!destiny_speech_active)return;
    if(!destiny() || !word(0x2004) || !word(0x1ff96) ||
       !TlkResourcesUseMd("audio.voices.mufasa_destiny") ||
       address(0xb243)!=0xc1a8c8 || address(destiny_speech_actor+48)!=0xc1aa3f){
        TlkMdSoundInterlevelStop();destiny_speech_trace("stop");destiny_speech_clear();return;
    }
    effect_tail();if(word(0xa89))return;
    if(destiny_speech_age<TLK_DESTINY_SPEECH_SECOND_DELAY)destiny_speech_age++;
    if(!destiny_speech_second && destiny_speech_age==TLK_DESTINY_SPEECH_SECOND_DELAY){
        destiny_speech_second=1;TlkMdSoundDestinySpeechSample(1);destiny_speech_trace("second");
    }
}
