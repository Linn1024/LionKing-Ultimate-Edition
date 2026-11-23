/* Shared lava-bubble C400E4/MD1AF85A: original MD has no peak sound. */
static int lava_bubble_choice;
static int lava_bubble_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=15 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       !TlkDefeatAudioScene(g_ram) || music_caller(cpu)!=0xc401de)return 0;
    unsigned actor=word(0x68);
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) || address(actor+4)!=0xc5878c ||
       address(actor+48)!=0xc400e4 || word(actor+44)!=9 || word(actor+46))return 0;
    unsigned selected=TlkResourcesUseMd("audio.effects.world.lava_bubbles");
    unsigned suppressed=selected && word(0x1ff96) && TlkMdSoundReady();
    static FILE *log;static int opened;
    if(!opened){opened=1;const char*p=getenv("TLK_LAVA_BUBBLE_AUDIO_TRACE");if(p)log=fopen(p,"w");
        if(log)fputs("field,level,actor,descriptor,action,caller,selected,suppressed\n",log);}
    if(log){fprintf(log,"%u,%u,%04x,c5878c,c400e4,c401de,%u,%u\n",snes_frame_counter+1,word(0x1ff9e),actor,selected,suppressed);fflush(log);}
    if(!suppressed)return 0;
    cpu->A=0;return 1;
}
