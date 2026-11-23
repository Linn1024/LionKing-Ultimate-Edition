/* Original SNES illustrations keep their native animation/event ownership.
 * Replace only their dialogue requests with the corresponding Genesis clips. */
static unsigned native_story_audio_kind;
static unsigned native_story_context(void) {
    if(!word(0x1ff96) || !TlkMdSoundReady())return 0;
    if(address(0xdf)==0xc005ab && word(0x1ff9e)==0 &&
       !TlkResourcesUseMd("gameplay.levels.pride_lands.interlevel_scene") &&
       TlkResourcesUseMd("audio.effects.interlevel.pride_lands"))return 1;
    if(address(0xdf)==0xc0070e && word(0x1ff9e)==15 &&
       !TlkResourcesUseMd("gameplay.levels.stampede.exit_flow") &&
       TlkResourcesUseMd("audio.effects.interlevel.stampede"))return 2;
    return 0;
}
static int native_story_owner(unsigned kind,unsigned actor) {
    return actor>=0xb293 && actor<0xdc13 && !((actor-0xb213)&127) &&
        address(actor+4)==(kind==1?0xc587b0:0xc58798) &&
        address(actor+48)==(kind==1?0xc4734f:0xc1a81d);
}
static void native_story_trace(const char *event,unsigned kind,unsigned actor,unsigned caller) {
    static FILE *log;static int checked;
    if(!checked){checked=1;const char *p=getenv("TLK_NATIVE_STORY_AUDIO_TRACE");if(p)log=fopen(p,"w");if(log)fputs("field,event,kind,actor,action,caller\n",log);}
    if(log){fprintf(log,"%u,%s,%u,%04x,%06x,%06x\n",(unsigned)snes_frame_counter+1,event,kind,actor,actor?address(actor+48):0,caller);fflush(log);}
}
static int native_story_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c)return 0;
    unsigned kind=native_story_context(),actor=word(0x68),caller=music_caller(cpu);
    if(!kind || !native_story_owner(kind,actor))return 0;
    if(kind==1 && ((caller==0xc473b7 && cpu->X==1) || (caller==0xc473d7 && cpu->X==2))) {
        cpu->A=0;TlkMdSoundInterlevelSample(caller==0xc473d7);effect_tail();native_story_audio_kind=1;
        native_story_trace("cue",kind,actor,caller);return 1;
    }
    if(kind==2 && caller==0xc1a87b && cpu->X==1 && word(actor+46)==3) {
        cpu->A=0;TlkMdSoundCliffSample();effect_tail();native_story_audio_kind=2;
        native_story_trace("cue",kind,actor,caller);return 1;
    }
    return 0;
}
static void native_story_frame(void) {
    unsigned kind=native_story_context(),owner=0;
    if(kind)for(unsigned actor=0xb293;actor<0xdc13;actor+=128)if(native_story_owner(kind,actor)){owner=actor;break;}
    /* Derive ownership from the restored guest, without a new save clock. */
    if(owner){
        if(native_story_audio_kind!=kind){TlkMdSoundCommand(1,0);music_active=pending_stop=0;music_track=0;}
        native_story_audio_kind=kind;effect_tail();
    }
    else if(native_story_audio_kind){TlkMdSoundInterlevelStop();native_story_trace("retire",native_story_audio_kind,0,0);native_story_audio_kind=0;}
}
