/* The shared adult injury already emits the selected Hurt voice at C35CA7.
 * C35B4B adds a separate native63 impact in the knockback entry. Original
 * shared MD196AC8 owns one PCM1/96 request, not this second SNES impact. */
static int adult_hurt_impact_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=63 || cpu->A!=120 || cpu->DB!=0x7e ||
       cpu->m_flag || cpu->x_flag || cpu->_flag_D || word(0x2000)!=0xffff ||
       !continue_world_scene() || word(0x1ff9e)<6 || word(0x1ff9e)>9 ||
       word(0x68)!=0xb213 || address(0xb217)!=0xc5858a ||
       address(0xb243)!=0xc35adf || music_caller(cpu)!=0xc35b4b)return 0;
    unsigned selected=TlkResourcesUseMd("audio.effects.simba.hurt");
    unsigned suppressed=selected && word(0x1ff96) && TlkMdSoundReady();
    static FILE *log;static int opened;
    if(!opened){opened=1;const char*p=getenv("TLK_ADULT_HURT_IMPACT_TRACE");if(p)log=fopen(p,"w");
        if(log)fputs("field,level,caller,selected,suppressed\n",log);}
    if(log){fprintf(log,"%u,%u,c35b4b,%u,%u\n",snes_frame_counter+1,word(0x1ff9e),selected,suppressed);fflush(log);}
    if(!suppressed)return 0;
    cpu->A=0;return 1;
}
