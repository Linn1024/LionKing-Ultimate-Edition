/* Original MD13FF34:165 on each wobble,168 once when falling starts. */
static int stalactite_choice;
static int stalactite_actor(unsigned actor) {
    if(!be_prepared() || word(0x2000)!=0xffff || actor<0xb293 || actor>=0xdc13 ||
       ((actor-0xb213)&127) || address(actor+4)!=0xc58774)return 0;
    unsigned draw=word(actor+12);
    return draw>=0x8000 && draw<=0xffe8 && word(draw+4)==actor+8;
}
static void stalactite_sound(unsigned actor,unsigned pc,unsigned value,const char *kind,int native_request,CpuState *cpu) {
    unsigned selected=TlkResourcesUseMd("audio.effects.world.be_prepared.stalactites");
    unsigned emitted=selected && word(0x1ff96) && TlkMdSoundReady();
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *p=getenv("TLK_STALACTITE_AUDIO_TRACE");if(p)log=fopen(p,"w");
        if(log)fputs("field,actor,descriptor,action,pc,kind,selected,emitted,value,player_x,player_y\n",log);}
    if(log){fprintf(log,"%u,%04x,%06x,%06x,%06x,%s,%u,%u,%u,%u,%u\n",snes_frame_counter+1,actor,address(actor+4),address(actor+48),pc,kind,selected,emitted,value,word(0xb21b),word(0xb21d));fflush(log);}
    if(!emitted)return;
    /* Keep the native request/queue and silence only its requested volume. */
    if(native_request)cpu->A=0;
    TlkMdSoundCommand(2,value);effect_tail();
}
static int stalactite_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=53 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D)return 0;
    unsigned actor=word(0x68);
    if(music_caller(cpu)!=0xc63f0c || !stalactite_actor(actor) || address(actor+48)!=0xc63e38)return 0;
    stalactite_sound(actor,0xc63f0c,165,"wobble",1,cpu);
    return TlkResourcesUseMd("audio.effects.world.be_prepared.stalactites") && word(0x1ff96) && TlkMdSoundReady();
}
static void stalactite_entry(CpuState *cpu,uint32_t pc,int before) {
    if(pc!=0xc63f64 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D || cpu->A!=0x3f2a || cpu->Y!=0x30)return;
    unsigned actor=word(0x68);if(!stalactite_actor(actor) || word(actor+34))return;
    /* LLE observes before the original store, AOT after that same store. */
    if(before?address(actor+48)==0xc63f2a:word(actor+48)!=0x3f2a)return;
    stalactite_sound(actor,pc,168,"fall_entry",0,cpu);
}
static void stalactite_entry_pre(CpuState *cpu,uint32_t pc) {stalactite_entry(cpu,pc,1);}
