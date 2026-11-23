/* Source5179: all four shared adult claw callers select C0E286/MD07DF26.
 * This is native54 -> original FM96; cub ledge-contact FM94 is separate. */
static int adult_swipe_choice;
static int adult_swipe_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=0x36 || word(0x2000)!=0xffff ||
       !continue_world_scene() || music_caller(cpu)!=0xc383d6)return 0;
    unsigned actor=word(0x68);
    if(actor!=word(0x6e) || actor<0xb213 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       address(actor+4)!=0xc5858a || address(actor+48)!=0xc3836b || address(actor+14)!=0xc0e286)return 0;
    unsigned draw=word(actor+12);
    if(draw<0x8000 || draw>0xffe8 || word(draw+4)!=actor+8)return 0;
    unsigned selected=TlkResourcesUseMd("audio.effects.simba.adult_swipe");
    unsigned emitted=selected && word(0x1ff96) && TlkMdSoundReady();
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *p=getenv("TLK_ADULT_SWIPE_AUDIO_TRACE");if(p)log=fopen(p,"w");
        if(log)fputs("field,actor,descriptor,action,stream,caller,selected,emitted,selector,value\n",log);}
    if(log){fprintf(log,"%u,%04x,c5858a,c3836b,c0e286,c383d6,%u,%u,2,96\n",snes_frame_counter+1,actor,selected,emitted);fflush(log);}
    if(!emitted)return 0;
    cpu->A=0;TlkMdSoundCommand(2,96);effect_tail();return 1;
}
