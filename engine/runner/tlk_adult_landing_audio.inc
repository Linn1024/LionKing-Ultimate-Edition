/* Native C0EEB6 calls C070D4 three times during the landing animation.
 * Original MD07E184 has only image/duration records and its loop: no thud.
 * Keep this distinct from program17's existing landing owner and hyena PCM4. */
static int adult_landing_thud_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=63 || cpu->DB!=0x7e || cpu->m_flag ||
       cpu->x_flag || cpu->_flag_D || music_caller(cpu)!=0xc070ed ||
       word(0x2000)!=0xffff || !continue_world_scene() || word(0x68)!=0xb213 ||
       address(0xb217)!=0xc5858a || address(0xb243)!=0xc362ec)return 0;
    unsigned cursor=address(0xb225);
    if(cursor<0xc0eeb6 || cursor>=0xc0ef04)return 0;
    unsigned selected=TlkResourcesUseMd("audio.effects.simba.adult_landing");
    unsigned muted=selected && word(0x1ff96) && TlkMdSoundReady();
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *p=getenv("TLK_ADULT_LANDING_THUD_TRACE");if(p)log=fopen(p,"w");
        if(log)fputs("field,level,actor,action,caller,event,parameter,source_md,muted\n",log);}
    if(log){fprintf(log,"%u,%u,b213,c362ec,c070ed,63,%u,%u,%u\n",snes_frame_counter+1,
        word(0x1ff9e),cpu->A,selected,muted);fflush(log);}
    if(!muted)return 0;
    cpu->A=0;return 1; /* Two-argument request: retain native queue at zero volume. */
}
