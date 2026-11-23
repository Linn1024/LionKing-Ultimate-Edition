/* Source5551: original1AA724 ->1AA6A0 has no defeat voice. Native adds63
 * immediately after entering C38CC1. Other native63 callers are independent. */
static int prepared_leaper_defeat_choice;
static int prepared_leaper_defeat_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=63 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       word(0x1ff9e)!=7 || address(0xdf)!=0xc004e5)return 0;
    unsigned caller=music_caller(cpu);
    if(caller!=0xc38dec && caller!=0xc38f37)return 0;
    unsigned actor=word(0x68);
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       address(actor+4)!=0xc587d6 || address(actor+48)!=0xc38cc1 || address(actor+14)!=0xc25947)return 0;
    unsigned draw=word(actor+12);
    if(draw<0x8000 || draw>0xffe8 || word(draw+4)!=actor+8)return 0;
    unsigned selected=TlkResourcesUseMd("audio.effects.world.be_prepared.leaper_defeat");
    unsigned suppress=selected && word(0x1ff96) && TlkMdSoundReady();
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *p=getenv("TLK_LEAPER_DEFEAT_AUDIO_TRACE");if(p)log=fopen(p,"w");
        if(log)fputs("field,actor,descriptor,action,stream,caller,selected,suppressed\n",log);}
    if(log){fprintf(log,"%u,%04x,c587d6,c38cc1,c25947,%06x,%u,%u\n",snes_frame_counter+1,actor,caller,selected,suppress);fflush(log);}
    if(!suppress)return 0;
    cpu->A=0;return 1;
}
