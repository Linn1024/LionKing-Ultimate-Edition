/* Source5188: both original big-cat actions play PCM18/96 once on entry.
 * Native chase lacks that entry cue and can repeat native30 later. */
static int big_cat_choice;
static int big_cat_actor(unsigned actor) {
    if(!continue_world_scene() || word(0x2000)!=0xffff || actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127))return 0;
    unsigned desc=address(actor+4),draw=word(actor+12);
    return (desc==0xc58ea8 || desc==0xc58eb4) && draw>=0x8000 && draw<=0xffe8 && word(draw+4)==actor+8;
}
static void big_cat_log(unsigned actor,unsigned pc,const char *kind,unsigned selected,unsigned emitted) {
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *p=getenv("TLK_BIG_CAT_AUDIO_TRACE");if(p)log=fopen(p,"w");
        if(log)fputs("field,actor,descriptor,action,pc,kind,selected,emitted,value,parameter\n",log);}
    if(log){fprintf(log,"%u,%04x,%06x,%06x,%06x,%s,%u,%u,18,96\n",snes_frame_counter+1,actor,address(actor+4),address(actor+48),pc,kind,selected,emitted);fflush(log);}
}
static void big_cat_entry(CpuState *cpu,uint32_t pc,int before) {
    if(pc!=0xc5d241 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D || cpu->A!=0xd207 || cpu->Y!=0x30)return;
    unsigned actor=word(0x68);if(!big_cat_actor(actor))return;
    /* BEFORE the original store in LLE; AFTER the same store in AOT.
     * Resuming at the next instruction cannot emit the entry a second time. */
    if(before?address(actor+48)==0xc5d207:word(actor+48)!=0xd207)return;
    unsigned selected=TlkResourcesUseMd("audio.effects.world.big_cats");
    unsigned emitted=selected && word(0x1ff96) && TlkMdSoundReady();
    big_cat_log(actor,pc,"chase_entry",selected,emitted);
    if(emitted){TlkMdSoundPcm(18,96);effect_tail();}
}
static void big_cat_entry_pre(CpuState *cpu,uint32_t pc) {big_cat_entry(cpu,pc,1);}
static int big_cat_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=0x1e)return 0;
    unsigned actor=word(0x68),caller=music_caller(cpu);if(!big_cat_actor(actor))return 0;
    unsigned action=address(actor+48);
    int entry=caller==0xc5d0d5 && action==0xc5d069 && address(actor+14)==0xc249c3;
    int late=(caller==0xc5d180 && action==0xc5d069 || caller==0xc5d312 && action==0xc5d207) && word(actor+46)==3;
    if(!entry && !late)return 0;
    unsigned selected=TlkResourcesUseMd("audio.effects.world.big_cats");
    unsigned active=selected && word(0x1ff96) && TlkMdSoundReady();
    big_cat_log(actor,caller,entry?"pounce_entry":"native_repeat",selected,active && entry);
    if(!active)return 0;
    cpu->A=0;
    if(entry){TlkMdSoundPcm(18,96);effect_tail();}
    return 1;
}
