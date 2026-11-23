/* Source5220: both sides of MD1AD028 request PCM13 with priority80. */
static int big_cat_hit_choice;
static int big_cat_hit_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=63 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D)return 0;
    unsigned actor=word(0x68),caller=music_caller(cpu);
    if((caller!=0xc5dea1 && caller!=0xc5deee) || !big_cat_actor(actor))return 0;
    unsigned selected=TlkResourcesUseMd("audio.effects.world.big_cat_hit");
    unsigned emitted=selected && word(0x1ff96) && TlkMdSoundReady();
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *p=getenv("TLK_BIG_CAT_HIT_TRACE");if(p)log=fopen(p,"w");
        if(log)fputs("field,actor,descriptor,action,caller,selected,emitted,value,parameter\n",log);}
    if(log){fprintf(log,"%u,%04x,%06x,%06x,%06x,%u,%u,13,80\n",snes_frame_counter+1,actor,address(actor+4),address(actor+48),caller,selected,emitted);fflush(log);}
    if(!emitted)return 0;
    cpu->A=0;TlkMdSoundPcm(13,80);effect_tail();return 1;
}
