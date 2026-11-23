/* Source5022: native charge cue52 is absent from both original MD branches. */
static int frog_attack_choice;
static int frog_attack_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=0x34 || !hakuna() || word(0x2000))return 0;
    unsigned actor=word(0x68),caller=music_caller(cpu);
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127))return 0;
    unsigned descriptor=address(actor+4),action=address(actor+48);
    if((descriptor!=0xc58ed8 && descriptor!=0xc58ee4) ||
       !((caller==0xc4106c && action==0xc40ee3) || (caller==0xc413fc && action==0xc41196)) ||
       word(actor+28)!=10 || address(actor+14)!=0xc26ab9)return 0;
    unsigned draw=word(actor+12),pose=draw>=0x8000 && draw<=0xffe8?address(draw+10):0;
    if(draw<0x8000 || draw>0xffe8 || word(draw+4)!=actor+8 || pose<0xc131a9 || pose>=0xc13480)return 0;
    unsigned selected=TlkResourcesUseMd("audio.effects.world.hakuna.frog_attack");
    unsigned suppressed=selected && word(0x1ff96) && TlkMdSoundReady();
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *p=getenv("TLK_FROG_ATTACK_AUDIO_TRACE");if(p)log=fopen(p,"w");
        if(log)fputs("field,actor,descriptor,action,caller,selected,suppressed\n",log);}
    if(log){fprintf(log,"%u,%04x,%06x,%06x,%06x,%u,%u\n",snes_frame_counter+1,actor,descriptor,action,caller,selected,suppressed);fflush(log);}
    if(!suppressed)return 0;
    cpu->A=0;return 1;
}
