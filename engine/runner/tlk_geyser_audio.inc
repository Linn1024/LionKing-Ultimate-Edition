/* Original MD13FF42:171 at geyser activation,92 at either real stop branch.
 * Native group11 transport/ramps stay intact; only owned voice kind10 is muted. */
static int geyser_audio_choice;
static int geyser_audio_actor(unsigned actor) {
    return be_prepared() && word(0x2000)==0xffff && actor>=0xb293 && actor<0xdc13 &&
        !((actor-0xb213)&127) && ((address(actor+4)==0xc58d52 && address(actor+48)==0xc2d4e4) ||
         (address(actor+4)==0xc5874a && address(actor+48)==0xc2d8cc));
}
static int geyser_audio_running(void) {
    if(!be_prepared() || !word(0x1ff96) || !word(0xa6bc) ||
       !TlkResourcesUseMd("audio.effects.world.be_prepared.geysers"))return 0;
    for(unsigned actor=0xb293;actor<0xdc13;actor+=128)
        if(geyser_audio_actor(actor) &&
           (address(actor+4)!=0xc5874a || word(actor+74)==0xffff))return 1;
    return 0;
}
static int geyser_audio(CpuState *cpu,uint32_t pc,int before) {
    if((pc!=0xc22c2c && pc!=0xc22cbf) || !be_prepared() || word(0x2000)!=0xffff ||
       cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D)return 0;
    unsigned actor=word(0x68),caller=0,value=0;
    if(pc==0xc22c2c){
        caller=music_caller(cpu);
        if(cpu->X!=41 || !geyser_audio_actor(actor) ||
           !((caller==0xc2d567 && address(actor+4)==0xc58d52) ||
             (caller==0xc2d997 && address(actor+4)==0xc5874a)))return 0;
        value=171;
    }else{
        caller=(unsigned)g_ram[(cpu->S+3)&65535]<<16|((word((cpu->S+1)&65535)+1)&65535);
        /* The C194B7 deletion branch can already have cleared active actor68.
         * This exact stop-group11 site still belongs to the original geyser. */
        if((before?word((cpu->S+4)&65535):cpu->A)!=11 ||
           (caller!=0xc2d5d1 && caller!=0xc2d700 && caller!=0xc2db42))return 0;
        value=92;
    }
    unsigned selected=TlkResourcesUseMd("audio.effects.world.be_prepared.geysers");
    unsigned emitted=selected && word(0x1ff96) && TlkMdSoundReady();
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *p=getenv("TLK_GEYSER_AUDIO_TRACE");if(p)log=fopen(p,"w");
        if(log)fputs("field,actor,descriptor,action,caller,selected,emitted,value,active,player_x,player_y\n",log);}
    if(log){fprintf(log,"%u,%04x,%06x,%06x,%06x,%u,%u,%u,%u,%u,%u\n",snes_frame_counter+1,actor,actor?address(actor+4):0,actor?address(actor+48):0,caller,selected,emitted,value,word(0xa6bc),word(0xb21b),word(0xb21d));fflush(log);}
    if(!emitted)return 0;
    TlkMdSoundCommand(2,value);effect_tail();return 1;
}
static void geyser_audio_pre(CpuState *cpu,uint32_t pc) {(void)geyser_audio(cpu,pc,1);}
