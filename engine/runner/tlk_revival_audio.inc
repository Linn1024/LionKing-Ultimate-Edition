/* Sources5123/5127: global revival call, separate from normal roar.
 * Current task68 can be a stale initializer; player6E owns this global cue.
 * Original MD adult path requests10 and then11 at the same ready boundary. */
static int revival_voice_choice;
static int revival_voice_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || !TlkDefeatAudioScene(g_ram))return 0;
    unsigned age=word(0x2000),actor=word(0x68),player=word(0x6e),caller=music_caller(cpu);
    int adult=age==0xffff;
    if((age && !adult) || cpu->X!=(adult?8:5) || caller!=(adult?0xc087d3:0xc087e8) ||
       player!=0xb213 || address(player+4)!=0xc5858a || !word(0x2004))return 0;
    unsigned selected=TlkResourcesUseMd("audio.effects.simba.revival_roar");
    unsigned emitted=selected && word(0x1ff96) && TlkMdSoundReady();
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *p=getenv("TLK_REVIVAL_AUDIO_TRACE");if(p)log=fopen(p,"w");
        if(log)fputs("field,level,current_task,player,age,caller,selected,emitted,voices\n",log);}
    if(log){fprintf(log,"%u,%u,%04x,%04x,%u,%06x,%u,%u,%s\n",snes_frame_counter+1,word(0x1ff9e),actor,player,age,caller,selected,emitted,adult?"10+11":"10");fflush(log);}
    if(!emitted)return 0;
    cpu->A=0;TlkMdSoundPcm(10,96);if(adult)TlkMdSoundPcm(11,96);effect_tail();return 1;
}
