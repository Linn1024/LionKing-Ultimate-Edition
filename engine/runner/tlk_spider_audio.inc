/* Source5011: both originals consume actor+46; native39 becomes MD PCM6/96. */
static int spider_choice;
static int spider_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=0x27 || !hakuna() || word(0x2000))return 0;
    unsigned actor=word(0x68);
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       address(actor+4)!=0xc58e9c || address(actor+48)!=0xc3a1f2 ||
       word(actor+46)!=1 || music_caller(cpu)!=0xc3a327)return 0;
    unsigned draw=word(actor+12);
    if(draw<0x8000 || draw>0xffe8 || word(draw+4)!=actor+8)return 0;
    unsigned pose=address(draw+10);
    if(pose<0xc3b1d5 || pose>=0xc3b300)return 0;
    unsigned selected=TlkResourcesUseMd("audio.effects.world.hakuna.spider");
    unsigned emitted=selected && word(0x1ff96) && TlkMdSoundReady();
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *p=getenv("TLK_SPIDER_AUDIO_TRACE");if(p)log=fopen(p,"w");
        if(log)fputs("field,actor,descriptor,action,phase,caller,selected,emitted,value,parameter\n",log);}
    if(log){fprintf(log,"%u,%04x,c58e9c,c3a1f2,1,c3a327,%u,%u,6,96\n",snes_frame_counter+1,actor,selected,emitted);fflush(log);}
    if(!emitted)return 0;
    cpu->A=0;TlkMdSoundPcm(6,96);effect_tail();return 1;
}
