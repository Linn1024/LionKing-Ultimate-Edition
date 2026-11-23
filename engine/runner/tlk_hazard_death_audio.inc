/* Source5081: shared water/lava death, native28 -> original MD FM103.
 * Initial cue precedes health0 and the late skip-display flag in both games. */
static int hazard_death_choice;
static int hazard_death_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=0x1c)return 0;
    unsigned level=word(0x1ff9e),scene=address(0xdf),actor=word(0x68);
    if(level>=10 || (scene!=0xc00387+level*50 && (level || scene!=0xc0080d)) ||
       actor!=word(0x6e) || actor<0xb213 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       address(actor+4)!=0xc5858a || address(actor+48)!=0xc3857f ||
       word(actor+44)!=0 || music_caller(cpu)!=0xc38608)return 0;
    unsigned selected=TlkResourcesUseMd("audio.effects.simba.hazard_death");
    unsigned emitted=selected && word(0x1ff96) && TlkMdSoundReady();
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *p=getenv("TLK_HAZARD_DEATH_AUDIO_TRACE");if(p)log=fopen(p,"w");
        if(log)fputs("field,level,actor,age,action,caller,selected,emitted,value\n",log);}
    if(log){fprintf(log,"%u,%u,%04x,%u,c3857f,c38608,%u,%u,103\n",
        snes_frame_counter+1,level,actor,word(0x2000),selected,emitted);fflush(log);}
    if(!emitted)return 0;
    cpu->A=0;TlkMdSoundCommand(2,103);effect_tail();return 1;
}
