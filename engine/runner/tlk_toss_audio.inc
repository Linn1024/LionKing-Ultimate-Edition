/* Original MD1B479A catch effect, before reward/harmful-bug handling.
 * Included by the audio owner: no guest position, scoring or timing writes. */
static int toss_catch_owner(unsigned actor) {
    if(word(0x1ff9e)!=10 || address(0xdf)!=0xc005dd ||
       address(0xb217)!=0xc5858a || word(0xa93)!=1 ||
       actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127))return 0;
    unsigned descriptor=cw_descriptor(actor),draw=word(actor+12);
    return descriptor>=0xc58999 && descriptor<=0xc58a05 &&
        !((descriptor-0xc58999)%12) && address(actor+48)==0xc5452c &&
        draw>=0x8000 && draw<=0xffe8 && word(draw+4)==actor+8;
}
static int toss_chew_opcode(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=6 || music_caller(cpu)!=0xc53d73 ||
       cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       word(0x1ff9e)!=10 || address(0xdf)!=0xc005dd || word(0x68)!=0xb213 ||
       address(0xb217)!=0xc5858a || address(0xb243)!=0xc53d0c ||
       address(0xb221)!=0xc261e1 || word(0xb23f)!=56 || word(0xa93))return 0;
    unsigned draw=word(0xb21f);
    if(draw<0x8000 || draw>0xffe8 || word(draw+4)!=0xb21b)return 0;
    int selected=TlkResourcesUseMd("audio.effects.bonus.toss_chew");
    int emitted=selected && word(0x1ff96) && TlkMdSoundReady();
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *path=getenv("TLK_TOSS_CHEW_TRACE");if(path)log=fopen(path,"w");
        if(log)fputs("field,caller,actor,timer,source_md,emitted\n",log);}
    if(log){fprintf(log,"%u,c53d73,b213,56,%u,%u\n",(unsigned)snes_frame_counter+1,selected,emitted);fflush(log);}
    if(emitted){TlkMdSoundCommand(19,12);effect_tail();hunt_fx=1;cpu->A=0;}
    return emitted;
}
static int toss_reward_audio_opcode(CpuState *cpu,uint32_t pc){
    if(pc!=0xc22c2c || cpu->X!=8 || cpu->DB!=0x7e || cpu->m_flag ||
       cpu->x_flag || cpu->_flag_D)return 0;
    unsigned actor=word(0x68);
    if(!toss_catch_owner(actor))return 0;
    unsigned kind=word(actor+42),caller=music_caller(cpu);
    if(!((kind==3 && caller==0xc54c86) || (kind==4 && caller==0xc54ca0) ||
         (kind==5 && caller==0xc54cba)))return 0;
    int selected=TlkResourcesUseMd("audio.effects.bonus.toss_rewards");
    int emitted=selected && word(0x1ff96) && TlkMdSoundReady();
    unsigned selector=kind==5?2:19,value=kind==5?98:15;
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *path=getenv("TLK_TOSS_REWARD_AUDIO_TRACE");if(path)log=fopen(path,"w");
        if(log)fputs("field,caller,actor,kind,selector,value,source_md,emitted\n",log);}
    if(log){fprintf(log,"%u,%06x,%04x,%u,%u,%u,%u,%u\n",(unsigned)snes_frame_counter+1,caller,actor,kind,selector,value,selected,emitted);fflush(log);}
    if(emitted){TlkMdSoundCommand(selector,value);effect_tail();hunt_fx=1;cpu->A=0;}
    return emitted;
}
static int toss_audio_opcode(CpuState *cpu,uint32_t pc) {
    if(toss_chew_opcode(cpu,pc))return 1;
    if(toss_reward_audio_opcode(cpu,pc))return 1;
    if(pc!=0xc545fb && pc!=0xc22c2c)return 0;
    if(cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D)return 0;
    unsigned actor=word(0x68);
    if(!toss_catch_owner(actor))return 0;
    int selected=TlkResourcesUseMd("audio.effects.bonus.toss_collect");
    int enabled=word(0x1ff96) && TlkMdSoundReady();
    int muted=pc==0xc22c2c && cpu->X==5 && music_caller(cpu)==0xc54ce9 && selected && enabled;
    int emitted=pc==0xc545fb && selected && enabled;
    if(pc==0xc545fb || muted) {
        static FILE *log;static int opened;
        if(!opened){opened=1;const char *path=getenv("TLK_TOSS_AUDIO_TRACE");if(path)log=fopen(path,"w");
            if(log)fputs("field,event,actor,descriptor,kind,source_md,emitted,muted\n",log);}
        if(log){fprintf(log,"%u,%s,%04x,%06x,%u,%u,%u,%u\n",(unsigned)snes_frame_counter+1,
            pc==0xc545fb?"catch":"native_cue",actor,cw_descriptor(actor),word(actor+42),selected,emitted,muted);fflush(log);}
    }
    if(emitted){
        TlkMdSoundCommand(2,93);effect_tail();
        /* Existing bounded bonus-effect ownership preserves the song/driver
         * during the effect, including independently selected native music. */
        hunt_fx=1;
    }
    if(muted)cpu->A=0;
    return pc==0xc545fb || muted;
}
