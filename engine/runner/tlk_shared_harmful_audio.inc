/* Source5106: main-world marker19 shares C55614/MD18FA9C in every level.
 * Bonus Hunt keeps its own independent harmful-contact source option. */
static int shared_harmful_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=0x12 || !TlkDefeatAudioScene(g_ram))return 0;
    unsigned actor=word(0x68);
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       address(actor+4)!=0xc58975 || music_caller(cpu)!=0xc5565b)return 0;
    unsigned draw=word(actor+12);
    if(draw<0x8000 || draw>0xffe8 || word(draw+4)!=actor+8 || address(draw+10)!=0xc5293f)return 0;
    unsigned selected=TlkResourcesUseMd("audio.effects.world.harmful_bug");
    unsigned emitted=selected && word(0x1ff96) && TlkMdSoundReady();
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *p=getenv("TLK_SHARED_HARMFUL_AUDIO_TRACE");if(p)log=fopen(p,"w");
        if(log)fputs("field,level,actor,descriptor,caller,selected,emitted,value\n",log);}
    if(log){fprintf(log,"%u,%u,%04x,c58975,c5565b,%u,%u,117\n",snes_frame_counter+1,word(0x1ff9e),actor,selected,emitted);fflush(log);}
    if(!emitted)return 0;
    cpu->A=0;TlkMdSoundCommand(2,117);effect_tail();return 1;
}
