/* Source5241: MD172 on either release direction; MD92 at shared landing.
 * Native41 transport/ramps stay intact, with request-owned output kind9. */
static int destiny_boulder_choice;
static int destiny_boulder_actor(unsigned actor) {
    return destiny() && word(0x2000)==0xffff && actor>=0xb293 && actor<0xdc13 &&
        !((actor-0xb213)&127) && (address(actor+4)==0xc588dd || address(actor+4)==0xc588fd);
}
static int destiny_boulder_running(void) {
    if(!destiny() || !word(0x1ff96) || !TlkResourcesUseMd("audio.effects.world.simbas_destiny.boulders"))return 0;
    for(unsigned actor=0xb293;actor<0xdc13;actor+=128)
        if(destiny_boulder_actor(actor) && address(actor+48)==0xc59015 &&
           (word(actor+56) || word(actor+58)))return 1;
    return 0;
}
static int destiny_boulder_audio(CpuState *cpu,uint32_t pc,int before) {
    if((pc!=0xc22c2c && pc!=0xc22cbf) || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D)return 0;
    unsigned actor=word(0x68);if(!destiny_boulder_actor(actor))return 0;
    unsigned caller=0,value=0;
    if(pc==0xc22c2c){
        caller=music_caller(cpu);
        if(cpu->X!=41 || (caller!=0xc59182 && caller!=0xc591d5) || address(actor+48)!=0xc59015)return 0;
        value=172;
    }else{
        caller=(unsigned)g_ram[(cpu->S+3)&65535]<<16|((word((cpu->S+1)&65535)+1)&65535);
        if((before?word((cpu->S+4)&65535):cpu->A)!=10 || caller!=0xc59384 ||
           address(actor+4)!=0xc588dd || address(actor+48)!=0xc593d3 || word(actor+46))return 0;
        value=92;
    }
    unsigned selected=TlkResourcesUseMd("audio.effects.world.simbas_destiny.boulders");
    unsigned emitted=selected && word(0x1ff96) && TlkMdSoundReady();
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *p=getenv("TLK_DESTINY_BOULDER_AUDIO_TRACE");if(p)log=fopen(p,"w");
        if(log)fputs("field,actor,descriptor,action,caller,selected,emitted,value,simba_x,simba_y\n",log);}
    if(log){fprintf(log,"%u,%04x,%06x,%06x,%06x,%u,%u,%u,%u,%u\n",snes_frame_counter+1,actor,address(actor+4),address(actor+48),caller,selected,emitted,value,word(0xb21b),word(0xb21d));fflush(log);}
    if(!emitted)return 0;
    TlkMdSoundCommand(2,value);effect_tail();return 1;
}
static void destiny_boulder_pre(CpuState *cpu,uint32_t pc) {(void)destiny_boulder_audio(cpu,pc,1);}
