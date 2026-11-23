/* Original shared adult pounce: native C37F6E/C3804F -> MD198AE6/FM96.
 * Keep the native action/cue timing; other requests for native54 are separate. */
static int adult_pounce_choice;
static int adult_pounce_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=54 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       word(0x2000)!=0xffff || !continue_world_scene() || music_caller(cpu)!=0xc3804f)return 0;
    unsigned actor=word(0x68);
    if(actor!=word(0x6e) || actor!=0xb213 || address(actor+4)!=0xc5858a ||
       address(actor+48)!=0xc37f6e || word(actor+46)!=0)return 0;
    unsigned draw=word(actor+12);
    if(draw<0x8000 || draw>0xffe8 || word(draw+4)!=actor+8)return 0;
    unsigned selected=TlkResourcesUseMd("audio.effects.simba.adult_pounce");
    unsigned emitted=selected && word(0x1ff96) && TlkMdSoundReady();
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *p=getenv("TLK_ADULT_POUNCE_AUDIO_TRACE");if(p)log=fopen(p,"w");
        if(log)fputs("field,actor,descriptor,action,stream,caller,selected,emitted,selector,value\n",log);}
    if(log){fprintf(log,"%u,%04x,c5858a,c37f6e,%06x,c3804f,%u,%u,2,96\n",snes_frame_counter+1,actor,address(actor+14),selected,emitted);fflush(log);}
    if(!emitted)return 0;
    cpu->A=0;TlkMdSoundCommand(2,96);effect_tail();return 1;
}
